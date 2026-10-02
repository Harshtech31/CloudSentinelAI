"""
Authentication endpoints (Register, Login, Refresh, Me).

Database-backed flows composing the auth utilities: bcrypt password
hashing at rest, JWT pair issuance with type-claim enforcement, and
401/409 semantics aligned with the global exception handlers.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.auth.jwt import REFRESH_TYPE, create_token_pair, decode_token, verify_token_type
from app.auth.password import hash_password, verify_password
from app.core.constants import UserRole
from app.core.exceptions import (
    AuthenticationError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)
from app.core.logging import logger
from app.database.models import User
from app.database.session import get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )


def _issue_tokens(user: User) -> TokenResponse:
    pair = create_token_pair(user.id, extra_claims={"role": user.role.value})
    return TokenResponse(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
        token_type=pair.token_type,
        expires_in=pair.expires_in,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User Account",
    description="Registers a new user with email, password, display name, and initial RBAC role.",
)
async def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    """Create an account with a bcrypt-hashed password."""
    existing = db.query(User).filter_by(email=payload.email.lower()).one_or_none()
    if existing is not None:
        raise ResourceAlreadyExistsError(f"An account with email {payload.email} already exists")

    user = User(
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Registered new user %s (role=%s)", user.email, user.role)
    return _user_response(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login & Token Generation",
    description="Authenticates user credentials and returns signed JWT access and refresh tokens.",
)
async def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Verify credentials and issue a JWT pair."""
    user = db.query(User).filter_by(email=payload.username.lower()).one_or_none()
    # Same error for unknown email and wrong password: no account enumeration.
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise AuthenticationError("Incorrect email or password")
    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    logger.info("User %s logged in", user.email)
    return _issue_tokens(user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh JWT Access Token",
    description="Generates a refreshed access token using a valid, unexpired refresh token.",
)
async def refresh_token(
    payload: RefreshTokenRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    """Exchange a refresh token for a fresh pair (refresh-type enforced)."""
    claims = decode_token(payload.refresh_token)
    verify_token_type(claims, REFRESH_TYPE)

    user = db.get(User, str(claims.get("sub", "")))
    if user is None:
        raise ResourceNotFoundError("Account no longer exists")
    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    return _issue_tokens(user)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Returns the authenticated account's profile from a Bearer access token.",
)
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the caller's profile (requires a valid access token)."""
    _ = UserRole  # role values flow through the response model
    return _user_response(current_user)
