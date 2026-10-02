"""create scans, findings, reports tables

Revision ID: a3f9c1d7e5b2
Revises: 0253ed8447f3
Create Date: 2026-10-02 13:17:04.211254+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a3f9c1d7e5b2"
down_revision: str | None = "0253ed8447f3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "scans",
        sa.Column("id", sa.String(length=20), nullable=False),
        sa.Column("user_id", sa.String(length=20), nullable=True),
        sa.Column(
            "target_cloud",
            sa.Enum("aws", "gcp", "azure", name="cloudprovider", native_enum=False, length=10),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "running",
                "completed",
                "failed",
                "cancelled",
                name="scanstatus",
                native_enum=False,
                length=12,
            ),
            nullable=False,
        ),
        sa.Column("regions", sa.String(length=500), nullable=False),
        sa.Column("services", sa.String(length=500), nullable=False),
        sa.Column("progress_percentage", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_scans_user_id_users"), ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_scans")),
    )
    op.create_index(op.f("ix_scans_status"), "scans", ["status"], unique=False)
    op.create_index(op.f("ix_scans_user_id"), "scans", ["user_id"], unique=False)

    op.create_table(
        "findings",
        sa.Column("id", sa.String(length=20), nullable=False),
        sa.Column("scan_id", sa.String(length=20), nullable=False),
        sa.Column("rule_id", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "severity",
            sa.Enum(
                "critical",
                "high",
                "medium",
                "low",
                "info",
                name="severity",
                native_enum=False,
                length=10,
            ),
            nullable=False,
        ),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("resource_type", sa.String(length=40), nullable=False),
        sa.Column("resource_id", sa.String(length=200), nullable=False),
        sa.Column("resource_arn", sa.String(length=300), nullable=True),
        sa.Column("region", sa.String(length=30), nullable=True),
        sa.Column("remediation", sa.Text(), nullable=True),
        sa.Column("remediation_url", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["scan_id"], ["scans.id"], name=op.f("fk_findings_scan_id_scans"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_findings")),
    )
    op.create_index(op.f("ix_findings_rule_id"), "findings", ["rule_id"], unique=False)
    op.create_index(op.f("ix_findings_scan_id"), "findings", ["scan_id"], unique=False)
    op.create_index(op.f("ix_findings_severity"), "findings", ["severity"], unique=False)

    op.create_table(
        "reports",
        sa.Column("id", sa.String(length=20), nullable=False),
        sa.Column("scan_id", sa.String(length=20), nullable=False),
        sa.Column(
            "format",
            sa.Enum(
                "json", "csv", "html", "pdf", name="reportformat", native_enum=False, length=10
            ),
            nullable=False,
        ),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["scan_id"], ["scans.id"], name=op.f("fk_reports_scan_id_scans"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reports")),
    )
    op.create_index(op.f("ix_reports_scan_id"), "reports", ["scan_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reports_scan_id"), table_name="reports")
    op.drop_table("reports")
    op.drop_index(op.f("ix_findings_severity"), table_name="findings")
    op.drop_index(op.f("ix_findings_scan_id"), table_name="findings")
    op.drop_index(op.f("ix_findings_rule_id"), table_name="findings")
    op.drop_table("findings")
    op.drop_index(op.f("ix_scans_user_id"), table_name="scans")
    op.drop_index(op.f("ix_scans_status"), table_name="scans")
    op.drop_table("scans")
