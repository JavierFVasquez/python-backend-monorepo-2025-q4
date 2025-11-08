import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from datetime import datetime

from services.products.domain.entities import Product


@pytest.fixture
def sample_product() -> Product:
    return Product(
        id="test-123",
        name="Test Product",
        description="Test Description",
        price=Decimal("99.99"),
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_cache() -> AsyncMock:
    return AsyncMock()

