"""End-to-end scan flow (roadmap task 22).

The complete user journey over real HTTP with the real background task:
register → login → start scan → poll → results → findings → stats →
dashboard. Mock collector/analyzer stand in for AWS (Member 2's track);
everything else — auth, routing, orchestrator, repositories, aggregates —
is the production code path.
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


@pytest.fixture()
def client():
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
        yield test_client
    app.dependency_overrides.pop(get_db, None)
    engine.dispose()


class _FakeAwsCollector(BaseCollector):
    """Simulates a small AWS account: 2 buckets + 1 user."""

    provider = "aws"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def collect(self) -> dict[str, list[dict]]:
        return {
            "s3_buckets": [
                {"arn": "arn:aws:s3:::acme-logs", "name": "acme-logs", "region": "us-east-1"},
                {"arn": "arn:aws:s3:::acme-pci", "name": "acme-pci", "region": "us-east-1"},
            ],
            "iam_users": [{"arn": "arn:aws:iam::1:user/dev", "name": "dev"}],
        }


def _fake_analyzer():
    class _A:
        def run(self, resources) -> list[RawFinding]:
            buckets = resources.get("s3_buckets", [])
            return [
                RawFinding(
                    rule_id="AWS-S3-PUBLIC",
                    title="Public S3 bucket",
                    description="Bucket allows public reads.",
                    severity="critical",
                    resource_type="s3_bucket",
                    resource_id=b["arn"],
                    resource_arn=b["arn"],
                    region=b.get("region"),
                    remediation="Enable Block Public Access.",
                )
                for b in buckets
                if b["name"] == "acme-pci"
            ]

    return _A()


def _register_login(client: TestClient) -> dict[str, str]:
    assert (
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "journey@user.io",
                "password": "Sup3rSecret!",
                "full_name": "Journey Analyst",
                "role": "analyst",
            },
        ).status_code
        == 201
    )
    tokens = client.post(
        "/api/v1/auth/login", json={"username": "journey@user.io", "password": "Sup3rSecret!"}
    ).json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_full_scan_journey(client: TestClient) -> None:
    headers = _register_login(client)

    # 1. Dashboard before any scan: neutral posture.
    before = client.get("/api/v1/dashboard/summary", headers=headers).json()
    assert before["security_score"] == 100.0

    # 2. Start a scan of the fake account.
    with (
        patch("app.tasks.scan_task._COLLECTOR_REGISTRY", {"s3": _FakeAwsCollector}),
        patch("app.tasks.scan_task.MisconfigurationOrchestrator", lambda: _fake_analyzer()),
    ):
        started = client.post(
            "/api/v1/scan/start",
            json={"services": ["s3"]},
            headers=headers,
        )
    assert started.status_code == 202
    scan_id = started.json()["scan_id"]

    # 3. Poll to completion (background task runs synchronously post-response).
    status_body = client.get(f"/api/v1/scan/{scan_id}/status", headers=headers).json()
    assert status_body["status"] == "completed"
    assert status_body["progress_percentage"] == 100

    # 4. Scan list shows the row with duration and resource count.
    listing = client.get("/api/v1/scan", headers=headers).json()
    assert listing["total"] == 1
    row = listing["scans"][0]
    assert row["scan_id"] == scan_id
    assert row["duration_seconds"] is not None

    # 5. Summary + results: 3 resources scanned, 1 critical finding.
    summary = client.get(f"/api/v1/scan/{scan_id}/summary", headers=headers).json()
    assert summary["total_findings"] == 1
    assert summary["critical_findings"] == 1
    results = client.get(f"/api/v1/scan/{scan_id}/results", headers=headers).json()
    assert results["scan"]["scan_id"] == scan_id

    # 6. Findings API: filter by severity, open detail, resolve it.
    findings = client.get(
        "/api/v1/findings", params={"severity": "critical"}, headers=headers
    ).json()
    assert findings["total"] == 1
    finding_id = findings["findings"][0]["id"]
    assert findings["findings"][0]["resource_arn"] == "arn:aws:s3:::acme-pci"

    resolved = client.patch(
        f"/api/v1/findings/{finding_id}", json={"status": "resolved"}, headers=headers
    )
    assert resolved.json()["status"] == "resolved"

    # 7. Stats reflect severity mix; dashboard now shows risk.
    stats = client.get("/api/v1/findings/stats/summary", headers=headers).json()
    assert stats["critical"] == 1 and stats["total"] == 1

    dashboard = client.get("/api/v1/dashboard/summary", headers=headers).json()
    assert dashboard["scanned_resources"] == 3
    # 1 completed scan, 1 critical → 100 - 10 = 90.
    assert dashboard["security_score"] == 90.0

    # 8. Rate limit: a running scan blocks a second start... but this one is
    # completed, so starting again works, then cancellation ends it.
    with patch("app.api.v1.scan.run_scan_task", lambda scan_id, **kwargs: None):
        second = client.post("/api/v1/scan/start", json={}, headers=headers)
        assert second.status_code == 202
        cancelled = client.delete(f"/api/v1/scan/{second.json()['scan_id']}", headers=headers)
        assert cancelled.json()["status"] == "cancelled"

    # 9. Third start now allowed (cancelled scans don't block).
    with patch("app.api.v1.scan.run_scan_task", lambda scan_id, **kwargs: None):
        assert client.post("/api/v1/scan/start", json={}, headers=headers).status_code == 202
