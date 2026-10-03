"""Integration tests for the findings API (roadmap tasks 10-13).

Creates users + scans + findings directly through repositories, then
exercises the HTTP surface: scoping, filters, pagination, stats, and the
resolve/reopen lifecycle.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.analyzers import RawFinding
from app.core.constants import Severity
from app.database.base import Base
from app.database.models import User
from app.database.repositories import FindingRepository, ScanRepository
from app.database.session import get_db

FINDINGS = "/api/v1/findings"


@pytest.fixture()
def env():
    """App + DB + two users with distinct scans/findings."""
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

    # Seed: alice (2 scans), bob (1 scan), each with distinguishable findings.
    with factory() as db:
        db.add_all(
            [
                User(id="usr_alice", email="alice@x.io", hashed_password="x", role="analyst"),
                User(id="usr_bob", email="bob@x.io", hashed_password="x", role="analyst"),
                User(id="usr_admin", email="admin@x.io", hashed_password="x", role="admin"),
            ]
        )
        db.commit()

        alice_scans = [ScanRepository(db).create(user_id="usr_alice") for _ in range(2)]
        bob_scan = ScanRepository(db).create(user_id="usr_bob")

        def _raw(rule: str, severity: Severity, arn: str) -> RawFinding:
            return RawFinding(
                rule_id=rule,
                title=f"Issue {rule}",
                description="d",
                severity=severity,
                resource_type="s3_bucket",
                resource_id=arn,
                resource_arn=arn,
            )

        fr = FindingRepository(db)
        fr.bulk_create_from_raw(
            alice_scans[0].id,
            [
                _raw("R-CRIT-1", Severity.CRITICAL, "arn:a1"),
                _raw("R-HIGH-1", Severity.HIGH, "arn:a2"),
            ],
        )
        fr.bulk_create_from_raw(
            alice_scans[1].id,
            [
                _raw("R-HIGH-2", Severity.HIGH, "arn:a3"),
                _raw("R-LOW-1", Severity.LOW, "arn:a4"),
            ],
        )
        fr.bulk_create_from_raw(bob_scan.id, [_raw("R-CRIT-2", Severity.CRITICAL, "arn:b1")])
        ids = {
            "alice_scans": [s.id for s in alice_scans],
            "bob_scan": bob_scan.id,
        }

    with TestClient(app) as test_client:
        yield test_client, factory, ids
    app.dependency_overrides.pop(get_db, None)
    engine.dispose()


def _token_for(client: TestClient, email: str) -> dict[str, str]:
    # Users are seeded directly (no register endpoint hit), so mint tokens
    # through the login endpoint using a registered password is impossible;
    # instead we mint via the JWT utility as the test subject.
    from app.auth.jwt import create_token_pair

    subject = {"alice@x.io": "usr_alice", "bob@x.io": "usr_bob", "admin@x.io": "usr_admin"}[email]
    pair = create_token_pair(subject, {"role": email.split("@")[0]})
    return {"Authorization": f"Bearer {pair.access_token}"}


class TestListFindings:
    def test_user_sees_only_own_scans_findings(self, env) -> None:
        client, _, _ = env
        headers = _token_for(client, "alice@x.io")
        body = client.get(FINDINGS, headers=headers).json()
        assert body["total"] == 4
        arns = {f["resource_arn"] for f in body["findings"]}
        assert arns == {"arn:a1", "arn:a2", "arn:a3", "arn:a4"}

    def test_severity_filter(self, env) -> None:
        client, _, _ = env
        headers = _token_for(client, "alice@x.io")
        body = client.get(f"{FINDINGS}?severity=high", headers=headers).json()
        assert body["total"] == 2
        assert {f["rule_id"] for f in body["findings"]} == {"R-HIGH-1", "R-HIGH-2"}

    def test_scan_filter(self, env) -> None:
        client, _, ids = env
        headers = _token_for(client, "alice@x.io")
        body = client.get(f"{FINDINGS}?scan_id={ids['alice_scans'][1]}", headers=headers).json()
        assert body["total"] == 2
        assert {f["rule_id"] for f in body["findings"]} == {"R-HIGH-2", "R-LOW-1"}

    def test_pagination(self, env) -> None:
        client, _, _ = env
        headers = _token_for(client, "alice@x.io")
        page1 = client.get(f"{FINDINGS}?limit=3&page=1", headers=headers).json()
        assert page1["total"] == 4
        assert len(page1["findings"]) == 3
        page2 = client.get(f"{FINDINGS}?limit=3&page=2", headers=headers).json()
        assert len(page2["findings"]) == 1
        ids1 = {f["id"] for f in page1["findings"]}
        ids2 = {f["id"] for f in page2["findings"]}
        assert ids1.isdisjoint(ids2)

    def test_other_users_scan_filter_yields_empty(self, env) -> None:
        client, _, ids = env
        headers = _token_for(client, "alice@x.io")
        body = client.get(f"{FINDINGS}?scan_id={ids['bob_scan']}", headers=headers).json()
        assert body["total"] == 0
        assert body["findings"] == []

    def test_admin_sees_all(self, env) -> None:
        client, _, _ = env
        headers = _token_for(client, "admin@x.io")
        body = client.get(FINDINGS, headers=headers).json()
        assert body["total"] == 5

    def test_requires_auth(self, env) -> None:
        client, _, _ = env
        assert client.get(FINDINGS).status_code in (401, 403)


class TestDetailAndStats:
    def test_detail_for_owner(self, env) -> None:
        client, _, _ = env
        headers = _token_for(client, "alice@x.io")
        listing = client.get(f"{FINDINGS}?severity=critical", headers=headers).json()
        finding_id = listing["findings"][0]["id"]
        detail = client.get(f"{FINDINGS}/{finding_id}", headers=headers)
        assert detail.status_code == 200
        assert detail.json()["rule_id"] == "R-CRIT-1"

    def test_detail_of_other_user_404(self, env) -> None:
        client, _, _ = env
        bob_headers = _token_for(client, "bob@x.io")
        listing = client.get(FINDINGS, headers=bob_headers).json()
        finding_id = listing["findings"][0]["id"]

        alice_headers = _token_for(client, "alice@x.io")
        resp = client.get(f"{FINDINGS}/{finding_id}", headers=alice_headers)
        assert resp.status_code == 404

    def test_stats_scoped_to_user(self, env) -> None:
        client, _, _ = env
        headers = _token_for(client, "alice@x.io")
        stats = client.get(f"{FINDINGS}/stats/summary", headers=headers).json()
        assert stats["critical"] == 1
        assert stats["high"] == 2
        assert stats["low"] == 1
        assert stats["total"] == 4

    def test_stats_scoped_to_scan(self, env) -> None:
        client, _, ids = env
        headers = _token_for(client, "alice@x.io")
        stats = client.get(
            f"{FINDINGS}/stats/summary?scan_id={ids['alice_scans'][0]}", headers=headers
        ).json()
        assert stats["critical"] == 1
        assert stats["total"] == 2


class TestResolve:
    def _alice_finding(self, client) -> str:
        headers = _token_for(client, "alice@x.io")
        listing = client.get(FINDINGS, headers=headers).json()
        return listing["findings"][0]["id"]

    def test_resolve_and_reopen(self, env) -> None:
        client, _, _ = env
        headers = _token_for(client, "alice@x.io")
        finding_id = self._alice_finding(client)

        resolved = client.patch(
            f"{FINDINGS}/{finding_id}", json={"status": "resolved"}, headers=headers
        )
        assert resolved.status_code == 200
        assert resolved.json()["status"] == "resolved"

        reopened = client.patch(
            f"{FINDINGS}/{finding_id}", json={"status": "open"}, headers=headers
        )
        assert reopened.status_code == 200
        assert reopened.json()["status"] == "open"

    def test_invalid_status_rejected(self, env) -> None:
        client, _, _ = env
        headers = _token_for(client, "alice@x.io")
        finding_id = self._alice_finding(client)
        resp = client.patch(
            f"{FINDINGS}/{finding_id}", json={"status": "yeeted"}, headers=headers
        )
        assert resp.status_code == 422

    def test_cannot_resolve_other_users_finding(self, env) -> None:
        client, _, _ = env
        bob_headers = _token_for(client, "bob@x.io")
        finding_id = client.get(FINDINGS, headers=bob_headers).json()["findings"][0]["id"]
        alice_headers = _token_for(client, "alice@x.io")
        resp = client.patch(
            f"{FINDINGS}/{finding_id}", json={"status": "resolved"}, headers=alice_headers
        )
        assert resp.status_code == 404
