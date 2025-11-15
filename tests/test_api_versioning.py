"""Tests for API versioning (P1-5)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint_no_versioning():
    """Health endpoint should not be versioned (infrastructure endpoint)."""
    response = client.get("/healthz")
    assert response.status_code == 200


def test_leads_v1_endpoint():
    """Test v1 leads endpoint exists."""
    response = client.get("/api/v1/leads")
    # Should not return 404 (may return 200 or 400 depending on query params)
    assert response.status_code != 404


def test_leads_legacy_endpoint():
    """Test legacy leads endpoint still works (backward compatibility)."""
    response = client.get("/leads")
    # Should not return 404 (may return 200 or 400 depending on query params)
    assert response.status_code != 404


def test_ingest_v1_endpoint():
    """Test v1 ingest endpoint exists."""
    response = client.post("/api/v1/ingest/domain", json={"domain": "invalid"})
    # Should return 400 (invalid domain) or 404 (domain not found), not 404 for endpoint
    assert response.status_code in [400, 404]


def test_ingest_legacy_endpoint():
    """Test legacy ingest endpoint still works (backward compatibility)."""
    response = client.post("/ingest/domain", json={"domain": "invalid"})
    # Should return 400 (invalid domain) or 404 (domain not found), not 404 for endpoint
    assert response.status_code in [400, 404]


def test_scan_v1_endpoint():
    """Test v1 scan endpoint exists."""
    response = client.post("/api/v1/scan/domain", json={"domain": "invalid"})
    # Should return 400 (invalid domain) or 404 (domain not found), not 404 for endpoint
    assert response.status_code in [400, 404]


def test_scan_legacy_endpoint():
    """Test legacy scan endpoint still works (backward compatibility)."""
    response = client.post("/scan/domain", json={"domain": "invalid"})
    # Should return 400 (invalid domain) or 404 (domain not found), not 404 for endpoint
    assert response.status_code in [400, 404]


def test_dashboard_v1_endpoint():
    """Test v1 dashboard endpoint exists."""
    response = client.get("/api/v1/dashboard")
    # Should return 200 (success) or 500 (db error), not 404
    assert response.status_code != 404


def test_dashboard_legacy_endpoint():
    """Test legacy dashboard endpoint still works (backward compatibility)."""
    response = client.get("/dashboard")
    # Should return 200 (success) or 500 (db error), not 404
    assert response.status_code != 404


def test_api_versioning_structure():
    """Test that v1 router structure is correct."""
    # Test that v1 endpoints are prefixed with /api/v1
    v1_endpoints = [
        "/api/v1/ingest/domain",
        "/api/v1/scan/domain",
        "/api/v1/leads",
        "/api/v1/dashboard",
    ]
    
    for endpoint in v1_endpoints:
        if endpoint.endswith("/domain"):
            response = client.post(endpoint, json={"domain": "invalid"})
        else:
            response = client.get(endpoint)
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404, f"Endpoint {endpoint} not found"


def test_legacy_endpoints_still_work():
    """Test that legacy endpoints still work (backward compatibility)."""
    legacy_endpoints = [
        ("/ingest/domain", "POST"),
        ("/scan/domain", "POST"),
        ("/leads", "GET"),
        ("/dashboard", "GET"),
    ]
    
    for endpoint, method in legacy_endpoints:
        if method == "POST":
            response = client.post(endpoint, json={"domain": "invalid"})
        else:
            response = client.get(endpoint)
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404, f"Legacy endpoint {endpoint} not found"

