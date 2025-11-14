"""Progress tracking endpoints for async operations."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.api.jobs import get_job, JobStatus


router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobProgressResponse(BaseModel):
    """Job progress response model."""

    job_id: str
    status: str
    total: int
    processed: int
    successful: int
    failed: int
    progress_percent: float
    remaining: int
    errors: List[str]
    message: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@router.get("/{job_id}", response_model=JobProgressResponse)
async def get_job_progress(job_id: str):
    """
    Get progress of a job by job_id.

    Args:
        job_id: Job identifier

    Returns:
        JobProgressResponse with current progress
    """
    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    progress_percent = (job.processed / job.total * 100) if job.total > 0 else 0.0
    remaining = job.total - job.processed

    return JobProgressResponse(
        job_id=job.job_id,
        status=job.status.value,
        total=job.total,
        processed=job.processed,
        successful=job.successful,
        failed=job.failed,
        progress_percent=round(progress_percent, 2),
        remaining=remaining,
        errors=job.errors,
        message=job.message,
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
    )
