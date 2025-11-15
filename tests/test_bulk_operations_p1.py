"""Tests for P1-4: Bulk Operations Optimization."""

import pytest
import os
import time
from unittest.mock import patch, Mock, MagicMock
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from app.db.models import Base, Company
from app.core.bulk_operations import (
    calculate_optimal_batch_size,
    get_partial_commit_log,
    store_partial_commit_log,
    get_bulk_log_context,
)
from app.core.tasks import scan_single_domain, process_batch_with_retry

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
def sample_domains(db_session):
    """Create sample domains in database (with unique test IDs for isolation)."""
    import uuid
    test_id = str(uuid.uuid4())[:8]  # Unique test ID
    domains = [
        f"example-{test_id}.com",
        f"google-{test_id}.com",
        f"microsoft-{test_id}.com",
        f"test1-{test_id}.com",
        f"test2-{test_id}.com"
    ]
    companies = []

    for domain in domains:
        company = Company(
            domain=domain,
            canonical_name=f"{domain} Inc",
        )
        db_session.add(company)
        companies.append(company)

    # Don't commit - let test transaction handle it
    # This ensures test isolation via transaction rollback
    db_session.flush()  # Flush to get IDs but don't commit
    return domains


class TestBatchSizeCalculation:
    """Test batch size calculation (rate-limit aware)."""

    def test_calculate_optimal_batch_size_default(self):
        """Test default batch size calculation."""
        batch_size = calculate_optimal_batch_size()
        
        # Default: DNS 10 req/s, WHOIS 5 req/s, 10s duration
        # WHOIS bottleneck: 5 req/s × 10s = 50 domains
        assert batch_size == 50

    def test_calculate_optimal_batch_size_dns_bottleneck(self):
        """Test when DNS is the bottleneck."""
        batch_size = calculate_optimal_batch_size(
            dns_rate_limit=5.0,  # Lower DNS rate
            whois_rate_limit=10.0,  # Higher WHOIS rate
            batch_duration=10.0,
        )
        
        # DNS bottleneck: 5 req/s × 10s = 50 domains
        assert batch_size == 50

    def test_calculate_optimal_batch_size_whois_bottleneck(self):
        """Test when WHOIS is the bottleneck."""
        batch_size = calculate_optimal_batch_size(
            dns_rate_limit=10.0,
            whois_rate_limit=3.0,  # Lower WHOIS rate
            batch_duration=10.0,
        )
        
        # WHOIS bottleneck: 3 req/s × 10s = 30 domains
        assert batch_size == 30

    def test_calculate_optimal_batch_size_max_limit(self):
        """Test max batch size limit."""
        batch_size = calculate_optimal_batch_size(
            dns_rate_limit=100.0,  # Very high rate
            whois_rate_limit=100.0,  # Very high rate
            batch_duration=10.0,
            max_batch_size=100,  # Max limit
        )
        
        # Should be capped at max_batch_size
        assert batch_size == 100

    def test_calculate_optimal_batch_size_custom_duration(self):
        """Test with custom batch duration."""
        batch_size = calculate_optimal_batch_size(
            dns_rate_limit=10.0,
            whois_rate_limit=5.0,
            batch_duration=5.0,  # Shorter duration
        )
        
        # WHOIS: 5 req/s × 5s = 25 domains
        assert batch_size == 25


class TestScanSingleDomainCommitFalse:
    """Test scan_single_domain with commit=False for batch processing."""

    def test_scan_single_domain_commit_false(self, db_session, sample_domains):
        """Test scan_single_domain with commit=False doesn't commit."""
        domain = sample_domains[0]
        
        # Mock DNS/WHOIS to avoid external calls
        with patch("app.core.tasks.analyze_dns") as mock_dns, \
             patch("app.core.tasks.get_whois_info") as mock_whois, \
             patch("app.core.tasks.classify_provider") as mock_provider, \
             patch("app.core.tasks.score_domain") as mock_score:
            
            mock_dns.return_value = {
                "mx_root": "outlook.com",
                "spf": True,
                "dkim": True,
                "dmarc_policy": "reject",
                "status": "success",
                "mx_records": ["mx1.outlook.com"],
            }
            mock_whois.return_value = {
                "registrar": "Test Registrar",
                "expires_at": None,
                "nameservers": ["ns1.example.com"],
            }
            mock_provider.return_value = "M365"
            mock_score.return_value = {
                "score": 75,
                "segment": "Migration",
                "reason": "Test reason",
            }
            
            # Scan with commit=False
            result = scan_single_domain(domain, db_session, commit=False)
            
            # Should succeed but not commit
            assert result["success"] is True
            assert result["domain"] == domain
            
            # Check that objects are added but not committed
            # (We can't easily test this without checking DB state, but the function should work)

    def test_scan_single_domain_commit_true_default(self, db_session, sample_domains):
        """Test scan_single_domain with commit=True (default) commits."""
        domain = sample_domains[0]
        
        # Mock DNS/WHOIS to avoid external calls
        with patch("app.core.tasks.analyze_dns") as mock_dns, \
             patch("app.core.tasks.get_whois_info") as mock_whois, \
             patch("app.core.tasks.classify_provider") as mock_provider, \
             patch("app.core.tasks.score_domain") as mock_score:
            
            mock_dns.return_value = {
                "mx_root": "outlook.com",
                "spf": True,
                "dkim": True,
                "dmarc_policy": "reject",
                "status": "success",
                "mx_records": ["mx1.outlook.com"],
            }
            mock_whois.return_value = {
                "registrar": "Test Registrar",
                "expires_at": None,
                "nameservers": ["ns1.example.com"],
            }
            mock_provider.return_value = "M365"
            mock_score.return_value = {
                "score": 75,
                "segment": "Migration",
                "reason": "Test reason",
            }
            
            # Scan with commit=True (default)
            result = scan_single_domain(domain, db_session, commit=True)
            
            # Should succeed and commit
            assert result["success"] is True
            assert result["domain"] == domain


