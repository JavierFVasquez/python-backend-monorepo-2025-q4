import pytest
from decimal import Decimal
from unittest.mock import AsyncMock

from services.products.application.create_product import CreateProduct
from services.products.domain.entities import Product


@pytest.mark.asyncio
async def test_create_product(mock_repository: AsyncMock, sample_product: Product) -> None:
    mock_repository.create.return_value = sample_product
    use_case = CreateProduct(mock_repository)

    product_data = {
        "name": "Test Product",
        "description": "Test Description",
        "price": Decimal("99.99"),
    }

    result = await use_case.execute(product_data)

    assert result.id == sample_product.id
    assert result.name == sample_product.name
    mock_repository.create.assert_called_once_with(product_data)

