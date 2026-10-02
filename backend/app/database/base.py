"""
SQLAlchemy Declarative Base for CloudSentinel AI.

Single Base for every ORM model. The naming convention makes constraint
names deterministic, which Alembic requires for stable future migrations
(rename/drop operations need named constraints, especially on Postgres).
"""

from datetime import UTC, datetime

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Deterministic constraint names — required for clean Alembic migrations.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base with conventional metadata and timestamps."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def utcnow() -> datetime:
    """Timezone-aware UTC now — default factory for timestamp columns."""
    return datetime.now(UTC)


class TimestampMixin:
    """created_at/updated_at columns shared by versioned tables."""

    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow, nullable=False)


__all__ = ["Base", "TimestampMixin", "utcnow", "NAMING_CONVENTION"]
