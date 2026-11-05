"""
FastAPI router for the Matters module (P06).

Base path: /api/v1
Matters: /api/v1/matters
Dashboard: /api/v1/dashboard
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import CryptoService, get_crypto
from app.core.exceptions import bad_request, unprocessable
from app.core.pagination import encode_cursor
from app.core.validators import validate_sort
from app.db.engine import get_db
from app.modules.matters import service
from app.modules.matters.dependencies import CurrentUser, get_current_user, require_matter_access
from app.modules.matters.models import Matter
from app.modules.matters.schemas import (
    DashboardOut,
    MatterCreate,
    MatterListOut,
    MatterOut,
    MatterPatch,
    MatterTransition,
    MemberAdd,
    MemberOut,
    ParcelCreate,
    ParcelOut,
    ParcelPatch,
    PartyCreate,
    PartyOut,
    PartyPatch,
)

router = APIRouter(prefix="/api/v1", tags=["matters"])

SORT_WHITELIST = ["created_at", "updated_at", "matter_number", "title", "stage", "status"]

# ---------------------------------------------------------------------------
# Matters
# ---------------------------------------------------------------------------

@router.get("/matters", response_model=MatterListOut)
async def list_matters(
    stage: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None, description="'me' or a user UUID"),
    forum_id: Optional[uuid.UUID] = Query(None),
    due_before: Optional[datetime] = Query(None),
    sort: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> MatterListOut:
    try:
        validated_sort = validate_sort(sort, SORT_WHITELIST)
    except ValueError as e:
        raise unprocessable(str(e))

    # Parse assigned_to ('me' or specific UUID)
    assigned_user_id: Optional[uuid.UUID] = None
    if assigned_to:
        if assigned_to.lower() == "me":
            assigned_user_id = current_user.user_id
        else:
            try:
                assigned_user_id = uuid.UUID(assigned_to)
            except ValueError:
                raise unprocessable("Invalid assigned_to UUID")

    matters = await service.list_matters(
        db=db,
        firm_id=current_user.firm_id,
        user_id=current_user.user_id,
        can_see_all=current_user.can_see_all_matters,
        stage=stage,
        status=status,
        q=q,
        assigned_user_id=assigned_user_id,
        forum_id=forum_id,
        due_before=due_before,
        sort=validated_sort,
        limit=limit,
        cursor=cursor,
    )
    has_more = len(matters) > limit
    items = matters[:limit]
    out_items = [
        MatterOut(**{c.key: getattr(m, c.key) for c in m.__table__.columns},
                  member_count=0, party_count=0, parcel_count=0,
                  hearing_count=0, next_deadline=None)
        for m in items
    ]
    next_cursor = None
    if has_more and items:
        next_cursor = encode_cursor(items[-1].created_at, items[-1].id)

    return MatterListOut(
        items=out_items,
        next_cursor=next_cursor,
        has_more=has_more,
        total_returned=len(out_items),
    )


@router.post("/matters", response_model=MatterOut, status_code=status.HTTP_201_CREATED)
async def create_matter(
    payload: MatterCreate,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> MatterOut:
    matter = await service.create_matter(
        db=db,
        firm_id=current_user.firm_id,
        actor_id=current_user.user_id,
        payload=payload,
        idempotency_key=idempotency_key,
    )
    return await service.get_matter(db, matter)


@router.get("/matters/{matter_id}", response_model=MatterOut)
async def get_matter(
    matter: Matter = Depends(require_matter_access),
    db: AsyncSession = Depends(get_db),
) -> MatterOut:
    return await service.get_matter(db, matter)


@router.patch("/matters/{matter_id}", response_model=MatterOut)
async def patch_matter(
    payload: MatterPatch,
    matter: Matter = Depends(require_matter_access),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> MatterOut:
    updated = await service.patch_matter(db, matter, current_user.user_id, payload)
    return await service.get_matter(db, updated)


@router.post("/matters/{matter_id}/transition", response_model=MatterOut)
async def transition_matter(
    payload: MatterTransition,
    matter: Matter = Depends(require_matter_access),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> MatterOut:
    updated = await service.transition_matter(db, matter, current_user.user_id, payload)
    return await service.get_matter(db, updated)


@router.post("/matters/{matter_id}/archive", response_model=MatterOut)
async def archive_matter(
    matter: Matter = Depends(require_matter_access),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> MatterOut:
    updated = await service.archive_matter(db, matter, current_user.user_id)
    return await service.get_matter(db, updated)


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------

@router.get("/matters/{matter_id}/members", response_model=List[MemberOut])
async def list_members(
    matter: Matter = Depends(require_matter_access),
    db: AsyncSession = Depends(get_db),
) -> List[MemberOut]:
    return await service.list_members(db, matter.id)


@router.post("/matters/{matter_id}/members", response_model=MemberOut, status_code=201)
async def add_member(
    payload: MemberAdd,
    matter: Matter = Depends(require_matter_access),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> MemberOut:
    return await service.add_member(db, matter, current_user.user_id, payload)


@router.delete("/matters/{matter_id}/members/{user_id}", status_code=204)
async def remove_member(
    user_id: uuid.UUID,
    matter: Matter = Depends(require_matter_access),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    await service.remove_member(db, matter, current_user.user_id, user_id)


# ---------------------------------------------------------------------------
# Parties
# ---------------------------------------------------------------------------

@router.get("/matters/{matter_id}/parties", response_model=List[PartyOut])
async def list_parties(
    matter: Matter = Depends(require_matter_access),
    db: AsyncSession = Depends(get_db),
    crypto: CryptoService = Depends(get_crypto),
) -> List[PartyOut]:
    parties = await service.list_parties(db, matter.id, crypto)
    return [PartyOut(**p) for p in parties]


@router.post("/matters/{matter_id}/parties", response_model=PartyOut, status_code=201)
async def create_party(
    payload: PartyCreate,
    matter: Matter = Depends(require_matter_access),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    crypto: CryptoService = Depends(get_crypto),
) -> PartyOut:
    party = await service.create_party(db, matter, current_user.user_id, payload, crypto)
    return PartyOut(
        id=party.id,
        matter_id=party.matter_id,
        name=crypto.decrypt(party.name_enc),
        party_role=party.party_role,
        notes=party.notes,
        created_at=party.created_at,
        updated_at=party.updated_at,
    )


@router.patch("/matters/{matter_id}/parties/{party_id}", response_model=PartyOut)
async def patch_party(
    party_id: uuid.UUID,
    payload: PartyPatch,
    matter: Matter = Depends(require_matter_access),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    crypto: CryptoService = Depends(get_crypto),
) -> PartyOut:
    party = await service.patch_party(db, matter, party_id, current_user.user_id, payload, crypto)
    return PartyOut(
        id=party.id,
        matter_id=party.matter_id,
        name=crypto.decrypt(party.name_enc),
        party_role=party.party_role,
        notes=party.notes,
        created_at=party.created_at,
        updated_at=party.updated_at,
    )


@router.delete("/matters/{matter_id}/parties/{party_id}", status_code=204)
async def delete_party(
    party_id: uuid.UUID,
    matter: Matter = Depends(require_matter_access),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    await service.delete_party(db, matter, party_id, current_user.user_id)


# ---------------------------------------------------------------------------
# Parcels
# ---------------------------------------------------------------------------

@router.get("/matters/{matter_id}/parcels", response_model=List[ParcelOut])
async def list_parcels(
    matter: Matter = Depends(require_matter_access),
    db: AsyncSession = Depends(get_db),
) -> List[ParcelOut]:
    return await service.list_parcels(db, matter.id)


@router.post("/matters/{matter_id}/parcels", response_model=ParcelOut, status_code=201)
async def create_parcel(
    payload: ParcelCreate,
    matter: Matter = Depends(require_matter_access),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> ParcelOut:
    return await service.create_parcel(db, matter, current_user.user_id, payload)


@router.patch("/matters/{matter_id}/parcels/{parcel_id}", response_model=ParcelOut)
async def patch_parcel(
    parcel_id: uuid.UUID,
    payload: ParcelPatch,
    matter: Matter = Depends(require_matter_access),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> ParcelOut:
    return await service.patch_parcel(db, matter, parcel_id, current_user.user_id, payload)


@router.delete("/matters/{matter_id}/parcels/{parcel_id}", status_code=204)
async def delete_parcel(
    parcel_id: uuid.UUID,
    matter: Matter = Depends(require_matter_access),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    await service.delete_parcel(db, matter, parcel_id, current_user.user_id)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@router.get("/dashboard", response_model=DashboardOut)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> DashboardOut:
    data = await service.get_dashboard(
        db=db,
        firm_id=current_user.firm_id,
        user_id=current_user.user_id,
        can_see_all=current_user.can_see_all_matters,
    )
    awaiting = [
        MatterOut(**{c.key: getattr(m, c.key) for c in m.__table__.columns},
                  member_count=0, party_count=0, parcel_count=0,
                  hearing_count=0, next_deadline=None)
        for m in data["awaiting_review"]
    ]
    return DashboardOut(
        due_soon=[],
        awaiting_review=awaiting,
        recent_activity=data["recent_activity"],
    )
