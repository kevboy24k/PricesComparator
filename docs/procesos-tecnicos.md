# Documentación técnica de procesos

## 1. Propósito y alcance

**Compara Tech GT** compara precios de productos tecnológicos entre varias
tiendas. La plataforma acepta una consulta en lenguaje natural, busca ofertas
actuales, valida que correspondan al producto solicitado, conserva precios e
imágenes y presenta las ofertas compatibles al usuario.

Este documento describe el comportamiento implementado actualmente. No es una
especificación de una futura arquitectura asíncrona: una búsqueda de texto
dispara la ingesta en vivo y la respuesta HTTP espera a que esta finalice.

## 2. Arquitectura y componentes

```text
Navegador
  └─ index.html + frontend/js/app.js + frontend/css/app.css
       └─ GET /api/productos?q=...
            └─ backend/api.php (PHP)
                 ├─ MySQL/MariaDB mediante PDO
                 └─ scrapers/live_ingest.py (Python)
                      ├─ Scrapers: Kemik, Intelaf y Pacifiko
                      ├─ Normalización, catálogo de atributos y matching
                      └─ MySQL/MariaDB mediante mysql-connector
```

| Componente | Responsabilidad principal |
| --- | --- |
| `index.html` | Estructura de la interfaz, buscador, listado, detalle y categorías. |
| `frontend/js/app.js` | Solicitudes a la API, indicador de carga, renderizado, foco y gráfico de historial. |
| `backend/api.php` | Enrutamiento HTTP, consulta de datos y ejecución controlada de la ingesta en vivo. |
| `scrapers/stores/*.py` | Obtención y normalización de resultados de cada tienda. |
| `scrapers/live_ingest.py` | Orquestación por búsqueda, validación y persistencia transaccional. |
| `scrapers/core/product_matcher.py` | Clasificación de tipo de artículo y resolución de coincidencias. |
| `scrapers/core/technology_catalog.py` | Catálogo de atributos, extracción y equivalencias permitidas. |
| MySQL/MariaDB | Catálogo, ofertas, atributos, precios históricos y auditoría. |

## 3. Proceso de búsqueda desde la interfaz

### 3.1 Inicio

Una búsqueda puede iniciarse por:

- Enviar el formulario principal.
- Elegir una sugerencia.
- Pulsar una categoría.
- Cambiar el orden de los resultados ya cargados.

Al enviar una consulta con texto, `loadProducts()` hace lo siguiente:

1. Incrementa un identificador de solicitud. Esto evita que una respuesta vieja
   reemplace a una búsqueda más reciente.
2. Muestra el indicador bajo el buscador: **“Buscando y comparando precios…”**.
3. Deshabilita temporalmente el botón Buscar y marca el formulario y el listado
   como ocupados mediante atributos ARIA.
4. Solicita `GET api/productos?q=<consulta codificada>`.
5. Al recibir una respuesta, oculta el indicador, habilita el botón y renderiza
   las tarjetas o el mensaje de resultado vacío/error.
6. Para búsquedas iniciadas por usuario, desplaza la ventana a `#resultados` y
   da foco programático a la sección para que teclado y lectores de pantalla
   lleguen al contenido actualizado.

La carga inicial sin texto obtiene el catálogo existente, pero no muestra el
indicador de búsqueda bajo el formulario porque no dispara una consulta activa.

### 3.2 Respuesta y tarjetas de producto

La API responde siempre con este envoltorio:

```json
{
  "success": true,
  "data": [],
  "message": null
}
```

Cada tarjeta muestra imagen, nombre, marca, categoría, precio mínimo vigente,
número de tiendas y el botón **Comparar precios**. Si el producto no tiene
imagen se utiliza un placeholder.

Al abrir el detalle se solicitan, en paralelo lógico dentro de la función de
interfaz, los datos del producto y su historial. Cada oferta de tienda muestra
su miniatura (`producto_tienda.imagen`); si no está disponible se usa la imagen
general de `producto` y, como último recurso, el placeholder.

### 3.3 Endpoints consumidos

