"""API v1 routes for Inventory service."""
from typing import Any

from fastapi import APIRouter, Depends, Request

from libs.auth.api_key import verify_api_key
from services.inventory.api.dependencies import get_inventory_repository, get_product_service
from services.inventory.api.schemas import InventoryCreate, InventoryUpdate
from services.inventory.api.serializers import serialize_inventory
from services.inventory.api.versioning import APIVersion
from services.inventory.application.get_inventory import GetInventory
from services.inventory.application.update_inventory import UpdateInventory
from services.inventory.domain.ports import InventoryRepository, ProductServicePort

# API v1 Router
router = APIRouter(
    prefix=f"{APIVersion.V1.prefix}/inventory",
    tags=["inventory", "v1"],
    responses={
        401: {"description": "Invalid or missing API key"},
        500: {"description": "Internal server error"},
    },
)


@router.post(
    "/",
    status_code=201,
    dependencies=[Depends(verify_api_key)],
    summary="[v1] Create inventory record",
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
    summary="[v1] Get inventory for a product",
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
    summary="[v1] Update inventory quantity",
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

