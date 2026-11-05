"""MVP schema, indexes, audit trigger, and Row-Level Security (M1-M11).

Revision ID: 4934e7e9f4f6
Revises: d082500b5c79
Create Date: 2026-11-05 11:08:17.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "4934e7e9f4f6"
down_revision: Union[str, None] = "d082500b5c79"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# List of all tenant tables requiring RLS isolation
TENANT_TABLES = [
    "parties",
    "matters",
    "matter_members",
    "matter_parties",
    "matter_stages",
    "land_parcels",
    "documents",
    "document_versions",
    "document_pages",
    "ocr_results",
    "processing_jobs",
    "extracted_fields",
    "extracted_field_versions",
    "pii_findings",
    "title_events",
    "encumbrances",
    "title_flags",
    "title_reports",
    "matter_notes",
    "matter_research_items",
    "drafts",
    "draft_versions",
    "draft_grounds",
    "draft_references",
    "citation_checks",
    "draft_reviews",
    "draft_comments",
    "draft_approvals",
    "exports",
    "deadlines",
    "hearings",
    "reminders",
    "audit_events",
    "audit_anchors",
    "privacy_receipts",
    "ai_runs",
]


def upgrade() -> None:
    # ── Advocate profiles & Login attempts (completing identity) ──
    op.create_table(
        "advocate_profiles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("enrolment_no", sa.String(50), nullable=False),
        sa.Column("state_code", sa.String(10), nullable=False, server_default="GJ"),
        sa.Column("verified_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "login_attempts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email_hash", sa.String(64), nullable=False),
        sa.Column("ip", sa.String(50), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_login_attempts_email_hash", "login_attempts", ["email_hash"])

    # ── 2. Reference Masters (Global) ──
    op.create_table(
        "forums",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("level", sa.String(50), nullable=False),
        sa.Column("state", sa.String(10), nullable=False, server_default="GJ"),
        sa.Column("needs_review", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "statutes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("short_title", sa.String(150), nullable=False, unique=True),
        sa.Column("official_title", sa.String(300), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("jurisdiction", sa.String(50), nullable=False, server_default="Gujarat"),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("needs_review", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "statute_sections",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("statute_id", sa.Uuid(), sa.ForeignKey("statutes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("section_number", sa.String(50), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("text_content", sa.Text(), nullable=False),
        sa.Column("needs_review", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("statute_id", "section_number", name="uq_statute_section"),
    )
    op.create_index("ix_statute_sections_statute_id", "statute_sections", ["statute_id"])

    # ── 3. Matters, Parties & Land Parcels ──
    op.create_table(
        "parties",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("type", sa.String(30), nullable=False),
        sa.Column("name_enc", sa.Text(), nullable=False),
        sa.Column("mobile_enc", sa.Text(), nullable=True),
        sa.Column("address_enc", sa.Text(), nullable=True),
        sa.Column("name_norm", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True),
        sa.CheckConstraint("type IN ('individual', 'company', 'government', 'bank', 'other')", name="ck_parties_type"),
    )
    op.create_index("ix_parties_firm_id", "parties", ["firm_id"])
    op.create_index("ix_parties_name_norm", "parties", ["name_norm"])

    op.create_table(
        "matters",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("matter_no", sa.String(50), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("forum_id", sa.Uuid(), sa.ForeignKey("forums.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("statute_id", sa.Uuid(), sa.ForeignKey("statutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("stage", sa.String(30), nullable=False, server_default="intake"),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("row_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True),
        sa.CheckConstraint("stage IN ('intake', 'ingestion', 'title', 'drafting', 'review', 'filed', 'closed')", name="ck_matters_stage"),
        sa.CheckConstraint("status IN ('open', 'archived')", name="ck_matters_status"),
    )
    op.create_index("ix_matters_firm_id", "matters", ["firm_id"])
    op.create_index("matters_firm_stage_idx", "matters", ["firm_id", "stage", "status"])
    op.create_index("matters_firm_created_idx", "matters", ["firm_id", sa.text("created_at DESC")])
    op.create_index(
        "matters_no_uq",
        "matters",
        ["firm_id", "matter_no"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "matter_members",
        sa.Column("matter_id", sa.Uuid(), sa.ForeignKey("matters.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("matter_role", sa.String(20), nullable=False, server_default="member"),
        sa.CheckConstraint("matter_role IN ('lead', 'member')", name="ck_matter_members_role"),
    )
    op.create_index("ix_matter_members_user_id", "matter_members", ["user_id"])
    op.create_index("ix_matter_members_firm_id", "matter_members", ["firm_id"])

    op.create_table(
        "matter_parties",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("matter_id", sa.Uuid(), sa.ForeignKey("matters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("party_id", sa.Uuid(), sa.ForeignKey("parties.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("side", sa.String(30), nullable=False),
        sa.UniqueConstraint("matter_id", "party_id", name="uq_matter_party"),
        sa.CheckConstraint("side IN ('our_client', 'opposite', 'proforma', 'third_party')", name="ck_matter_parties_side"),
    )
    op.create_index("ix_matter_parties_firm_id", "matter_parties", ["firm_id"])

    op.create_table(
        "matter_stages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("matter_id", sa.Uuid(), sa.ForeignKey("matters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_stage", sa.String(30), nullable=True),
        sa.Column("to_stage", sa.String(30), nullable=False),
        sa.Column("transitioned_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("transitioned_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("note", sa.Text(), nullable=True),
    )
    op.create_index("ix_matter_stages_firm_id", "matter_stages", ["firm_id"])

    op.create_table(
        "land_parcels",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("matter_id", sa.Uuid(), sa.ForeignKey("matters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("village", sa.String(100), nullable=False),
        sa.Column("taluka", sa.String(100), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("survey_no", sa.String(50), nullable=False),
        sa.Column("sub_no", sa.String(30), nullable=True),
        sa.Column("khata_no", sa.String(30), nullable=True),
        sa.Column("area_raw", sa.String(50), nullable=False),
        sa.Column("area_sqm", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True),
    )
    op.create_index("ix_land_parcels_firm_id", "land_parcels", ["firm_id"])
    op.create_index("ix_land_parcels_matter_id", "land_parcels", ["matter_id"])

    # ── 4. Documents & Extraction ──
    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("matter_id", sa.Uuid(), sa.ForeignKey("matters.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("doc_type", sa.String(50), nullable=False),
        sa.Column("source", sa.String(50), nullable=False, server_default="client"),
        sa.Column("certified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("current_version_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True),
    )
    op.create_index("ix_documents_firm_id", "documents", ["firm_id"])
    op.create_index("ix_documents_matter_id", "documents", ["matter_id"])

    op.create_table(
        "document_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("document_id", sa.Uuid(), sa.ForeignKey("documents.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("sha256", sa.LargeBinary(32), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("mime", sa.String(100), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("scan_status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("uploaded_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("document_id", "version_no", name="uq_doc_version"),
        sa.CheckConstraint("size_bytes > 0", name="ck_docver_size"),
        sa.CheckConstraint("scan_status IN ('pending', 'clean', 'infected', 'failed')", name="ck_docver_scan_status"),
    )
    op.create_index("ix_document_versions_firm_id", "document_versions", ["firm_id"])
    op.create_index("docver_sha_idx", "document_versions", ["firm_id", "sha256"])

    op.create_table(
        "document_pages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("version_id", sa.Uuid(), sa.ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("page_no", sa.Integer(), nullable=False),
        sa.Column("image_key", sa.String(500), nullable=False),
        sa.Column("redacted_image_key", sa.String(500), nullable=True),
        sa.UniqueConstraint("version_id", "page_no", name="uq_page_version_num"),
    )
    op.create_index("ix_document_pages_firm_id", "document_pages", ["firm_id"])

    op.create_table(
        "ocr_results",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("page_id", sa.Uuid(), sa.ForeignKey("document_pages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("engine", sa.String(50), nullable=False),
        sa.Column("engine_version", sa.String(50), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("boxes", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("mean_confidence", sa.Float(), nullable=False),
    )
    op.create_index("ix_ocr_results_firm_id", "ocr_results", ["firm_id"])

    op.create_table(
        "processing_jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("document_version_id", sa.Uuid(), sa.ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step", sa.String(50), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="queued"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_code", sa.String(100), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('queued', 'processing', 'completed', 'failed')", name="ck_jobs_status"),
    )
    op.create_index("ix_processing_jobs_firm_id", "processing_jobs", ["firm_id"])

    op.create_table(
        "extracted_fields",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("document_version_id", sa.Uuid(), sa.ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parcel_id", sa.Uuid(), sa.ForeignKey("land_parcels.id", ondelete="SET NULL"), nullable=True),
        sa.Column("field_key", sa.String(100), nullable=False),
        sa.Column("value_raw", sa.Text(), nullable=True),
        sa.Column("value_norm", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Numeric(4, 3), nullable=True),
        sa.Column("page_id", sa.Uuid(), sa.ForeignKey("document_pages.id", ondelete="SET NULL"), nullable=True),
        sa.Column("bbox", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="auto"),
        sa.Column("verified_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("row_version", sa.Integer(), nullable=False, server_default="1"),
        sa.CheckConstraint("status IN ('auto', 'needs_review', 'verified', 'rejected')", name="ck_extracted_field_status"),
    )
    op.create_index("ix_extracted_fields_firm_id", "extracted_fields", ["firm_id"])
    op.create_index(
        "fields_review_idx",
        "extracted_fields",
        ["firm_id", "status"],
        postgresql_where=sa.text("status = 'needs_review'"),
    )

    op.create_table(
        "extracted_field_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("field_id", sa.Uuid(), sa.ForeignKey("extracted_fields.id", ondelete="CASCADE"), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("changed_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("reason", sa.String(300), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_extracted_field_versions_firm_id", "extracted_field_versions", ["firm_id"])

    op.create_table(
        "pii_findings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("page_id", sa.Uuid(), sa.ForeignKey("document_pages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(50), nullable=False),
        sa.Column("bbox", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("redacted", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_pii_findings_firm_id", "pii_findings", ["firm_id"])

    # ── 5. Title Chain ──
    op.create_table(
        "title_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("parcel_id", sa.Uuid(), sa.ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("entry_no", sa.String(50), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=True),
        sa.Column("certification_date", sa.Date(), nullable=True),
        sa.Column("parties", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("area_sqm", sa.Integer(), nullable=True),
        sa.Column("source_page_id", sa.Uuid(), sa.ForeignKey("document_pages.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('active', 'disputed', 'cancelled', 'superseded')", name="ck_title_events_status"),
    )
    op.create_index("ix_title_events_firm_id", "title_events", ["firm_id"])
    op.create_index("ix_title_events_parcel_id", "title_events", ["parcel_id"])

    op.create_table(
        "title_event_links",
        sa.Column("parent_event_id", sa.Uuid(), sa.ForeignKey("title_events.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("child_event_id", sa.Uuid(), sa.ForeignKey("title_events.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "encumbrances",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("parcel_id", sa.Uuid(), sa.ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(50), nullable=False),
        sa.Column("holder", sa.String(200), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("created_event_id", sa.Uuid(), sa.ForeignKey("title_events.id", ondelete="SET NULL"), nullable=True),
        sa.Column("discharged_event_id", sa.Uuid(), sa.ForeignKey("title_events.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_encumbrances_firm_id", "encumbrances", ["firm_id"])

    op.create_table(
        "title_flags",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("parcel_id", sa.Uuid(), sa.ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rule_code", sa.String(100), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="warning"),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("event_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("resolved_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("resolution_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("severity IN ('info', 'warning', 'critical')", name="ck_title_flags_severity"),
    )
    op.create_index("ix_title_flags_firm_id", "title_flags", ["firm_id"])

    op.create_table(
        "title_reports",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("matter_id", sa.Uuid(), sa.ForeignKey("matters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parcel_id", sa.Uuid(), sa.ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("signed_off_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("file_key", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_title_reports_firm_id", "title_reports", ["firm_id"])

    op.create_table(
        "matter_notes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("matter_id", sa.Uuid(), sa.ForeignKey("matters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ref_type", sa.String(50), nullable=False),
        sa.Column("ref_id", sa.Uuid(), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("client_visible", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_matter_notes_firm_id", "matter_notes", ["firm_id"])

    # ── 6. Research Corpus ──
    op.create_table(
        "legal_sources",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("court_id", sa.String(100), nullable=False),
        sa.Column("forum_id", sa.Uuid(), sa.ForeignKey("forums.id", ondelete="SET NULL"), nullable=True),
        sa.Column("citation", sa.String(200), nullable=False, unique=True),
        sa.Column("case_name", sa.String(400), nullable=False),
        sa.Column("decided_on", sa.Date(), nullable=True),
        sa.Column("bench", sa.String(250), nullable=True),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("source_licence", sa.String(100), nullable=False, server_default="public_domain"),
        sa.Column("file_key", sa.String(500), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Postgres tsvector & pgvector column on source_passages
    op.execute("""
    CREATE TABLE source_passages (
        id uuid PRIMARY KEY,
        source_id uuid NOT NULL REFERENCES legal_sources(id) ON DELETE CASCADE,
        para_no int,
        language varchar(10) NOT NULL DEFAULT 'en',
        text text NOT NULL,
        tsv tsvector GENERATED ALWAYS AS (to_tsvector('simple', text)) STORED,
        embedding vector(1024)
    );
    """)
    op.create_index("ix_source_passages_source_id", "source_passages", ["source_id"])
    op.execute("CREATE INDEX passages_tsv_idx ON source_passages USING gin (tsv);")
    op.execute("CREATE INDEX passages_trgm_idx ON source_passages USING gin (text gin_trgm_ops);")
    op.execute("CREATE INDEX passages_vec_idx ON source_passages USING hnsw (embedding vector_cosine_ops);")

    op.create_table(
        "citation_aliases",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("legal_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alias", sa.String(200), nullable=False),
    )
    op.create_index("ix_citation_aliases_alias", "citation_aliases", ["alias"])

    op.create_table(
        "matter_research_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("matter_id", sa.Uuid(), sa.ForeignKey("matters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("legal_sources.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("passage_id", sa.Uuid(), sa.ForeignKey("source_passages.id", ondelete="SET NULL"), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("saved_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_matter_research_items_firm_id", "matter_research_items", ["firm_id"])

    op.create_table(
        "ingestion_batches",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("provenance", sa.String(200), nullable=False),
        sa.Column("licence", sa.String(100), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("loaded_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── 7. Drafting & Citations ──
    op.create_table(
        "templates",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("forum_id", sa.Uuid(), sa.ForeignKey("forums.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("statute_id", sa.Uuid(), sa.ForeignKey("statutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True),
    )
    op.create_index("ix_templates_firm_id", "templates", ["firm_id"])

    op.create_table(
        "template_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("template_id", sa.Uuid(), sa.ForeignKey("templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("body", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("approved_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("template_id", "version", name="uq_template_version"),
    )

    op.create_table(
        "drafts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("matter_id", sa.Uuid(), sa.ForeignKey("matters.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("template_version_id", sa.Uuid(), sa.ForeignKey("template_versions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="drafting"),
        sa.Column("current_version_id", sa.Uuid(), nullable=True),
        sa.Column("lead_author", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True),
        sa.CheckConstraint("status IN ('drafting', 'review', 'changes_requested', 'approved')", name="ck_drafts_status"),
    )
    op.create_index("ix_drafts_firm_id", "drafts", ["firm_id"])

    op.create_table(
        "draft_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("draft_id", sa.Uuid(), sa.ForeignKey("drafts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("content_hash", sa.LargeBinary(32), nullable=False),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("draft_id", "version_no", name="uq_draft_version"),
    )
    op.create_index("ix_draft_versions_firm_id", "draft_versions", ["firm_id"])

    op.create_table(
        "draft_grounds",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("draft_version_id", sa.Uuid(), sa.ForeignKey("draft_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("source", sa.String(30), nullable=False, server_default="user"),
        sa.UniqueConstraint("draft_version_id", "ordinal", name="uq_ground_ordinal"),
    )
    op.create_index("ix_draft_grounds_firm_id", "draft_grounds", ["firm_id"])

    op.create_table(
        "draft_references",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("draft_version_id", sa.Uuid(), sa.ForeignKey("draft_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ground_ordinal", sa.Integer(), nullable=False),
        sa.Column("ref_type", sa.String(30), nullable=False),
        sa.Column("document_page_id", sa.Uuid(), sa.ForeignKey("document_pages.id", ondelete="SET NULL"), nullable=True),
        sa.Column("statute_section_id", sa.Uuid(), sa.ForeignKey("statute_sections.id", ondelete="SET NULL"), nullable=True),
        sa.Column("passage_id", sa.Uuid(), sa.ForeignKey("source_passages.id", ondelete="SET NULL"), nullable=True),
        sa.Column("bbox", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("label", sa.String(300), nullable=False),
        sa.CheckConstraint("ref_type IN ('document', 'statute', 'precedent', 'external')", name="ck_draft_ref_type"),
    )
    op.create_index("ix_draft_references_firm_id", "draft_references", ["firm_id"])

    op.create_table(
        "citation_checks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("draft_version_id", sa.Uuid(), sa.ForeignKey("draft_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reference_id", sa.Uuid(), sa.ForeignKey("draft_references.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="unverified"),
        sa.Column("matched_source_id", sa.Uuid(), sa.ForeignKey("legal_sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('verified', 'unverified', 'not_found', 'external_verified')", name="ck_cite_check_status"),
    )
    op.create_index("ix_citation_checks_firm_id", "citation_checks", ["firm_id"])

    op.create_table(
        "draft_reviews",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("draft_version_id", sa.Uuid(), sa.ForeignKey("draft_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("state", sa.String(30), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_draft_reviews_firm_id", "draft_reviews", ["firm_id"])

    op.create_table(
        "draft_comments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("draft_version_id", sa.Uuid(), sa.ForeignKey("draft_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("anchor", sa.String(100), nullable=False),
        sa.Column("author_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_draft_comments_firm_id", "draft_comments", ["firm_id"])

    op.create_table(
        "draft_approvals",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("draft_version_id", sa.Uuid(), sa.ForeignKey("draft_versions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("approver_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("content_hash", sa.LargeBinary(32), nullable=False),
    )
    op.create_index("ix_draft_approvals_firm_id", "draft_approvals", ["firm_id"])

    op.create_table(
        "exports",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("draft_version_id", sa.Uuid(), sa.ForeignKey("draft_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("format", sa.String(10), nullable=False),
        sa.Column("watermarked", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("file_key", sa.String(500), nullable=False),
        sa.Column("exported_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("exported_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("format IN ('docx', 'pdf')", name="ck_exports_format"),
    )
    op.create_index("ix_exports_firm_id", "exports", ["firm_id"])

    # ── 8. Deadlines & Hearings ──
    op.create_table(
        "limitation_rules",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("act", sa.String(150), nullable=False),
        sa.Column("section", sa.String(50), nullable=False),
        sa.Column("forum_id", sa.Uuid(), sa.ForeignKey("forums.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("title", sa.String(250), nullable=False),
        sa.Column("days", sa.Integer(), nullable=False),
        sa.Column("count_from", sa.String(50), nullable=False),
        sa.Column("exclusions", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("source_ref", sa.String(200), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("reviewed_by", sa.String(150), nullable=False),
        sa.Column("reviewed_at", sa.Date(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("needs_review", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("act", "section", "forum_id", "version", name="uq_limitation_rule"),
        sa.CheckConstraint("days > 0", name="ck_limitation_days"),
    )

    op.create_table(
        "holidays",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("calendar_id", sa.String(50), nullable=False, server_default="GJ_REVENUE"),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("scope", sa.String(50), nullable=False, server_default="state"),
        sa.UniqueConstraint("calendar_id", "date", name="uq_holiday_calendar_date"),
    )

    op.create_table(
        "deadlines",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("matter_id", sa.Uuid(), sa.ForeignKey("matters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rule_id", sa.Uuid(), sa.ForeignKey("limitation_rules.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("rule_version", sa.Integer(), nullable=True),
        sa.Column("trigger_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("calculation", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("owner_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("row_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('open', 'completed', 'dismissed')", name="ck_deadlines_status"),
    )
    op.create_index("ix_deadlines_firm_id", "deadlines", ["firm_id"])
    op.create_index(
        "deadlines_open_idx",
        "deadlines",
        ["firm_id", "due_date"],
        postgresql_where=sa.text("status = 'open'"),
    )

    op.create_table(
        "hearings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("matter_id", sa.Uuid(), sa.ForeignKey("matters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("forum_id", sa.Uuid(), sa.ForeignKey("forums.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("hearing_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("board_item", sa.String(50), nullable=True),
        sa.Column("stage", sa.String(100), nullable=True),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column("source", sa.String(30), nullable=False, server_default="manual"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_hearings_firm_id", "hearings", ["firm_id"])
    op.create_index("hearings_calendar_idx", "hearings", ["firm_id", "hearing_at"])

    op.create_table(
        "reminders",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("target_type", sa.String(30), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.Column("remind_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("channel", sa.String(30), nullable=False, server_default="in_app"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_reminders_firm_id", "reminders", ["firm_id"])

    # ── 9. Audit & Privacy ──
    op.create_table(
        "audit_events",
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("seq", sa.BigInteger(), nullable=False),
        sa.Column("at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("actor_role", sa.String(50), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column("resource_id", sa.Uuid(), nullable=True),
        sa.Column("matter_id", sa.Uuid(), nullable=True),
        sa.Column("ip", sa.String(50), nullable=True),
        sa.Column("user_agent", sa.String(255), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("prev_hash", sa.LargeBinary(32), nullable=False),
        sa.Column("hash", sa.LargeBinary(32), nullable=False),
        sa.PrimaryKeyConstraint("firm_id", "seq"),
    )
    op.create_index("audit_matter_idx", "audit_events", ["firm_id", "matter_id", sa.text("at DESC")])
    op.create_index("audit_actor_idx", "audit_events", ["firm_id", "actor_id", sa.text("at DESC")])

    # Immutable append-only audit trigger preventing UPDATE and DELETE
    op.execute("""
    CREATE OR REPLACE FUNCTION audit_events_prevent_tamper()
    RETURNS TRIGGER AS $$
    BEGIN
        RAISE EXCEPTION 'audit_events is append-only: updates and deletes are prohibited';
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER trg_audit_events_immutable
    BEFORE UPDATE OR DELETE ON audit_events
    FOR EACH ROW EXECUTE FUNCTION audit_events_prevent_tamper();
    """)

    op.create_table(
        "audit_anchors",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("up_to_seq", sa.BigInteger(), nullable=False),
        sa.Column("hash", sa.LargeBinary(32), nullable=False),
        sa.Column("anchored_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_anchors_firm_id", "audit_anchors", ["firm_id"])

    op.create_table(
        "privacy_receipts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("matter_id", sa.Uuid(), sa.ForeignKey("matters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("period", sa.String(50), nullable=False),
        sa.Column("file_key", sa.String(500), nullable=False),
        sa.Column("audit_anchor_id", sa.Uuid(), sa.ForeignKey("audit_anchors.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_privacy_receipts_firm_id", "privacy_receipts", ["firm_id"])

    op.create_table(
        "ai_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("firm_id", sa.Uuid(), sa.ForeignKey("firms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("task", sa.String(50), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("model_version", sa.String(50), nullable=False),
        sa.Column("input_refs", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("prompt_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("tokens", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("invoked_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_runs_firm_id", "ai_runs", ["firm_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(50), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index(
        "notifications_user_unread_idx",
        "notifications",
        ["user_id", sa.text("read_at NULLS FIRST"), sa.text("created_at DESC")],
    )

    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("notification_id", sa.Uuid(), sa.ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.String(30), nullable=False),
        sa.Column("provider_id", sa.String(100), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_notification_deliveries_notification_id", "notification_deliveries", ["notification_id"])

    # ── 10. Enable and Force Row-Level Security on every tenant table ──
    for table in TENANT_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;")
        op.execute(f"""
        CREATE POLICY firm_isolation ON {table}
        AS RESTRICTIVE
        FOR ALL
        USING (firm_id = NULLIF(current_setting('app.firm_id', true), '')::uuid);
        """)


def downgrade() -> None:
    for table in reversed(TENANT_TABLES):
        op.execute(f"DROP POLICY IF EXISTS firm_isolation ON {table};")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")

    op.execute("DROP TRIGGER IF EXISTS trg_audit_events_immutable ON audit_events;")
    op.execute("DROP FUNCTION IF EXISTS audit_events_prevent_tamper();")

    op.drop_table("notification_deliveries")
    op.drop_table("notifications")
    op.drop_table("ai_runs")
    op.drop_table("privacy_receipts")
    op.drop_table("audit_anchors")
    op.drop_table("audit_events")
    op.drop_table("reminders")
    op.drop_table("hearings")
    op.drop_table("deadlines")
    op.drop_table("holidays")
    op.drop_table("limitation_rules")
    op.drop_table("exports")
    op.drop_table("draft_approvals")
    op.drop_table("draft_comments")
    op.drop_table("draft_reviews")
    op.drop_table("citation_checks")
    op.drop_table("draft_references")
    op.drop_table("draft_grounds")
    op.drop_table("draft_versions")
    op.drop_table("drafts")
    op.drop_table("template_versions")
    op.drop_table("templates")
    op.drop_table("ingestion_batches")
    op.drop_table("matter_research_items")
    op.drop_table("citation_aliases")
    op.drop_table("source_passages")
    op.drop_table("legal_sources")
    op.drop_table("matter_notes")
    op.drop_table("title_reports")
    op.drop_table("title_flags")
    op.drop_table("encumbrances")
    op.drop_table("title_event_links")
    op.drop_table("title_events")
    op.drop_table("pii_findings")
    op.drop_table("extracted_field_versions")
    op.drop_table("extracted_fields")
    op.drop_table("processing_jobs")
    op.drop_table("ocr_results")
    op.drop_table("document_pages")
    op.drop_table("document_versions")
    op.drop_table("documents")
    op.drop_table("land_parcels")
    op.drop_table("matter_stages")
    op.drop_table("matter_parties")
    op.drop_table("matter_members")
    op.drop_table("matters")
    op.drop_table("parties")
    op.drop_table("statute_sections")
    op.drop_table("statutes")
    op.drop_table("forums")
    op.drop_table("login_attempts")
    op.drop_table("advocate_profiles")
