"""
Executive security dashboard endpoints.

Database-backed dashboard summary (roadmap_part2_core_pipeline.md task 14,
Member 1 track): aggregates the current user's scans and findings into the
posture metrics the DashboardPage renders. Security score follows the
classic CPSM penalty model — start at 100, subtract by severity weight
per completed scan, floor at zero. Attack-path counts report zero until
the Lead's Phase 2 wire-up lands (never fake data).
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.constants import Severity
from app.database.models import Scan, User
from app.database.repositories import FindingRepository, ScanRepository
from app.database.session import get_db
from app.schemas.dashboard import DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

_SEVERITY_PENALTY = {
    Severity.CRITICAL: 10.0,
    Severity.HIGH: 5.0,
    Severity.MEDIUM: 2.0,
    Severity.LOW: 0.5,
    Severity.INFO: 0.0,
}


def security_score(counts: dict[str, int], completed_scans: int) -> float:
    """100 minus severity penalties, normalized per completed scan.

    An account with no completed scans shows a neutral 100.0; findings
    only start costing once there are scans to weigh.
    """
    if completed_scans == 0:
        return 100.0
    total_penalty = sum(
        _SEVERITY_PENALTY.get(Severity(severity), 0.0) * count
        for severity, count in counts.items()
        if severity != "total"
    )
    return round(max(0.0, 100.0 - (total_penalty / completed_scans)), 1)


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Executive Dashboard Summary",
    description=(
        "High-level posture metrics for the authenticated user: security "
        "score, scanned resources, finding counts, and attack paths."
    ),
)
async def get_dashboard_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardSummaryResponse:
    """Aggregate posture summary across the user's scans (roadmap task 14)."""
    scan_repo = ScanRepository(db)
    finding_repo = FindingRepository(db)

    _, scans_total = scan_repo.list_for_user(user.id, page=1, limit=1)
    completed_scans = (
        db.scalar(
            select(func.count())
            .select_from(Scan)
            .where(Scan.user_id == user.id, Scan.status == "completed")
        )
        or 0
    )
    resources_scanned = (
        db.scalar(
            select(func.coalesce(func.sum(Scan.resources_scanned), 0)).where(
                Scan.user_id == user.id
            )
        )
        or 0
    )

    counts = finding_repo.count_by_severity_for_user(user.id)
    return DashboardSummaryResponse(
        security_score=security_score(counts, completed_scans),
        scanned_resources=int(resources_scanned),
        total_findings=counts["total"],
        critical_findings=counts["critical"],
        attack_paths_identified=0,
    )


__all__ = ["router", "security_score"]
