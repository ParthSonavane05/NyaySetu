"""Tests for error handling and RFC 7807-style error format."""

from __future__ import annotations

import pytest
from fastapi import APIRouter
from httpx import ASGITransport, AsyncClient

from app.core.errors import ConflictError, NotFoundError, ValidationFailedError
from app.main import create_app


def _make_app_with_error_routes():
    app = create_app()
    error_router = APIRouter(prefix="/test-errors")

    @error_router.get("/not-found")
    async def raise_not_found():
        raise NotFoundError(detail="Thing not found")

    @error_router.get("/conflict")
    async def raise_conflict():
        raise ConflictError()

    @error_router.get("/validation")
    async def raise_validation():
        errs = [
            {"field": "survey_no", "code": "invalid_format", "message": "Use format like 142/A"}
        ]
        raise ValidationFailedError(
            detail="One or more fields are invalid.",
            errors=errs,
        )

    @error_router.get("/unhandled")
    async def raise_unhandled():
        raise RuntimeError("boom")

    app.include_router(error_router)
    return app


@pytest.fixture
async def error_client() -> AsyncClient:
    app = _make_app_with_error_routes()
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac  # type: ignore[misc]


@pytest.mark.anyio
async def test_not_found_error_format(error_client: AsyncClient) -> None:
    resp = await error_client.get("/test-errors/not-found")
    assert resp.status_code == 404
    body = resp.json()
    assert body["code"] == "not_found"
    assert body["detail"] == "Thing not found"
    assert "request_id" in body
    assert body["status"] == 404
    assert "type" in body


@pytest.mark.anyio
async def test_conflict_error_format(error_client: AsyncClient) -> None:
    resp = await error_client.get("/test-errors/conflict")
    assert resp.status_code == 409
    body = resp.json()
    assert body["code"] == "conflict"
    assert body["status"] == 409


@pytest.mark.anyio
async def test_validation_error_with_errors_list(error_client: AsyncClient) -> None:
    resp = await error_client.get("/test-errors/validation")
    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == "validation_error"
    assert body["status"] == 422
    assert len(body["errors"]) == 1
    assert body["errors"][0]["field"] == "survey_no"


@pytest.mark.anyio
async def test_unhandled_exception_returns_500(error_client: AsyncClient) -> None:
    resp = await error_client.get("/test-errors/unhandled")
    assert resp.status_code == 500
    body = resp.json()
    assert body["code"] == "internal_error"
    assert body["status"] == 500
    assert "request_id" in body
    assert "boom" not in body["detail"]
    assert "RuntimeError" not in body.get("detail", "")
