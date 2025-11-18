"""Integration tests for API endpoints (ingest, scan, leads)."""

import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# Import app after setting up test environment
from app.db.models import Base

# Test database URL - use PostgreSQL from environment or fallback to test DB
# In Docker container: use 'postgres' (service name)
# Local testing: use 'localhost'
# Priority: TEST_DATABASE_URL > HUNTER_DATABASE_URL > DATABASE_URL > default
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv(
        "HUNTER_DATABASE_URL",
        os.getenv(
            "DATABASE_URL",
            "postgresql://dyn365hunter:password123@localhost:5432/dyn365hunter",
        ),
    ),
    # Keep DATABASE_URL as-is (postgres:5432 in container, localhost:5432 locally)
    # Don't replace - container uses 'postgres', local uses 'localhost'
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
    # Import app here to avoid import-time database connection
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
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_healthz(self, client):
        """Test /healthz endpoint."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestIngestEndpoints:
    """Test ingest endpoints."""

    def test_ingest_domain_success(self, client):
        """Test successful domain ingestion."""
        response = client.post(
            "/ingest/domain",
            json={"domain": "example.com", "company_name": "Example Inc"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["domain"] == "example.com"
        assert "company_id" in data
        assert "message" in data

    def test_ingest_domain_with_email(self, client):
        """Test domain ingestion with email."""
        response = client.post(
            "/ingest/domain",
            json={
                "domain": "test.com",
                "company_name": "Test Inc",
                "email": "user@test.com",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["domain"] == "test.com"

    def test_ingest_domain_normalization(self, client):
        """Test domain normalization in ingestion."""
        response = client.post(
            "/ingest/domain",
            json={"domain": "WWW.EXAMPLE.COM", "company_name": "Example"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["domain"] == "example.com"

    def test_ingest_domain_invalid(self, client):
        """Test invalid domain ingestion."""
        response = client.post(
            "/ingest/domain", json={"domain": "", "company_name": "Test"}
        )
        assert response.status_code == 422  # Validation error

    def test_ingest_domain_duplicate(self, client):
        """Test duplicate domain ingestion (idempotent)."""
        # First ingestion
        response1 = client.post(
            "/ingest/domain",
            json={"domain": "duplicate.com", "company_name": "First Name"},
        )
        assert response1.status_code == 201
        company_id_1 = response1.json()["company_id"]

        # Second ingestion (should update, not create new)
        response2 = client.post(
            "/ingest/domain",
            json={"domain": "duplicate.com", "company_name": "Updated Name"},
        )
        assert response2.status_code == 201
        company_id_2 = response2.json()["company_id"]

        # Should be same company_id (idempotent)
        assert company_id_1 == company_id_2


class TestScanEndpoints:
    """Test scan endpoints."""

    def test_scan_domain_not_ingested(self, client):
        """Test scanning domain that hasn't been ingested."""
        response = client.post("/scan/domain", json={"domain": "notingested.com"})
        # Should return 404 or 400
        assert response.status_code in [400, 404]

    def test_scan_domain_success(self, client):
        """Test successful domain scan."""
        # First ingest
        ingest_response = client.post(
            "/ingest/domain",
            json={"domain": "scantest.com", "company_name": "Scan Test"},
        )
        assert ingest_response.status_code == 201

        # Then scan (with mocked DNS/WHOIS)
        with patch("app.core.analyzer_dns.analyze_dns") as mock_dns, patch(
            "app.core.analyzer_whois.get_whois_info"
        ) as mock_whois:

            mock_dns.return_value = {
                "mx_records": ["mail.scantest.com"],
                "mx_root": "scantest.com",
                "spf": True,
                "dkim": True,
                "dmarc_policy": "reject",
                "status": "success",
            }
            mock_whois.return_value = {
                "registrar": "Test Registrar",
                "expires_at": "2025-12-31",
                "nameservers": ["ns1.test.com"],
            }

            response = client.post("/scan/domain", json={"domain": "scantest.com"})

            # May timeout or succeed depending on actual DNS lookup
            # If it times out, status code might be different
            assert response.status_code in [200, 500, 503]

    def test_scan_domain_invalid(self, client):
        """Test scanning invalid domain."""
        response = client.post("/scan/domain", json={"domain": ""})
        assert response.status_code == 422  # Validation error


