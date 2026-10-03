"""
Cloud Scan management endpoints.

Database-backed scan API (roadmap_part2_core_pipeline.md tasks 6-9, 18-19,
Member 1 track). `POST /scan/start` creates the scan row and enqueues the
orchestrator as a FastAPI BackgroundTask; the other endpoints read and
transition the row through the repositories.

Ownership rule: users see and cancel their own scans; admins see all.
The one-concurrent-scan-per-user rule returns 409 (roadmap task 18).
"""

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_current_user
from app.core.constants import ScanStatus
from app.core.exceptions import (
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)
from app.database.models import User
from app.database.repositories import FindingRepository, ScanRepository
from app.database.session import get_db
from app.schemas.scan import (
    ScanListItemResponse,
    ScanListResponse,
    ScanResultsResponse,
    ScanStartRequest,
    ScanStatusResponse,
    ScanSummaryResponse,
    scan_to_list_item,
)
from app.tasks.scan_task import run_scan_task

router = APIRouter(prefix="/scan", tags=["Scans"])

_ACTIVE = (ScanStatus.PENDING, ScanStatus.RUNNING)


def _get_scan_or_404(db: Session, scan_id: str, user: User):
    """Fetch a scan the user may access (owner or admin) or raise 404.

    A 404 — not a 403 — for other users' scans avoids leaking scan ids.
    """
    scan = ScanRepository(db).get(scan_id)
    if scan is None:
        raise ResourceNotFoundError(f"Scan {scan_id} not found")
    if user.role != "admin" and scan.user_id != user.id:
        raise ResourceNotFoundError(f"Scan {scan_id} not found")
    return scan


def _summary_for(db: Session, scan) -> ScanSummaryResponse:
    counts = FindingRepository(db).count_by_severity(scan_id=scan.id)
    return ScanSummaryResponse(
        scan_id=scan.id,
        status=scan.status,
        total_findings=counts["total"],
        critical_findings=counts["critical"],
        high_findings=counts["high"],
        attack_paths_count=0,  # attack-path extraction is the Lead's Phase 2 wire-up
    )


@router.post(
    "/start",
    response_model=ScanStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Initiate Cloud Security Scan",
    description=(
        "Create a scan row and start the collection pipeline in the "
        "background. Limited to one active (pending/running) scan per user."
    ),
)
async def start_scan(
    payload: ScanStartRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScanStatusResponse:
    """Create a PENDING scan and enqueue the orchestrator (roadmap task 6)."""
    repos = ScanRepository(db)
    if repos.has_active_scan(user.id):
        raise ResourceAlreadyExistsError(
            "You already have a scan in progress. Wait for it to finish or cancel it."
        )

    scan = repos.create(
        user_id=user.id,
        target_cloud=payload.target_cloud,
        regions=payload.regions,
        services=payload.services,
    )
    # The task must hit the SAME database as this request — derive the
    # session factory from the injected session's bind instead of the
    # global SessionLocal (identical in production, decisive in tests).
    task_session_factory = sessionmaker(bind=db.get_bind(), autoflush=False, expire_on_commit=False)
    background_tasks.add_task(run_scan_task, scan.id, session_factory=task_session_factory)
    return ScanStatusResponse(
        scan_id=scan.id,
        status=scan.status,
        target_cloud=scan.target_cloud,
        created_at=scan.created_at,
        progress_percentage=scan.progress_percentage,
    )


@router.get(
    "",
    response_model=ScanListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Scans for Current User",
    description="Paginated scans belonging to the authenticated user, newest first.",
)
async def list_scans(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScanListResponse:
    """List the current user's scans (roadmap task 9)."""
    rows, total = ScanRepository(db).list_for_user(user.id, page=page, limit=limit)
    return ScanListResponse(
        total=total,
        page=page,
        limit=limit,
        scans=[scan_to_list_item(row) for row in rows],
    )


@router.get(
    "/{scan_id}/status",
    response_model=ScanStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Poll Scan Execution Status",
    description="Real-time execution progress of an active scan (frontend polling target).",
)
async def get_scan_status(
    scan_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScanStatusResponse:
    """Current status of a scan (roadmap task 7)."""
    scan = _get_scan_or_404(db, scan_id, user)
    return ScanStatusResponse(
        scan_id=scan.id,
        status=scan.status,
        target_cloud=scan.target_cloud,
        created_at=scan.created_at,
        progress_percentage=scan.progress_percentage,
    )


@router.get(
    "/{scan_id}/summary",
    response_model=ScanSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Scan Summary Metrics",
    description="Aggregate finding metrics for a scan.",
)
async def get_scan_summary(
    scan_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScanSummaryResponse:
    """Summary metrics for a scan."""
    scan = _get_scan_or_404(db, scan_id, user)
    return _summary_for(db, scan)


@router.get(
    "/{scan_id}/results",
    response_model=ScanResultsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Scan Results",
    description="Scan row plus aggregate finding metrics (roadmap task 8).",
)
async def get_scan_results(
    scan_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScanResultsResponse:
    """Full result payload for one scan."""
    scan = _get_scan_or_404(db, scan_id, user)
    return ScanResultsResponse(scan=scan_to_list_item(scan), summary=_summary_for(db, scan))


@router.delete(
    "/{scan_id}",
    status_code=status.HTTP_200_OK,
    summary="Cancel a Scan",
    description="Cancel a pending or running scan. Finished scans cannot be cancelled.",
)
async def cancel_scan(
    scan_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScanListItemResponse:
    """Cooperative cancellation — flips the row; the task checks between stages (task 19)."""
    repos = ScanRepository(db)
    scan = _get_scan_or_404(db, scan_id, user)
    if scan.status not in _ACTIVE:
        raise ResourceAlreadyExistsError(
            f"Scan {scan_id} is already {scan.status.value}; it cannot be cancelled."
        )
    repos.mark_cancelled(scan)
    return scan_to_list_item(scan)
