from services.products.domain.entities import Product
from services.products.domain.ports import ProductRepository


class ListProducts:
    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository

    async def execute(self, page: int, size: int) -> tuple[list[Product], int]:
        return await self.repository.list_products(page, size)

