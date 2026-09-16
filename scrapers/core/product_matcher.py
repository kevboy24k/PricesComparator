"""Coincidencias automáticas: identificar el artículo antes de puntuar su nombre."""

import re
import unicodedata
from difflib import SequenceMatcher


# Solo estas familias se pueden incorporar automáticamente al catálogo.  La
# búsqueda no debe convertir artículos ajenos a tecnología en productos.
TECHNOLOGY_CATEGORIES = {
    'cpu': 'Procesadores',
    'gpu': 'Tarjetas gráficas',
    'ram': 'Memorias RAM',
    'storage': 'SSD',
    'motherboard': 'Motherboards',
    'laptop': 'Laptops',
    'computer': 'Computadoras de escritorio',
    'monitor': 'Monitores',
    'keyboard': 'Teclados',
    'mouse': 'Mouse',
    'audio': 'Audio y audífonos',
    'webcam': 'Webcams',
    'network': 'Redes',
    'printer': 'Impresoras',
    'tablet': 'Tablets',
    'phone': 'Celulares',
    'console': 'Consolas y videojuegos',
    'case': 'Gabinetes',
    'power_supply': 'Fuentes de poder',
    'cooling': 'Refrigeración',
    'accessory': 'Accesorios tecnológicos',
}


def normalize(text: str) -> str:
    text = str(text or '').replace('™', '').replace('®', '')
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', text)).strip()


def canonical(text: str) -> str:
    text = normalize(text)
    text = re.sub(r'\br([3579])(?=\s|\d)', r'ryzen \1 ', text)
    text = re.sub(r'\b(rtx|gtx|rx|arc)\s*(?=\d|[ab]\d)', r'\1 ', text)
    text = re.sub(r'\b(i[3579])\s*(?=\d)', r'\1 ', text)
    text = re.sub(r'\b(ryzen\s+[3579])\s+(\d{4}[a-z0-9]*)\s+pro\b', r'\1 pro \2', text)
    text = re.sub(r'\b(\d+)\s+(gb|tb)\b', r'\1\2', text)
    text = re.sub(r'\b(\d+)\s+(hz|fps|dpi|w|mm)\b', r'\1\2', text)
    return re.sub(r'\s+', ' ', text).strip()


def component_models(text: str) -> dict[str, set[str]]:
    text = canonical(text)
    models = {'gpu': set(), 'cpu': set()}
    for found in re.finditer(
        r'\b(rtx|gtx|rx|arc)\s+([ab]?\d{3,4})\s*'
        r'(ti\s*super|ti|super|xtx|xt|gre)?\b', text
    ):
        variant = re.sub(r'ti\s*super', 'ti super', found[3] or '')
        models['gpu'].add(' '.join(filter(None, (found[1], found[2], variant))))
    suffix = r'(x3d|xt|gt|ge|hs|hx|kf|ks|x|g|f|k|u|h|t|s)?\b'
    for found in re.finditer(
        r'\bryzen\s+([3579])\s+(pro\s+)?(\d{4})\s*' + suffix, text
    ):
        models['cpu'].add(f'ryzen {found[1]} {"pro " if found[2] else ""}{found[3]}{found[4] or ""}')
    for found in re.finditer(r'\b(i[3579])\s+(\d{4,5})\s*' + suffix, text):
        models['cpu'].add(f'{found[1]} {found[2]}{found[3] or ""}')
    for found in re.finditer(r'\bcore\s+ultra\s+([579])\s+(\d{3})\s*' + suffix, text):
        models['cpu'].add(f'core ultra {found[1]} {found[2]}{found[3] or ""}')
    return models


def capacities(text: str) -> set[str]:
    return {re.sub(r'\s+', '', value) for value in re.findall(r'\b\d+\s*(?:gb|tb)\b', canonical(text))}


def memory_generations(text: str) -> set[str]:
    return set(re.findall(r'\bddr[345]\b', canonical(text)))


def storage_interfaces(text: str) -> set[str]:
    normalized = canonical(text)
    interfaces = set()
    if re.search(r'\bnvme\b', normalized):
        interfaces.add('nvme')
    if re.search(r'sata\b', normalized):
        interfaces.add('sata')
    if re.search(r'\bm\s*2\b|\bm2\b', normalized):
        interfaces.add('m2')
    return interfaces


