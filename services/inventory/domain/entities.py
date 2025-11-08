from datetime import datetime


class Inventory:
    def __init__(
        self,
        product_id: str,
        quantity: int,
        last_updated: datetime,
    ) -> None:
        self.product_id = product_id
        self.quantity = quantity
        self.last_updated = last_updated

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
            "last_updated": self.last_updated.isoformat(),
        }

