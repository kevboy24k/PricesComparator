-- Agrega los datos originales necesarios para revisar y aprobar coincidencias.
ALTER TABLE producto_match_pendiente
    ADD COLUMN idtienda INT UNSIGNED NULL AFTER idmatch,
    ADD COLUMN nombre_tienda VARCHAR(255) NULL AFTER nombre_detectado,
    ADD COLUMN sku_tienda VARCHAR(150) NULL AFTER nombre_tienda,
    ADD COLUMN url VARCHAR(500) NULL AFTER sku_tienda,
    ADD COLUMN imagen VARCHAR(500) NULL AFTER url,
    ADD COLUMN precio DECIMAL(12,2) NULL AFTER imagen,
    ADD COLUMN moneda CHAR(3) NULL DEFAULT 'GTQ' AFTER precio,
    ADD COLUMN disponible TINYINT(1) NULL DEFAULT 0 AFTER moneda,
    ADD CONSTRAINT fk_match_tienda FOREIGN KEY (idtienda)
        REFERENCES tienda(idtienda) ON DELETE SET NULL;
