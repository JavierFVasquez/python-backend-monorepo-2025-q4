import os
from contextlib import asynccontextmanager
from pathlib import Path

from beanie import init_beanie
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from libs.common.logging import setup_logging
from libs.common.middleware import ErrorHandlerMiddleware, RequestIDMiddleware
from services.inventory.api.routes import router as inventory_router
from services.inventory.infrastructure.database.models import InventoryModel

# Load environment variables
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path, override=True)

SERVICE_NAME = "inventory"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "inventory_db")

logger = setup_logging(SERVICE_NAME, LOG_LEVEL)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info(f"{SERVICE_NAME} service starting up")
    client = AsyncIOMotorClient(MONGODB_URI)
    database = client[MONGODB_DATABASE]
    await init_beanie(database=database, document_models=[InventoryModel])

    yield

    # Shutdown
    logger.info(f"{SERVICE_NAME} service shutting down")


app = FastAPI(
    title="Inventory Service",
    description="Microservice for managing product inventory",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration - usar variables de entorno en producción
CORS_ORIGINS_ENV = os.getenv("CORS_ORIGINS", "")

# Si CORS_ORIGINS está vacío o es "*", permitir todos los orígenes sin credentials
# Si tiene valores específicos, usar esos y permitir credentials
if CORS_ORIGINS_ENV and CORS_ORIGINS_ENV != "*":
    ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_ENV.split(",")]
    ALLOW_CREDENTIALS = True
else:
    # En desarrollo: permitir todos los orígenes sin credentials
    ALLOWED_ORIGINS = ["*"]
    ALLOW_CREDENTIALS = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
    max_age=3600,  # Cache preflight requests por 1 hora (evita problemas con 307)
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

app.include_router(inventory_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("INVENTORY_SERVICE_PORT", 8002))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

