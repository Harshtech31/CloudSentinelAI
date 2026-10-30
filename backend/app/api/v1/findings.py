"""
Security findings API endpoints for CloudSentinel AI.

Database-backed findings API: paginated listing with severity/scan/status filters,
single-finding detail, resolve/reopen transitions, CIS compliance report,
and AI-powered explanation and remediation generation via Amazon Bedrock.
"""

from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.ai.explain import explain_finding
from app.analyzers.compliance import CIS_BENCHMARK_CONTROLS
from app.api.dependencies import get_current_user
from app.core.constants import Severity
from app.core.exceptions import ResourceNotFoundError
from app.database.models import Finding, Scan, User
from app.database.repositories import FindingRepository, ScanRepository
from app.database.session import get_db
from app.schemas.findings import (
    ComplianceControlStatus,
    ComplianceReportResponse,
    FindingExplainResponse,
    FindingListResponse,
    FindingResponse,
    FindingStatsResponse,
    FindingUpdateRequest,
)

router = APIRouter(prefix="/findings", tags=["Findings"])

MAX_PAGE_LIMIT = 200

# Mapping of core CIS control descriptions
CIS_CONTROL_DESCRIPTIONS = {
    "1.4": "Ensure access keys are rotated every 90 days or less",
    "1.5": "Ensure MFA is enabled for all IAM users with console access",
    "1.16": "Ensure IAM policies that allow full '*:*' administrative privileges are restricted",
    "2.1.1": "Ensure all S3 buckets employ default server-side encryption",
    "2.1.3": "Ensure S3 bucket server access logging is enabled",
    "2.1.4": "Ensure S3 bucket object versioning is enabled",
    "2.1.5": "Ensure S3 Block Public Access setting is enabled for all buckets",
    "2.2.1": "Ensure EBS volume encryption is enabled by default",
    "2.3.1": "Ensure RDS database storage encryption is enabled at rest",
    "2.3.2": "Ensure RDS database instances are not publicly accessible",
    "3.1": "Ensure CloudTrail is enabled across all AWS regions",
    "3.2": "Ensure CloudTrail log file validation is enabled",
    "3.5": "Ensure AWS Config recording is enabled in all regions",
    "4.1": "Ensure no security group permits ingress from 0.0.0.0/0 to port 22",
    "4.2": "Ensure no security group permits ingress from 0.0.0.0/0 to port 3389",
    "4.3": "Ensure no security group allows unrestricted ingress traffic",
    "4.4": "Ensure the default VPC is not used for production workloads",
    "4.5": "Ensure subnets do not automatically assign public IP addresses",
    "5.1": "Ensure Network ACLs restrict unauthorized network traffic",
    "5.2": "Ensure VPC flow logs are active in all VPCs",
}


