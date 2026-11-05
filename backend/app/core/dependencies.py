"""Authentication and security dependencies for FastAPI endpoints."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID

from fastapi import Depends, Header, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_crypto import decode_access_token
from app.core.db import get_db_session
from app.core.errors import DomainError, NotFoundError, PermissionDeniedError
from app.core.permissions import get_capabilities_for_role
from app.modules.auth.models import Session


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    user_id: UUID
    firm_id: UUID | None
    role: str
    session_id: UUID | None
    capabilities: set[str]
    is_client: bool = False
    mfa_completed: bool = True


async def get_current_principal(
    request: Request,
    authorization: str | None = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db_session),
) -> AuthenticatedPrincipal:
    """Validate Bearer access token, verify session/user status, and construct principal."""
    if not authorization or not authorization.startswith("Bearer "):
        raise DomainError(
            detail="Missing or invalid Authorization header.",
            code="unauthenticated",
            status_code=401,
            title="Unauthenticated",
        )

    token = authorization.split("Bearer ", 1)[1].strip()
    payload = decode_access_token(token)

    user_id = UUID(payload["sub"])
    firm_id = UUID(payload["firm_id"]) if payload.get("firm_id") else None
    role = payload.get("role", "guest")
    session_id = UUID(payload["sid"]) if payload.get("sid") else None
    is_client = payload.get("principal") == "client"
    mfa_completed = payload.get("mfa_completed", True)

    # Check session revocation if session_id is present
    if session_id:
        stmt = select(Session).where(Session.id == session_id, Session.revoked_at.is_(None))
        session_row = (await db.execute(stmt)).scalar_one_or_none()
        if not session_row:
            raise DomainError(
                detail="Session has been revoked or expired.",
                code="unauthenticated",
                status_code=401,
                title="Session revoked",
            )

    capabilities = set(get_capabilities_for_role(role))

    # Bind to request state for access logs & tenancy RLS
    request.state.user_id = user_id
    request.state.firm_id = firm_id
    request.state.role = role

    return AuthenticatedPrincipal(
        user_id=user_id,
        firm_id=firm_id,
        role=role,
        session_id=session_id,
        capabilities=capabilities,
        is_client=is_client,
        mfa_completed=mfa_completed,
    )


def require_capability(capability: str) -> Any:
    """Dependency factory checking that caller has the given capability."""

    async def _checker(
        principal: AuthenticatedPrincipal = Depends(get_current_principal),
    ) -> AuthenticatedPrincipal:
        if capability not in principal.capabilities:
            raise PermissionDeniedError(
                detail="You do not have permission to perform this action.",
                code="capability_missing",
                title="Forbidden",
            )
        return principal

    return _checker


class MatterAccessChecker(Protocol):
    async def __call__(
        self, matter_id: UUID, principal: AuthenticatedPrincipal, db: AsyncSession
    ) -> bool: ...


async def require_matter_access(
    matter_id: UUID,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
) -> UUID:
    """Protocol stub for checking matter access.

    Until P06 (M3 Matters) is built, partners with all_matters_access or firm users pass;
    out-of-scope resources return 404 (D-05).
    """
    if not principal.firm_id:
        raise NotFoundError(detail="Matter not found.")
    return matter_id
