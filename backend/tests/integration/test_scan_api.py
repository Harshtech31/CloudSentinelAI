"""Integration tests for the scan API (roadmap tasks 6-9, 18-19).

Runs the real HTTP stack on in-memory SQLite. The orchestrator runs as a
real FastAPI BackgroundTask — mock collectors/analyzers are injected by
patching the module-level defaults the task uses, exactly how the API
process will run it.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.analyzers import RawFinding
from app.collectors.base import BaseCollector
from app.database.base import Base
from app.database.session import get_db

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
SCANS = "/api/v1/scan"


@pytest.fixture()
def client():
    """App + fresh DB per test; yields (TestClient, auth headers helper)."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def _override():
        session = factory()
        try:
            yield session
        finally:
            session.close()

    from app.main import app

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client, factory
    app.dependency_overrides.pop(get_db, None)
    engine.dispose()


def _register_and_login(client: TestClient, email: str = "scan@user.io") -> dict[str, str]:
    resp = client.post(
        REGISTER,
        json={
            "email": email,
            "password": "Sup3rSecret!",
            "full_name": "Scan User",
            "role": "analyst",
        },
    )
    assert resp.status_code == 201, resp.text
    resp = client.post(LOGIN, json={"username": email, "password": "Sup3rSecret!"})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


class _StaticCollector(BaseCollector):
    provider = "aws"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def collect(self) -> dict[str, list[dict]]:
        return {"s3_buckets": [{"arn": "arn:aws:s3:::acme", "name": "acme", "region": "us-east-1"}]}


def _static_analyzer_factory(findings):
    class _Analyzer:
        def run(self, resources):
            return findings

    return _Analyzer()


def _raw() -> RawFinding:
    return RawFinding(
        rule_id="AWS-S3-001",
        title="Public S3 bucket",
        description="Bucket grants public read.",
        severity="high",
        resource_type="s3_bucket",
        resource_id="arn:aws:s3:::acme",
        region="us-east-1",
    )


class TestStartScan:
    def test_start_returns_202_and_runs_to_completion(
        self,
        client,  # noqa: ANN001
    ) -> None:
        test_client, _ = client
        headers = _register_and_login(test_client)

        with (
            patch("app.tasks.scan_task._COLLECTOR_REGISTRY", {"s3": _StaticCollector}),
            patch(
                "app.tasks.scan_task.MisconfigurationOrchestrator",
                lambda: _static_analyzer_factory([_raw()]),
            ),
        ):
            resp = test_client.post(
                f"{SCANS}/start",
                json={"target_cloud": "aws", "regions": ["us-east-1"], "services": ["s3"]},
                headers=headers,
            )
        assert resp.status_code == 202, resp.text
        body = resp.json()
        scan_id = body["scan_id"]
        assert body["status"] == "pending"

        # BackgroundTasks run after the response; the scan should now be done.
        status_resp = test_client.get(f"{SCANS}/{scan_id}/status", headers=headers)
        assert status_resp.status_code == 200
        assert status_resp.json()["status"] == "completed"
        assert status_resp.json()["progress_percentage"] == 100

        # Summary reflects the persisted finding.
        summary = test_client.get(f"{SCANS}/{scan_id}/summary", headers=headers).json()
        assert summary["total_findings"] == 1
        assert summary["high_findings"] == 1
        assert summary["critical_findings"] == 0

    def test_start_requires_auth(self, client) -> None:
        test_client, _ = client
        assert test_client.post(f"{SCANS}/start", json={}).status_code in (401, 403)

    def test_rate_limit_second_concurrent_scan_409(self, client) -> None:
        test_client, _ = client
        headers = _register_and_login(test_client)

        # Keep the first scan pending (no collector registered → the task
        # still runs, but we block completion by patching run_scan_task).
        with patch("app.api.v1.scan.run_scan_task", lambda scan_id, **kwargs: None):
            first = test_client.post(
                f"{SCANS}/start", json={"services": ["s3"]}, headers=headers
            )
            assert first.status_code == 202
            second = test_client.post(
                f"{SCANS}/start", json={"services": ["s3"]}, headers=headers
            )
            assert second.status_code == 409

    def test_cancel_then_start_is_allowed(self, client) -> None:
        test_client, _ = client
        headers = _register_and_login(test_client)
        with patch("app.api.v1.scan.run_scan_task", lambda scan_id, **kwargs: None):
            first = test_client.post(f"{SCANS}/start", json={}, headers=headers)
            scan_id = first.json()["scan_id"]
            cancel = test_client.delete(f"{SCANS}/{scan_id}", headers=headers)
            assert cancel.status_code == 200
            assert cancel.json()["status"] == "cancelled"
            again = test_client.post(f"{SCANS}/start", json={}, headers=headers)
            assert again.status_code == 202

    def test_cancel_finished_scan_conflicts(self, client) -> None:
        test_client, _ = client
        headers = _register_and_login(test_client)
        with (
            patch("app.tasks.scan_task._COLLECTOR_REGISTRY", {"s3": _StaticCollector}),
            patch(
                "app.tasks.scan_task.MisconfigurationOrchestrator",
                lambda: _static_analyzer_factory([]),
            ),
        ):
            scan_id = test_client.post(
                f"{SCANS}/start", json={"services": ["s3"]}, headers=headers
            ).json()["scan_id"]
        resp = test_client.delete(f"{SCANS}/{scan_id}", headers=headers)
        assert resp.status_code == 409


class TestScanReads:
    def _completed_scan(self, test_client, headers) -> str:
        with (
            patch("app.tasks.scan_task._COLLECTOR_REGISTRY", {"s3": _StaticCollector}),
            patch(
                "app.tasks.scan_task.MisconfigurationOrchestrator",
                lambda: _static_analyzer_factory([_raw()]),
            ),
        ):
            return test_client.post(
                f"{SCANS}/start", json={"services": ["s3"]}, headers=headers
            ).json()["scan_id"]

    def test_list_shows_own_scans_only(self, client) -> None:
        test_client, _ = client
        headers_a = _register_and_login(test_client, "a@x.io")
        headers_b = _register_and_login(test_client, "b@x.io")
        self._completed_scan(test_client, headers_a)

        list_a = test_client.get(f"{SCANS}", headers=headers_a).json()
        assert list_a["total"] == 1
        list_b = test_client.get(f"{SCANS}", headers=headers_b).json()
        assert list_b["total"] == 0

    def test_results_include_scan_and_summary(self, client) -> None:
        test_client, _ = client
        headers = _register_and_login(test_client)
        scan_id = self._completed_scan(test_client, headers)

        results = test_client.get(f"{SCANS}/{scan_id}/results", headers=headers)
        assert results.status_code == 200
        body = results.json()
        assert body["scan"]["scan_id"] == scan_id
        assert body["summary"]["total_findings"] == 1

    def test_other_users_scan_is_404(self, client) -> None:
        test_client, _ = client
        headers_a = _register_and_login(test_client, "owner@x.io")
        headers_b = _register_and_login(test_client, "intruder@x.io")
        scan_id = self._completed_scan(test_client, headers_a)

        for path in ("status", "summary", "results"):
            resp = test_client.get(f"{SCANS}/{scan_id}/{path}", headers=headers_b)
            assert resp.status_code == 404, path
        assert test_client.delete(f"{SCANS}/{scan_id}", headers=headers_b).status_code == 404

    def test_unknown_scan_is_404(self, client) -> None:
        test_client, _ = client
        headers = _register_and_login(test_client)
        assert test_client.get(f"{SCANS}/scn_nope/status", headers=headers).status_code == 404
