"""
Report ORM Model for CloudSentinel AI.
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import ReportFormat
from app.database.base import Base, TimestampMixin


def _new_report_id() -> str:
    return f"rpt_{uuid4().hex[:12]}"


class Report(TimestampMixin, Base):
    """An exported artifact generated from a completed scan."""

    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, default=_new_report_id)
    scan_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("scans.id", ondelete="CASCADE"), index=True, nullable=False
    )
    format: Mapped[ReportFormat] = mapped_column(
        Enum(
            ReportFormat,
            native_enum=False,
            length=10,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=ReportFormat.JSON,
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    scan = relationship("Scan", back_populates="reports")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Report {self.id} {self.format} scan={self.scan_id}>"


__all__ = ["Report"]
