"""
Authentication endpoints (Register, Login, Refresh).
"""

from fastapi import APIRouter, status

from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User Account",
    description="Registers a new user with email, password, display name, and initial RBAC role.",
)
async def register(payload: RegisterRequest) -> UserResponse:
    """Register a new user account (Scaffold stub)."""
    return UserResponse(
        id="usr_01j8k9",
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        is_active=True,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login & Token Generation",
    description="Authenticates user credentials and returns signed JWT access and refresh tokens.",
)
async def login(payload: LoginRequest) -> TokenResponse:
    """Authenticate and obtain JWT tokens (Scaffold stub)."""
    return TokenResponse(
        access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.dummy_access_token",
        refresh_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.dummy_refresh_token",
        token_type="bearer",
        expires_in=3600,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh JWT Access Token",
    description="Generates a refreshed access token using a valid, unexpired refresh token.",
)
async def refresh_token(payload: RefreshTokenRequest) -> TokenResponse:
    """Refresh JWT access token (Scaffold stub)."""
    return TokenResponse(
        access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.dummy_refreshed_token",
        refresh_token=payload.refresh_token,
        token_type="bearer",
        expires_in=3600,
    )
