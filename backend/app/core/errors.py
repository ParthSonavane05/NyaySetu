"""Domain exceptions and RFC 7807-style error responses."""

from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import ORJSONResponse
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_502_BAD_GATEWAY,
)


class DomainError(Exception):
    """Base for all domain exceptions."""

    status_code: int = HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "internal_error"
    title: str = "Internal server error"
    detail: str = "An unexpected error occurred."

    def __init__(
        self,
        detail: str | None = None,
        title: str | None = None,
        code: str | None = None,
        status_code: int | None = None,
        errors: list[dict[str, Any]] | None = None,
        **extra: Any,
    ) -> None:
        self.detail = detail or self.__class__.detail
        self.title = title or self.__class__.title
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        self.errors = errors
        self.extra = extra
        super().__init__(self.detail)


class NotFoundError(DomainError):
    status_code = HTTP_404_NOT_FOUND
    code = "not_found"
    title = "Resource not found"
    detail = "The requested resource was not found."


class PermissionDeniedError(DomainError):
    """Maps to 404 to avoid leaking resource existence."""

    status_code = HTTP_404_NOT_FOUND
    code = "not_found"
    title = "Resource not found"
    detail = "The requested resource was not found."


class ConflictError(DomainError):
    status_code = HTTP_409_CONFLICT
    code = "conflict"
    title = "Conflict"
    detail = "The request conflicts with the current state."


class ValidationFailedError(DomainError):
    status_code = HTTP_422_UNPROCESSABLE_ENTITY
    code = "validation_error"
    title = "Request validation failed"
    detail = "One or more fields are invalid."


class ExternalServiceError(DomainError):
    status_code = HTTP_502_BAD_GATEWAY
    code = "external_service_error"
    title = "External service error"
    detail = "An upstream service is unavailable."


class RateLimitedError(DomainError):
    status_code = HTTP_429_TOO_MANY_REQUESTS
    code = "rate_limited"
    title = "Rate limit exceeded"
    detail = "Too many requests. Please try again later."


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def build_error_body(
    *,
    code: str,
    title: str,
    status: int,
    detail: str,
    request_id: str,
    errors: list[dict[str, Any]] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "type": f"https://api.nyaysetu.in/errors/{code}",
        "code": code,
        "title": title,
        "status": status,
        "detail": detail,
        "request_id": request_id,
    }
    if errors:
        body["errors"] = errors
    if extra:
        body["meta"] = extra
    return body


async def domain_exception_handler(request: Request, exc: DomainError) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content=build_error_body(
            code=exc.code,
            title=exc.title,
            status=exc.status_code,
            detail=exc.detail,
            request_id=_request_id(request),
            errors=exc.errors,
            extra=exc.extra if exc.extra else None,
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    import structlog

    logger = structlog.get_logger("app.errors")
    logger.error(
        "unhandled_exception",
        exc_type=type(exc).__name__,
        exc_val=str(exc),
        request_id=_request_id(request),
    )
    return ORJSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=build_error_body(
            code="internal_error",
            title="Internal server error",
            status=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
            request_id=_request_id(request),
        ),
    )
