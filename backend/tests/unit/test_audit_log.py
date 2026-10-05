"""Tests for the audit trail (roadmap tasks 28-29)."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.constants import ScanStatus
from app.database.base import Base
from app.database.models import AuditLog
from app.database.repositories import AuditLogRepository, ScanRepository


@pytest.fixture()
def env():
    """DB + repos over fresh in-memory SQLite."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = factory()
    yield session, ScanRepository(session), AuditLogRepository(session)
    session.close()
    engine.dispose()


class TestScanLifecycleAudit:
    def test_create_writes_audit_entry(self, env) -> None:
        session, scans, audits = env
        scan = scans.create(user_id="usr_1")
        trail = audits.list_for_entity("scan", scan.id)
        assert [entry.action for entry in trail] == ["scan.created"]
        assert trail[0].actor_id == "usr_1"

    def test_full_lifecycle_leaves_complete_trail(self, env) -> None:
        session, scans, audits = env
        scan = scans.create(user_id="usr_1")
        fresh = scans.get(scan.id)
        scans.mark_running(fresh)
        fresh = scans.get(scan.id)
        fresh.resources_scanned = 7
        session.commit()
        scans.mark_completed(fresh)

        trail = audits.list_for_entity("scan", scan.id)
        assert [entry.action for entry in trail] == [
            "scan.created",
            "scan.started",
            "scan.completed",
        ]
        completed = trail[-1]
        assert completed.detail == "resources_scanned=7"

    def test_failed_scan_audits_message(self, env) -> None:
        session, scans, audits = env
        scan = scans.create(user_id="usr_1")
        scans.mark_failed(scans.get(scan.id), "AWS credentials invalid")
        trail = audits.list_for_entity("scan", scan.id)
        assert trail[-1].action == "scan.failed"
        assert "credentials" in (trail[-1].detail or "")

    def test_cancelled_scan_audits(self, env) -> None:
        session, scans, audits = env
        scan = scans.create(user_id="usr_1")
        scans.mark_cancelled(scans.get(scan.id))
        trail = audits.list_for_entity("scan", scan.id)
        assert trail[-1].action == "scan.cancelled"

    def test_audit_shares_transaction_with_mutation(self, env) -> None:
        """An audit entry must never trail its action: same transaction.

        Simulates a crash between mutation and commit — the rollback must
        take the audit entry with it (atomicity proof).
        """
        session, scans, _ = env
        scan = scans.create(user_id="usr_1")
        fresh = scans.get(scan.id)
        fresh.status = ScanStatus.RUNNING
        session.add(
            AuditLog(
                actor_id=fresh.user_id,
                action="scan.started",
                entity_type="scan",
                entity_id=fresh.id,
            )
        )
        session.rollback()  # simulated crash before commit

        trail = (
            session.query(AuditLog)
            .filter_by(entity_id=scan.id)
            .order_by(AuditLog.created_at.asc())
            .all()
        )
        assert [entry.action for entry in trail] == ["scan.created"]  # only the committed entry

    def test_entries_are_queryable_by_action(self, env) -> None:
        session, scans, audits = env
        for _ in range(3):
            scans.create(user_id="usr_1")
        created = session.query(AuditLog).filter_by(action="scan.created").all()
        assert len(created) == 3
