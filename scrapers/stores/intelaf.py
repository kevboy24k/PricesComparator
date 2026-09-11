import re
import time
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup

from core.base import StoreScraper


class IntelafScraper(StoreScraper):
    api_url = "https://api.intelaf.com:2053/app/api/producto/busqueda"
    site_url = "https://www.intelaf.com"

    def search(self, query: str) -> list[dict]:
        payload = {
            "SucursalesCodigo": [],
            "CantidadMaxima": 30,
            "Instruccion": {"nombre": "busqueda", "valor": ""},
            "PrecioMenor": 0,
            "PrecioMayor": 0,
            "Acendente": True,
            "Categorias": [],
            "Marcas": [],
            "Pagina": 1,
            "Orden": "default",
            "Query": query,
        }
        headers = {
            "content-type": "application/json",
            "app-name": "intelaf-web",
            "app-version": "1.2.2",
            "User-Agent": self.user_agent,
        }
        response = None
        for attempt in range(3):
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=25)
            if response.status_code < 500:
                break
            time.sleep(1.5 * (attempt + 1))
        response.raise_for_status()
        body = response.json()
        products = body.get("Response", {}).get("Productos", [])
        results = []
        for product in products:
            code = str(product.get("Codigo") or "").strip()
            price = product.get("PrecioDescuento") or product.get("PrecioNormal")
            stock = product.get("Existencia") or []
            results.append({
                "name": str(product.get("Descripcion") or "").strip(),
                "sku": code or None,
                "price": float(price) if price else None,
                "currency": "GTQ",
                "available": any(float(x.get("Existencia", 0) or 0) > 0 for x in stock),
                "url": urljoin(self.site_url, f"/precios_stock_detallado/{quote(code.lower())}"),
                "image": product.get("Imagen"),
            })
        return results

    def get_product(self, url: str) -> dict:
        html = self.fetch(url)
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)
        name_node = soup.select_one("h1")
        code_node = soup.select_one(".detalle-producto span")
        price_node = soup.select_one(".precio-promo p, .precio-normal p")
        image_node = soup.select_one('meta[property="og:image"], img[alt*="Selected Product"]')
        return {
            "name": name_node.get_text(" ", strip=True) if name_node else None,
            "sku": code_node.get_text(" ", strip=True) if code_node else None,
            "price": self.parse_price(price_node.get_text(" ", strip=True)) if price_node else None,
            "currency": "GTQ",
            "available": "no disponible" not in text.lower(),
            "url": url,
            "image": image_node.get("content") if image_node and image_node.name == "meta" else image_node.get("src") if image_node else None,
        }

    @staticmethod
    def parse_price(value: str) -> float | None:
        found = re.search(r"Q\s*([\d,]+)(?:\s*\.\s*(\d{2}))?", value)
        if not found:
            return None
        return float(f"{found.group(1).replace(',', '')}.{found.group(2) or '00'}")
