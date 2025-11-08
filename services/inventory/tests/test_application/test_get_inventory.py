import pytest
from unittest.mock import AsyncMock

from libs.common.errors import NotFoundError
from services.inventory.application.get_inventory import GetInventory
from services.inventory.domain.entities import Inventory


@pytest.mark.asyncio
async def test_get_inventory_success(
    mock_repository: AsyncMock,
    mock_product_service: AsyncMock,
    sample_inventory: Inventory,
) -> None:
    mock_product_service.get_product.return_value = {"id": "test-123"}
    mock_repository.get_by_product_id.return_value = sample_inventory
    use_case = GetInventory(mock_repository, mock_product_service)

    result = await use_case.execute("test-123", "request-123")

    assert result.product_id == sample_inventory.product_id
    assert result.quantity == sample_inventory.quantity
    mock_product_service.get_product.assert_called_once_with("test-123", "request-123")
    mock_repository.get_by_product_id.assert_called_once_with("test-123")


@pytest.mark.asyncio
async def test_get_inventory_product_not_found(
    mock_repository: AsyncMock, mock_product_service: AsyncMock
) -> None:
    mock_product_service.get_product.return_value = None
    use_case = GetInventory(mock_repository, mock_product_service)

    with pytest.raises(NotFoundError):
        await use_case.execute("non-existent", "request-123")


@pytest.mark.asyncio
async def test_get_inventory_not_found(
    mock_repository: AsyncMock, mock_product_service: AsyncMock
) -> None:
    mock_product_service.get_product.return_value = {"id": "test-123"}
    mock_repository.get_by_product_id.return_value = None
    use_case = GetInventory(mock_repository, mock_product_service)

    with pytest.raises(NotFoundError):
        await use_case.execute("test-123", "request-123")

