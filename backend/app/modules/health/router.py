"""Health check endpoints."""

from __future__ import annotations

import asyncio
from typing import Any

import structlog
from fastapi import APIRouter, status
from fastapi.responses import ORJSONResponse

from app.core.config import get_settings

router = APIRouter(prefix="/health", tags=["health"])
logger = structlog.get_logger("app.health")


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness() -> ORJSONResponse:
    """Check database, Redis, and S3 connectivity with strict short timeouts."""
    checks: dict[str, Any] = {}
    all_ok = True

    # ── Database ──
    async def _check_db() -> None:
        from sqlalchemy import text

        from app.core.db import get_engine

        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

    try:
        await asyncio.wait_for(_check_db(), timeout=1.0)
        checks["database"] = "ok"
    except Exception:
        logger.warning("readiness_check_failed", service="database")
        checks["database"] = "unavailable"
        all_ok = False

    # ── Redis ──
    async def _check_redis() -> None:
        from redis.asyncio import Redis

        settings = get_settings()
        r: Redis = Redis.from_url(
            settings.redis_url,
            socket_connect_timeout=1.0,
            socket_timeout=1.0,
        )  # type: ignore[assignment]
        try:
            await r.ping()
        finally:
            await r.aclose()

    try:
        await asyncio.wait_for(_check_redis(), timeout=1.0)
        checks["redis"] = "ok"
    except Exception:
        logger.warning("readiness_check_failed", service="redis")
        checks["redis"] = "unavailable"
        all_ok = False

    # ── S3 / MinIO ──
    def _check_s3() -> None:
        import boto3
        from botocore.config import Config as BotoConfig

        settings = get_settings()
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            config=BotoConfig(connect_timeout=1, read_timeout=1, retries={"max_attempts": 0}),
        )
        s3.head_bucket(Bucket=settings.s3_bucket_name)

    try:
        await asyncio.wait_for(asyncio.to_thread(_check_s3), timeout=1.0)
        checks["storage"] = "ok"
    except Exception:
        logger.warning("readiness_check_failed", service="storage")
        checks["storage"] = "unavailable"
        all_ok = False

    return ORJSONResponse(
        status_code=status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "ok" if all_ok else "degraded", "checks": checks},
    )
