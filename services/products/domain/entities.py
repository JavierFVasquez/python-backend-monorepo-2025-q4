from datetime import datetime
from decimal import Decimal


class Product:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        price: Decimal | str,
        created_at: datetime | str,
        updated_at: datetime | str,
    ) -> None:
        self.id = id
        self.name = name
        self.description = description
        # Handle both Decimal and str for price
        self.price = Decimal(price) if isinstance(price, str) else price
        # Handle both datetime and str for timestamps
        self.created_at = (
            datetime.fromisoformat(created_at)
            if isinstance(created_at, str)
            else created_at
        )
        self.updated_at = (
            datetime.fromisoformat(updated_at)
            if isinstance(updated_at, str)
            else updated_at
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": str(self.price),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Create a Product from a dictionary (useful for cache deserialization)."""
        return cls(**data)

