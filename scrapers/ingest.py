import argparse
import logging
import os
import re
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

from core.product_matcher import normalize
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


def same_model(scraped_name: str, model: str | None) -> bool:
    if not model:
        return False
    return re.search(rf"(?<![a-z0-9]){re.escape(normalize(model))}(?![a-z0-9])", normalize(scraped_name)) is not None


def find_product(cursor, scraped_name: str):
    cursor.execute(
        "SELECT idproducto,nombre,modelo FROM producto WHERE estado=1"
    )
    products = cursor.fetchall()
    model_matches = [p for p in products if same_model(scraped_name, p[2])]
    if len(model_matches) == 1:
        return model_matches[0]
    return None


def ingest(store: str, query: str) -> None:
    scraper = SCRAPERS[store](delay=1.5)
    results = scraper.search(query)
    db = connect_db()
    cursor = db.cursor()
    log_id = None
    updated = 0
    errors = 0

    try:
        cursor.execute(
            "SELECT idtienda FROM tienda WHERE LOWER(nombre)=LOWER(%s) AND estado=1",
            (store,),
        )
        row = cursor.fetchone()
        if not row:
            raise RuntimeError(f"La tienda '{store}' no existe en la tabla tienda")
        store_id = row[0]

        cursor.execute(
            "INSERT INTO scraper_log (idtienda,fecha_inicio,estado) VALUES (%s,NOW(),'ejecutando')",
            (store_id,),
        )
        log_id = cursor.lastrowid

        for item in results:
            try:
                name = (item.get("name") or "").strip()
                price = item.get("price")
                url = item.get("url")
                product = find_product(cursor, name)

                if not product:
                    cursor.execute(
                        "SELECT idmatch FROM producto_match_pendiente "
                        "WHERE estado='pendiente' AND ((idtienda=%s AND url=%s) "
                        "OR (idtienda IS NULL AND nombre_detectado=%s)) LIMIT 1",
                        (store_id, url, name),
                    )
                    pending = cursor.fetchone()
                    if pending:
                        cursor.execute(
                            "UPDATE producto_match_pendiente SET idtienda=%s,"
                            "nombre_detectado=%s,nombre_tienda=%s,sku_tienda=%s,url=%s,"
                            "imagen=%s,precio=%s,moneda=%s,disponible=%s WHERE idmatch=%s",
                            (store_id, name, name, item.get("sku"), url, item.get("image"),
                             price, item.get("currency", "GTQ"), int(bool(item.get("available"))), pending[0]),
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO producto_match_pendiente "
                            "(idtienda,nombre_detectado,nombre_tienda,sku_tienda,url,imagen,"
                            "precio,moneda,disponible,puntuacion,estado) "
                            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'pendiente')",
                            (store_id, name, name, item.get("sku"), url, item.get("image"),
                             price, item.get("currency", "GTQ"), int(bool(item.get("available"))), 0),
                        )
                    logging.warning("Sin producto para emparejar: %s", name)
                    errors += 1
                    continue
                if price is None or not url:
                    raise ValueError("resultado sin precio o URL")

                product_id = product[0]
                cursor.execute(
                    "INSERT INTO producto_tienda "
                    "(idproducto,idtienda,nombre_tienda,sku_tienda,url,imagen,disponibilidad) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s) "
                    "ON DUPLICATE KEY UPDATE nombre_tienda=VALUES(nombre_tienda), "
                    "url=VALUES(url), imagen=VALUES(imagen), disponibilidad=VALUES(disponibilidad), "
                    "actualizado_en=NOW()",
                    (product_id, store_id, name, item.get("sku"), url,
                     item.get("image"), int(bool(item.get("available")))),
                )
                cursor.execute(
                    "SELECT idproducto_tienda FROM producto_tienda "
                    "WHERE idproducto=%s AND idtienda=%s",
                    (product_id, store_id),
                )
                product_store_id = cursor.fetchone()[0]
                available = int(bool(item.get("available")))
                cursor.execute(
                    "SELECT precio,disponible FROM precio WHERE idproducto_tienda=%s "
                    "ORDER BY fecha DESC,idprecio DESC LIMIT 1",
                    (product_store_id,),
                )
                previous = cursor.fetchone()
                if not previous or float(previous[0]) != float(price) or int(previous[1]) != available:
                    previous_price = previous[0] if previous else None
                    cursor.execute(
                        "INSERT INTO precio "
                        "(idproducto_tienda,precio,precio_anterior,moneda,disponible) "
                        "VALUES (%s,%s,%s,%s,%s)",
                        (product_store_id, price, previous_price,
                         item.get("currency", "GTQ"), available),
                    )
                updated += 1
            except Exception as error:
                logging.exception("Error procesando %s: %s", item.get("name"), error)
                errors += 1

        status = "completado" if errors == 0 else "error"
        cursor.execute(
            "UPDATE scraper_log SET fecha_fin=NOW(),productos_encontrados=%s, "
            "productos_actualizados=%s,errores=%s,estado=%s WHERE idscraper_log=%s",
            (len(results), updated, errors, status, log_id),
        )
        db.commit()
        logging.info("Ingesta finalizada: encontrados=%s actualizados=%s errores=%s",
                     len(results), updated, errors)
    except Exception:
        db.rollback()
        if log_id:
            cursor.execute(
                "UPDATE scraper_log SET fecha_fin=NOW(),estado='error',mensaje=%s "
                "WHERE idscraper_log=%s", ("Error general de ingesta", log_id)
            )
            db.commit()
        raise
    finally:
        cursor.close()
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("store", choices=SCRAPERS)
    parser.add_argument("query")
    args = parser.parse_args()
    ingest(args.store, args.query)
