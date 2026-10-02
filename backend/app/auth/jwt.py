"""
JWT Utilities for CloudSentinel AI.

Thin, purpose-named layer over `app.core.security` that adds token-type
verification (access vs refresh) — refresh tokens must never be
accepted at protected endpoints, and vice versa.
"""

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
)
from app.core.security import (
    decode_token as _core_decode_token,
)

ACCESS_TYPE = "access"
REFRESH_TYPE = "refresh"


@dataclass
class TokenPair:
    """Access + refresh tokens as the login/refresh endpoints return them."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


def create_token_pair(
    subject: str,
    extra_claims: dict[str, Any] | None = None,
    access_expires: timedelta | None = None,
) -> TokenPair:
    """Issue a matched access/refresh pair for one subject."""
    return TokenPair(
        access_token=create_access_token(
            subject, expires_delta=access_expires, extra_claims=extra_claims
        ),
        refresh_token=create_refresh_token(subject),
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate any token signature/expiry.

    Raises AuthenticationError (instead of jwt exceptions) so the API
    layer maps failures to 401 uniformly.
    """
    try:
        return _core_decode_token(token)
    except AuthenticationError:
        raise
    except Exception as exc:
        raise AuthenticationError("Invalid or expired token") from exc


def verify_token_type(payload: dict[str, Any], expected: str) -> None:
    """Ensure a token payload has the expected `type` claim.

    Raises AuthenticationError on mismatch — the guard that keeps
    refresh tokens from authenticating API calls.
    """
    actual = payload.get("type")
    if actual != expected:
        raise AuthenticationError(f"Expected a {expected} token, got {actual!r}")


__all__ = [
    "TokenPair",
    "create_token_pair",
    "decode_token",
    "verify_token_type",
    "ACCESS_TYPE",
    "REFRESH_TYPE",
]
