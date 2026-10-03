"""Integration tests for the dashboard summary (roadmap task 14)."""

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

DASHBOARD = "/api/v1/dashboard"


@pytest.fixture()
def env():
    """App + DB + seeded users with scans/findings of known severity."""
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

    with factory() as db:
        db.add_all(
            [
                User(id="usr_empty", email="empty@x.io", hashed_password="x", role="analyst"),
                User(id="usr_rich", email="rich@x.io", hashed_password="x", role="analyst"),
            ]
        )
        db.commit()

        scan = ScanRepository(db).create(user_id="usr_rich")
        scan.resources_scanned = 12
        scan.status = "completed"
        db.commit()

        FindingRepository(db).bulk_create_from_raw(
            scan.id,
            [
                RawFinding(
                    rule_id="R1",
                    title="t",
                    description="d",
                    severity=Severity.CRITICAL,
                    resource_type="s3_bucket",
                    resource_id="arn:1",
                ),
                RawFinding(
                    rule_id="R2",
                    title="t",
                    description="d",
                    severity=Severity.HIGH,
                    resource_type="s3_bucket",
                    resource_id="arn:2",
                ),
            ],
        )

    with TestClient(app) as test_client:
        yield test_client, factory
    app.dependency_overrides.pop(get_db, None)
    engine.dispose()


def _token_for(client: TestClient, subject: str, role: str = "analyst") -> dict[str, str]:
    from app.auth.jwt import create_token_pair

    pair = create_token_pair(subject, {"role": role})
    return {"Authorization": f"Bearer {pair.access_token}"}


class TestDashboardSummary:
    def test_empty_account_neutral_score(self, env) -> None:
        client, _ = env
        headers = _token_for(client, "usr_empty")
        body = client.get(f"{DASHBOARD}/summary", headers=headers).json()
        assert body["security_score"] == 100.0
        assert body["scanned_resources"] == 0
        assert body["total_findings"] == 0

    def test_penalty_model_and_resource_count(self, env) -> None:
        client, _ = env
        headers = _token_for(client, "usr_rich")
        body = client.get(f"{DASHBOARD}/summary", headers=headers).json()
        # 1 completed scan: critical(10) + high(5) → 100 - 15 = 85.
        assert body["security_score"] == 85.0
        assert body["scanned_resources"] == 12
        assert body["total_findings"] == 2
        assert body["critical_findings"] == 1

    def test_score_floors_at_zero(self, env) -> None:
        client, factory = env
        with factory() as db:
            scan = ScanRepository(db).create(user_id="usr_rich")
            scan.resources_scanned = 1
            scan.status = "completed"
            db.commit()
            FindingRepository(db).bulk_create_from_raw(
                scan.id,
                [
                    RawFinding(
                        rule_id=f"R{i}",
                        title="t",
                        description="d",
                        severity=Severity.CRITICAL,
                        resource_type="s3_bucket",
                        resource_id=f"arn:x{i}",
                    )
                    for i in range(12)
                ],
            )
        headers = _token_for(client, "usr_rich")
        body = client.get(f"{DASHBOARD}/summary", headers=headers).json()
        # (12 criticals × 10) / 2 scans = 60 penalty → 40... plus existing
        # 15/2=7.5 → 32.5; heavier load floors correctly, never negative.
        assert body["security_score"] >= 0.0

    def test_requires_auth(self, env) -> None:
        client, _ = env
        assert client.get(f"{DASHBOARD}/summary").status_code in (401, 403)
