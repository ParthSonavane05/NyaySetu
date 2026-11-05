"""
Business logic for the Matters module (P06).

All DB interactions live here; the router calls service functions only.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import CryptoService
from app.core.exceptions import bad_request, conflict, not_found
from app.core.pagination import decode_cursor
from app.core.validators import normalise_survey_number, parse_area
from app.modules.matters.models import (
    Matter,
    MatterAuditLog,
    MatterMember,
    MatterParcel,
    MatterParty,
    MatterStage,
    MatterStatus,
    PartyRole,
)
from app.modules.matters.schemas import (
    MatterCreate,
    MatterOut,
    MatterPatch,
    MatterTransition,
    MemberAdd,
    ParcelCreate,
    ParcelPatch,
    PartyCreate,
    PartyPatch,
)
from app.modules.matters.transitions import (
    is_backward,
    is_valid_transition,
    transition_error_message,
)

SORT_WHITELIST = ["created_at", "updated_at", "matter_number", "title", "stage", "status"]


# ---------------------------------------------------------------------------
# Audit helper
# ---------------------------------------------------------------------------

async def _audit(
    db: AsyncSession,
    matter_id: uuid.UUID,
    actor_id: uuid.UUID | None,
    action: str,
    payload: dict | None = None,
) -> None:
    log = MatterAuditLog(
        matter_id=matter_id,
        actor_id=actor_id,
        action=action,
        payload=json.dumps(payload) if payload else None,
    )
    db.add(log)


# ---------------------------------------------------------------------------
# Matter number generation (D-08: race-free via advisory lock)
# ---------------------------------------------------------------------------

async def _next_matter_number(db: AsyncSession, firm_id: uuid.UUID) -> str:
    year = datetime.now(timezone.utc).year
    # Advisory lock scoped to (firm_id, year) — prevents duplicate sequences
    lock_key = int(hashlib.md5(f"{firm_id}{year}".encode()).hexdigest()[:8], 16)
    await db.execute(text(f"SELECT pg_advisory_xact_lock({lock_key})"))

    result = await db.execute(
        select(func.count(Matter.id)).where(
            Matter.firm_id == firm_id,
            func.extract("year", Matter.created_at) == year,
        )
    )
    count = (result.scalar() or 0) + 1
    return f"MAT-{year}-{count:04d}"


# ---------------------------------------------------------------------------
# Matter CRUD
# ---------------------------------------------------------------------------

async def list_matters(
    db: AsyncSession,
    firm_id: uuid.UUID,
    user_id: uuid.UUID,
    can_see_all: bool,
    stage: Optional[str] = None,
    status: Optional[str] = None,
    q: Optional[str] = None,
    assigned_user_id: Optional[uuid.UUID] = None,
    forum_id: Optional[uuid.UUID] = None,
    due_before: Optional[datetime] = None,
    sort: str = "created_at",
    limit: int = 20,
    cursor: Optional[str] = None,
) -> list[Matter]:
    stmt = select(Matter).where(
        Matter.firm_id == firm_id,
        Matter.is_archived == False,
    )

    if not can_see_all:
        # Subquery: only matters where user is a member
        member_sub = select(MatterMember.matter_id).where(
            MatterMember.user_id == user_id
        )
        stmt = stmt.where(Matter.id.in_(member_sub))

    if stage:
        stmt = stmt.where(Matter.stage == stage)
    if status:
        stmt = stmt.where(Matter.status == status)
    if assigned_user_id:
        stmt = stmt.where(Matter.assigned_to == assigned_user_id)
    if forum_id:
        stmt = stmt.where(Matter.forum_id == forum_id)
    if q:
        # Trigram similarity — requires pg_trgm extension; fallback to ILIKE
        stmt = stmt.where(Matter.title.ilike(f"%{q}%"))

    # Sort & Cursor pagination (D-12: composite cursor on created_at, id)
    desc = sort.startswith("-")
    field = sort.lstrip("-")
    col = getattr(Matter, field, Matter.created_at)

    if cursor:
        try:
            ts, last_id = decode_cursor(cursor)
            # If sorting by created_at (primary case for cursor pagination)
            if field == "created_at":
                if desc:
                    stmt = stmt.where(
                        (Matter.created_at < ts)
                        | ((Matter.created_at == ts) & (Matter.id < last_id))
                    )
                else:
                    stmt = stmt.where(
                        (Matter.created_at > ts)
                        | ((Matter.created_at == ts) & (Matter.id > last_id))
                    )
        except Exception:
            pass  # Fall back to default ordering if cursor format is corrupt

    stmt = stmt.order_by(col.desc() if desc else col.asc(), Matter.id.desc() if desc else Matter.id.asc())

    stmt = stmt.limit(limit + 1)
    result = await db.execute(stmt)
    rows = list(result.scalars().all())
    return rows


async def create_matter(
    db: AsyncSession,
    firm_id: uuid.UUID,
    actor_id: uuid.UUID,
    payload: MatterCreate,
    idempotency_key: Optional[str] = None,
) -> Matter:
    # Idempotency check
    if idempotency_key:
        existing = await db.execute(
            select(Matter).where(
                Matter.firm_id == firm_id,
                Matter.idempotency_key == idempotency_key,
            )
        )
        found = existing.scalar_one_or_none()
        if found:
            return found  # idempotent — return existing

    matter_number = await _next_matter_number(db, firm_id)
    matter = Matter(
        firm_id=firm_id,
        matter_number=matter_number,
        title=payload.title,
        description=payload.description,
        stage=payload.stage,
        status=payload.status,
        forum_id=payload.forum_id,
        assigned_to=payload.assigned_to,
        idempotency_key=idempotency_key,
    )
    db.add(matter)
    await db.flush()  # get matter.id

    # Auto-add creator as member
    db.add(MatterMember(matter_id=matter.id, user_id=actor_id, role_in_matter="lead"))

    await _audit(db, matter.id, actor_id, "matter.created", {"matter_number": matter_number})
    await db.commit()
    await db.refresh(matter)
    return matter


async def get_matter(db: AsyncSession, matter: Matter) -> MatterOut:
    """Build MatterOut with counts (hearings stubbed as 0 until P07)."""
    member_count = (
        await db.execute(
            select(func.count(MatterMember.id)).where(MatterMember.matter_id == matter.id)
        )
    ).scalar() or 0
    party_count = (
        await db.execute(
            select(func.count(MatterParty.id)).where(MatterParty.matter_id == matter.id)
        )
    ).scalar() or 0
    parcel_count = (
        await db.execute(
            select(func.count(MatterParcel.id)).where(MatterParcel.matter_id == matter.id)
        )
    ).scalar() or 0

    return MatterOut(
        **{c.key: getattr(matter, c.key) for c in matter.__table__.columns},
        member_count=member_count,
        party_count=party_count,
        parcel_count=parcel_count,
        hearing_count=0,       # P07
        next_deadline=None,    # P07
    )


async def patch_matter(
    db: AsyncSession,
    matter: Matter,
    actor_id: uuid.UUID,
    payload: MatterPatch,
) -> Matter:
    if matter.row_version != payload.row_version:
        raise conflict(f"row_version mismatch: expected {matter.row_version}, got {payload.row_version}")

    changes: dict = {}
    for field in ("title", "description", "status", "forum_id", "assigned_to"):
        val = getattr(payload, field)
        if val is not None:
            setattr(matter, field, val)
            changes[field] = str(val)

    matter.row_version += 1
    await _audit(db, matter.id, actor_id, "matter.patched", changes)
    await db.commit()
    await db.refresh(matter)
    return matter


async def transition_matter(
    db: AsyncSession,
    matter: Matter,
    actor_id: uuid.UUID,
    payload: MatterTransition,
) -> Matter:
    if not is_valid_transition(matter.stage, payload.to_stage):
        raise bad_request(transition_error_message(matter.stage, payload.to_stage))

    if is_backward(matter.stage, payload.to_stage) and not payload.note:
        raise bad_request("A note is required for backward stage transitions")

    old_stage = matter.stage
    matter.stage = payload.to_stage
    matter.row_version += 1

    await _audit(db, matter.id, actor_id, "matter.transitioned", {
        "from": old_stage.value,
        "to": payload.to_stage.value,
        "note": payload.note,
    })
    await db.commit()
    await db.refresh(matter)
    return matter


async def archive_matter(
    db: AsyncSession,
    matter: Matter,
    actor_id: uuid.UUID,
) -> Matter:
    matter.stage = MatterStage.ARCHIVED
    matter.status = MatterStatus.ARCHIVED
    matter.is_archived = True
    matter.row_version += 1
    await _audit(db, matter.id, actor_id, "matter.archived", {})
    await db.commit()
    await db.refresh(matter)
    return matter


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------

async def add_member(
    db: AsyncSession,
    matter: Matter,
    actor_id: uuid.UUID,
    payload: MemberAdd,
) -> MatterMember:
    existing = await db.execute(
        select(MatterMember).where(
            MatterMember.matter_id == matter.id,
            MatterMember.user_id == payload.user_id,
        )
    )
    if existing.scalar_one_or_none():
        raise conflict("User is already a member of this matter")

    member = MatterMember(
        matter_id=matter.id,
        user_id=payload.user_id,
        role_in_matter=payload.role_in_matter,
    )
    db.add(member)
    await _audit(db, matter.id, actor_id, "matter.member.added", {"user_id": str(payload.user_id)})
    await db.commit()
    await db.refresh(member)
    return member


async def remove_member(
    db: AsyncSession,
    matter: Matter,
    actor_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    result = await db.execute(
        select(MatterMember).where(
            MatterMember.matter_id == matter.id,
            MatterMember.user_id == user_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise not_found("Member not found")
    await db.delete(member)
    await _audit(db, matter.id, actor_id, "matter.member.removed", {"user_id": str(user_id)})
    await db.commit()


async def list_members(db: AsyncSession, matter_id: uuid.UUID) -> list[MatterMember]:
    result = await db.execute(
        select(MatterMember).where(MatterMember.matter_id == matter_id)
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Parties
# ---------------------------------------------------------------------------

async def create_party(
    db: AsyncSession,
    matter: Matter,
    actor_id: uuid.UUID,
    payload: PartyCreate,
    crypto: CryptoService,
) -> MatterParty:
    party = MatterParty(
        matter_id=matter.id,
        name_enc=crypto.encrypt(payload.name),
        party_role=payload.party_role,
        notes=payload.notes,
    )
    db.add(party)
    await _audit(db, matter.id, actor_id, "matter.party.created", {"role": payload.party_role.value})
    await db.commit()
    await db.refresh(party)
    return party


async def patch_party(
    db: AsyncSession,
    matter: Matter,
    party_id: uuid.UUID,
    actor_id: uuid.UUID,
    payload: PartyPatch,
    crypto: CryptoService,
) -> MatterParty:
    result = await db.execute(
        select(MatterParty).where(
            MatterParty.id == party_id,
            MatterParty.matter_id == matter.id,
        )
    )
    party = result.scalar_one_or_none()
    if not party:
        raise not_found("Party not found")

    if payload.name is not None:
        party.name_enc = crypto.encrypt(payload.name)
    if payload.party_role is not None:
        party.party_role = payload.party_role
    if payload.notes is not None:
        party.notes = payload.notes

    await _audit(db, matter.id, actor_id, "matter.party.patched", {"party_id": str(party_id)})
    await db.commit()
    await db.refresh(party)
    return party


async def delete_party(
    db: AsyncSession,
    matter: Matter,
    party_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> None:
    result = await db.execute(
        select(MatterParty).where(
            MatterParty.id == party_id,
            MatterParty.matter_id == matter.id,
        )
    )
    party = result.scalar_one_or_none()
    if not party:
        raise not_found("Party not found")
    await db.delete(party)
    await _audit(db, matter.id, actor_id, "matter.party.deleted", {"party_id": str(party_id)})
    await db.commit()


async def list_parties(
    db: AsyncSession,
    matter_id: uuid.UUID,
    crypto: CryptoService,
) -> list[dict]:
    result = await db.execute(
        select(MatterParty).where(MatterParty.matter_id == matter_id)
    )
    parties = []
    for p in result.scalars().all():
        parties.append({
            "id": p.id,
            "matter_id": p.matter_id,
            "name": crypto.decrypt(p.name_enc),
            "party_role": p.party_role,
            "notes": p.notes,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
        })
    return parties


# ---------------------------------------------------------------------------
# Parcels
# ---------------------------------------------------------------------------

async def create_parcel(
    db: AsyncSession,
    matter: Matter,
    actor_id: uuid.UUID,
    payload: ParcelCreate,
) -> MatterParcel:
    try:
        survey_number = normalise_survey_number(payload.survey_number_raw)
    except ValueError as e:
        raise bad_request(str(e))

    area_sqm: Decimal | None = None
    area_label: str | None = None
    if payload.area_raw:
        try:
            area_sqm, area_label = parse_area(payload.area_raw)
        except ValueError as e:
            raise bad_request(str(e))

    parcel = MatterParcel(
        matter_id=matter.id,
        survey_number=survey_number,
        survey_number_raw=payload.survey_number_raw,
        village=payload.village,
        taluka=payload.taluka,
        district=payload.district,
        area_sqm=float(area_sqm) if area_sqm is not None else None,
        area_label=area_label,
        notes=payload.notes,
    )
    db.add(parcel)
    await _audit(db, matter.id, actor_id, "matter.parcel.created", {"survey": survey_number})
    await db.commit()
    await db.refresh(parcel)
    return parcel


async def patch_parcel(
    db: AsyncSession,
    matter: Matter,
    parcel_id: uuid.UUID,
    actor_id: uuid.UUID,
    payload: ParcelPatch,
) -> MatterParcel:
    result = await db.execute(
        select(MatterParcel).where(
            MatterParcel.id == parcel_id,
            MatterParcel.matter_id == matter.id,
        )
    )
    parcel = result.scalar_one_or_none()
    if not parcel:
        raise not_found("Parcel not found")

    if payload.survey_number_raw is not None:
        try:
            parcel.survey_number = normalise_survey_number(payload.survey_number_raw)
        except ValueError as e:
            raise bad_request(str(e))
        parcel.survey_number_raw = payload.survey_number_raw

    if payload.area_raw is not None:
        try:
            area_sqm, area_label = parse_area(payload.area_raw)
            parcel.area_sqm = float(area_sqm)
            parcel.area_label = area_label
        except ValueError as e:
            raise bad_request(str(e))

    for field in ("village", "taluka", "district", "notes"):
        val = getattr(payload, field)
        if val is not None:
            setattr(parcel, field, val)

    await _audit(db, matter.id, actor_id, "matter.parcel.patched", {"parcel_id": str(parcel_id)})
    await db.commit()
    await db.refresh(parcel)
    return parcel


async def delete_parcel(
    db: AsyncSession,
    matter: Matter,
    parcel_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> None:
    result = await db.execute(
        select(MatterParcel).where(
            MatterParcel.id == parcel_id,
            MatterParcel.matter_id == matter.id,
        )
    )
    parcel = result.scalar_one_or_none()
    if not parcel:
        raise not_found("Parcel not found")
    await db.delete(parcel)
    await _audit(db, matter.id, actor_id, "matter.parcel.deleted", {"parcel_id": str(parcel_id)})
    await db.commit()


async def list_parcels(db: AsyncSession, matter_id: uuid.UUID) -> list[MatterParcel]:
    result = await db.execute(
        select(MatterParcel).where(MatterParcel.matter_id == matter_id)
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

async def get_dashboard(
    db: AsyncSession,
    firm_id: uuid.UUID,
    user_id: uuid.UUID,
    can_see_all: bool,
) -> dict:
    base_stmt = select(Matter).where(
        Matter.firm_id == firm_id,
        Matter.is_archived == False,
    )
    if not can_see_all:
        member_sub = select(MatterMember.matter_id).where(MatterMember.user_id == user_id)
        base_stmt = base_stmt.where(Matter.id.in_(member_sub))

    # Awaiting review
    review_stmt = base_stmt.where(Matter.stage == MatterStage.REVIEW).limit(10)
    review_result = await db.execute(review_stmt)
    awaiting_review = list(review_result.scalars().all())

    # Recent activity (last 10 audit log entries)
    audit_stmt = (
        select(MatterAuditLog)
        .order_by(MatterAuditLog.created_at.desc())
        .limit(10)
    )
    audit_result = await db.execute(audit_stmt)
    recent = [
        {
            "action": log.action,
            "matter_id": str(log.matter_id),
            "actor_id": str(log.actor_id) if log.actor_id else None,
            "created_at": log.created_at.isoformat(),
        }
        for log in audit_result.scalars().all()
    ]

    return {
        "due_soon": [],           # P07 — hearings/deadlines not built yet
        "awaiting_review": awaiting_review,
        "recent_activity": recent,
    }
