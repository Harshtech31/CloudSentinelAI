"""
Cloud Scan management endpoints for OpenAPI docs.
"""

from fastapi import APIRouter, status

from app.core.constants import CloudProvider, ScanStatus
from app.schemas.scan import (
    ScanStartRequest,
    ScanStatusResponse,
    ScanSummaryResponse,
)

router = APIRouter(prefix="/scan", tags=["Scans"])


@router.post(
    "/start",
    response_model=ScanStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Initiate Cloud Security Scan",
    description="Trigger an automated multi-cloud configuration collection and security evaluation.",
)
async def start_scan(payload: ScanStartRequest) -> ScanStatusResponse:
    """Trigger a new cloud infrastructure security scan (Scaffold stub)."""
    return ScanStatusResponse(
        scan_id="scn_83f12a9c",
        status=ScanStatus.PENDING,
        target_cloud=payload.target_cloud,
        progress_percentage=0,
    )


@router.get(
    "/{scan_id}/status",
    response_model=ScanStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Poll Scan Execution Status",
    description="Check real-time execution progress of an active scan.",
)
async def get_scan_status(scan_id: str) -> ScanStatusResponse:
    """Get current status of a scan (Scaffold stub)."""
    return ScanStatusResponse(
        scan_id=scan_id,
        status=ScanStatus.COMPLETED,
        target_cloud=CloudProvider.AWS,
        progress_percentage=100,
    )


@router.get(
    "/{scan_id}/summary",
    response_model=ScanSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Scan Summary Metrics",
    description="Returns aggregate metric counts for a finished scan.",
)
async def get_scan_summary(scan_id: str) -> ScanSummaryResponse:
    """Get summary metrics for a scan (Scaffold stub)."""
    return ScanSummaryResponse(
        scan_id=scan_id,
        status=ScanStatus.COMPLETED,
        total_findings=0,
        critical_findings=0,
        high_findings=0,
        attack_paths_count=0,
    )
