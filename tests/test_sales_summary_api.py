"""Tests for Sales Summary API endpoint (Phase 2)."""

import pytest
import os
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from app.db.models import Base, Company, DomainSignal, LeadScore
from app.main import app
from app.db.session import get_db

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
    engine = create_engine(TEST_DATABASE_URL)

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
    except OperationalError as e:
        pytest.skip(f"Test database not available: {TEST_DATABASE_URL} - {e}")

    Base.metadata.create_all(bind=engine)
    
    # Run G16 migration for contact_quality_score and linkedin_pattern columns
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='companies' AND column_name='contact_quality_score'
            """))
            if result.fetchone() is None:
                conn.execute(text("""
                    ALTER TABLE companies 
                    ADD COLUMN IF NOT EXISTS contact_emails JSONB,
                    ADD COLUMN IF NOT EXISTS contact_quality_score INTEGER,
                    ADD COLUMN IF NOT EXISTS linkedin_pattern VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS tenant_size VARCHAR(50)
                """))
                conn.commit()
    except Exception:
        pass
    
    # Run G20 migration for local_provider and dmarc_coverage
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='domain_signals' AND column_name='local_provider'
            """))
            if result.fetchone() is None:
                conn.execute(text("""
                    ALTER TABLE domain_signals 
                    ADD COLUMN IF NOT EXISTS local_provider VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS dmarc_coverage INTEGER
                """))
                conn.commit()
    except Exception:
        pass
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        transaction.rollback()
        session.close()
        connection.close()
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_lead_migration(db_session):
    """Create a test lead with Migration segment."""
    domain = "migration-test.com"
    
    # Create company
    company = Company(
        domain=domain,
        canonical_name="Migration Test Inc",
        provider="Local",
        tenant_size="large",
        contact_quality_score=80,
    )
    db_session.add(company)
    db_session.commit()
    
    # Create domain signal
    signal = DomainSignal(
        domain=domain,
        scan_status="completed",
        spf=False,
        dkim=False,
        dmarc_policy="none",
        dmarc_coverage=None,
        local_provider="TürkHost",
        expires_at=date.today() + timedelta(days=45),
    )
    db_session.add(signal)
    db_session.commit()
    
    # Create lead score
    lead_score = LeadScore(
        domain=domain,
        readiness_score=85,
        segment="Migration",
        reason="High readiness for migration",
    )
    db_session.add(lead_score)
    db_session.commit()
    
    return domain


@pytest.fixture(scope="function")
def test_lead_existing(db_session):
    """Create a test lead with Existing segment."""
    domain = "existing-test.com"
    
    # Create company
    company = Company(
        domain=domain,
        canonical_name="Existing Test Corp",
        provider="M365",
        tenant_size="medium",
        contact_quality_score=70,
    )
    db_session.add(company)
    db_session.commit()
    
    # Create domain signal
    signal = DomainSignal(
        domain=domain,
        scan_status="completed",
        spf=True,
        dkim=True,
        dmarc_policy="quarantine",
        dmarc_coverage=75,
        local_provider=None,
        expires_at=date.today() + timedelta(days=200),
    )
    db_session.add(signal)
    db_session.commit()
    
    # Create lead score
    lead_score = LeadScore(
        domain=domain,
        readiness_score=75,
        segment="Existing",
        reason="Existing M365 customer",
    )
    db_session.add(lead_score)
    db_session.commit()
    
    return domain


@pytest.fixture(scope="function")
def test_lead_cold(db_session):
    """Create a test lead with Cold segment."""
    domain = "cold-test.com"
    
    # Create company
    company = Company(
        domain=domain,
        canonical_name="Cold Test Ltd",
        provider="Google",
        tenant_size="small",
        contact_quality_score=50,
    )
    db_session.add(company)
    db_session.commit()
    
    # Create domain signal
    signal = DomainSignal(
        domain=domain,
        scan_status="completed",
        spf=True,
        dkim=False,
        dmarc_policy="none",
        dmarc_coverage=None,
        local_provider=None,
        expires_at=date.today() + timedelta(days=300),
    )
    db_session.add(signal)
    db_session.commit()
    
    # Create lead score
    lead_score = LeadScore(
        domain=domain,
        readiness_score=40,
        segment="Cold",
        reason="Cold lead",
    )
    db_session.add(lead_score)
    db_session.commit()
    
    return domain


