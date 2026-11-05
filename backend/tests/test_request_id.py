"""Tests for request ID propagation."""

from __future__ import annotations

import uuid

import pytest
from fastapi import APIRouter
from httpx import ASGITransport, AsyncClient

from app.core.errors import NotFoundError
from app.main import create_app


@pytest.mark.anyio
async def test_request_id_generated(client: AsyncClient) -> None:
    """Response must include X-Request-ID even if not sent."""
    resp = await client.get("/health/live")
    rid = resp.headers.get("x-request-id")
    assert rid is not None
    assert len(rid) > 0


@pytest.mark.anyio
async def test_request_id_echoed(client: AsyncClient) -> None:
    """Caller-supplied X-Request-ID must be echoed back."""
    custom_id = f"test-{uuid.uuid4()}"
    resp = await client.get("/health/live", headers={"X-Request-ID": custom_id})
    assert resp.headers["x-request-id"] == custom_id


@pytest.mark.anyio
async def test_request_id_in_error_response() -> None:
    """Error responses must include the request_id in the body."""
    custom_id = f"req-{uuid.uuid4()}"
    app = create_app()
    r = APIRouter()

    @r.get("/test-rid-error")
    async def err():
        raise NotFoundError()

    app.include_router(r)

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/test-rid-error", headers={"X-Request-ID": custom_id})
    assert resp.status_code == 404
    body = resp.json()
    assert body["request_id"] == custom_id
