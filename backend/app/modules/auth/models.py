"""Database models for identity, firms, memberships, sessions, and MFA."""

from __future__ import annotations

# Re-export identity models from central schema to maintain backward compatibility
from app.core.models import (
    AdvocateProfile,
    Firm,
    FirmMembership,
    Invitation,
    LoginAttempt,
    MFACredential,
    PasswordResetToken,
    Session,
    User,
)
from app.core.models_base import JSON_TYPE, Base

__all__ = [
    "JSON_TYPE",
    "AdvocateProfile",
    "Base",
    "Firm",
    "FirmMembership",
    "Invitation",
    "LoginAttempt",
    "MFACredential",
    "PasswordResetToken",
    "Session",
    "User",
]
