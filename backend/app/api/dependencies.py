"""
API Dependencies for CloudSentinel AI.

`get_current_user` — the security boundary every protected endpoint
composes: Bearer token extraction, JWT validation with access-type
enforcement, and a live database lookup. Optional variants support
public-with-identity endpoints.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.jwt import ACCESS_TYPE, decode_token, verify_token_type
from app.core.constants import UserRole
from app.core.exceptions import AuthenticationError
from app.database.models import User
from app.database.session import get_db

_bearer = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated User from a Bearer access token.

    Enforces: valid signature/expiry, token type == access, and the
    account existing and being active.
    """
    payload = decode_token(credentials.credentials)
    verify_token_type(payload, ACCESS_TYPE)

    user_id = str(payload.get("sub", ""))
    if not user_id:
        raise AuthenticationError("Token subject is empty")

    user = db.get(User, user_id)
    if user is None:
        raise AuthenticationError("Account no longer exists")
    if not user.is_active:
        raise AuthenticationError("Account is disabled")
    return user


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
) -> User | None:
    """Like get_current_user but yields None when no/invalid token is given."""
    if credentials is None:
        return None
    try:
        return get_current_user(credentials, db)
    except AuthenticationError:
        return None


def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    """Role gate for admin-only endpoints."""
    if current_user.role != UserRole.ADMIN:
        raise AuthenticationError("Administrator role required")
    return current_user


__all__ = ["get_current_user", "get_current_user_optional", "get_current_active_admin"]
