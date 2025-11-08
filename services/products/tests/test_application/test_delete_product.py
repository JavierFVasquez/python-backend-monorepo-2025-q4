import pytest
from unittest.mock import AsyncMock

from libs.common.errors import NotFoundError
from services.products.application.delete_product import DeleteProduct


@pytest.mark.asyncio
async def test_delete_product(mock_repository: AsyncMock, mock_cache: AsyncMock) -> None:
    mock_repository.delete.return_value = True
    use_case = DeleteProduct(mock_repository, mock_cache)

    await use_case.execute("test-123")

    mock_repository.delete.assert_called_once_with("test-123")
    mock_cache.delete.assert_called_once_with("product:test-123")


@pytest.mark.asyncio
async def test_delete_product_not_found(
    mock_repository: AsyncMock, mock_cache: AsyncMock
) -> None:
    mock_repository.delete.return_value = False
    use_case = DeleteProduct(mock_repository, mock_cache)

    with pytest.raises(NotFoundError):
        await use_case.execute("non-existent")