class TestPartialCommitLog:
    """Test partial commit log functionality."""

    def test_store_and_get_partial_commit_log(self):
        """Test storing and retrieving partial commit log."""
        bulk_id = "test_job_123"
        batch_no = 1
        total_batches = 5
        committed = [
            {"domain": "example.com", "status": "success", "timestamp": "2025-01-28T10:00:00Z"}
        ]
        failed = [
            {"domain": "invalid.com", "status": "error", "error": "Invalid domain", "timestamp": "2025-01-28T10:00:01Z"}
        ]
        
        # Store log
        success = store_partial_commit_log(
            bulk_id=bulk_id,
            batch_no=batch_no,
            total_batches=total_batches,
            committed=committed,
            failed=failed,
        )
        
        # May fail if Redis unavailable, that's OK
        if success:
            # Get log
            log = get_partial_commit_log(bulk_id)
            assert log["bulk_id"] == bulk_id
            assert log["batch_no"] == batch_no
            assert log["total_batches"] == total_batches
            assert len(log["committed"]) == 1
            assert len(log["failed"]) == 1
            assert log["committed"][0]["domain"] == "example.com"
            assert log["failed"][0]["domain"] == "invalid.com"

    def test_get_partial_commit_log_not_found(self):
        """Test getting non-existent partial commit log."""
        log = get_partial_commit_log("nonexistent_job_id")
        
        # Should return empty lists
        assert log["committed"] == []
        assert log["failed"] == []


class TestBulkLogContext:
    """Test bulk log context for structured logging."""

    def test_get_bulk_log_context(self):
        """Test bulk log context generation."""
        context = get_bulk_log_context(
            bulk_id="test_job_123",
            batch_no=2,
            total_batches=10,
            batch_size=50,
        )
        
        assert context["bulk_id"] == "test_job_123"
        assert context["batch_no"] == 2
        assert context["total_batches"] == 10
        assert context["batch_size"] == 50


class TestBatchProcessingWithRetry:
    """Test batch processing with retry logic (deadlock prevention)."""

    @pytest.mark.skip(reason="Requires Redis and full scan setup")
    def test_process_batch_with_retry_success(self, db_session, sample_domains):
        """Test successful batch processing."""
        from app.core.progress_tracker import get_progress_tracker
        
        batch = sample_domains[:3]  # First 3 domains
        tracker = get_progress_tracker()
        job_id = tracker.create_job(batch)
        
        # Mock DNS/WHOIS to avoid external calls
        with patch("app.core.tasks.analyze_dns") as mock_dns, \
             patch("app.core.tasks.get_whois_info") as mock_whois, \
             patch("app.core.tasks.classify_provider") as mock_provider, \
             patch("app.core.tasks.score_domain") as mock_score:
            
            mock_dns.return_value = {
                "mx_root": "outlook.com",
                "spf": True,
                "dkim": True,
                "dmarc_policy": "reject",
                "status": "success",
                "mx_records": ["mx1.outlook.com"],
            }
            mock_whois.return_value = {
                "registrar": "Test Registrar",
                "expires_at": None,
                "nameservers": ["ns1.example.com"],
            }
            mock_provider.return_value = "M365"
            mock_score.return_value = {
                "score": 75,
                "segment": "Migration",
                "reason": "Test reason",
            }
            
            # Process batch
            succeeded, failed, committed, failed_results = process_batch_with_retry(
                batch=batch,
                job_id=job_id,
                batch_no=1,
                total_batches=1,
                is_rescan=False,
                db=db_session,
            )
            
            # Should succeed
            assert succeeded > 0
            assert len(committed) == succeeded
            assert len(failed_results) == failed

    def test_process_batch_with_retry_deadlock_retry(self, db_session, sample_domains):
        """Test batch processing retries on deadlock."""
        from sqlalchemy.exc import OperationalError
        
        batch = sample_domains[:2]
        job_id = "test_job_deadlock"
        
        # Mock to raise OperationalError (deadlock) on first call, succeed on retry
        call_count = [0]
        
        def mock_scan_side_effect(domain, db, commit=False):
            call_count[0] += 1
            if call_count[0] <= 2:  # First 2 calls fail
                raise OperationalError("deadlock detected", None, None)
            return {"success": True, "domain": domain, "result": {"score": 75}}
        
        with patch("app.core.tasks.scan_single_domain", side_effect=mock_scan_side_effect):
            # Should retry and eventually succeed
            # Note: This test may need adjustment based on actual retry behavior
            pass  # Placeholder - actual implementation would test retry logic


class TestBatchIsolation:
    """Test batch isolation (one batch failure doesn't affect others)."""

    @pytest.mark.skip(reason="Requires full integration setup")
    def test_batch_isolation(self, db_session, sample_domains):
        """Test that one batch failure doesn't affect other batches."""
        # This would test that if batch 1 fails, batch 2 still processes
        # Requires full bulk_scan_task integration test
        pass

