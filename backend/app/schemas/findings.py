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
    ai_explanation: str | None = Field(
        None,
        description="AI-generated contextual explanation from Bedrock",
        example="This finding exposes...",
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


class FindingUpdateRequest(BaseModel):
    """Payload for the finding PATCH endpoint (roadmap task 12)."""

    status: str = Field(
        ...,
        description="New lifecycle status: `resolved` or `open`",
        example="resolved",
        pattern="^(resolved|open)$",
    )


class FindingListResponse(BaseModel):
    """Paginated list of findings."""

    total: int = Field(..., description="Total matching findings count", example=42)
    page: int = Field(1, description="Current page number", example=1)
    limit: int = Field(50, description="Items per page", example=50)
    findings: list[FindingResponse] = Field(default_factory=list, description="List of findings")


class FindingExplainResponse(BaseModel):
    """AI-powered natural language explanation and remediation playbook."""

    finding_id: str = Field(..., description="Finding ID", example="fnd_123")
    explanation: str = Field(..., description="Contextual analysis and attack implications")
    remediation_steps: list[str] = Field(
        default_factory=list, description="Ordered step-by-step mitigation actions"
    )
    provider: str = Field("bedrock", description="AI provider used", example="bedrock")
    model: str = Field("us.anthropic.claude-haiku-4-5-20251001-v1:0", description="LLM model ID")
    tokens_used: int = Field(0, description="Total prompt and completion tokens")


class ComplianceControlStatus(BaseModel):
    """Individual CIS benchmark control status."""

    control_id: str = Field(..., description="Control identifier (e.g. 1.5, 2.1.5)")
    framework: str = Field("CIS AWS Benchmark v1.5", description="Compliance standard")
    description: str = Field(..., description="Requirement description")
    status: str = Field("PASSED", description="Control status: PASSED or FAILED")
    severity: str = Field("MEDIUM", description="Control severity if failing")


class ComplianceReportResponse(BaseModel):
    """Overall compliance assessment report."""

    framework: str = Field("CIS AWS Benchmark v1.5", description="Framework evaluated")
    compliance_score: float = Field(
        ..., description="Overall compliance pass percentage (0-100%)", example=85.0
    )
    compliance_percentage: float | None = Field(
        None, description="Alias for compliance_score", example=85.0
    )
    total_controls: int = Field(..., description="Total controls evaluated", example=20)
    passed_controls: int = Field(..., description="Passed controls count", example=17)
    failed_controls: int = Field(..., description="Failed controls count", example=3)
    controls: list[ComplianceControlStatus] = Field(
        default_factory=list, description="Control status breakdown"
    )


__all__ = [
    "FindingResponse",
    "FindingStatsResponse",
    "FindingUpdateRequest",
    "FindingListResponse",
    "FindingExplainResponse",
    "ComplianceControlStatus",
    "ComplianceReportResponse",
]
