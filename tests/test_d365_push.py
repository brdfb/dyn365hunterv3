"""Tests for D365 push integration (Faz 1: Skeleton + Phase 2.5: Validation)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings


@pytest.fixture
def client():
    """Test client."""
    return TestClient(app)


@pytest.fixture
def mock_d365_enabled(monkeypatch):
    """Mock D365 enabled flag."""
    monkeypatch.setattr(settings, "d365_enabled", True)


@pytest.fixture
def mock_d365_disabled(monkeypatch):
    """Mock D365 disabled flag."""
    monkeypatch.setattr(settings, "d365_enabled", False)


def test_d365_push_endpoint_disabled(client, mock_d365_disabled):
    """Test D365 push endpoint returns 403 when disabled."""
    response = client.post(
        "/api/v1/d365/push-lead",
        json={"lead_id": 1}
    )
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"].lower()


def test_d365_push_endpoint_missing_params(client, mock_d365_enabled):
    """Test D365 push endpoint returns 400 when both lead_id and domain are missing."""
    response = client.post(
        "/api/v1/d365/push-lead",
        json={}
    )
    assert response.status_code == 400
    assert "lead_id" in response.json()["detail"].lower() or "domain" in response.json()["detail"].lower()


def test_d365_push_endpoint_enqueues_task(client, mock_d365_enabled):
    """Test D365 push endpoint enqueues task and returns 202 Accepted."""
    from unittest.mock import patch, MagicMock
    
    with patch("app.api.v1.d365_routes.push_lead_to_d365") as mock_task:
        mock_task_result = MagicMock()
        mock_task_result.id = "test-job-id-123"
        mock_task.delay.return_value = mock_task_result
        
        response = client.post(
            "/api/v1/d365/push-lead",
            json={"lead_id": 1}
        )
        
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        assert data["job_id"] == "test-job-id-123"
        mock_task.delay.assert_called_once_with(1)


def test_d365_push_endpoint_domain_not_implemented(client, mock_d365_enabled):
    """Test D365 push endpoint with domain (not yet implemented)."""
    response = client.post(
        "/api/v1/d365/push-lead",
        json={"domain": "example.com"}
    )
    # Domain-based push not yet implemented
    assert response.status_code == 501

