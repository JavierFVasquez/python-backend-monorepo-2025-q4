"""
gRPC Client - Puerto de salida (Driven Adapter)

Este adaptador implementa el puerto ProductServicePort
usando gRPC para comunicación con Products Service.
"""
import logging
from decimal import Decimal
from typing import Any

import grpc

from services.inventory.domain.ports import ProductServicePort
from services.inventory.infrastructure.grpc.products import (
    products_pb2,
    products_pb2_grpc,
)

logger = logging.getLogger(__name__)


class ProductsGrpcClient(ProductServicePort):
    """
    Cliente gRPC para Products Service.
    
    Arquitectura Hexagonal:
    - Es un adaptador de salida (driven adapter)
    - Implementa el puerto ProductServicePort
    - Traduce llamadas del dominio a peticiones gRPC
    """

    def __init__(self, grpc_url: str) -> None:
        """
        Args:
            grpc_url: URL del servidor gRPC (ej: "localhost:50051")
        """
        self.grpc_url = grpc_url
        self._channel: grpc.aio.Channel | None = None
        self._stub: products_pb2_grpc.ProductsServiceStub | None = None

    async def _ensure_connection(self) -> None:
        """Asegurar que hay una conexión gRPC abierta."""
        if self._channel is None:
            self._channel = grpc.aio.insecure_channel(self.grpc_url)
            self._stub = products_pb2_grpc.ProductsServiceStub(self._channel)
            logger.info(f"gRPC channel created to {self.grpc_url}")

    async def close(self) -> None:
        """Cerrar la conexión gRPC."""
        if self._channel:
            await self._channel.close()
            self._channel = None
            self._stub = None
            logger.info("gRPC channel closed")

    async def get_product(
        self, product_id: str, request_id: str
    ) -> dict[str, Any] | None:
        """
        Obtener información de un producto vía gRPC.
        
        Args:
            product_id: ID del producto
            request_id: ID de la petición (para tracing)
            
        Returns:
            Diccionario con datos del producto o None si no existe
        """
        try:
            await self._ensure_connection()

            if self._stub is None:
                raise RuntimeError("gRPC stub not initialized")

            # Crear metadata para tracing
            metadata = (("x-request-id", request_id),)

            # Llamar al servicio gRPC
            response = await self._stub.GetProduct(
                products_pb2.GetProductRequest(product_id=product_id),
                metadata=metadata,
            )

            # Convertir respuesta gRPC a diccionario
            product = response.product
            return {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": Decimal(product.price),
                "images": list(product.images) if product.images else [],
                "created_at": product.created_at,
                "updated_at": product.updated_at,
            }

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                logger.warning(
                    f"Product {product_id} not found via gRPC "
                    f"(request_id: {request_id})"
                )
                return None
            logger.error(
                f"gRPC error getting product {product_id}: {e.code()} - "
                f"{e.details()} (request_id: {request_id})"
            )
            raise

        except Exception as e:
            logger.error(
                f"Error getting product {product_id} via gRPC: {e} "
                f"(request_id: {request_id})"
            )
            raise

    async def product_exists(self, product_id: str) -> bool:
        """
        Verificar si un producto existe.
        
        Args:
            product_id: ID del producto
            
        Returns:
            True si existe, False si no
        """
        try:
            await self._ensure_connection()

            if self._stub is None:
                raise RuntimeError("gRPC stub not initialized")

            response = await self._stub.ProductExists(
                products_pb2.ProductExistsRequest(product_id=product_id)
            )

            return response.exists

        except grpc.RpcError as e:
            logger.error(
                f"gRPC error checking product existence {product_id}: "
                f"{e.code()} - {e.details()}"
            )
            raise

        except Exception as e:
            logger.error(
                f"Error checking product existence {product_id} via gRPC: {e}"
            )
            raise


def get_products_grpc_client(grpc_url: str) -> ProductsGrpcClient:
    """
    Factory function para crear el cliente gRPC.
    
    Args:
        grpc_url: URL del servidor gRPC
        
    Returns:
        Cliente gRPC configurado
    """
    return ProductsGrpcClient(grpc_url)

