from libs.common.errors import NotFoundError
from services.products.domain.ports import CachePort, ProductRepository


class DeleteProduct:
    def __init__(self, repository: ProductRepository, cache: CachePort) -> None:
        self.repository = repository
        self.cache = cache

    async def execute(self, product_id: str) -> None:
        deleted = await self.repository.delete(product_id)
        if not deleted:
            raise NotFoundError(f"Product with id {product_id} not found")

        cache_key = f"product:{product_id}"
        await self.cache.delete(cache_key)

