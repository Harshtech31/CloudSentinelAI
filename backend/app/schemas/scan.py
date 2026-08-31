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
