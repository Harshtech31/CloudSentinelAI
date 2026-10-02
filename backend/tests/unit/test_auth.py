"""Unit tests for app.auth utilities (roadmap task 19)."""

from datetime import timedelta

import pytest

from app.auth import jwt as auth_jwt
from app.auth.password import hash_password, verify_password
from app.auth.permissions import (
    EXPORT_REPORTS,
    MANAGE_USERS,
    SCAN,
    VIEW,
    permissions_for,
    require_permission,
    role_can,
    roles_with,
)
from app.core.constants import UserRole
from app.core.exceptions import AuthenticationError, PermissionDeniedError

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------


class TestPassword:
    def test_roundtrip(self) -> None:
        hashed = hash_password("Sup3rSecret!")
        assert verify_password("Sup3rSecret!", hashed) is True

    def test_wrong_password_fails(self) -> None:
        hashed = hash_password("Sup3rSecret!")
        assert verify_password("wrong-password", hashed) is False

    def test_hash_is_salted(self) -> None:
        """Same plaintext twice yields different hashes (unique salts)."""
        assert hash_password("Sup3rSecret!") != hash_password("Sup3rSecret!")

    def test_plaintext_not_recoverable(self) -> None:
        hashed = hash_password("Sup3rSecret!")
        assert "Sup3rSecret" not in hashed


# ---------------------------------------------------------------------------
# JWT helpers with token-type verification
# ---------------------------------------------------------------------------


class TestJwt:
    def test_token_pair_shape(self) -> None:
        pair = auth_jwt.create_token_pair("user-123", {"role": "admin"})
        assert pair.access_token and pair.refresh_token
        assert pair.access_token != pair.refresh_token
        assert pair.token_type == "bearer"

    def test_decode_roundtrip_with_claims(self) -> None:
        pair = auth_jwt.create_token_pair("user-123", {"role": "analyst"})
        payload = auth_jwt.decode_token(pair.access_token)
        assert payload["sub"] == "user-123"
        assert payload["role"] == "analyst"

    def test_refresh_token_has_refresh_type(self) -> None:
        pair = auth_jwt.create_token_pair("user-123")
        assert auth_jwt.decode_token(pair.refresh_token)["type"] == auth_jwt.REFRESH_TYPE
        assert auth_jwt.decode_token(pair.access_token)["type"] == auth_jwt.ACCESS_TYPE

    def test_refresh_token_rejected_as_access(self) -> None:
        """The core guard: a refresh token must not authenticate API calls."""
        pair = auth_jwt.create_token_pair("user-123")
        payload = auth_jwt.decode_token(pair.refresh_token)
        with pytest.raises(AuthenticationError, match="access"):
            auth_jwt.verify_token_type(payload, auth_jwt.ACCESS_TYPE)

    def test_access_token_rejected_as_refresh(self) -> None:
        pair = auth_jwt.create_token_pair("user-123")
        payload = auth_jwt.decode_token(pair.access_token)
        with pytest.raises(AuthenticationError, match="refresh"):
            auth_jwt.verify_token_type(payload, auth_jwt.REFRESH_TYPE)

    def test_garbage_token_raises_authentication_error(self) -> None:
        with pytest.raises(AuthenticationError):
            auth_jwt.decode_token("not.a.jwt")

    def test_tampered_token_rejected(self) -> None:
        pair = auth_jwt.create_token_pair("user-123")
        tampered = pair.access_token[:-3] + ("aaa" if pair.access_token[-3:] != "aaa" else "bbb")
        with pytest.raises(AuthenticationError):
            auth_jwt.decode_token(tampered)

    def test_expired_token_raises(self) -> None:
        pair = auth_jwt.create_token_pair("user-123", access_expires=timedelta(seconds=-30))
        with pytest.raises(AuthenticationError, match="expired|Invalid"):
            auth_jwt.decode_token(pair.access_token)


# ---------------------------------------------------------------------------
# RBAC permission matrix
# ---------------------------------------------------------------------------


class TestPermissions:
    def test_admin_is_superuser(self) -> None:
        for permission in (VIEW, SCAN, MANAGE_USERS, EXPORT_REPORTS):
            assert role_can(UserRole.ADMIN, permission) is True

    def test_analyst_can_scan_but_not_manage_users(self) -> None:
        assert role_can(UserRole.ANALYST, SCAN) is True
        assert role_can(UserRole.ANALYST, MANAGE_USERS) is False

    def test_viewer_is_read_only(self) -> None:
        assert role_can(UserRole.VIEWER, VIEW) is True
        assert role_can(UserRole.VIEWER, SCAN) is False

    def test_unknown_role_denied(self) -> None:
        assert role_can("intern", VIEW) is False

    def test_require_permission_raises_when_denied(self) -> None:
        with pytest.raises(PermissionDeniedError):
            require_permission(UserRole.VIEWER, MANAGE_USERS)

    def test_require_permission_passes_when_allowed(self) -> None:
        require_permission(UserRole.ANALYST, EXPORT_REPORTS)  # must not raise

    def test_permissions_for_frontend_mirroring(self) -> None:
        assert MANAGE_USERS in permissions_for(UserRole.ADMIN)
        assert permissions_for("nonexistent-role") == frozenset()

    def test_roles_with_covers_matrix(self) -> None:
        assert set(roles_with(MANAGE_USERS)) == {UserRole.ADMIN}
        assert UserRole.VIEWER in roles_with(VIEW)
