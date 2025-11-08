"""
Seed data for Inventory service (MongoDB).

Usage:
    poetry run python -m seeds.seed_inventory
    poetry run python -m seeds.seed_inventory --clear
"""
import asyncio
import os
from datetime import datetime
from pathlib import Path

# Load environment variables from .env BEFORE importing dependencies
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path, override=True)

from beanie import init_beanie
from infrastructure.database.models import InventoryModel
from motor.motor_asyncio import AsyncIOMotorClient

# Seed data: product_id y cantidad inicial
# Estos IDs deben corresponder con productos existentes en el servicio de productos
SEED_INVENTORY = [
    {"product_id": "product-01", "quantity": 100},  # iPhone 15 Pro
    {"product_id": "product-02", "quantity": 50},   # MacBook Pro 16"
    {"product_id": "product-03", "quantity": 200},  # AirPods Pro
    {"product_id": "product-04", "quantity": 75},   # iPad Air M2
    {"product_id": "product-05", "quantity": 60},   # Samsung Galaxy S24 Ultra
    {"product_id": "product-06", "quantity": 150},  # Sony WH-1000XM5
    {"product_id": "product-07", "quantity": 30},   # PlayStation 5
    {"product_id": "product-08", "quantity": 80},   # Nintendo Switch OLED
    {"product_id": "product-09", "quantity": 120},  # Apple Watch Series 9
    {"product_id": "product-10", "quantity": 40},  # DJI Mini 4 Pro
    {"product_id": "product-11", "quantity": 90},  # GoPro HERO12 Black
    {"product_id": "product-12", "quantity": 250}, # Logitech MX Master 3S
    {"product_id": "product-13", "quantity": 45},  # Dell XPS 15
    {"product_id": "product-14", "quantity": 25},  # Samsung 55" QLED 4K TV
    {"product_id": "product-15", "quantity": 130}, # Bose QuietComfort 45
    {"product_id": "product-16", "quantity": 15},  # Canon EOS R6 Mark II
    {"product_id": "product-17", "quantity": 300}, # Amazon Echo Dot (5th Gen)
    {"product_id": "product-18", "quantity": 70},  # Google Pixel 8 Pro
    {"product_id": "product-19", "quantity": 95},  # Razer BlackWidow V4 Pro
    {"product_id": "product-20", "quantity": 35},  # HP LaserJet Pro M404n
    {"product_id": "product-21", "quantity": 55},  # Microsoft Surface Pro 9
    {"product_id": "product-22", "quantity": 180}, # Fitbit Charge 6
    {"product_id": "product-23", "quantity": 210}, # Kindle Paperwhite
    {"product_id": "product-24", "quantity": 42},  # Asus ROG Strix Gaming Monitor 27"
    {"product_id": "product-25", "quantity": 160}, # SanDisk Extreme Portable SSD 1TB
    {"product_id": "product-26", "quantity": 220}, # Anker PowerCore 26800mAh
    {"product_id": "product-27", "quantity": 110}, # Logitech C920 HD Pro Webcam
    {"product_id": "product-28", "quantity": 38},  # Meta Quest 3
    {"product_id": "product-29", "quantity": 145}, # JBL Flip 6
    {"product_id": "product-30", "quantity": 28},  # Lenovo ThinkPad X1 Carbon Gen 11
    {"product_id": "product-31", "quantity": 85},  # TP-Link WiFi 6 Router AX3000
    {"product_id": "product-32", "quantity": 65},  # Seagate Backup Plus 4TB
]


async def init_db():
    """Initialize MongoDB connection with Beanie."""
    mongodb_url = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    database_name = os.getenv("MONGODB_DATABASE", "inventory_db")

    client = AsyncIOMotorClient(mongodb_url)
    database = client[database_name]

    await init_beanie(database=database, document_models=[InventoryModel])
    return client


async def seed_database() -> None:
    """Insert seed data into MongoDB."""
    client = await init_db()

    try:
        # Check if data already exists
        existing_count = await InventoryModel.count()

        if existing_count > 0:
            print(f"⚠️  Database already has {existing_count} inventory records. Skipping seed.")
            return

        # Insert seed data
        now = datetime.utcnow()
        inventory_records = [
            InventoryModel(
                product_id=item["product_id"],
                quantity=item["quantity"],
                last_updated=now,
            )
            for item in SEED_INVENTORY
        ]

        # Insert all records
        await InventoryModel.insert_many(inventory_records)

        print(f"✅ Seeded {len(inventory_records)} inventory records successfully!")
        print("\nSample inventory:")
        for record in inventory_records[:3]:
            print(f"  • Product {record.product_id}: {record.quantity} units")

    finally:
        client.close()


async def clear_database() -> None:
    """Clear all inventory records from MongoDB."""
    client = await init_db()

    try:
        result = await InventoryModel.delete_all()
        count = result.deleted_count if result else 0
        print(f"✅ Cleared {count} inventory records from database")

    finally:
        client.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        print("🗑️  Clearing database...")
        asyncio.run(clear_database())
    else:
        print("🌱 Seeding database...")
        asyncio.run(seed_database())

