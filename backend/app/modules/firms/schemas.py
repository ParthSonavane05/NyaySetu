"""Pydantic schemas for Firms, Users, Roles, Retention, and Profile management."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ── Firm Schemas ──


class FirmDetailOut(BaseModel):
    id: UUID
    name: str
    status: str
    region: str
    kms_key_id: str
    retention_default_days: int | None = None
    settings: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FirmUpdateIn(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=200)
    settings: dict[str, Any] | None = None


class RetentionPolicyIn(BaseModel):
    retention_default_days: int | None = Field(
        None,
        ge=30,
        le=36500,
        description="Default retention in days (e.g. 2555 days for 7 years). None indicates indefinitely until archive.",
    )


class RetentionPolicyOut(BaseModel):
    firm_id: UUID
    retention_default_days: int | None
    notice: str = "Retention is firm-configurable; legal holds override scheduled retention."


# ── User & Membership Schemas ──


class FirmUserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: str
    all_matters_access: bool
    status: str
    locale: str
    mfa_enabled: bool
    enrolment_no: str | None = None
    advocate_verified: bool = False
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FirmUserUpdateIn(BaseModel):
    role: str | None = Field(None, pattern=r"^(admin|partner|associate|paralegal|researcher)$")
    status: str | None = Field(None, pattern=r"^(active|suspended)$")
    all_matters_access: bool | None = None


# ── Invitations ──


class FirmInvitationIn(BaseModel):
    email: EmailStr
    role: str = Field(..., pattern=r"^(admin|partner|associate|paralegal|researcher)$")


class FirmInvitationOut(BaseModel):
    id: UUID
    firm_id: UUID
    email: EmailStr
    role: str
    expires_at: datetime
    created_at: datetime
    invite_url: str

    model_config = ConfigDict(from_attributes=True)


# ── Advocate Profile & /me/profile ──


class AdvocateProfileIn(BaseModel):
    enrolment_no: str = Field(
        ...,
        description="Bar Council enrolment formatted as <STATE>/<number>/<year> (e.g. 'GJ/1842/2016')",
    )


class AdvocateProfileOut(BaseModel):
    enrolment_no: str
    state_code: str
    verified_at: datetime | None = None
    verified_by: UUID | None = None
    is_verified: bool = False
    notice: str = "Internal advocate record. Does not imply live Bar Council verification."


class UserProfileOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    locale: str
    mfa_enabled: bool
    status: str
    advocate_profile: AdvocateProfileOut | None = None


class UserProfileUpdateIn(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=150)
    locale: str | None = Field(None, pattern=r"^(en|gu|hi)$")
    advocate_profile: AdvocateProfileIn | None = None


class AdvocateVerifyIn(BaseModel):
    is_verified: bool
