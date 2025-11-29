"""Dynamics 365 integration API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
from app.config import settings
from app.core.logging import logger
from app.db.session import get_db
from app.db.models import Company
from app.tasks.d365_push import push_lead_to_d365
from app.core.d365_metrics import track_push_requested


router = APIRouter(prefix="/d365", tags=["d365", "v1"])


class PushLeadRequest(BaseModel):
    """Request model for pushing a lead to D365."""
    lead_id: Optional[int] = None
    domain: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "lead_id": 123
            }
        }


class PushLeadResponse(BaseModel):
    """Response model for push lead endpoint."""
    status: str
    job_id: Optional[str] = None
    message: str


@router.post("/push-lead", response_model=PushLeadResponse, status_code=status.HTTP_202_ACCEPTED)
async def push_lead_to_d365_endpoint(
    request: PushLeadRequest,
    db: Session = Depends(get_db)
):
    """
    Push a lead to Dynamics 365.
    
    Accepts either lead_id or domain. Enqueues a Celery task and returns immediately.
    
    Returns:
        202 Accepted with job_id
    """
    if not settings.d365_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="D365 integration is disabled. Set HUNTER_D365_ENABLED=true to enable."
        )
    
    # Validate request
    if not request.lead_id and not request.domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either lead_id or domain must be provided"
        )
    
    # TODO: Validate lead exists in database
    # For now, skeleton implementation
    
    # Enqueue Celery task
    if request.lead_id:
        task = push_lead_to_d365.delay(request.lead_id)
        job_id = task.id
        # Phase 3: Track metrics
        track_push_requested()
    else:
        # TODO: Resolve domain to lead_id
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Domain-based push not yet implemented"
        )
    
    logger.info(
        "d365_push_enqueued",
        message="D365 push task enqueued",
        lead_id=request.lead_id,
        domain=request.domain,
        job_id=job_id
    )
    
    return PushLeadResponse(
        status="accepted",
        job_id=job_id,
        message="D365 push task enqueued (skeleton implementation)"
    )


class RetryLeadResponse(BaseModel):
    """Response model for retry lead endpoint."""
    status: str
    job_id: Optional[str] = None
    message: str


class BulkRetryRequest(BaseModel):
    """Request model for bulk retry endpoint."""
    lead_ids: List[int]
    
    class Config:
        json_schema_extra = {
            "example": {
                "lead_ids": [123, 456, 789]
            }
        }


class BulkRetryResponse(BaseModel):
    """Response model for bulk retry endpoint."""
    status: str
    total: int
    queued: int
    failed: int
    job_ids: List[str]
    message: str


@router.post("/retry/{lead_id}", response_model=RetryLeadResponse, status_code=status.HTTP_202_ACCEPTED)
async def retry_lead_to_d365(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """
    Manually retry pushing a lead to Dynamics 365.
    
    Resets the lead's sync status and enqueues a new push task.
    
    Returns:
        202 Accepted with job_id
    """
    if not settings.d365_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="D365 integration is disabled. Set HUNTER_D365_ENABLED=true to enable."
        )
    
    # Check if lead exists
    company = db.query(Company).filter(Company.id == lead_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} not found"
        )
    
    # Reset sync status to allow retry
    company.d365_sync_status = "pending"
    company.d365_sync_error = None
    company.d365_sync_attempt_count = 0  # Reset attempt count
    db.commit()
    
    # Enqueue Celery task
    task = push_lead_to_d365.delay(lead_id)
    job_id = task.id
    track_push_requested()
    
    logger.info(
        "d365_retry_enqueued",
        message="D365 retry task enqueued",
        lead_id=lead_id,
        domain=company.domain,
        job_id=job_id
    )
    
    return RetryLeadResponse(
        status="accepted",
        job_id=job_id,
        message=f"D365 retry task enqueued for lead {lead_id}"
    )


@router.post("/retry-bulk", response_model=BulkRetryResponse, status_code=status.HTTP_202_ACCEPTED)
async def retry_leads_bulk(
    request: BulkRetryRequest,
    db: Session = Depends(get_db)
):
    """
    Manually retry pushing multiple leads to Dynamics 365.
    
    Resets the sync status for all leads and enqueues push tasks.
    
    Returns:
        202 Accepted with job_ids
    """
    if not settings.d365_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="D365 integration is disabled. Set HUNTER_D365_ENABLED=true to enable."
        )
    
    if not request.lead_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="lead_ids list cannot be empty"
        )
    
    # Check if leads exist and reset their status
    companies = db.query(Company).filter(Company.id.in_(request.lead_ids)).all()
    existing_ids = {c.id for c in companies}
    missing_ids = set(request.lead_ids) - existing_ids
    
    # Reset sync status for existing leads
    for company in companies:
        company.d365_sync_status = "pending"
        company.d365_sync_error = None
        company.d365_sync_attempt_count = 0  # Reset attempt count
    db.commit()
    
    # Enqueue Celery tasks for existing leads
    job_ids = []
    for company in companies:
        task = push_lead_to_d365.delay(company.id)
        job_ids.append(task.id)
        track_push_requested()
    
    logger.info(
        "d365_bulk_retry_enqueued",
        message="D365 bulk retry tasks enqueued",
        total=len(request.lead_ids),
        queued=len(job_ids),
        missing=len(missing_ids),
        missing_ids=list(missing_ids) if missing_ids else None
    )
    
    return BulkRetryResponse(
        status="accepted",
        total=len(request.lead_ids),
        queued=len(job_ids),
        failed=len(missing_ids),
        job_ids=job_ids,
        message=f"Enqueued {len(job_ids)} retry tasks. {len(missing_ids)} leads not found." if missing_ids else f"Enqueued {len(job_ids)} retry tasks."
    )

