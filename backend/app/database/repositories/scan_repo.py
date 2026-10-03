"""
Scan Repository for CloudSentinel AI.

CRUD and lifecycle operations for `Scan` rows (roadmap_part2_core_pipeline.md
task 1, Member 1 track). Repositories own querying and row mutations;
HTTP concerns (status codes, response models) stay in the API layer.

Mutation methods commit immediately: scan rows must be visible to the
background task's separate session the moment the API responds.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.constants import CloudProvider, ScanStatus
from app.database.models import Scan

ACTIVE_STATUSES = (ScanStatus.PENDING, ScanStatus.RUNNING)


class ScanRepository:
    """Database operations for `Scan` rows."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # -- creation -----------------------------------------------------------

    def create(
        self,
        *,
        user_id: str | None,
        target_cloud: CloudProvider = CloudProvider.AWS,
        regions: list[str] | None = None,
        services: list[str] | None = None,
    ) -> Scan:
        """Insert a PENDING scan row and commit it immediately."""
        scan = Scan(
            user_id=user_id,
            target_cloud=target_cloud,
            regions=",".join(regions or ["us-east-1"]),
            services=",".join(services or []),
            status=ScanStatus.PENDING,
        )
        self.db.add(scan)
        self.db.commit()
        self.db.refresh(scan)
        return scan

    # -- reads ---------------------------------------------------------------

    def get(self, scan_id: str) -> Scan | None:
        """Fetch one scan by id, or None."""
        return self.db.get(Scan, scan_id)

    def get_for_user(self, scan_id: str, user_id: str) -> Scan | None:
        """Fetch a scan owned by the given user, or None."""
        scan = self.get(scan_id)
        if scan is None or scan.user_id != user_id:
            return None
        return scan

    def list_for_user(
        self, user_id: str, *, page: int = 1, limit: int = 50
    ) -> tuple[list[Scan], int]:
        """Paginated scans for one user, newest first, with total count."""
        total = self.db.scalar(
            select(func.count()).select_from(Scan).where(Scan.user_id == user_id)
        )
        rows = self.db.scalars(
            select(Scan)
            .where(Scan.user_id == user_id)
            .order_by(Scan.created_at.desc(), Scan.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        ).all()
        return list(rows), int(total or 0)

    def has_active_scan(self, user_id: str) -> bool:
        """True when the user already has a PENDING or RUNNING scan (rate limit)."""
        stmt = (
            select(func.count())
            .select_from(Scan)
            .where(Scan.user_id == user_id, Scan.status.in_(ACTIVE_STATUSES))
        )
        return (self.db.scalar(stmt) or 0) > 0

    # -- lifecycle (each commits) ---------------------------------------------

    def mark_running(self, scan: Scan) -> Scan:
        scan.mark_running()
        self.db.commit()
        return scan

    def mark_completed(self, scan: Scan) -> Scan:
        scan.mark_completed()
        self.db.commit()
        return scan

    def mark_failed(self, scan: Scan, message: str) -> Scan:
        scan.mark_failed(message)
        self.db.commit()
        return scan

    def mark_cancelled(self, scan: Scan) -> Scan:
        scan.status = ScanStatus.CANCELLED
        scan.error_message = "Cancelled by user"
        self.db.commit()
        return scan

    def update_progress(self, scan: Scan, percentage: int) -> Scan:
        scan.progress_percentage = max(0, min(100, int(percentage)))
        self.db.commit()
        return scan


__all__ = ["ScanRepository", "ACTIVE_STATUSES"]
