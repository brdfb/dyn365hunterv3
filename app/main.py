"""FastAPI application entry point."""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import settings
from app.db.session import get_db, engine
from app.api import ingest, scan, leads

# Create FastAPI app
app = FastAPI(
    title="Dyn365Hunter MVP",
    description="Lead intelligence engine for domain-based analysis",
    version="0.1.0"
)

# Register routers
app.include_router(ingest.router)
app.include_router(scan.router)
app.include_router(leads.router)


@app.get("/healthz")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    
    Returns:
        dict: Status and database connection status
    """
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
    
    return {
        "status": "ok",
        "database": db_status,
        "environment": settings.environment
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Dyn365Hunter MVP API",
        "version": "0.1.0",
        "docs": "/docs"
    }

