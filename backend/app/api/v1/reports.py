"""
Security assessment report export endpoints for OpenAPI docs.
"""

from fastapi import APIRouter, status

from app.schemas.reports import (
    ReportGenerateRequest,
    ReportListResponse,
    ReportResponse,
)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post(
    "/generate",
    response_model=ReportResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger Report Generation",
    description="Compiles an assessment report in PDF, HTML, JSON, or CSV format with contextual AI explanations.",
)
async def generate_report(payload: ReportGenerateRequest) -> ReportResponse:
    """Trigger report generation in JSON, CSV, HTML, or PDF (Scaffold stub)."""
    return ReportResponse(
        id="rep_01k9m2",
        scan_id=payload.scan_id,
        format=payload.format,
        download_url="/api/v1/reports/rep_01k9m2/download",
        file_size_bytes=0,
    )


@router.get(
    "/{report_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Download Generated Report File",
    description="Streams or downloads the generated assessment report file.",
)
async def download_report(report_id: str):
    """Download generated report artifact (Scaffold stub)."""
    return {"report_id": report_id, "status": "ready", "download": "placeholder"}


@router.get(
    "",
    response_model=ReportListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Generated Security Reports",
    description="Returns list of previously generated export reports for the user or organization.",
)
async def list_reports() -> ReportListResponse:
    """List generated security reports (Scaffold stub)."""
    return ReportListResponse(reports=[])
