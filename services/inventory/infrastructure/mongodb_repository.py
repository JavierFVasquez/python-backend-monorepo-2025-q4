from datetime import datetime
from typing import Any

from services.inventory.domain.entities import Inventory
from services.inventory.domain.ports import InventoryRepository
from services.inventory.infrastructure.database.models import InventoryModel


class MongoDBInventoryRepository(InventoryRepository):
    async def get_by_product_id(self, product_id: str) -> Inventory | None:
        inventory_model = await InventoryModel.find_one(InventoryModel.product_id == product_id)

        if not inventory_model:
            return None

        return self._to_entity(inventory_model)

    async def create(self, inventory_data: dict[str, Any]) -> Inventory:
        inventory_model = InventoryModel(
            product_id=inventory_data["product_id"],
            quantity=inventory_data.get("quantity", 0),
            last_updated=datetime.utcnow(),
        )

        await inventory_model.insert()
        return self._to_entity(inventory_model)

    async def update_quantity(self, product_id: str, quantity_delta: int) -> Inventory | None:
        inventory_model = await InventoryModel.find_one(InventoryModel.product_id == product_id)

        if not inventory_model:
            return None

        inventory_model.quantity += quantity_delta
        inventory_model.last_updated = datetime.utcnow()

        await inventory_model.save()
        return self._to_entity(inventory_model)

    def _to_entity(self, model: InventoryModel) -> Inventory:
        return Inventory(
            product_id=model.product_id,
            quantity=model.quantity,
            last_updated=model.last_updated,
        )

