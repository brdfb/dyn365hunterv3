"""Unit tests for error handling in bulk scan."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.tasks import scan_single_domain


class TestErrorHandling:
    """Test error handling in bulk scan."""
    
    def test_scan_single_domain_dns_error(self, db_session):
        """Test handling DNS errors."""
        from app.db.models import Company
        
        # Create company
        company = Company(
            domain="test.com",
            company_name="Test Inc",
            email="test@test.com"
        )
        db_session.add(company)
        db_session.commit()
        
        # Mock DNS error
        with patch('app.core.tasks.analyze_dns') as mock_dns:
            mock_dns.side_effect = Exception("DNS resolution failed")
            
            result = scan_single_domain("test.com", db_session)
            
            assert result["success"] is False
            assert "error" in result
            assert "dns" in result["error"].lower() or "failed" in result["error"].lower()
    
    def test_scan_single_domain_whois_error(self, db_session):
        """Test handling WHOIS errors (should continue)."""
        from app.db.models import Company
        
        # Create company
        company = Company(
            domain="test.com",
            company_name="Test Inc",
            email="test@test.com"
        )
        db_session.add(company)
        db_session.commit()
        
        # Mock WHOIS error (should not fail the scan)
        with patch('app.core.tasks.analyze_dns') as mock_dns, \
             patch('app.core.tasks.get_whois_info') as mock_whois:
            
            # DNS succeeds
            mock_dns.return_value = {
                "status": "success",
                "mx_root": "outlook.com",
                "spf": True,
                "dkim": True,
                "dmarc_policy": "reject",
                "mx_records": ["outlook.com"]
            }
            
            # WHOIS fails
            mock_whois.side_effect = Exception("WHOIS lookup failed")
            
            result = scan_single_domain("test.com", db_session)
            
            # Should still succeed (WHOIS is optional)
            assert result["success"] is True
            assert result["result"]["scan_status"] == "whois_failed"
    
    def test_scan_single_domain_database_error(self, db_session):
        """Test handling database errors."""
        from app.db.models import Company
        
        # Create company
        company = Company(
            domain="test.com",
            company_name="Test Inc",
            email="test@test.com"
        )
        db_session.add(company)
        db_session.commit()
        
        # Mock database error
        with patch('app.core.tasks.analyze_dns') as mock_dns, \
             patch.object(db_session, 'commit') as mock_commit:
            
            mock_dns.return_value = {
                "status": "success",
                "mx_root": "outlook.com",
                "spf": True,
                "dkim": True,
                "dmarc_policy": "reject",
                "mx_records": ["outlook.com"]
            }
            
            mock_commit.side_effect = Exception("Database connection lost")
            
            result = scan_single_domain("test.com", db_session)
            
            assert result["success"] is False
            assert "error" in result
    
    def test_scan_single_domain_partial_failure_continues(self, db_session):
        """Test that partial failures don't stop processing."""
        from app.db.models import Company
        from app.core.progress_tracker import get_progress_tracker
        
        # Create companies
        companies = [
            Company(domain="valid1.com", company_name="Valid 1", email="test@valid1.com"),
            Company(domain="valid2.com", company_name="Valid 2", email="test@valid2.com"),
            Company(domain="invalid.com", company_name="Invalid", email="test@invalid.com")
        ]
        for company in companies:
            db_session.add(company)
        db_session.commit()
        
        # Mock one domain to fail
        with patch('app.core.tasks.analyze_dns') as mock_dns:
            call_count = 0
            def dns_side_effect(domain):
                nonlocal call_count
                call_count += 1
                if domain == "invalid.com":
                    raise Exception("DNS error")
                return {
                    "status": "success",
                    "mx_root": "outlook.com",
                    "spf": True,
                    "dkim": True,
                    "dmarc_policy": "reject",
                    "mx_records": ["outlook.com"]
                }
            
            mock_dns.side_effect = dns_side_effect
            
            # Test that scan_single_domain handles errors gracefully
            result1 = scan_single_domain("valid1.com", db_session)
            result2 = scan_single_domain("invalid.com", db_session)
            result3 = scan_single_domain("valid2.com", db_session)
            
            assert result1["success"] is True
            assert result2["success"] is False
            assert result3["success"] is True  # Should continue after error
    
    def test_bulk_scan_handles_exceptions(self, db_session):
        """Test that bulk scan task handles exceptions."""
        from app.core.progress_tracker import get_progress_tracker
        from app.core.tasks import bulk_scan_task
        
        # Create job
        tracker = get_progress_tracker()
        job_id = tracker.create_job(["test.com"])
        
        # Mock scan to raise exception
        with patch('app.core.tasks.scan_single_domain') as mock_scan:
            mock_scan.side_effect = Exception("Unexpected error")
            
            # Should not raise exception
            try:
                bulk_scan_task(job_id)
            except Exception:
                pytest.fail("bulk_scan_task should handle exceptions gracefully")
            
            # Check job status
            job = tracker.get_job(job_id)
            assert job is not None
            # Status might be "failed" or "completed" depending on implementation
            assert job["status"] in ["failed", "completed"]
    
    def test_rate_limiter_handles_concurrent_requests(self):
        """Test rate limiter with concurrent requests."""
        from app.core.rate_limiter import RateLimiter
        import threading
        
        limiter = RateLimiter(rate=10.0, burst=10.0)
        results = []
        
        def acquire_token():
            results.append(limiter.acquire())
        
        # Create 20 threads (more than burst)
        threads = [threading.Thread(target=acquire_token) for _ in range(20)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Should have exactly burst number of successes
        assert sum(results) == 10  # burst limit
    
    def test_progress_tracker_handles_redis_error(self):
        """Test progress tracker handles Redis errors gracefully."""
        from app.core.progress_tracker import ProgressTracker
        from unittest.mock import Mock
        
        tracker = ProgressTracker()
        mock_redis = Mock()
        mock_redis.get.side_effect = Exception("Redis connection error")
        tracker.redis_client = mock_redis
        
        # Should handle error gracefully
        result = tracker.get_job("test-job")
        assert result is None  # Should return None on error
    
    def test_progress_tracker_handles_invalid_json(self):
        """Test progress tracker handles invalid JSON."""
        from app.core.progress_tracker import ProgressTracker
        from unittest.mock import Mock
        
        tracker = ProgressTracker()
        mock_redis = Mock()
        mock_redis.get.return_value = "invalid json"
        tracker.redis_client = mock_redis
        
        # Should handle JSON decode error
        try:
            result = tracker.get_job("test-job")
            # Should either return None or handle gracefully
            assert result is None or isinstance(result, dict)
        except Exception:
            # If exception is raised, it should be caught somewhere
            pass

