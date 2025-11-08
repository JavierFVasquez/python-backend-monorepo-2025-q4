import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from libs.common.logging import setup_logging
from libs.common.middleware import ErrorHandlerMiddleware, RequestIDMiddleware
from services.products.api.dependencies import async_session_maker, engine
from services.products.api.routes import router as products_router
from services.products.infrastructure.database.models import Base
from services.products.infrastructure.grpc.grpc_server import serve_grpc
from services.products.infrastructure.supabase_repository import SupabaseProductRepository

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path, override=True)

SERVICE_NAME = "products"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logger = setup_logging(SERVICE_NAME, LOG_LEVEL)


async def run_grpc_server() -> None:
    """Run gRPC server in background."""
    grpc_port = int(os.getenv("PRODUCTS_GRPC_PORT", 50051))
    # Create a long-lived session for gRPC server
    session = async_session_maker()
    repository = SupabaseProductRepository(session)
    logger.info(f"Starting gRPC server on port {grpc_port}")
    await serve_grpc(repository, grpc_port)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info(f"{SERVICE_NAME} HTTP service starting up")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start gRPC server in background
    grpc_task = asyncio.create_task(run_grpc_server())

    yield

    # Shutdown
    logger.info(f"{SERVICE_NAME} service shutting down")
    grpc_task.cancel()
    try:
        await grpc_task
    except asyncio.CancelledError:
        pass
    await engine.dispose()


app = FastAPI(
    title="Products Service",
    description="Microservice for managing products - HTTP API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration - usar variables de entorno en producción
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
    max_age=3600,  # Cache preflight requests por 1 hora (evita problemas con 307)
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

app.include_router(products_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "http_port": os.getenv("PRODUCTS_SERVICE_PORT", "8001"),
        "grpc_port": os.getenv("PRODUCTS_GRPC_PORT", "50051"),
    }


if __name__ == "__main__":
    import uvicorn

    http_port = int(os.getenv("PRODUCTS_SERVICE_PORT", 8001))
    grpc_port = int(os.getenv("PRODUCTS_GRPC_PORT", 50051))

    logger.info("Starting Products Service:")
    logger.info(f"  HTTP API: http://0.0.0.0:{http_port}")
    logger.info(f"  gRPC API: grpc://0.0.0.0:{grpc_port}")

    # Run both HTTP and gRPC servers
    async def serve():
        # Start gRPC server in background
        grpc_task = asyncio.create_task(run_grpc_server())

        # Run HTTP server
        config = uvicorn.Config(
            "main:app",
            host="0.0.0.0",
            port=http_port,
            reload=True,
            reload_dirs=["services/products"]
        )
        server = uvicorn.Server(config)
        await server.serve()

        # Wait for gRPC to finish (it won't unless interrupted)
        await grpc_task

    asyncio.run(serve())

