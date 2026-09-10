from abc import ABC, abstractmethod
from typing import Any
import time, requests

class StoreScraper(ABC):
    user_agent = 'ComparaTechGT/0.1 (+contacto@comparatech.gt)'
    def __init__(self, delay: float = 1.5): self.delay = delay
    def fetch(self, url: str) -> str:
        time.sleep(self.delay)
        r = requests.get(url, headers={'User-Agent': self.user_agent}, timeout=20)
        r.raise_for_status(); return r.text
    @abstractmethod
    def search(self, query: str) -> list[dict[str, Any]]: ...
    @abstractmethod
    def get_product(self, url: str) -> dict[str, Any]: ...
    def normalize_product(self, product: dict[str, Any]) -> dict[str, Any]: return product
