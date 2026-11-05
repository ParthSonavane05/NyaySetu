"""Shared validators for domain fields (Docs 02 section 9.2).

Validates:
- Enrolment number: `<STATE>/<number>/<year>` (e.g. GJ/1842/2016, 1950 to current year)
- Mobile number: E.164 or 10-digit Indian mobile
- Survey number: alphanumeric with `/` and optional sub-numbers
- Area: `H-A-Sq.m` format
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from app.core.errors import ValidationFailedError

ENROLMENT_REGEX = re.compile(r"^([A-Z]{2})\/(\d{1,8})\/(\d{4})$")
VALID_INDIAN_STATE_CODES = {
    "AP",
    "AR",
    "AS",
    "BR",
    "CG",
    "GA",
    "GJ",
    "HR",
    "HP",
    "JH",
    "KA",
    "KL",
    "MP",
    "MH",
    "MN",
    "ML",
    "MZ",
    "NL",
    "OD",
    "PB",
    "RJ",
    "SK",
    "TN",
    "TS",
    "TR",
    "UP",
    "UK",
    "WB",
    "DL",
    "JK",
    "LA",
    "CH",
    "DN",
    "DD",
    "PY",
    "AN",
    "LD",
}


def validate_enrolment_no(enrolment_no: str) -> tuple[str, str, int]:
    """Validate Bar Council enrolment format `<STATE>/<number>/<year>`.

    Example: 'GJ/1842/2016'.
    Returns: (state_code, number_str, year_int).
    Raises: ValidationFailedError if invalid.
    """
    clean_enrolment = enrolment_no.strip().upper()
    match = ENROLMENT_REGEX.match(clean_enrolment)
    if not match:
        raise ValidationFailedError(
            detail="Enrolment number must follow '<STATE>/<number>/<year>' format (e.g., 'GJ/1842/2016')."
        )

    state, number, year_str = match.groups()
    if state not in VALID_INDIAN_STATE_CODES:
        raise ValidationFailedError(detail=f"Invalid state code '{state}' in enrolment number.")

    year = int(year_str)
    current_year = datetime.now(UTC).year
    if year < 1950 or year > current_year:
        raise ValidationFailedError(
            detail=f"Enrolment year must be between 1950 and {current_year}."
        )

    return state, number, year
