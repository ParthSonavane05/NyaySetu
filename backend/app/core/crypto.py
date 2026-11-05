"""
Crypto interface — Fernet symmetric encryption for PII fields (party/member names).

Usage:
    crypto = get_crypto()
    ciphertext = crypto.encrypt("Ramesh Patel")
    plaintext  = crypto.decrypt(ciphertext)

Key source: settings.SECRET_KEY (base64url-encoded 32-byte Fernet key).
See BRAIN.md §5 for rotation strategy.
"""

from __future__ import annotations

import base64
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


class CryptoService:
    """Thin wrapper around Fernet that fulfils the crypto interface contract."""

    def __init__(self, key: str) -> None:
        # Accept raw base64url key or a Fernet URL-safe key string
        raw = key.encode() if isinstance(key, str) else key
        # Pad if necessary so Fernet accepts it
        padded = raw + b"=" * (-len(raw) % 4)
        self._fernet = Fernet(padded)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def encrypt(self, plaintext: str) -> str:
        """Return base64 ciphertext token for *plaintext*."""
        if not plaintext:
            return ""
        token = self._fernet.encrypt(plaintext.encode("utf-8"))
        return base64.b64encode(token).decode("ascii")

    def decrypt(self, ciphertext: str) -> str:
        """Return plaintext from base64 ciphertext token.

        Raises ``ValueError`` on bad / tampered ciphertext.
        """
        if not ciphertext:
            return ""
        try:
            raw = base64.b64decode(ciphertext.encode("ascii"))
            return self._fernet.decrypt(raw).decode("utf-8")
        except (InvalidToken, Exception) as exc:
            raise ValueError("Ciphertext could not be decrypted") from exc


@lru_cache(maxsize=1)
def _build_crypto() -> CryptoService:
    return CryptoService(settings.SECRET_KEY)


def get_crypto() -> CryptoService:
    """FastAPI dependency — returns the singleton CryptoService."""
    return _build_crypto()

