"""
RBAC Permissions for CloudSentinel AI.

Static permission matrix per role. Viewers read; analysts read and run
scans; admins manage users and settings. The matrix is the single
source both the API dependencies and the frontend route guards mirror.
"""

from collections.abc import Sequence

from app.core.constants import UserRole
from app.core.exceptions import PermissionDeniedError
from app.core.logging import logger

# Canonical role names mirror app.core.constants.UserRole.
Role = UserRole

VIEW = "view"
SCAN = "scan"
MANAGE_USERS = "manage_users"
MANAGE_SETTINGS = "manage_settings"
EXPORT_REPORTS = "export_reports"

PERMISSIONS: dict[str, frozenset[str]] = {
    Role.ADMIN: frozenset({VIEW, SCAN, MANAGE_USERS, MANAGE_SETTINGS, EXPORT_REPORTS}),
    Role.ANALYST: frozenset({VIEW, SCAN, EXPORT_REPORTS}),
    Role.VIEWER: frozenset({VIEW}),
}


def role_can(role: str | UserRole, permission: str) -> bool:
    """True when the role holds the permission; unknown roles deny."""
    key = role.value if isinstance(role, UserRole) else str(role)
    return permission in PERMISSIONS.get(key, frozenset())


def require_permission(role: str | UserRole, permission: str) -> None:
    """Enforce a permission; raises PermissionDeniedError when denied."""
    if not role_can(role, permission):
        logger.warning("Permission denied: role=%s needs=%s", role, permission)
        raise PermissionDeniedError(f"Role {role!r} lacks permission {permission!r}")


def permissions_for(role: str | UserRole) -> frozenset[str]:
    """The permission set for a role (frontend menu mirroring)."""
    key = role.value if isinstance(role, UserRole) else str(role)
    return PERMISSIONS.get(key, frozenset())


def roles_with(permission: str) -> Sequence[str]:
    """Roles holding a permission (diagnostics/tests)."""
    return [role for role, perms in PERMISSIONS.items() if permission in perms]


__all__ = [
    "Role",
    "PERMISSIONS",
    "VIEW",
    "SCAN",
    "MANAGE_USERS",
    "MANAGE_SETTINGS",
    "EXPORT_REPORTS",
    "role_can",
    "require_permission",
    "permissions_for",
    "roles_with",
]
