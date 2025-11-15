"""API v1 dashboard endpoints - Proxy to legacy handlers."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dashboard import get_dashboard, get_kpis, DashboardResponse, KPIsResponse
from app.db.session import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard", "v1"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard_v1(db: Session = Depends(get_db)):
    """V1 endpoint - Get dashboard statistics with aggregated lead data."""
    return await get_dashboard(db=db)


@router.get("/kpis", response_model=KPIsResponse)
async def get_kpis_v1(db: Session = Depends(get_db)):
    """V1 endpoint - Get KPI statistics."""
    return await get_kpis(db=db)

