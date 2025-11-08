"""
Seed data for Products service.

Usage:
    poetry run python -m seeds.seed_products
"""
import asyncio
import uuid
from decimal import Decimal
from datetime import datetime
from pathlib import Path

# Load environment variables from .env BEFORE importing dependencies
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path, override=True)

from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import async_session_maker
from infrastructure.database.models import ProductModel


SEED_PRODUCTS = [
    {
        "id": str(uuid.uuid4()),
        "name": "Laptop Pro 15\"",
        "description": "High-performance laptop with 16GB RAM and 512GB SSD",
        "price": Decimal("1299.99"),
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless mouse with precision tracking",
        "price": Decimal("29.99"),
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Mechanical Keyboard",
        "description": "RGB mechanical keyboard with Cherry MX switches",
        "price": Decimal("149.99"),
    },
    {
        "id": str(uuid.uuid4()),
        "name": "27\" 4K Monitor",
        "description": "Ultra HD monitor with HDR support",
        "price": Decimal("599.99"),
    },
    {
        "id": str(uuid.uuid4()),
        "name": "USB-C Hub",
        "description": "Multi-port USB-C hub with HDMI and ethernet",
        "price": Decimal("79.99"),
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Noise Cancelling Headphones",
        "description": "Premium wireless headphones with active noise cancellation",
        "price": Decimal("299.99"),
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Webcam HD 1080p",
        "description": "Full HD webcam with autofocus and dual microphones",
        "price": Decimal("89.99"),
    },
    {
        "id": str(uuid.uuid4()),
        "name": "External SSD 1TB",
        "description": "Portable solid state drive with USB 3.2",
        "price": Decimal("159.99"),
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Desk Lamp LED",
        "description": "Adjustable LED desk lamp with touch control",
        "price": Decimal("49.99"),
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Phone Stand",
        "description": "Aluminum phone stand with cable management",
        "price": Decimal("24.99"),
    },
]


async def seed_database() -> None:
    """Insert seed data into database."""
    async with async_session_maker() as session:
        # Check if data already exists
        from sqlalchemy import select
        result = await session.execute(select(ProductModel))
        existing_products = result.scalars().all()
        
        if len(existing_products) > 0:
            print(f"⚠️  Database already has {len(existing_products)} products. Skipping seed.")
            return
        
        # Insert seed data
        now = datetime.utcnow()
        products = [
            ProductModel(
                **product,
                created_at=now,
                updated_at=now,
            )
            for product in SEED_PRODUCTS
        ]
        
        session.add_all(products)
        await session.commit()
        
        print(f"✅ Seeded {len(products)} products successfully!")
        print("\nSample products:")
        for p in products[:3]:
            print(f"  • {p.name} - ${p.price}")


async def clear_database() -> None:
    """Clear all products from database."""
    async with async_session_maker() as session:
        from sqlalchemy import delete
        result = await session.execute(delete(ProductModel))
        await session.commit()
        print(f"✅ Cleared {result.rowcount} products from database")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        print("🗑️  Clearing database...")
        asyncio.run(clear_database())
    else:
        print("🌱 Seeding database...")
        asyncio.run(seed_database())