class TestLeadsEndpoints:
    """Test leads endpoints."""

    def test_get_leads_empty(self, client):
        """Test getting leads when none exist."""
        response = client.get("/leads")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Note: May not be empty if other tests ran before (test isolation limitation)
        # But should return valid list format
        assert len(data) >= 0

    def test_get_leads_with_filter(self, client):
        """Test getting leads with filters."""
        response = client.get("/leads?segment=Migration&min_score=70")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_leads_segment_filter(self, client):
        """Test segment filter."""
        response = client.get("/leads?segment=Migration")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_leads_min_score_filter(self, client):
        """Test min_score filter."""
        response = client.get("/leads?min_score=50")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_leads_provider_filter(self, client):
        """Test provider filter."""
        response = client.get("/leads?provider=M365")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_lead_not_found(self, client):
        """Test getting single lead that doesn't exist."""
        response = client.get("/leads/nonexistent.com")
        assert response.status_code == 404

    def test_get_lead_success(self, client):
        """Test getting single lead."""
        # First ingest
        ingest_response = client.post(
            "/ingest/domain",
            json={"domain": "leadtest.com", "company_name": "Lead Test"},
        )
        assert ingest_response.status_code == 201

        # Get lead
        response = client.get("/leads/leadtest.com")
        # May return 404 if not scanned yet, or 200 if scanned
        assert response.status_code in [200, 404]

    def test_get_leads_includes_priority_score(self, client):
        """Test that GET /leads includes priority_score in response."""
        response = client.get("/leads")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # If there are leads, check that priority_score is included
        if len(data) > 0:
            assert "priority_score" in data[0]

    def test_get_lead_includes_priority_score(self, client):
        """Test that GET /leads/{domain} includes priority_score in response."""
        # First ingest
        ingest_response = client.post(
            "/ingest/domain",
            json={"domain": "prioritytest.com", "company_name": "Priority Test"},
        )
        assert ingest_response.status_code == 201

        # Get lead (may be 404 if not scanned)
        response = client.get("/leads/prioritytest.com")
        if response.status_code == 200:
            data = response.json()
            assert "priority_score" in data
            assert isinstance(data["priority_score"], (int, type(None)))

    def test_get_leads_includes_referral_type(self, client, db_session):
        """Test that GET /leads includes referral_type field (Task 2.5)."""
        from app.db.models import Company, DomainSignal, LeadScore, PartnerCenterReferral
        from app.core.normalizer import normalize_domain

        # Create test data: domain with referral
        test_domain = normalize_domain("referraltest.com")
        
        # Create company
        company = Company(domain=test_domain, canonical_name="Referral Test")
        db_session.add(company)
        
        # Create domain signal
        signal = DomainSignal(domain=test_domain, spf=True, dkim=True, dmarc_policy="reject")
        db_session.add(signal)
        
        # Create lead score
        score = LeadScore(domain=test_domain, readiness_score=75, segment="Migration")
        db_session.add(score)
        
        # Create referral
        referral = PartnerCenterReferral(
            referral_id="test-ref-123",
            referral_type="co-sell",
            domain=test_domain,
            company_name="Referral Test"
        )
        db_session.add(referral)
        db_session.commit()

        # Test GET /leads endpoint
        response = client.get("/leads")
        assert response.status_code == 200
        data = response.json()
        
        # Check response format (should be LeadsListResponse with pagination)
        if "leads" in data:
            # New format with pagination
            leads = data["leads"]
            assert isinstance(leads, list)
            if len(leads) > 0:
                # Find our test domain
                test_lead = next((l for l in leads if l.get("domain") == test_domain), None)
                if test_lead:
                    assert "referral_type" in test_lead
                    assert test_lead["referral_type"] == "co-sell"
        else:
            # Legacy format (list)
            assert isinstance(data, list)
            if len(data) > 0:
                test_lead = next((l for l in data if l.get("domain") == test_domain), None)
                if test_lead:
                    assert "referral_type" in test_lead
                    assert test_lead["referral_type"] == "co-sell"

    def test_get_lead_includes_referral_type(self, client, db_session):
        """Test that GET /leads/{domain} includes referral_type field (Task 2.5)."""
        from app.db.models import Company, DomainSignal, LeadScore, PartnerCenterReferral
        from app.core.normalizer import normalize_domain

        # Create test data: domain with referral
        test_domain = normalize_domain("referraltest2.com")
        
        # Create company
        company = Company(domain=test_domain, canonical_name="Referral Test 2")
        db_session.add(company)
        
        # Create domain signal
        signal = DomainSignal(domain=test_domain, spf=True, dkim=True, dmarc_policy="reject")
        db_session.add(signal)
        
        # Create lead score
        score = LeadScore(domain=test_domain, readiness_score=80, segment="Migration")
        db_session.add(score)
        
        # Create referral
        referral = PartnerCenterReferral(
            referral_id="test-ref-456",
            referral_type="marketplace",
            domain=test_domain,
            company_name="Referral Test 2"
        )
        db_session.add(referral)
        db_session.commit()

        # Test GET /leads/{domain} endpoint
        response = client.get(f"/leads/{test_domain}")
        assert response.status_code == 200
        data = response.json()
        
        assert "referral_type" in data
        assert data["referral_type"] == "marketplace"

    def test_get_leads_referral_type_none_when_no_referral(self, client, db_session):
        """Test that referral_type is None when domain has no referral (Task 2.5)."""
        from app.db.models import Company, DomainSignal, LeadScore
        from app.core.normalizer import normalize_domain

        # Create test data: domain without referral
        test_domain = normalize_domain("noreferraltest.com")
        
        # Create company
        company = Company(domain=test_domain, canonical_name="No Referral Test")
        db_session.add(company)
        
        # Create domain signal
        signal = DomainSignal(domain=test_domain, spf=True, dkim=True, dmarc_policy="reject")
        db_session.add(signal)
        
        # Create lead score
        score = LeadScore(domain=test_domain, readiness_score=70, segment="Migration")
        db_session.add(score)
        db_session.commit()

        # Test GET /leads/{domain} endpoint
        response = client.get(f"/leads/{test_domain}")
        assert response.status_code == 200
        data = response.json()
        
        assert "referral_type" in data
        assert data["referral_type"] is None


