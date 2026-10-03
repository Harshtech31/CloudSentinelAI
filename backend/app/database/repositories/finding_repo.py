"""
Finding Repository for CloudSentinel AI.

CRUD and query operations for `Finding` rows (roadmap_part2_core_pipeline.md
task 2, Member 1 track). Includes the bulk inserter the scan pipeline uses
to persist analyzer output (`RawFinding` → `Finding` rows) and the
aggregations behind the findings-stats and dashboard endpoints.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.analyzers import RawFinding
from app.core.constants import Severity
from app.database.models import Finding, Scan

SEVERITY_ORDER = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]


class FindingRepository:
    """Database operations for `Finding` rows."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # -- writes ---------------------------------------------------------------

    def bulk_create_from_raw(self, scan_id: str, raw_findings: list[RawFinding]) -> list[Finding]:
        """Persist analyzer output for a scan in one transaction.

        The `metadata` dicts are serialized to JSON text in the
        `metadata_json` column (the model stores Text, not JSONB, so the
        schema stays portable across SQLite and Postgres).
        """
        import json

        rows = [
            Finding(
                scan_id=scan_id,
                rule_id=raw.rule_id,
                title=raw.title,
                description=raw.description,
                severity=raw.severity,
                risk_score=0.0,  # risk scoring lands with the risk engine wire-up
                resource_type=raw.resource_type,
                resource_id=raw.resource_id,
                resource_arn=raw.resource_arn,
                region=raw.region,
                remediation=raw.remediation,
                remediation_url=raw.remediation_url,
                metadata_json=json.dumps(raw.metadata) if raw.metadata else None,
            )
            for raw in raw_findings
        ]
        self.db.add_all(rows)
        self.db.commit()
        return rows

    # -- reads ----------------------------------------------------------------

    def get(self, finding_id: str) -> Finding | None:
        """Fetch one finding by id, or None."""
        return self.db.get(Finding, finding_id)

    def list_paginated(
        self,
        *,
        scan_id: str | None = None,
        severity: Severity | None = None,
        status: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[Finding], int]:
        """Paginated findings with optional filters, newest first."""
        conditions = []
        if scan_id is not None:
            conditions.append(Finding.scan_id == scan_id)
        if severity is not None:
            conditions.append(Finding.severity == severity)
        if status is not None:
            conditions.append(Finding.status == status)

        total_stmt = select(func.count()).select_from(Finding)
        rows_stmt = select(Finding)
        if conditions:
            total_stmt = total_stmt.where(*conditions)
            rows_stmt = rows_stmt.where(*conditions)

        total = self.db.scalar(total_stmt)
        rows = self.db.scalars(
            rows_stmt.order_by(Finding.created_at.desc(), Finding.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        ).all()
        return list(rows), int(total or 0)

    def count_by_severity(self, *, scan_id: str | None = None) -> dict[str, int]:
        """Severity counts (all severities present, zero when absent).

        Basis for the findings-stats endpoint and the dashboard summary.
        When scan_id is given only that scan's findings are counted.
        """
        stmt = select(Finding.severity, func.count()).group_by(Finding.severity)
        if scan_id is not None:
            stmt = stmt.where(Finding.scan_id == scan_id)
        counts = {severity.value: 0 for severity in SEVERITY_ORDER}
        for severity_value, count in self.db.execute(stmt):
            counts[str(severity_value)] = int(count)
        counts["total"] = sum(counts.values())
        return counts

    def count_by_severity_for_user(self, user_id: str) -> dict[str, int]:
        """Severity counts across every scan owned by a user.

        The dashboard's per-tenant aggregation: joins findings to their
        owning scan so each user's posture reflects only their data.
        """
        stmt = (
            select(Finding.severity, func.count())
            .join(Scan, Finding.scan_id == Scan.id)
            .where(Scan.user_id == user_id)
            .group_by(Finding.severity)
        )
        counts = {severity.value: 0 for severity in SEVERITY_ORDER}
        for severity_value, count in self.db.execute(stmt):
            counts[str(severity_value)] = int(count)
        counts["total"] = sum(counts.values())
        return counts

    # -- mutations --------------------------------------------------------------

    def resolve(self, finding: Finding) -> Finding:
        """Mark a finding resolved and commit."""
        finding.status = "resolved"
        self.db.commit()
        return finding

    def reopen(self, finding: Finding) -> Finding:
        """Return a resolved finding to the open state and commit."""
        finding.status = "open"
        self.db.commit()
        return finding


__all__ = ["FindingRepository", "SEVERITY_ORDER"]
