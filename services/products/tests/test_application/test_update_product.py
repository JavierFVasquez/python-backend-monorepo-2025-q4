import pytest
from decimal import Decimal
from unittest.mock import AsyncMock

from libs.common.errors import NotFoundError
from services.products.application.update_product import UpdateProduct
from services.products.domain.entities import Product


@pytest.mark.asyncio
async def test_update_product(
    mock_repository: AsyncMock, mock_cache: AsyncMock, sample_product: Product
) -> None:
    mock_repository.update.return_value = sample_product
    use_case = UpdateProduct(mock_repository, mock_cache)

    update_data = {"price": Decimal("79.99")}
    result = await use_case.execute("test-123", update_data)

    assert result.id == sample_product.id
    mock_repository.update.assert_called_once_with("test-123", update_data)
    mock_cache.delete.assert_called_once_with("product:test-123")


@pytest.mark.asyncio
async def test_update_product_not_found(
    mock_repository: AsyncMock, mock_cache: AsyncMock
) -> None:
    mock_repository.update.return_value = None
    use_case = UpdateProduct(mock_repository, mock_cache)

    with pytest.raises(NotFoundError):
        await use_case.execute("non-existent", {"price": Decimal("79.99")})

