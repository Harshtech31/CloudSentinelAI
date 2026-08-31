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
