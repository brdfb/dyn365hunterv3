"""API v1 sales summary endpoint - Proxy to legacy handler."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.api.sales_summary import get_sales_summary, SalesSummaryResponse
from app.db.session import get_db

router = APIRouter(prefix="/leads", tags=["sales", "v1"])


@router.get("/{domain}/sales-summary", response_model=SalesSummaryResponse)
async def get_sales_summary_v1(
    domain: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """V1 endpoint - Get complete sales intelligence summary for a lead."""
    return await get_sales_summary(domain=domain, request=request, db=db)

