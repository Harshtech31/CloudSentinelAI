"""Unit tests for the Finding repository (roadmap task 21)."""

import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.analyzers import RawFinding
from app.core.constants import Severity
from app.database.base import Base
from app.database.models import Scan
from app.database.repositories import FindingRepository


@pytest.fixture()
def repo():
    """FindingRepository over a fresh in-memory SQLite database per test."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = factory()
    try:
        yield FindingRepository(session)
    finally:
        session.close()


@pytest.fixture()
def scan_id(repo) -> str:
    """A parent scan row to satisfy the findings FK."""
    scan = Scan(user_id="usr_1")
    repo.db.add(scan)
    repo.db.commit()
    return scan.id


def _raw(**overrides) -> RawFinding:
    defaults = dict(
        rule_id="AWS-S3-001",
        title="Public S3 bucket",
        description="Bucket grants public read access.",
        severity=Severity.HIGH,
        resource_type="s3_bucket",
        resource_id="arn:aws:s3:::acme-logs",
        resource_arn="arn:aws:s3:::acme-logs",
        region="us-east-1",
        remediation="Enable S3 Block Public Access.",
        remediation_url="https://docs.aws.amazon.com/s3",
        metadata={"acl": "public-read"},
    )
    defaults.update(overrides)
    return RawFinding(**defaults)


class TestBulkCreate:
    def test_bulk_insert_maps_all_fields(self, repo: FindingRepository, scan_id: str) -> None:
        rows = repo.bulk_create_from_raw(scan_id, [_raw(), _raw(rule_id="AWS-IAM-002")])
        assert len(rows) == 2
        first = rows[0]
        assert first.scan_id == scan_id
        assert first.id.startswith("fnd_")
        assert first.rule_id == "AWS-S3-001"
        assert first.severity == Severity.HIGH
        assert first.resource_arn == "arn:aws:s3:::acme-logs"
        assert first.remediation == "Enable S3 Block Public Access."
        assert first.status == "open"
        assert json.loads(first.metadata_json or "{}") == {"acl": "public-read"}

    def test_bulk_insert_empty_list_is_noop(self, repo: FindingRepository, scan_id: str) -> None:
        assert repo.bulk_create_from_raw(scan_id, []) == []

    def test_optional_fields_default_to_none(self, repo: FindingRepository, scan_id: str) -> None:
        (row,) = repo.bulk_create_from_raw(
            scan_id,
            [
                _raw(
                    resource_arn=None,
                    region=None,
                    remediation=None,
                    remediation_url=None,
                    metadata={},
                )
            ],
        )
        assert row.resource_arn is None
        assert row.region is None
        assert row.metadata_json is None


class TestReads:
    def test_get_missing_returns_none(self, repo: FindingRepository) -> None:
        assert repo.get("fnd_nope") is None

    def test_list_paginates_and_filters_by_severity(
        self, repo: FindingRepository, scan_id: str
    ) -> None:
        repo.bulk_create_from_raw(
            scan_id,
            [
                _raw(rule_id="R1", severity=Severity.CRITICAL),
                _raw(rule_id="R2", severity=Severity.HIGH),
                _raw(rule_id="R3", severity=Severity.HIGH),
                _raw(rule_id="R4", severity=Severity.LOW),
            ],
        )
        rows, total = repo.list_paginated(severity=Severity.HIGH, page=1, limit=10)
        assert total == 2
        assert {r.rule_id for r in rows} == {"R2", "R3"}

        page_rows, page_total = repo.list_paginated(page=2, limit=3)
        assert page_total == 4
        assert len(page_rows) == 1

    def test_list_filters_by_scan_and_status(self, repo: FindingRepository, scan_id: str) -> None:
        repo.bulk_create_from_raw(scan_id, [_raw()])
        rows, total = repo.list_paginated(scan_id=scan_id, status="open")
        assert total == 1
        _, other_total = repo.list_paginated(scan_id="scn_other")
        assert other_total == 0

    def test_count_by_severity_includes_zeroes(self, repo: FindingRepository, scan_id: str) -> None:
        repo.bulk_create_from_raw(
            scan_id, [_raw(severity=Severity.CRITICAL), _raw(severity=Severity.CRITICAL)]
        )
        counts = repo.count_by_severity()
        assert counts["critical"] == 2
        assert counts["high"] == 0
        assert counts["total"] == 2

    def test_count_by_severity_scoped_to_scan(self, repo: FindingRepository, scan_id: str) -> None:
        other_scan = Scan(user_id="usr_1")
        repo.db.add(other_scan)
        repo.db.commit()
        repo.bulk_create_from_raw(scan_id, [_raw()])
        repo.bulk_create_from_raw(other_scan.id, [_raw(), _raw()])
        assert repo.count_by_severity(scan_id=scan_id)["total"] == 1
        assert repo.count_by_severity(scan_id=other_scan.id)["total"] == 2


class TestResolve:
    def test_resolve_and_reopen(self, repo: FindingRepository, scan_id: str) -> None:
        (row,) = repo.bulk_create_from_raw(scan_id, [_raw()])
        assert repo.resolve(row).status == "resolved"
        assert repo.reopen(row).status == "open"
