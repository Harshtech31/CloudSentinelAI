"""Alembic migration environment for CloudSentinel AI.

Resolves the database URL from application settings (never from this
repository), registers every ORM model with autogenerate, and supports
both offline (SQL emission) and online (direct DDL) modes.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool

from app.core.config import settings
from app.database import (
    Base,
    models,  # noqa: F401  (register all mappers)
)

# Alembic Config object (provides access to alembic.ini values).
config = context.config

# Interpret the config file for Python logging when present.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Autogenerate target: the shared declarative Base metadata.
target_metadata = Base.metadata


def _sync_url() -> str:
    """Derive a sync driver URL from the configured database URL.

    The app default is an asyncpg URL (used by the async engine in
    Phase 2); Alembic needs a sync driver, so asyncpg:// is rewritten
    to psycopg2:// while leaving explicit DATABASE_SYNC_URL values
    untouched.
    """
    url = settings.DATABASE_SYNC_URL
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    return url


def run_migrations_offline() -> None:
    """Emit SQL to stdout without a live DB connection."""
    context.configure(
        url=_sync_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live connection with a non-pooling engine."""
    connectable = context.config.attributes.get("connection", None)

    if connectable is None:
        from sqlalchemy import engine_from_config

        section = config.get_section(config.config_ini_section, {})
        section["sqlalchemy.url"] = _sync_url()
        connectable = engine_from_config(
            section,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
