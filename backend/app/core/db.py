"""Async SQLAlchemy engine, session factory, and request-scoped dependency."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            echo=settings.database_echo,
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields a session with per-request transaction."""
    factory = get_session_factory()
    async with factory() as session:
        async with session.begin():
            yield session


async def set_rls_context(
    session: AsyncSession,
    *,
    firm_id: UUID,
    user_id: UUID,
) -> None:
    """Set PostgreSQL session-local variables for Row-Level Security."""
    await session.execute(text("SET LOCAL app.firm_id = :fid"), {"fid": str(firm_id)})
    await session.execute(text("SET LOCAL app.user_id = :uid"), {"uid": str(user_id)})


async def dispose_engine() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
