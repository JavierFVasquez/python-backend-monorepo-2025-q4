import logging

from libs.common.errors import NotFoundError, ValidationError
from services.inventory.domain.entities import Inventory
from services.inventory.domain.ports import InventoryRepository

logger = logging.getLogger(__name__)


class UpdateInventory:
    def __init__(self, repository: InventoryRepository) -> None:
        self.repository = repository

    async def execute(
        self, product_id: str, quantity_delta: int, request_id: str
    ) -> Inventory:
        inventory = await self.repository.get_by_product_id(product_id)
        if not inventory:
            raise NotFoundError(f"Inventory for product {product_id} not found")

        new_quantity = inventory.quantity + quantity_delta
        if new_quantity < 0:
            raise ValidationError("Insufficient inventory quantity")

        updated_inventory = await self.repository.update_quantity(product_id, quantity_delta)
        if not updated_inventory:
            raise NotFoundError(f"Failed to update inventory for product {product_id}")

        logger.info(
            f"Updated inventory for product {product_id}: "
            f"{inventory.quantity} -> {updated_inventory.quantity}",
            extra={
                "request_id": request_id,
                "product_id": product_id,
                "old_quantity": inventory.quantity,
                "new_quantity": updated_inventory.quantity,
                "delta": quantity_delta,
            },
        )

        return updated_inventory

