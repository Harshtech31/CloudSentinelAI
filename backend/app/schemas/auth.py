"""
Authentication and user request/response schemas for OpenAPI docs.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.core.constants import UserRole


class RegisterRequest(BaseModel):
    """User account registration payload."""

    email: EmailStr = Field(
        ..., description="User email address", example="harshith@cloudsentinel.ai"
    )
    password: str = Field(
        ..., min_length=8, description="User password (min 8 chars)", example="SecurePassword123!"
    )
    full_name: str = Field(
        "Harshith Lead", description="User full display name", example="Harshith"
    )
    role: UserRole = Field(UserRole.ANALYST, description="RBAC user role")


class LoginRequest(BaseModel):
    """User login payload."""

    username: str = Field(
        ..., description="User email or username", example="harshith@cloudsentinel.ai"
    )
    password: str = Field(..., description="User password", example="SecurePassword123!")


class TokenResponse(BaseModel):
    """JWT Access and Refresh token response."""

    access_token: str = Field(
        ...,
        description="Signed JWT access token",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    )
    refresh_token: str = Field(
        ...,
        description="Signed JWT refresh token",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    )
    token_type: str = Field("bearer", description="Token type", example="bearer")
    expires_in: int = Field(3600, description="Access token expiration in seconds", example=3600)


class RefreshTokenRequest(BaseModel):
    """Refresh token payload."""

    refresh_token: str = Field(
        ..., description="Valid JWT refresh token", example="eyJhbGciOiJIUzI1Ni..."
    )


class UserResponse(BaseModel):
    """Public user profile response."""

    id: str = Field(..., description="Unique user identifier", example="usr_01j8k9")
    email: str = Field(..., description="User email address", example="harshith@cloudsentinel.ai")
    full_name: str = Field(..., description="User full name", example="Harshith")
    role: UserRole = Field(..., description="Assigned RBAC role", example="analyst")
    is_active: bool = Field(True, description="Account active status", example=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
