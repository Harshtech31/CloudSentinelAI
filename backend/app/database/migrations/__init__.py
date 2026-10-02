"""
Alembic Migrations Package for CloudSentinel AI.

Alembic's operating files live in `backend/alembic.ini` +
`backend/migrations/` (standard layout). This package marker documents
that relationship and re-exports nothing by design: migration scripts
import `Base` from `app.database` directly in `env.py`.
"""

__all__: list[str] = []
