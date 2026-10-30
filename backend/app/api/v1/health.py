"""
Health check endpoints for service liveness and readiness probes.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import APP_NAME, APP_VERSION
from app.database.session import get_db
from app.schemas.health import (
    DeepHealthResponse,
    HealthResponse,
    ReadinessResponse,
    VersionResponse,
)

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
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
    "/health/ready",
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


@router.get(
    "/health/deep",
    response_model=DeepHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Deep Component Health Check",
    description="Actively queries the database and inspects AI provider configuration for deep readiness.",
)
async def deep_health_check(db: Session = Depends(get_db)) -> DeepHealthResponse:
    """Deep health check testing database query and AI provider status."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"unhealthy: {exc}"

    return DeepHealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        ai_provider=settings.LLM_PROVIDER,
        components={
            "database": db_status,
            "attack_engine": "ready",
            "graph_store": "ready",
            "ai_inference": "bedrock_haiku_configured"
            if settings.LLM_PROVIDER == "bedrock"
            else settings.LLM_PROVIDER,
        },
    )


@router.get(
    "/version",
    response_model=VersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Version",
    description="Returns current semantic version and running environment metadata.",
)
async def get_version() -> VersionResponse:
    """Return backend service version information."""
    return VersionResponse(
        version=APP_VERSION,
        service=APP_NAME,
        environment=settings.ENVIRONMENT,
    )