| Endpoint | Uso |
| --- | --- |
| `GET /api/productos` | Catálogo y ordenamiento de resultados guardados. |
| `GET /api/productos?q=...` | Ingesta en vivo seguida del listado filtrado. |
| `GET /api/productos/{id}` | Producto, ofertas activas, atributos y especificaciones. |
| `GET /api/productos/{id}/historial` | Serie diaria del precio mínimo para la gráfica. |
| `GET /api/productos/{id}/precios` | Precios por tienda. |
| `GET /api/categorias` | Botones de categorías del buscador. |
| `GET /api/tiendas` | Catálogo de tiendas activas. |

## 4. Proceso de búsqueda e ingesta en vivo

### 4.1 Activación desde PHP

En `backend/api.php`, una solicitud a `GET /api/productos?q=...` ejecuta:

```text
PHP → proc_open(python live_ingest.py "consulta") → espera finalización
```

El intérprete configurado es `scrapers/.venv/bin/python`; si no existe, se usa
`python3`. La consulta se protege con `escapeshellarg()` antes de crear el
proceso. Los errores del proceso se registran en el log de PHP y no se entregan
al navegador con detalles internos.

Una vez que Python termina, PHP consulta el catálogo local. Divide la consulta
en tokens y exige que **cada token** aparezca en al menos uno de estos campos:

- `producto.nombre`
- `producto.modelo`
- `marca.nombre`
- `producto_tienda.nombre_tienda`

El resultado se ordena por precio mínimo, precio descendente o nombre, según el
parámetro `sort`.

### 4.2 Construcción del perfil de búsqueda

`build_search_profile()` convierte una consulta libre en una estructura:

```text
"SSD SATA 500 GB 2.5"
  → categoría: storage
  → atributos: interfaz=sata, capacidad=500 GB, formato=2.5
  → capacidades equivalentes permitidas: 480, 500, 512 GB
```

El catálogo reconoce las categorías: procesadores, GPU, RAM, SSD, motherboards,
laptops, PC de escritorio, monitores, teclados, mouse, audio, webcams, redes,
impresoras, tablets, teléfonos, consolas, gabinetes, fuentes, refrigeración y
accesorios.

Los atributos se extraen solo si aparecen explícitamente. Ejemplos:

| Categoría | Atributos relevantes |
| --- | --- |
| SSD | Capacidad, interfaz SATA/NVMe/SAS/USB, formato y protocolo PCIe. |
| RAM | Capacidad, DDR, velocidad y DIMM/SODIMM. |
| Monitor | Pulgadas, resolución, Hz y tipo de panel. |
| Laptop/PC | Marca, modelo, CPU, GPU, RAM, almacenamiento y pantalla cuando aplique. |
| Fuente | Watts, certificación 80 Plus y modularidad. |
| GPU | Marca del chip, modelo, VRAM y edición. |

Las equivalencias de capacidad solo se aplican a RAM y SSD. Por ejemplo, 1 TB
puede buscar 960, 1000 y 1024 GB. Esta expansión **no** relaja interfaz,
generación DDR, tipo de producto ni modelo; por eso un SSD SATA no puede
aceptar un NVMe y una laptop no se acepta como un SSD.

### 4.3 Captura de datos desde tiendas

Para cada tienda activa se crea un registro `scraper_log` con estado
`ejecutando`. Se ejecuta el scraper correspondiente para la consulta original
y para las variantes de búsqueda permitidas por el perfil.

Cada scraper debe devolver objetos con este contrato mínimo:

```json
{
  "name": "Nombre publicado por la tienda",
  "sku": "SKU opcional",
  "price": 689.00,
  "currency": "GTQ",
  "available": true,
  "url": "https://tienda.example/producto",
  "image": "https://tienda.example/imagen.jpg"
}
```

La ingesta agrupa resultados por URL para evitar repetir la misma oferta cuando
una variante de consulta devuelve el mismo producto.

### 4.4 Validación inicial de una oferta

Antes de comparar nombres, `valid_offer()` exige:

- Nombre no vacío.
- URL HTTP o HTTPS válida.
- Precio numérico, finito y mayor que cero.

Después, `relevant()` valida que el tipo de artículo de la oferta coincida con
el tipo solicitado. Se rechazan explícitamente, según el contexto, laptops,
PC armadas, combos, accesorios y placas madre que solamente mencionan el
componente buscado.

Ejemplo: ante `SSD SATA 500 GB`, se descartan una laptop con SSD, un case con
SSD incluido, un SSD NVMe y un SSD SATA de capacidad incompatible. Un SSD SATA
de 480 o 512 GB puede pasar únicamente por la equivalencia comercial permitida.

