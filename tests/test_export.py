"""Tests for export endpoints."""

import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.models import Base, Company, DomainSignal, LeadScore
from datetime import datetime

# Test database URL
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
)


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    from sqlalchemy.exc import OperationalError

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


@pytest.fixture
def sample_leads(db_session):
    """Create sample leads for testing."""
    # Clean up any existing test data first
    db_session.query(LeadScore).filter(
        LeadScore.domain.in_(["example.com", "test.com"])
    ).delete(synchronize_session=False)
    db_session.query(DomainSignal).filter(
        DomainSignal.domain.in_(["example.com", "test.com"])
    ).delete(synchronize_session=False)
    db_session.query(Company).filter(
        Company.domain.in_(["example.com", "test.com"])
    ).delete(synchronize_session=False)
    db_session.commit()

    # Create companies
    company1 = Company(
        domain="example.com", canonical_name="Example Inc", provider="M365"
    )
    company2 = Company(domain="test.com", canonical_name="Test Corp", provider="Google")
    db_session.add(company1)
    db_session.add(company2)
    db_session.commit()

    # Create domain signals
    signal1 = DomainSignal(
        domain="example.com",
        spf=True,
        dkim=True,
        dmarc_policy="reject",
        mx_root="outlook.com",
        scan_status="success",
        scanned_at=datetime.now(),
    )
    signal2 = DomainSignal(
        domain="test.com",
        spf=True,
        dkim=False,
        dmarc_policy="none",
        mx_root="aspmx.l.google.com",
        scan_status="success",
        scanned_at=datetime.now(),
    )
    db_session.add(signal1)
    db_session.add(signal2)
    db_session.commit()

    # Create lead scores
    score1 = LeadScore(
        domain="example.com",
        readiness_score=85,
        segment="Migration",
        reason="High readiness score with M365 provider",
    )
    score2 = LeadScore(
        domain="test.com",
        readiness_score=60,
        segment="Existing",
        reason="Google provider with medium score",
    )
    db_session.add(score1)
    db_session.add(score2)
    db_session.commit()

    yield

    # Cleanup (transaction rollback will handle this, but explicit cleanup for safety)
    try:
        db_session.query(LeadScore).filter(
            LeadScore.domain.in_(["example.com", "test.com"])
        ).delete(synchronize_session=False)
        db_session.query(DomainSignal).filter(
            DomainSignal.domain.in_(["example.com", "test.com"])
        ).delete(synchronize_session=False)
        db_session.query(Company).filter(
            Company.domain.in_(["example.com", "test.com"])
        ).delete(synchronize_session=False)
        db_session.commit()
    except Exception:
        db_session.rollback()


def test_export_leads_csv(client, db_session, sample_leads):
    """Test CSV export with no filters."""
    response = client.get("/leads/export?format=csv")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in response.headers["content-disposition"]
    assert "leads_" in response.headers["content-disposition"]
    assert ".csv" in response.headers["content-disposition"]

    # Check CSV content
    content = response.text
    assert "domain" in content
    assert "example.com" in content
    assert "test.com" in content
    assert "Migration" in content
    assert "Existing" in content


def test_export_leads_csv_with_filters(client, db_session, sample_leads):
    """Test CSV export with segment filter."""
    response = client.get("/leads/export?format=csv&segment=Migration")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

    # Check CSV content
    content = response.text
    assert "example.com" in content
    assert "test.com" not in content  # Should be filtered out
    assert "Migration" in content


def test_export_leads_csv_with_min_score(client, db_session, sample_leads):
    """Test CSV export with min_score filter."""
    response = client.get("/leads/export?format=csv&min_score=70")

    assert response.status_code == 200

    # Check CSV content
    content = response.text
    assert "example.com" in content  # Score 85
    assert "test.com" not in content  # Score 60, filtered out


def test_export_leads_csv_with_provider(client, db_session, sample_leads):
    """Test CSV export with provider filter."""
    response = client.get("/leads/export?format=csv&provider=M365")

    assert response.status_code == 200

    # Check CSV content
    content = response.text
    assert "example.com" in content
    assert "test.com" not in content  # Google provider, filtered out


def test_export_leads_csv_empty_result(client, db_session):
    """Test CSV export with no leads."""
    response = client.get("/leads/export?format=csv")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

    # Check CSV content (should have headers only)
    content = response.text
    assert "domain" in content


def test_export_leads_xlsx(client, db_session, sample_leads):
    """Test Excel export."""
    response = client.get("/leads/export?format=xlsx")

    assert response.status_code == 200
    assert (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        in response.headers["content-type"]
    )
    assert "attachment" in response.headers["content-disposition"]
    assert "leads_" in response.headers["content-disposition"]
    assert ".xlsx" in response.headers["content-disposition"]

    # Check that it's a valid Excel file (starts with PK header for ZIP format)
    assert response.content[:2] == b"PK"


def test_export_leads_invalid_format(client, db_session):
    """Test export with invalid format."""
    response = client.get("/leads/export?format=json")

    assert response.status_code == 422  # Validation error


def test_export_leads_invalid_min_score(client, db_session):
    """Test export with invalid min_score."""
    response = client.get("/leads/export?format=csv&min_score=150")

    assert response.status_code == 422  # Validation error (ge=0, le=100)
