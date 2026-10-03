"""
Report Repository for CloudSentinel AI.

CRUD for exported report artifacts (roadmap_part2_core_pipeline.md
task 3, Member 1 track). Rows record what was exported, in which
format, and where the renderer wrote the file; bytes live on disk,
never in the database.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.constants import ReportFormat
from app.database.models import Report


class ReportRepository:
    """Database operations for `Report` rows."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        scan_id: str,
        format: ReportFormat,
        file_path: str,
        file_size_bytes: int = 0,
    ) -> Report:
        """Insert a report artifact row and commit."""
        report = Report(
            scan_id=scan_id,
            format=format,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get(self, report_id: str) -> Report | None:
        """Fetch one report by id, or None."""
        return self.db.get(Report, report_id)

    def list_for_scan(
        self, scan_id: str, *, page: int = 1, limit: int = 50
    ) -> tuple[list[Report], int]:
        """Paginated reports generated for a scan, newest first."""
        total = self.db.scalar(
            select(func.count()).select_from(Report).where(Report.scan_id == scan_id)
        )
        rows = self.db.scalars(
            select(Report)
            .where(Report.scan_id == scan_id)
            .order_by(Report.created_at.desc(), Report.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        ).all()
        return list(rows), int(total or 0)

    def delete(self, report: Report) -> None:
        """Remove a report row and commit (file on disk is unchanged)."""
        self.db.delete(report)
        self.db.commit()


__all__ = ["ReportRepository"]
