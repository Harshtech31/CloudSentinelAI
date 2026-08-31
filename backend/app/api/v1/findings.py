"""
Security findings API endpoints for OpenAPI docs.
"""

from fastapi import APIRouter, Query, status

from app.core.constants import Severity
from app.schemas.findings import (
    FindingListResponse,
    FindingResponse,
    FindingStatsResponse,
)

router = APIRouter(prefix="/findings", tags=["Findings"])


@router.get(
    "",
    response_model=FindingListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Security Findings",
    description="Retrieve paginated list of security misconfiguration findings, optionally filtered by severity.",
)
async def list_findings(
    severity: Severity | None = Query(None, description="Filter findings by severity level"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
) -> FindingListResponse:
    """List all detected misconfiguration findings (Scaffold stub)."""
    return FindingListResponse(
        total=0,
        page=page,
        limit=limit,
        findings=[],
    )


@router.get(
    "/stats/summary",
    response_model=FindingStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Finding Severity Statistics",
    description="Aggregates count of all findings broken down by severity level (critical, high, medium, low, info).",
)
async def get_findings_stats() -> FindingStatsResponse:
    """Get finding counts grouped by severity (Scaffold stub)."""
    return FindingStatsResponse(
        critical=0,
        high=0,
        medium=0,
        low=0,
        info=0,
        total=0,
    )


@router.get(
    "/{finding_id}",
    response_model=FindingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Single Finding Detail",
    description="Fetch full finding detail including violation description and remediation instructions.",
)
async def get_finding(finding_id: str) -> FindingResponse:
    """Get single finding detail (Scaffold stub)."""
    return FindingResponse(
        id=finding_id,
        scan_id="scn_83f12a9c",
        rule_id="AWS-IAM-001",
        title="Sample Misconfiguration Finding",
        description="Detailed description placeholder.",
        severity=Severity.HIGH,
        risk_score=7.5,
        resource_type="iam_user",
        resource_arn="arn:aws:iam::123456789012:user/sample",
        region="us-east-1",
        remediation_guidance="Apply least privilege permissions.",
        status="open",
    )
