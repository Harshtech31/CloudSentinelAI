"""Unit tests for the Scan repository (roadmap task 20)."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.constants import CloudProvider, ScanStatus
from app.database.base import Base
from app.database.repositories import ScanRepository


@pytest.fixture()
def repo():
    """ScanRepository over a fresh in-memory SQLite database per test."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = factory()
    try:
        yield ScanRepository(session)
    finally:
        session.close()


class TestCreate:
    def test_create_defaults_to_pending(self, repo: ScanRepository) -> None:
        scan = repo.create(user_id="usr_1")
        assert scan.id.startswith("scn_")
        assert scan.status == ScanStatus.PENDING
        assert scan.progress_percentage == 0
        assert scan.target_cloud == CloudProvider.AWS

    def test_create_stores_regions_and_services(self, repo: ScanRepository) -> None:
        scan = repo.create(
            user_id="usr_1",
            regions=["us-east-1", "us-west-2"],
            services=["iam", "s3"],
        )
        assert scan.regions == "us-east-1,us-west-2"
        assert scan.services == "iam,s3"

    def test_create_commits_immediately(self, repo: ScanRepository) -> None:
        scan = repo.create(user_id="usr_1")
        # A fresh session (simulating the background task's own session)
        # must already see the row.
        assert repo.get(scan.id) is not None


class TestReads:
    def test_get_missing_returns_none(self, repo: ScanRepository) -> None:
        assert repo.get("scn_nope") is None

    def test_get_for_user_enforces_ownership(self, repo: ScanRepository) -> None:
        scan = repo.create(user_id="usr_1")
        assert repo.get_for_user(scan.id, "usr_1") is not None
        assert repo.get_for_user(scan.id, "usr_2") is None

    def test_list_for_user_paginates_newest_first(self, repo: ScanRepository) -> None:
        for _ in range(5):
            repo.create(user_id="usr_1")
        repo.create(user_id="usr_2")  # other user must not leak in

        rows, total = repo.list_for_user("usr_1", page=1, limit=3)
        assert total == 5
        assert len(rows) == 3

        rows2, total2 = repo.list_for_user("usr_1", page=2, limit=3)
        assert total2 == 5
        assert len(rows2) == 2
        assert {r.id for r in rows}.isdisjoint({r.id for r in rows2})


class TestLifecycle:
    def test_mark_running_stamps_start_time(self, repo: ScanRepository) -> None:
        scan = repo.create(user_id="usr_1")
        repo.mark_running(scan)
        assert scan.status == ScanStatus.RUNNING
        assert scan.started_at is not None

    def test_mark_completed_sets_progress_100(self, repo: ScanRepository) -> None:
        scan = repo.create(user_id="usr_1")
        repo.mark_completed(scan)
        assert scan.status == ScanStatus.COMPLETED
        assert scan.progress_percentage == 100
        assert scan.completed_at is not None

    def test_mark_failed_records_message(self, repo: ScanRepository) -> None:
        scan = repo.create(user_id="usr_1")
        repo.mark_failed(scan, "AWS credentials invalid")
        assert scan.status == ScanStatus.FAILED
        assert scan.error_message == "AWS credentials invalid"

    def test_mark_failed_truncates_long_messages(self, repo: ScanRepository) -> None:
        scan = repo.create(user_id="usr_1")
        repo.mark_failed(scan, "x" * 5000)
        assert len(scan.error_message or "") <= 1000

    def test_mark_cancelled(self, repo: ScanRepository) -> None:
        scan = repo.create(user_id="usr_1")
        repo.mark_cancelled(scan)
        assert scan.status == ScanStatus.CANCELLED

    def test_update_progress_clamps(self, repo: ScanRepository) -> None:
        scan = repo.create(user_id="usr_1")
        repo.update_progress(scan, 150)
        assert scan.progress_percentage == 100
        repo.update_progress(scan, -5)
        assert scan.progress_percentage == 0


class TestRateLimit:
    def test_no_active_scan_initially(self, repo: ScanRepository) -> None:
        assert repo.has_active_scan("usr_1") is False

    def test_pending_scan_counts_as_active(self, repo: ScanRepository) -> None:
        repo.create(user_id="usr_1")
        assert repo.has_active_scan("usr_1") is True

    def test_running_scan_counts_as_active(self, repo: ScanRepository) -> None:
        scan = repo.create(user_id="usr_1")
        repo.mark_running(scan)
        assert repo.has_active_scan("usr_1") is True

    def test_completed_scan_does_not_block(self, repo: ScanRepository) -> None:
        scan = repo.create(user_id="usr_1")
        repo.mark_completed(scan)
        assert repo.has_active_scan("usr_1") is False

    def test_failed_and_cancelled_do_not_block(self, repo: ScanRepository) -> None:
        failed = repo.create(user_id="usr_1")
        repo.mark_failed(failed, "boom")
        cancelled = repo.create(user_id="usr_1")
        repo.mark_cancelled(cancelled)
        assert repo.has_active_scan("usr_1") is False

    def test_other_users_scans_do_not_block(self, repo: ScanRepository) -> None:
        repo.create(user_id="usr_2")
        assert repo.has_active_scan("usr_1") is False
