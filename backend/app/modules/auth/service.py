"""Authentication service: login, MFA, sessions, tokens, invitations, client OTP."""

from __future__ import annotations

import json
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from app.core.adapters import AuditServiceStub, get_email_sender, get_sms_sender
from app.core.auth_crypto import (
    ACCESS_TOKEN_LIFETIME,
    MFA_CHALLENGE_LIFETIME,
    REFRESH_TOKEN_LIFETIME,
    create_access_token,
    decrypt_secret,
    encrypt_secret,
    generate_recovery_codes,
    generate_secure_token,
    generate_totp_secret,
    get_totp_uri,
    hash_password,
    hash_token,
    validate_password_policy,
    verify_password,
    verify_totp_code,
)
from app.core.breach_check import BreachedPasswordChecker, MockBreachedPasswordChecker
from app.core.errors import ConflictError, DomainError, NotFoundError, ValidationFailedError
from app.core.permissions import get_capabilities_for_role
from app.modules.auth.models import (
    Firm,
    FirmMembership,
    Invitation,
    MFACredential,
    PasswordResetToken,
    Session,
    User,
)
from app.modules.auth.schemas import (
    AuthMeOut,
    FirmOut,
    SessionOut,
    TokenOut,
    UserOut,
)


class AuthService:
    def __init__(self, db: AsyncSession, redis: Redis | None = None) -> None:  # type: ignore[type-arg]
        self.db = db
        self.redis = redis
        self.breach_checker: BreachedPasswordChecker = MockBreachedPasswordChecker()

    async def _check_rate_limit(self, key: str, max_attempts: int, window_seconds: int) -> None:
        if not self.redis:
            return
        pipe = self.redis.pipeline(transaction=True)
        pipe.incr(key)
        pipe.expire(key, window_seconds, nx=True)
        results = await pipe.execute()
        current: int = results[0]
        if current > max_attempts:
            raise DomainError(
                detail="Too many attempts. Please try again later.",
                code="rate_limited",
                status_code=429,
                title="Rate Limited",
            )

    async def _check_and_update_lockout(self, email: str) -> None:
        """Lockout check: 5 failures / 10 min -> 15 min lockout."""
        if not self.redis:
            return
        lock_key = f"lockout:{email.lower()}"
        is_locked = await self.redis.get(lock_key)
        if is_locked:
            raise DomainError(
                detail="Account temporarily locked due to failed attempts. Please try again later.",
                code="account_locked",
                status_code=423,
                title="Account Locked",
            )

    async def _record_failed_login(self, email: str) -> None:
        if not self.redis:
            return
        fail_key = f"login_fails:{email.lower()}"
        pipe = self.redis.pipeline(transaction=True)
        pipe.incr(fail_key)
        pipe.expire(fail_key, 600, nx=True)  # 10 minutes window
        res = await pipe.execute()
        fails = res[0]
        if fails >= 5:
            # Lock for 15 minutes (900 seconds)
            lock_key = f"lockout:{email.lower()}"
            await self.redis.setex(lock_key, 900, "1")
            await self.redis.delete(fail_key)

    async def _clear_login_fails(self, email: str) -> None:
        if not self.redis:
            return
        await self.redis.delete(f"login_fails:{email.lower()}")

    # ── Register Firm ──

    async def register_firm(
        self,
        *,
        firm_name: str,
        admin_name: str,
        email: str,
        password: str,
        ip: str | None = None,
    ) -> dict[str, Any]:
        policy_errors = validate_password_policy(password, email)
        if policy_errors:
            raise ValidationFailedError(detail=policy_errors[0])

        if await self.breach_checker.is_breached(password):
            raise ValidationFailedError(
                detail="This password appears in known data breaches. Choose a safer one."
            )

        # Check existing user
        stmt = select(User).where(User.email == email.lower().strip())
        existing = (await self.db.execute(stmt)).scalar_one_or_none()
        if existing:
            raise ConflictError(detail="An account with this email already exists.")

        firm = Firm(name=firm_name.strip(), status="active")
        self.db.add(firm)
        await self.db.flush()

        user = User(
            email=email.lower().strip(),
            password_hash=hash_password(password),
            full_name=admin_name.strip(),
            status="active",
            mfa_enabled=False,
        )
        self.db.add(user)
        await self.db.flush()

        membership = FirmMembership(
            firm_id=firm.id,
            user_id=user.id,
            role="admin",
            all_matters_access=True,
            status="active",
        )
        self.db.add(membership)
        await self.db.flush()

        await AuditServiceStub.record(
            firm_id=firm.id,
            actor_id=user.id,
            actor_role="admin",
            action="firm.register",
            resource_type="firm",
            resource_id=firm.id,
            ip=ip,
        )

        return {"firm_id": firm.id, "user_id": user.id, "message": "Firm registered successfully."}

    # ── Login ──

    async def login(
        self,
        *,
        email: str,
        password: str,
        ip: str | None = None,
        device_info: str | None = None,
    ) -> dict[str, Any]:
        clean_email = email.lower().strip()
        await self._check_and_update_lockout(clean_email)

        if ip:
            await self._check_rate_limit(f"rl:login_ip:{ip}", max_attempts=10, window_seconds=60)

        stmt = select(User).where(User.email == clean_email)
        user = (await self.db.execute(stmt)).scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash):
            await self._record_failed_login(clean_email)
            raise DomainError(
                detail="Invalid email or password.",
                code="unauthenticated",
                status_code=401,
                title="Authentication failed",
            )

        if user.status != "active":
            raise DomainError(
                detail="Account is not active.",
                code="unauthenticated",
                status_code=401,
                title="Account disabled",
            )

        await self._clear_login_fails(clean_email)

        # Get primary firm membership
        m_stmt = select(FirmMembership).where(
            FirmMembership.user_id == user.id, FirmMembership.status == "active"
        )
        membership = (await self.db.execute(m_stmt)).scalars().first()
        firm_id = membership.firm_id if membership else None
        role = membership.role if membership else "associate"

        # Mandatory MFA check
        if user.mfa_enabled:
            challenge_id = generate_secure_token(24)
            if self.redis:
                challenge_data = {
                    "user_id": str(user.id),
                    "firm_id": str(firm_id) if firm_id else None,
                    "role": role,
                    "device_info": device_info,
                    "ip": ip,
                }
                await self.redis.setex(
                    f"mfa_challenge:{challenge_id}",
                    int(MFA_CHALLENGE_LIFETIME.total_seconds()),
                    json.dumps(challenge_data),
                )
            return {
                "mfa_required": True,
                "challenge_id": challenge_id,
                "message": "Please provide 6-digit MFA code.",
            }

        # Issue tokens directly if MFA not enabled (for initial enrolment phase)
        tokens, refresh_token = await self._issue_session_tokens(
            user_id=user.id,
            firm_id=firm_id,
            role=role,
            ip=ip,
            device_info=device_info,
            mfa_completed=False,
        )
        return {"mfa_required": False, "tokens": tokens, "refresh_token": refresh_token}

    # ── MFA Verify ──

    async def verify_mfa(
        self,
        *,
        challenge_id: str,
        code: str,
        ip: str | None = None,
    ) -> tuple[TokenOut, str]:
        if not self.redis:
            raise DomainError(
                detail="MFA service currently unavailable.", code="external_service_error"
            )

        raw_data = await self.redis.get(f"mfa_challenge:{challenge_id}")
        if not raw_data:
            raise DomainError(
                detail="MFA challenge expired or invalid.", code="unauthenticated", status_code=401
            )

        data = json.loads(raw_data)
        user_id = UUID(data["user_id"])
        firm_id = UUID(data["firm_id"]) if data.get("firm_id") else None
        role = data.get("role", "associate")
        device_info = data.get("device_info")

        # Rate limit MFA verification per challenge
        await self._check_rate_limit(
            f"rl:mfa_try:{challenge_id}", max_attempts=5, window_seconds=300
        )

        stmt = select(MFACredential).where(MFACredential.user_id == user_id)
        mfa_cred = (await self.db.execute(stmt)).scalar_one_or_none()
        if not mfa_cred or not mfa_cred.confirmed_at:
            raise DomainError(
                detail="MFA is not configured for this user.",
                code="unauthenticated",
                status_code=401,
            )

        secret = decrypt_secret(mfa_cred.secret_enc)
        valid = verify_totp_code(secret, code)

        if not valid:
            # Check recovery codes
            hashed_code = hash_token(code.strip().upper())
            if hashed_code in mfa_cred.recovery_codes_hash:
                mfa_cred.recovery_codes_hash.remove(hashed_code)
                await self.db.flush()
                valid = True

        if not valid:
            raise DomainError(detail="Invalid MFA code.", code="unauthenticated", status_code=401)

        # Consumed challenge
        await self.redis.delete(f"mfa_challenge:{challenge_id}")

        return await self._issue_session_tokens(
            user_id=user_id,
            firm_id=firm_id,
            role=role,
            ip=ip,
            device_info=device_info,
            mfa_completed=True,
        )

    # ── Issue Session Tokens ──

    async def _issue_session_tokens(
        self,
        *,
        user_id: UUID,
        firm_id: UUID | None,
        role: str,
        ip: str | None,
        device_info: str | None,
        family_id: UUID | None = None,
        mfa_completed: bool = True,
    ) -> tuple[TokenOut, str]:
        session_id = uuid7()
        fam_id = family_id or uuid7()
        raw_refresh_token = generate_secure_token(48)
        csrf_token = generate_secure_token(32)

        session = Session(
            id=session_id,
            user_id=user_id,
            firm_id=firm_id or UUID("00000000-0000-0000-0000-000000000000"),
            family_id=fam_id,
            token_hash=hash_token(raw_refresh_token),
            ip=ip,
            device_info=device_info,
            expires_at=datetime.now(UTC) + REFRESH_TOKEN_LIFETIME,
        )
        self.db.add(session)
        await self.db.flush()

        # Cache CSRF token in Redis for session verification
        if self.redis:
            await self.redis.setex(
                f"csrf:{session_id}",
                int(REFRESH_TOKEN_LIFETIME.total_seconds()),
                csrf_token,
            )

        access_token = create_access_token(
            user_id=user_id,
            firm_id=firm_id,
            role=role,
            session_id=session_id,
            mfa_completed=mfa_completed,
        )

        token_out = TokenOut(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(ACCESS_TOKEN_LIFETIME.total_seconds()),
            csrf_token=csrf_token,
        )
        return token_out, raw_refresh_token

    # ── Refresh Token with Rotation & Reuse Detection ──

    async def rotate_refresh_token(
        self,
        *,
        refresh_token: str,
        csrf_header: str | None,
        ip: str | None = None,
    ) -> tuple[TokenOut, str]:
        token_hashed = hash_token(refresh_token)

        stmt = select(Session).where(Session.token_hash == token_hashed)
        session = (await self.db.execute(stmt)).scalar_one_or_none()

        if not session:
            # Possible token reuse attack or invalid token!
            raise DomainError(
                detail="Invalid refresh token.", code="unauthenticated", status_code=401
            )

        # CSRF check
        if self.redis:
            expected_csrf = await self.redis.get(f"csrf:{session.id}")
            if not expected_csrf or expected_csrf != csrf_header:
                raise DomainError(
                    detail="Invalid or missing CSRF token.", code="unauthenticated", status_code=401
                )

        # Check if already revoked -> REUSE DETECTED: revoke entire family!
        if session.revoked_at is not None:
            await self.db.execute(
                update(Session)
                .where(Session.family_id == session.family_id)
                .values(revoked_at=datetime.now(UTC))
            )
            await self.db.flush()

            # Alert user via email adapter
            user = (
                await self.db.execute(select(User).where(User.id == session.user_id))
            ).scalar_one_or_none()
            if user:
                await get_email_sender().send_email(
                    to=user.email,
                    subject="Security Alert: Session terminated",
                    body=(
                        "A previously used session token was submitted. "
                        "All active sessions have been revoked for your safety."
                    ),
                )

            raise DomainError(
                detail="Token reuse detected. All active sessions have been revoked.",
                code="token_reused",
                status_code=401,
                title="Security Alert",
            )

        # Check expiration (ensure both are aware/naive comparable)
        now = datetime.now(UTC)
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at < now:
            raise DomainError(
                detail="Refresh token has expired.", code="token_expired", status_code=401
            )

        # Revoke the used session token
        session.revoked_at = now
        await self.db.flush()

        # Fetch user role
        m_stmt = select(FirmMembership).where(
            FirmMembership.user_id == session.user_id,
            FirmMembership.firm_id == session.firm_id,
            FirmMembership.status == "active",
        )
        membership = (await self.db.execute(m_stmt)).scalar_one_or_none()
        role = membership.role if membership else "associate"

        # Issue new token in the same family
        return await self._issue_session_tokens(
            user_id=session.user_id,
            firm_id=session.firm_id,
            role=role,
            ip=ip,
            device_info=session.device_info,
            family_id=session.family_id,
            mfa_completed=True,
        )

    # ── MFA Enrolment ──

    async def start_mfa_enroll(self, user_id: UUID) -> tuple[str, str]:
        user = (await self.db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not user:
            raise NotFoundError(detail="User not found.")

        secret = generate_totp_secret()
        uri = get_totp_uri(secret, user.email)
        return secret, uri

    async def confirm_mfa_enroll(self, *, user_id: UUID, secret: str, code: str) -> list[str]:
        if not verify_totp_code(secret, code):
            raise ValidationFailedError(detail="Invalid verification code.")

        recovery_codes = generate_recovery_codes()
        recovery_hashes = [hash_token(rc) for rc in recovery_codes]

        stmt = select(MFACredential).where(MFACredential.user_id == user_id)
        existing = (await self.db.execute(stmt)).scalar_one_or_none()

        enc_secret = encrypt_secret(secret)
        now = datetime.now(UTC)

        if existing:
            existing.secret_enc = enc_secret
            existing.recovery_codes_hash = recovery_hashes
            existing.confirmed_at = now
        else:
            cred = MFACredential(
                user_id=user_id,
                secret_enc=enc_secret,
                recovery_codes_hash=recovery_hashes,
                confirmed_at=now,
            )
            self.db.add(cred)

        await self.db.execute(update(User).where(User.id == user_id).values(mfa_enabled=True))
        await self.db.flush()

        return recovery_codes

    # ── Password Reset Flow ──

    async def forgot_password(self, email: str, ip: str | None = None) -> None:
        clean_email = email.lower().strip()
        user = (
            await self.db.execute(select(User).where(User.email == clean_email))
        ).scalar_one_or_none()
        if not user:
            # Generic response to prevent account enumeration
            return

        raw_token = generate_secure_token(32)
        pr_token = PasswordResetToken(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        self.db.add(pr_token)
        await self.db.flush()

        reset_url = f"https://app.nyaysetu.in/auth/reset-password?token={raw_token}"
        await get_email_sender().send_email(
            to=user.email,
            subject="NyaySetu: Password Reset Request",
            body=f"Click the link to reset your password (valid for 1 hour): {reset_url}",
        )

    async def reset_password(self, *, token: str, new_password: str) -> None:
        policy_errors = validate_password_policy(new_password)
        if policy_errors:
            raise ValidationFailedError(detail=policy_errors[0])

        if await self.breach_checker.is_breached(new_password):
            raise ValidationFailedError(
                detail="This password appears in known data breaches. Choose a safer one."
            )

        token_hash = hash_token(token)
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > datetime.now(UTC),
        )
        reset_row = (await self.db.execute(stmt)).scalar_one_or_none()
        if not reset_row:
            raise DomainError(
                detail="Invalid or expired reset token.", code="unauthenticated", status_code=400
            )

        # Single-use: mark token as used
        reset_row.used_at = datetime.now(UTC)

        # Update user password & revoke all active sessions
        await self.db.execute(
            update(User)
            .where(User.id == reset_row.user_id)
            .values(password_hash=hash_password(new_password))
        )
        await self.db.execute(
            update(Session)
            .where(Session.user_id == reset_row.user_id)
            .values(revoked_at=datetime.now(UTC))
        )
        await self.db.flush()

    async def change_password(
        self, *, user_id: UUID, current_password: str, new_password: str
    ) -> None:
        user = (await self.db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not user or not verify_password(current_password, user.password_hash):
            raise DomainError(
                detail="Current password incorrect.", code="unauthenticated", status_code=400
            )

        policy_errors = validate_password_policy(new_password, user.email)
        if policy_errors:
            raise ValidationFailedError(detail=policy_errors[0])

        user.password_hash = hash_password(new_password)
        # Revoke other sessions
        await self.db.execute(
            update(Session).where(Session.user_id == user_id).values(revoked_at=datetime.now(UTC))
        )
        await self.db.flush()

    # ── Accept Invitation ──

    async def accept_invitation(
        self, *, token: str, full_name: str, password: str
    ) -> dict[str, Any]:
        policy_errors = validate_password_policy(password)
        if policy_errors:
            raise ValidationFailedError(detail=policy_errors[0])

        token_hash = hash_token(token)
        stmt = select(Invitation).where(
            Invitation.token_hash == token_hash,
            Invitation.accepted_at.is_(None),
            Invitation.expires_at > datetime.now(UTC),
        )
        invitation = (await self.db.execute(stmt)).scalar_one_or_none()
        if not invitation:
            raise NotFoundError(detail="Invalid or expired invitation.")

        # Check if user already exists
        user_stmt = select(User).where(User.email == invitation.email.lower().strip())
        user = (await self.db.execute(user_stmt)).scalar_one_or_none()

        if not user:
            user = User(
                email=invitation.email.lower().strip(),
                password_hash=hash_password(password),
                full_name=full_name.strip(),
                status="active",
                mfa_enabled=False,
            )
            self.db.add(user)
            await self.db.flush()

        membership = FirmMembership(
            firm_id=invitation.firm_id,
            user_id=user.id,
            role=invitation.role,
            status="active",
        )
        self.db.add(membership)
        invitation.accepted_at = datetime.now(UTC)
        await self.db.flush()

        return {"user_id": user.id, "firm_id": invitation.firm_id, "role": invitation.role}

    # ── Client OTP Login ──

    async def request_client_otp(self, mobile: str) -> None:
        clean_mobile = mobile.strip()
        if not self.redis:
            raise DomainError(detail="OTP service unavailable.", code="external_service_error")

        cooldown_key = f"otp_cooldown:{clean_mobile}"
        if await self.redis.get(cooldown_key):
            raise DomainError(
                detail="Please wait before requesting another OTP.",
                code="rate_limited",
                status_code=429,
            )

        raw_otp = f"{secrets.randbelow(900000) + 100000:06d}"
        otp_hash = hash_token(raw_otp)

        otp_key = f"client_otp:{clean_mobile}"
        # 5 minutes expiry, max 5 attempts
        await self.redis.setex(otp_key, 300, json.dumps({"hash": otp_hash, "attempts": 0}))
        # 60s resend cooldown
        await self.redis.setex(cooldown_key, 60, "1")

        await get_sms_sender().send_sms(
            to=clean_mobile,
            message=f"NyaySetu login OTP: {raw_otp}. Valid for 5 minutes.",
        )

    async def verify_client_otp(self, mobile: str, code: str) -> TokenOut:
        clean_mobile = mobile.strip()
        if not self.redis:
            raise DomainError(detail="OTP service unavailable.", code="external_service_error")

        otp_key = f"client_otp:{clean_mobile}"
        data_raw = await self.redis.get(otp_key)
        if not data_raw:
            raise DomainError(
                detail="OTP expired or not requested.", code="unauthenticated", status_code=401
            )

        otp_data = json.loads(data_raw)
        attempts = otp_data.get("attempts", 0) + 1

        if attempts > 5:
            await self.redis.delete(otp_key)
            raise DomainError(
                detail="Maximum OTP attempts exceeded.", code="unauthenticated", status_code=401
            )

        otp_data["attempts"] = attempts
        await self.redis.setex(otp_key, 300, json.dumps(otp_data))

        if hash_token(code.strip()) != otp_data["hash"]:
            raise DomainError(detail="Invalid OTP code.", code="unauthenticated", status_code=401)

        await self.redis.delete(otp_key)

        client_user_id = uuid7()
        access_token = create_access_token(
            user_id=client_user_id,
            firm_id=None,
            role="client",
            is_client=True,
            mfa_completed=True,
        )
        return TokenOut(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(ACCESS_TOKEN_LIFETIME.total_seconds()),
            csrf_token="",
        )

    # ── Sessions List and Revocation ──

    async def list_sessions(
        self, user_id: UUID, current_session_id: UUID | None
    ) -> list[SessionOut]:
        stmt = (
            select(Session)
            .where(Session.user_id == user_id, Session.revoked_at.is_(None))
            .order_by(Session.created_at.desc())
        )
        rows = (await self.db.execute(stmt)).scalars().all()
        return [
            SessionOut(
                id=s.id,
                family_id=s.family_id,
                device_info=s.device_info,
                ip=s.ip,
                created_at=s.created_at,
                expires_at=s.expires_at,
                is_current=(s.id == current_session_id),
            )
            for s in rows
        ]

    async def revoke_session(self, *, user_id: UUID, session_id: UUID) -> None:
        stmt = select(Session).where(Session.id == session_id, Session.user_id == user_id)
        session = (await self.db.execute(stmt)).scalar_one_or_none()
        if not session:
            raise NotFoundError(detail="Session not found.")
        session.revoked_at = datetime.now(UTC)
        await self.db.flush()

    async def revoke_all_sessions(self, user_id: UUID) -> None:
        await self.db.execute(
            update(Session)
            .where(Session.user_id == user_id, Session.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )
        await self.db.flush()

    # ── /auth/me ──

    async def get_me(self, user_id: UUID, firm_id: UUID | None, role: str) -> AuthMeOut:
        stmt = select(User).where(User.id == user_id)
        user = (await self.db.execute(stmt)).scalar_one_or_none()
        if not user:
            raise NotFoundError(detail="User not found.")

        m_stmt = select(FirmMembership, Firm).join(Firm).where(FirmMembership.user_id == user_id)
        memberships = (await self.db.execute(m_stmt)).all()

        firms_out = [
            FirmOut(id=f.id, name=f.name, status=f.status, role=m.role) for m, f in memberships
        ]

        curr_firm = next((f for f in firms_out if f.id == firm_id), None)
        active_role = curr_firm.role if curr_firm else role

        return AuthMeOut(
            user=UserOut(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                locale=user.locale,
                mfa_enabled=user.mfa_enabled,
                status=user.status,
            ),
            firms=firms_out,
            current_firm=curr_firm,
            role=active_role,
            capabilities=get_capabilities_for_role(active_role),
            locale=user.locale,
        )
