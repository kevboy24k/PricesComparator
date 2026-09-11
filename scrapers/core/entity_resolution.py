"""Resolvedor genérico de entidades para títulos de catálogo y tiendas.

No contiene marcas, modelos ni categorías de productos. Evalúa la evidencia que
aparece en ambos títulos: identificadores, capacidades, tokens distintivos y
similitud de cadenas. Las reglas específicas de seguridad del matcher principal
siguen teniendo prioridad para componentes que pueden confundirse peligrosamente.
"""

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from core.product_matcher import canonical


COMMON_WORDS = {
    'a', 'al', 'con', 'de', 'del', 'el', 'en', 'for', 'la', 'las', 'los',
    'para', 'por', 'sin', 'the', 'un', 'una', 'with', 'y', 'and',
    'accesorio', 'adaptador', 'black', 'blanco', 'color', 'compatible',
    'computadora', 'desktop', 'disponible', 'equipo', 'gaming', 'incluye',
    'laptop', 'memoria', 'modelo', 'negro', 'nuevo', 'pc', 'producto',
    'profesional', 'tecnologia', 'version',
}


@dataclass(frozen=True)
class Evidence:
    score: float
    coverage: float
    anchors: tuple[str, ...]
    matched_anchors: tuple[str, ...]


def _tokens(value: str) -> set[str]:
    return {token for token in canonical(value).split() if len(token) > 1 and token not in COMMON_WORDS}


def _anchors(value: str) -> set[str]:
    """Tokens estables: SKU/modelo, capacidad o números de dos dígitos."""
    return {
        token for token in _tokens(value)
        if re.search(r'\d', token) and (len(token) >= 2 or token.isdigit())
    }


def _contains_anchor(anchor: str, candidate: str) -> bool:
    if re.search(rf'(?<![a-z0-9]){re.escape(anchor)}(?![a-z0-9])', candidate):
        return True
    # Algunas tiendas unen un sufijo a un modelo (por ejemplo, "g502x").
    return len(anchor) >= 3 and anchor in candidate


def compare(left: str, right: str) -> Evidence:
    """Devuelve evidencia direccional de que *right* representa a *left*."""
    normalized_left, normalized_right = canonical(left), canonical(right)
    if not normalized_left or not normalized_right:
        return Evidence(0.0, 0.0, (), ())

    left_tokens, right_tokens = _tokens(left), _tokens(right)
    anchors = _anchors(left)
    matched = {anchor for anchor in anchors if _contains_anchor(anchor, normalized_right)}
    anchor_coverage = len(matched) / len(anchors) if anchors else 1.0
    token_coverage = len(left_tokens & right_tokens) / len(left_tokens) if left_tokens else 0.0
    sequence = SequenceMatcher(None, normalized_left, normalized_right).ratio()

    # Si la consulta aporta una identidad concreta, todos sus identificadores
    # deben estar presentes. Sin ellos, la coincidencia queda para revisión.
    if anchors and anchor_coverage < 1.0:
        score = 35.0 * anchor_coverage + 35.0 * token_coverage + 15.0 * sequence
    else:
        score = 55.0 * anchor_coverage + 30.0 * token_coverage + 15.0 * sequence
    return Evidence(round(min(score, 100.0), 2), round(token_coverage, 3),
                    tuple(sorted(anchors)), tuple(sorted(matched)))


def score(left: str, right: str) -> float:
    return compare(left, right).score
