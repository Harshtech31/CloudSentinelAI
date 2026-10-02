"""
Database Seed Script for CloudSentinel AI.

Creates the default test account for local development and demo runs.
Idempotent: re-running never duplicates or overwrites.

Usage:
    python -m app.database.seed            # default engine (Postgres/SQLite)
    DATABASE_SYNC_URL=sqlite:///dev.db python -m app.database.seed
"""

import getpass
import sys

from app.core.constants import UserRole
from app.core.logging import logger
from app.core.security import get_password_hash
from app.database.models import User
from app.database.session import session_scope

DEFAULT_EMAIL = "admin@cloudsentinel.ai"
DEFAULT_NAME = "CloudSentinel Admin"


def seed_test_user(
    email: str = DEFAULT_EMAIL,
    password: str | None = None,
    full_name: str = DEFAULT_NAME,
    role: UserRole = UserRole.ADMIN,
) -> User | None:
    """Create the test user if missing; return the User or None if exists.

    Password source: argument, then CSP_SEED_PASSWORD, then an interactive
    prompt. Nothing is logged in plaintext.
    """
    import os

    resolved_password = password or os.getenv("CSP_SEED_PASSWORD")
    if not resolved_password:
        resolved_password = getpass.getpass(f"Password for {email}: ")
    if not resolved_password:
        logger.error("No password provided; seed aborted")
        return None

    with session_scope() as db:
        existing = db.query(User).filter_by(email=email).one_or_none()
        if existing is not None:
            logger.info("Seed user %s already exists (id=%s) — nothing to do", email, existing.id)
            return None
        user = User(
            email=email,
            hashed_password=get_password_hash(resolved_password),
            full_name=full_name,
            role=role,
            is_active=True,
        )
        db.add(user)
        db.flush()
        logger.info("Seeded user %s (id=%s, role=%s)", user.email, user.id, user.role)
        return user


def main() -> int:
    """CLI entrypoint for `python -m app.database.seed`."""
    user = seed_test_user()
    return 0 if user is not None or seed_user_exists() else 1


def seed_user_exists() -> bool:
    """True when the default seed account is already present."""
    with session_scope() as db:
        return db.query(User).filter_by(email=DEFAULT_EMAIL).one_or_none() is not None


if __name__ == "__main__":
    sys.exit(main())
