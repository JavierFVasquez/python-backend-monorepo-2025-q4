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

    def __init__(
        self,
        grpc_url: str,
        use_ssl: bool = False,
        timeout: int = 30,
    ) -> None:
        """
        Args:
            grpc_url: URL del servidor gRPC (ej: "localhost:50051")
            use_ssl: Si debe usar canal seguro (SSL/TLS). Auto-detecta si el puerto es 443
            timeout: Timeout en segundos para operaciones gRPC
        """
        self.grpc_url = grpc_url
        self._channel: grpc.aio.Channel | None = None
        self._stub: products_pb2_grpc.ProductsServiceStub | None = None

        # Auto-detectar SSL si el puerto es 443
        if not use_ssl and ":443" in grpc_url:
            use_ssl = True
            logger.info(f"Auto-detected SSL for port 443: {grpc_url}")

        self.use_ssl = use_ssl
        self.timeout = timeout

    def _get_channel_options(self) -> list[tuple[str, Any]]:
        """
        Configurar opciones del canal gRPC para mejor estabilidad.

        Returns:
            Lista de opciones del canal
        """
        return [
            # Keep-alive settings - previenen que el canal se cierre
            ("grpc.keepalive_time_ms", 30000),  # 30 segundos
            ("grpc.keepalive_timeout_ms", 10000),  # 10 segundos
            ("grpc.keepalive_permit_without_calls", True),
            ("grpc.http2.max_pings_without_data", 0),

            # Retry y timeout settings
            ("grpc.initial_reconnect_backoff_ms", 1000),
            ("grpc.max_reconnect_backoff_ms", 5000),
            ("grpc.min_reconnect_backoff_ms", 1000),

            # Message size limits (10MB)
            ("grpc.max_send_message_length", 10 * 1024 * 1024),
            ("grpc.max_receive_message_length", 10 * 1024 * 1024),

            # DNS resolution
            ("grpc.dns_min_time_between_resolutions_ms", 10000),
        ]

    async def _ensure_connection(self) -> None:
        """Asegurar que hay una conexión gRPC abierta."""
        if self._channel is None:
            options = self._get_channel_options()

            if self.use_ssl:
                # Canal seguro con SSL/TLS para producción
                credentials = grpc.ssl_channel_credentials()
                self._channel = grpc.aio.secure_channel(
                    self.grpc_url,
                    credentials,
                    options=options,
                )
                logger.info(f"gRPC secure channel created to {self.grpc_url}")
            else:
                # Canal inseguro para desarrollo local
                self._channel = grpc.aio.insecure_channel(
                    self.grpc_url,
                    options=options,
                )
                logger.info(f"gRPC insecure channel created to {self.grpc_url}")

            self._stub = products_pb2_grpc.ProductsServiceStub(self._channel)

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

            # Llamar al servicio gRPC con timeout
            response = await self._stub.GetProduct(
                products_pb2.GetProductRequest(product_id=product_id),
                metadata=metadata,
                timeout=self.timeout,
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
                products_pb2.ProductExistsRequest(product_id=product_id),
                timeout=self.timeout,
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


def get_products_grpc_client(
    grpc_url: str,
    use_ssl: bool = False,
    timeout: int = 30,
) -> ProductsGrpcClient:
    """
    Factory function para crear el cliente gRPC.

    Args:
        grpc_url: URL del servidor gRPC
        use_ssl: Si debe usar SSL/TLS (auto-detecta puerto 443)
        timeout: Timeout en segundos para operaciones gRPC

    Returns:
        Cliente gRPC configurado
    """
    return ProductsGrpcClient(grpc_url, use_ssl=use_ssl, timeout=timeout)
