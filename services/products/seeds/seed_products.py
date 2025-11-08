"""
Seed data for Products service.

Usage:
    poetry run python -m seeds.seed_products
"""
import asyncio
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Load environment variables from .env BEFORE importing dependencies
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path, override=True)

from api.dependencies import async_session_maker
from infrastructure.database.models import ProductModel

SEED_PRODUCTS = [
    {
        "id": 'product-01',
        "name": "iPhone 15 Pro",
        "description": "Latest Apple iPhone with A17 Pro chip, 256GB storage, and titanium design",
        "price": Decimal("1199.99"),
        "images": [
            "https://cdn.dummyjson.com/product-images/smartphones/iphone-13-pro/1.webp",
            "https://cdn.dummyjson.com/product-images/smartphones/iphone-13-pro/2.webp",
            "https://cdn.dummyjson.com/product-images/smartphones/iphone-13-pro/3.webp",
        ],
    },
    {
        "id": 'product-02',
        "name": "MacBook Pro 16\"",
        "description": "Apple MacBook Pro with M3 Max chip, 32GB RAM, 1TB SSD",
        "price": Decimal("2999.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/laptops/Apple%20MacBook%20Pro%2014%20Inch%20Space%20Grey/1.png",
            "https://cdn.dummyjson.com/products/images/laptops/Apple%20MacBook%20Pro%2014%20Inch%20Space%20Grey/2.png",
        ],
    },
    {
        "id": 'product-03',
        "name": "AirPods Pro (2nd generation)",
        "description": "Active noise cancellation, adaptive transparency, and personalized spatial audio",
        "price": Decimal("249.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/mobile-accessories/Apple%20Airpods/1.png",
        ],
    },
    {
        "id": 'product-04',
        "name": "iPad Air M2",
        "description": "iPad Air with M2 chip, 11-inch Liquid Retina display, 256GB",
        "price": Decimal("749.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/tablets/iPad%20Mini%202021%20Starlight/1.png",
            "https://cdn.dummyjson.com/products/images/tablets/iPad%20Mini%202021%20Starlight/2.png",
        ],
    },
    {
        "id": 'product-05',
        "name": "Samsung Galaxy S24 Ultra",
        "description": "Samsung flagship with AI features, S Pen, 512GB storage",
        "price": Decimal("1299.99"),
        "images": [
            "https://cdn.dummyjson.com/product-images/smartphones/samsung-galaxy-s7/1.webp",
            "https://cdn.dummyjson.com/product-images/smartphones/samsung-galaxy-s7/2.webp",
            "https://cdn.dummyjson.com/product-images/smartphones/samsung-galaxy-s7/3.webp",
        ],
    },
    {
        "id": 'product-06',
        "name": "Sony WH-1000XM5",
        "description": "Industry-leading noise canceling wireless headphones with premium sound quality",
        "price": Decimal("399.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/mobile-accessories/Beats%20Flex%20Wireless%20Earphones/1.png",
        ],
    },
    {
        "id": 'product-07',
        "name": "PlayStation 5",
        "description": "Sony PS5 console with ultra-high speed SSD and 4K gaming",
        "price": Decimal("499.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/vehicle/Dodge%20Hornet%20GT%20Plus/1.png",
            "https://cdn.dummyjson.com/products/images/vehicle/Dodge%20Hornet%20GT%20Plus/2.png",
        ],
    },
    {
        "id": 'product-08',
        "name": "Nintendo Switch OLED",
        "description": "Nintendo Switch with vibrant 7-inch OLED screen and enhanced audio",
        "price": Decimal("349.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/laptops/Huawei%20Matebook%20X%20Pro/1.png",
        ],
    },
    {
        "id": 'product-09',
        "name": "Apple Watch Series 9",
        "description": "Advanced health and fitness features with always-on Retina display",
        "price": Decimal("429.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/mens-watches/Brown%20Leather%20Belt%20Watch/1.png",
            "https://cdn.dummyjson.com/products/images/mens-watches/Brown%20Leather%20Belt%20Watch/2.png",
        ],
    },
    {
        "id": 'product-10',
        "name": "DJI Mini 4 Pro",
        "description": "Compact drone with 4K HDR video, omnidirectional obstacle sensing",
        "price": Decimal("759.99"),
        "images": [
            "https://cdn.dummyjson.com/product-images/furniture/bedside-table-african-cherry/1.webp",
            "https://cdn.dummyjson.com/product-images/furniture/bedside-table-african-cherry/2.webp",
            "https://cdn.dummyjson.com/product-images/furniture/bedside-table-african-cherry/3.webp",
        ],
    },
    {
        "id": 'product-11',
        "name": "GoPro HERO12 Black",
        "description": "Waterproof action camera with 5.3K60 video and HyperSmooth stabilization",
        "price": Decimal("399.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/sports-accessories/Baseball%20Glove/1.png",
        ],
    },
    {
        "id": 'product-12',
        "name": "Logitech MX Master 3S",
        "description": "Advanced wireless mouse with ultra-fast scrolling and ergonomic design",
        "price": Decimal("99.99"),
        "images": [
            "https://cdn.dummyjson.com/product-images/mobile-accessories/amazon-echo-plus/1.webp",
            "https://cdn.dummyjson.com/product-images/mobile-accessories/amazon-echo-plus/2.webp",
        ],
    },
    {
        "id": 'product-13',
        "name": "Dell XPS 15",
        "description": "Premium laptop with 12th Gen Intel i7, 16GB RAM, 512GB SSD, 15.6\" OLED display",
        "price": Decimal("1799.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/laptops/New%20DELL%20XPS%2013%209300%20Laptop/1.png",
        ],
    },
    {
        "id": 'product-14',
        "name": "Samsung 55\" QLED 4K TV",
        "description": "Quantum Dot technology, 4K resolution, HDR10+, Smart TV features",
        "price": Decimal("899.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/groceries/Protein%20Powder/1.png",
            "https://cdn.dummyjson.com/products/images/groceries/Red%20Onions/1.png",
        ],
    },
    {
        "id": 'product-15',
        "name": "Bose QuietComfort 45",
        "description": "Premium noise-canceling wireless headphones with superior comfort",
        "price": Decimal("329.99"),
        "images": [
            "https://cdn.dummyjson.com/product-images/mobile-accessories/apple-homepod-mini-cosmic-grey/1.webp",
        ],
    },
    {
        "id": 'product-16',
        "name": "Canon EOS R6 Mark II",
        "description": "Full-frame mirrorless camera with 24.2MP sensor and 4K 60p video",
        "price": Decimal("2499.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/sports-accessories/Baseball%20Ball/1.png",
            "https://cdn.dummyjson.com/products/images/sports-accessories/Baseball%20Glove/1.png",
        ],
    },
    {
        "id": 'product-17',
        "name": "Amazon Echo Dot (5th Gen)",
        "description": "Smart speaker with Alexa, improved audio and temperature sensor",
        "price": Decimal("49.99"),
        "images": [
            "https://cdn.dummyjson.com/product-images/mobile-accessories/amazon-echo-plus/1.webp",
            "https://cdn.dummyjson.com/product-images/mobile-accessories/amazon-echo-plus/2.webp",
        ],
    },
    {
        "id": 'product-18',
        "name": "Google Pixel 8 Pro",
        "description": "Google's flagship phone with AI features, advanced camera, 256GB storage",
        "price": Decimal("999.99"),
        "images": [
            "https://cdn.dummyjson.com/product-images/smartphones/samsung-galaxy-s8/1.webp",
            "https://cdn.dummyjson.com/product-images/smartphones/samsung-galaxy-s8/2.webp",
            "https://cdn.dummyjson.com/product-images/smartphones/samsung-galaxy-s8/3.webp",
        ],
    },
    {
        "id": 'product-19',
        "name": "Razer BlackWidow V4 Pro",
        "description": "Mechanical gaming keyboard with RGB lighting and programmable keys",
        "price": Decimal("229.99"),
        "images": [
            "https://cdn.dummyjson.com/product-images/fragrances/gucci-bloom-eau-de/1.webp",
            "https://cdn.dummyjson.com/product-images/fragrances/gucci-bloom-eau-de/2.webp",
            "https://cdn.dummyjson.com/product-images/fragrances/gucci-bloom-eau-de/3.webp",
        ],
    },
    {
        "id": 'product-20',
        "name": "HP LaserJet Pro M404n",
        "description": "Fast monochrome laser printer for home office and small business",
        "price": Decimal("279.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/furniture/Annibale%20Colombo%20Sofa/1.png",
        ],
    },
    {
        "id": 'product-21',
        "name": "Microsoft Surface Pro 9",
        "description": "2-in-1 tablet/laptop with Intel i5, 8GB RAM, 256GB SSD, 13\" touchscreen",
        "price": Decimal("1099.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/tablets/Samsung%20Galaxy%20Tab%20S8%20Plus%20Grey/1.png",
            "https://cdn.dummyjson.com/products/images/tablets/Samsung%20Galaxy%20Tab%20S8%20Plus%20Grey/2.png",
        ],
    },
    {
        "id": 'product-22',
        "name": "Fitbit Charge 6",
        "description": "Advanced fitness tracker with heart rate monitoring and GPS",
        "price": Decimal("159.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/mens-watches/Longines%20Master%20Collection/1.png",
        ],
    },
    {
        "id": 'product-23',
        "name": "Kindle Paperwhite",
        "description": "Waterproof e-reader with 6.8\" glare-free display and adjustable warm light",
        "price": Decimal("139.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/tablets/iPad%20Mini%202021%20Starlight/1.png",
        ],
    },
    {
        "id": 'product-24',
        "name": "Asus ROG Strix Gaming Monitor 27\"",
        "description": "1440p 165Hz gaming monitor with G-SYNC and HDR",
        "price": Decimal("449.99"),
        "images": [
            "https://cdn.dummyjson.com/product-images/mobile-accessories/tv-studio-camera-pedestal/1.webp",
        ],
    },
    {
        "id": 'product-25',
        "name": "SanDisk Extreme Portable SSD 1TB",
        "description": "Rugged external SSD with 1050MB/s read speeds and IP55 rating",
        "price": Decimal("129.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/laptops/Asus%20Zenbook%20Pro%20Dual%20Screen%20Laptop/1.png",
        ],
    },
    {
        "id": 'product-26',
        "name": "Anker PowerCore 26800mAh",
        "description": "High-capacity portable charger with 3 USB ports and fast charging",
        "price": Decimal("69.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/mobile-accessories/Apple%20MagSafe%20Battery%20Pack/1.png",
        ],
    },
    {
        "id": 'product-27',
        "name": "Logitech C920 HD Pro Webcam",
        "description": "Full HD 1080p webcam with stereo audio and automatic light correction",
        "price": Decimal("79.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/sports-accessories/Cricket%20Helmet/1.png",
        ],
    },
    {
        "id": 'product-28',
        "name": "Meta Quest 3",
        "description": "Advanced VR headset with mixed reality capabilities and 128GB storage",
        "price": Decimal("499.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/sunglasses/Classic%20Sun%20Glasses/1.png",
            "https://cdn.dummyjson.com/products/images/sunglasses/Classic%20Sun%20Glasses/2.png",
        ],
    },
    {
        "id": 'product-29',
        "name": "JBL Flip 6",
        "description": "Portable Bluetooth speaker with powerful sound and IP67 waterproof rating",
        "price": Decimal("129.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/mobile-accessories/Selfie%20Lamp%20with%20iPhone/1.png",
        ],
    },
    {
        "id": 'product-30',
        "name": "Lenovo ThinkPad X1 Carbon Gen 11",
        "description": "Business ultrabook with Intel i7, 16GB RAM, 512GB SSD, 14\" display",
        "price": Decimal("1699.99"),
        "images": [
            "https://cdn.dummyjson.com/product-images/laptops/lenovo-yoga-920/1.webp",
            "https://cdn.dummyjson.com/product-images/laptops/lenovo-yoga-920/2.webp",
            "https://cdn.dummyjson.com/product-images/laptops/lenovo-yoga-920/3.webp",
        ],
    },
    {
        "id": 'product-31',
        "name": "TP-Link WiFi 6 Router AX3000",
        "description": "Dual-band wireless router with WiFi 6, 4 Gigabit LAN ports",
        "price": Decimal("99.99"),
        "images": [
            "https://cdn.dummyjson.com/product-images/mobile-accessories/beats-flex-wireless-earphones/1.webp",
        ],
    },
    {
        "id": 'product-32',
        "name": "Seagate Backup Plus 4TB",
        "description": "Portable external hard drive with USB 3.0 and automatic backup software",
        "price": Decimal("109.99"),
        "images": [
            "https://cdn.dummyjson.com/products/images/kitchen-accessories/Microwave%20Oven/1.png",
        ],
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

