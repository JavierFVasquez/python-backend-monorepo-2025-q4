from typing import Any

from libs.common.jsonapi import serialize_collection, serialize_resource
from services.products.domain.entities import Product


def serialize_product(product: Product) -> dict[str, Any]:
    attributes = product.to_dict()
    product_id = attributes.pop("id")
    return serialize_resource("products", product_id, attributes)


def serialize_products(
    products: list[Product], page: int, size: int, total: int
) -> dict[str, Any]:
    items = [product.to_dict() for product in products]
    return serialize_collection("products", items, page, size, total)

