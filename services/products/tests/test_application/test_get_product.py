import pytest
import json
from unittest.mock import AsyncMock

from libs.common.errors import NotFoundError
from services.products.application.get_product import GetProduct
from services.products.domain.entities import Product


@pytest.mark.asyncio
async def test_get_product_from_cache(
    mock_repository: AsyncMock, mock_cache: AsyncMock, sample_product: Product
) -> None:
    mock_cache.get.return_value = json.dumps(sample_product.to_dict())
    use_case = GetProduct(mock_repository, mock_cache)

    result = await use_case.execute("test-123")

    assert result.id == sample_product.id
    mock_cache.get.assert_called_once_with("product:test-123")
    mock_repository.get_by_id.assert_not_called()


@pytest.mark.asyncio
async def test_get_product_from_repository(
    mock_repository: AsyncMock, mock_cache: AsyncMock, sample_product: Product
) -> None:
    mock_cache.get.return_value = None
    mock_repository.get_by_id.return_value = sample_product
    use_case = GetProduct(mock_repository, mock_cache)

    result = await use_case.execute("test-123")

    assert result.id == sample_product.id
    mock_repository.get_by_id.assert_called_once_with("test-123")
    mock_cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_get_product_not_found(
    mock_repository: AsyncMock, mock_cache: AsyncMock
) -> None:
    mock_cache.get.return_value = None
    mock_repository.get_by_id.return_value = None
    use_case = GetProduct(mock_repository, mock_cache)

    with pytest.raises(NotFoundError):
        await use_case.execute("non-existent")

