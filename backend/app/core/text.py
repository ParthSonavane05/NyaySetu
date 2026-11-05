"""Unicode NFC normalisation and Gujarati/Devanagari digit conversion."""

from __future__ import annotations

import unicodedata

# Gujarati digits U+0AE6..U+0AEF
# Devanagari digits U+0966..U+096F
_DIGIT_MAP = str.maketrans(
    "૦૧૨૩૪૫૬૭૮૯" "०१२३४५६७८९",
    "0123456789" "0123456789",
)


def normalise_text(value: str) -> str:
    """NFC-normalise and convert Gujarati/Devanagari digits to ASCII."""
    return unicodedata.normalize("NFC", value).translate(_DIGIT_MAP)
