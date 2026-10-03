"""
Scan ORM Model for CloudSentinel AI.
"""

import enum
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import CloudProvider, ScanStatus
from app.database.base import Base, TimestampMixin


def _new_scan_id() -> str:
    return f"scn_{uuid4().hex[:12]}"


class Scan(TimestampMixin, Base):
    """One cloud scan run: collection → analysis → findings."""

    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, default=_new_scan_id)
    user_id: Mapped[str | None] = mapped_column(
        String(20), ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    target_cloud: Mapped[CloudProvider] = mapped_column(
        Enum(
            CloudProvider,
            native_enum=False,
            length=10,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=CloudProvider.AWS,
        nullable=False,
    )
    status: Mapped[ScanStatus] = mapped_column(
        Enum(
            ScanStatus, native_enum=False, length=12, values_callable=lambda e: [m.value for m in e]
        ),
        default=ScanStatus.PENDING,
        index=True,
        nullable=False,
    )
    regions: Mapped[str] = mapped_column(String(500), default="us-east-1", nullable=False)
    services: Mapped[str] = mapped_column(
        String(500), default="iam,ec2,s3,vpc,security_groups,rds,cloudtrail", nullable=False
    )
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    resources_scanned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    user = relationship("User", back_populates="scans")
    findings = relationship("Finding", back_populates="scan", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="scan", cascade="all, delete-orphan")

    def mark_running(self) -> None:
        """Transition to RUNNING and stamp the start time."""
        self.status = ScanStatus.RUNNING
        self.started_at = datetime.now(UTC)

    def mark_completed(self) -> None:
        """Transition to COMPLETED at 100% and stamp the end time."""
        self.status = ScanStatus.COMPLETED
        self.progress_percentage = 100
        self.completed_at = datetime.now(UTC)

    def mark_failed(self, message: str) -> None:
        """Transition to FAILED with an operator-readable reason."""
        self.status = ScanStatus.FAILED
        self.error_message = message[:1000]
        self.completed_at = datetime.now(UTC)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Scan {self.id} {self.target_cloud}/{self.status}>"


# Kept for typing completeness; enum members are used via app.core.constants.
_ = enum.Enum

__all__ = ["Scan"]
