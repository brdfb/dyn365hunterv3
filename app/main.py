"""FastAPI application entry point."""
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import settings
from app.db.session import get_db, engine
from app.api import ingest, scan, leads, dashboard, email_tools, progress, admin, notes, tags, favorites, pdf, rescan, alerts

# Create FastAPI app
app = FastAPI(
    title="Dyn365Hunter MVP",
    description="Lead intelligence engine for domain-based analysis",
    version="1.0.0"
)

# Register routers
app.include_router(ingest.router)
app.include_router(scan.router)
app.include_router(leads.router)
app.include_router(dashboard.router)
app.include_router(email_tools.router)
app.include_router(progress.router)
app.include_router(admin.router)
app.include_router(notes.router)
app.include_router(tags.router)
app.include_router(favorites.router)
app.include_router(pdf.router)
app.include_router(rescan.router)
app.include_router(alerts.router)

# Mount static files for Mini UI
import os
# Try multiple paths for Docker and local development
possible_paths = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "mini-ui"),  # Local dev
    "/app/mini-ui",  # Docker
    os.path.join(os.getcwd(), "mini-ui"),  # Fallback
]
mini_ui_path = None
for path in possible_paths:
    if os.path.exists(path):
        mini_ui_path = path
        break

if mini_ui_path:
    app.mount("/mini-ui", StaticFiles(directory=mini_ui_path, html=True), name="mini-ui")


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
        "version": "1.0.0",
        "docs": "/docs"
    }

