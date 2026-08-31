"""
Unit tests for security utilities (password hashing and JWT tokens).
"""

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing_and_verification():
    """Verify bcrypt hashing and verification functions."""
    plain = "SuperSecurePassword123!"
    hashed = get_password_hash(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_access_and_refresh_token():
    """Verify creation and decoding of JWT access and refresh tokens."""
    user_id = "user-12345"
    access_token = create_access_token(subject=user_id, extra_claims={"role": "admin"})

    decoded_access = decode_token(access_token)
    assert decoded_access["sub"] == user_id
    assert decoded_access["role"] == "admin"
    assert decoded_access["type"] == "access"

    refresh_token = create_refresh_token(subject=user_id)
    decoded_refresh = decode_token(refresh_token)
    assert decoded_refresh["sub"] == user_id
    assert decoded_refresh["type"] == "refresh"
