"""NyaySetu application factory."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.core.config import get_settings
from app.core.db import dispose_engine
from app.core.errors import DomainError, domain_exception_handler, unhandled_exception_handler
from app.core.logging import setup_logging
from app.core.middleware import AccessLogMiddleware, RequestIDMiddleware, SecurityHeadersMiddleware
from app.modules.auth.router import router as auth_router
from app.modules.firms.router import router as firms_router
from app.modules.health.router import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    settings = get_settings()

    setup_logging(
        json_output=not settings.is_local,
        log_level="DEBUG" if settings.is_local else "INFO",
    )

    app = FastAPI(
        title="NyaySetu API",
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url=None,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # ── Exception handlers ──
    app.add_exception_handler(DomainError, domain_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # ── Middleware (order: executed top to bottom for ASGI wrapper, outermost is RequestID) ──
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ──
    app.include_router(health_router)
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(firms_router, prefix="/api/v1")

    return app


app = create_app()
