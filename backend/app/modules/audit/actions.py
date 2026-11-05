"""Canonical audit action name constants.

All modules MUST import and use these constants — never bare string literals.
The convention is <module>.<noun>.<verb>.
"""

from __future__ import annotations

# ── Auth ──────────────────────────────────────────────────────────────────────
AUTH_FIRM_REGISTERED = "auth.firm.registered"
AUTH_LOGIN_SUCCESS = "auth.login.success"
AUTH_LOGIN_FAILURE = "auth.login.failure"
AUTH_LOGOUT = "auth.logout"
AUTH_MFA_ENROLLED = "auth.mfa.enrolled"
AUTH_MFA_VERIFIED = "auth.mfa.verified"
AUTH_MFA_FAILED = "auth.mfa.failed"
AUTH_PASSWORD_RESET_REQUESTED = "auth.password.reset.requested"
AUTH_PASSWORD_RESET = "auth.password.reset"
AUTH_PASSWORD_CHANGED = "auth.password.changed"
AUTH_REFRESH_REUSE = "auth.refresh.reuse"
AUTH_SESSION_REVOKED = "auth.session.revoked"
AUTH_INVITATION_CREATED = "auth.invitation.created"
AUTH_INVITATION_ACCEPTED = "auth.invitation.accepted"

# ── Firm ──────────────────────────────────────────────────────────────────────
FIRM_UPDATED = "firm.updated"
FIRM_USER_ROLE_CHANGED = "firm.user.role_changed"
FIRM_USER_SUSPENDED = "firm.user.suspended"
FIRM_RETENTION_UPDATED = "firm.retention.updated"

# ── User profile ──────────────────────────────────────────────────────────────
USER_PROFILE_UPDATED = "user.profile.updated"
ADVOCATE_VERIFIED = "advocate.verified"

# ── Matters ───────────────────────────────────────────────────────────────────
MATTER_CREATED = "matter.created"
MATTER_UPDATED = "matter.updated"
MATTER_ARCHIVED = "matter.archived"

# ── Documents ─────────────────────────────────────────────────────────────────
DOCUMENT_UPLOADED = "document.uploaded"
DOCUMENT_DOWNLOADED = "document.download"
DOCUMENT_DELETED = "document.deleted"

# ── PII / field ───────────────────────────────────────────────────────────────
PII_REVEALED = "pii.reveal"
FIELD_VERIFIED = "field.verified"

# ── Drafts ────────────────────────────────────────────────────────────────────
DRAFT_CREATED = "draft.created"
DRAFT_SUBMITTED = "draft.submitted"
DRAFT_APPROVED = "draft.approve"
DRAFT_EXPORTED = "draft.exported"

# ── Audit ─────────────────────────────────────────────────────────────────────
AUDIT_VIEWED = "audit.viewed"
AUDIT_CHAIN_VERIFIED = "audit.chain.verified"

