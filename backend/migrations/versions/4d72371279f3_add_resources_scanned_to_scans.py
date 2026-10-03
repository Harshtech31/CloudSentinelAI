"""add resources_scanned to scans

Revision ID: 4d72371279f3
Revises: a3f9c1d7e5b2
Create Date: 2026-10-03 10:45:18.487812+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4d72371279f3"
down_revision: str | None = "a3f9c1d7e5b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # server_default keeps the ADD COLUMN valid on Postgres tables that
    # already hold rows; the ORM default fills it for new rows going forward.
    op.add_column(
        "scans",
        sa.Column("resources_scanned", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("scans", "resources_scanned")
