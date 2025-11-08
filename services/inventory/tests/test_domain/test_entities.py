from datetime import datetime

from services.inventory.domain.entities import Inventory


def test_inventory_creation() -> None:
    inventory = Inventory(
        product_id="123",
        quantity=100,
        last_updated=datetime(2024, 1, 1),
    )

    assert inventory.product_id == "123"
    assert inventory.quantity == 100
    assert inventory.last_updated == datetime(2024, 1, 1)


def test_inventory_to_dict() -> None:
    inventory = Inventory(
        product_id="123",
        quantity=100,
        last_updated=datetime(2024, 1, 1, 12, 0, 0),
    )

    inventory_dict = inventory.to_dict()

    assert inventory_dict["product_id"] == "123"
    assert inventory_dict["quantity"] == 100
    assert "last_updated" in inventory_dict

