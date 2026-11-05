"""Tests for health endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_liveness(client: AsyncClient) -> None:
    resp = await client.get("/health/live")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.anyio
async def test_readiness_returns_json(client: AsyncClient) -> None:
    """Readiness returns structured JSON even if backends are down."""
    resp = await client.get("/health/ready")
    data = resp.json()
    assert "status" in data
    assert "checks" in data
    assert isinstance(data["checks"], dict)
