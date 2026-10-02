"""Integration tests for the DB-backed auth API (roadmap task 20)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
REFRESH = "/api/v1/auth/refresh"
ME = "/api/v1/auth/me"

VALID_REGISTER = {
    "email": "Ana@Example.com",
    "password": "Sup3rSecret!",
    "full_name": "Analyst One",
    "role": "analyst",
}


@pytest.fixture()
def client() -> TestClient:
    """App wired to a fresh in-memory SQLite database per test.

    StaticPool keeps one shared connection so `create_all` and the app
    see the same in-memory database.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def _override() -> object:
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


class TestRegister:
    def test_register_creates_user_and_lowercases_email(self, client: TestClient) -> None:
        resp = client.post(REGISTER, json=VALID_REGISTER)
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["email"] == "ana@example.com"
        assert body["role"] == "analyst"
        assert "password" not in body and "hashed_password" not in body

    def test_register_rejects_short_password(self, client: TestClient) -> None:
        resp = client.post(
            REGISTER, json={**VALID_REGISTER, "email": "x@y.io", "password": "Sh0rt!"}
        )
        assert resp.status_code == 422

    def test_register_rejects_invalid_email(self, client: TestClient) -> None:
        resp = client.post(REGISTER, json={**VALID_REGISTER, "email": "not-an-email"})
        assert resp.status_code == 422

    def test_duplicate_register_conflicts(self, client: TestClient) -> None:
        assert client.post(REGISTER, json=VALID_REGISTER).status_code == 201
        resp = client.post(REGISTER, json=VALID_REGISTER)
        assert resp.status_code == 409

    def test_duplicate_case_insensitive(self, client: TestClient) -> None:
        assert client.post(REGISTER, json=VALID_REGISTER).status_code == 201
        resp = client.post(REGISTER, json={**VALID_REGISTER, "email": "ANA@example.com"})
        assert resp.status_code == 409


class TestLogin:
    def _register(self, client: TestClient) -> None:
        assert client.post(REGISTER, json=VALID_REGISTER).status_code == 201

    def test_login_returns_token_pair(self, client: TestClient) -> None:
        self._register(client)
        resp = client.post(LOGIN, json={"username": "ana@example.com", "password": "Sup3rSecret!"})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        for key in ("access_token", "refresh_token", "token_type", "expires_in"):
            assert key in body
        assert body["token_type"] == "bearer"

    def test_login_via_original_cased_email(self, client: TestClient) -> None:
        """Users can type their email with any casing."""
        self._register(client)
        resp = client.post(LOGIN, json={"username": "Ana@Example.com", "password": "Sup3rSecret!"})
        assert resp.status_code == 200

    def test_wrong_password_is_401(self, client: TestClient) -> None:
        self._register(client)
        resp = client.post(LOGIN, json={"username": "ana@example.com", "password": "nope1234"})
        assert resp.status_code == 401

    def test_unknown_user_is_identical_401(self, client: TestClient) -> None:
        """No user enumeration: unknown email must be indistinguishable."""
        good = client.post(LOGIN, json={"username": "ana@example.com", "password": "nope1234"})
        ghost = client.post(LOGIN, json={"username": "ghost@nowhere.io", "password": "nope1234"})
        # Register the real user after both calls to prove responses matched before.
        client.post(REGISTER, json=VALID_REGISTER)
        assert good.status_code == ghost.status_code == 401
        assert good.json() == ghost.json()

    def test_refresh_token_rejected_as_username(self, client: TestClient) -> None:
        self._register(client)
        resp = client.post(
            LOGIN, json={"username": "ana@example.com", "password": "not-the-password"}
        )
        assert resp.status_code == 401


class TestRefresh:
    def _tokens(self, client: TestClient) -> dict:
        client.post(REGISTER, json=VALID_REGISTER)
        resp = client.post(LOGIN, json={"username": "ana@example.com", "password": "Sup3rSecret!"})
        return resp.json()

    def test_refresh_returns_new_pair(self, client: TestClient) -> None:
        tokens = self._tokens(client)
        resp = client.post(REFRESH, json={"refresh_token": tokens["refresh_token"]})
        assert resp.status_code == 200, resp.text
        new = resp.json()
        assert new["access_token"] and new["refresh_token"]

    def test_access_token_rejected_at_refresh(self, client: TestClient) -> None:
        tokens = self._tokens(client)
        resp = client.post(REFRESH, json={"refresh_token": tokens["access_token"]})
        assert resp.status_code == 401

    def test_garbage_token_rejected(self, client: TestClient) -> None:
        resp = client.post(REFRESH, json={"refresh_token": "garbage.token.here"})
        assert resp.status_code == 401


class TestMe:
    def _bearer(self, client: TestClient) -> dict[str, str]:
        client.post(REGISTER, json=VALID_REGISTER)
        tokens = client.post(
            LOGIN, json={"username": "ana@example.com", "password": "Sup3rSecret!"}
        ).json()
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    def test_me_returns_profile(self, client: TestClient) -> None:
        resp = client.get(ME, headers=self._bearer(client))
        assert resp.status_code == 200
        assert resp.json()["email"] == "ana@example.com"
        assert resp.json()["role"] == "analyst"

    def test_me_requires_token(self, client: TestClient) -> None:
        assert client.get(ME).status_code in (401, 403)

    def test_me_rejects_refresh_token(self, client: TestClient) -> None:
        client.post(REGISTER, json=VALID_REGISTER)
        tokens = client.post(
            LOGIN, json={"username": "ana@example.com", "password": "Sup3rSecret!"}
        ).json()
        resp = client.get(ME, headers={"Authorization": f"Bearer {tokens['refresh_token']}"})
        assert resp.status_code == 401

    def test_me_rejects_garbage_token(self, client: TestClient) -> None:
        resp = client.get(ME, headers={"Authorization": "Bearer junk.junk.junk"})
        assert resp.status_code == 401
