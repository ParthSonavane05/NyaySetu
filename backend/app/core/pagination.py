"""
Cursor-based pagination using (created_at, id) composite (D-12).

Usage:
    page = paginate(query, cursor, limit, session)
"""

from __future__ import annotations

import base64
import json
from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel

T = TypeVar("T")


def encode_cursor(created_at: datetime, id: UUID) -> str:
    payload = json.dumps({"ts": created_at.isoformat(), "id": str(id)})
    return base64.urlsafe_b64encode(payload.encode()).decode()


def decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    try:
        payload = json.loads(base64.urlsafe_b64decode(cursor.encode()))
        return datetime.fromisoformat(payload["ts"]), UUID(payload["id"])
    except Exception as exc:
        raise ValueError(f"Invalid pagination cursor: {cursor}") from exc


class PageMeta(BaseModel):
    next_cursor: Optional[str] = None
    has_more: bool = False
    total_returned: int = 0


class Page(BaseModel, Generic[T]):
    items: List[T]
    meta: PageMeta
