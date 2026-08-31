"""
Custom domain exceptions and FastAPI global exception handlers.
"""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class CloudSentinelException(Exception):
    """Base exception for CloudSentinel AI domain errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred in CloudSentinel AI.",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(CloudSentinelException):
    """Raised when authentication fails or credentials are invalid."""

    def __init__(
        self,
        message: str = "Invalid authentication credentials.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED, details=details)


class PermissionDeniedError(CloudSentinelException):
    """Raised when a user lacks sufficient permissions for an action."""

    def __init__(self, message: str = "Permission denied.", details: dict[str, Any] | None = None):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN, details=details)


class ResourceNotFoundError(CloudSentinelException):
    """Raised when a requested resource does not exist."""

    def __init__(
        self,
        message: str = "Requested resource was not found.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND, details=details)


class ResourceAlreadyExistsError(CloudSentinelException):
    """Raised when trying to create a resource that already exists."""

    def __init__(
        self, message: str = "Resource already exists.", details: dict[str, Any] | None = None
    ):
        super().__init__(message, status_code=status.HTTP_409_CONFLICT, details=details)


class ValidationError(CloudSentinelException):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation failed.", details: dict[str, Any] | None = None):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, details=details)


class ScanExecutionError(CloudSentinelException):
    """Raised when a cloud collector or scan fails to execute."""

    def __init__(
        self,
        message: str = "Cloud security scan execution failed.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details=details
        )


class GraphBuildError(CloudSentinelException):
    """Raised when building or traversing the security graph fails."""

    def __init__(
        self,
        message: str = "Failed to construct security knowledge graph.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details=details
        )


class AIProviderError(CloudSentinelException):
    """Raised when an AI/LLM provider fails to generate an explanation."""

    def __init__(
        self, message: str = "AI explanation service error.", details: dict[str, Any] | None = None
    ):
        super().__init__(message, status_code=status.HTTP_502_BAD_GATEWAY, details=details)


def setup_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with the FastAPI application."""

    @app.exception_handler(CloudSentinelException)
    async def cloudsentinel_exception_handler(request: Request, exc: CloudSentinelException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "type": exc.__class__.__name__,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )
