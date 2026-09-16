import json
import logging
import re
import sys

from core.product_matcher import (
    TECHNOLOGY_CATEGORIES,
    canonical,
    classify_match,
    component_models,
    incompatibility_reason,
    has_catalog_identity,
    product_type,
    technology_identity_matches,
)
from core.utils import utils
from core.technology_catalog import (
    SearchProfile,
    attributes_match,
    build_search_profile,
    offer_attribute_rows,
    query_variants,
)
from ingest import connect_db, load_catalog, revalidate_offers, valid_offer, SCRAPERS

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")


def query_tokens(query: str) -> list[str]:
    return canonical(query).split()


def relevant(item: dict, query: str, profile: SearchProfile | None = None) -> bool:
    target = {"name": query, "model": query}
    kind = product_type(target)
    item_kind = product_type(item)
    if not canonical(query) or item_kind not in TECHNOLOGY_CATEGORIES:
        return False
    incompatibility = incompatibility_reason(item, target)
    # La única incompatibilidad que puede resolverse por una equivalencia del
    # perfil es la capacidad comercial. Tipo, interfaz, modelo y variante no
    # se relajan nunca.
    if incompatibility:
        if (incompatibility == "Capacidad diferente o sin confirmar"
                and profile and kind in ("ram", "storage")
                and item_kind == kind and profile.category == kind
                and attributes_match(profile, item.get("name", ""))):
            return True
        return False
    if kind in ("cpu", "gpu"):
        if classify_match(item, [target])["classification"] != "automatico":
            return False
        # Respetar calificadores de búsqueda además de la identidad del componente.
        identity = component_models(query)[kind]
        remaining = canonical(query)
        for model in identity:
            # Los modelos se validaron por separado (RTX5070 / RTX 5070, 7600X / 7600 X).
            remaining = re.sub(r"\b" + re.escape(model) + r"\b", "", remaining)
        if identity and remaining == canonical(query):
            matched = all(token in canonical(item.get("name")) for token in query_tokens(query))
        else:
            matched = all(token in canonical(item.get("name")).split() for token in remaining.split())
        return matched and (not profile or profile.category != kind or attributes_match(profile, item.get("name", "")))
    # RAM y almacenamiento admiten equivalencias comerciales de capacidad.
    # La categoría ya fue validada arriba, por lo que una laptop nunca puede
    # pasar esta ruta aunque anuncie RAM o SSD en sus especificaciones.
    if profile and kind in ("ram", "storage") and profile.category == kind:
        return attributes_match(profile, item.get("name", ""))
    if kind in TECHNOLOGY_CATEGORIES:
        if not technology_identity_matches(item, target):
            return False
        return not profile or profile.category != kind or attributes_match(profile, item.get("name", ""))
    # Para modelos o marcas que no aparecen en reglas predefinidas, la
    # evidencia del identificador del producto decide la coincidencia.
    return classify_match(item, [target])["classification"] == "automatico"


def catalog_product(cursor, query: str, first_result: dict, profile: SearchProfile | None = None):
    # La búsqueda define la identidad; nunca una laptop devuelta en primer lugar.
    if not has_catalog_identity(query):
        utils.report_error("Consulta sin identidad de producto; no se crea ni reutiliza catálogo: %s", query)
        return None
    target = {"name": query.strip(), "model": query.strip()}
    if not relevant(first_result, query, profile):
        return None
    catalog = load_catalog(cursor)
    result = classify_match(target, catalog)
    if result["classification"] == "automatico":
        return result["product"]
    if result["score"] >= 90:
        utils.report_error("Catálogo ambiguo para %s; se omite automáticamente", query)
        return None
    kind = product_type(target) or product_type(first_result)
    # Solo se agregan categorías tecnológicas reconocidas. A diferencia de
    # CPU/GPU, RAM y almacenamiento se identifican por DDR/capacidad/interfaz.
    profile_match = (profile is not None and kind in ("ram", "storage")
                     and profile.category == kind and attributes_match(profile, first_result.get("name", "")))
    if kind not in TECHNOLOGY_CATEGORIES or (
        product_type(target) in TECHNOLOGY_CATEGORIES
        and kind not in ("cpu", "gpu")
        and not profile_match
        and not technology_identity_matches(first_result, target)
    ):
        utils.report_error("Búsqueda tecnológica sin identidad verificable: %s", query)
        return None
    category = TECHNOLOGY_CATEGORIES[kind]
    cursor.execute("INSERT IGNORE INTO categoria (nombre) VALUES (%s)", (category,))
    cursor.execute("SELECT idcategoria FROM categoria WHERE nombre=%s", (category,))
    category_id = cursor.fetchone()[0]

    brand = None
    brand_text = canonical(query)
    brand_name = next((value for value in ("AMD", "Intel", "NVIDIA", "ASUS", "MSI", "Gigabyte", "Zotac")
                       if value.lower() in brand_text.split()), None)
    if brand_name is None:
        if "ryzen" in brand_text or "rx " in brand_text:
            brand_name = "AMD"
        elif "rtx " in brand_text or "gtx " in brand_text:
            brand_name = "NVIDIA"
        elif "core" in brand_text or re.search(r"\bi[3579]\b|\barc\b", brand_text):
            brand_name = "Intel"
    if brand_name:
        cursor.execute("SELECT idmarca FROM marca WHERE LOWER(nombre)=LOWER(%s)", (brand_name,))
        row = cursor.fetchone()
        brand = row[0] if row else None
    display_name = query.strip()
    if brand_name and brand_name.lower() not in brand_text.split():
        display_name = f"{brand_name} {display_name}"
    # Conservar la familia y TODOS los sufijos; "Ti" no es un modelo por sí solo.
    model = query.strip()
    sku_global = "AUTO-" + re.sub(r"[^A-Z0-9-]", "-", canonical(display_name).upper()).strip("-")
    cursor.execute(
        "INSERT INTO producto (idcategoria,idmarca,nombre,modelo,sku_global,imagen,descripcion) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE idproducto=LAST_INSERT_ID(idproducto)",
        (category_id, brand, display_name, model, sku_global, first_result.get("image"),
         "Producto agregado automáticamente desde una búsqueda en vivo."),
    )
    cursor.execute("SELECT idproducto,nombre,modelo,sku_global FROM producto WHERE sku_global=%s AND estado=1", (sku_global,))
    row = cursor.fetchone()
    return {"idproducto": row[0], "name": row[1], "model": row[2], "sku_global": row[3]} if row else None


