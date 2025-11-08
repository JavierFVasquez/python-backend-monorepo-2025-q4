from abc import ABC, abstractmethod
from typing import Any

from services.inventory.domain.entities import Inventory


class InventoryRepository(ABC):
    @abstractmethod
    async def get_by_product_id(self, product_id: str) -> Inventory | None:
        pass

    @abstractmethod
    async def create(self, inventory_data: dict[str, Any]) -> Inventory:
        pass

    @abstractmethod
    async def update_quantity(self, product_id: str, quantity_delta: int) -> Inventory | None:
        pass


class ProductServicePort(ABC):
    @abstractmethod
    async def get_product(self, product_id: str, request_id: str) -> dict[str, Any] | None:
        pass

