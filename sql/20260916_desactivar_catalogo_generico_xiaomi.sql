-- Corrige el producto automático genérico AUTO-XIAOMI creado por una búsqueda
-- de marca. Se desactiva sin borrar las ofertas ni el historial de precios.
START TRANSACTION;

UPDATE producto_tienda AS pt
INNER JOIN producto AS p ON p.idproducto = pt.idproducto
SET pt.estado = 0
WHERE p.sku_global = 'AUTO-XIAOMI'
  AND p.nombre = 'Xiaomi';

UPDATE producto
SET estado = 0
WHERE sku_global = 'AUTO-XIAOMI'
  AND nombre = 'Xiaomi';

COMMIT;
