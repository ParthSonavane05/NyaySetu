"""FastAPI router for Firm settings, member administration, and user profiles."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.dependencies import (
    AuthenticatedPrincipal,
    get_current_principal,
    require_capability,
)
from app.core.errors import DomainError
from app.modules.firms.schemas import (
    AdvocateProfileOut,
    AdvocateVerifyIn,
    FirmDetailOut,
    FirmInvitationIn,
    FirmInvitationOut,
    FirmUpdateIn,
    FirmUserOut,
    FirmUserUpdateIn,
    RetentionPolicyIn,
    RetentionPolicyOut,
    UserProfileOut,
    UserProfileUpdateIn,
)
from app.modules.firms.service import FirmService

router = APIRouter(tags=["firms"])


async def get_firm_service(db: AsyncSession = Depends(get_db_session)) -> FirmService:
    return FirmService(db=db)


def _ensure_firm_id(principal: AuthenticatedPrincipal) -> UUID:
    if not principal.firm_id:
        raise DomainError(
            detail="Principal is not associated with an active firm.",
            code="firm_required",
            status_code=400,
        )
    return principal.firm_id


# ── Firm Settings ──


@router.get("/firm", response_model=FirmDetailOut)
async def get_current_firm(
    principal: AuthenticatedPrincipal = Depends(require_capability("firm.manage")),
    firm_service: FirmService = Depends(get_firm_service),
) -> FirmDetailOut:
    """View current firm configuration."""
    firm_id = _ensure_firm_id(principal)
    return await firm_service.get_firm(firm_id)


@router.patch("/firm", response_model=FirmDetailOut)
async def update_current_firm(
    payload: FirmUpdateIn,
    principal: AuthenticatedPrincipal = Depends(require_capability("firm.manage")),
    firm_service: FirmService = Depends(get_firm_service),
) -> FirmDetailOut:
    """Update firm name or firm settings."""
    firm_id = _ensure_firm_id(principal)
    return await firm_service.update_firm(firm_id, payload)


# ── Retention Policy ──


@router.get("/firm/retention", response_model=RetentionPolicyOut)
async def get_firm_retention(
    principal: AuthenticatedPrincipal = Depends(require_capability("firm.manage")),
    firm_service: FirmService = Depends(get_firm_service),
) -> RetentionPolicyOut:
    """View firm retention policy."""
    firm_id = _ensure_firm_id(principal)
    return await firm_service.get_retention_policy(firm_id)


@router.put("/firm/retention", response_model=RetentionPolicyOut)
async def set_firm_retention(
    payload: RetentionPolicyIn,
    principal: AuthenticatedPrincipal = Depends(require_capability("firm.manage")),
    firm_service: FirmService = Depends(get_firm_service),
) -> RetentionPolicyOut:
    """Configure firm retention policy (days or indefinite)."""
    firm_id = _ensure_firm_id(principal)
    return await firm_service.set_retention_policy(firm_id, payload.retention_default_days)


# ── User Administration ──


@router.get("/firm/users", response_model=list[FirmUserOut])
async def list_firm_users(
    principal: AuthenticatedPrincipal = Depends(require_capability("user.view")),
    firm_service: FirmService = Depends(get_firm_service),
) -> list[FirmUserOut]:
    """List all users in the current firm."""
    firm_id = _ensure_firm_id(principal)
    return await firm_service.list_firm_users(firm_id)


@router.post(
    "/firm/invitations", response_model=FirmInvitationOut, status_code=status.HTTP_201_CREATED
)
async def invite_firm_user(
    payload: FirmInvitationIn,
    principal: AuthenticatedPrincipal = Depends(require_capability("user.manage")),
    firm_service: FirmService = Depends(get_firm_service),
) -> FirmInvitationOut:
    """Invite a new user to the firm by email with role."""
    firm_id = _ensure_firm_id(principal)
    return await firm_service.create_invitation(
        firm_id=firm_id,
        email=payload.email,
        role=payload.role,
    )


@router.patch("/firm/users/{user_id}", response_model=FirmUserOut)
async def update_firm_user(
    user_id: UUID,
    payload: FirmUserUpdateIn,
    principal: AuthenticatedPrincipal = Depends(require_capability("user.manage")),
    firm_service: FirmService = Depends(get_firm_service),
) -> FirmUserOut:
    """Update role, status (active/suspended), or all_matters_access.

    Guards: Last admin cannot be demoted or suspended.
    """
    firm_id = _ensure_firm_id(principal)
    return await firm_service.update_firm_user(
        firm_id=firm_id,
        target_user_id=user_id,
        payload=payload,
        acting_user_id=principal.user_id,
    )


@router.post("/firm/users/{user_id}/verify-advocate", response_model=AdvocateProfileOut)
async def verify_advocate(
    user_id: UUID,
    payload: AdvocateVerifyIn,
    principal: AuthenticatedPrincipal = Depends(require_capability("user.manage")),
    firm_service: FirmService = Depends(get_firm_service),
) -> AdvocateProfileOut:
    """Manual admin verification flag for advocate Bar Council enrolment number."""
    return await firm_service.verify_advocate_profile(
        target_user_id=user_id,
        admin_user_id=principal.user_id,
        is_verified=payload.is_verified,
    )


# ── /me/profile ──


@router.get("/me/profile", response_model=UserProfileOut)
async def get_my_profile(
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    firm_service: FirmService = Depends(get_firm_service),
) -> UserProfileOut:
    """Get profile and advocate enrolment details for currently authenticated user."""
    return await firm_service.get_user_profile(principal.user_id)


@router.patch("/me/profile", response_model=UserProfileOut)
async def update_my_profile(
    payload: UserProfileUpdateIn,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    firm_service: FirmService = Depends(get_firm_service),
) -> UserProfileOut:
    """Update user profile (name, locale, Bar Council enrolment)."""
    return await firm_service.update_user_profile(principal.user_id, payload)
