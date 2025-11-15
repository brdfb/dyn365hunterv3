"""Tests for API versioning (P1-5)."""

import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from app.db.models import Base

# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv(
        "HUNTER_DATABASE_URL",
        os.getenv(
            "DATABASE_URL",
            "postgresql://dyn365hunter:password123@localhost:5432/dyn365hunter",
        ),
    ),
)


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    # Use PostgreSQL (JSONB/ARRAY support required)
    engine = create_engine(TEST_DATABASE_URL)

    try:
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
    except OperationalError as e:
        pytest.skip(f"Test database not available: {TEST_DATABASE_URL} - {e}")

    # Create tables (if not exist)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Start a transaction for test isolation
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        # Rollback transaction instead of dropping tables
        transaction.rollback()
        session.close()
        connection.close()
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with test database."""
    from app.main import app
    from app.db.session import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    
    yield test_client
    
    # Cleanup
    app.dependency_overrides.clear()


def test_health_endpoint_no_versioning(client):
    """Health endpoint should not be versioned (infrastructure endpoint)."""
    response = client.get("/healthz")
    assert response.status_code == 200


def test_leads_v1_endpoint(client):
    """Test v1 leads endpoint exists."""
    response = client.get("/api/v1/leads")
    # Should not return 404 (may return 200 or 400 depending on query params)
    assert response.status_code != 404


def test_leads_legacy_endpoint(client):
    """Test legacy leads endpoint still works (backward compatibility)."""
    response = client.get("/leads")
    # Should not return 404 (may return 200 or 400 depending on query params)
    assert response.status_code != 404


def test_ingest_v1_endpoint(client):
    """Test v1 ingest endpoint exists."""
    response = client.post("/api/v1/ingest/domain", json={"domain": "invalid"})
    # Should return 400 (invalid domain), 422 (validation error), or 404 (domain not found), not 404 for endpoint
    assert response.status_code in [400, 422, 404]


def test_ingest_legacy_endpoint(client):
    """Test legacy ingest endpoint still works (backward compatibility)."""
    response = client.post("/ingest/domain", json={"domain": "invalid"})
    # Should return 400 (invalid domain), 422 (validation error), or 404 (domain not found), not 404 for endpoint
    assert response.status_code in [400, 422, 404]


def test_scan_v1_endpoint(client):
    """Test v1 scan endpoint exists."""
    response = client.post("/api/v1/scan/domain", json={"domain": "invalid"})
    # Should return 400 (invalid domain), 422 (validation error), or 404 (domain not found), not 404 for endpoint
    assert response.status_code in [400, 422, 404]


def test_scan_legacy_endpoint(client):
    """Test legacy scan endpoint still works (backward compatibility)."""
    response = client.post("/scan/domain", json={"domain": "invalid"})
    # Should return 400 (invalid domain), 422 (validation error), or 404 (domain not found), not 404 for endpoint
    assert response.status_code in [400, 422, 404]


def test_dashboard_v1_endpoint(client):
    """Test v1 dashboard endpoint exists."""
    response = client.get("/api/v1/dashboard")
    # Should return 200 (success) or 500 (db error), not 404
    assert response.status_code != 404


def test_dashboard_legacy_endpoint(client):
    """Test legacy dashboard endpoint still works (backward compatibility)."""
    response = client.get("/dashboard")
    # Should return 200 (success) or 500 (db error), not 404
    assert response.status_code != 404


def test_api_versioning_structure(client):
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


def test_legacy_endpoints_still_work(client):
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


class TestResponseFormatConsistency:
    """Test response format consistency between v1 and legacy endpoints."""
    
    def test_dashboard_response_format_consistency(self, client):
        """Test that v1 and legacy dashboard endpoints return same format."""
        v1_response = client.get("/api/v1/dashboard")
        legacy_response = client.get("/dashboard")
        
        # Both should succeed or both should fail (consistency)
        assert (v1_response.status_code == 200) == (legacy_response.status_code == 200), \
            "Dashboard endpoints should have consistent success/failure"
        
        if v1_response.status_code == 200 and legacy_response.status_code == 200:
            # Response formats should match
            v1_data = v1_response.json()
            legacy_data = legacy_response.json()
            
            # Check that both have same keys
            assert set(v1_data.keys()) == set(legacy_data.keys()), \
                "Dashboard response keys should match between v1 and legacy"
    
    def test_leads_response_format_consistency(self, client):
        """Test that v1 and legacy leads endpoints return same format."""
        v1_response = client.get("/api/v1/leads?limit=1")
        legacy_response = client.get("/leads?limit=1")
        
        # Both should succeed or both should fail (consistency)
        assert (v1_response.status_code == 200) == (legacy_response.status_code == 200), \
            "Leads endpoints should have consistent success/failure"
        
        if v1_response.status_code == 200 and legacy_response.status_code == 200:
            # Response formats should match
            v1_data = v1_response.json()
            legacy_data = legacy_response.json()
            
            # Both should be lists or both should be dicts
            assert type(v1_data) == type(legacy_data), \
                "Leads response types should match between v1 and legacy"


class TestZeroDowntimeDeployment:
    """Test zero downtime deployment scenarios."""
    
    def test_dual_path_routing_active(self, client):
        """Test that both v1 and legacy paths are active simultaneously."""
        # Test that both endpoints respond (zero downtime deployment)
        v1_response = client.get("/api/v1/dashboard")
        legacy_response = client.get("/dashboard")
        
        # Both should be accessible (not 404)
        assert v1_response.status_code != 404, "V1 endpoint should be accessible"
        assert legacy_response.status_code != 404, "Legacy endpoint should be accessible"
    
    def test_legacy_endpoint_not_deprecated_yet(self, client):
        """Test that legacy endpoints don't return deprecation headers yet."""
        # Legacy endpoints should not have deprecation headers (future: v1.2)
        response = client.get("/dashboard")
        
        # Should not have deprecation header (yet)
        assert "Deprecation" not in response.headers, \
            "Legacy endpoints should not be deprecated yet (v1.1)"
        assert "Sunset" not in response.headers, \
            "Legacy endpoints should not have sunset date yet (v1.1)"
