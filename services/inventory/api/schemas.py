from pydantic import BaseModel, ConfigDict, Field


class InventoryUpdate(BaseModel):
    """Schema for updating inventory quantity with delta changes."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quantity_delta": 50,
            }
        }
    )

    quantity_delta: int = Field(
        ...,
        description="Quantity change (positive to add, negative to subtract)",
        examples=[50, -10],
    )


class InventoryCreate(BaseModel):
    """Schema for creating a new inventory record for a product."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "550e8400-e29b-41d4-a716-446655440000",
                "quantity": 100,
            }
        }
    )

    product_id: str = Field(
        ...,
        min_length=1,
        description="UUID of the product to track inventory for",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    quantity: int = Field(
        default=0,
        ge=0,
        description="Initial quantity in stock (must be >= 0)",
        examples=[100, 0],
    )

