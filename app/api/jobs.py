"""Job tracking for async operations like CSV ingestion with scanning."""

import uuid
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class JobProgress:
    """Job progress tracking."""

    job_id: str
    status: JobStatus
    total: int
    processed: int = 0
    successful: int = 0
    failed: int = 0
    errors: list = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    message: str = ""


# In-memory job store (for MVP - can be replaced with Redis/DB later)
_job_store: Dict[str, JobProgress] = {}


def create_job(total: int, message: str = "") -> str:
    """Create a new job and return job_id."""
    job_id = str(uuid.uuid4())
    _job_store[job_id] = JobProgress(
        job_id=job_id,
        status=JobStatus.PENDING,
        total=total,
        message=message,
        started_at=datetime.utcnow(),
    )
    return job_id


def update_job_progress(
    job_id: str,
    processed: int = None,
    successful: int = None,
    failed: int = None,
    error: str = None,
    status: JobStatus = None,
    message: str = None,
) -> Optional[JobProgress]:
    """Update job progress."""
    if job_id not in _job_store:
        return None

    job = _job_store[job_id]

    if processed is not None:
        job.processed = processed
    if successful is not None:
        job.successful = successful
    if failed is not None:
        job.failed = failed
    if error:
        job.errors.append(error)
    if status:
        job.status = status
    if message:
        job.message = message

    # Auto-update status based on progress
    if job.processed >= job.total:
        if job.status == JobStatus.PROCESSING:
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()

    return job


def get_job(job_id: str) -> Optional[JobProgress]:
    """Get job progress by job_id."""
    return _job_store.get(job_id)


def start_job(job_id: str) -> Optional[JobProgress]:
    """Mark job as processing."""
    if job_id not in _job_store:
        return None
    _job_store[job_id].status = JobStatus.PROCESSING
    return _job_store[job_id]


def complete_job(job_id: str, success: bool = True) -> Optional[JobProgress]:
    """Mark job as completed or failed."""
    if job_id not in _job_store:
        return None
    job = _job_store[job_id]
    job.status = JobStatus.COMPLETED if success else JobStatus.FAILED
    job.completed_at = datetime.utcnow()
    return job
