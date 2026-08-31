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