### 4.5 Resolución de coincidencias

El matching no depende de una lista cerrada de modelos. Combina:

1. Normalización: minúsculas, sin acentos y separación uniforme de tokens.
2. Identificadores/anclas: SKU, modelos, números y capacidades distintivas.
3. Cobertura de tokens relevantes.
4. Similitud de texto.
5. Reglas estrictas para variantes de CPU y GPU, como `X`, `X3D`, `Ti`,
   `Super`, `XT` o `KF`.
6. Comparación de atributos extraídos cuando la consulta los aporta.

El resultado se clasifica como:

| Clasificación | Acción |
| --- | --- |
| `automatico` | La oferta puede asociarse y persistirse. |
| Intermedia (65 a menos de 90) | No se publica automáticamente; se guarda como candidata para revisión. |
| Incompatible o insuficiente | Se omite y queda registrado como advertencia. |

Las incompatibilidades explícitas tienen prioridad sobre una puntuación alta.
Esto evita que una coincidencia textual atractiva sobrescriba una diferencia
crítica de tipo, interfaz, capacidad o variante.

### 4.6 Creación o localización del producto de catálogo

La consulta del usuario define la identidad del producto, no el primer
resultado devuelto por una tienda.

- Si el catálogo ya contiene una coincidencia automática, se utiliza ese
  producto.
- Si no existe y la primera oferta compatible confirma una categoría
  tecnológica reconocida, se crea un producto con SKU global `AUTO-...`.
- Si hay ambigüedad alta o no hay identidad verificable, no se crea producto.

Una marca sola o una combinación de marca y categoría no tiene identidad de
producto suficiente. Por ejemplo, `Xiaomi`, `Audífonos` y `Audífonos Xiaomi`
pueden servir como consultas exploratorias, pero no crean ni reutilizan un
producto canónico. Esta regla evita que modelos distintos se acumulen bajo un
contenedor genérico como `AUTO-XIAOMI`.

Esto permite admitir productos nuevos sin convertir resultados imprecisos en
productos del catálogo.

### 4.7 Persistencia, auditoría e historial

Para cada tienda se usa un `SAVEPOINT`. Si la captura o validación de una tienda
falla, se revierte únicamente su trabajo y la ingesta continúa con las demás.

```text
Oferta válida
  ├─ upsert producto_tienda
  │    ├─ nombre, SKU de tienda, URL, imagen, disponibilidad
  │    └─ estado=1 (reactiva una oferta antes desactivada)
  ├─ upsert producto_tienda_atributo
  │    └─ valor, unidad, confianza=1.0, fuente=regla
  └─ insert precio solo si cambió precio o disponibilidad
```

Hay una relación activa por `producto + tienda`. Si una tienda devuelve varias
ofertas compatibles, se conserva la disponible más económica; si ninguna está
disponible, se conserva la agotada más económica.

`revalidate_offers()` revisa las asociaciones activas previas de la tienda. Si
una ya no pasa las reglas actuales, cambia `producto_tienda.estado` a `0`, pero
no borra los precios históricos.

Al terminar cada tienda se actualiza `scraper_log` con fecha final, cantidad de
productos encontrados, ofertas guardadas, errores, estado y resumen. Las
validaciones y omisiones de Python se registran mediante
`utils.report_error()`.

## 5. Modelo de datos que interviene

| Tabla | Rol en el proceso |
| --- | --- |
| `categoria` | Clasificación funcional del producto. |
| `marca` | Marca normalizada del catálogo. |
| `producto` | Identidad canónica: nombre, modelo, SKU global e imagen general. |
| `producto_tienda` | Oferta de una tienda: nombre publicado, URL, imagen y disponibilidad. |
| `precio` | Histórico inmutable de cambios de precio y disponibilidad. |
| `producto_especificacion` | Especificaciones generales del producto. |
| `categoria_atributo` | Vocabulario de atributos válidos por categoría. |
| `producto_tienda_atributo` | Atributos extraídos para una oferta, con confianza y fuente. |
| `producto_match_pendiente` | Evidencia de coincidencias no concluyentes para revisión humana. |
| `scraper_log` | Auditoría de cada ejecución por tienda. |

## 6. Flujo completo de ejemplo

Consulta: **`Monitor 27 pulgadas QHD 165Hz IPS`**

