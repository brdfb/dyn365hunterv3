"""Tests for UI upgrade features (G19): sorting, pagination, search."""

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
    # Check if columns exist, if not add them
    try:
        with engine.connect() as conn:
            # Check if contact_quality_score column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='companies' AND column_name='contact_quality_score'
            """))
            if result.fetchone() is None:
                # Add missing columns
                conn.execute(text("""
                    ALTER TABLE companies 
                    ADD COLUMN IF NOT EXISTS contact_emails JSONB,
                    ADD COLUMN IF NOT EXISTS contact_quality_score INTEGER,
                    ADD COLUMN IF NOT EXISTS linkedin_pattern VARCHAR(255)
                """))
                conn.commit()
    except Exception:
        # If migration fails, continue (columns may already exist)
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
    """Create test leads for UI upgrade tests."""
    # Create test companies with different scores, segments, providers
    test_domains = [
        ("example1.com", "Example 1 Inc", "M365", "Migration", 85),
        ("example2.com", "Example 2 Corp", "Google", "Existing", 60),
        ("example3.com", "Example 3 Ltd", "M365", "Migration", 75),
        ("example4.com", "Example 4 LLC", "Yandex", "Cold", 40),
        ("example5.com", "Example 5 SA", "M365", "Migration", 90),
        ("testdomain.com", "Test Domain Inc", "Google", "Existing", 55),
        ("another.com", "Another Corp", "M365", "Migration", 80),
        ("sample.com", "Sample Ltd", "Zoho", "Cold", 35),
    ]

    companies = []
    for domain, name, provider, segment, score in test_domains:
        company = Company(
            domain=domain,
            canonical_name=name,
            provider=provider,
        )
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


class TestSorting:
    """Test sorting functionality."""

    def test_sort_by_domain_asc(self, client, test_leads):
        """Test sorting by domain ascending."""
        response = client.get("/leads?sort_by=domain&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        assert "leads" in data
        leads = data["leads"]
        assert len(leads) > 0

        # Check if sorted by domain (ascending)
        domains = [lead["domain"] for lead in leads]
        assert domains == sorted(domains)

    def test_sort_by_domain_desc(self, client, test_leads):
        """Test sorting by domain descending."""
        response = client.get("/leads?sort_by=domain&sort_order=desc")
        assert response.status_code == 200
        data = response.json()
        leads = data["leads"]
        domains = [lead["domain"] for lead in leads]
        assert domains == sorted(domains, reverse=True)

    def test_sort_by_readiness_score_asc(self, client, test_leads):
        """Test sorting by readiness_score ascending."""
        response = client.get("/leads?sort_by=readiness_score&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        leads = data["leads"]
        scores = [
            lead["readiness_score"] if lead["readiness_score"] is not None else -1
            for lead in leads
        ]
        assert scores == sorted(scores)

    def test_sort_by_readiness_score_desc(self, client, test_leads):
        """Test sorting by readiness_score descending."""
        response = client.get("/leads?sort_by=readiness_score&sort_order=desc")
        assert response.status_code == 200
        data = response.json()
        leads = data["leads"]
        scores = [
            lead["readiness_score"] if lead["readiness_score"] is not None else -1
            for lead in leads
        ]
        assert scores == sorted(scores, reverse=True)

    def test_sort_by_provider(self, client, test_leads):
        """Test sorting by provider."""
        response = client.get("/leads?sort_by=provider&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        leads = data["leads"]
        providers = [lead["provider"] or "" for lead in leads]
        assert providers == sorted(providers)

    def test_sort_by_segment(self, client, test_leads):
        """Test sorting by segment."""
        response = client.get("/leads?sort_by=segment&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        leads = data["leads"]
        segments = [lead["segment"] or "" for lead in leads]
        assert segments == sorted(segments)

    def test_sort_invalid_field(self, client, test_leads):
        """Test sorting with invalid field falls back to default."""
        response = client.get("/leads?sort_by=invalid_field&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        assert "leads" in data
        # Should still return results with default sorting

    def test_sort_invalid_order(self, client, test_leads):
        """Test sorting with invalid order."""
        response = client.get("/leads?sort_by=domain&sort_order=invalid")
        assert response.status_code == 422  # Validation error


class TestPagination:
    """Test pagination functionality."""

    def test_pagination_default(self, client, test_leads):
        """Test default pagination (page 1, page_size 50)."""
        response = client.get("/leads")
        assert response.status_code == 200
        data = response.json()
        assert "leads" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert data["page"] == 1
        assert data["page_size"] == 50

    def test_pagination_page_1(self, client, test_leads):
        """Test pagination page 1."""
        response = client.get("/leads?page=1&page_size=3")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert len(data["leads"]) <= 3

    def test_pagination_page_2(self, client, test_leads):
        """Test pagination page 2."""
        response = client.get("/leads?page=2&page_size=3")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert len(data["leads"]) <= 3

    def test_pagination_page_size(self, client, test_leads):
        """Test custom page size."""
        response = client.get("/leads?page_size=5")
        assert response.status_code == 200
        data = response.json()
        assert data["page_size"] == 5
        assert len(data["leads"]) <= 5

    def test_pagination_max_page_size(self, client, test_leads):
        """Test max page size (200)."""
        response = client.get("/leads?page_size=200")
        assert response.status_code == 200
        data = response.json()
        assert data["page_size"] == 200

    def test_pagination_exceeds_max(self, client, test_leads):
        """Test page size exceeding max (200)."""
        response = client.get("/leads?page_size=300")
        assert response.status_code == 422  # Validation error

    def test_pagination_invalid_page(self, client, test_leads):
        """Test invalid page number (0 or negative)."""
        response = client.get("/leads?page=0")
        assert response.status_code == 422  # Validation error

    def test_pagination_total_pages(self, client, test_leads):
        """Test total_pages calculation."""
        response = client.get("/leads?page_size=3")
        assert response.status_code == 200
        data = response.json()
        assert "total_pages" in data
        # total_pages should be ceil(total / page_size)
        expected_pages = (data["total"] + 2) // 3  # Ceiling division
        assert data["total_pages"] == expected_pages


class TestSearch:
    """Test search functionality."""

    def test_search_by_domain(self, client, test_leads):
        """Test searching by domain."""
        response = client.get("/leads?search=example1")
        assert response.status_code == 200
        data = response.json()
        leads = data["leads"]
        # All results should contain "example1" in domain
        assert all("example1" in lead["domain"].lower() for lead in leads)

    def test_search_by_company_name(self, client, test_leads):
        """Test searching by company name."""
        response = client.get("/leads?search=Example")
        assert response.status_code == 200
        data = response.json()
        leads = data["leads"]
        # Results should contain "Example" in domain or canonical_name
        assert len(leads) > 0
        assert all(
            "example" in lead["domain"].lower()
            or (lead.get("canonical_name") and "example" in lead["canonical_name"].lower())
            for lead in leads
        )

    def test_search_by_provider(self, client, test_leads):
        """Test searching by provider."""
        response = client.get("/leads?search=M365")
        assert response.status_code == 200
        data = response.json()
        leads = data["leads"]
        # Results should contain "M365" in provider
        assert all(lead["provider"] == "M365" for lead in leads)

    def test_search_case_insensitive(self, client, test_leads):
        """Test search is case insensitive."""
        response1 = client.get("/leads?search=EXAMPLE")
        response2 = client.get("/leads?search=example")
        assert response1.status_code == 200
        assert response2.status_code == 200
        # Should return same results (case insensitive)
        data1 = response1.json()
        data2 = response2.json()
        assert data1["total"] == data2["total"]

    def test_search_no_results(self, client, test_leads):
        """Test search with no matching results."""
        response = client.get("/leads?search=nonexistentdomain12345")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["leads"]) == 0

    def test_search_empty_string(self, client, test_leads):
        """Test search with empty string returns all results."""
        response = client.get("/leads?search=")
        assert response.status_code == 200
        data = response.json()
        # Should return all leads (empty search is ignored)
        assert data["total"] > 0


class TestCombinedFeatures:
    """Test combining sorting, pagination, and search."""

    def test_sort_and_pagination(self, client, test_leads):
        """Test sorting combined with pagination."""
        response = client.get("/leads?sort_by=readiness_score&sort_order=desc&page=1&page_size=3")
        assert response.status_code == 200
        data = response.json()
        leads = data["leads"]
        assert len(leads) <= 3
        # Check if sorted descending
        scores = [
            lead["readiness_score"] if lead["readiness_score"] is not None else -1
            for lead in leads
        ]
        assert scores == sorted(scores, reverse=True)

    def test_search_and_pagination(self, client, test_leads):
        """Test search combined with pagination."""
        response = client.get("/leads?search=M365&page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["leads"]) <= 2
        # All results should match search
        assert all(lead["provider"] == "M365" for lead in data["leads"])

    def test_search_and_sort(self, client, test_leads):
        """Test search combined with sorting."""
        response = client.get("/leads?search=example&sort_by=domain&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        leads = data["leads"]
        domains = [lead["domain"] for lead in leads]
        assert domains == sorted(domains)

    def test_all_features_combined(self, client, test_leads):
        """Test sorting, pagination, and search all together."""
        response = client.get(
            "/leads?search=M365&sort_by=readiness_score&sort_order=desc&page=1&page_size=2"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["leads"]) <= 2
        # All results should match search
        assert all(lead["provider"] == "M365" for lead in data["leads"])
        # Should be sorted descending
        scores = [
            lead["readiness_score"] if lead["readiness_score"] is not None else -1
            for lead in data["leads"]
        ]
        assert scores == sorted(scores, reverse=True)

