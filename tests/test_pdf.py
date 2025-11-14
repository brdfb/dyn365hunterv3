"""Tests for PDF summary endpoint (G17)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.models import Company, DomainSignal, LeadScore
from app.db.session import SessionLocal


client = TestClient(app)


@pytest.fixture
def db():
    """Create a database session for testing."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_domain(db: Session):
    """Create a test domain with scan data."""
    domain = "test-pdf.com"

    # Create company
    company = Company(
        canonical_name="Test PDF Company", domain=domain, provider="Google"
    )
    db.add(company)

    # Create domain signal
    signal = DomainSignal(
        domain=domain,
        spf=True,
        dkim=True,
        dmarc_policy="quarantine",
        mx_root="google.com",
        registrar="Test Registrar",
        scan_status="success",
    )
    db.add(signal)

    # Create lead score
    score = LeadScore(
        domain=domain,
        readiness_score=80,
        segment="Migration",
        reason="High readiness score for migration",
    )
    db.add(score)

    db.commit()
    return domain


def test_pdf_summary_generation(db: Session, test_domain: str):
    """Test PDF summary generation."""
    response = client.get(f"/leads/{test_domain}/summary.pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert test_domain in response.headers["content-disposition"]

    # Verify PDF content (basic check)
    assert len(response.content) > 0
    assert response.content.startswith(b"%PDF")


def test_pdf_summary_not_found(db: Session):
    """Test PDF summary for non-existent domain."""
    response = client.get("/leads/nonexistent.com/summary.pdf")
    assert response.status_code == 404


def test_pdf_summary_not_scanned(db: Session):
    """Test PDF summary for domain that hasn't been scanned."""
    domain = "not-scanned.com"

    # Create company but no scan data
    company = Company(canonical_name="Not Scanned", domain=domain, provider="Unknown")
    db.add(company)
    db.commit()

    response = client.get(f"/leads/{domain}/summary.pdf")
    assert response.status_code == 404
    assert "not been scanned" in response.json()["detail"]