def save_review_candidate(cursor, store_id: int, item: dict, score: float) -> None:
    """Conserva evidencia incierta para revisión y posterior entrenamiento."""
    cursor.execute(
        "SELECT idmatch FROM producto_match_pendiente WHERE idtienda=%s AND url=%s "
        "AND estado='pendiente' LIMIT 1", (store_id, item['url'])
    )
    row = cursor.fetchone()
    values = (item['name'], item.get('sku'), item.get('image'), item['price'],
              item.get('currency', 'GTQ'), int(bool(item.get('available'))), score)
    if row:
        cursor.execute(
            "UPDATE producto_match_pendiente SET nombre_detectado=%s,nombre_tienda=%s,sku_tienda=%s,"
            "imagen=%s,precio=%s,moneda=%s,disponible=%s,puntuacion=%s WHERE idmatch=%s",
            (item['name'], *values, row[0]),
        )
        return
    cursor.execute(
        "INSERT INTO producto_match_pendiente "
        "(idtienda,nombre_detectado,nombre_tienda,sku_tienda,url,imagen,precio,moneda,disponible,puntuacion,estado) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'pendiente')",
        (store_id, item['name'], item['name'], item.get('sku'), item['url'], item.get('image'),
         item['price'], item.get('currency', 'GTQ'), int(bool(item.get('available'))), score),
    )


def save_offer(cursor, store_id: int, product: dict, item: dict, profile: SearchProfile | None = None):
    result = classify_match(item, [product])
    profile_match = (profile is not None and profile.category in ("ram", "storage")
                     and product_type(product) == profile.category
                     and product_type(item) == profile.category
                     and attributes_match(profile, item.get("name", "")))
    if not valid_offer(item) or (result['classification'] != 'automatico' and not profile_match):
        utils.report_error('Oferta inválida para %s: %s', product['name'], result['reason'])
        raise ValueError('La oferta no corresponde inequívocamente al producto')
    cursor.execute(
        "INSERT INTO producto_tienda (idproducto,idtienda,nombre_tienda,sku_tienda,url,imagen,disponibilidad) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE nombre_tienda=VALUES(nombre_tienda),"
        "sku_tienda=VALUES(sku_tienda),url=VALUES(url),imagen=VALUES(imagen),"
        "disponibilidad=VALUES(disponibilidad),estado=1,actualizado_en=NOW()",
        (product["idproducto"], store_id, item["name"], item.get("sku"), item["url"], item.get("image"),
         int(bool(item.get("available")))),
    )
    cursor.execute("SELECT idproducto_tienda FROM producto_tienda WHERE idproducto=%s AND idtienda=%s",
                   (product["idproducto"], store_id))
    product_store_id = cursor.fetchone()[0]
    for code, value_text, value_number, unit in offer_attribute_rows(item.get("name", ""), profile.category if profile else product_type(product)):
        cursor.execute(
            "INSERT INTO producto_tienda_atributo "
            "(idproducto_tienda,codigo,valor_texto,valor_numero,unidad,confianza,fuente) "
            "VALUES (%s,%s,%s,%s,%s,%s,'regla') "
            "ON DUPLICATE KEY UPDATE valor_texto=VALUES(valor_texto),valor_numero=VALUES(valor_numero),"
            "unidad=VALUES(unidad),confianza=VALUES(confianza),extraido_en=NOW()",
            (product_store_id, code, value_text, value_number, unit, 1.0),
        )
    if item.get("price") is not None:
        available = int(bool(item.get("available")))
        cursor.execute("SELECT precio,disponible FROM precio WHERE idproducto_tienda=%s ORDER BY fecha DESC,idprecio DESC LIMIT 1",
                       (product_store_id,))
        previous = cursor.fetchone()
        if not previous or float(previous[0]) != float(item["price"]) or int(previous[1]) != available:
            cursor.execute("INSERT INTO precio (idproducto_tienda,precio,precio_anterior,moneda,disponible) VALUES (%s,%s,%s,%s,%s)",
                           (product_store_id, item["price"], previous[0] if previous else None,
                            item.get("currency", "GTQ"), available))
    if item.get('image') and str(product.get('sku_global') or '').startswith('AUTO-'):
        cursor.execute('UPDATE producto SET imagen=%s WHERE idproducto=%s',
                       (item['image'], product['idproducto']))


