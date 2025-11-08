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


async def get_inventory_repository() -> InventoryRepository:
    return MongoDBInventoryRepository()


async def get_product_service() -> ProductServicePort:
    """
    Factory para obtener el cliente de Products Service.
    Ahora usa gRPC en lugar de HTTP para comunicación inter-service.
    """
    return ProductsGrpcClient(PRODUCTS_GRPC_URL)

