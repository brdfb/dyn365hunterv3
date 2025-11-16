"""Integration tests for G19 features: UI upgrade e2e."""

import pytest
import os
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

# Test Redis URL
TEST_REDIS_URL = os.getenv(
    "TEST_REDIS_URL",
    os.getenv(
        "HUNTER_REDIS_URL",
        os.getenv("REDIS_URL", "redis://localhost:6379/1"),
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
                    ADD COLUMN IF NOT EXISTS linkedin_pattern VARCHAR(255)
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
def test_leads(db_session):
    """Create test leads for integration tests."""
    test_domains = [
        ("test1.com", "Test 1 Inc", "M365", "Migration", 85),
        ("test2.com", "Test 2 Corp", "Google", "Existing", 60),
        ("test3.com", "Test 3 Ltd", "M365", "Migration", 75),
    ]

    companies = []
    for domain, name, provider, segment, score in test_domains:
        company = Company(domain=domain, canonical_name=name, provider=provider)
        db_session.add(company)
        companies.append(company)

    db_session.commit()

    # Create domain signals
    for domain, _, _, segment, score in test_domains:
        signal = DomainSignal(
            domain=domain,
            scan_status="completed",
            spf=True,
            dkim=True,
            dmarc_policy="reject",
        )
        db_session.add(signal)
    
    db_session.commit()
    
    # Create lead scores
    for domain, _, _, segment, score in test_domains:
        lead_score = LeadScore(
            domain=domain,
            readiness_score=score,
            segment=segment,
            reason=f"Test score for {domain}",
        )
        db_session.add(lead_score)

    db_session.commit()
    return test_domains


class TestUIUpgradeEndToEnd:
    """Test UI upgrade features end-to-end."""

    def test_leads_endpoint_with_all_params(self, client, test_leads):
        """Test /leads endpoint with all UI upgrade parameters."""
        response = client.get(
            "/leads?search=test&sort_by=readiness_score&sort_order=desc&page=1&page_size=2"
        )
        assert response.status_code == 200
        data = response.json()
        assert "leads" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert len(data["leads"]) <= 2

    def test_dashboard_kpis_endpoint(self, client, test_leads):
        """Test /dashboard/kpis endpoint."""
        response = client.get("/dashboard/kpis")
        assert response.status_code == 200
        data = response.json()
        assert "total_leads" in data
        assert "migration_leads" in data
        assert "high_priority" in data
        assert isinstance(data["total_leads"], int)
        assert isinstance(data["migration_leads"], int)
        assert isinstance(data["high_priority"], int)

    def test_score_breakdown_endpoint(self, client, test_leads):
        """Test /leads/{domain}/score-breakdown endpoint."""
        domain = "test1.com"
        response = client.get(f"/leads/{domain}/score-breakdown")
        assert response.status_code == 200
        data = response.json()
        assert "base_score" in data
        assert "provider" in data
        assert "signal_points" in data
        assert "risk_points" in data
        assert "total_score" in data

    def test_score_breakdown_not_found(self, client):
        """Test score breakdown for non-existent domain."""
        response = client.get("/leads/nonexistent.com/score-breakdown")
        assert response.status_code == 404



