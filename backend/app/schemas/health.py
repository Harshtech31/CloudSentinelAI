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
