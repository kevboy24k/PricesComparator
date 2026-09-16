import re
from urllib.parse import quote, urljoin

from bs4 import BeautifulSoup

from core.base import StoreScraper


class PacifikoScraper(StoreScraper):
    site_url = "https://www.pacifiko.com"
    search_url = site_url + "/index.php?route=product/search&search="

    def search(self, query: str) -> list[dict]:
        html = self.fetch(self.search_url + quote(query))
        soup = BeautifulSoup(html, "html.parser")
        results = []
        seen = set()
        for card in soup.select(".product-layout[data-id]"):
            link = card.select_one("a.listing-product-link[href]")
            name_node = card.select_one("h4 a.listing-product-link")
            price_node = card.select_one(".price-new, .price-special, .price")
            if not link or not name_node or not price_node:
                continue
            product_url = urljoin(self.site_url, link["href"])
            if product_url in seen:
                continue
            seen.add(product_url)
            image_node = card.select_one(".product-image-container img, .product-card__gallery img")
            card_text = card.get_text(" ", strip=True).lower()
            # El texto visible se trunca en las tarjetas; data-name/title
            # conserva las especificaciones necesarias para la validación.
            name = (card.get("data-name") or link.get("title")
                    or (image_node.get("alt") if image_node else None)
                    or name_node.get_text(" ", strip=True))
            results.append({
                "name": name.strip(),
                "sku": card.get("data-id"),
                "price": self.parse_price(price_node.get_text(" ", strip=True)),
                "currency": "GTQ",
                "available": "no disponible" not in card_text and "agotado" not in card_text,
                "url": product_url,
                "image": (image_node.get("data-src") or image_node.get("src")) if image_node else None,
            })
        return results

    def get_product(self, url: str) -> dict:
        html = self.fetch(url)
        soup = BeautifulSoup(html, "html.parser")
        name_node = soup.select_one("h1")
        price_node = soup.select_one(".product_page_price .price, .product_page_price")
        pid_node = soup.find(string=lambda value: value and "PID" in value)
        image_node = soup.select_one('meta[property="og:image"]')
        text = soup.get_text(" ", strip=True).lower()
        return {
            "name": name_node.get_text(" ", strip=True) if name_node else None,
            "sku": pid_node.parent.get_text(" ", strip=True).replace("PID", "").strip() if pid_node else None,
            "price": self.parse_price(price_node.get_text(" ", strip=True)) if price_node else None,
            "currency": "GTQ",
            "available": "actualmente no disponible" not in text and "agotado" not in text,
            "url": url,
            "image": image_node.get("content") if image_node else None,
        }

    @staticmethod
    def parse_price(value: str) -> float | None:
        found = re.search(r"Q\s*([\d,]+)(?:\s*\.\s*(\d{2}))?", value)
        if not found:
            return None
        return float(f"{found.group(1).replace(',', '')}.{found.group(2) or '00'}")
