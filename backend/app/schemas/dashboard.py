"""
Executive dashboard schemas for OpenAPI docs.
"""

from pydantic import BaseModel, Field


class DashboardSummaryResponse(BaseModel):
    """Executive security dashboard posture summary."""

    security_score: float = Field(
        ..., description="Overall cloud security score (0-100)", example=87.5
    )
    scanned_resources: int = Field(..., description="Total cloud assets scanned", example=142)
    total_findings: int = Field(..., description="Total active misconfigurations", example=15)
    critical_findings: int = Field(..., description="Critical severity findings count", example=2)
    attack_paths_identified: int = Field(
        ..., description="Total exploitable attack chains detected", example=3
    )


class TrendPoint(BaseModel):
    """Data point in security posture trend timeline."""

    date: str = Field(..., description="Date or scan timestamp", example="2026-10-30")
    security_score: float = Field(..., description="Score on that date", example=92.0)
    total_findings: int = Field(..., description="Total active findings", example=12)
    critical_findings: int = Field(..., description="Critical findings count", example=2)


class DashboardTrendsResponse(BaseModel):
    """Historical security posture score and finding trends."""

    trends: list[TrendPoint] = Field(default_factory=list, description="Chronological trend points")


class TopRiskItem(BaseModel):
    """Highest risk security finding."""

    id: str = Field(..., description="Finding ID", example="fnd_123")
    rule_id: str = Field(..., description="Security rule ID", example="AWS-NET-001")
    title: str = Field(..., description="Finding headline", example="Security Group Open SSH")
    severity: str = Field(..., description="Severity level", example="CRITICAL")
    risk_score: float = Field(..., description="Contextual risk score", example=9.5)
    resource_type: str = Field(..., description="Cloud resource type", example="AWS::EC2::SecurityGroup")
    resource_id: str = Field(..., description="Resource ID", example="sg-0123")
    region: str = Field("global", description="AWS region", example="us-east-1")


class TopRisksResponse(BaseModel):
    """Top priority security risks requiring immediate remediation."""

    top_risks: list[TopRiskItem] = Field(default_factory=list, description="Ranked critical findings")


__all__ = [
    "DashboardSummaryResponse",
    "TrendPoint",
    "DashboardTrendsResponse",
    "TopRiskItem",
    "TopRisksResponse",
]
