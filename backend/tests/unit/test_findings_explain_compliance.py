"""
Unit tests for Finding AI Explanation and Compliance Report REST endpoints.
"""

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.jwt import create_access_token
from app.core.constants import CloudProvider, ScanStatus, Severity
from app.database.base import Base
from app.database.models import Finding, Scan, User
from app.database.session import get_db
from app.main import app


@pytest.fixture
def test_setup():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = TestingSession()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    user = User(email="analyst@example.com", hashed_password="pw", full_name="Analyst", is_active=True)
    session.add(user)
    session.commit()
    session.refresh(user)

    scan = Scan(id="scn_exp_test", user_id=user.id, target_cloud=CloudProvider.AWS, status=ScanStatus.COMPLETED)
    session.add(scan)
    session.commit()

    finding = Finding(
        id="fnd_test_exp_1",
        scan_id=scan.id,
        rule_id="AWS-IAM-001",
        title="MFA Not Enabled on User",
        description="IAM user alice lacks MFA.",
        severity=Severity.HIGH,
        risk_score=7.5,
        resource_type="AWS::IAM::User",
        resource_id="alice",
        remediation="Enable virtual MFA in AWS Console.",
        status="open",
    )
    session.add(finding)
    session.commit()

    token = create_access_token(user.id, extra_claims={"role": user.role})
    headers = {"Authorization": f"Bearer {token}"}

    yield client, headers, scan.id, finding.id

    session.close()
    app.dependency_overrides.pop(get_db, None)


def test_get_compliance_report(test_setup):
    client, headers, scan_id, finding_id = test_setup

    res = client.get(f"/api/v1/findings/compliance-report?scan_id={scan_id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "compliance_score" in data
    assert data["total_controls"] >= 20
    assert "controls" in data
    # Control 1.5 should be marked FAILED because AWS-IAM-001 is open
    ctrl_1_5 = next(c for c in data["controls"] if c["control_id"] == "1.5")
    assert ctrl_1_5["status"] == "FAILED"


def test_post_finding_explain(test_setup):
    client, headers, scan_id, finding_id = test_setup

    res = client.post(f"/api/v1/findings/{finding_id}/explain", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["finding_id"] == finding_id
    assert "explanation" in data
    assert len(data["explanation"]) > 0
    assert "remediation_steps" in data
    assert len(data["remediation_steps"]) > 0
