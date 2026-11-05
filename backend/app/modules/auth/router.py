"""FastAPI router for Authentication module (`/auth`)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, Header, Request, Response, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_db_session
from app.core.dependencies import AuthenticatedPrincipal, get_current_principal
from app.modules.auth.schemas import (
    AuthMeOut,
    ClientOTPRequestIn,
    ClientOTPVerifyIn,
    InvitationAcceptIn,
    LoginIn,
    LoginMFARequiredOut,
    MFAConfirmIn,
    MFAConfirmOut,
    MFAEnrollOut,
    MFAVerifyIn,
    PasswordChangeIn,
    PasswordForgotIn,
    PasswordResetIn,
    RegisterFirmIn,
    SessionOut,
    TokenOut,
)
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


async def get_redis() -> Redis:  # type: ignore[type-arg]
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


async def get_auth_service(
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),  # type: ignore[type-arg]
) -> AuthService:
    return AuthService(db=db, redis=redis)


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=7 * 24 * 3600,  # 7 days
        httponly=True,
        secure=not settings.is_local,
        samesite="strict",
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
    )


# ── Register Firm ──


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_firm(
    payload: RegisterFirmIn,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    ip = request.client.host if request.client else None
    res = await auth_service.register_firm(
        firm_name=payload.firm_name,
        admin_name=payload.admin_name,
        email=payload.email,
        password=payload.password,
        ip=ip,
    )
    return {"message": res["message"], "firm_id": str(res["firm_id"])}


# ── Login ──


@router.post("/login", response_model=TokenOut | LoginMFARequiredOut)
async def login(
    payload: LoginIn,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenOut | LoginMFARequiredOut:
    ip = request.client.host if request.client else None
    device_info = request.headers.get("user-agent")
    result = await auth_service.login(
        email=payload.email,
        password=payload.password,
        ip=ip,
        device_info=device_info,
    )
    if result.get("mfa_required"):
        return LoginMFARequiredOut(
            mfa_required=True,
            challenge_id=result["challenge_id"],
            message=result["message"],
        )

    tokens: TokenOut = result["tokens"]
    refresh_token: str = result["refresh_token"]
    _set_refresh_cookie(response, refresh_token)
    return tokens


# ── MFA Verify ──


@router.post("/mfa/verify", response_model=TokenOut)
async def verify_mfa(
    payload: MFAVerifyIn,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenOut:
    ip = request.client.host if request.client else None
    tokens, refresh_token = await auth_service.verify_mfa(
        challenge_id=payload.challenge_id,
        code=payload.code,
        ip=ip,
    )
    _set_refresh_cookie(response, refresh_token)
    return tokens


# ── MFA Enrolment ──


@router.post("/mfa/enroll", response_model=MFAEnrollOut)
async def enroll_mfa(
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    auth_service: AuthService = Depends(get_auth_service),
) -> MFAEnrollOut:
    secret, uri = await auth_service.start_mfa_enroll(principal.user_id)
    return MFAEnrollOut(secret=secret, uri=uri)


@router.post("/mfa/confirm", response_model=MFAConfirmOut)
async def confirm_mfa(
    payload: MFAConfirmIn,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    auth_service: AuthService = Depends(get_auth_service),
) -> MFAConfirmOut:
    recovery_codes = await auth_service.confirm_mfa_enroll(
        user_id=principal.user_id,
        secret=payload.secret,
        code=payload.code,
    )
    return MFAConfirmOut(confirmed=True, recovery_codes=recovery_codes)


# ── Refresh Token ──


@router.post("/refresh", response_model=TokenOut)
async def refresh_token(
    request: Request,
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenOut:
    if not refresh_token:
        from app.core.errors import DomainError

        raise DomainError(
            detail="Missing refresh token cookie.", code="unauthenticated", status_code=401
        )

    ip = request.client.host if request.client else None
    tokens, new_refresh_token = await auth_service.rotate_refresh_token(
        refresh_token=refresh_token,
        csrf_header=x_csrf_token,
        ip=ip,
    )
    _set_refresh_cookie(response, new_refresh_token)
    return tokens


# ── Logout ──


@router.post("/logout")
async def logout(
    response: Response,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    if principal.session_id:
        await auth_service.revoke_session(
            user_id=principal.user_id, session_id=principal.session_id
        )
    _clear_refresh_cookie(response)
    return {"message": "Logged out successfully."}


@router.post("/logout-all")
async def logout_all(
    response: Response,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    await auth_service.revoke_all_sessions(principal.user_id)
    _clear_refresh_cookie(response)
    return {"message": "All sessions revoked."}


# ── Password flows ──


@router.post("/password/forgot")
async def forgot_password(
    payload: PasswordForgotIn,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    ip = request.client.host if request.client else None
    await auth_service.forgot_password(payload.email, ip=ip)
    return {"message": "If this email is registered, password reset instructions have been sent."}


@router.post("/password/reset")
async def reset_password(
    payload: PasswordResetIn,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    await auth_service.reset_password(token=payload.token, new_password=payload.new_password)
    return {"message": "Password reset successfully. Please login with your new password."}


@router.post("/password/change")
async def change_password(
    payload: PasswordChangeIn,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    await auth_service.change_password(
        user_id=principal.user_id,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )
    return {"message": "Password updated successfully."}


# ── Invitations ──


@router.post("/invitations/accept")
async def accept_invitation(
    payload: InvitationAcceptIn,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    await auth_service.accept_invitation(
        token=payload.token,
        full_name=payload.full_name,
        password=payload.password,
    )
    return {"message": "Invitation accepted successfully. You can now login."}


# ── /auth/me ──


@router.get("/me", response_model=AuthMeOut)
async def get_me(
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthMeOut:
    return await auth_service.get_me(
        user_id=principal.user_id,
        firm_id=principal.firm_id,
        role=principal.role,
    )


# ── Sessions ──


@router.get("/sessions", response_model=list[SessionOut])
async def list_sessions(
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    auth_service: AuthService = Depends(get_auth_service),
) -> list[SessionOut]:
    return await auth_service.list_sessions(
        user_id=principal.user_id,
        current_session_id=principal.session_id,
    )


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: UUID,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    await auth_service.revoke_session(user_id=principal.user_id, session_id=session_id)
    return {"message": "Session revoked."}


# ── Client OTP Login ──


@router.post("/client/otp/request")
async def request_client_otp(
    payload: ClientOTPRequestIn,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    await auth_service.request_client_otp(payload.mobile)
    return {"message": "OTP has been sent to your mobile number."}


@router.post("/client/otp/verify", response_model=TokenOut)
async def verify_client_otp(
    payload: ClientOTPVerifyIn,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenOut:
    return await auth_service.verify_client_otp(payload.mobile, payload.code)
