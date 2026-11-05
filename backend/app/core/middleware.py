"""Application middleware: request ID injection, structured access logging, security headers."""

from __future__ import annotations

import time

import structlog
from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from uuid_utils import uuid7

from app.core.errors import unhandled_exception_handler


class RequestIDMiddleware:
    """Accept X-Request-ID from caller or generate UUIDv7. Pure ASGI middleware."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        incoming = headers.get(b"x-request-id", b"").decode("latin1").strip()
        request_id = incoming if incoming else str(uuid7())

        if "state" not in scope:
            scope["state"] = {}
        scope["state"]["request_id"] = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                resp_headers = MutableHeaders(scope=message)
                resp_headers["X-Request-ID"] = request_id
            await send(message)

        await self.app(scope, receive, send_wrapper)


class SecurityHeadersMiddleware:
    """Inject standard security headers. Pure ASGI middleware."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-Frame-Options"] = "DENY"
                headers["X-XSS-Protection"] = "1; mode=block"
                headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
                headers["Cache-Control"] = "no-store"
                headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
            await send(message)

        await self.app(scope, receive, send_wrapper)


class AccessLogMiddleware:
    """Emit one structured log line per request. No request bodies."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        logger = structlog.get_logger("app.access")
        start = time.perf_counter()
        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            # Fallback for unexpected exceptions reaching the outer middleware
            request = Request(scope)
            resp = await unhandled_exception_handler(request, exc)
            await resp(scope, receive, send_wrapper)
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            state = scope.get("state", {})
            user_id = state.get("user_id")
            firm_id = state.get("firm_id")

            logger.info(
                "request",
                method=scope.get("method"),
                route=scope.get("path"),
                status=status_code,
                duration_ms=duration_ms,
                user_id=str(user_id) if user_id else None,
                firm_id=str(firm_id) if firm_id else None,
            )
