"""
Finding ORM Model for CloudSentinel AI.
"""

from uuid import uuid4

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import Severity
from app.database.base import Base, TimestampMixin


def _new_finding_id() -> str:
    return f"fnd_{uuid4().hex[:12]}"


class Finding(TimestampMixin, Base):
    """One misconfiguration detected by the rule engine during a scan."""

    __tablename__ = "findings"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, default=_new_finding_id)
    scan_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("scans.id", ondelete="CASCADE"), index=True, nullable=False
    )
    rule_id: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    severity: Mapped[Severity] = mapped_column(
        Enum(
            Severity, native_enum=False, length=10, values_callable=lambda e: [m.value for m in e]
        ),
        index=True,
        nullable=False,
    )
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    resource_type: Mapped[str] = mapped_column(String(40), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(200), nullable=False)
    resource_arn: Mapped[str | None] = mapped_column(String(300), nullable=True)
    region: Mapped[str | None] = mapped_column(String(30), nullable=True)
    remediation: Mapped[str | None] = mapped_column(Text, nullable=True)
    remediation_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    scan = relationship("Scan", back_populates="findings")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Finding {self.rule_id} {self.severity} {self.resource_id}>"


__all__ = ["Finding"]
