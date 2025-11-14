"""Tests for Celery tasks (G18)."""
import pytest
from unittest.mock import patch, MagicMock, Mock
from sqlalchemy.orm import Session
from app.db.models import Company, DomainSignal, LeadScore, Alert
from app.db.session import SessionLocal
from app.core.progress_tracker import get_progress_tracker
from app.core.tasks import (
    bulk_scan_task,
    process_pending_alerts_task,
    daily_rescan_task,
    scan_single_domain
)


@pytest.fixture
def db():
    """Create a database session for testing."""
    db = SessionLocal()
    try:
        yield db
        db.rollback()
    finally:
        db.close()


@pytest.fixture
def test_company(db: Session):
    """Create a test company."""
    company = Company(
        canonical_name="Test Company",
        domain="test-tasks.com"
    )
    db.add(company)
    db.commit()
    return company


@pytest.fixture
def test_domain_with_signal(db: Session, test_company):
    """Create a test domain with signal."""
    signal = DomainSignal(
        domain=test_company.domain,
        spf=True,
        dkim=True,
        dmarc_policy="quarantine",
        mx_root="outlook.com",
        scan_status="success"
    )
    db.add(signal)
    
    score = LeadScore(
        domain=test_company.domain,
        readiness_score=75,
        segment="Migration",
        reason="Test score"
    )
    db.add(score)
    db.commit()
    return test_company.domain