def product_type(product: dict) -> str | None:
    text = canonical(product.get('name', ''))
    # Un periférico puede mencionar el equipo o componente al que está destinado.
    accessory = re.search(
        r'\b(cooler|disipador|ventilador|heatsink|waterblock|bloque de agua|'
        r'soporte|bracket|adaptador|adapter|cable|funda|cargador|repuesto|'
        r'carcasa|backplate|pasta termica|refrigeracion|enfriador)\b', text
    )
    primary = re.search(r'\b(procesador|processor|cpu|ryzen|i[3579]|core|rtx|gtx|rx|arc|tarjeta|graphics card)\b', text)
    cooling_component = re.search(r'\b(?:cooler master|cooler|disipador|heatsink)\b', text)
    cooling_context = re.search(r'\b(?:cpu|procesador|am[45]|lga\s*\d+|radiador|\d{2,3}\s*mm)\b', text)
    included_with_primary = (primary and cooling_component and primary.start() < cooling_component.start()
                             and re.search(r'\b(con|with|incluye|includes|incluido)\b', text[primary.start():cooling_component.start()]))
    if (re.search(r'\b(refrigeracion(?: liquida)?|liquid cooling|water cooling|aio)\b', text)
            or (cooling_component and cooling_context)) and not included_with_primary and not re.search(r'\bwaterblock\b', text):
        return 'cooling'
    if accessory:
        included_cooling = (primary and primary.start() < accessory.start()
                            and accessory[0] in ('cooler', 'disipador', 'heatsink', 'ventilador')
                            and re.search(r'\b(con|with|incluye|includes|incluido|wraith)\b', text[primary.start():accessory.start()]))
        if not included_cooling:
            return 'accessory'
    if re.search(r'\b(bundle|combo|paquete|kit de actualizacion|upgrade kit)\b', text):
        return 'bundle'
    # "Memoria para laptop/desktop" es un módulo de RAM, no una laptop ni una
    # computadora. Se evalúa antes de detectar el equipo donde se instalará.
    if re.search(r'\b(memoria|memory)\b', text) and re.search(r'\b(ram|ddr[345])\b', text):
        return 'ram'
    if re.search(r'\b(motherboard|mainboard|placa (base|madre)|tarjeta madre)\b', text):
        return 'motherboard'
    if re.search(r'\b(laptops?|notebooks?|portatil|netbook|omnibook|thinkpad|thinkbook|ideapad|vivobook|zenbook|macbook)\b', text):
        return 'laptop'
    if re.search(r'\b(zephyrus|legion|loq|predator helios|nitro v|rog (strix|scar) [gs]\d+|tuf gaming [af]\d+|msi (katana|thin|cyborg|vector|sword))\b', text):
        return 'laptop'
    computer = re.search(r'\b(pc|desktop|computer|computadora|ordenador|workstation|all in one|aio|equipo armado|torre gaming)\b', text)
    if computer:
        # "Tarjeta gráfica para PC" sigue siendo una tarjeta gráfica.
        if not re.search(r'\b(tarjeta (grafica|de video)|graphics card|procesador|processor)\b', text):
            return 'computer'
        if primary and computer.start() < primary.start():
            return 'computer'
    if re.search(r'\b(monitor(?:es)?|pantallas?)\b', text):
        return 'monitor'
    if re.search(r'\b(teclado|keyboard)\b', text):
        return 'keyboard'
    if re.search(r'\b(mouse|mice|raton)\b', text):
        return 'mouse'
    if re.search(r'\b(audifonos?|headphones?|headset|earbuds?|bocinas?|altavoces?|speaker)\b', text):
        return 'audio'
    if re.search(r'\b(webcam|camara web)\b', text):
        return 'webcam'
    if re.search(r'\b(router|switch|access point|punto de acceso|wifi|wi fi|redes?)\b', text):
        return 'network'
    if re.search(r'\b(impresoras?|printers?|multifuncional(?:es)?)\b', text):
        return 'printer'
    if re.search(r'\b(tablet|ipad)\b', text):
        return 'tablet'
    if re.search(r'\b(celular|smartphone|iphone|samsung galaxy|xiaomi redmi|google pixel)\b', text):
        return 'phone'
    if re.search(r'\b(playstation|ps[45]|xbox|nintendo switch|consola)\b', text):
        return 'console'
    if re.search(r'\b(gabinete|chasis|case)\b', text):
        return 'case'
    if re.search(r'\b(fuentes?(?: de poder)?|power supply|psu)\b', text):
        return 'power_supply'
    if re.search(r'\b(refrigeracion|liquid cooling|water cooling)\b', text):
        return 'cooling'
    models = component_models(text)
    if models['cpu'] and models['gpu']:
        return 'computer'
    # Algunos títulos omiten "laptop/PC", pero enumeran RAM, disco y procesador/GPU.
    if (models['cpu'] or models['gpu']) and re.search(r'\b(ram|ddr[345])\b', text) and re.search(r'\b(ssd|hdd|nvme)\b', text):
        return 'computer'
    category = normalize(product.get('category', ''))
    categories = {normalize(category): kind for kind, category in TECHNOLOGY_CATEGORIES.items()}
    # Se conservan los nombres utilizados por instalaciones ya creadas.
    categories.update({'ssd': 'storage', 'monitores': 'monitor'})
    if category in categories:
        return categories[category]
    if models['cpu'] or re.search(r'\b(procesador|processor|cpu)\b', text):
        return 'cpu'
    if models['gpu'] or re.search(r'\b(tarjeta grafica|tarjeta de video|graphics card|gpu)\b', text):
        return 'gpu'
    if re.search(r'\b(ram|ddr[345])\b', text):
        return 'ram'
    if re.search(r'\b(ssd|hdd|nvme|solid state|unidad de estado solido)\b', text):
        return 'storage'
    return None


