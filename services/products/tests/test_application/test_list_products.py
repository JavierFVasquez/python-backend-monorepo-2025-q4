import pytest
from unittest.mock import AsyncMock

from services.products.application.list_products import ListProducts
from services.products.domain.entities import Product


@pytest.mark.asyncio
async def test_list_products(mock_repository: AsyncMock, sample_product: Product) -> None:
    mock_repository.list_products.return_value = ([sample_product], 1)
    use_case = ListProducts(mock_repository)

    products, total = await use_case.execute(page=1, size=10)

    assert len(products) == 1
    assert total == 1
    assert products[0].id == sample_product.id
    mock_repository.list_products.assert_called_once_with(1, 10)