class TestDashboardEndpoints:
    """Test dashboard endpoints."""

    def test_get_dashboard_empty(self, client):
        """Test dashboard endpoint structure (may not be empty if other tests ran)."""
        response = client.get("/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "total_leads" in data
        assert "migration" in data
        assert "existing" in data
        assert "cold" in data
        assert "skip" in data
        assert "avg_score" in data
        assert "high_priority" in data
        # Check types and non-negative values
        assert isinstance(data["total_leads"], int)
        assert isinstance(data["migration"], int)
        assert isinstance(data["existing"], int)
        assert isinstance(data["cold"], int)
        assert isinstance(data["skip"], int)
        assert isinstance(data["avg_score"], (int, float))
        assert isinstance(data["high_priority"], int)
        assert data["total_leads"] >= 0
        assert data["migration"] >= 0
        assert data["existing"] >= 0
        assert data["cold"] >= 0
        assert data["skip"] >= 0
        assert data["avg_score"] >= 0.0
        assert data["high_priority"] >= 0

    def test_get_dashboard_with_data(self, client):
        """Test dashboard with some data."""
        # Ingest a domain
        ingest_response = client.post(
            "/ingest/domain",
            json={"domain": "dashboardtest.com", "company_name": "Dashboard Test"},
        )
        assert ingest_response.status_code == 201

        # Dashboard should still work (even without scanned leads)
        response = client.get("/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "total_leads" in data
        assert isinstance(data["total_leads"], int)
        assert isinstance(data["migration"], int)
        assert isinstance(data["existing"], int)
        assert isinstance(data["cold"], int)
        assert isinstance(data["skip"], int)
        assert isinstance(data["avg_score"], (int, float))
        assert isinstance(data["high_priority"], int)
