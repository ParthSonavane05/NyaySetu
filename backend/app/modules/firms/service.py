"""Business service for Firm settings, member administration, retention, and advocate profiles."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_crypto import hash_token
from app.core.errors import ConflictError, NotFoundError
from app.modules.audit import actions as A
from app.modules.audit.service import AuditService
from app.core.models import (
    AdvocateProfile,
    Firm,
    FirmMembership,
    Invitation,
    Session,
    User,
)
from app.core.validators import validate_enrolment_no
from app.modules.firms.schemas import (
    AdvocateProfileOut,
    FirmDetailOut,
    FirmInvitationOut,
    FirmUpdateIn,
    FirmUserOut,
    FirmUserUpdateIn,
    RetentionPolicyOut,
    UserProfileOut,
    UserProfileUpdateIn,
)


class FirmService:
    def __init__(self, db: AsyncSession, actor_id: UUID | None = None, actor_role: str | None = None) -> None:
        self.db = db
        self.actor_id = actor_id
        self.actor_role = actor_role

    async def _audit(
        self,
        *,
        firm_id: UUID,
        action: str,
        resource_type: str | None = None,
        resource_id: UUID | None = None,
        metadata: dict | None = None,
    ) -> None:
        """Record audit event inside the current transaction."""
        if not self.actor_id:
            return
        await AuditService(self.db).record(
            firm_id=firm_id,
            actor_id=self.actor_id,
            actor_role=self.actor_role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata,
        )

    # ── Firm Settings (GET/PATCH /firm) ──

    async def get_firm(self, firm_id: UUID) -> FirmDetailOut:
        firm = await self.db.get(Firm, firm_id)
        if not firm or firm.status == "closed":
            raise NotFoundError(detail="Firm not found.")

        return FirmDetailOut(
            id=firm.id,
            name=firm.name,
            status=firm.status,
            region=firm.region,
            kms_key_id=firm.kms_key_id,
            retention_default_days=firm.retention_default_days,
            settings=firm.settings,
            created_at=firm.created_at,
            updated_at=firm.updated_at,
        )

    async def update_firm(self, firm_id: UUID, payload: FirmUpdateIn) -> FirmDetailOut:
        firm = await self.db.get(Firm, firm_id)
        if not firm or firm.status == "closed":
            raise NotFoundError(detail="Firm not found.")

        if payload.name is not None:
            firm.name = payload.name.strip()
        if payload.settings is not None:
            updated_settings = dict(firm.settings)
            updated_settings.update(payload.settings)
            firm.settings = updated_settings

        firm.updated_at = datetime.now(UTC)
        await self.db.flush()
        return await self.get_firm(firm_id)

    # ── Retention Policy (GET/PUT /firm/retention) ──

    async def get_retention_policy(self, firm_id: UUID) -> RetentionPolicyOut:
        firm = await self.db.get(Firm, firm_id)
        if not firm:
            raise NotFoundError(detail="Firm not found.")

        return RetentionPolicyOut(
            firm_id=firm.id,
            retention_default_days=firm.retention_default_days,
        )

    async def set_retention_policy(
        self, firm_id: UUID, retention_default_days: int | None
    ) -> RetentionPolicyOut:
        firm = await self.db.get(Firm, firm_id)
        if not firm:
            raise NotFoundError(detail="Firm not found.")

        firm.retention_default_days = retention_default_days
        firm.updated_at = datetime.now(UTC)
        await self.db.flush()

        return RetentionPolicyOut(
            firm_id=firm.id,
            retention_default_days=firm.retention_default_days,
        )

    # ── User Management (GET /firm/users, PATCH /firm/users/{id}) ──

    async def list_firm_users(self, firm_id: UUID) -> list[FirmUserOut]:
        stmt = (
            select(User, FirmMembership, AdvocateProfile)
            .join(FirmMembership, FirmMembership.user_id == User.id)
            .outerjoin(AdvocateProfile, AdvocateProfile.user_id == User.id)
            .where(FirmMembership.firm_id == firm_id)
            .order_by(FirmMembership.created_at.asc())
        )
        rows = (await self.db.execute(stmt)).all()

        users_out: list[FirmUserOut] = []
        for user, membership, adv_prof in rows:
            users_out.append(
                FirmUserOut(
                    id=user.id,
                    email=user.email,
                    full_name=user.full_name,
                    role=membership.role,
                    all_matters_access=membership.all_matters_access,
                    status=membership.status,
                    locale=user.locale,
                    mfa_enabled=user.mfa_enabled,
                    enrolment_no=adv_prof.enrolment_no if adv_prof else None,
                    advocate_verified=adv_prof.verified_at is not None if adv_prof else False,
                    joined_at=membership.created_at,
                )
            )
        return users_out

    async def update_firm_user(
        self,
        *,
        firm_id: UUID,
        target_user_id: UUID,
        payload: FirmUserUpdateIn,
        acting_user_id: UUID,
    ) -> FirmUserOut:
        # Check target membership in this firm
        stmt = select(FirmMembership).where(
            FirmMembership.firm_id == firm_id,
            FirmMembership.user_id == target_user_id,
        )
        membership = (await self.db.execute(stmt)).scalar_one_or_none()
        if not membership:
            raise NotFoundError(detail="User is not a member of this firm.")

        # Guard: Last admin cannot be demoted or suspended
        if membership.role == "admin" and (
            (payload.role is not None and payload.role != "admin")
            or (payload.status is not None and payload.status != "active")
        ):
            admin_count_stmt = select(func.count(FirmMembership.id)).where(
                FirmMembership.firm_id == firm_id,
                FirmMembership.role == "admin",
                FirmMembership.status == "active",
            )
            admin_count = (await self.db.execute(admin_count_stmt)).scalar() or 0
            if admin_count <= 1:
                raise ConflictError(
                    detail="Cannot demote or suspend the last active administrator for this firm.",
                    code="last_admin_protected",
                )

        if payload.role is not None:
            membership.role = payload.role
        if payload.status is not None:
            membership.status = payload.status
            # When suspending, immediately revoke all active sessions for this user
            if payload.status == "suspended":
                await self.db.execute(
                    update(Session)
                    .where(Session.user_id == target_user_id, Session.firm_id == firm_id)
                    .values(revoked_at=datetime.now(UTC))
                )
        if payload.all_matters_access is not None:
            membership.all_matters_access = payload.all_matters_access

        await self.db.flush()

        # Reload updated user view
        users = await self.list_firm_users(firm_id)
        target = next((u for u in users if u.id == target_user_id), None)
        if not target:
            raise NotFoundError(detail="User not found after update.")
        return target

    # ── Invitations (POST /firm/invitations) ──

    async def create_invitation(self, *, firm_id: UUID, email: str, role: str) -> FirmInvitationOut:
        clean_email = email.lower().strip()

        # Check if already a member of this firm
        existing_member_stmt = (
            select(FirmMembership)
            .join(User, User.id == FirmMembership.user_id)
            .where(FirmMembership.firm_id == firm_id, User.email == clean_email)
        )
        if (await self.db.execute(existing_member_stmt)).scalar_one_or_none():
            raise ConflictError(
                detail="User is already a member of this firm.", code="user_already_member"
            )

        # Invalidate any prior active invitation for this email in this firm
        prior_inv_stmt = select(Invitation).where(
            Invitation.firm_id == firm_id,
            Invitation.email == clean_email,
            Invitation.accepted_at.is_(None),
        )
        prior_invs = (await self.db.execute(prior_inv_stmt)).scalars().all()
        for pi in prior_invs:
            pi.expires_at = datetime.now(UTC)

        raw_token = secrets.token_urlsafe(32)
        token_hash = hash_token(raw_token)
        # 72 hours expiry per requirement
        expires_at = datetime.now(UTC) + timedelta(hours=72)

        invitation = Invitation(
            firm_id=firm_id,
            email=clean_email,
            role=role,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(invitation)
        await self.db.flush()

        invite_url = f"/auth/invitations/accept?token={raw_token}"
        return FirmInvitationOut(
            id=UUID(str(invitation.id)),
            firm_id=UUID(str(firm_id)),
            email=invitation.email,
            role=invitation.role,
            expires_at=invitation.expires_at,
            created_at=invitation.created_at,
            invite_url=invite_url,
        )

    # ── Profile & Advocate Management (GET/PATCH /me/profile) ──

    async def get_user_profile(self, user_id: UUID) -> UserProfileOut:
        user = await self.db.get(User, user_id)
        if not user:
            raise NotFoundError(detail="User not found.")

        adv_stmt = select(AdvocateProfile).where(AdvocateProfile.user_id == user_id)
        adv_prof = (await self.db.execute(adv_stmt)).scalar_one_or_none()

        adv_out: AdvocateProfileOut | None = None
        if adv_prof:
            adv_out = AdvocateProfileOut(
                enrolment_no=adv_prof.enrolment_no,
                state_code=adv_prof.state_code,
                verified_at=adv_prof.verified_at,
                verified_by=adv_prof.verified_by,
                is_verified=adv_prof.verified_at is not None,
            )

        return UserProfileOut(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            locale=user.locale,
            mfa_enabled=user.mfa_enabled,
            status=user.status,
            advocate_profile=adv_out,
        )

    async def update_user_profile(
        self, user_id: UUID, payload: UserProfileUpdateIn
    ) -> UserProfileOut:
        user = await self.db.get(User, user_id)
        if not user:
            raise NotFoundError(detail="User not found.")

        if payload.full_name is not None:
            user.full_name = payload.full_name.strip()
        if payload.locale is not None:
            user.locale = payload.locale

        if payload.advocate_profile is not None:
            state_code, num, yr = validate_enrolment_no(payload.advocate_profile.enrolment_no)
            enrolment_clean = f"{state_code}/{num}/{yr}"

            adv_stmt = select(AdvocateProfile).where(AdvocateProfile.user_id == user_id)
            adv_prof = (await self.db.execute(adv_stmt)).scalar_one_or_none()

            if adv_prof:
                adv_prof.enrolment_no = enrolment_clean
                adv_prof.state_code = state_code
                # Modifying enrolment resets previous manual verification
                adv_prof.verified_at = None
                adv_prof.verified_by = None
            else:
                adv_prof = AdvocateProfile(
                    user_id=user_id,
                    enrolment_no=enrolment_clean,
                    state_code=state_code,
                )
                self.db.add(adv_prof)

        user.updated_at = datetime.now(UTC)
        await self.db.flush()
        return await self.get_user_profile(user_id)

    async def verify_advocate_profile(
        self, *, target_user_id: UUID, admin_user_id: UUID, is_verified: bool
    ) -> AdvocateProfileOut:
        adv_stmt = select(AdvocateProfile).where(AdvocateProfile.user_id == target_user_id)
        adv_prof = (await self.db.execute(adv_stmt)).scalar_one_or_none()
        if not adv_prof:
            raise NotFoundError(detail="Advocate profile not found for user.")

        if is_verified:
            adv_prof.verified_at = datetime.now(UTC)
            adv_prof.verified_by = admin_user_id
        else:
            adv_prof.verified_at = None
            adv_prof.verified_by = None

        await self.db.flush()
        return AdvocateProfileOut(
            enrolment_no=adv_prof.enrolment_no,
            state_code=adv_prof.state_code,
            verified_at=adv_prof.verified_at,
            verified_by=adv_prof.verified_by,
            is_verified=adv_prof.verified_at is not None,
        )
