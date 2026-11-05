"""Tests for Unicode NFC normalisation and digit conversion."""

from __future__ import annotations

from app.core.text import normalise_text


def test_gujarati_digits() -> None:
    assert normalise_text("૧૨૩૪૫") == "12345"


def test_devanagari_digits() -> None:
    assert normalise_text("०१२३४५६७८९") == "0123456789"


def test_mixed_text() -> None:
    result = normalise_text("Survey No. ૧૨/અ, Plot ३४")
    assert result == "Survey No. 12/અ, Plot 34"


def test_nfc_normalisation() -> None:
    # é as two code points (e + combining accent) -> single code point
    decomposed = "caf\u0065\u0301"
    result = normalise_text(decomposed)
    assert result == "café"
    assert len(result) == 4  # NFC composed