def run(query: str, stores=None) -> dict:
    db = connect_db()
    cursor = db.cursor()
    summary = {"query": query, "stores": {}, "created": 0, "offers": 0, "skipped": 0,
               "invalidated": 0, "review": 0}
    profile = build_search_profile(query, product_type({"name": query}))
    search_terms = query_variants(query, profile)
    try:
        for store, scraper_class in SCRAPERS.items():
            if stores is not None and store not in stores:
                continue
            cursor.execute("SELECT idtienda FROM tienda WHERE LOWER(nombre)=LOWER(%s) AND estado=1", (store,))
            store_row = cursor.fetchone()
            if not store_row:
                continue
            store_id = store_row[0]
            cursor.execute("INSERT INTO scraper_log (idtienda,fecha_inicio,estado) VALUES (%s,NOW(),'ejecutando')", (store_id,))
            log_id = cursor.lastrowid
            found = saved = skipped = invalidated = created = review = 0
            cursor.execute("SAVEPOINT ingesta_tienda")
            try:
                results_by_url = {}
                for search_term in search_terms:
                    for item in scraper_class(delay=1.5).search(search_term):
                        key = item.get("url") or f"{item.get('name')}|{item.get('price')}"
                        results_by_url.setdefault(key, item)
                raw_results = list(results_by_url.values())
                invalidated = revalidate_offers(cursor, store_id, load_catalog(cursor))
                found = len(raw_results)
                results = []
                for item in raw_results:
                    if valid_offer(item) and relevant(item, query, profile):
                        results.append(item)
                    else:
                        skipped += 1
                        if valid_offer(item):
                            candidate = classify_match(item, [{"name": query, "model": query}])
                            if 65 <= candidate['score'] < 90 and not incompatibility_reason(item, {"name": query}):
                                save_review_candidate(cursor, store_id, item, candidate['score'])
                                review += 1
                        reason = incompatibility_reason(item, {"name": query}) or "Datos incompletos o búsqueda no coincidente"
                        utils.report_error("%s: omitido %s (%s)", store, item.get("name"), reason)
                # Solo hay una oferta por producto/tienda: conservar la disponible más económica.
                results.sort(key=lambda item: (not bool(item.get("available")), float(item["price"]), item["url"]))
                if results:
                    cursor.execute("SELECT COUNT(*) FROM producto")
                    before = cursor.fetchone()[0]
                    product = catalog_product(cursor, query, results[0], profile)
                    cursor.execute("SELECT COUNT(*) FROM producto")
                    created = max(0, cursor.fetchone()[0] - before)
                    for item in results:
                        result = classify_match(item, [product]) if product else None
                        profile_variant = (profile.category in ("ram", "storage") and product
                                           and product_type(product) == profile.category
                                           and product_type(item) == profile.category
                                           and attributes_match(profile, item.get("name", "")))
                        if not saved and result and (result["classification"] == "automatico" or profile_variant):
                            save_offer(cursor, store_id, product, item, profile)
                            saved += 1
                        else:
                            skipped += 1
                            utils.report_error("%s: omitido %s (%s)", store, item["name"],
                                               "Oferta duplicada" if saved else result["reason"] if result else "Sin producto inequívoco")
                status, errors = "completado", 0
                message = f"Omitidos: {skipped}; para revisión: {review}; ofertas invalidadas: {invalidated}"
            except Exception as error:
                cursor.execute("ROLLBACK TO SAVEPOINT ingesta_tienda")
                saved = invalidated = created = review = 0
                utils.report_error("Error de ingesta en %s: %s", store, error)
                status, errors, message = "error", 1, str(error)
            cursor.execute(
                "UPDATE scraper_log SET fecha_fin=NOW(),productos_encontrados=%s,productos_actualizados=%s,"
                "errores=%s,estado=%s,mensaje=%s WHERE idscraper_log=%s",
                (found, saved, errors, status, message, log_id),
            )
            db.commit()
            summary["stores"][store] = {"found": found, "saved": saved, "skipped": skipped,
                                        "invalidated": invalidated, "review": review, "errors": errors}
            summary["created"] += created
            summary["offers"] += saved
            summary["skipped"] += skipped
            summary["invalidated"] += invalidated
            summary["review"] += review
        return summary
    except Exception as error:
        db.rollback()
        utils.report_error("Error general de ingesta: %s", error)
        raise
    finally:
        cursor.close()
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python live_ingest.py 'Ryzen 5 5500'")
    print(json.dumps(run(sys.argv[1]), ensure_ascii=False))
