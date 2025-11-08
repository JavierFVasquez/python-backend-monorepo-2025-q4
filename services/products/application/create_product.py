from typing import Any

from services.products.domain.entities import Product
from services.products.domain.ports import ProductRepository


class CreateProduct:
    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository

    async def execute(self, product_data: dict[str, Any]) -> Product:
        return await self.repository.create(product_data)

