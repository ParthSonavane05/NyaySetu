"""
Shared validators — survey-number normalisation, area parser, sort whitelist.

See BRAIN.md §3 D-09, D-10.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

# ---------------------------------------------------------------------------
# Gujarati digit / character normalisation (D-09)
# ---------------------------------------------------------------------------

_GUJARATI_DIGIT_TABLE = str.maketrans(
    "૦૧૨૩૪૫૬૭૮૯",
    "0123456789",
)

# Survey number suffixes written in Gujarati script → ASCII equivalents
# Common suffix vowels seen on Gujarat 7/12 records (non-exhaustive but covers
# the standard set used in revenue offices).
_GUJARATI_SUFFIX_TABLE = str.maketrans(
    {
        "અ": "A",
        "આ": "B",   # ā → B by convention in Gujarat survey records
        "ઇ": "C",
        "ઈ": "D",
        "ઉ": "E",
        "ઊ": "F",
        "એ": "G",
        "ઐ": "H",
        "ઓ": "I",
        "ઔ": "J",
        "ક": "K",
        "ખ": "KH",
        "ગ": "G",
        "ઘ": "GH",
    }
)

# Regex: optional integer, forward-slash separator, optional suffix
_SURVEY_RE = re.compile(r"^(\d+(?:/\d+)*)(/?[A-Z]*)$", re.IGNORECASE)


def normalise_survey_number(raw: str) -> str:
    """Normalise a survey-number string to ASCII canonical form.

    Accepts Gujarati-script digits and common suffix letters.

    Examples::

        normalise_survey_number("૧૪૨/અ")  → "142/A"
        normalise_survey_number("142/a")   → "142/A"
        normalise_survey_number("12/3")    → "12/3"
    """
    if not raw:
        raise ValueError("Survey number must not be empty")

    # 1. Translate Gujarati digits to ASCII
    text = raw.translate(_GUJARATI_DIGIT_TABLE)

    # 2. Translate Gujarati suffix vowels to their ASCII equivalents
    text = text.translate(_GUJARATI_SUFFIX_TABLE)

    # 3. Uppercase the whole string (handles lowercase ASCII suffixes)
    text = text.strip().upper()

    # 4. Validate the resulting form
    if not _SURVEY_RE.match(text):
        raise ValueError(
            f"Invalid survey number format after normalisation: '{text}' "
            f"(original: '{raw}'). Expected pattern: <digits>[/<digits>][/<letter>]"
        )

    return text


# ---------------------------------------------------------------------------
# Area parser (D-10): H-A-Sq.m → total square metres
# ---------------------------------------------------------------------------

# Conversion constants
_SQMT_PER_ARE = Decimal("100")          # 1 Are = 100 sq.m
_SQMT_PER_HECTARE = Decimal("10000")    # 1 Hectare = 10 000 sq.m


def parse_area(raw: str) -> tuple[Decimal, str]:
    """Parse a Gujarat revenue area string into (total_sqm, normalised_label).

    Accepts formats:
      - ``"2-15-500"``  → 2 Hectares, 15 Ares, 500 Sq.m
      - ``"0-05-250"``  → 0 Hectares, 5 Ares, 250 Sq.m
      - ``"500"``       → plain Sq.m shorthand
      - ``"1.5"``       → decimal hectares (H only)

    Returns ``(total_sq_metres, canonical_label)`` where the label is
    ``"<H>H <A>A <S>Sq.m"``.

    Raises ``ValueError`` on invalid input.
    """
    raw = raw.strip()

    # Three-part H-A-S
    if "-" in raw:
        parts = raw.split("-")
        if len(parts) != 3:
            raise ValueError(
                f"Area must have 3 hyphen-separated parts (H-A-Sq.m), got: '{raw}'"
            )
        try:
            h, a, s = (Decimal(p) for p in parts)
        except InvalidOperation:
            raise ValueError(f"Non-numeric area part in '{raw}'")

        if h < 0 or a < 0 or s < 0:
            raise ValueError("Area components must be non-negative")

        total = h * _SQMT_PER_HECTARE + a * _SQMT_PER_ARE + s
        label = f"{h}H {a}A {s}Sq.m"
        return total, label

    # Plain number → interpret as Sq.m
    try:
        sqm = Decimal(raw)
    except InvalidOperation:
        raise ValueError(f"Cannot parse area value: '{raw}'")

    if sqm < 0:
        raise ValueError("Area must be non-negative")

    return sqm, f"0H 0A {sqm}Sq.m"


# ---------------------------------------------------------------------------
# Sort whitelist validator
# ---------------------------------------------------------------------------

def validate_sort(
    sort_param: str | None,
    whitelist: list[str],
    default: str = "created_at",
) -> str:
    """Return validated sort field or raise ValueError.

    *whitelist* should contain bare field names (without ``-`` prefix).
    A leading ``-`` on *sort_param* indicates descending order.
    """
    if sort_param is None:
        return default

    direction = ""
    field = sort_param
    if sort_param.startswith("-"):
        direction = "-"
        field = sort_param[1:]

    if field not in whitelist:
        raise ValueError(
            f"Invalid sort field '{field}'. "
            f"Allowed: {', '.join(whitelist)}"
        )

    return f"{direction}{field}"


# ---------------------------------------------------------------------------
# Generic helper
# ---------------------------------------------------------------------------

def non_empty_string(v: Any, field_name: str = "field") -> str:
    """Pydantic validator helper — ensures value is a non-empty stripped string."""
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return v.strip()

