from decimal import Decimal
from datetime import datetime

from services.products.domain.entities import Product


def test_product_creation() -> None:
    product = Product(
        id="123",
        name="Test Product",
        description="Test Description",
        price=Decimal("99.99"),
        images=["https://i.imgur.com/test.png"],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )

    assert product.id == "123"
    assert product.name == "Test Product"
    assert product.description == "Test Description"
    assert product.price == Decimal("99.99")
    assert product.images == ["https://i.imgur.com/test.png"]


def test_product_to_dict() -> None:
    product = Product(
        id="123",
        name="Test Product",
        description="Test Description",
        price=Decimal("99.99"),
        images=["https://i.imgur.com/test.png"],
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 12, 0, 0),
    )

    product_dict = product.to_dict()

    assert product_dict["id"] == "123"
    assert product_dict["name"] == "Test Product"
    assert product_dict["price"] == "99.99"
    assert product_dict["images"] == ["https://i.imgur.com/test.png"]
    assert "created_at" in product_dict
    assert "updated_at" in product_dict

