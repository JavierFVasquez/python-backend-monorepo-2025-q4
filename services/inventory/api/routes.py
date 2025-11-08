from typing import Any

from fastapi import APIRouter, Depends, Request

from libs.auth.api_key import verify_api_key
from services.inventory.api.dependencies import get_inventory_repository, get_product_service
from services.inventory.api.schemas import InventoryCreate, InventoryUpdate
from services.inventory.api.serializers import serialize_inventory
from services.inventory.application.get_inventory import GetInventory
from services.inventory.application.update_inventory import UpdateInventory
from services.inventory.domain.ports import InventoryRepository, ProductServicePort

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    responses={
        401: {"description": "Invalid or missing API key"},
        500: {"description": "Internal server error"},
    },
)


@router.post(
    "/",
    status_code=201,
    dependencies=[Depends(verify_api_key)],
    summary="Create inventory record",
    description="Creates a new inventory record for a product with an initial quantity.",
    response_description="The newly created inventory record",
    responses={
        201: {
            "description": "Inventory record created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "type": "inventory",
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "attributes": {
                                "quantity": 100,
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
async def create_inventory(
    inventory: InventoryCreate,
    repository: InventoryRepository = Depends(get_inventory_repository),
) -> dict[str, Any]:
    created_inventory = await repository.create(inventory.model_dump())
    return serialize_inventory(created_inventory)


@router.get(
    "/{product_id}",
    dependencies=[Depends(verify_api_key)],
    summary="Get inventory for a product",
    description="Retrieves the inventory record for a specific product. Includes product details via gRPC call.",
    response_description="The inventory record with product information",
    responses={
        200: {
            "description": "Inventory record found",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "type": "inventory",
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "attributes": {
                                "quantity": 100,
                                "product": {
                                    "id": "550e8400-e29b-41d4-a716-446655440000",
                                    "name": "Laptop Dell XPS 15",
                                    "description": "High-performance laptop",
                                    "price": "1299.99",
                                    "images": [
                                        "https://i.imgur.com/3Qnm0Wj.png",
                                        "https://i.imgur.com/xKZJ6mF.png"
                                    ],
                                },
                                "created_at": "2025-11-08T10:30:00",
                                "updated_at": "2025-11-08T10:30:00",
                            }
                        }
                    }
                }
            },
        },
        404: {
            "description": "Inventory record not found",
            "content": {
                "application/json": {
                    "example": {
                        "errors": [{
                            "status": "404",
                            "title": "Not Found",
                            "detail": "Inventory record not found"
                        }]
                    }
                }
            }
        },
    },
)
async def get_inventory(
    product_id: str,
    request: Request,
    repository: InventoryRepository = Depends(get_inventory_repository),
    product_service: ProductServicePort = Depends(get_product_service),
) -> dict[str, Any]:
    request_id = getattr(request.state, "request_id", "unknown")
    use_case = GetInventory(repository, product_service)
    product, inventory = await use_case.execute(product_id, request_id)
    return serialize_inventory(inventory, product)


@router.patch(
    "/{product_id}",
    dependencies=[Depends(verify_api_key)],
    summary="Update inventory quantity",
    description="Updates the inventory quantity by applying a delta (positive to add stock, negative to remove).",
    response_description="The updated inventory record",
    responses={
        200: {
            "description": "Inventory updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "type": "inventory",
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "attributes": {
                                "quantity": 150,
                                "created_at": "2025-11-08T10:30:00",
                                "updated_at": "2025-11-08T12:15:00",
                            }
                        }
                    }
                }
            },
        },
        404: {
            "description": "Inventory record not found",
            "content": {
                "application/json": {
                    "example": {
                        "errors": [{
                            "status": "404",
                            "title": "Not Found",
                            "detail": "Inventory record not found"
                        }]
                    }
                }
            }
        },
        400: {
            "description": "Invalid input data or insufficient stock",
            "content": {
                "application/json": {
                    "example": {
                        "errors": [{
                            "status": "400",
                            "title": "Bad Request",
                            "detail": "Insufficient stock for this operation"
                        }]
                    }
                }
            }
        },
    },
)
async def update_inventory(
    product_id: str,
    inventory_update: InventoryUpdate,
    request: Request,
    repository: InventoryRepository = Depends(get_inventory_repository),
) -> dict[str, Any]:
    request_id = getattr(request.state, "request_id", "unknown")
    use_case = UpdateInventory(repository)
    updated_inventory = await use_case.execute(
        product_id, inventory_update.quantity_delta, request_id
    )
    return serialize_inventory(updated_inventory)

