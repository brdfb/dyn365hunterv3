"""Partner Center referrals endpoints (Phase 2)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.db.session import get_db
from app.config import settings
from app.core.logging import logger
from app.core.referral_ingestion import sync_referrals_from_partner_center
from app.core.tasks import sync_partner_center_referrals_task


router = APIRouter(prefix="/api/referrals", tags=["referrals"])


class SyncReferralsRequest(BaseModel):
    """Request model for manual referral sync."""

    force: bool = False  # Force sync even if recently synced (future enhancement)


class SyncReferralsResponse(BaseModel):
    """Response model for referral sync operation."""

    success: bool
    message: str
    enqueued: bool = False  # Task enqueued successfully
    task_id: Optional[str] = None  # Celery task ID for monitoring/debugging
    success_count: int = 0  # Will be 0 initially (task runs async)
    failure_count: int = 0  # Will be 0 initially (task runs async)
    skipped_count: int = 0  # Will be 0 initially (task runs async)
    errors: List[str] = []


@router.post("/sync", response_model=SyncReferralsResponse)
async def sync_referrals(
    request: Optional[SyncReferralsRequest] = None,
    db: Session = Depends(get_db),
):
    """
    Manually sync referrals from Partner Center.

    **Note**: This is an internal/admin-only endpoint. Not intended for public API consumers.

    This endpoint:
    - Fetches referrals from Partner Center API
    - Normalizes domains from referrals
    - Upserts companies with Azure Tenant ID override
    - Triggers domain scans (idempotent - domain-based)
    - Tracks referral lifecycle in partner_center_referrals table

    **MVP**: This endpoint triggers async Celery task for long-running operation.
    Sync results are logged. Use `task_id` to monitor task execution.

    Args:
        request: Optional sync request (force flag for future enhancement)
        db: Database session

    Returns:
        SyncReferralsResponse with task_id and sync status

    Raises:
        400: If Partner Center integration is disabled (feature flag OFF)
        500: If sync operation fails
    """
    # Feature flag check
    if not settings.partner_center_enabled:
        raise HTTPException(
            status_code=400,
            detail="Partner Center integration is disabled. Enable feature flag to use this endpoint.",
        )

    try:
        # Trigger async Celery task for long-running sync operation
        # Task will handle sync_referrals_from_partner_center() execution
        task_result = sync_partner_center_referrals_task.delay()

        logger.info(
            "partner_center_sync_triggered",
            task_id=task_result.id,
            feature_flag_enabled=settings.partner_center_enabled,
        )

        # Return immediate response (task runs async)
        return SyncReferralsResponse(
            success=True,
            message="Referral sync task enqueued. Check logs for results.",
            enqueued=True,
            task_id=task_result.id,
            success_count=0,  # Will be updated by task (check logs)
            failure_count=0,
            skipped_count=0,
            errors=[],
        )

    except Exception as e:
        logger.error(
            "partner_center_sync_error",
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start referral sync: {str(e)}",
        )

