-- 2026-09-16: Catálogo de atributos por categoría y atributos extraídos de cada oferta.
-- Ejecutar una vez en instalaciones existentes después de seleccionar la base compara_tech_gt.

use compara_tech_gt;

CREATE TABLE IF NOT EXISTS categoria_atributo (
    idcategoria_atributo INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    idcategoria INT UNSIGNED NOT NULL,
    codigo VARCHAR(80) NOT NULL,
    nombre VARCHAR(120) NOT NULL,
    tipo_valor ENUM('texto','numero','decimal','booleano','lista') NOT NULL DEFAULT 'texto',
    unidad VARCHAR(20) NULL,
    comparador ENUM('exacto','equivalente','rango','texto') NOT NULL DEFAULT 'exacto',
    requerido_busqueda TINYINT(1) NOT NULL DEFAULT 0,
    descripcion VARCHAR(500) NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    UNIQUE KEY uk_categoria_atributo (idcategoria,codigo),
    CONSTRAINT fk_categoria_atributo_categoria FOREIGN KEY (idcategoria)
        REFERENCES categoria(idcategoria) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS producto_tienda_atributo (
    idproducto_tienda_atributo BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    idproducto_tienda INT UNSIGNED NOT NULL,
    codigo VARCHAR(80) NOT NULL,
    valor_texto VARCHAR(255) NULL,
    valor_numero DECIMAL(14,3) NULL,
    unidad VARCHAR(20) NULL,
    confianza DECIMAL(5,4) NOT NULL DEFAULT 1.0000,
    fuente ENUM('regla','ia','manual') NOT NULL DEFAULT 'regla',
    extraido_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_producto_tienda_atributo (idproducto_tienda,codigo),
    CONSTRAINT fk_producto_tienda_atributo_oferta FOREIGN KEY (idproducto_tienda)
        REFERENCES producto_tienda(idproducto_tienda) ON DELETE CASCADE,
    INDEX idx_pta_codigo_numero (codigo,valor_numero),
    INDEX idx_pta_codigo_texto (codigo,valor_texto)
) ENGINE=InnoDB;

INSERT IGNORE INTO categoria_atributo (idcategoria,codigo,nombre,tipo_valor,unidad,comparador,requerido_busqueda,descripcion)
SELECT c.idcategoria,a.codigo,a.nombre,a.tipo_valor,a.unidad,a.comparador,a.requerido_busqueda,a.descripcion
FROM categoria c
JOIN (
    SELECT 'Procesadores' categoria,'brand' codigo,'Marca' nombre,'texto' tipo_valor,NULL unidad,'texto' comparador,0 requerido_busqueda,'Fabricante del procesador' descripcion UNION ALL
    SELECT 'Procesadores','model','Modelo','texto',NULL,'exacto',1,'Familia, número y sufijo del procesador' UNION ALL
    SELECT 'Procesadores','socket','Socket','texto',NULL,'exacto',0,'Socket compatible' UNION ALL
    SELECT 'Tarjetas gráficas','brand','Ensamblador','texto',NULL,'exacto',0,'Marca de la tarjeta' UNION ALL
    SELECT 'Tarjetas gráficas','model','Modelo de GPU','texto',NULL,'exacto',1,'Familia, número y variante de la GPU' UNION ALL
    SELECT 'Tarjetas gráficas','vram_gb','Memoria de video','numero','GB','exacto',0,'VRAM instalada' UNION ALL
    SELECT 'Memorias RAM','capacity_gb','Capacidad','numero','GB','equivalente',1,'Capacidad del módulo; no del equipo que lo contiene' UNION ALL
    SELECT 'Memorias RAM','memory_generation','Generación','texto',NULL,'exacto',1,'DDR3, DDR4 o DDR5' UNION ALL
    SELECT 'Memorias RAM','form_factor','Formato','texto',NULL,'exacto',0,'DIMM o SODIMM' UNION ALL
    SELECT 'Memorias RAM','speed_mts','Velocidad','numero','MT/s','rango',0,'Velocidad nominal de memoria' UNION ALL
    SELECT 'SSD','capacity_gb','Capacidad','numero','GB','equivalente',1,'480/500/512 GB y 960/1000/1024 GB son grupos comerciales equivalentes' UNION ALL
    SELECT 'SSD','storage_interface','Interfaz','texto',NULL,'exacto',1,'SATA, NVMe, SAS o USB' UNION ALL
    SELECT 'SSD','form_factor','Formato','texto',NULL,'exacto',0,'M.2 o 2.5 pulgadas' UNION ALL
    SELECT 'SSD','protocol','Protocolo','texto',NULL,'exacto',0,'PCIe 4 o PCIe 5 cuando se indique' UNION ALL
    SELECT 'Motherboards','socket','Socket','texto',NULL,'exacto',1,'Socket del procesador' UNION ALL
    SELECT 'Motherboards','chipset','Chipset','texto',NULL,'exacto',0,'Chipset de la placa' UNION ALL
    SELECT 'Motherboards','memory_generation','Generación de RAM','texto',NULL,'exacto',0,'DDR soportada' UNION ALL
    SELECT 'Laptops','brand','Marca','texto',NULL,'texto',0,'Fabricante del equipo' UNION ALL
    SELECT 'Laptops','model','Modelo','texto',NULL,'exacto',1,'Modelo de laptop' UNION ALL
    SELECT 'Laptops','ram_gb','RAM instalada','numero','GB','exacto',0,'Memoria incluida en el equipo' UNION ALL
    SELECT 'Laptops','storage_gb','Almacenamiento incluido','numero','GB','exacto',0,'Disco incluido; no identifica un SSD individual' UNION ALL
    SELECT 'Computadoras de escritorio','cpu_model','Procesador','texto',NULL,'texto',0,'Procesador incluido' UNION ALL
    SELECT 'Computadoras de escritorio','gpu_model','Tarjeta gráfica','texto',NULL,'texto',0,'GPU incluida' UNION ALL
    SELECT 'Computadoras de escritorio','storage_gb','Almacenamiento incluido','numero','GB','exacto',0,'Disco incluido' UNION ALL
    SELECT 'Monitores','screen_inches','Tamaño','decimal','pulgadas','rango',0,'Diagonal de pantalla' UNION ALL
    SELECT 'Monitores','resolution','Resolución','texto',NULL,'exacto',0,'Resolución nativa' UNION ALL
    SELECT 'Monitores','refresh_hz','Frecuencia','numero','Hz','rango',0,'Frecuencia de actualización' UNION ALL
    SELECT 'Teclados','connection','Conexión','texto',NULL,'exacto',0,'USB, Bluetooth, inalámbrico u otra' UNION ALL
    SELECT 'Teclados','layout','Distribución','texto',NULL,'exacto',0,'ANSI, ISO, español u otra' UNION ALL
    SELECT 'Teclados','switch_type','Switch','texto',NULL,'exacto',0,'Tipo de interruptor' UNION ALL
    SELECT 'Mouse','connection','Conexión','texto',NULL,'exacto',0,'Cableado, Bluetooth o inalámbrico' UNION ALL
    SELECT 'Mouse','sensor_dpi','Sensibilidad','numero','DPI','rango',0,'Sensibilidad máxima' UNION ALL
    SELECT 'Audio y audífonos','audio_type','Tipo','texto',NULL,'exacto',0,'Audífonos, bocinas, headset u otro' UNION ALL
    SELECT 'Audio y audífonos','connection','Conexión','texto',NULL,'exacto',0,'Cableado o inalámbrico' UNION ALL
    SELECT 'Webcams','resolution','Resolución','texto',NULL,'exacto',0,'Resolución de captura' UNION ALL
    SELECT 'Webcams','frame_rate','Frecuencia','numero','FPS','rango',0,'Cuadros por segundo' UNION ALL
    SELECT 'Redes','network_type','Tipo','texto',NULL,'exacto',0,'Router, switch, access point u otro' UNION ALL
    SELECT 'Redes','wifi_standard','Estándar Wi-Fi','texto',NULL,'exacto',0,'Wi-Fi 5, 6, 6E o 7' UNION ALL
    SELECT 'Impresoras','printer_type','Tipo','texto',NULL,'exacto',0,'Tinta, láser, térmica u otra' UNION ALL
    SELECT 'Impresoras','color','Color','booleano',NULL,'exacto',0,'Impresión a color' UNION ALL
    SELECT 'Tablets','storage_gb','Almacenamiento','numero','GB','equivalente',0,'Capacidad interna' UNION ALL
    SELECT 'Tablets','screen_inches','Tamaño','decimal','pulgadas','rango',0,'Diagonal de pantalla' UNION ALL
    SELECT 'Celulares','storage_gb','Almacenamiento','numero','GB','equivalente',0,'Capacidad interna' UNION ALL
    SELECT 'Celulares','ram_gb','Memoria RAM','numero','GB','exacto',0,'Memoria instalada' UNION ALL
    SELECT 'Consolas y videojuegos','platform','Plataforma','texto',NULL,'exacto',1,'Plataforma de consola o videojuego' UNION ALL
    SELECT 'Consolas y videojuegos','storage_gb','Almacenamiento','numero','GB','equivalente',0,'Capacidad interna' UNION ALL
    SELECT 'Gabinetes','form_factor','Formato','texto',NULL,'exacto',0,'ATX, microATX, mini-ITX u otro' UNION ALL
    SELECT 'Gabinetes','side_panel','Panel lateral','texto',NULL,'exacto',0,'Vidrio, malla u otro' UNION ALL
    SELECT 'Fuentes de poder','power_w','Potencia','numero','W','rango',1,'Potencia nominal' UNION ALL
    SELECT 'Fuentes de poder','efficiency','Certificación','texto',NULL,'exacto',0,'80 Plus Bronze, Gold, Platinum u otra' UNION ALL
    SELECT 'Fuentes de poder','modularity','Modularidad','texto',NULL,'exacto',0,'No modular, semi o modular' UNION ALL
    SELECT 'Refrigeración','cooling_type','Tipo','texto',NULL,'exacto',0,'Aire o líquida' UNION ALL
    SELECT 'Refrigeración','radiator_mm','Radiador','numero','mm','exacto',0,'Tamaño del radiador' UNION ALL
    SELECT 'Accesorios tecnológicos','accessory_type','Tipo','texto',NULL,'exacto',0,'Cable, adaptador, soporte, funda u otro' UNION ALL
    SELECT 'Accesorios tecnológicos','compatibility','Compatibilidad','texto',NULL,'texto',0,'Equipo o estándar compatible'
) a ON a.categoria=c.nombre;

INSERT IGNORE INTO categoria_atributo (idcategoria,codigo,nombre,tipo_valor,unidad,comparador,requerido_busqueda,descripcion)
SELECT c.idcategoria,a.codigo,a.nombre,a.tipo_valor,a.unidad,a.comparador,a.requerido_busqueda,a.descripcion
FROM categoria c
JOIN (
    SELECT 'Procesadores' categoria,'cores' codigo,'Núcleos' nombre,'numero' tipo_valor,NULL unidad,'exacto' comparador,0 requerido_busqueda,'Cantidad de núcleos' descripcion UNION ALL
    SELECT 'Procesadores','threads','Hilos','numero',NULL,'exacto',0,'Cantidad de hilos' UNION ALL
    SELECT 'Procesadores','generation','Generación','texto',NULL,'exacto',0,'Generación comercial' UNION ALL
    SELECT 'Tarjetas gráficas','chipset_brand','Fabricante del chip','texto',NULL,'exacto',0,'NVIDIA, AMD o Intel' UNION ALL
    SELECT 'Tarjetas gráficas','edition','Edición','texto',NULL,'exacto',0,'Ventus, TUF, Strix u otra' UNION ALL
    SELECT 'Motherboards','brand','Marca','texto',NULL,'exacto',0,'Fabricante de la placa' UNION ALL
    SELECT 'Motherboards','model','Modelo','texto',NULL,'exacto',1,'Modelo de la placa' UNION ALL
    SELECT 'Motherboards','form_factor','Formato','texto',NULL,'exacto',0,'ATX, microATX o mini-ITX' UNION ALL
    SELECT 'Laptops','cpu_model','Procesador','texto',NULL,'texto',0,'Procesador incluido' UNION ALL
    SELECT 'Laptops','gpu_model','Tarjeta gráfica','texto',NULL,'texto',0,'GPU incluida' UNION ALL
    SELECT 'Laptops','screen_inches','Tamaño de pantalla','decimal','pulgadas','rango',0,'Diagonal de pantalla' UNION ALL
    SELECT 'Computadoras de escritorio','brand','Marca','texto',NULL,'texto',0,'Fabricante o ensamblador' UNION ALL
    SELECT 'Computadoras de escritorio','model','Modelo','texto',NULL,'exacto',1,'Modelo del equipo' UNION ALL
    SELECT 'Computadoras de escritorio','ram_gb','RAM instalada','numero','GB','exacto',0,'Memoria incluida' UNION ALL
    SELECT 'Monitores','brand','Marca','texto',NULL,'exacto',0,'Fabricante del monitor' UNION ALL
    SELECT 'Monitores','model','Modelo','texto',NULL,'exacto',1,'Modelo del monitor' UNION ALL
    SELECT 'Monitores','panel_type','Panel','texto',NULL,'exacto',0,'IPS, VA, TN, OLED o mini LED' UNION ALL
    SELECT 'Teclados','brand','Marca','texto',NULL,'exacto',0,'Fabricante del teclado' UNION ALL
    SELECT 'Teclados','model','Modelo','texto',NULL,'exacto',1,'Modelo del teclado' UNION ALL
    SELECT 'Mouse','brand','Marca','texto',NULL,'exacto',0,'Fabricante del mouse' UNION ALL
    SELECT 'Mouse','model','Modelo','texto',NULL,'exacto',1,'Modelo del mouse' UNION ALL
    SELECT 'Mouse','buttons','Botones','numero',NULL,'exacto',0,'Número de botones' UNION ALL
    SELECT 'Audio y audífonos','brand','Marca','texto',NULL,'exacto',0,'Fabricante del equipo de audio' UNION ALL
    SELECT 'Audio y audífonos','model','Modelo','texto',NULL,'exacto',1,'Modelo de audio' UNION ALL
    SELECT 'Audio y audífonos','noise_cancelling','Cancelación de ruido','booleano',NULL,'exacto',0,'ANC o cancelación activa de ruido' UNION ALL
    SELECT 'Webcams','brand','Marca','texto',NULL,'exacto',0,'Fabricante de la webcam' UNION ALL
    SELECT 'Webcams','model','Modelo','texto',NULL,'exacto',1,'Modelo de webcam' UNION ALL
    SELECT 'Webcams','connection','Conexión','texto',NULL,'exacto',0,'USB, Bluetooth u otra' UNION ALL
    SELECT 'Redes','brand','Marca','texto',NULL,'exacto',0,'Fabricante de red' UNION ALL
    SELECT 'Redes','model','Modelo','texto',NULL,'exacto',1,'Modelo de red' UNION ALL
    SELECT 'Redes','ports','Puertos','numero',NULL,'exacto',0,'Número de puertos físicos' UNION ALL
    SELECT 'Impresoras','brand','Marca','texto',NULL,'exacto',0,'Fabricante de impresora' UNION ALL
    SELECT 'Impresoras','model','Modelo','texto',NULL,'exacto',1,'Modelo de impresora' UNION ALL
    SELECT 'Impresoras','connection','Conexión','texto',NULL,'exacto',0,'USB, Wi-Fi u otra' UNION ALL
    SELECT 'Tablets','brand','Marca','texto',NULL,'exacto',0,'Fabricante de tablet' UNION ALL
    SELECT 'Tablets','model','Modelo','texto',NULL,'exacto',1,'Modelo de tablet' UNION ALL
    SELECT 'Tablets','connectivity','Conectividad','texto',NULL,'exacto',0,'Wi-Fi o celular' UNION ALL
    SELECT 'Celulares','brand','Marca','texto',NULL,'exacto',0,'Fabricante de celular' UNION ALL
    SELECT 'Celulares','model','Modelo','texto',NULL,'exacto',1,'Modelo de celular' UNION ALL
    SELECT 'Celulares','connectivity','Conectividad','texto',NULL,'exacto',0,'4G, 5G, Wi-Fi u otra' UNION ALL
    SELECT 'Consolas y videojuegos','brand','Marca','texto',NULL,'exacto',0,'Fabricante de consola' UNION ALL
    SELECT 'Consolas y videojuegos','model','Modelo','texto',NULL,'exacto',1,'Modelo de consola o videojuego' UNION ALL
    SELECT 'Consolas y videojuegos','edition','Edición','texto',NULL,'exacto',0,'Edición física, digital, slim u otra' UNION ALL
    SELECT 'Gabinetes','brand','Marca','texto',NULL,'exacto',0,'Fabricante de gabinete' UNION ALL
    SELECT 'Gabinetes','model','Modelo','texto',NULL,'exacto',1,'Modelo de gabinete' UNION ALL
    SELECT 'Gabinetes','color','Color','texto',NULL,'exacto',0,'Color principal' UNION ALL
    SELECT 'Fuentes de poder','brand','Marca','texto',NULL,'exacto',0,'Fabricante de fuente' UNION ALL
    SELECT 'Fuentes de poder','model','Modelo','texto',NULL,'exacto',1,'Modelo de fuente' UNION ALL
    SELECT 'Refrigeración','brand','Marca','texto',NULL,'exacto',0,'Fabricante de refrigeración' UNION ALL
    SELECT 'Refrigeración','model','Modelo','texto',NULL,'exacto',1,'Modelo de refrigeración' UNION ALL
    SELECT 'Refrigeración','socket','Socket','texto',NULL,'exacto',0,'Socket compatible' UNION ALL
    SELECT 'Accesorios tecnológicos','brand','Marca','texto',NULL,'exacto',0,'Fabricante del accesorio' UNION ALL
    SELECT 'Accesorios tecnológicos','model','Modelo','texto',NULL,'exacto',1,'Modelo del accesorio' UNION ALL
    SELECT 'Accesorios tecnológicos','connection','Conexión','texto',NULL,'exacto',0,'USB, HDMI, Bluetooth u otra'
) a ON a.categoria=c.nombre;
