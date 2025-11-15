"""API v1 PDF endpoints - Proxy to legacy handlers."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.pdf import get_pdf_summary
from app.db.session import get_db

router = APIRouter(prefix="/leads", tags=["pdf", "v1"])


@router.get("/{domain}/summary.pdf")
async def get_pdf_summary_v1(domain: str, db: Session = Depends(get_db)):
    """V1 endpoint - Generate a PDF summary for a domain."""
    return await get_pdf_summary(domain=domain, db=db)

