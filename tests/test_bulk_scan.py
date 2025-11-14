"""Integration tests for bulk scan functionality."""
import pytest
import os
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from unittest.mock import patch, Mock

from app.db.models import Base, Company
from app.main import app

# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv(
        "DATABASE_URL",
        "postgresql://dyn365hunter:password123@localhost:5432/dyn365hunter"
    )
)

# Test Redis URL
TEST_REDIS_URL = os.getenv(
    "TEST_REDIS_URL",
    os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/1"  # Use DB 1 for testing
    )
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
        transaction.rollback()
        connection.close()
        session.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides = {}
    from app.db.session import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_domains(db_session):
    """Create sample domains in database."""
    domains = ["example.com", "google.com", "microsoft.com"]
    companies = []
    
    for domain in domains:
        company = Company(
            domain=domain,
            company_name=f"{domain} Inc",
            email=f"contact@{domain}",
            website=f"https://{domain}"
        )
        db_session.add(company)
        companies.append(company)
    
    db_session.commit()
    return domains


class TestBulkScanAPI:
    """Test bulk scan API endpoints."""
    
    def test_bulk_scan_create_job(self, test_client, sample_domains):
        """Test creating a bulk scan job."""
        with patch('app.core.tasks.bulk_scan_task.delay') as mock_task:
            response = test_client.post(
                "/scan/bulk",
                json={"domain_list": sample_domains}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "job_id" in data
            assert data["total"] == len(sample_domains)
            assert data["message"] == "Bulk scan job created successfully"
            
            # Should trigger Celery task
            mock_task.assert_called_once()
    
    def test_bulk_scan_invalid_domain(self, test_client, sample_domains):
        """Test bulk scan with invalid domain."""
        invalid_domains = sample_domains + ["invalid-domain-format!!!"]
        
        response = test_client.post(
            "/scan/bulk",
            json={"domain_list": invalid_domains}
        )
        
        # Should normalize and filter invalid domains
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == len(sample_domains)  # Only valid domains
    
    def test_bulk_scan_missing_domain(self, test_client, sample_domains):
        """Test bulk scan with domain not in database."""
        missing_domains = sample_domains + ["nonexistent.com"]
        
        response = test_client.post(
            "/scan/bulk",
            json={"domain_list": missing_domains}
        )
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
    
    def test_bulk_scan_empty_list(self, test_client):
        """Test bulk scan with empty domain list."""
        response = test_client.post(
            "/scan/bulk",
            json={"domain_list": []}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_bulk_scan_too_many_domains(self, test_client, sample_domains):
        """Test bulk scan with too many domains."""
        too_many = sample_domains * 500  # 1500 domains (max is 1000)
        
        response = test_client.post(
            "/scan/bulk",
            json={"domain_list": too_many}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_bulk_scan_status_not_found(self, test_client):
        """Test getting status for non-existent job."""
        response = test_client.get("/scan/bulk/nonexistent-job-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_bulk_scan_status(self, test_client, sample_domains):
        """Test getting bulk scan job status."""
        from app.core.progress_tracker import get_progress_tracker
        
        # Create job
        tracker = get_progress_tracker()
        job_id = tracker.create_job(sample_domains)
        tracker.set_status(job_id, "running")
        tracker.update_progress(job_id, 1, 1, 0, None)
        
        # Get status
        response = test_client.get(f"/scan/bulk/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] == "running"
        assert data["total"] == len(sample_domains)
        assert data["processed"] == 1
        assert data["progress"] > 0
    
    def test_get_bulk_scan_results_not_completed(self, test_client, sample_domains):
        """Test getting results for non-completed job."""
        from app.core.progress_tracker import get_progress_tracker
        
        # Create job
        tracker = get_progress_tracker()
        job_id = tracker.create_job(sample_domains)
        tracker.set_status(job_id, "running")
        
        # Try to get results
        response = test_client.get(f"/scan/bulk/{job_id}/results")
        
        assert response.status_code == 400
        assert "not completed" in response.json()["detail"].lower()
    
    def test_get_bulk_scan_results(self, test_client, sample_domains):
        """Test getting bulk scan results."""
        from app.core.progress_tracker import get_progress_tracker
        
        # Create job and add results
        tracker = get_progress_tracker()
        job_id = tracker.create_job(sample_domains)
        tracker.set_status(job_id, "completed")
        tracker.update_progress(job_id, len(sample_domains), len(sample_domains), 0, None)
        
        # Add results
        for domain in sample_domains:
            tracker.store_result(job_id, domain, {
                "domain": domain,
                "score": 75,
                "segment": "Migration"
            })
        
        # Get results
        response = test_client.get(f"/scan/bulk/{job_id}/results")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["total"] == len(sample_domains)
        assert data["succeeded"] == len(sample_domains)
        assert len(data["results"]) == len(sample_domains)


class TestBulkScanTask:
    """Test bulk scan Celery task."""
    
    def test_scan_single_domain_success(self, db_session, sample_domains):
        """Test scanning a single domain successfully."""
        from app.core.tasks import scan_single_domain
        
        domain = sample_domains[0]
        result = scan_single_domain(domain, db_session)
        
        assert result["success"] is True
        assert result["domain"] == domain
        assert "result" in result
        assert result["result"]["domain"] == domain
        assert "score" in result["result"]
    
    def test_scan_single_domain_not_found(self, db_session):
        """Test scanning a domain that doesn't exist."""
        from app.core.tasks import scan_single_domain
        
        result = scan_single_domain("nonexistent.com", db_session)
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()
    
    def test_scan_single_domain_invalid(self, db_session):
        """Test scanning an invalid domain."""
        from app.core.tasks import scan_single_domain
        
        result = scan_single_domain("invalid-domain-format!!!", db_session)
        
        assert result["success"] is False
        assert "error" in result
        assert "invalid" in result["error"].lower()
    
    @pytest.mark.skip(reason="Requires Redis and Celery worker running")
    def test_bulk_scan_task_integration(self, db_session, sample_domains):
        """Test bulk scan task end-to-end (requires Redis)."""
        from app.core.progress_tracker import get_progress_tracker
        from app.core.tasks import bulk_scan_task
        
        # Create job
        tracker = get_progress_tracker()
        job_id = tracker.create_job(sample_domains)
        
        # Run task (synchronously for testing)
        bulk_scan_task(job_id)
        
        # Check results
        job = tracker.get_job(job_id)
        assert job["status"] == "completed"
        assert job["processed"] == len(sample_domains)
        assert job["succeeded"] > 0
        
        # Check results stored
        results = tracker.get_results(job_id)
        assert len(results) == job["succeeded"]

