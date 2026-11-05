"""Audit module router: GET /audit/events, GET /audit/verify."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.dependencies import AuthenticatedPrincipal, get_current_principal
from app.core.errors import PermissionDeniedError
from app.core.models import AuditEvent
from app.core.pagination import CursorParams, decode_cursor, encode_cursor
from app.modules.audit.schemas import AuditEventListOut, AuditEventOut, AuditVerifyOut
from app.modules.audit.service import AuditService

router = APIRouter(tags=["audit"])

_DEFAULT_LIMIT = 50


@router.get("/audit/events", response_model=AuditEventListOut)
async def list_audit_events(
    matter_id: UUID | None = Query(None),
    actor_id: UUID | None = Query(None),
    action: str | None = Query(None),
    from_time: datetime | None = Query(None, alias="from"),
    to_time: datetime | None = Query(None, alias="to"),
    cursor: str | None = Query(None),
    limit: int = Query(_DEFAULT_LIMIT, ge=1, le=200),
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
) -> AuditEventListOut:
    """Return a cursor-paginated list of audit events scoped to the caller's firm.

    Scoping rules
    -------------
    - ``audit.view`` → admins/partners see **all** firm events
    - ``audit.view_own`` → others see only events where ``actor_id == caller``
    - Neither capability → 404 (D-05)
    """
    if not principal.firm_id:
        raise PermissionDeniedError()

    has_full = "audit.view" in principal.capabilities
    has_own = "audit.view_own" in principal.capabilities

    if not has_full and not has_own:
        raise PermissionDeniedError()

    stmt = select(AuditEvent).where(AuditEvent.firm_id == principal.firm_id)

    if not has_full:
        # Only own events
        stmt = stmt.where(AuditEvent.actor_id == principal.user_id)
    else:
        # Optional actor_id filter from request
        if actor_id is not None:
            stmt = stmt.where(AuditEvent.actor_id == actor_id)

    if matter_id is not None:
        stmt = stmt.where(AuditEvent.matter_id == matter_id)
    if action is not None:
        stmt = stmt.where(AuditEvent.action == action)
    if from_time is not None:
        stmt = stmt.where(AuditEvent.at >= from_time)
    if to_time is not None:
        stmt = stmt.where(AuditEvent.at <= to_time)

    # Cursor: seq-based (descending)
    if cursor:
        last_seq = int(decode_cursor(cursor))
        stmt = stmt.where(AuditEvent.seq < last_seq)

    stmt = stmt.order_by(AuditEvent.seq.desc()).limit(limit + 1)

    rows = (await db.execute(stmt)).scalars().all()

    has_more = len(rows) > limit
    page = rows[:limit]

    next_cursor: str | None = None
    if has_more and page:
        next_cursor = encode_cursor(str(page[-1].seq))

    items = [
        AuditEventOut(
            seq=e.seq,
            at=e.at,
            actor_id=e.actor_id,
            actor_role=e.actor_role,
            action=e.action,
            resource_type=e.resource_type,
            resource_id=e.resource_id,
            matter_id=e.matter_id,
            ip=e.ip,
            hash=e.hash.hex(),
        )
        for e in page
    ]

    return AuditEventListOut(items=items, next_cursor=next_cursor)


@router.get("/audit/verify", response_model=AuditVerifyOut)
async def verify_audit_chain(
    from_seq: int = Query(1, ge=1),
    to_seq: int | None = Query(None),
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
) -> AuditVerifyOut:
    """Re-derive and verify the hash chain for this firm.

    Only admins and partners (``audit.view``) may call this endpoint.
    """
    if not principal.firm_id or "audit.view" not in principal.capabilities:
        raise PermissionDeniedError()

    svc = AuditService(db)
    result = await svc.verify_chain(principal.firm_id, from_seq=from_seq, to_seq=to_seq)
    return AuditVerifyOut(**result)

