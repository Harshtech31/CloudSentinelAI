"""
Cloud scan request and response schemas for OpenAPI docs.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.core.constants import CloudProvider, ScanStatus


class ScanStartRequest(BaseModel):
    """Payload to initiate a new cloud scan."""

    target_cloud: CloudProvider = Field(
        CloudProvider.AWS, description="Target cloud provider to scan"
    )
    regions: list[str] = Field(
        ["us-east-1"], description="List of regions to scan", example=["us-east-1", "us-west-2"]
    )
    services: list[str] = Field(
        ["iam", "ec2", "s3", "vpc", "security_groups", "rds", "cloudtrail"],
        description="Services to collect and analyze",
        example=["iam", "ec2", "s3"],
    )


class ScanStatusResponse(BaseModel):
    """Real-time scan status model."""

    scan_id: str = Field(..., description="Unique scan identifier", example="scn_83f12a9c")
    status: ScanStatus = Field(
        ..., description="Current status of scan execution", example="running"
    )
    target_cloud: CloudProvider = Field(..., description="Target cloud provider", example="aws")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Scan start timestamp"
    )
    progress_percentage: int = Field(0, description="Scan progress (0-100%)", example=50)


class ScanSummaryResponse(BaseModel):
    """Summary metrics of a scan."""

    scan_id: str = Field(..., description="Unique scan identifier", example="scn_83f12a9c")
    status: ScanStatus = Field(..., description="Execution status", example="completed")
    total_findings: int = Field(0, description="Total misconfigurations identified", example=12)
    critical_findings: int = Field(0, description="Critical severity findings count", example=2)
    high_findings: int = Field(0, description="High severity findings count", example=4)
    attack_paths_count: int = Field(0, description="Exploitable attack paths discovered", example=3)


# ---------------------------------------------------------------------------
# Phase 2 additive schemas (roadmap task 15). Existing shapes above are
# unchanged — the frontend API services are written against them.
# ---------------------------------------------------------------------------


class ScanListItemResponse(BaseModel):
    """One scan row as returned in lists and detail views."""

    scan_id: str = Field(..., description="Unique scan identifier", example="scn_83f12a9c")
    status: ScanStatus = Field(..., description="Execution status", example="completed")
    target_cloud: CloudProvider = Field(..., description="Target cloud provider", example="aws")
    regions: list[str] = Field(default_factory=list, description="Regions covered by the scan")
    services: list[str] = Field(default_factory=list, description="Services included in the scan")
    progress_percentage: int = Field(0, description="Scan progress (0-100%)", example=100)
    created_at: datetime = Field(..., description="Scan creation timestamp")
    started_at: datetime | None = Field(None, description="Scan start timestamp")
    completed_at: datetime | None = Field(None, description="Scan completion timestamp")
    duration_seconds: float | None = Field(
        None, description="Wall-clock duration in seconds once started", example=18.4
    )
    error_message: str | None = Field(None, description="Failure reason when status is failed")


class ScanListResponse(BaseModel):
    """Paginated list of the current user's scans."""

    total: int = Field(..., description="Total scans for the user", example=7)
    page: int = Field(1, description="Current page number", example=1)
    limit: int = Field(50, description="Items per page", example=50)
    scans: list[ScanListItemResponse] = Field(
        default_factory=list, description="Scan rows for this page"
    )


class ScanResultsResponse(BaseModel):
    """Full result payload for one completed scan."""

    scan: ScanListItemResponse = Field(..., description="The scan row")
    summary: ScanSummaryResponse = Field(..., description="Aggregate finding metrics")


def scan_to_list_item(scan: object) -> ScanListItemResponse:
    """Map a `Scan` model row onto `ScanListItemResponse`.

    Typed as `object` to keep the schema module import-light; the body
    duck-types the attributes the ORM always provides. Regions/services
    are stored comma-joined and split back into lists here; duration is
    computed from the lifecycle timestamps when both ends exist.
    """
    started_at = getattr(scan, "started_at", None)
    completed_at = getattr(scan, "completed_at", None)
    duration = (
        (completed_at - started_at).total_seconds()
        if started_at is not None and completed_at is not None
        else None
    )
    return ScanListItemResponse(
        scan_id=scan.id,
        status=scan.status,
        target_cloud=scan.target_cloud,
        regions=[r for r in (scan.regions or "").split(",") if r],
        services=[s for s in (scan.services or "").split(",") if s],
        progress_percentage=scan.progress_percentage,
        created_at=scan.created_at,
        started_at=started_at,
        completed_at=completed_at,
        duration_seconds=duration,
        error_message=scan.error_message,
    )
