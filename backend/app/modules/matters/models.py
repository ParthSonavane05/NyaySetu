"""
ORM models for the Matters module (P06).

Tables:
  matters            — core matter record
  matter_members     — firm users linked to a matter
  matter_parties     — litigants / opposing counsel (names encrypted)
  matter_parcels     — land parcels (survey numbers, area)
  matter_audit_log   — append-only audit trail (canonical action names §8)
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class MatterStage(str, enum.Enum):
    INTAKE = "INTAKE"
    DUE_DILIGENCE = "DUE_DILIGENCE"
    DRAFTING = "DRAFTING"
    REVIEW = "REVIEW"
    FILED = "FILED"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class MatterStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    URGENT = "URGENT"
    ARCHIVED = "ARCHIVED"


class PartyRole(str, enum.Enum):
    PETITIONER = "PETITIONER"
    RESPONDENT = "RESPONDENT"
    INTERVENER = "INTERVENER"
    WITNESS = "WITNESS"
    OTHER = "OTHER"


# ---------------------------------------------------------------------------
# Matter
# ---------------------------------------------------------------------------

class Matter(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "matters"

    firm_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    matter_number: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    stage: Mapped[MatterStage] = mapped_column(
        SAEnum(MatterStage, name="matter_stage"), nullable=False, default=MatterStage.INTAKE
    )
    status: Mapped[MatterStatus] = mapped_column(
        SAEnum(MatterStatus, name="matter_status"), nullable=False, default=MatterStatus.ACTIVE
    )
    forum_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    row_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Relationships
    members: Mapped[list[MatterMember]] = relationship("MatterMember", back_populates="matter", lazy="select")
    parties: Mapped[list[MatterParty]] = relationship("MatterParty", back_populates="matter", lazy="select")
    parcels: Mapped[list[MatterParcel]] = relationship("MatterParcel", back_populates="matter", lazy="select")
    audit_logs: Mapped[list[MatterAuditLog]] = relationship("MatterAuditLog", back_populates="matter", lazy="select")

    __table_args__ = (
        UniqueConstraint("firm_id", "matter_number", name="uq_matters_firm_number"),
        UniqueConstraint("firm_id", "idempotency_key", name="uq_matters_firm_idempotency"),
        Index("ix_matters_firm_stage", "firm_id", "stage"),
        Index("ix_matters_firm_status", "firm_id", "status"),
    )


# ---------------------------------------------------------------------------
# Matter Members
# ---------------------------------------------------------------------------

class MatterMember(Base, TimestampMixin):
    __tablename__ = "matter_members"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matter_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    role_in_matter: Mapped[str] = mapped_column(String(64), nullable=False, default="member")

    matter: Mapped[Matter] = relationship("Matter", back_populates="members")

    __table_args__ = (
        UniqueConstraint("matter_id", "user_id", name="uq_matter_members"),
    )


# ---------------------------------------------------------------------------
# Matter Parties (names encrypted per §5)
# ---------------------------------------------------------------------------

class MatterParty(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "matter_parties"

    matter_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # name stored as Fernet-encrypted ciphertext (see BRAIN.md §5)
    name_enc: Mapped[str] = mapped_column(Text, nullable=False)
    party_role: Mapped[PartyRole] = mapped_column(
        SAEnum(PartyRole, name="party_role"), nullable=False, default=PartyRole.OTHER
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    matter: Mapped[Matter] = relationship("Matter", back_populates="parties")


# ---------------------------------------------------------------------------
# Matter Parcels
# ---------------------------------------------------------------------------

class MatterParcel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "matter_parcels"

    matter_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    survey_number: Mapped[str] = mapped_column(String(64), nullable=False)   # normalised ASCII
    survey_number_raw: Mapped[str] = mapped_column(String(128), nullable=False)  # original input
    village: Mapped[str | None] = mapped_column(String(256), nullable=True)
    taluka: Mapped[str | None] = mapped_column(String(256), nullable=True)
    district: Mapped[str | None] = mapped_column(String(256), nullable=True)
    area_sqm: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)   # total sq.m
    area_label: Mapped[str | None] = mapped_column(String(64), nullable=True)       # "2H 15A 500Sq.m"
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    matter: Mapped[Matter] = relationship("Matter", back_populates="parcels")


# ---------------------------------------------------------------------------
# Matter Audit Log (append-only)
# ---------------------------------------------------------------------------

class MatterAuditLog(Base, TimestampMixin):
    __tablename__ = "matter_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matter_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)   # canonical action name
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON blob

    matter: Mapped[Matter] = relationship("Matter", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_matter_audit_logs_matter_created", "matter_id", "created_at"),
    )