def technology_identity_matches(detected: dict, candidate: dict) -> bool:
    """Comprueba las especificaciones que distinguen una búsqueda tecnológica.

    No exige palabras de relleno (por ejemplo, "memoria" o "de") que cada
    tienda redacta distinto, pero sí protege DDR, capacidad e interfaz cuando
    la consulta las indica.
    """
    detected_type = product_type(detected)
    candidate_type = product_type(candidate)
    if detected_type not in TECHNOLOGY_CATEGORIES or candidate_type != detected_type:
        return False
    detected_name = detected.get('name', '')
    candidate_name = candidate.get('name', '')
    if not capacities(candidate_name).issubset(capacities(detected_name)):
        return False
    if detected_type == 'ram' and not memory_generations(candidate_name).issubset(memory_generations(detected_name)):
        return False
    if detected_type == 'storage' and not storage_interfaces(candidate_name).issubset(storage_interfaces(detected_name)):
        return False
    # Códigos como NV2, G502 o A15 son identidad del producto y no deben
    # confundirse con cualquier artículo de la misma categoría.
    identifiers = set(re.findall(r'\b(?=[a-z0-9]*[a-z])(?=[a-z0-9]*\d)[a-z0-9]+\b', canonical(candidate_name)))
    identifiers.update(re.findall(r'\b\d{2,}\b', canonical(candidate_name)))
    identifiers -= {'ddr3', 'ddr4', 'ddr5', 'm2', 'wifi6', 'wifi7'}
    detected_tokens = set(canonical(detected_name).split())
    return identifiers.issubset(detected_tokens)


def incompatibility_reason(detected: dict, candidate: dict) -> str | None:
    left = canonical(detected.get('name', ''))
    right = canonical(candidate.get('name', ''))
    if not left or not right:
        return 'Nombre de producto vacío'
    left_type, right_type = product_type(detected), product_type(candidate)
    if left_type and right_type and left_type != right_type:
        return f'Tipo de producto distinto: {left_type} / {right_type}'
    left_models, right_models = component_models(left), component_models(right)
    for kind in ('cpu', 'gpu'):
        if left_models[kind] and right_models[kind] and left_models[kind] != right_models[kind]:
            return 'Modelo o variante de componente diferente'
    if right_type in ('cpu', 'gpu'):
        # Evita que la coincidencia de SKU o un número aislado venza la identidad.
        if not left_models[right_type] or not right_models[right_type]:
            return 'No se pudo identificar el modelo completo del componente'
        if left_type != right_type:
            return 'No se pudo identificar el tipo de artículo'
    if capacities(right) and not capacities(right).issubset(capacities(left)):
        return 'Capacidad diferente o sin confirmar'
    if right_type == 'gpu':
        brands = {'asus', 'msi', 'gigabyte', 'zotac', 'pny', 'sapphire', 'powercolor', 'asrock', 'palit'}
        expected = brands.intersection(right.split())
        if expected and expected != brands.intersection(left.split()):
            return 'Fabricante de tarjeta diferente o sin confirmar'
        for edition in ('ventus', 'tuf', 'strix', 'suprim', 'aorus', 'eagle', 'windforce',
                        'gaming trio', 'gaming x', 'dual', 'prime', 'trinity', 'twin edge', 'pulse', 'nitro'):
            if re.search(r'\b' + edition + r'\b', right) and not re.search(r'\b' + edition + r'\b', left):
                return 'Edición de tarjeta diferente o sin confirmar'
    return None


