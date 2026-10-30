"""
Unit tests for user onboarding endpoints and credential validation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.jwt import create_access_token
from app.database.base import Base
from app.database.models import User, UserIntegration
from app.database.session import get_db
from app.main import app


@pytest.fixture
def onboarding_setup():
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

    user = User(
        email="onboard_tester@example.com",
        hashed_password="hashed_pw",
        full_name="Onboarding Tester",
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_access_token(user.id, extra_claims={"role": user.role})
    headers = {"Authorization": f"Bearer {token}"}

    yield client, session, user, headers

    app.dependency_overrides.clear()


def test_get_iam_policy(onboarding_setup):
    client, _, _, headers = onboarding_setup
    resp = client.get("/api/v1/onboarding/iam-policy", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "Statement" in data
    assert data.get("Version") == "2012-10-17"


def test_onboarding_status_unconfigured(onboarding_setup):
    client, _, _, headers = onboarding_setup
    resp = client.get("/api/v1/onboarding/status", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_onboarded"] is False
    assert data["aws_configured"] is False


def test_validate_ai_bedrock(onboarding_setup):
    client, _, _, headers = onboarding_setup
    resp = client.post(
        "/api/v1/onboarding/validate-ai",
        headers=headers,
        json={"provider": "bedrock"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is True
    assert data["provider"] == "bedrock"


def test_validate_ai_invalid_openai(onboarding_setup):
    client, _, _, headers = onboarding_setup
    resp = client.post(
        "/api/v1/onboarding/validate-ai",
        headers=headers,
        json={"provider": "openai", "api_key": "not-a-valid-key"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is False
    assert "must start with sk-" in data["error_message"].lower()


def test_save_onboarding_invalid_credentials_blocks_user(onboarding_setup):
    client, _, _, headers = onboarding_setup
    payload = {
        "aws_access_key_id": "AKIAINVALIDKEYTEST1",
        "aws_secret_access_key": "secret_key_that_is_long_enough",
        "region": "us-east-1",
        "ai_provider": "bedrock",
        "trigger_initial_scan": False,
    }
    resp = client.post("/api/v1/onboarding/complete", headers=headers, json=payload)
    assert resp.status_code == 400
    assert "AWS credential validation failed" in resp.json()["detail"]


def test_onboarding_status_when_configured(onboarding_setup):
    client, session, user, headers = onboarding_setup
    integ = UserIntegration(
        user_id=user.id,
        aws_account_id="123456789012",
        aws_caller_arn="arn:aws:iam::123456789012:user/tester",
        aws_access_key_id="AKIAEXAMPLEMOCKKEY1",
        aws_secret_access_key="mocksecret",
        aws_default_region="us-east-1",
        ai_provider="bedrock",
        is_onboarded=True,
    )
    session.add(integ)
    session.commit()

    resp = client.get("/api/v1/onboarding/status", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_onboarded"] is True
    assert data["aws_configured"] is True
    assert data["aws_account_id"] == "123456789012"
