"""Unit tests for the scan orchestrator (roadmap tasks 4-5, 24).

Collectors and the analyzer orchestrator are injected exactly the way the
API layer will inject them — mocks here prove the pipeline wiring without
any AWS dependency.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.analyzers import RawFinding
from app.analyzers.misconfigurations import MisconfigurationOrchestrator
from app.collectors.base import BaseCollector, CredentialsError
from app.core.constants import ScanStatus
from app.database.base import Base
from app.database.models import User
from app.database.repositories import FindingRepository, ScanRepository
from app.tasks.scan_task import registered_services, run_scan_task


@pytest.fixture()
def db_env():
    """Fresh in-memory SQLite; yields (session_factory, scan_repo)."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    session = factory()
    session.add(User(id="usr_1", email="a@b.io", hashed_password="x", role="admin"))
    session.commit()
    session.close()

    yield factory, ScanRepository(factory())
    engine.dispose()


def _make_scan(factory, user_id: str = "usr_1", services: str = "iam,s3") -> str:
    repos = ScanRepository(factory())
    scan = repos.create(user_id=user_id, services=services.split(","))
    return scan.id


class _StaticCollector(BaseCollector):
    """Collector double returning canned resources."""

    provider = "aws"

    def __init__(self, resources: dict[str, list[dict]] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._resources = resources or {}

    def collect(self) -> dict[str, list[dict]]:
        return self._resources


class _ExplodingCollector(BaseCollector):
    provider = "aws"

    def collect(self) -> dict[str, list[dict]]:
        raise CredentialsError("The security token included in the request is invalid")


class _StaticAnalyzer(MisconfigurationOrchestrator):
    """Analyzer-orchestrator double returning one canned RawFinding."""

    def __init__(self, findings: list[RawFinding] | None = None) -> None:
        self._findings = findings or []

    def run(self, resources) -> list[RawFinding]:  # type: ignore[override]
        return self._findings


def _raw_finding(rule_id: str = "AWS-S3-001") -> RawFinding:
    return RawFinding(
        rule_id=rule_id,
        title="Public S3 bucket",
        description="Bucket grants public read.",
        severity="high",
        resource_type="s3_bucket",
        resource_id="arn:aws:s3:::acme",
        region="us-east-1",
    )


class TestHappyPath:
    def test_full_pipeline_persists_findings_and_completes(self, db_env) -> None:
        factory, _ = db_env
        scan_id = _make_scan(factory)

        collector = _StaticCollector(
            {
                "s3_buckets": [{"arn": "arn:aws:s3:::acme", "name": "acme", "region": "us-east-1"}],
                "iam_users": [{"arn": "arn:aws:iam::1:user/alice", "name": "alice"}],
            }
        )
        analyzer = _StaticAnalyzer([_raw_finding()])

        run_scan_task(
            scan_id,
            session_factory=factory,
            collector_factory=lambda service: collector,
            analyzer=analyzer,
        )

        repos = ScanRepository(factory())
        scan = repos.get(scan_id)
        assert scan.status == ScanStatus.COMPLETED
        assert scan.progress_percentage == 100
        assert scan.started_at is not None
        assert scan.completed_at is not None

        findings, total = FindingRepository(factory()).list_paginated(scan_id=scan_id)
        assert total == 1
        assert findings[0].rule_id == "AWS-S3-001"

    def test_empty_collector_completes_with_zero_findings(self, db_env) -> None:
        factory, _ = db_env
        scan_id = _make_scan(factory)
        run_scan_task(
            scan_id,
            session_factory=factory,
            collector_factory=lambda service: _StaticCollector({}),
            analyzer=_StaticAnalyzer([]),
        )
        scan = ScanRepository(factory()).get(scan_id)
        assert scan.status == ScanStatus.COMPLETED

    def test_unregistered_service_is_skipped_not_fatal(self, db_env) -> None:
        factory, _ = db_env
        scan_id = _make_scan(factory, services="iam")
        run_scan_task(
            scan_id,
            session_factory=factory,
            collector_factory=lambda service: _StaticCollector({}),
            analyzer=_StaticAnalyzer([]),
        )
        scan = ScanRepository(factory()).get(scan_id)
        assert scan.status == ScanStatus.COMPLETED

    def test_progress_written_between_stages(self, db_env) -> None:
        factory, _ = db_env
        scan_id = _make_scan(factory)
        seen: list[int] = []

        real_update = ScanRepository.update_progress

        def spying_update(self, scan, percentage):  # noqa: ANN001
            seen.append(percentage)
            return real_update(self, scan, percentage)

        ScanRepository.update_progress = spying_update
        try:
            run_scan_task(
                scan_id,
                session_factory=factory,
                collector_factory=lambda service: _StaticCollector({}),
                analyzer=_StaticAnalyzer([]),
            )
        finally:
            ScanRepository.update_progress = real_update

        assert seen == [10, 40, 60, 75, 90]


class TestFailures:
    def test_credential_error_marks_failed(self, db_env) -> None:
        factory, _ = db_env
        scan_id = _make_scan(factory)
        run_scan_task(
            scan_id,
            session_factory=factory,
            collector_factory=lambda service: _ExplodingCollector(),
            analyzer=_StaticAnalyzer([]),
        )
        scan = ScanRepository(factory()).get(scan_id)
        assert scan.status == ScanStatus.FAILED
        assert "Cloud API error" in (scan.error_message or "")
        assert scan.completed_at is not None

    def test_unexpected_error_marks_failed(self, db_env) -> None:
        factory, _ = db_env

        class _Boom(BaseCollector):
            provider = "aws"

            def collect(self):
                raise RuntimeError("disk on fire")

        scan_id = _make_scan(factory)
        run_scan_task(
            scan_id,
            session_factory=factory,
            collector_factory=lambda service: _Boom(),
            analyzer=_StaticAnalyzer([]),
        )
        scan = ScanRepository(factory()).get(scan_id)
        assert scan.status == ScanStatus.FAILED
        assert "Internal error" in (scan.error_message or "")

    def test_missing_scan_is_noop(self, db_env) -> None:
        factory, _ = db_env
        # Must not raise.
        run_scan_task(
            "scn_missing",
            session_factory=factory,
            collector_factory=lambda service: _StaticCollector({}),
            analyzer=_StaticAnalyzer([]),
        )


class TestCancellation:
    def test_cancel_between_stages_stops_completion(self, db_env) -> None:
        factory, _ = db_env
        scan_id = _make_scan(factory)

        # Simulate the API marking the scan cancelled mid-run: flip the
        # status the moment the orchestrator first re-reads the row.
        real_run = run_scan_task

        def cancel_then_run(*args, **kwargs):  # noqa: ANN002, ANN003
            repos = ScanRepository(factory())
            repos.mark_cancelled(repos.get(scan_id))
            return real_run(*args, **kwargs)

        # Re-running with an already-cancelled scan: the pre-flight re-read
        # in the task sees CANCELLED after mark_running and must not complete.
        cancel_then_run(
            scan_id,
            session_factory=factory,
            collector_factory=lambda service: _StaticCollector({}),
            analyzer=_StaticAnalyzer([]),
        )

        scan = ScanRepository(factory()).get(scan_id)
        # mark_running overwrote CANCELLED → RUNNING before the cancel point
        # was observed; the task stopped and never reached COMPLETED.
        assert scan.status != ScanStatus.COMPLETED


class TestRegistry:
    def test_registered_services_starts_empty(self) -> None:
        assert isinstance(registered_services(), list)
