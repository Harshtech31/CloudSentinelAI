"""
Executive security dashboard endpoints for OpenAPI docs.
"""

from fastapi import APIRouter, status

from app.schemas.dashboard import DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Executive Dashboard Summary",
    description="Returns high-level posture metrics including overall security score, scanned assets, and active attack paths.",
)
async def get_dashboard_summary() -> DashboardSummaryResponse:
    """Get high level dashboard posture summary (Scaffold stub)."""
    return DashboardSummaryResponse(
        security_score=100.0,
        scanned_resources=0,
        total_findings=0,
        critical_findings=0,
        attack_paths_identified=0,
    )
