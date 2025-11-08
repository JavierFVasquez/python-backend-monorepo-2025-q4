import os
from pathlib import Path

from dotenv import load_dotenv

from services.inventory.domain.ports import InventoryRepository, ProductServicePort
from services.inventory.infrastructure.grpc.products_grpc_client import ProductsGrpcClient
from services.inventory.infrastructure.mongodb_repository import MongoDBInventoryRepository

# Load environment variables
env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(env_path, override=True)

# gRPC configuration
PRODUCTS_GRPC_URL = os.getenv("PRODUCTS_GRPC_URL", "localhost:50051")
PRODUCTS_GRPC_USE_SSL = os.getenv("PRODUCTS_GRPC_USE_SSL", "false").lower() == "true"
PRODUCTS_GRPC_TIMEOUT = int(os.getenv("PRODUCTS_GRPC_TIMEOUT", "30"))


async def get_inventory_repository() -> InventoryRepository:
    return MongoDBInventoryRepository()


async def get_product_service() -> ProductServicePort:
    """
    Factory para obtener el cliente de Products Service.
    Ahora usa gRPC en lugar de HTTP para comunicación inter-service.

    Configuración:
    - PRODUCTS_GRPC_URL: URL del servidor gRPC
    - PRODUCTS_GRPC_USE_SSL: "true" para usar SSL/TLS (auto-detecta puerto 443)
    - PRODUCTS_GRPC_TIMEOUT: Timeout en segundos (default: 30)
    """
    return ProductsGrpcClient(
        grpc_url=PRODUCTS_GRPC_URL,
        use_ssl=PRODUCTS_GRPC_USE_SSL,
        timeout=PRODUCTS_GRPC_TIMEOUT,
    )

