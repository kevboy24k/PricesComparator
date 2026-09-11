-- 2026-09-11: categorías adicionales para el catálogo exclusivo de tecnología.
-- Es seguro ejecutarlo más de una vez.
USE compara_tech_gt;

INSERT IGNORE INTO categoria (nombre) VALUES
    ('Computadoras de escritorio'),
    ('Teclados'),
    ('Mouse'),
    ('Audio y audífonos'),
    ('Webcams'),
    ('Redes'),
    ('Impresoras'),
    ('Tablets'),
    ('Celulares'),
    ('Consolas y videojuegos'),
    ('Gabinetes'),
    ('Fuentes de poder'),
    ('Refrigeración'),
    ('Accesorios tecnológicos');
