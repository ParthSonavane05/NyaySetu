"""Pydantic schemas for Auth module."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterFirmIn(BaseModel):
    firm_name: str = Field(min_length=2, max_length=150)
    admin_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class LoginMFARequiredOut(BaseModel):
    mfa_required: bool = True
    challenge_id: str
    message: str = "Please provide 6-digit MFA code."


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes in seconds
    csrf_token: str


class MFAVerifyIn(BaseModel):
    challenge_id: str
    code: str = Field(min_length=6, max_length=10)


class MFAEnrollOut(BaseModel):
    secret: str
    uri: str


class MFAConfirmIn(BaseModel):
    secret: str
    code: str = Field(min_length=6, max_length=6)


class MFAConfirmOut(BaseModel):
    confirmed: bool
    recovery_codes: list[str]


class PasswordForgotIn(BaseModel):
    email: EmailStr


class PasswordResetIn(BaseModel):
    token: str
    new_password: str = Field(min_length=12, max_length=128)


class PasswordChangeIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=12, max_length=128)


class InvitationAcceptIn(BaseModel):
    token: str
    full_name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=12, max_length=128)


class ClientOTPRequestIn(BaseModel):
    mobile: str = Field(min_length=10, max_length=15)


class ClientOTPVerifyIn(BaseModel):
    mobile: str = Field(min_length=10, max_length=15)
    code: str = Field(min_length=6, max_length=6)


class UserOut(BaseModel):
    id: UUID
    email: str
    full_name: str
    locale: str
    mfa_enabled: bool
    status: str


class FirmOut(BaseModel):
    id: UUID
    name: str
    status: str
    role: str


class AuthMeOut(BaseModel):
    user: UserOut
    firms: list[FirmOut]
    current_firm: FirmOut | None
    role: str
    capabilities: list[str]
    locale: str


class SessionOut(BaseModel):
    id: UUID
    family_id: UUID
    device_info: str | None
    ip: str | None
    created_at: datetime
    expires_at: datetime
    is_current: bool = False
