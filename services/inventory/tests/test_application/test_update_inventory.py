import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from libs.common.errors import NotFoundError, ValidationError
from services.inventory.application.update_inventory import UpdateInventory
from services.inventory.domain.entities import Inventory


@pytest.mark.asyncio
async def test_update_inventory_success(
    mock_repository: AsyncMock, sample_inventory: Inventory
) -> None:
    updated_inventory = Inventory(
        product_id="test-123", quantity=90, last_updated=datetime.utcnow()
    )
    mock_repository.get_by_product_id.return_value = sample_inventory
    mock_repository.update_quantity.return_value = updated_inventory
    use_case = UpdateInventory(mock_repository)

    result = await use_case.execute("test-123", -10, "request-123")

    assert result.quantity == 90
    mock_repository.update_quantity.assert_called_once_with("test-123", -10)


@pytest.mark.asyncio
async def test_update_inventory_insufficient_quantity(
    mock_repository: AsyncMock, sample_inventory: Inventory
) -> None:
    mock_repository.get_by_product_id.return_value = sample_inventory
    use_case = UpdateInventory(mock_repository)

    with pytest.raises(ValidationError):
        await use_case.execute("test-123", -200, "request-123")


@pytest.mark.asyncio
async def test_update_inventory_not_found(mock_repository: AsyncMock) -> None:
    mock_repository.get_by_product_id.return_value = None
    use_case = UpdateInventory(mock_repository)

    with pytest.raises(NotFoundError):
        await use_case.execute("non-existent", -10, "request-123")

