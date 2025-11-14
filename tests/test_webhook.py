"""Tests for webhook endpoint and API key authentication."""

import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from app.db.models import Base, ApiKey, Company, RawLead
from app.core.api_key_auth import hash_api_key, generate_api_key
from app.main import app

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
    engine = create_engine(TEST_DATABASE_URL)

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
    except OperationalError as e:
        pytest.skip(f"Test database not available: {TEST_DATABASE_URL} - {e}")

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
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


@pytest.fixture(scope="function")
def api_key(db_session):
    """Create a test API key."""
    api_key_value = generate_api_key()
    key_hash = hash_api_key(api_key_value)

    api_key_record = ApiKey(
        key_hash=key_hash, name="test-api-key", rate_limit_per_minute=60, is_active=True
    )
    db_session.add(api_key_record)
    db_session.commit()
    db_session.refresh(api_key_record)

    return api_key_value, api_key_record


def test_webhook_requires_api_key(client):
    """Test that webhook endpoint requires API key."""
    response = client.post(
        "/ingest/webhook", json={"domain": "example.com", "company_name": "Example Inc"}
    )
    assert response.status_code == 401
    assert "API key required" in response.json()["detail"]


def test_webhook_invalid_api_key(client):
    """Test that invalid API key is rejected."""
    response = client.post(
        "/ingest/webhook",
        json={"domain": "example.com", "company_name": "Example Inc"},
        headers={"X-API-Key": "invalid-key"},
    )
    assert response.status_code == 401
    assert "Invalid or inactive API key" in response.json()["detail"]


def test_webhook_success(client, api_key):
    """Test successful webhook ingestion."""
    api_key_value, api_key_record = api_key

    response = client.post(
        "/ingest/webhook",
        json={
            "domain": "example.com",
            "company_name": "Example Inc",
            "contact_emails": ["john@example.com", "jane@example.com"],
        },
        headers={"X-API-Key": api_key_value},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["domain"] == "example.com"
    assert data["ingested"] is True
    assert data["enriched"] is True


def test_webhook_without_contact_emails(client, api_key):
    """Test webhook ingestion without contact emails."""
    api_key_value, api_key_record = api_key

    response = client.post(
        "/ingest/webhook",
        json={"domain": "test.com", "company_name": "Test Inc"},
        headers={"X-API-Key": api_key_value},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["ingested"] is True
    assert data["enriched"] is False


def test_webhook_invalid_domain(client, api_key):
    """Test webhook with invalid domain."""
    api_key_value, api_key_record = api_key

    response = client.post(
        "/ingest/webhook",
        json={"domain": "invalid..domain", "company_name": "Test Inc"},
        headers={"X-API-Key": api_key_value},
    )

    assert response.status_code == 400
    assert "Invalid domain format" in response.json()["detail"]


def test_webhook_creates_company(client, api_key, db_session):
    """Test that webhook creates company record."""
    api_key_value, api_key_record = api_key

    response = client.post(
        "/ingest/webhook",
        json={"domain": "newcompany.com", "company_name": "New Company"},
        headers={"X-API-Key": api_key_value},
    )

    assert response.status_code == 201

    # Check company was created
    company = (
        db_session.query(Company).filter(Company.domain == "newcompany.com").first()
    )
    assert company is not None
    assert company.canonical_name == "New Company"


def test_webhook_creates_raw_lead(client, api_key, db_session):
    """Test that webhook creates raw_lead record."""
    api_key_value, api_key_record = api_key

    response = client.post(
        "/ingest/webhook",
        json={"domain": "testlead.com", "company_name": "Test Lead"},
        headers={"X-API-Key": api_key_value},
    )

    assert response.status_code == 201

    # Check raw_lead was created
    raw_lead = (
        db_session.query(RawLead).filter(RawLead.domain == "testlead.com").first()
    )
    assert raw_lead is not None
    assert raw_lead.source == "webhook"
    assert raw_lead.company_name == "Test Lead"


def test_webhook_enrichment(client, api_key, db_session):
    """Test that webhook enriches company data."""
    api_key_value, api_key_record = api_key

    response = client.post(
        "/ingest/webhook",
        json={
            "domain": "enriched.com",
            "company_name": "Enriched Company",
            "contact_emails": [
                "john.doe@enriched.com",
                "jane.smith@enriched.com",
                "bob@enriched.com",
            ],
        },
        headers={"X-API-Key": api_key_value},
    )

    assert response.status_code == 201

    # Check enrichment data
    company = db_session.query(Company).filter(Company.domain == "enriched.com").first()
    assert company is not None
    assert company.contact_emails is not None
    assert len(company.contact_emails) == 3
    assert company.contact_quality_score is not None
    assert company.contact_quality_score > 0
    assert company.linkedin_pattern is not None


def test_webhook_inactive_api_key(client, db_session):
    """Test that inactive API key is rejected."""
    api_key_value = generate_api_key()
    key_hash = hash_api_key(api_key_value)

    api_key_record = ApiKey(
        key_hash=key_hash,
        name="inactive-key",
        rate_limit_per_minute=60,
        is_active=False,
    )
    db_session.add(api_key_record)
    db_session.commit()

    response = client.post(
        "/ingest/webhook",
        json={"domain": "example.com", "company_name": "Example Inc"},
        headers={"X-API-Key": api_key_value},
    )

    assert response.status_code == 401
    assert "Invalid or inactive API key" in response.json()["detail"]
