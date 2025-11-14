"""Dashboard endpoints for aggregated statistics."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db
from app.core.constants import HIGH_PRIORITY_SCORE


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardResponse(BaseModel):
    """Response model for dashboard statistics."""

    total_leads: int
    migration: int
    existing: int
    cold: int
    skip: int
    avg_score: float
    max_score: Optional[int] = None  # Maximum readiness score
    high_priority: int  # Migration + score >= HIGH_PRIORITY_SCORE


@router.get("", response_model=DashboardResponse)
async def get_dashboard(db: Session = Depends(get_db)):
    """
    Get dashboard statistics with aggregated lead data.

        Returns:
        DashboardResponse with:
        - total_leads: Total number of scanned leads
        - migration: Count of Migration segment leads
        - existing: Count of Existing segment leads
        - cold: Count of Cold segment leads
        - skip: Count of Skip segment leads
        - avg_score: Average readiness score
        - max_score: Maximum readiness score
        - high_priority: Count of high priority leads (Migration + score >= HIGH_PRIORITY_SCORE)
    """
    try:
        # Query for segment counts and average score
        # Only count leads that have been scanned (readiness_score IS NOT NULL)
        query = """
            SELECT 
                COUNT(*) AS total_leads,
                COUNT(CASE WHEN segment = 'Migration' THEN 1 END) AS migration,
                COUNT(CASE WHEN segment = 'Existing' THEN 1 END) AS existing,
                COUNT(CASE WHEN segment = 'Cold' THEN 1 END) AS cold,
                COUNT(CASE WHEN segment = 'Skip' THEN 1 END) AS skip,
                COALESCE(AVG(readiness_score), 0.0) AS avg_score,
                MAX(readiness_score) AS max_score,
                COUNT(CASE WHEN segment = 'Migration' AND readiness_score >= :high_priority_score THEN 1 END) AS high_priority
            FROM leads_ready
            WHERE readiness_score IS NOT NULL
        """

        result = db.execute(text(query), {"high_priority_score": HIGH_PRIORITY_SCORE})
        row = result.fetchone()

        if not row:
            # Empty database case
            return DashboardResponse(
                total_leads=0,
                migration=0,
                existing=0,
                cold=0,
                skip=0,
                avg_score=0.0,
                max_score=None,
                high_priority=0,
            )

        return DashboardResponse(
            total_leads=row.total_leads or 0,
            migration=row.migration or 0,
            existing=row.existing or 0,
            cold=row.cold or 0,
            skip=row.skip or 0,
            avg_score=float(row.avg_score) if row.avg_score else 0.0,
            max_score=int(row.max_score) if row.max_score is not None else None,
            high_priority=row.high_priority or 0,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
