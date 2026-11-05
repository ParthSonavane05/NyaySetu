"""Comprehensive SQLAlchemy 2.0 schema for NyaySetu MVP (M1 through M11).

Defines:
- Identity & Tenancy: firms, users, firm_memberships, advocate_profiles, invitations, sessions, mfa_credentials, login_attempts, password_reset_tokens
- Matters: matters, matter_members, parties, matter_parties, matter_stages, forums, statutes, statute_sections, land_parcels
- Documents: documents, document_versions, document_pages, ocr_results, processing_jobs, extracted_fields, extracted_field_versions, pii_findings
- Title Chain: title_events, title_event_links, encumbrances, title_flags, title_reports, matter_notes
- Research: legal_sources, source_passages, citation_aliases, matter_research_items, ingestion_batches
- Drafting: templates, template_versions, drafts, draft_versions, draft_grounds, draft_references, citation_checks, draft_reviews, draft_comments, draft_approvals, exports
- Deadlines & Hearings: limitation_rules, holidays, deadlines, hearings, reminders
- Audit & Privacy: audit_events, audit_anchors, privacy_receipts, ai_runs, notifications, notification_deliveries
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import LargeBinary

from app.core.models_base import (
    JSON_TYPE,
    Base,
    RowVersionMixin,
    SoftDeleteMixin,
    TenantMixin,
    TimestampMixin,
    UUIDv7PrimaryKeyMixin,
)

# ══════════════════════════════════════════════════════════════════════════════
# 1. IDENTITY & TENANCY
# ══════════════════════════════════════════════════════════════════════════════


class Firm(Base, UUIDv7PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "firms"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    region: Mapped[str] = mapped_column(String(50), default="ap-south-1", nullable=False)
    kms_key_id: Mapped[str] = mapped_column(
        String(200), default="alias/nyaysetu-default", nullable=False
    )
    retention_default_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    settings: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, default=dict, nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('active', 'suspended', 'closed')", name="ck_firms_status"),
    )


class User(Base, UUIDv7PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    locale: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("locale IN ('en', 'gu', 'hi')", name="ck_users_locale"),
        CheckConstraint(
            "status IN ('invited', 'active', 'locked', 'disabled')", name="ck_users_status"
        ),
    )


class FirmMembership(Base, UUIDv7PrimaryKeyMixin):
    __tablename__ = "firm_memberships"

    firm_id: Mapped[UUID] = mapped_column(
        ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    all_matters_access: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("firm_id", "user_id", name="uq_firm_user"),
        CheckConstraint(
            "role IN ('admin', 'partner', 'associate', 'paralegal', 'researcher')",
            name="ck_memberships_role",
        ),
        CheckConstraint("status IN ('active', 'suspended')", name="ck_memberships_status"),
    )


class AdvocateProfile(Base, UUIDv7PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "advocate_profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    enrolment_no: Mapped[str] = mapped_column(String(50), nullable=False)
    state_code: Mapped[str] = mapped_column(String(10), default="GJ", nullable=False)
    verified_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Invitation(Base, UUIDv7PrimaryKeyMixin):
    __tablename__ = "invitations"

    firm_id: Mapped[UUID] = mapped_column(
        ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class Session(Base, UUIDv7PrimaryKeyMixin):
    __tablename__ = "sessions"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    firm_id: Mapped[UUID] = mapped_column(
        ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    family_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    device_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class MFACredential(Base, UUIDv7PrimaryKeyMixin):
    __tablename__ = "mfa_credentials"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(20), default="totp", nullable=False)
    secret_enc: Mapped[str] = mapped_column(Text, nullable=False)
    recovery_codes_hash: Mapped[list[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class LoginAttempt(Base, UUIDv7PrimaryKeyMixin):
    __tablename__ = "login_attempts"

    email_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class PasswordResetToken(Base, UUIDv7PrimaryKeyMixin):
    __tablename__ = "password_reset_tokens"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


# ══════════════════════════════════════════════════════════════════════════════
# 2. REFERENCE MASTERS (Global, un-tenant-isolated)
# ══════════════════════════════════════════════════════════════════════════════


class Forum(Base, UUIDv7PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "forums"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    level: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # taluka, subdivision, district, state, tribunal, high_court
    state: Mapped[str] = mapped_column(String(10), default="GJ", nullable=False)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Statute(Base, UUIDv7PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "statutes"

    short_title: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    official_title: Mapped[str] = mapped_column(String(300), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(50), default="Gujarat", nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class StatuteSection(Base, UUIDv7PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "statute_sections"

    statute_id: Mapped[UUID] = mapped_column(
        ForeignKey("statutes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    section_number: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    text_content: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # Placeholder flagged needs_review
    needs_review: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (UniqueConstraint("statute_id", "section_number", name="uq_statute_section"),)


# ══════════════════════════════════════════════════════════════════════════════
# 3. MATTERS, PARTIES, & PARCELS
# ══════════════════════════════════════════════════════════════════════════════


class Party(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "parties"

    type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # individual, company, government, bank
    name_enc: Mapped[str] = mapped_column(Text, nullable=False)
    mobile_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    address_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    name_norm: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True
    )  # Unaccented/trigram for search

    __table_args__ = (
        CheckConstraint(
            "type IN ('individual', 'company', 'government', 'bank', 'other')",
            name="ck_parties_type",
        ),
    )


class Matter(
    Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin, SoftDeleteMixin, RowVersionMixin
):
    __tablename__ = "matters"

    matter_no: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    forum_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("forums.id", ondelete="RESTRICT"), nullable=True
    )
    statute_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("statutes.id", ondelete="RESTRICT"), nullable=True
    )
    stage: Mapped[str] = mapped_column(String(30), default="intake", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "stage IN ('intake', 'ingestion', 'title', 'drafting', 'review', 'filed', 'closed')",
            name="ck_matters_stage",
        ),
        CheckConstraint("status IN ('open', 'archived')", name="ck_matters_status"),
    )


class MatterMember(Base):
    __tablename__ = "matter_members"

    matter_id: Mapped[UUID] = mapped_column(
        ForeignKey("matters.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True
    )
    firm_id: Mapped[UUID] = mapped_column(
        ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    matter_role: Mapped[str] = mapped_column(String(20), default="member", nullable=False)

    __table_args__ = (
        CheckConstraint("matter_role IN ('lead', 'member')", name="ck_matter_members_role"),
    )


class MatterParty(Base, UUIDv7PrimaryKeyMixin, TenantMixin):
    __tablename__ = "matter_parties"

    matter_id: Mapped[UUID] = mapped_column(
        ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    party_id: Mapped[UUID] = mapped_column(
        ForeignKey("parties.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    side: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # our_client, opposite, proforma, third_party

    __table_args__ = (
        UniqueConstraint("matter_id", "party_id", name="uq_matter_party"),
        CheckConstraint(
            "side IN ('our_client', 'opposite', 'proforma', 'third_party')",
            name="ck_matter_parties_side",
        ),
    )


class MatterStage(Base, UUIDv7PrimaryKeyMixin, TenantMixin):
    __tablename__ = "matter_stages"

    matter_id: Mapped[UUID] = mapped_column(
        ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_stage: Mapped[str | None] = mapped_column(String(30), nullable=True)
    to_stage: Mapped[str] = mapped_column(String(30), nullable=False)
    transitioned_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    transitioned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


class LandParcel(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "land_parcels"

    matter_id: Mapped[UUID] = mapped_column(
        ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    village: Mapped[str] = mapped_column(String(100), nullable=False)
    taluka: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    survey_no: Mapped[str] = mapped_column(String(50), nullable=False)
    sub_no: Mapped[str | None] = mapped_column(String(30), nullable=True)
    khata_no: Mapped[str | None] = mapped_column(String(30), nullable=True)
    area_raw: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Format H-A-Sq.m e.g. 1-22-00
    area_sqm: Mapped[int] = mapped_column(Integer, nullable=False)


# ══════════════════════════════════════════════════════════════════════════════
# 4. DOCUMENTS & EXTRACTION
# ══════════════════════════════════════════════════════════════════════════════


class Document(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "documents"

    matter_id: Mapped[UUID] = mapped_column(
        ForeignKey("matters.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    doc_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 7_12, 8a, ferfar, sale_deed, order, other
    source: Mapped[str] = mapped_column(String(50), default="client", nullable=False)
    certified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    current_version_id: Mapped[UUID | None] = mapped_column(nullable=True)


class DocumentVersion(Base, UUIDv7PrimaryKeyMixin, TenantMixin):
    __tablename__ = "document_versions"

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    sha256: Mapped[bytes] = mapped_column(LargeBinary(32), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime: Mapped[str] = mapped_column(String(100), nullable=False)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scan_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    uploaded_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("document_id", "version_no", name="uq_doc_version"),
        CheckConstraint("size_bytes > 0", name="ck_docver_size"),
        CheckConstraint(
            "scan_status IN ('pending', 'clean', 'infected', 'failed')",
            name="ck_docver_scan_status",
        ),
    )


class DocumentPage(Base, UUIDv7PrimaryKeyMixin, TenantMixin):
    __tablename__ = "document_pages"

    version_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    page_no: Mapped[int] = mapped_column(Integer, nullable=False)
    image_key: Mapped[str] = mapped_column(String(500), nullable=False)
    redacted_image_key: Mapped[str | None] = mapped_column(String(500), nullable=True)

    __table_args__ = (UniqueConstraint("version_id", "page_no", name="uq_page_version_num"),)


class OCRResult(Base, UUIDv7PrimaryKeyMixin, TenantMixin):
    __tablename__ = "ocr_results"

    page_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_pages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    engine: Mapped[str] = mapped_column(String(50), nullable=False)
    engine_version: Mapped[str] = mapped_column(String(50), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    boxes: Mapped[list[dict[str, Any]]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    mean_confidence: Mapped[float] = mapped_column(Float, nullable=False)


class ProcessingJob(Base, UUIDv7PrimaryKeyMixin, TenantMixin):
    __tablename__ = "processing_jobs"

    document_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="queued", nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('queued', 'processing', 'completed', 'failed')", name="ck_jobs_status"
        ),
    )


class ExtractedField(Base, UUIDv7PrimaryKeyMixin, TenantMixin, RowVersionMixin):
    __tablename__ = "extracted_fields"

    document_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parcel_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("land_parcels.id", ondelete="SET NULL"), nullable=True, index=True
    )
    field_key: Mapped[str] = mapped_column(String(100), nullable=False)
    value_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_norm: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    page_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("document_pages.id", ondelete="SET NULL"), nullable=True
    )
    bbox: Mapped[dict[str, Any] | None] = mapped_column(JSON_TYPE, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="auto", nullable=False)
    verified_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('auto', 'needs_review', 'verified', 'rejected')",
            name="ck_extracted_field_status",
        ),
    )


class ExtractedFieldVersion(Base, UUIDv7PrimaryKeyMixin, TenantMixin):
    __tablename__ = "extracted_field_versions"

    field_id: Mapped[UUID] = mapped_column(
        ForeignKey("extracted_fields.id", ondelete="CASCADE"), nullable=False, index=True
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)
    changed_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(String(300), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class PIIFinding(Base, UUIDv7PrimaryKeyMixin, TenantMixin):
    __tablename__ = "pii_findings"

    page_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_pages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(50), nullable=False)  # aadhaar, pan, mobile, bank_acc
    bbox: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, nullable=False)
    redacted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


# ══════════════════════════════════════════════════════════════════════════════
# 5. TITLE CHAIN
# ══════════════════════════════════════════════════════════════════════════════


class TitleEvent(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "title_events"

    parcel_id: Mapped[UUID] = mapped_column(
        ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # mutation, sale, partition, mortgage, discharge, order
    entry_no: Mapped[str] = mapped_column(String(50), nullable=False)
    event_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    certification_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    parties: Mapped[list[dict[str, Any]]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    area_sqm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_page_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("document_pages.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'disputed', 'cancelled', 'superseded')",
            name="ck_title_events_status",
        ),
    )


class TitleEventLink(Base):
    __tablename__ = "title_event_links"

    parent_event_id: Mapped[UUID] = mapped_column(
        ForeignKey("title_events.id", ondelete="CASCADE"), primary_key=True
    )
    child_event_id: Mapped[UUID] = mapped_column(
        ForeignKey("title_events.id", ondelete="CASCADE"), primary_key=True
    )


class Encumbrance(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "encumbrances"

    parcel_id: Mapped[UUID] = mapped_column(
        ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # mortgage, attachment, lease, litigation
    holder: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    created_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("title_events.id", ondelete="SET NULL"), nullable=True
    )
    discharged_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("title_events.id", ondelete="SET NULL"), nullable=True
    )


class TitleFlag(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "title_flags"

    parcel_id: Mapped[UUID] = mapped_column(
        ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rule_code: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="warning", nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    event_ids: Mapped[list[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    resolved_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=True
    )
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "severity IN ('info', 'warning', 'critical')", name="ck_title_flags_severity"
        ),
    )


class TitleReport(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "title_reports"

    matter_id: Mapped[UUID] = mapped_column(
        ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parcel_id: Mapped[UUID] = mapped_column(
        ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    signed_off_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=True
    )
    file_key: Mapped[str | None] = mapped_column(String(500), nullable=True)


class MatterNote(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "matter_notes"

    matter_id: Mapped[UUID] = mapped_column(
        ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ref_type: Mapped[str] = mapped_column(String(50), nullable=False)
    ref_id: Mapped[UUID | None] = mapped_column(nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    client_visible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


# ══════════════════════════════════════════════════════════════════════════════
# 6. RESEARCH CORPUS
# ══════════════════════════════════════════════════════════════════════════════


class LegalSource(Base, UUIDv7PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "legal_sources"

    court_id: Mapped[str] = mapped_column(String(100), nullable=False)
    forum_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("forums.id", ondelete="SET NULL"), nullable=True
    )
    citation: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    case_name: Mapped[str] = mapped_column(String(400), nullable=False)
    decided_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    bench: Mapped[str | None] = mapped_column(String(250), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    source_licence: Mapped[str] = mapped_column(
        String(100), default="public_domain", nullable=False
    )
    file_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)


class SourcePassage(Base, UUIDv7PrimaryKeyMixin):
    __tablename__ = "source_passages"

    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("legal_sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    para_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    # On PostgreSQL pgvector uses vector(1024); on generic SQL we fallback to LargeBinary
    embedding: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)


class CitationAlias(Base, UUIDv7PrimaryKeyMixin):
    __tablename__ = "citation_aliases"

    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("legal_sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    alias: Mapped[str] = mapped_column(String(200), nullable=False, index=True)


class MatterResearchItem(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "matter_research_items"

    matter_id: Mapped[UUID] = mapped_column(
        ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("legal_sources.id", ondelete="RESTRICT"), nullable=False
    )
    passage_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("source_passages.id", ondelete="SET NULL"), nullable=True
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    saved_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )


class IngestionBatch(Base, UUIDv7PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ingestion_batches"

    provenance: Mapped[str] = mapped_column(String(200), nullable=False)
    licence: Mapped[str] = mapped_column(String(100), nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    loaded_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )


# ══════════════════════════════════════════════════════════════════════════════
# 7. DRAFTING & CITATIONS
# ══════════════════════════════════════════════════════════════════════════════


class Template(Base, UUIDv7PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "templates"

    firm_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("firms.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # appeal, revision, application, writ
    forum_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("forums.id", ondelete="RESTRICT"), nullable=True
    )
    statute_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("statutes.id", ondelete="RESTRICT"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)


class TemplateVersion(Base, UUIDv7PrimaryKeyMixin):
    __tablename__ = "template_versions"

    template_id: Mapped[UUID] = mapped_column(
        ForeignKey("templates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    body: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    approved_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    __table_args__ = (UniqueConstraint("template_id", "version", name="uq_template_version"),)


class Draft(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "drafts"

    matter_id: Mapped[UUID] = mapped_column(
        ForeignKey("matters.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    template_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("template_versions.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="drafting", nullable=False)
    current_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    lead_author: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('drafting', 'review', 'changes_requested', 'approved')",
            name="ck_drafts_status",
        ),
    )


class DraftVersion(Base, UUIDv7PrimaryKeyMixin, TenantMixin):
    __tablename__ = "draft_versions"

    draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("drafts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    content: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, nullable=False)
    content_hash: Mapped[bytes] = mapped_column(LargeBinary(32), nullable=False)
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    __table_args__ = (UniqueConstraint("draft_id", "version_no", name="uq_draft_version"),)


class DraftGround(Base, UUIDv7PrimaryKeyMixin, TenantMixin):
    __tablename__ = "draft_grounds"

    draft_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("draft_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(
        String(30), default="user", nullable=False
    )  # user, ai, template

    __table_args__ = (UniqueConstraint("draft_version_id", "ordinal", name="uq_ground_ordinal"),)


class DraftReference(Base, UUIDv7PrimaryKeyMixin, TenantMixin):
    __tablename__ = "draft_references"

    draft_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("draft_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ground_ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    ref_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # document, statute, precedent, external
    document_page_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("document_pages.id", ondelete="SET NULL"), nullable=True
    )
    statute_section_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("statute_sections.id", ondelete="SET NULL"), nullable=True
    )
    passage_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("source_passages.id", ondelete="SET NULL"), nullable=True
    )
    bbox: Mapped[dict[str, Any] | None] = mapped_column(JSON_TYPE, nullable=True)
    label: Mapped[str] = mapped_column(String(300), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "ref_type IN ('document', 'statute', 'precedent', 'external')", name="ck_draft_ref_type"
        ),
    )


class CitationCheck(Base, UUIDv7PrimaryKeyMixin, TenantMixin):
    __tablename__ = "citation_checks"

    draft_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("draft_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reference_id: Mapped[UUID] = mapped_column(
        ForeignKey("draft_references.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), default="unverified", nullable=False
    )  # verified, unverified, not_found, external_verified
    matched_source_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("legal_sources.id", ondelete="SET NULL"), nullable=True
    )
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('verified', 'unverified', 'not_found', 'external_verified')",
            name="ck_cite_check_status",
        ),
    )


class DraftReview(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "draft_reviews"

    draft_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("draft_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reviewer_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    state: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # in_review, changes_requested, approved
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)


class DraftComment(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "draft_comments"

    draft_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("draft_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    anchor: Mapped[str] = mapped_column(String(100), nullable=False)
    author_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class DraftApproval(Base, UUIDv7PrimaryKeyMixin, TenantMixin):
    __tablename__ = "draft_approvals"

    draft_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("draft_versions.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    approver_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    approved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    content_hash: Mapped[bytes] = mapped_column(LargeBinary(32), nullable=False)


class Export(Base, UUIDv7PrimaryKeyMixin, TenantMixin):
    __tablename__ = "exports"

    draft_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("draft_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    format: Mapped[str] = mapped_column(String(10), nullable=False)  # docx, pdf
    watermarked: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    file_key: Mapped[str] = mapped_column(String(500), nullable=False)
    exported_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    exported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    __table_args__ = (CheckConstraint("format IN ('docx', 'pdf')", name="ck_exports_format"),)


# ══════════════════════════════════════════════════════════════════════════════
# 8. DEADLINES & HEARINGS
# ══════════════════════════════════════════════════════════════════════════════


class LimitationRule(Base, UUIDv7PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "limitation_rules"

    act: Mapped[str] = mapped_column(String(150), nullable=False)
    section: Mapped[str] = mapped_column(String(50), nullable=False)
    forum_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("forums.id", ondelete="RESTRICT"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    count_from: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # date_of_order, date_of_service
    exclusions: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON_TYPE, default=list, nullable=False
    )
    source_ref: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    reviewed_by: Mapped[str] = mapped_column(String(150), nullable=False)
    reviewed_at: Mapped[date] = mapped_column(Date, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("act", "section", "forum_id", "version", name="uq_limitation_rule"),
        CheckConstraint("days > 0", name="ck_limitation_days"),
    )


class Holiday(Base, UUIDv7PrimaryKeyMixin):
    __tablename__ = "holidays"

    calendar_id: Mapped[str] = mapped_column(String(50), default="GJ_REVENUE", nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    scope: Mapped[str] = mapped_column(String(50), default="state", nullable=False)

    __table_args__ = (UniqueConstraint("calendar_id", "date", name="uq_holiday_calendar_date"),)


class Deadline(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin, RowVersionMixin):
    __tablename__ = "deadlines"

    matter_id: Mapped[UUID] = mapped_column(
        ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rule_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("limitation_rules.id", ondelete="RESTRICT"), nullable=True
    )
    rule_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trigger_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    calculation: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, default=dict, nullable=False)
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('open', 'completed', 'dismissed')", name="ck_deadlines_status"),
    )


class Hearing(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "hearings"

    matter_id: Mapped[UUID] = mapped_column(
        ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    forum_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("forums.id", ondelete="RESTRICT"), nullable=True
    )
    hearing_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    board_item: Mapped[str | None] = mapped_column(String(50), nullable=True)
    stage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(30), default="manual", nullable=False)


class Reminder(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "reminders"

    target_type: Mapped[str] = mapped_column(String(30), nullable=False)  # deadline, hearing
    target_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    channel: Mapped[str] = mapped_column(String(30), default="in_app", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)


# ══════════════════════════════════════════════════════════════════════════════
# 9. AUDIT & PRIVACY
# ══════════════════════════════════════════════════════════════════════════════


class AuditEvent(Base):
    """Tamper-evident, append-only, hash-chained audit log with composite primary key."""

    __tablename__ = "audit_events"

    firm_id: Mapped[UUID] = mapped_column(
        ForeignKey("firms.id", ondelete="RESTRICT"), primary_key=True
    )
    seq: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    actor_id: Mapped[UUID | None] = mapped_column(nullable=True)
    actor_role: Mapped[str | None] = mapped_column(String(50), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[UUID | None] = mapped_column(nullable=True)
    matter_id: Mapped[UUID | None] = mapped_column(nullable=True)
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON_TYPE, default=dict, nullable=False
    )
    prev_hash: Mapped[bytes] = mapped_column(LargeBinary(32), nullable=False)
    hash: Mapped[bytes] = mapped_column(LargeBinary(32), nullable=False)


class AuditAnchor(Base, UUIDv7PrimaryKeyMixin, TenantMixin):
    __tablename__ = "audit_anchors"

    up_to_seq: Mapped[int] = mapped_column(BigInteger, nullable=False)
    hash: Mapped[bytes] = mapped_column(LargeBinary(32), nullable=False)
    anchored_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class PrivacyReceipt(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "privacy_receipts"

    matter_id: Mapped[UUID] = mapped_column(
        ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period: Mapped[str] = mapped_column(String(50), nullable=False)
    file_key: Mapped[str] = mapped_column(String(500), nullable=False)
    audit_anchor_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("audit_anchors.id", ondelete="SET NULL"), nullable=True
    )


class AIRun(Base, UUIDv7PrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "ai_runs"

    task: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    input_refs: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON_TYPE, default=list, nullable=False
    )
    prompt_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    invoked_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )


class Notification(Base, UUIDv7PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "notifications"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, default=dict, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class NotificationDelivery(Base, UUIDv7PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "notification_deliveries"

    notification_id: Mapped[UUID] = mapped_column(
        ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    channel: Mapped[str] = mapped_column(String(30), nullable=False)  # email, sms, whatsapp
    provider_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
