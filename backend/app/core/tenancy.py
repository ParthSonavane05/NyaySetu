"""Multi-tenancy dependency: sets RLS context and provides current-user stub."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session, set_rls_context


@dataclass(frozen=True, slots=True)
class CurrentUser:
    user_id: UUID
    firm_id: UUID
    role: str  # Firm Admin | Partner | Associate | Paralegal | Researcher | Client


async def get_current_user(request: Request) -> CurrentUser:
    """Stub: in production this validates the JWT/session and returns the real user.

    For now, reads from request state (set by tests or dev middleware).
    """
    state = request.state
    return CurrentUser(
        user_id=getattr(state, "user_id", UUID("00000000-0000-0000-0000-000000000000")),
        firm_id=getattr(state, "firm_id", UUID("00000000-0000-0000-0000-000000000000")),
        role=getattr(state, "role", "Associate"),
    )


async def get_tenant_session(
    session: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user),
) -> AsyncSession:
    """Yields a session with RLS variables set for the current tenant."""
    await set_rls_context(session, firm_id=user.firm_id, user_id=user.user_id)
    return session
