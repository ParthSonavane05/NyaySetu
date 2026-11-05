"""Authentication and security utilities: Argon2id, JWT, AES-GCM, TOTP."""

from __future__ import annotations

import base64
import hashlib
import os
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
import pyotp
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from uuid_utils import uuid7

from app.core.config import get_settings
from app.core.errors import DomainError

# Argon2id password hasher with production-grade parameters
_ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,  # 64 MB
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    """Hash password using Argon2id."""
    return _ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against Argon2id hash with constant-time behavior."""
    try:
        return _ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def hash_token(token: str) -> str:
    """Hash a token (refresh, invitation, reset) using SHA-256 for DB storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# ── JWT token operations ──

ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)
REFRESH_TOKEN_LIFETIME = timedelta(days=7)
MFA_CHALLENGE_LIFETIME = timedelta(minutes=5)


def create_access_token(
    *,
    user_id: UUID | Any,
    firm_id: UUID | None | Any,
    role: str,
    session_id: UUID | None | Any = None,
    is_client: bool = False,
    mfa_completed: bool = True,
) -> str:
    """Create a signed 15-minute access JWT."""
    settings = get_settings()
    now = datetime.now(UTC)
    claims: dict[str, Any] = {
        "sub": str(user_id),
        "firm_id": str(firm_id) if firm_id else None,
        "role": role,
        "sid": str(session_id) if session_id else None,
        "principal": "client" if is_client else "user",
        "mfa_completed": mfa_completed,
        "iat": int(now.timestamp()),
        "exp": int((now + ACCESS_TOKEN_LIFETIME).timestamp()),
        "jti": str(uuid7()),
    }
    return jwt.encode(claims, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate access JWT."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"],
            options={"require": ["sub", "exp", "iat"]},
        )
        return dict(payload)
    except jwt.ExpiredSignatureError as exc:
        raise DomainError(detail="Token has expired.", code="token_expired") from exc
    except jwt.PyJWTError as exc:
        raise DomainError(detail="Invalid token.", code="unauthenticated") from exc


def generate_secure_token(nbytes: int = 32) -> str:
    """Generate a high-entropy URL-safe token."""
    return secrets.token_urlsafe(nbytes)


# ── Envelope / Secret Encryption (AES-256-GCM) ──


def _get_encryption_key() -> bytes:
    settings = get_settings()
    # Derives 32-byte key from app secret
    return hashlib.sha256(f"mfa-enc:{settings.secret_key}".encode()).digest()


def encrypt_secret(plain_text: str) -> str:
    """Encrypt sensitive string (e.g. TOTP secret) with AES-256-GCM."""
    aesgcm = AESGCM(_get_encryption_key())
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plain_text.encode("utf-8"), None)
    return base64.b64encode(nonce + ct).decode("utf-8")


def decrypt_secret(cipher_text: str) -> str:
    """Decrypt AES-256-GCM encrypted string."""
    raw = base64.b64decode(cipher_text.encode("utf-8"))
    nonce = raw[:12]
    ct = raw[12:]
    aesgcm = AESGCM(_get_encryption_key())
    pt = aesgcm.decrypt(nonce, ct, None)
    return pt.decode("utf-8")


# ── TOTP MFA Operations ──


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="NyaySetu")


def verify_totp_code(secret: str, code: str) -> bool:
    """Verify TOTP 6-digit code with +/- 1 time step tolerance (30 sec window)."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code.strip(), valid_window=1)


def generate_recovery_codes(count: int = 8) -> list[str]:
    """Generate a set of single-use alphanumeric recovery codes."""
    return [secrets.token_hex(4).upper() for _ in range(count)]


# ── Constant-time password validation ──


def validate_password_policy(password: str, email: str | None = None) -> list[str]:
    """Enforce Docs 02 section 9.2: 12-128 chars, not equal to email."""
    errors: list[str] = []
    if len(password) < 12:
        errors.append("Password must be at least 12 characters long.")
    if len(password) > 128:
        errors.append("Password must not exceed 128 characters.")
    if email and password.lower().strip() == email.lower().strip():
        errors.append("Password must not be equal to email address.")
    return errors
