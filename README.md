# Compara Tech GT

MVP para comparar precios de tecnología en tiendas de Guatemala. Incluye frontend vanilla, API PHP 8.2/PDO, MySQL/MariaDB, historial de precios y una base para scrapers Python separados por tienda.

## Requisitos

- PHP 8.2+ con PDO MySQL y Apache `mod_rewrite`.
- MySQL 8 o MariaDB.
- Python 3.10+ para scrapers.

## Instalación

1. Copia `.env.example` a `.env` y completa las credenciales.
2. Ejecuta `database/schema.sql` y después `database/seed.sql` en MySQL.
3. Sirve el proyecto desde Apache/XAMPP. La interfaz queda en `/PricesComparator/` y la API en `/PricesComparator/api/productos`.
4. Para probar la base de scrapers: `cd scrapers && pip install -r requirements.txt && python main.py kemik "Ryzen 5 7600"`.

La semilla contiene datos demo para validar la interfaz sin depender de tiendas externas. Las clases de tienda están preparadas para implementarse después de revisar robots.txt, APIs públicas y datos estructurados; no evaden CAPTCHA ni mecanismos anti-bot.

## API

`GET api/productos?q=ryzen+7600`, `GET api/productos/{id}`, `GET api/productos/{id}/precios`, `GET api/productos/{id}/historial`, `GET api/tiendas` y `GET api/categorias`. Todas las respuestas siguen `{success, data, message}`.

## Próxima integración

El proceso de ingesta debe leer los resultados comunes de cada scraper, obtener o crear la relación `producto_tienda` y agregar un nuevo registro en `precio` por cada actualización. El esquema conserva los registros anteriores para la gráfica y auditoría.


## comandos

cd /Applications/XAMPP/xamppfiles/htdocs/PricesComparator/scrapers
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py kemik "Ryzen 5 7600"