import argparse
import logging

from ingest import connect_db

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def list_pending() -> None:
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT m.idmatch,m.nombre_detectado,t.nombre tienda,m.precio,m.url "
        "FROM producto_match_pendiente m LEFT JOIN tienda t ON t.idtienda=m.idtienda "
        "WHERE m.estado='pendiente' ORDER BY m.creado_en DESC"
    )
    rows = cursor.fetchall()
    if not rows:
        print("No hay coincidencias pendientes.")
    for row in rows:
        print(f"[{row['idmatch']}] {row['tienda'] or '-'} | "
              f"Q{row['precio'] or '-'} | {row['nombre_detectado']} | {row['url'] or '-'}")
    cursor.close()
    db.close()


def approve(match_id: int, product_id: int) -> None:
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM producto_match_pendiente "
            "WHERE idmatch=%s AND estado='pendiente' FOR UPDATE", (match_id,)
        )
        match = cursor.fetchone()
        if not match:
            raise ValueError("La coincidencia no existe o ya fue procesada")
        if not match["idtienda"] or not match["url"] or match["precio"] is None:
            raise ValueError("La coincidencia no tiene datos completos; ejecuta una ingesta nueva")

        cursor.execute(
            "SELECT idproducto FROM producto WHERE idproducto=%s AND estado=1", (product_id,)
        )
        if not cursor.fetchone():
            raise ValueError("El producto indicado no existe o está inactivo")

        cursor.execute(
            "INSERT INTO producto_tienda "
            "(idproducto,idtienda,nombre_tienda,sku_tienda,url,imagen,disponibilidad) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE nombre_tienda=VALUES(nombre_tienda), "
            "url=VALUES(url),imagen=VALUES(imagen),disponibilidad=VALUES(disponibilidad),"
            "actualizado_en=NOW()",
            (product_id, match["idtienda"], match["nombre_tienda"] or match["nombre_detectado"],
             match["sku_tienda"], match["url"], match["imagen"], int(match["disponible"] or 0)),
        )
        cursor.execute(
            "SELECT idproducto_tienda FROM producto_tienda WHERE idproducto=%s AND idtienda=%s",
            (product_id, match["idtienda"]),
        )
        product_store_id = cursor.fetchone()["idproducto_tienda"]
        cursor.execute(
            "INSERT INTO precio (idproducto_tienda,precio,moneda,disponible) VALUES (%s,%s,%s,%s)",
            (product_store_id, match["precio"], match["moneda"] or "GTQ", int(match["disponible"] or 0)),
        )
        cursor.execute(
            "UPDATE producto_match_pendiente SET idproducto_tienda=%s,estado='aprobado' "
            "WHERE idmatch=%s", (product_store_id, match_id)
        )
        db.commit()
        logging.info("Coincidencia %s aprobada para producto %s", match_id, product_id)
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()
        db.close()


def reject(match_id: int) -> None:
    db = connect_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE producto_match_pendiente SET estado='rechazado' "
        "WHERE idmatch=%s AND estado='pendiente'", (match_id,)
    )
    db.commit()
    print("Coincidencia rechazada." if cursor.rowcount else "No existe una coincidencia pendiente con ese ID.")
    cursor.close()
    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Revisión de coincidencias de scrapers")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="listar coincidencias pendientes")
    approve_parser = subparsers.add_parser("approve", help="aprobar y asociar a un producto")
    approve_parser.add_argument("match_id", type=int)
    approve_parser.add_argument("product_id", type=int)
    reject_parser = subparsers.add_parser("reject", help="rechazar coincidencia")
    reject_parser.add_argument("match_id", type=int)
    args = parser.parse_args()

    if args.command == "list":
        list_pending()
    elif args.command == "approve":
        approve(args.match_id, args.product_id)
    else:
        reject(args.match_id)
