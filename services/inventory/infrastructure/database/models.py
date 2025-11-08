from datetime import datetime

from beanie import Document
from pydantic import Field


class InventoryModel(Document):
    product_id: str = Field(..., index=True, unique=True)
    quantity: int = Field(default=0, ge=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "inventory"
        indexes = ["product_id"]

