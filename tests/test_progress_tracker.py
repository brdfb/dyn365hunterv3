"""Unit tests for progress tracking functionality."""
import pytest
import json
import sys
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Mock redis module before importing progress_tracker
mock_redis_module = MagicMock()
mock_redis_client_class = MagicMock()
mock_redis_module.from_url = mock_redis_client_class

# Add redis to sys.modules before importing
sys.modules['redis'] = mock_redis_module

from app.core.progress_tracker import ProgressTracker, get_progress_tracker


class TestProgressTracker:
    """Test progress tracker functionality."""
    
    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        redis_mock = Mock()
        redis_mock.get.return_value = None
        redis_mock.setex.return_value = None
        redis_mock.hset.return_value = None
        redis_mock.hgetall.return_value = {}
        redis_mock.expire.return_value = None
        return redis_mock
    
    @pytest.fixture
    def tracker(self, mock_redis):
        """Create a progress tracker with mocked Redis."""
        tracker = ProgressTracker()
        tracker.redis_client = mock_redis
        return tracker
    
    def test_create_job(self, tracker, mock_redis):
        """Test job creation."""
        domain_list = ["example.com", "google.com"]
        job_id = tracker.create_job(domain_list)
        
        # Should return a job ID
        assert job_id is not None
        assert isinstance(job_id, str)
        
        # Should call setex twice (job data + domain list)
        assert mock_redis.setex.call_count == 2
        
        # Check job data structure
        # setex(key, ttl, value) - so args are: (key, ttl, value)
        call_args = mock_redis.setex.call_args_list[0]
        job_key = call_args[0][0]
        job_data = json.loads(call_args[0][2])  # value is 3rd argument
        
        assert job_key.startswith("bulk_scan:job:")
        assert job_data["status"] == "pending"
        assert job_data["total"] == 2
        assert job_data["processed"] == 0
        assert job_data["succeeded"] == 0
        assert job_data["failed"] == 0
        assert job_data["errors"] == []
    
    def test_get_job_not_found(self, tracker, mock_redis):
        """Test getting non-existent job."""
        mock_redis.get.return_value = None
        result = tracker.get_job("nonexistent")
        assert result is None
    
    def test_get_job_found(self, tracker, mock_redis):
        """Test getting existing job."""
        job_data = {
            "job_id": "test-job",
            "status": "running",
            "total": 10,
            "processed": 5,
            "succeeded": 4,
            "failed": 1,
            "errors": []
        }
        mock_redis.get.return_value = json.dumps(job_data)
        
        result = tracker.get_job("test-job")
        assert result is not None
        assert result["status"] == "running"
        assert result["total"] == 10
        assert result["processed"] == 5
    
    def test_update_progress(self, tracker, mock_redis):
        """Test progress update."""
        # Setup existing job
        job_data = {
            "job_id": "test-job",
            "status": "running",
            "total": 10,
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "errors": []
        }
        mock_redis.get.return_value = json.dumps(job_data)
        
        # Update progress
        tracker.update_progress("test-job", 5, 4, 1, None)
        
        # Should call setex to update job
        assert mock_redis.setex.call_count > 0
        
        # Check updated data
        call_args = mock_redis.setex.call_args
        updated_job = json.loads(call_args[0][2])  # value is 3rd argument
        assert updated_job["processed"] == 5
        assert updated_job["succeeded"] == 4
        assert updated_job["failed"] == 1
        assert updated_job["progress"] == 50  # 5/10 * 100
    
    def test_update_progress_with_error(self, tracker, mock_redis):
        """Test progress update with error."""
        # Setup existing job
        job_data = {
            "job_id": "test-job",
            "status": "running",
            "total": 10,
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "errors": []
        }
        mock_redis.get.return_value = json.dumps(job_data)
        
        # Update progress with error
        error = {
            "domain": "example.com",
            "error": "Test error",
            "timestamp": None
        }
        tracker.update_progress("test-job", 1, 0, 1, error)
        
        # Check error was added
        call_args = mock_redis.setex.call_args
        updated_job = json.loads(call_args[0][2])  # value is 3rd argument
        assert len(updated_job["errors"]) == 1
        assert updated_job["errors"][0]["domain"] == "example.com"
        assert updated_job["errors"][0]["error"] == "Test error"
        assert updated_job["errors"][0]["timestamp"] is not None  # Should be set
    
    def test_set_status(self, tracker, mock_redis):
        """Test status update."""
        # Setup existing job
        job_data = {
            "job_id": "test-job",
            "status": "running",
            "total": 10,
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "errors": []
        }
        mock_redis.get.return_value = json.dumps(job_data)
        
        # Set status to completed
        tracker.set_status("test-job", "completed")
        
        # Check status was updated
        call_args = mock_redis.setex.call_args
        updated_job = json.loads(call_args[0][2])  # value is 3rd argument
        assert updated_job["status"] == "completed"
    
    def test_store_result(self, tracker, mock_redis):
        """Test storing scan result."""
        result = {
            "domain": "example.com",
            "score": 75,
            "segment": "Migration"
        }
        
        tracker.store_result("test-job", "example.com", result)
        
        # Should call hset to store result
        mock_redis.hset.assert_called_once()
        call_args = mock_redis.hset.call_args
        assert call_args[0][0].endswith(":results")
        assert call_args[0][1] == "example.com"
        stored_result = json.loads(call_args[0][2])
        assert stored_result["domain"] == "example.com"
        assert stored_result["score"] == 75
    
    def test_get_results(self, tracker, mock_redis):
        """Test getting scan results."""
        results = {
            "example.com": json.dumps({"domain": "example.com", "score": 75}),
            "google.com": json.dumps({"domain": "google.com", "score": 80})
        }
        mock_redis.hgetall.return_value = results
        
        results_list = tracker.get_results("test-job")
        
        assert len(results_list) == 2
        assert results_list[0]["domain"] in ["example.com", "google.com"]
    
    def test_get_domain_list(self, tracker, mock_redis):
        """Test getting domain list."""
        domain_list = ["example.com", "google.com"]
        mock_redis.get.return_value = json.dumps(domain_list)
        
        result = tracker.get_domain_list("test-job")
        
        assert result == domain_list
    
    def test_get_progress_tracker_singleton(self):
        """Test get_progress_tracker returns singleton."""
        # Reset singleton
        import app.core.progress_tracker
        app.core.progress_tracker._progress_tracker = None
        
        tracker1 = get_progress_tracker()
        tracker2 = get_progress_tracker()
        
        # Should return same instance
        assert tracker1 is tracker2
