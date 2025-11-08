from abc import ABC, abstractmethod
from typing import Any

from services.products.domain.entities import Product


class ProductRepository(ABC):
    @abstractmethod
    async def create(self, product_data: dict[str, Any]) -> Product:
        pass

    @abstractmethod
    async def get_by_id(self, product_id: str) -> Product | None:
        pass

    @abstractmethod
    async def update(self, product_id: str, product_data: dict[str, Any]) -> Product | None:
        pass

    @abstractmethod
    async def delete(self, product_id: str) -> bool:
        pass

    @abstractmethod
    async def list_products(
        self, page: int, size: int
    ) -> tuple[list[Product], int]:
        pass


class CachePort(ABC):
    @abstractmethod
    async def get(self, key: str) -> str | None:
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: int) -> None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

