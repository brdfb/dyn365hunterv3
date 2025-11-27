"""Dynamics 365 integration API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from app.config import settings
from app.core.logging import logger
from app.db.session import get_db
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

