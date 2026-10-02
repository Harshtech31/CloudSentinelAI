"""
Database Session Management for CloudSentinel AI.

Sync SQLAlchemy engine + session factory. The async URL in settings is
used by docker-compose/Postgres in deployment; tests and local scripts
run on the sync engine against SQLite (or a Postgres DATABASE_SYNC_URL).

Phase 2 will add the async engine when the scan pipeline moves to
async collection (roadmap_part2_core_pipeline.md).
"""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logging import logger


def _database_url() -> str:
    """Resolve the sync database URL.

    Precedence: DATABASE_SYNC_URL env override, then settings, then
    local SQLite for tests/scripts. A Postgres URL is kept as-is —
    connecting lazily means a temporarily unreachable database never
    breaks application import; health checks report it instead.
    """
    import os

    env_url = os.getenv("DATABASE_SYNC_URL", "")
    if env_url:
        return env_url
    url = getattr(settings, "DATABASE_SYNC_URL", "") or ""
    if url:
        return url
    return "sqlite:///./cloudsentinel.db"


def create_db_engine(url: str | None = None) -> Engine:
    """Build the sync engine with conservative pool settings."""
    resolved = url or _database_url()
    engine_kwargs: dict = {"pool_pre_ping": True}
    if resolved.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine = create_engine(resolved, **engine_kwargs)
    logger.debug("Database engine created for %s", resolved.split("@")[-1])
    return engine


engine: Engine = create_db_engine()

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a session, always closed on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Context manager with commit/rollback semantics for scripts/tasks."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_all() -> None:
    """Create tables from model metadata (dev/test convenience; Alembic owns prod schema)."""
    from app.database import models  # noqa: F401  (register mappers)

    Base = models.Base
    Base.metadata.create_all(bind=engine)


__all__ = ["engine", "SessionLocal", "get_db", "session_scope", "create_all", "create_db_engine"]
