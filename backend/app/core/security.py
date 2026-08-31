"""
Security utilities: password hashing, verification, and JWT creation.
"""

import hashlib
import hmac
import os
from datetime import UTC, datetime, timedelta
from typing import Any

try:
    import bcrypt

    _HAS_BCRYPT = True
except ImportError:
    _HAS_BCRYPT = False

try:
    import jwt
except ImportError:
    from jose import jwt  # type: ignore

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hash."""
    if _HAS_BCRYPT and (hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$")):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False

    # Fallback verification for SHA256 PBKDF2 hashes
    if "$" in hashed_password:
        parts = hashed_password.split("$")
        if len(parts) == 3 and parts[0] == "pbkdf2_sha256":
            salt = parts[1]
            expected_hash = parts[2]
            computed = hashlib.pbkdf2_hmac(
                "sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000
            ).hex()
            return hmac.compare_digest(expected_hash, computed)

    return False


def get_password_hash(password: str) -> str:
    """Generate a secure password hash."""
    if _HAS_BCRYPT:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    # Standard library fallback using PBKDF2-HMAC-SHA256
    salt = os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()
    return f"pbkdf2_sha256${salt}${hashed}"


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a signed JWT access token."""
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: dict[str, Any] = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.now(UTC),
    }
    if extra_claims:
        to_encode.update(extra_claims)

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT refresh token."""
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode: dict[str, Any] = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": datetime.now(UTC),
    }

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a signed JWT token."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
