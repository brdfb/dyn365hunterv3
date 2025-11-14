"""Progress tracking for bulk scan jobs using Redis."""

import json
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import redis
from app.config import settings


class ProgressTracker:
    """Track progress of bulk scan jobs in Redis."""

    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        self.job_prefix = "bulk_scan:job:"
        self.job_ttl = 3600  # 1 hour TTL

    def create_job(self, domain_list: List[str]) -> str:
        """
        Create a new bulk scan job.

        Args:
            domain_list: List of domains to scan

        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        job_key = f"{self.job_prefix}{job_id}"

        job_data = {
            "job_id": job_id,
            "status": "pending",
            "total": len(domain_list),
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "errors": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        self.redis_client.setex(job_key, self.job_ttl, json.dumps(job_data))

        # Store domain list separately
        domain_list_key = f"{job_key}:domains"
        self.redis_client.setex(domain_list_key, self.job_ttl, json.dumps(domain_list))

        return job_id

    def get_job(self, job_id: str) -> Optional[Dict]:
        """
        Get job status.

        Args:
            job_id: Job ID

        Returns:
            Job data or None if not found
        """
        job_key = f"{self.job_prefix}{job_id}"
        job_data = self.redis_client.get(job_key)

        if not job_data:
            return None

        return json.loads(job_data)

    def update_progress(
        self,
        job_id: str,
        processed: int,
        succeeded: int = 0,
        failed: int = 0,
        error: Optional[Dict] = None,
    ):
        """
        Update job progress.

        Args:
            job_id: Job ID
            processed: Number of domains processed
            succeeded: Number of domains succeeded
            failed: Number of domains failed
            error: Error details (if any)
        """
        job_key = f"{self.job_prefix}{job_id}"
        job_data = self.redis_client.get(job_key)

        if not job_data:
            return

        job = json.loads(job_data)
        job["processed"] = processed
        job["succeeded"] = succeeded
        job["failed"] = failed
        job["updated_at"] = datetime.utcnow().isoformat()

        if error:
            # Add timestamp if not present
            if "timestamp" not in error or error["timestamp"] is None:
                error["timestamp"] = datetime.utcnow().isoformat()
            job["errors"].append(error)

        # Calculate progress percentage
        if job["total"] > 0:
            job["progress"] = int((processed / job["total"]) * 100)
        else:
            job["progress"] = 0

        self.redis_client.setex(job_key, self.job_ttl, json.dumps(job))

    def set_status(self, job_id: str, status: str):
        """
        Set job status.

        Args:
            job_id: Job ID
            status: Status (pending, running, completed, failed)
        """
        job_key = f"{self.job_prefix}{job_id}"
        job_data = self.redis_client.get(job_key)

        if not job_data:
            return

        job = json.loads(job_data)
        job["status"] = status
        job["updated_at"] = datetime.utcnow().isoformat()

        self.redis_client.setex(job_key, self.job_ttl, json.dumps(job))

    def store_result(self, job_id: str, domain: str, result: Dict):
        """
        Store scan result for a domain.

        Args:
            job_id: Job ID
            domain: Domain name
            result: Scan result
        """
        results_key = f"{self.job_prefix}{job_id}:results"
        self.redis_client.hset(results_key, domain, json.dumps(result))
        self.redis_client.expire(results_key, self.job_ttl)

    def get_results(self, job_id: str) -> List[Dict]:
        """
        Get all scan results for a job.

        Args:
            job_id: Job ID

        Returns:
            List of scan results
        """
        results_key = f"{self.job_prefix}{job_id}:results"
        results = self.redis_client.hgetall(results_key)

        return [json.loads(result) for result in results.values()]

    def get_domain_list(self, job_id: str) -> Optional[List[str]]:
        """
        Get domain list for a job.

        Args:
            job_id: Job ID

        Returns:
            Domain list or None if not found
        """
        job_key = f"{self.job_prefix}{job_id}"
        domain_list_key = f"{job_key}:domains"
        domain_list_data = self.redis_client.get(domain_list_key)

        if not domain_list_data:
            return None

        return json.loads(domain_list_data)


# Global progress tracker instance
_progress_tracker: Optional[ProgressTracker] = None


def get_progress_tracker() -> ProgressTracker:
    """Get global progress tracker instance."""
    global _progress_tracker
    if _progress_tracker is None:
        _progress_tracker = ProgressTracker()
    return _progress_tracker