```text
1. Navegador muestra spinner y solicita /api/productos?q=...
2. PHP ejecuta live_ingest.py y espera su resultado.
3. Python detecta categoría monitor y atributos: 27, QHD, 165 Hz, IPS.
4. Cada scraper consulta su tienda; las URLs duplicadas se consolidan.
5. Se rechaza cualquier TV, laptop, monitor FHD, 144 Hz o panel distinto
   cuando el dato es explícito.
6. Las ofertas inequívocas se asocian al producto y guardan sus atributos,
   imagen, disponibilidad y un nuevo precio solo si cambió.
7. PHP consulta el catálogo actualizado y devuelve los productos que contienen
   todos los tokens solicitados.
8. El navegador renderiza tarjetas, enfoca Resultados y permite abrir ofertas.
```

## 7. Manejo de errores y límites actuales

### Errores controlados

- Error de una tienda: rollback al `SAVEPOINT`, actualización de `scraper_log`
  como `error` y continuación con las otras tiendas.
- Error general de base: rollback de la operación principal y registro con
  `utils.report_error()`.
- Error de API: se registra con `error_log()` y el navegador recibe una
  respuesta JSON genérica de error interno.
- Sin resultados: se devuelve una lista vacía; no es un error técnico.

### Límites que deben considerarse al publicar una beta

- La ingesta se ejecuta dentro de la solicitud web. Una búsqueda lenta mantiene
  ocupado el proceso PHP y al usuario esperando hasta que termine.
- No hay caché, cola, límite de consultas ni autenticación de beta en el
  endpoint actual. Una URL pública permite que terceros disparen scrapers.
- La API permite cualquier origen mediante `Access-Control-Allow-Origin: *`.
- Se debe respetar la política de cada tienda. Los scrapers no deben eludir
  CAPTCHA, mecanismos anti-bot ni restricciones de acceso.

Para una versión con mayor tráfico conviene mover la ingesta a una cola o worker,
registrar trabajos por consulta, responder el catálogo de inmediato y actualizar
la interfaz mediante polling o eventos. También se recomienda proteger el sitio
de beta con autenticación y aplicar rate limiting.

## 8. Operación y pruebas

### Requisitos

- Apache/PHP 8.2+ con PDO MySQL y `mod_rewrite`.
- MySQL 8 o MariaDB.
- Python 3.10+ y dependencias de `scrapers/requirements.txt`.
- Archivo `.env` con `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y
  `DB_PASSWORD`.

### Comandos útiles

```sh
# Entorno Python
cd /Applications/XAMPP/xamppfiles/htdocs/PricesComparator/scrapers
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Ingesta de una tienda o de todas las tiendas
.venv/bin/python ingest.py intelaf "RTX 5070"
.venv/bin/python live_ingest.py "SSD SATA 500 GB 2.5"

# Pruebas de regresión
cd /Applications/XAMPP/xamppfiles/htdocs/PricesComparator
PYTHONPATH=scrapers scrapers/.venv/bin/python -m unittest discover -s scrapers/tests -v
```

### Lista de verificación manual

1. Abrir la página y confirmar que carga el catálogo inicial.
2. Buscar una consulta específica y confirmar que aparece y desaparece el
   spinner bajo el buscador.
3. Confirmar el desplazamiento y foco en la sección Resultados.
4. Abrir una tarjeta y validar miniaturas, URL, precio, disponibilidad e
   historial de las ofertas.
5. Revisar `scraper_log` y los logs de PHP/Python tras una búsqueda.
6. Probar consultas incompatibles, por ejemplo `SSD SATA 500 GB` y verificar
   que no aparezcan laptops ni SSD NVMe.

## 9. Evolución hacia IA

La IA debe ser una capa de apoyo, no un reemplazo de las restricciones duras.
Las reglas explícitas de tipo, modelo, capacidad e interfaz deben seguir
descartando incompatibilidades antes de llamar a un modelo.

El origen de datos para un modelo supervisado es `producto_match_pendiente`
después de revisión humana. Solo los pares aprobados/rechazados con trazabilidad
deben utilizarse para entrenamiento y evaluación. Una IA futura puede decidir
casos intermedios, siempre registrando su puntuación, evidencia, versión del
modelo y decisión; nunca debe aceptar automáticamente una oferta que viola una
regla técnica explícita.
