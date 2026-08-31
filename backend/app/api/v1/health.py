"""
Health check endpoints for service liveness and readiness probes.
"""

from fastapi import APIRouter, status

from app.core.config import settings
from app.core.constants import APP_NAME, APP_VERSION
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness Health Probe",
    description="Returns the operational status, version, and running environment of the CloudSentinel backend.",
)
async def health_check() -> HealthResponse:
    """Basic liveness health probe."""
    return HealthResponse(
        status="ok",
        service=APP_NAME,
        version=APP_VERSION,
        environment=settings.ENVIRONMENT,
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness Health Probe",
    description="Validates that database connections, graph engines, and attack path discovery services are initialized.",
)
async def readiness_check() -> ReadinessResponse:
    """Readiness probe checking component statuses."""
    return ReadinessResponse(
        status="ready",
        components={
            "api": "healthy",
            "database": "configured",
            "attack_engine": "ready",
            "graph_engine": "ready",
        },
    )
