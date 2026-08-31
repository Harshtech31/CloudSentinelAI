"""
Report generation and export schemas for OpenAPI docs.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.core.constants import ReportFormat


class ReportGenerateRequest(BaseModel):
    """Payload to trigger security report compilation."""

    scan_id: str = Field(
        ..., description="Target scan ID to generate report for", example="scn_83f12a9c"
    )
    format: ReportFormat = Field(
        ReportFormat.PDF, description="Export format (pdf, html, json, csv)"
    )
    include_ai_explanations: bool = Field(
        True, description="Include LLM remediation guidance in report"
    )


class ReportResponse(BaseModel):
    """Generated report metadata."""

    id: str = Field(..., description="Unique report identifier", example="rep_01k9m2")
    scan_id: str = Field(..., description="Associated scan identifier", example="scn_83f12a9c")
    format: ReportFormat = Field(..., description="Report format", example="pdf")
    download_url: str = Field(
        ..., description="API download URL", example="/api/v1/reports/rep_01k9m2/download"
    )
    file_size_bytes: int = Field(0, description="Generated file size in bytes", example=248000)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Generation timestamp"
    )


class ReportListResponse(BaseModel):
    """List of generated reports."""

    reports: list[ReportResponse] = Field(default_factory=list, description="List of reports")
