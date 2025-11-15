"""API v1 progress endpoints - Proxy to legacy handlers."""

from fastapi import APIRouter
from app.api.progress import get_job_progress, JobProgressResponse

router = APIRouter(prefix="/jobs", tags=["progress", "v1"])


@router.get("/{job_id}", response_model=JobProgressResponse)
async def get_job_progress_v1(job_id: str):
    """V1 endpoint - Get progress of a job by job_id."""
    return await get_job_progress(job_id=job_id)

