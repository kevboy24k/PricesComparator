import argparse
import logging
import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

from core.product_matcher import classify_match
from core.utils import utils
from stores.kemik import KemikScraper
from stores.intelaf import IntelafScraper
from stores.pacifiko import PacifikoScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

SCRAPERS = {
    "kemik": KemikScraper,
    "intelaf": IntelafScraper,
    "pacifiko": PacifikoScraper,
}


def connect_db():
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "compara_tech_gt"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
    )


def load_catalog(cursor):
    cursor.execute(
        "SELECT idproducto,nombre,modelo,sku_global,"
        "(SELECT nombre FROM categoria WHERE idcategoria=producto.idcategoria) "
        "FROM producto WHERE estado=1"
    )
    return [
        {"idproducto": row[0], "name": row[1], "model": row[2],
         "sku_global": row[3], "category": row[4]}
        for row in cursor.fetchall()
    ]


def find_product(cursor, item: dict):
    return classify_match(item, load_catalog(cursor))


def valid_offer(item: dict) -> bool:
    from math import isfinite
    try:
        return (bool(str(item.get("name") or "").strip())
                and str(item.get("url") or "").startswith(("https://", "http://"))
                and isfinite(float(item.get("price"))) and float(item["price"]) > 0)
    except (TypeError, ValueError):
        return False


def revalidate_offers(cursor, store_id: int, catalog: list[dict]) -> int:
    """Retirar asociaciones antiguas inválidas conservando su historial de precios."""
    products = {product["idproducto"]: product for product in catalog}
    cursor.execute(
        "SELECT idproducto_tienda,idproducto,nombre_tienda,sku_tienda "
        "FROM producto_tienda WHERE idtienda=%s AND estado=1", (store_id,)
    )
    invalidated = 0
    for offer_id, product_id, name, sku in cursor.fetchall():
        product = products.get(product_id)
        if not product:
            continue
        result = classify_match({"name": name, "sku": sku}, [product])
        if result["classification"] != "automatico":
            cursor.execute("UPDATE producto_tienda SET estado=0 WHERE idproducto_tienda=%s", (offer_id,))
            utils.report_error("Oferta %s desactivada: %s", offer_id, result["reason"])
            invalidated += 1
    return invalidated


def ingest(store: str, query: str) -> dict:
    # Ambos puntos de entrada usan exactamente las mismas reglas automáticas.
    from live_ingest import run
    return run(query, stores=(store,))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("store", choices=SCRAPERS)
    parser.add_argument("query")
    args = parser.parse_args()
    ingest(args.store, args.query)
