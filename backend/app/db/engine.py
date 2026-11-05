"""Async SQLAlchemy engine + session factory."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

try:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.APP_ENV == "development",
        pool_size=10,
        max_overflow=20,
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
except Exception:
    # Graceful fallback when DB driver (e.g. asyncpg) is not yet installed in local dev/test environment
    engine = None
    AsyncSessionLocal = None


async def get_db() -> AsyncSession:
    if AsyncSessionLocal is None:
        raise RuntimeError(
            "Database engine is not initialized. Please install asyncpg or check DATABASE_URL."
        )
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

