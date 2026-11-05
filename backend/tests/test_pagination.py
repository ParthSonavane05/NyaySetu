"""Tests for cursor pagination and sorting helpers."""

from __future__ import annotations

import pytest

from app.core.errors import ValidationFailedError
from app.core.pagination import (
    MAX_PAGE_LIMIT,
    CursorPage,
    CursorParams,
    decode_cursor,
    encode_cursor,
    validate_sort_field,
)


def test_encode_decode_roundtrip() -> None:
    original = "2024-01-15T10:30:00Z|abc123"
    encoded = encode_cursor(original)
    assert isinstance(encoded, str)
    assert encoded != original  # it's opaque
    decoded = decode_cursor(encoded)
    assert decoded == original


def test_decode_invalid_cursor_raises() -> None:
    with pytest.raises(ValidationFailedError, match="Invalid pagination cursor"):
        decode_cursor("not-valid-base64!!!")


def test_cursor_params_default() -> None:
    params = CursorParams()
    assert params.cursor is None
    assert params.limit == 25


def test_cursor_params_clamp_limit() -> None:
    params = CursorParams(limit=200)
    assert params.limit == MAX_PAGE_LIMIT


def test_cursor_params_min_limit() -> None:
    with pytest.raises(ValidationFailedError):
        CursorParams(limit=0)


def test_cursor_page_model() -> None:
    page = CursorPage[str](items=["a", "b"], next_cursor="abc", has_more=True)
    assert len(page.items) == 2
    assert page.has_more is True


def test_validate_sort_field_ok() -> None:
    result = validate_sort_field("created_at", {"created_at", "name"})
    assert result == "created_at"


def test_validate_sort_field_desc() -> None:
    result = validate_sort_field("-created_at", {"created_at", "name"})
    assert result == "-created_at"


def test_validate_sort_field_disallowed() -> None:
    with pytest.raises(ValidationFailedError, match="not allowed"):
        validate_sort_field("secret_field", {"created_at", "name"})
