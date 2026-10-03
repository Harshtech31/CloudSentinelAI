"""
Security findings API endpoints.

Database-backed findings API (roadmap_part2_core_pipeline.md tasks 10-13,
Member 1 track): paginated listing with severity/scan/status filters,
single-finding detail, resolve/reopen transitions, and severity stats.
Every read is tenant-scoped by scan ownership — findings inherit the
scan's user.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.constants import Severity
from app.core.exceptions import ResourceNotFoundError
from app.database.models import Finding, Scan, User
from app.database.repositories import FindingRepository, ScanRepository
from app.database.session import get_db
from app.schemas.findings import (
    FindingListResponse,
    FindingResponse,
    FindingStatsResponse,
    FindingUpdateRequest,
)

router = APIRouter(prefix="/findings", tags=["Findings"])

MAX_PAGE_LIMIT = 200


def _to_response(finding: Finding) -> FindingResponse:
    """Map a Finding row onto the API schema (arn is required by contract)."""
    return FindingResponse(
        id=finding.id,
        scan_id=finding.scan_id,
        rule_id=finding.rule_id,
        title=finding.title,
        description=finding.description,
        severity=finding.severity,
        risk_score=finding.risk_score,
        resource_type=finding.resource_type,
        resource_arn=finding.resource_arn or finding.resource_id,
        region=finding.region or "global",
        remediation_guidance=finding.remediation or "",
        status=finding.status,
        created_at=finding.created_at,
    )


def _finding_for_user(db: Session, finding_id: str, user: User) -> Finding:
    """Fetch a finding whose parent scan belongs to the user (or admin)."""
    finding = FindingRepository(db).get(finding_id)
    if finding is None:
        raise ResourceNotFoundError(f"Finding {finding_id} not found")
    scan = ScanRepository(db).get(finding.scan_id)
    if scan is None or (user.role != "admin" and scan.user_id != user.id):
        # Same anti-enumeration rule as scans: 404, never 403.
        raise ResourceNotFoundError(f"Finding {finding_id} not found")
    return finding


def _query_findings(
    db: Session,
    user: User,
    *,
    severity: Severity | None,
    scan_id: str | None,
    status_filter: str | None,
    page: int,
    limit: int,
) -> tuple[list[Finding], int]:
    """Findings listing scoped to scans the user owns (admins see all)."""
    repo = FindingRepository(db)
    if user.role == "admin":
        return repo.list_paginated(
            scan_id=scan_id,
            severity=severity,
            status=status_filter,
            page=page,
            limit=limit,
        )
    owned_scan_ids = {scan.id for scan in db.query(Scan).filter(Scan.user_id == user.id).all()}
    if scan_id is not None:
        if scan_id not in owned_scan_ids:
            return [], 0
        return repo.list_paginated(
            scan_id=scan_id,
            severity=severity,
            status=status_filter,
            page=page,
            limit=limit,
        )
    # All scans owned by the user: filter client-side per scan is O(scans)
    # queries; with pagination the pragmatic path is one filter per scan
    # merged in memory. Accounts stay small (per-user scans), so this is fine.
    merged: list[Finding] = []
    total = 0
    for owned_id in owned_scan_ids:
        rows, row_total = repo.list_paginated(
            scan_id=owned_id,
            severity=severity,
            status=status_filter,
            page=1,
            limit=MAX_PAGE_LIMIT,
        )
        merged.extend(rows)
        total += row_total
    merged.sort(key=lambda f: (f.created_at, f.id), reverse=True)
    start = (page - 1) * limit
    return merged[start : start + limit], total


@router.get(
    "",
    response_model=FindingListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Security Findings",
    description=(
        "Paginated misconfiguration findings across the user's scans, "
        "filterable by severity, scan, and lifecycle status."
    ),
)
async def list_findings(
    severity: Severity | None = Query(None, description="Filter by severity level"),
    scan_id: str | None = Query(None, description="Filter by scan"),
    status_filter: str | None = Query(
        None, alias="status", description="Filter by lifecycle status"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FindingListResponse:
    """List findings visible to the current user (roadmap task 10)."""
    rows, total = _query_findings(
        db,
        user,
        severity=severity,
        scan_id=scan_id,
        status_filter=status_filter,
        page=page,
        limit=limit,
    )
    return FindingListResponse(
        total=total,
        page=page,
        limit=limit,
        findings=[_to_response(row) for row in rows],
    )


@router.get(
    "/stats/summary",
    response_model=FindingStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Finding Severity Statistics",
    description="Finding counts grouped by severity across the user's scans.",
)
async def get_findings_stats(
    scan_id: str | None = Query(None, description="Scope stats to one scan"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FindingStatsResponse:
    """Severity aggregation (roadmap task 13)."""
    repo = FindingRepository(db)
    if user.role == "admin" or scan_id is not None:
        counts = repo.count_by_severity(scan_id=scan_id)
    else:
        counts = {sev.value: 0 for sev in Severity}
        counts["total"] = 0
        for owned in db.query(Scan).filter(Scan.user_id == user.id).all():
            scan_counts = repo.count_by_severity(scan_id=owned.id)
            for key in counts:
                if key == "total":
                    continue
                counts[key] += scan_counts.get(key, 0)
                counts["total"] += scan_counts.get(key, 0)
    return FindingStatsResponse(**counts)


@router.get(
    "/{finding_id}",
    response_model=FindingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Single Finding Detail",
    description="Full finding detail including description and remediation guidance.",
)
async def get_finding(
    finding_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FindingResponse:
    """Single finding detail (roadmap task 11)."""
    finding = _finding_for_user(db, finding_id, user)
    return _to_response(finding)


@router.patch(
    "/{finding_id}",
    response_model=FindingResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Finding Status",
    description="Mark a finding resolved, or reopen a resolved one.",
)
async def update_finding(
    finding_id: str,
    payload: FindingUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FindingResponse:
    """Resolve/reopen transition (roadmap task 12)."""
    finding = _finding_for_user(db, finding_id, user)
    repo = FindingRepository(db)
    if payload.status == "resolved":
        finding = repo.resolve(finding)
    else:
        finding = repo.reopen(finding)
    return _to_response(finding)
