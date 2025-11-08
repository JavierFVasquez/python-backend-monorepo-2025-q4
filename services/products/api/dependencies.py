import os
from collections.abc import AsyncGenerator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from services.products.domain.ports import CachePort, ProductRepository
from services.products.infrastructure.redis_cache import RedisCache
from services.products.infrastructure.supabase_repository import SupabaseProductRepository

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(env_path, override=True)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def get_database_url(async_driver: bool = True) -> str:
    """
    Obtener URL de base de datos desde variables de entorno.
    
    Args:
        async_driver: Si True usa asyncpg, si False usa psycopg2 (para migraciones)
    """
    # Usar DATABASE_URL directamente desde .env
    db_url = os.getenv("DATABASE_URL", "")

    if db_url:
        # Solo cambiar el driver, mantener el resto de la URL intacta
        if async_driver:
            # asyncpg necesita +asyncpg en el protocolo
            url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        else:
            # psycopg2 usa postgresql:// sin el +asyncpg
            url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)

        return url

    # Fallback para desarrollo local
    driver = "+asyncpg" if async_driver else ""
    return f"postgresql{driver}://postgres:postgres@localhost:54321/products_db"


DATABASE_URL = get_database_url()

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

redis_cache = RedisCache(REDIS_URL)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_product_repository(
    session: AsyncSession = None,
) -> ProductRepository:
    if session is None:
        async with async_session_maker() as session:
            return SupabaseProductRepository(session)
    return SupabaseProductRepository(session)


async def get_cache() -> CachePort:
    return redis_cache


async def get_repository_async() -> ProductRepository:
    """Factory para obtener repositorio asíncrono (para gRPC server)."""
    # Reusar el async session maker existente
    async with async_session_maker() as session:
        return SupabaseProductRepository(session)