def confidence(a: str, b: str) -> float:
    left, right = canonical(a), canonical(b)
    if not left or not right:
        return 0.0
    return round(SequenceMatcher(None, left, right).ratio() * 100, 2)


def classify(score: float) -> str:
    return 'automatico' if score >= 90 else 'omitido'


def model_matches(name: str, model: str | None) -> bool:
    model = canonical(model)
    if not model:
        return False
    return re.search(rf'(?<![a-z0-9]){re.escape(model)}(?![a-z0-9])', canonical(name)) is not None


def score_match(detected: dict, candidate: dict) -> float:
    if incompatibility_reason(detected, candidate):
        return 0.0
    name_score = confidence(detected.get('name'), candidate.get('name'))
    detected_sku = normalize(detected.get('sku'))
    candidate_sku = normalize(candidate.get('sku_global'))
    if detected_sku and detected_sku == candidate_sku:
        return 100.0
    kind = product_type(candidate)
    if kind in ('cpu', 'gpu'):
        # Ya se verificaron tipo, familia, número y sufijo; no solo el texto.
        model = candidate.get('model')
        if model and not model_matches(detected.get('name'), model):
            # Admitir abreviaturas/espacios del modelo completo, no otros SKU específicos.
            model_ids = component_models(model)[kind]
            if model_ids != component_models(candidate.get('name'))[kind]:
                return min(name_score, 89.0)
        return round(90 + name_score * 0.1, 2)
    # Compartir un procesador/GPU no identifica una laptop específica.
    if kind in ('laptop', 'computer', 'bundle') and canonical(detected.get('name')) != canonical(candidate.get('name')):
        if not candidate.get('model') or component_models(candidate['model'])['cpu'] or component_models(candidate['model'])['gpu']:
            return min(name_score, 89.0)
    if kind in TECHNOLOGY_CATEGORIES and technology_identity_matches(detected, candidate):
        # Para RAM/SSD y periféricos, las tiendas no comparten el mismo texto,
        # pero sí deben compartir la categoría y las especificaciones pedidas.
        return round(90 + name_score * 0.1, 2)
    deterministic_score = round(90 + name_score * 0.1, 2) if model_matches(detected.get('name'), candidate.get('model')) else name_score
    # Respaldo genérico: no conoce marcas, categorías ni listas de modelos.
    # Es útil para modelos nuevos que ya existen en el catálogo (G502, X100,
    # etc.) y nunca sobreescribe una incompatibilidad validada al inicio.
    from core.entity_resolution import score as evidence_score
    return max(deterministic_score, evidence_score(candidate.get('name', ''), detected.get('name', '')))


def classify_match(detected: dict, catalog: list[dict]) -> dict:
    scored = [{'product': product, 'score': score_match(detected, product)} for product in catalog]
    scored.sort(key=lambda item: item['score'], reverse=True)
    if not scored:
        return {'product': None, 'score': 0, 'margin': 0, 'classification': 'nuevo', 'reason': 'Sin productos en catálogo'}
    best = scored[0]
    margin = best['score'] - (scored[1]['score'] if len(scored) > 1 else 0)
    automatic = best['score'] >= 90 and margin >= 5
    reason = None if automatic else (incompatibility_reason(detected, best['product']) or
                                     ('Coincidencia ambigua' if best['score'] >= 90 else 'Identidad insuficiente'))
    return {**best, 'margin': margin, 'classification': 'automatico' if automatic else 'omitido', 'reason': reason}


def match(detected: dict, catalog: list[dict]) -> dict | None:
    result = classify_match(detected, catalog)
    return {'product': result['product'], 'confidence': result['score']} if result['classification'] == 'automatico' else None
