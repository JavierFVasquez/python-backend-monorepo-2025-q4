from typing import Any

from libs.common.errors import NotFoundError
from services.products.domain.entities import Product
from services.products.domain.ports import CachePort, ProductRepository


class UpdateProduct:
    def __init__(self, repository: ProductRepository, cache: CachePort) -> None:
        self.repository = repository
        self.cache = cache

    async def execute(self, product_id: str, product_data: dict[str, Any]) -> Product:
        product = await self.repository.update(product_id, product_data)
        if not product:
            raise NotFoundError(f"Product with id {product_id} not found")

        cache_key = f"product:{product_id}"
        await self.cache.delete(cache_key)

        return product

