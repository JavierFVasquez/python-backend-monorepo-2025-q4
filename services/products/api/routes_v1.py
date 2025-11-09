"""API v1 routes for Products service."""
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from libs.auth.api_key import verify_api_key
from services.products.api.dependencies import get_cache, get_db_session, get_product_repository
from services.products.api.schemas import ProductCreate, ProductUpdate
from services.products.api.serializers import serialize_product, serialize_products
from services.products.api.versioning import APIVersion
from services.products.application.create_product import CreateProduct
from services.products.application.delete_product import DeleteProduct
from services.products.application.get_product import GetProduct
from services.products.application.list_products import ListProducts
from services.products.application.update_product import UpdateProduct
from services.products.domain.ports import CachePort

# API v1 Router
router = APIRouter(
    prefix=f"{APIVersion.V1.prefix}/products",
    tags=["products", "v1"],
    responses={
        401: {"description": "Invalid or missing API key"},
        500: {"description": "Internal server error"},
    },
)


@router.post(
    "/",
    status_code=201,
    dependencies=[Depends(verify_api_key)],
    summary="[v1] Create a new product",
    description="Creates a new product with the provided name, description, and price.",
)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    repository = await get_product_repository(db)
    use_case = CreateProduct(repository)
    created = await use_case.execute(product.model_dump())
    return serialize_product(created)


@router.get(
    "/{product_id}",
    dependencies=[Depends(verify_api_key)],
    summary="[v1] Get a product by ID",
)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db_session),
    cache: CachePort = Depends(get_cache),
) -> dict[str, Any]:
    repository = await get_product_repository(db)
    use_case = GetProduct(repository, cache)
    product = await use_case.execute(product_id)
    return serialize_product(product)


@router.get(
    "/",
    dependencies=[Depends(verify_api_key)],
    summary="[v1] List all products",
)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    repository = await get_product_repository(db)
    use_case = ListProducts(repository)
    products, total = await use_case.execute(page, size)
    return serialize_products(products, page, size, total)


@router.patch(
    "/{product_id}",
    dependencies=[Depends(verify_api_key)],
    summary="[v1] Update a product",
)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db_session),
    cache: CachePort = Depends(get_cache),
) -> dict[str, Any]:
    repository = await get_product_repository(db)
    use_case = UpdateProduct(repository, cache)
    updated = await use_case.execute(product_id, product_update.model_dump(exclude_unset=True))
    return serialize_product(updated)


@router.delete(
    "/{product_id}",
    status_code=204,
    dependencies=[Depends(verify_api_key)],
    summary="[v1] Delete a product",
)
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db_session),
    cache: CachePort = Depends(get_cache),
) -> None:
    repository = await get_product_repository(db)
    use_case = DeleteProduct(repository, cache)
    await use_case.execute(product_id)

