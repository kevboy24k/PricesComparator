# Compara Tech GT

MVP para comparar precios de tecnología en tiendas de Guatemala. Incluye frontend vanilla, API PHP 8.2/PDO, MySQL/MariaDB, historial de precios y una base para scrapers Python separados por tienda.

## Requisitos

- PHP 8.2+ con PDO MySQL y Apache `mod_rewrite`.
- MySQL 8 o MariaDB.
- Python 3.10+ para scrapers.

## Instalación

1. Copia `.env.example` a `.env` y completa las credenciales.
2. Ejecuta `database/schema.sql` y después `database/seed.sql` en MySQL.
   En una instalación existente ejecuta también `sql/20260911_categorias_tecnologicas.sql` y
   `sql/20260916_catalogo_atributos_tecnologicos.sql`.
3. Sirve el proyecto desde Apache/XAMPP. La interfaz queda en `/PricesComparator/` y la API en `/PricesComparator/api/productos`.
4. Para probar la base de scrapers: `cd scrapers && pip install -r requirements.txt && python main.py kemik "Ryzen 5 7600"`.

La semilla contiene datos demo para validar la interfaz sin depender de tiendas externas. Las clases de tienda están preparadas para implementarse después de revisar robots.txt, APIs públicas y datos estructurados; no evaden CAPTCHA ni mecanismos anti-bot.

## API

`GET api/productos?q=ryzen+7600`, `GET api/productos/{id}`, `GET api/productos/{id}/precios`, `GET api/productos/{id}/historial`, `GET api/tiendas` y `GET api/categorias`. Todas las respuestas siguen `{success, data, message}`.

## Ingesta

El proceso de ingesta valida los resultados de cada scraper, obtiene o crea la relación `producto_tienda` y agrega un registro en `precio` cuando cambia el precio o la disponibilidad. El esquema conserva los registros anteriores para la gráfica y auditoría. Las reglas automáticas se describen al final de este documento.


## comandos

cd /Applications/XAMPP/xamppfiles/htdocs/PricesComparator/scrapers
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py kemik "Ryzen 5 7600"
## Ingesta automática y coincidencias

Las búsquedas web (`scrapers/live_ingest.py`) y la ingesta por tienda utilizan el mismo flujo:

```sh
cd scrapers
.venv/bin/python ingest.py intelaf "RTX 5070"
.venv/bin/python live_ingest.py "Ryzen 5 7600"
```

Se comprueba el tipo de artículo antes de comparar modelos. Una laptop, PC, combo,
placa madre o accesorio que mencione una GPU/procesador no se asocia al componente.
Se distinguen familia, número y variantes como Ti, Super, XT, X3D y KF, y se respetan
capacidad, fabricante y edición cuando el producto buscado los especifica.

Solo se guardan coincidencias automáticas inequívocas. El resolvedor combina
identificadores del modelo, capacidades, tokens distintivos y similitud textual;
no requiere una lista de marcas o modelos para reconocer una búsqueda nueva como
`G502 X`. Las incompatibilidades explícitas se rechazan antes de calcular la
similitud. Los casos con puntuación intermedia se conservan en
`producto_match_pendiente`: aprobarlos o rechazarlos con `matches.py` crea el
historial etiquetado necesario para entrenar un modelo supervisado más adelante.
Cada ejecución por tienda deja un resumen en `scraper_log`. Una falla revierte los
cambios de esa tienda y permite continuar con las demás.

La búsqueda define el producto del catálogo; el primer resultado no define su identidad.
Si falta un producto de una categoría tecnológica reconocida, se crea automáticamente
solo después de validar que la oferta corresponde a la categoría. En RAM y
almacenamiento se validan DDR, capacidad e interfaz indicadas; por ejemplo,
`Memoria RAM DDR5 de 8GB` no puede asociarse con una laptop ni con memoria DDR4,
y `SSD NVMe 1TB` no puede asociarse con un SSD SATA o de 512GB. Las búsquedas
fuera de las categorías tecnológicas reconocidas no crean productos.
Como el esquema admite una oferta por producto/tienda, se elige la oferta disponible
más económica entre las compatibles (o la más económica agotada si no hay disponibles).
En cada ingesta se revalidan las asociaciones activas de la tienda; las inválidas se
desactivan sin borrar precios históricos. Las ofertas válidas pueden reactivarlas y
actualizan la imagen de los productos creados automáticamente.

## Catálogo de atributos tecnológicos

`scrapers/core/technology_catalog.py` centraliza los atributos relevantes de cada
categoría tecnológica y `categoria_atributo` los deja disponibles en la base para
administración e integraciones futuras de IA. Cada oferta aceptada conserva los
atributos detectados, su confianza y origen (`regla`, `ia` o `manual`) en
`producto_tienda_atributo`.

Los perfiles se aplican a todas las categorías del catálogo: componentes,
equipos, monitores, periféricos, red, impresión, móviles, consolas, gabinetes,
fuentes, refrigeración y accesorios. Solo se validan los atributos que el usuario
incluye en la consulta; por ejemplo, un monitor puede exigir tamaño, resolución,
Hz y panel, mientras una fuente puede exigir watts y certificación.

Las equivalencias comerciales de capacidad se habilitan únicamente para SSD y
RAM: una consulta `SSD SATA 500 GB` busca 480, 500 y 512 GB, pero mantiene SATA
como requisito y descarta NVMe, laptops, PCs, combos y accesorios. Los monitores
también expanden sinónimos de resolución (`Full HD`/`FHD`/`1080p`/`1920x1080`,
por ejemplo). La capacidad y especificación real detectada se conserva por oferta;
una equivalencia solo amplía la búsqueda, no modifica sus datos.

Pruebas de regresión, con tiendas y base de datos simuladas:

```sh
PYTHONPATH=scrapers scrapers/.venv/bin/python -m unittest discover -s scrapers/tests -v
```

## Evolución hacia IA / machine learning

No se debe entrenar un modelo con datos no etiquetados: convertiría errores de
emparejamiento en datos de entrenamiento. Primero se revisan las entradas de
`producto_match_pendiente` con `python matches.py list`, y se aprueban o rechazan.
Cuando haya suficientes pares reales de distintas tiendas y categorías, ese
historial permite entrenar y evaluar un clasificador. Un servicio de IA puede
usarse después como desempate de los casos intermedios, nunca para sobrescribir una
incompatibilidad explícita ni sin registrar la decisión y su evidencia.
