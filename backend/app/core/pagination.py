"""Cursor-based pagination and sorting whitelist helpers."""

from __future__ import annotations

import base64
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")

MAX_PAGE_LIMIT = 100
DEFAULT_PAGE_LIMIT = 25


class CursorParams(BaseModel):
    cursor: str | None = None
    limit: int = Field(default=DEFAULT_PAGE_LIMIT, ge=1)

    @field_validator("limit", mode="before")
    @classmethod
    def _clamp_limit(cls, v: Any) -> int:
        if isinstance(v, int | str):
            val = int(v)
            if val < 1:
                from app.core.errors import ValidationFailedError

                raise ValidationFailedError(detail="Limit must be at least 1.")
            return min(val, MAX_PAGE_LIMIT)
        return DEFAULT_PAGE_LIMIT


class CursorPage(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None
    has_more: bool = False


def encode_cursor(value: str) -> str:
    return base64.urlsafe_b64encode(value.encode()).decode()


def decode_cursor(cursor: str) -> str:
    try:
        return base64.urlsafe_b64decode(cursor.encode()).decode()
    except Exception as exc:
        from app.core.errors import ValidationFailedError

        raise ValidationFailedError(detail="Invalid pagination cursor.") from exc


def validate_sort_field(field: str, allowed: set[str]) -> str:
    clean_field = field.lstrip("-").lstrip("+")
    if clean_field not in allowed:
        from app.core.errors import ValidationFailedError

        raise ValidationFailedError(
            detail=f"Sort by '{clean_field}' is not allowed. Allowed: {', '.join(sorted(allowed))}"
        )
    return field
