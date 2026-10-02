"""
Authentication Package for CloudSentinel AI.

JWT creation/verification, password hashing, and RBAC permission
logic. Endpoints in `app.api.v1.auth` compose these utilities; the
request dependency lives in `app.api.dependencies`.
"""

from app.auth.jwt import (
    TokenPair,
    create_token_pair,
    decode_token,
    verify_token_type,
)
from app.auth.password import hash_password, verify_password
from app.auth.permissions import (
    PERMISSIONS,
    Role,
    permissions_for,
    require_permission,
    role_can,
)

__all__ = [
    "TokenPair",
    "create_token_pair",
    "decode_token",
    "verify_token_type",
    "hash_password",
    "verify_password",
    "Role",
    "PERMISSIONS",
    "role_can",
    "require_permission",
    "permissions_for",
]
