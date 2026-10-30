"""
Executive security dashboard endpoints for CloudSentinel AI.

Database-backed dashboard summary, historical posture trends, and prioritized
top security risks for the authenticated user.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.constants import Severity
from app.database.models import Finding, Scan, User
from app.database.repositories import FindingRepository, ScanRepository
from app.database.session import get_db
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    DashboardTrendsResponse,
    TopRiskItem,
    TopRisksResponse,
    TrendPoint,
)
from app.services.graph_service import graph_store

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

_SEVERITY_PENALTY = {
    Severity.CRITICAL: 10.0,
    Severity.HIGH: 5.0,
    Severity.MEDIUM: 2.0,
    Severity.LOW: 0.5,
    Severity.INFO: 0.0,
}


def security_score(counts: dict[str, int], completed_scans: int) -> float:
    """100 minus severity penalties, normalized per completed scan."""
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
        "score, scanned resources, finding counts, and detected attack paths."
    ),
)
async def get_dashboard_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardSummaryResponse:
    """Aggregate posture summary across the user's scans."""
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
    attack_paths_count = graph_store.get_stats().attack_paths_count

    return DashboardSummaryResponse(
        security_score=security_score(counts, completed_scans),
        scanned_resources=int(resources_scanned),
        total_findings=counts["total"],
        critical_findings=counts["critical"],
        attack_paths_identified=attack_paths_count,
    )


@router.get(
    "/trends",
    response_model=DashboardTrendsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Historical Posture Trends",
    description="Returns security posture score and finding volume trends over historical scans.",
)
async def get_dashboard_trends(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardTrendsResponse:
    """Fetch posture trends over the user's completed scans."""
    scans = db.scalars(
        select(Scan)
        .where(Scan.user_id == user.id, Scan.status == "completed")
        .order_by(Scan.created_at.asc())
        .limit(10)
    ).all()

    points: list[TrendPoint] = []

    for scan in scans:
        findings_count = (
            db.scalar(select(func.count()).select_from(Finding).where(Finding.scan_id == scan.id))
            or 0
        )
        crit_count = (
            db.scalar(
                select(func.count())
                .select_from(Finding)
                .where(Finding.scan_id == scan.id, Finding.severity == Severity.CRITICAL)
            )
            or 0
        )
        date_str = scan.created_at.strftime("%Y-%m-%d") if scan.created_at else "2026-10-30"

        penalty = crit_count * 10.0 + (findings_count - crit_count) * 2.0
        score = max(0.0, round(100.0 - penalty, 1))

        points.append(
            TrendPoint(
                date=date_str,
                security_score=score,
                total_findings=findings_count,
                critical_findings=crit_count,
            )
        )

    if not points:
        # Default baseline point if no scans run yet
        points.append(
            TrendPoint(
                date="Today",
                security_score=100.0,
                total_findings=0,
                critical_findings=0,
            )
        )

    return DashboardTrendsResponse(trends=points)


@router.get(
    "/top-risks",
    response_model=TopRisksResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Top Priority Security Risks",
    description="Returns the highest risk active findings for the user, sorted by risk severity.",
)
async def get_top_risks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TopRisksResponse:
    """Fetch top priority critical and high findings."""
    query = (
        select(Finding)
        .join(Scan, Finding.scan_id == Scan.id)
        .where(Scan.user_id == user.id, Finding.status == "open")
        .order_by(desc(Finding.risk_score), desc(Finding.created_at))
        .limit(10)
    )
    findings = db.scalars(query).all()

    items = [
        TopRiskItem(
            id=f.id,
            rule_id=f.rule_id,
            title=f.title,
            severity=str(f.severity.value if hasattr(f.severity, "value") else f.severity),
            risk_score=f.risk_score,
            resource_type=f.resource_type,
            resource_id=f.resource_id,
            region=f.region or "global",
        )
        for f in findings
    ]

    return TopRisksResponse(top_risks=items)


__all__ = ["router", "security_score"]
