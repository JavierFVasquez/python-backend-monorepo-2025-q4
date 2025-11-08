from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from libs.auth.api_key import verify_api_key
from services.products.api.dependencies import get_cache, get_db_session, get_product_repository
from services.products.api.schemas import ProductCreate, ProductUpdate
from services.products.api.serializers import serialize_product, serialize_products
from services.products.application.create_product import CreateProduct
from services.products.application.delete_product import DeleteProduct
from services.products.application.get_product import GetProduct
from services.products.application.list_products import ListProducts
from services.products.application.update_product import UpdateProduct
from services.products.domain.ports import CachePort

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={
        401: {"description": "Invalid or missing API key"},
        500: {"description": "Internal server error"},
    },
)


@router.post(
    "/",
    status_code=201,
    dependencies=[Depends(verify_api_key)],
    summary="Create a new product",
    description="Creates a new product with the provided name, description, and price.",
    response_description="The newly created product",
    responses={
        201: {
            "description": "Product created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "type": "products",
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "attributes": {
                                "name": "Laptop Dell XPS 15",
                                "description": "High-performance laptop with Intel Core i7 processor",
                                "price": "1299.99",
                                "created_at": "2025-11-08T10:30:00",
                                "updated_at": "2025-11-08T10:30:00",
                            }
                        }
                    }
                }
            },
        },
        400: {
            "description": "Invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "errors": [{
                            "status": "400",
                            "title": "Bad Request",
                            "detail": "Validation error in request body"
                        }]
                    }
                }
            }
        },
    },
)
async def create_product(
    product: ProductCreate,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    repository = await get_product_repository(session)
    use_case = CreateProduct(repository)
    created_product = await use_case.execute(product.model_dump())
    return serialize_product(created_product)


@router.get(
    "/{product_id}",
    dependencies=[Depends(verify_api_key)],
    summary="Get a product by ID",
    description="Retrieves a single product by its unique identifier. Uses cache for improved performance.",
    response_description="The requested product",
    responses={
        200: {
            "description": "Product found",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "type": "products",
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "attributes": {
                                "name": "Laptop Dell XPS 15",
                                "description": "High-performance laptop",
                                "price": "1299.99",
                                "created_at": "2025-11-08T10:30:00",
                                "updated_at": "2025-11-08T10:30:00",
                            }
                        }
                    }
                }
            },
        },
        404: {
            "description": "Product not found",
            "content": {
                "application/json": {
                    "example": {
                        "errors": [{
                            "status": "404",
                            "title": "Not Found",
                            "detail": "Product not found"
                        }]
                    }
                }
            }
        },
    },
)
async def get_product(
    product_id: str,
    session: AsyncSession = Depends(get_db_session),
    cache: CachePort = Depends(get_cache),
) -> dict[str, Any]:
    repository = await get_product_repository(session)
    use_case = GetProduct(repository, cache)
    product = await use_case.execute(product_id)
    return serialize_product(product)


@router.patch(
    "/{product_id}",
    dependencies=[Depends(verify_api_key)],
    summary="Update a product",
    description="Updates one or more fields of an existing product. All fields are optional.",
    response_description="The updated product",
    responses={
        200: {
            "description": "Product updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "type": "products",
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "attributes": {
                                "name": "Laptop Dell XPS 15 (Updated)",
                                "description": "High-performance laptop",
                                "price": "1199.99",
                                "created_at": "2025-11-08T10:30:00",
                                "updated_at": "2025-11-08T11:45:00",
                            }
                        }
                    }
                }
            },
        },
        404: {
            "description": "Product not found",
            "content": {
                "application/json": {
                    "example": {
                        "errors": [{
                            "status": "404",
                            "title": "Not Found",
                            "detail": "Product not found"
                        }]
                    }
                }
            }
        },
        400: {
            "description": "Invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "errors": [{
                            "status": "400",
                            "title": "Bad Request",
                            "detail": "Invalid field values"
                        }]
                    }
                }
            }
        },
    },
)
async def update_product(
    product_id: str,
    product: ProductUpdate,
    session: AsyncSession = Depends(get_db_session),
    cache: CachePort = Depends(get_cache),
) -> dict[str, Any]:
    repository = await get_product_repository(session)
    use_case = UpdateProduct(repository, cache)
    updated_product = await use_case.execute(
        product_id, product.model_dump(exclude_unset=True)
    )
    return serialize_product(updated_product)


@router.delete(
    "/{product_id}",
    status_code=204,
    dependencies=[Depends(verify_api_key)],
    summary="Delete a product",
    description="Permanently deletes a product by its ID. This action cannot be undone.",
    response_description="Product deleted successfully (no content)",
    responses={
        204: {"description": "Product deleted successfully (no content returned)"},
        404: {
            "description": "Product not found",
            "content": {
                "application/json": {
                    "example": {
                        "errors": [{
                            "status": "404",
                            "title": "Not Found",
                            "detail": "Product not found"
                        }]
                    }
                }
            }
        },
    },
)
async def delete_product(
    product_id: str,
    session: AsyncSession = Depends(get_db_session),
    cache: CachePort = Depends(get_cache),
) -> None:
    repository = await get_product_repository(session)
    use_case = DeleteProduct(repository, cache)
    await use_case.execute(product_id)


@router.get(
    "/",
    dependencies=[Depends(verify_api_key)],
    summary="List all products",
    description="Retrieves a paginated list of all products.",
    response_description="Paginated list of products",
    responses={
        200: {
            "description": "Products retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "type": "products",
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "attributes": {
                                    "name": "Laptop Dell XPS 15",
                                    "description": "High-performance laptop",
                                    "price": "1299.99",
                                    "created_at": "2025-11-08T10:30:00",
                                    "updated_at": "2025-11-08T10:30:00",
                                }
                            },
                            {
                                "type": "products",
                                "id": "660f9511-f30c-52e5-b827-557766551111",
                                "attributes": {
                                    "name": "Mouse Logitech MX Master 3",
                                    "description": "Ergonomic wireless mouse",
                                    "price": "99.99",
                                    "created_at": "2025-11-08T09:15:00",
                                    "updated_at": "2025-11-08T09:15:00",
                                }
                            }
                        ],
                        "meta": {
                            "page": {
                                "number": 1,
                                "size": 10,
                                "total": 2
                            }
                        }
                    }
                }
            },
        }
    },
)
async def list_products(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page (1-100)"),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    repository = await get_product_repository(session)
    use_case = ListProducts(repository)
    products, total = await use_case.execute(page, size)
    return serialize_products(products, page, size, total)

