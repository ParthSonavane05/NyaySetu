"""SQLAlchemy 2.0 declarative mixins and common column types."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON
from uuid_utils import uuid7

# Dialect-agnostic JSON type: JSONB on PostgreSQL, JSON elsewhere
JSON_TYPE = JSON().with_variant(JSONB(), "postgresql")  # type: ignore[no-untyped-call]


class Base(DeclarativeBase):
    pass


class UUIDv7PrimaryKeyMixin:
    """Primary key using UUIDv7 (time-ordered)."""

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)


class TimestampMixin:
    """UTC created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class SoftDeleteMixin:
    """Soft delete support with deleted_at and deleted_by."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    deleted_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class TenantMixin:
    """Mandatory tenant isolation column for every tenant-scoped table."""

    firm_id: Mapped[UUID] = mapped_column(
        ForeignKey("firms.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )


class RowVersionMixin:
    """Optimistic concurrency control with row_version."""

    row_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default="1",
        nullable=False,
    )
