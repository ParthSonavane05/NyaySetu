"""Pydantic v2 request/response schemas for the Matters module."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.modules.matters.models import MatterStage, MatterStatus, PartyRole


# ---------------------------------------------------------------------------
# Matter
# ---------------------------------------------------------------------------

class MatterCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=512)
    description: Optional[str] = None
    stage: MatterStage = MatterStage.INTAKE
    status: MatterStatus = MatterStatus.ACTIVE
    forum_id: Optional[uuid.UUID] = None
    assigned_to: Optional[uuid.UUID] = None


class MatterPatch(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=512)
    description: Optional[str] = None
    status: Optional[MatterStatus] = None
    forum_id: Optional[uuid.UUID] = None
    assigned_to: Optional[uuid.UUID] = None
    row_version: int = Field(..., description="Current row_version for optimistic locking")


class MatterTransition(BaseModel):
    to_stage: MatterStage
    note: Optional[str] = Field(None, max_length=1024)

    @model_validator(mode="after")
    def note_required_for_backward(self) -> "MatterTransition":
        # Actual backward check is done in service with current stage context.
        # This validator just ensures note is a non-empty string when provided.
        if self.note is not None and not self.note.strip():
            raise ValueError("note must not be blank when provided")
        return self


class MatterOut(BaseModel):
    id: uuid.UUID
    firm_id: uuid.UUID
    matter_number: str
    title: str
    description: Optional[str]
    stage: MatterStage
    status: MatterStatus
    forum_id: Optional[uuid.UUID]
    assigned_to: Optional[uuid.UUID]
    row_version: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    # Counts — hearings/deadlines empty until P07
    member_count: int = 0
    party_count: int = 0
    parcel_count: int = 0
    hearing_count: int = 0
    next_deadline: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------

class MemberAdd(BaseModel):
    user_id: uuid.UUID
    role_in_matter: str = Field("member", max_length=64)


class MemberOut(BaseModel):
    id: uuid.UUID
    matter_id: uuid.UUID
    user_id: uuid.UUID
    role_in_matter: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Parties (names decrypted before returning)
# ---------------------------------------------------------------------------

class PartyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=512)
    party_role: PartyRole = PartyRole.OTHER
    notes: Optional[str] = None


class PartyPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=512)
    party_role: Optional[PartyRole] = None
    notes: Optional[str] = None


class PartyOut(BaseModel):
    id: uuid.UUID
    matter_id: uuid.UUID
    name: str          # decrypted
    party_role: PartyRole
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Parcels
# ---------------------------------------------------------------------------

class ParcelCreate(BaseModel):
    survey_number_raw: str = Field(..., min_length=1, max_length=128,
                                   description="Raw survey number (Gujarati or ASCII)")
    village: Optional[str] = Field(None, max_length=256)
    taluka: Optional[str] = Field(None, max_length=256)
    district: Optional[str] = Field(None, max_length=256)
    area_raw: Optional[str] = Field(None, description="Area in H-A-Sq.m format, e.g. '2-15-500'")
    notes: Optional[str] = None


class ParcelPatch(BaseModel):
    survey_number_raw: Optional[str] = Field(None, min_length=1, max_length=128)
    village: Optional[str] = Field(None, max_length=256)
    taluka: Optional[str] = Field(None, max_length=256)
    district: Optional[str] = Field(None, max_length=256)
    area_raw: Optional[str] = None
    notes: Optional[str] = None


class ParcelOut(BaseModel):
    id: uuid.UUID
    matter_id: uuid.UUID
    survey_number: str       # normalised
    survey_number_raw: str   # original
    village: Optional[str]
    taluka: Optional[str]
    district: Optional[str]
    area_sqm: Optional[Decimal]
    area_label: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class DashboardOut(BaseModel):
    due_soon: List[MatterOut] = []
    awaiting_review: List[MatterOut] = []
    recent_activity: List[dict] = []


# ---------------------------------------------------------------------------
# List response wrapper
# ---------------------------------------------------------------------------

class MatterListOut(BaseModel):
    items: List[MatterOut]
    next_cursor: Optional[str] = None
    has_more: bool = False
    total_returned: int = 0
