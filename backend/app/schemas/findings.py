"""
Security findings schemas for OpenAPI docs.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.core.constants import Severity


class FindingResponse(BaseModel):
    """Single security misconfiguration finding model."""

    id: str = Field(..., description="Unique finding identifier", example="fnd_01j7b9")
    scan_id: str = Field(..., description="Associated scan identifier", example="scn_83f12a9c")
    rule_id: str = Field(..., description="Identifier of the rule violated", example="AWS-IAM-001")
    title: str = Field(
        ..., description="Short finding summary", example="Root account MFA is disabled"
    )
    description: str = Field(
        ...,
        description="Detailed description of misconfiguration",
        example="The root account has console access enabled without multi-factor authentication.",
    )
    severity: Severity = Field(..., description="Vulnerability severity level", example="critical")
    risk_score: float = Field(..., description="Calculated risk score (0.0 - 10.0)", example=9.5)
    resource_type: str = Field(..., description="Cloud resource type", example="iam_user")
    resource_arn: str = Field(
        ...,
        description="Resource Amazon Resource Name or ID",
        example="arn:aws:iam::123456789012:root",
    )
    region: str = Field(
        "global", description="Cloud region of affected resource", example="us-east-1"
    )
    remediation_guidance: str = Field(
        "",
        description="Recommended remediation action",
        example="Enable hardware or virtual MFA for the AWS root account.",
    )
    status: str = Field("open", description="Finding lifecycle status", example="open")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Detection timestamp")


class FindingStatsResponse(BaseModel):
    """Aggregated finding counts grouped by severity."""

    critical: int = Field(0, description="Count of critical findings", example=2)
    high: int = Field(0, description="Count of high findings", example=5)
    medium: int = Field(0, description="Count of medium findings", example=8)
    low: int = Field(0, description="Count of low findings", example=3)
    info: int = Field(0, description="Count of info findings", example=1)
    total: int = Field(0, description="Total active findings", example=19)


class FindingListResponse(BaseModel):
    """Paginated list of findings."""

    total: int = Field(..., description="Total matching findings count", example=42)
    page: int = Field(1, description="Current page number", example=1)
    limit: int = Field(50, description="Items per page", example=50)
    findings: list[FindingResponse] = Field(default_factory=list, description="List of findings")
