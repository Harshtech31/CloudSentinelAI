"""Unit tests for the Report repository (roadmap task 3)."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.constants import ReportFormat
from app.database.base import Base
from app.database.models import Scan
from app.database.repositories import ReportRepository


@pytest.fixture()
def repo():
    """ReportRepository over a fresh in-memory SQLite database per test."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = factory()
    try:
        yield ReportRepository(session)
    finally:
        session.close()


@pytest.fixture()
def scan_id(repo) -> str:
    scan = Scan(user_id="usr_1")
    repo.db.add(scan)
    repo.db.commit()
    return scan.id


class TestReportRepo:
    def test_create_stores_artifact_metadata(self, repo: ReportRepository, scan_id: str) -> None:
        report = repo.create(
            scan_id=scan_id,
            format=ReportFormat.JSON,
            file_path="/tmp/report.json",
            file_size_bytes=2048,
        )
        assert report.id.startswith("rpt_")
        assert report.scan_id == scan_id
        assert report.format == ReportFormat.JSON
        assert report.file_size_bytes == 2048
        assert report.generated_at is not None

    def test_get_missing_returns_none(self, repo: ReportRepository) -> None:
        assert repo.get("rpt_nope") is None

    def test_list_for_scan_scopes_and_paginates(self, repo: ReportRepository, scan_id: str) -> None:
        other = Scan(user_id="usr_1")
        repo.db.add(other)
        repo.db.commit()
        repo.create(scan_id=scan_id, format=ReportFormat.CSV, file_path="/a.csv")
        repo.create(scan_id=other.id, format=ReportFormat.CSV, file_path="/b.csv")
        repo.create(scan_id=scan_id, format=ReportFormat.HTML, file_path="/a.html")

        rows, total = repo.list_for_scan(scan_id)
        assert total == 2
        assert {r.file_path for r in rows} == {"/a.csv", "/a.html"}

    def test_delete_removes_row(self, repo: ReportRepository, scan_id: str) -> None:
        report = repo.create(scan_id=scan_id, format=ReportFormat.JSON, file_path="/x.json")
        repo.delete(report)
        assert repo.get(report.id) is None
