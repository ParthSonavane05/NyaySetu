"""Initial migration — creates all P06 matter tables.

Revision ID: 0001
Revises:
Create Date: 2026-11-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Enums ---
    matter_stage = postgresql.ENUM(
        "INTAKE", "DUE_DILIGENCE", "DRAFTING", "REVIEW", "FILED", "CLOSED", "ARCHIVED",
        name="matter_stage",
    )
    matter_status = postgresql.ENUM(
        "ACTIVE", "ON_HOLD", "URGENT", "ARCHIVED",
        name="matter_status",
    )
    party_role = postgresql.ENUM(
        "PETITIONER", "RESPONDENT", "INTERVENER", "WITNESS", "OTHER",
        name="party_role",
    )

    matter_stage.create(op.get_bind(), checkfirst=True)
    matter_status.create(op.get_bind(), checkfirst=True)
    party_role.create(op.get_bind(), checkfirst=True)

    # --- matters ---
    op.create_table(
        "matters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("matter_number", sa.String(32), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("stage", sa.Enum("INTAKE", "DUE_DILIGENCE", "DRAFTING", "REVIEW", "FILED", "CLOSED", "ARCHIVED", name="matter_stage"), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "ON_HOLD", "URGENT", "ARCHIVED", name="matter_status"), nullable=False),
        sa.Column("forum_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("row_version", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_archived", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("idempotency_key", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("firm_id", "matter_number", name="uq_matters_firm_number"),
        sa.UniqueConstraint("firm_id", "idempotency_key", name="uq_matters_firm_idempotency"),
    )
    op.create_index("ix_matters_firm_id", "matters", ["firm_id"])
    op.create_index("ix_matters_firm_stage", "matters", ["firm_id", "stage"])
    op.create_index("ix_matters_firm_status", "matters", ["firm_id", "status"])
    op.create_index("ix_matters_forum_id", "matters", ["forum_id"])
    op.create_index("ix_matters_assigned_to", "matters", ["assigned_to"])

    # --- matter_members ---
    op.create_table(
        "matter_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("matter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("matters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_in_matter", sa.String(64), nullable=False, server_default="member"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("matter_id", "user_id", name="uq_matter_members"),
    )

    # --- matter_parties ---
    op.create_table(
        "matter_parties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("matter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("matters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name_enc", sa.Text, nullable=False),
        sa.Column("party_role", sa.Enum("PETITIONER", "RESPONDENT", "INTERVENER", "WITNESS", "OTHER", name="party_role"), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_matter_parties_matter_id", "matter_parties", ["matter_id"])

    # --- matter_parcels ---
    op.create_table(
        "matter_parcels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("matter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("matters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("survey_number", sa.String(64), nullable=False),
        sa.Column("survey_number_raw", sa.String(128), nullable=False),
        sa.Column("village", sa.String(256), nullable=True),
        sa.Column("taluka", sa.String(256), nullable=True),
        sa.Column("district", sa.String(256), nullable=True),
        sa.Column("area_sqm", sa.Numeric(18, 4), nullable=True),
        sa.Column("area_label", sa.String(64), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_matter_parcels_matter_id", "matter_parcels", ["matter_id"])

    # --- matter_audit_logs ---
    op.create_table(
        "matter_audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("matter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("matters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("payload", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_matter_audit_logs_matter_id", "matter_audit_logs", ["matter_id"])
    op.create_index("ix_matter_audit_logs_matter_created", "matter_audit_logs", ["matter_id", "created_at"])


def downgrade() -> None:
    op.drop_table("matter_audit_logs")
    op.drop_table("matter_parcels")
    op.drop_table("matter_parties")
    op.drop_table("matter_members")
    op.drop_table("matters")

    op.execute("DROP TYPE IF EXISTS party_role")
    op.execute("DROP TYPE IF EXISTS matter_status")
    op.execute("DROP TYPE IF EXISTS matter_stage")
