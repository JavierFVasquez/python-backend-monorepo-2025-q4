import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from services.inventory.domain.entities import Inventory


@pytest.fixture
def sample_inventory() -> Inventory:
    return Inventory(
        product_id="test-123",
        quantity=100,
        last_updated=datetime(2024, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_product_service() -> AsyncMock:
    return AsyncMock()

