import json

from libs.common.errors import NotFoundError
from services.products.domain.entities import Product
from services.products.domain.ports import CachePort, ProductRepository


class GetProduct:
    def __init__(self, repository: ProductRepository, cache: CachePort | None = None) -> None:
        self.repository = repository
        self.cache = cache

    async def execute(self, product_id: str) -> Product:
        # Try cache if available
        if self.cache:
            cache_key = f"product:{product_id}"
            cached = await self.cache.get(cache_key)

            if cached:
                product_dict = json.loads(cached)
                return Product(**product_dict)

        product = await self.repository.get_by_id(product_id)
        if not product:
            raise NotFoundError(f"Product with id {product_id} not found")

        # Set cache if available
        if self.cache:
            cache_key = f"product:{product_id}"
            await self.cache.set(cache_key, json.dumps(product.to_dict()), ttl=300)

        return product

