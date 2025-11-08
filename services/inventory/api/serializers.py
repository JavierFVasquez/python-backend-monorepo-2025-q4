from typing import Any

from libs.common.jsonapi import serialize_resource
from services.inventory.domain.entities import Inventory


def serialize_inventory(inventory: Inventory, product: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Serializa un inventario, opcionalmente incluyendo datos del producto.
    
    Args:
        inventory: Entidad de inventario
        product: Datos del producto (opcional) obtenidos del servicio de productos
    """
    attributes = inventory.to_dict()
    product_id = attributes.pop("product_id")

    # Si hay datos del producto, incluirlos en los atributos
    if product:
        attributes["product"] = {
            "id": product.get("id"),
            "name": product.get("name"),
            "description": product.get("description"),
            "price": product.get("price"),
        }

    return serialize_resource("inventory", product_id, attributes)

