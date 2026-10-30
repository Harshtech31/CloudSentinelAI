"""
Unit tests for the health check and readiness endpoints.
"""

from fastapi.testclient import TestClient


def test_health_check_endpoint(client: TestClient):
    """Verify /api/v1/health returns 200 OK and expected status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "service" in data


def test_readiness_check_endpoint(client: TestClient):
    """Verify /api/v1/health/ready returns 200 OK and component statuses."""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "components" in data
    assert data["components"]["api"] == "healthy"


def test_root_endpoint(client: TestClient):
    """Verify root / returns 200 OK with service info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "docs" in data


def test_deep_health_check_endpoint(client: TestClient):
    """Verify /api/v1/health/deep returns 200 OK and deep diagnostics."""
    response = client.get("/api/v1/health/deep")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert "database" in data
    assert "ai_provider" in data
    assert "components" in data


def test_version_endpoint(client: TestClient):
    """Verify /api/v1/version returns 200 OK with semantic version."""
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["service"] == "CloudSentinel AI"


def test_eval_scenarios_endpoint(client: TestClient):
    """Verify /api/v1/eval/scenarios loads cataloged evaluation scenarios."""
    response = client.get("/api/v1/eval/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert "scenarios" in data
    assert len(data["scenarios"]) >= 3
    scenario_ids = [s["id"] for s in data["scenarios"]]
    assert "S1" in scenario_ids
    assert "S2" in scenario_ids
