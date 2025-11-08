import logging
from typing import Any

from libs.common.errors import NotFoundError
from services.inventory.domain.entities import Inventory
from services.inventory.domain.ports import InventoryRepository, ProductServicePort

logger = logging.getLogger(__name__)


class GetInventory:
    def __init__(
        self, repository: InventoryRepository, product_service: ProductServicePort
    ) -> None:
        self.repository = repository
        self.product_service = product_service

    async def execute(self, product_id: str, request_id: str) -> tuple[dict[str, Any], Inventory]:
        """
        Obtiene el inventario de un producto junto con sus datos.

        Returns:
            tuple: (product_data, inventory) donde product_data contiene la info del producto
        """
        product = await self.product_service.get_product(product_id, request_id)
        if not product:
            raise NotFoundError(f"Product with id {product_id} not found")

        inventory = await self.repository.get_by_product_id(product_id)
        if not inventory:
            raise NotFoundError(f"Inventory for product {product_id} not found")

        logger.info(
            f"Retrieved inventory for product {product_id}",
            extra={"request_id": request_id, "quantity": inventory.quantity},
        )

        return product, inventory

