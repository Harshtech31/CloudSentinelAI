"""
Health and readiness probe schemas for OpenAPI docs.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Liveness probe response model."""

    status: str = Field(..., description="Service health status indicator", example="ok")
    service: str = Field(..., description="Name of the service", example="CloudSentinel AI")
    version: str = Field(..., description="Application version", example="0.1.0")
    environment: str = Field(..., description="Current running environment", example="development")


class ReadinessResponse(BaseModel):
    """Readiness probe response model checking underlying components."""

    status: str = Field(..., description="Overall readiness status", example="ready")
    components: dict[str, str] = Field(
        ...,
        description="Health states of individual sub-engines and connections",
        example={
            "api": "healthy",
            "database": "configured",
            "attack_engine": "ready",
            "graph_engine": "ready",
        },
    )


class DeepHealthResponse(BaseModel):
    """Deep health check response checking DB and AI engine connectivity."""

    status: str = Field(..., description="Overall deep health status", example="healthy")
    database: str = Field(..., description="Database connection status", example="connected")
    ai_provider: str = Field(..., description="Configured AI provider", example="bedrock")
    components: dict[str, str] = Field(
        ...,
        description="Component status dictionary",
    )


class VersionResponse(BaseModel):
    """Application version schema."""

    version: str = Field(..., description="Application version string", example="1.0.0")
    service: str = Field(..., description="Application service name", example="CloudSentinel AI")
    environment: str = Field(..., description="Deployment environment", example="development")