def _to_response(finding: Finding) -> FindingResponse:
    """Map a Finding row onto the API schema."""
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
    description="Paginated misconfiguration findings across the user's scans.",
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
    """List findings visible to the current user."""
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
    """Severity aggregation."""
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
    "/compliance-report",
    response_model=ComplianceReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get CIS Compliance Report",
    description="Calculates compliance score and control-by-control pass/fail breakdown against CIS AWS Benchmark v1.5.",
)
async def get_compliance_report(
    scan_id: str | None = Query(None, description="Optional scan ID filter"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ComplianceReportResponse:
    """Evaluate and return CIS AWS Benchmark compliance breakdown."""
    rows, _ = _query_findings(
        db,
        user,
        severity=None,
        scan_id=scan_id,
        status_filter="open",
        page=1,
        limit=500,
    )

    # Detect failing controls from open findings
    failing_controls: set[str] = set()
    rule_map = {
        "AWS-IAM-001": "1.5",
        "AWS-IAM-002": "1.16",
        "AWS-IAM-003": "1.4",
        "AWS-S3-001": "2.1.5",
        "AWS-S3-002": "2.1.4",
        "AWS-S3-003": "2.1.3",
        "AWS-ENC-001": "2.3.1",
        "AWS-ENC-002": "2.1.1",
        "AWS-ENC-003": "2.3.2",
        "AWS-CIS-3.1": "3.1",
        "AWS-CIS-3.2": "3.2",
        "AWS-CIS-3.5": "3.5",
        "AWS-NET-001": "4.1",
        "AWS-NET-002": "4.2",
        "AWS-NET-003": "4.3",
        "AWS-NET-004": "4.4",
        "AWS-NET-005": "4.5",
    }

    for f in rows:
        ctrl = rule_map.get(f.rule_id)
        if ctrl:
            failing_controls.add(ctrl)

    controls: list[ComplianceControlStatus] = []
    for cid in CIS_BENCHMARK_CONTROLS:
        is_failing = cid in failing_controls
        desc = CIS_CONTROL_DESCRIPTIONS.get(cid, f"CIS Control {cid}")
        controls.append(
            ComplianceControlStatus(
                control_id=cid,
                framework="CIS AWS Benchmark v1.5",
                description=desc,
                status="FAILED" if is_failing else "PASSED",
                severity="HIGH" if cid in ["1.5", "1.16", "2.1.5", "3.1", "4.1", "4.2"] else "MEDIUM",
            )
        )

    total_controls = len(CIS_BENCHMARK_CONTROLS)
    failed_count = len(failing_controls)
    passed_count = total_controls - failed_count
    score = round((passed_count / total_controls) * 100.0, 1)

    return ComplianceReportResponse(
        framework="CIS AWS Benchmark v1.5",
        compliance_score=score,
        total_controls=total_controls,
        passed_controls=passed_count,
        failed_controls=failed_count,
        controls=controls,
    )


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
    """Single finding detail."""
    finding = _finding_for_user(db, finding_id, user)
    return _to_response(finding)


@router.post(
    "/{finding_id}/explain",
    response_model=FindingExplainResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate AI Finding Explanation",
    description="Invokes Amazon Bedrock (Claude Haiku 4.5) to produce contextual risk analysis and step-by-step mitigation.",
)
async def explain_single_finding(
    finding_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FindingExplainResponse:
    """Generate LLM contextual explanation for a security finding."""
    finding = _finding_for_user(db, finding_id, user)

    finding_facts: dict[str, Any] = {
        "id": finding.id,
        "rule_id": finding.rule_id,
        "title": finding.title,
        "description": finding.description,
        "severity": finding.severity.value if hasattr(finding.severity, "value") else str(finding.severity),
        "resource_type": finding.resource_type,
        "resource_id": finding.resource_id,
        "resource_arn": finding.resource_arn,
        "region": finding.region or "global",
        "remediation_guidance": finding.remediation or "",
    }

    explanation = explain_finding(finding_facts, audience="analyst")

    # Extract bullet points as structured remediation steps
    raw_steps = [
        line.strip().lstrip("-*123456789. ")
        for line in explanation.text.split("\n")
        if line.strip().startswith(("-", "*", "1.", "2.", "3.", "4.", "5."))
    ]
    if not raw_steps:
        raw_steps = [
            f"Review the configuration of {finding.resource_id} against rule {finding.rule_id}.",
            f"Apply the recommended remediation: {finding.remediation or 'Scope permissions according to least privilege.'}",
            "Re-run CloudSentinel AI scan to verify resolution.",
        ]

    return FindingExplainResponse(
        finding_id=finding.id,
        explanation=explanation.text,
        remediation_steps=raw_steps[:10],
        provider=explanation.provider,
        model=explanation.model,
        tokens_used=explanation.tokens_used,
    )


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
    """Resolve/reopen transition."""
    finding = _finding_for_user(db, finding_id, user)
    repo = FindingRepository(db)
    if payload.status == "resolved":
        finding = repo.resolve(finding)
    else:
        finding = repo.reopen(finding)
    return _to_response(finding)


__all__ = ["router"]
