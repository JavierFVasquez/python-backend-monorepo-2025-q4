from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    """Schema for creating a new product."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Laptop Dell XPS 15",
                "description": "High-performance laptop with Intel Core i7 processor, 16GB RAM, and 512GB SSD",
                "price": 1299.99,
                "images": [
                    "https://placehold.co/600x400/png",
                    "https://placehold.co/600x400/png"
                ]
            }
        }
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Product name (1-255 characters)",
        examples=["Laptop Dell XPS 15"],
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Detailed product description",
        examples=["High-performance laptop with Intel Core i7 processor"],
    )
    price: Decimal = Field(
        ...,
        gt=0,
        description="Product price in USD (must be greater than 0)",
        examples=[1299.99],
    )
    images: list[str] = Field(
        default_factory=list,
        description="Array of product image URLs (PNG or WEBP with transparent background)",
        examples=[["https://placehold.co/600x400/png"]],
    )


class ProductUpdate(BaseModel):
    """Schema for updating an existing product. All fields are optional."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Laptop Dell XPS 15 (Updated)",
                "price": 1199.99,
                "images": ["https://placehold.co/600x400/png"]
            }
        }
    )

    name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated product name (1-255 characters)",
        examples=["Laptop Dell XPS 15 (Updated)"],
    )
    description: str | None = Field(
        None,
        min_length=1,
        description="Updated product description",
        examples=["High-performance laptop with upgraded specs"],
    )
    price: Decimal | None = Field(
        None,
        gt=0,
        description="Updated product price in USD (must be greater than 0)",
        examples=[1199.99],
    )
    images: list[str] | None = Field(
        None,
        description="Updated array of product image URLs (PNG or WEBP with transparent background)",
        examples=[["https://placehold.co/600x400/png"]],
    )

