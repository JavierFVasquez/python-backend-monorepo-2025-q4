import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.products.domain.entities import Product
from services.products.domain.ports import ProductRepository
from services.products.infrastructure.database.models import ProductModel


class SupabaseProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, product_data: dict[str, Any]) -> Product:
        product_id = str(uuid.uuid4())
        now = datetime.utcnow()

        product_model = ProductModel(
            id=product_id,
            name=product_data["name"],
            description=product_data["description"],
            price=Decimal(str(product_data["price"])),
            images=product_data.get("images", []),
            created_at=now,
            updated_at=now,
        )

        self.session.add(product_model)
        await self.session.commit()
        await self.session.refresh(product_model)

        return self._to_entity(product_model)

    async def get_by_id(self, product_id: str) -> Product | None:
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.id == product_id)
        )
        product_model = result.scalar_one_or_none()

        if not product_model:
            return None

        return self._to_entity(product_model)

    async def update(self, product_id: str, product_data: dict[str, Any]) -> Product | None:
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.id == product_id)
        )
        product_model = result.scalar_one_or_none()

        if not product_model:
            return None

        if "name" in product_data:
            product_model.name = product_data["name"]
        if "description" in product_data:
            product_model.description = product_data["description"]
        if "price" in product_data:
            product_model.price = Decimal(str(product_data["price"]))
        if "images" in product_data:
            product_model.images = product_data["images"]

        product_model.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(product_model)

        return self._to_entity(product_model)

    async def delete(self, product_id: str) -> bool:
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.id == product_id)
        )
        product_model = result.scalar_one_or_none()

        if not product_model:
            return False

        await self.session.delete(product_model)
        await self.session.commit()
        return True

    async def list_products(self, page: int, size: int) -> tuple[list[Product], int]:
        offset = (page - 1) * size

        count_result = await self.session.execute(select(ProductModel))
        total = len(count_result.scalars().all())

        result = await self.session.execute(
            select(ProductModel).offset(offset).limit(size)
        )
        product_models = result.scalars().all()

        products = [self._to_entity(model) for model in product_models]
        return products, total

    def _to_entity(self, model: ProductModel) -> Product:
        return Product(
            id=model.id,
            name=model.name,
            description=model.description,
            price=model.price,
            images=model.images if model.images else [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