class TestSalesSummaryAPI:
    """Tests for Sales Summary API endpoint."""

    def test_sales_summary_migration_lead(self, client, test_lead_migration):
        """Test sales summary for migration lead."""
        domain = test_lead_migration
        response = client.get(f"/api/v1/leads/{domain}/sales-summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert data["domain"] == domain
        assert "one_liner" in data
        assert isinstance(data["call_script"], list)
        assert len(data["call_script"]) > 0
        assert isinstance(data["discovery_questions"], list)
        assert len(data["discovery_questions"]) > 0
        assert isinstance(data["offer_tier"], dict)
        assert "tier" in data["offer_tier"]
        assert isinstance(data["opportunity_potential"], int)
        assert 0 <= data["opportunity_potential"] <= 100
        assert data["urgency"] in ["low", "medium", "high"]
        assert "metadata" in data
        
        # Check metadata
        assert data["metadata"]["domain"] == domain
        assert data["metadata"]["segment"] == "Migration"
        assert data["metadata"]["provider"] == "Local"
        assert data["metadata"]["tenant_size"] == "large"
        assert data["metadata"]["local_provider"] == "TürkHost"
        
        # Check offer tier for large tenant
        assert data["offer_tier"]["tier"] == "Enterprise"
        assert data["offer_tier"]["price_per_user_per_month"] == 20
        
        # Check urgency (should be high for migration with high score)
        assert data["urgency"] == "high"
        
        # Check opportunity potential (should be high)
        assert data["opportunity_potential"] >= 70

    def test_sales_summary_existing_lead(self, client, test_lead_existing):
        """Test sales summary for existing lead."""
        domain = test_lead_existing
        response = client.get(f"/api/v1/leads/{domain}/sales-summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert data["domain"] == domain
        assert "one_liner" in data
        assert isinstance(data["call_script"], list)
        assert isinstance(data["discovery_questions"], list)
        assert isinstance(data["offer_tier"], dict)
        assert isinstance(data["opportunity_potential"], int)
        assert data["urgency"] in ["low", "medium", "high"]
        
        # Check metadata
        assert data["metadata"]["segment"] == "Existing"
        assert data["metadata"]["provider"] == "M365"
        assert data["metadata"]["tenant_size"] == "medium"
        
        # Check offer tier for medium tenant
        assert data["offer_tier"]["tier"] == "Business Standard"
        assert data["offer_tier"]["price_per_user_per_month"] == 10

    def test_sales_summary_cold_lead(self, client, test_lead_cold):
        """Test sales summary for cold lead."""
        domain = test_lead_cold
        response = client.get(f"/api/v1/leads/{domain}/sales-summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert data["domain"] == domain
        assert "one_liner" in data
        assert isinstance(data["call_script"], list)
        assert isinstance(data["discovery_questions"], list)
        assert isinstance(data["offer_tier"], dict)
        assert isinstance(data["opportunity_potential"], int)
        assert data["urgency"] in ["low", "medium", "high"]
        
        # Check metadata
        assert data["metadata"]["segment"] == "Cold"
        assert data["metadata"]["provider"] == "Google"
        
        # Check urgency (should be low for cold lead)
        assert data["urgency"] == "low"
        
        # Check opportunity potential (should be lower)
        assert data["opportunity_potential"] <= 60

    def test_sales_summary_not_found(self, client):
        """Test sales summary for non-existent domain."""
        response = client.get("/api/v1/leads/nonexistent-domain-xyz-12345.com/sales-summary")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_sales_summary_legacy_endpoint(self, client, test_lead_migration):
        """Test legacy endpoint still works."""
        domain = test_lead_migration
        response = client.get(f"/leads/{domain}/sales-summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == domain
        assert "one_liner" in data

    def test_sales_summary_response_shape_stable(self, client, test_lead_migration):
        """Test that response shape is stable and consistent."""
        domain = test_lead_migration
        
        # Call multiple times
        response1 = client.get(f"/api/v1/leads/{domain}/sales-summary")
        response2 = client.get(f"/api/v1/leads/{domain}/sales-summary")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Check that structure is consistent
        assert set(data1.keys()) == set(data2.keys())
        assert data1["domain"] == data2["domain"]
        assert data1["metadata"]["segment"] == data2["metadata"]["segment"]
        assert data1["offer_tier"]["tier"] == data2["offer_tier"]["tier"]
        assert data1["urgency"] == data2["urgency"]
        
        # One-liner, segment explanation, provider reasoning, call script, and questions may vary slightly, but structure should be same
        assert isinstance(data1["one_liner"], str)
        assert isinstance(data2["one_liner"], str)
        assert isinstance(data1["segment_explanation"], str)
        assert isinstance(data2["segment_explanation"], str)
        assert len(data1["segment_explanation"]) > 0
        assert isinstance(data1["provider_reasoning"], str)
        assert isinstance(data2["provider_reasoning"], str)
        assert len(data1["provider_reasoning"]) > 0
        # security_reasoning can be None or dict
        if data1["security_reasoning"] is not None:
            assert isinstance(data1["security_reasoning"], dict)
            assert "risk_level" in data1["security_reasoning"]
        # opportunity_rationale should be present
        assert "opportunity_rationale" in data1
        assert isinstance(data1["opportunity_rationale"], dict)
        assert "total" in data1["opportunity_rationale"]
        assert "factors" in data1["opportunity_rationale"]
        # Verify opportunity_rationale["total"] matches opportunity_potential
        assert data1["opportunity_rationale"]["total"] == data1["opportunity_potential"]
        # Verify next_step is present
        assert "next_step" in data1
        assert isinstance(data1["next_step"], dict)
        assert "action" in data1["next_step"]
        assert "timeline" in data1["next_step"]
        assert "priority" in data1["next_step"]
        assert "message" in data1["next_step"]
        assert "internal_note" in data1["next_step"]
        assert isinstance(data1["call_script"], list)
        assert isinstance(data2["call_script"], list)
        assert isinstance(data1["discovery_questions"], list)
        assert isinstance(data2["discovery_questions"], list)

    def test_sales_summary_with_minimal_data(self, client, db_session):
        """Test sales summary with minimal lead data."""
        domain = "minimal-test.com"
        
        # Create minimal company
        company = Company(
            domain=domain,
            canonical_name="Minimal Test",
            provider=None,
        )
        db_session.add(company)
        db_session.commit()
        
        # Create minimal domain signal
        signal = DomainSignal(
            domain=domain,
            scan_status="completed",
        )
        db_session.add(signal)
        db_session.commit()
        
        # No lead score - should still work
        response = client.get(f"/api/v1/leads/{domain}/sales-summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == domain
        assert "one_liner" in data
        assert isinstance(data["call_script"], list)
        assert isinstance(data["discovery_questions"], list)
        assert isinstance(data["offer_tier"], dict)
        assert isinstance(data["opportunity_potential"], int)
        assert data["urgency"] in ["low", "medium", "high"]