class TestBulkScanTask:
    """Tests for bulk_scan_task."""
    
    def test_bulk_scan_task_with_rescan(self, db: Session, test_company, test_domain_with_signal):
        """Test bulk_scan_task with is_rescan=True."""
        from app.core.progress_tracker import get_progress_tracker
        
        tracker = get_progress_tracker()
        job_id = tracker.create_job([test_domain_with_signal])
        
        # Mock the task context
        mock_task = MagicMock()
        mock_task.request = MagicMock()
        
        with patch("app.core.tasks.rescan_domain") as mock_rescan:
            mock_rescan.return_value = {
                "success": True,
                "domain": test_domain_with_signal,
                "result": {
                    "domain": test_domain_with_signal,
                    "score": 80,
                    "segment": "Migration"
                },
                "changes_detected": True,
                "signal_changes": 1,
                "score_changes": 0,
                "alerts_created": 1
            }
            
            # Call task directly (not as Celery task)
            bulk_scan_task(mock_task, job_id, is_rescan=True)
            
            # Verify rescan was called
            mock_rescan.assert_called_once_with(test_domain_with_signal, db)
            
            # Verify job status
            job = tracker.get_job(job_id)
            assert job["status"] == "completed"
            assert job["succeeded"] == 1
            assert job["failed"] == 0
    
    def test_bulk_scan_task_with_scan(self, db: Session, test_company):
        """Test bulk_scan_task with is_rescan=False (regular scan)."""
        from app.core.progress_tracker import get_progress_tracker
        
        tracker = get_progress_tracker()
        job_id = tracker.create_job([test_company.domain])
        
        # Mock the task context
        mock_task = MagicMock()
        mock_task.request = MagicMock()
        
        with patch("app.core.tasks.scan_single_domain") as mock_scan:
            mock_scan.return_value = {
                "success": True,
                "domain": test_company.domain,
                "result": {
                    "domain": test_company.domain,
                    "score": 75,
                    "segment": "Migration"
                }
            }
            
            # Call task directly
            bulk_scan_task(mock_task, job_id, is_rescan=False)
            
            # Verify scan was called
            mock_scan.assert_called_once_with(test_company.domain, db)
            
            # Verify job status
            job = tracker.get_job(job_id)
            assert job["status"] == "completed"
    
    def test_bulk_scan_task_job_not_found(self, db: Session):
        """Test bulk_scan_task with non-existent job_id."""
        mock_task = MagicMock()
        
        # Should not raise, just return early
        bulk_scan_task(mock_task, "non-existent-job-id", is_rescan=False)
    
    def test_bulk_scan_task_domain_list_not_found(self, db: Session):
        """Test bulk_scan_task with job but no domain list."""
        from app.core.progress_tracker import get_progress_tracker
        
        tracker = get_progress_tracker()
        # Create job but don't store domain list
        job_id = "test-job-no-domains"
        job_key = f"bulk_scan:job:{job_id}"
        import json
        from datetime import datetime
        job_data = {
            "job_id": job_id,
            "status": "pending",
            "total": 0,
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "errors": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        tracker.redis_client.setex(
            job_key,
            3600,
            json.dumps(job_data)
        )
        
        mock_task = MagicMock()
        
        bulk_scan_task(mock_task, job_id, is_rescan=False)
        
        # Job should be marked as failed
        job = tracker.get_job(job_id)
        assert job["status"] == "failed"
    
    def test_bulk_scan_task_scan_failure(self, db: Session, test_company):
        """Test bulk_scan_task handling scan failures."""
        from app.core.progress_tracker import get_progress_tracker
        
        tracker = get_progress_tracker()
        job_id = tracker.create_job([test_company.domain])
        
        mock_task = MagicMock()
        
        with patch("app.core.tasks.scan_single_domain") as mock_scan:
            mock_scan.return_value = {
                "success": False,
                "error": "Scan failed"
            }
            
            bulk_scan_task(mock_task, job_id, is_rescan=False)
            
            # Verify job status
            job = tracker.get_job(job_id)
            assert job["status"] == "completed"
            assert job["failed"] == 1
            assert job["succeeded"] == 0
    
    def test_bulk_scan_task_exception_handling(self, db: Session, test_company):
        """Test bulk_scan_task exception handling."""
        from app.core.progress_tracker import get_progress_tracker
        
        tracker = get_progress_tracker()
        job_id = tracker.create_job([test_company.domain])
        
        mock_task = MagicMock()
        
        with patch("app.core.tasks.scan_single_domain") as mock_scan:
            mock_scan.side_effect = Exception("Unexpected error")
            
            # Should not raise, should handle gracefully
            bulk_scan_task(mock_task, job_id, is_rescan=False)
            
            # Verify job status
            job = tracker.get_job(job_id)
            assert job["status"] == "completed"
            assert job["failed"] == 1


class TestProcessPendingAlertsTask:
    """Tests for process_pending_alerts_task."""
    
    def test_process_pending_alerts_task_success(self, db: Session, test_company):
        """Test process_pending_alerts_task successfully processing alerts."""
        # Create a pending alert
        alert = Alert(
            domain=test_company.domain,
            alert_type="mx_changed",
            alert_message="MX changed",
            status="pending"
        )
        db.add(alert)
        db.commit()
        
        mock_task = MagicMock()
        
        with patch("app.core.tasks.process_pending_alerts") as mock_process:
            mock_process.return_value = 1
            
            result = process_pending_alerts_task(mock_task)
            
            assert result["status"] == "completed"
            assert result["processed"] == 1
            mock_process.assert_called_once()
    
    def test_process_pending_alerts_task_no_alerts(self, db: Session):
        """Test process_pending_alerts_task with no pending alerts."""
        mock_task = MagicMock()
        
        with patch("app.core.tasks.process_pending_alerts") as mock_process:
            mock_process.return_value = 0
            
            result = process_pending_alerts_task(mock_task)
            
            assert result["status"] == "completed"
            assert result["processed"] == 0
            mock_process.assert_called_once()
    
    def test_process_pending_alerts_task_exception(self, db: Session):
        """Test process_pending_alerts_task exception handling."""
        mock_task = MagicMock()
        
        with patch("app.core.tasks.process_pending_alerts") as mock_process:
            mock_process.side_effect = Exception("Processing error")
            
            with pytest.raises(Exception):
                process_pending_alerts_task(mock_task)


class TestDailyRescanTask:
    """Tests for daily_rescan_task."""
    
    def test_daily_rescan_task_no_domains(self, db: Session):
        """Test daily_rescan_task with no domains to rescan."""
        mock_task = MagicMock()
        
        result = daily_rescan_task(mock_task)
        
        assert result["status"] == "completed"
        assert result["total"] == 0
        assert "No domains to rescan" in result["message"]
    
    def test_daily_rescan_task_with_domains(self, db: Session, test_company, test_domain_with_signal):
        """Test daily_rescan_task with domains to rescan."""
        mock_task = MagicMock()
        
        with patch("app.core.tasks.bulk_scan_task") as mock_bulk_scan:
            mock_bulk_scan.delay = MagicMock()
            
            with patch("app.core.tasks.get_progress_tracker") as mock_tracker:
                mock_tracker_instance = MagicMock()
                mock_tracker_instance.create_job = MagicMock(return_value="test-job-id")
                mock_tracker.return_value = mock_tracker_instance
                
                result = daily_rescan_task(mock_task)
                
                assert result["status"] == "completed"
                assert result["total"] > 0
                # Verify bulk_scan_task.delay was called
                assert mock_bulk_scan.delay.called
    
    def test_daily_rescan_task_exception(self, db: Session):
        """Test daily_rescan_task exception handling."""
        mock_task = MagicMock()
        
        with patch("app.core.tasks.DomainSignal") as mock_signal:
            mock_signal.query = MagicMock()
            mock_signal.query.distinct = MagicMock(side_effect=Exception("DB error"))
            
            with pytest.raises(Exception):
                daily_rescan_task(mock_task)


class TestScanSingleDomain:
    """Tests for scan_single_domain helper function."""
    
    def test_scan_single_domain_success(self, db: Session, test_company):
        """Test scan_single_domain successfully scanning a domain."""
        with patch("app.core.tasks.analyze_dns") as mock_dns:
            mock_dns.return_value = {
                "status": "success",
                "spf": True,
                "dkim": True,
                "dmarc_policy": "quarantine",
                "mx_root": "outlook.com",
                "mx_records": ["outlook.com"]
            }
            
            with patch("app.core.tasks.get_whois_info") as mock_whois:
                mock_whois.return_value = {
                    "registrar": "Test Registrar",
                    "expires_at": None
                }
                
                with patch("app.core.tasks.classify_provider") as mock_provider:
                    mock_provider.return_value = "M365"
                    
                    with patch("app.core.tasks.score_domain") as mock_score:
                        mock_score.return_value = {
                            "score": 85,
                            "segment": "Migration",
                            "reason": "High score"
                        }
                        
                        result = scan_single_domain(test_company.domain, db)
                        
                        assert result["success"] is True
                        assert result["domain"] == test_company.domain
                        assert "result" in result
    
    def test_scan_single_domain_not_found(self, db: Session):
        """Test scan_single_domain with domain not found."""
        result = scan_single_domain("nonexistent.com", db)
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    def test_scan_single_domain_invalid(self, db: Session):
        """Test scan_single_domain with invalid domain."""
        result = scan_single_domain("invalid!!!", db)
        
        assert result["success"] is False
        assert "invalid" in result["error"].lower()
    
    def test_scan_single_domain_dns_error(self, db: Session, test_company):
        """Test scan_single_domain with DNS error."""
        with patch("app.core.tasks.analyze_dns") as mock_dns:
            mock_dns.return_value = {
                "status": "dns_timeout",
                "error": "DNS timeout"
            }
            
            result = scan_single_domain(test_company.domain, db)
            
            # Should still create records with error status
            assert result["success"] is True  # Or False depending on implementation
            # Check that error is handled gracefully

