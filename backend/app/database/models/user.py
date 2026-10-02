"""
User ORM Model for CloudSentinel AI.
"""

from uuid import uuid4

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import UserRole
from app.database.base import Base, TimestampMixin


def _new_user_id() -> str:
    return f"usr_{uuid4().hex[:12]}"


class User(TimestampMixin, Base):
    """A console account (SOC analyst, admin, or viewer)."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, default=_new_user_id)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole, native_enum=False, length=20, values_callable=lambda e: [m.value for m in e]
        ),
        default=UserRole.ANALYST,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Default cascade only: scan history must survive account deletion
    # (FK is nullable with ondelete=SET NULL; SQLAlchemy nulls the FK
    # on parent delete). Findings/reports remain tied to their scan.
    scans = relationship("Scan", back_populates="user")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.id} {self.email} ({self.role})>"


__all__ = ["User"]
