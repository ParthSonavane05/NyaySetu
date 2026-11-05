"""Pydantic schemas for the audit module."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_serializer


class AuditEventOut(BaseModel):
    seq: int
    at: datetime
    actor_id: UUID | None
    actor_role: str | None
    action: str
    resource_type: str | None
    resource_id: UUID | None
    matter_id: UUID | None
    ip: str | None
    # hash is exposed as hex string (safe to show, helps manual verification)
    hash: str

    @field_serializer("hash")
    def _ser_hash(self, v: str) -> str:  # noqa: PLR6301
        return v

    model_config = {"from_attributes": True}


class AuditEventListOut(BaseModel):
    items: list[AuditEventOut]
    next_cursor: str | None
    total: int | None = None


class AuditVerifyOut(BaseModel):
    ok: bool
    verified_count: int
    first_tampered_seq: int | None
    from_seq: int
    to_seq: int

