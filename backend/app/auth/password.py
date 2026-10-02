"""
Password Utilities for CloudSentinel AI.

Purpose-named wrappers over the core hashing implementation so auth
code reads uniformly. Hashing uses bcrypt when available with a
PBKDF2-SHA256 fallback (managed by app.core.security).
"""

from app.core.security import get_password_hash as _core_hash
from app.core.security import verify_password as _core_verify


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password for storage."""
    return _core_hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against a stored hash."""
    return _core_verify(plain_password, hashed_password)


__all__ = ["hash_password", "verify_password"]
