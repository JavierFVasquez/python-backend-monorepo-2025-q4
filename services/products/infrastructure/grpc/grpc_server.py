"""
gRPC Server - Puerto de entrada (Driving Adapter)

Este adaptador expone la funcionalidad del dominio vía gRPC
para comunicación inter-service.
"""
import logging

import grpc

from libs.common.errors import NotFoundError
from services.products.application.get_product import GetProduct
from services.products.application.list_products import ListProducts
from services.products.domain.ports import ProductRepository
from services.products.infrastructure.grpc.products import (
    products_pb2,
    products_pb2_grpc,
)

logger = logging.getLogger(__name__)


class ProductsServicer(products_pb2_grpc.ProductsServiceServicer):
    """
    Implementación del servidor gRPC para Products Service.
    
    Arquitectura Hexagonal:
    - Es un adaptador de entrada (driving adapter)
    - Traduce peticiones gRPC a casos de uso del dominio
    - No contiene lógica de negocio
    """

    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository
        self.get_product_use_case = GetProduct(repository)
        self.list_products_use_case = ListProducts(repository)

    async def GetProduct(
        self,
        request: products_pb2.GetProductRequest,
        context: grpc.aio.ServicerContext,
    ) -> products_pb2.GetProductResponse:
        """
        Obtener un producto por ID.
        """
        try:
            product = await self.get_product_use_case.execute(request.product_id)

            logger.info(f"GetProduct called from Inventory for product_id={request.product_id} with request_id={context.request_id}") # Just for demonstration purposes

            return products_pb2.GetProductResponse(
                product=products_pb2.Product(
                    id=product.id,
                    name=product.name,
                    description=product.description or "",
                    price=str(product.price),
                    created_at=product.created_at.isoformat(),
                    updated_at=product.updated_at.isoformat(),
                )
            )
        except NotFoundError as e:
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"Error in GetProduct: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL, "Internal server error"
            )

    async def ProductExists(
        self,
        request: products_pb2.ProductExistsRequest,
        context: grpc.aio.ServicerContext,
    ) -> products_pb2.ProductExistsResponse:
        """
        Verificar si un producto existe.
        """
        try:
            product = await self.repository.get_by_id(request.product_id)

            if product:
                return products_pb2.ProductExistsResponse(
                    exists=True,
                    product=products_pb2.Product(
                        id=product.id,
                        name=product.name,
                        description=product.description or "",
                        price=str(product.price),
                        created_at=product.created_at.isoformat(),
                        updated_at=product.updated_at.isoformat(),
                    ),
                )
            return products_pb2.ProductExistsResponse(exists=False)

        except Exception as e:
            logger.error(f"Error in ProductExists: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL, "Internal server error"
            )

    async def ListProducts(
        self,
        request: products_pb2.ListProductsRequest,
        context: grpc.aio.ServicerContext,
    ) -> products_pb2.ListProductsResponse:
        """
        Listar productos con paginación.
        """
        try:
            products, total = await self.list_products_use_case.execute(
                page=request.page or 1, size=request.size or 10
            )

            return products_pb2.ListProductsResponse(
                products=[
                    products_pb2.Product(
                        id=p.id,
                        name=p.name,
                        description=p.description or "",
                        price=str(p.price),
                        created_at=p.created_at.isoformat(),
                        updated_at=p.updated_at.isoformat(),
                    )
                    for p in products
                ],
                total=total,
                page=request.page or 1,
                size=request.size or 10,
            )

        except Exception as e:
            logger.error(f"Error in ListProducts: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL, "Internal server error"
            )


async def serve_grpc(repository: ProductRepository, port: int = 50051) -> None:
    """
    Iniciar el servidor gRPC.
    
    Args:
        repository: Repositorio de productos
        port: Puerto donde escuchará el servidor gRPC
    """
    server = grpc.aio.server()
    products_pb2_grpc.add_ProductsServiceServicer_to_server(
        ProductsServicer(repository), server
    )
    server.add_insecure_port(f"[::]:{port}")

    logger.info(f"Starting gRPC server on port {port}")
    await server.start()
    await server.wait_for_termination()

