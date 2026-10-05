"""
Audit Log ORM Model for CloudSentinel AI.

Immutable trail of security-relevant actions (roadmap task 28): who
(actor), did what (action), to which entity. Rows are append-only —
no update or delete paths are exposed anywhere in the application.
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


def _new_audit_id() -> str:
    return f"aud_{uuid4().hex[:12]}"


class AuditLog(TimestampMixin, Base):
    """One recorded action performed by a user on an entity."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, default=_new_audit_id)
    actor_id: Mapped[str | None] = mapped_column(
        String(20), ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    action: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        index=True,
        nullable=False,
    )

    actor = relationship("User", viewonly=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AuditLog {self.action} {self.entity_type}/{self.entity_id} by {self.actor_id}>"


__all__ = ["AuditLog"]
