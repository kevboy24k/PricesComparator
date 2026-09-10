from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import re
from core.base import StoreScraper


class KemikScraper(StoreScraper):
    search_url = "https://www.kemik.gt/search"

    def search(self, query: str) -> list[dict]:
        url = f"{self.search_url}?query={quote(query)}"
        html = self.fetch(url)
        soup = BeautifulSoup(html, "html.parser")

        products = []

        seen = set()
        # Kemik usa enlaces con h3 y data-component="Price" para sus tarjetas.
        for link_node in soup.select("a[href]"):
            name_node = link_node.select_one("h3")
            price_node = link_node.select_one('[data-component="Price"]')

            if not name_node or not price_node or not link_node:
                continue

            product_url = urljoin("https://www.kemik.gt", link_node["href"])
            if product_url in seen:
                continue
            seen.add(product_url)
            image_node = link_node.select_one("img")
            card_text = link_node.get_text(" ", strip=True).lower()

            products.append({
                "name": name_node.get_text(" ", strip=True),
                "sku": None,
                "price": self.parse_price(price_node.get_text(" ", strip=True)),
                "currency": "GTQ",
                "available": "agotado" not in card_text,
                "url": product_url,
                "image": urljoin("https://www.kemik.gt", image_node["src"])
                    if image_node and image_node.get("src") else None,
            })

        return products

    @staticmethod
    def parse_price(value: str) -> float | None:
        match = re.search(r"Q\s*([\d,]+)(?:\s*\.\s*(\d{2}))?", value)
        if not match:
            return None
        try:
            integer = match.group(1).replace(",", "")
            cents = match.group(2) or "00"
            return float(f"{integer}.{cents}")
        except ValueError:
            return None

    def get_product(self, url: str) -> dict:
        html = self.fetch(url)
        soup = BeautifulSoup(html, "html.parser")
        name_node = soup.select_one("h1")
        price_node = soup.select_one('[data-component="Price"]')
        image_node = soup.select_one('img[alt="Product image"], img[alt="Product thumbnail"]')
        return {
            "name": name_node.get_text(" ", strip=True) if name_node else None,
            "price": self.parse_price(price_node.get_text(" ", strip=True))
            if price_node else None,
            "currency": "GTQ",
            "available": "agotado" not in soup.get_text(" ", strip=True).lower(),
            "url": url,
            "image": image_node.get("src") if image_node else None,
        }
