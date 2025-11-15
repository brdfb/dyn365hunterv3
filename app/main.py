"""FastAPI application entry point."""

import json
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import settings
from app.db.session import get_db, engine
from app.core.middleware import RequestIDMiddleware
from app.core.error_tracking import *  # Initialize Sentry
from app.api import (
    ingest,
    scan,
    leads,
    dashboard,
    email_tools,
    progress,
    admin,
    notes,
    tags,
    favorites,
    pdf,
    rescan,
    alerts,
    health,
    auth,
)
from app.api.v1 import (
    ingest as ingest_v1,
    scan as scan_v1,
    leads as leads_v1,
    dashboard as dashboard_v1,
    email_tools as email_tools_v1,
    progress as progress_v1,
    admin as admin_v1,
    notes as notes_v1,
    tags as tags_v1,
    favorites as favorites_v1,
    pdf as pdf_v1,
    rescan as rescan_v1,
    alerts as alerts_v1,
)
from fastapi import APIRouter


class UTF8JSONResponse(JSONResponse):
    """Custom JSONResponse that ensures UTF-8 encoding for Turkish characters."""
    
    def render(self, content: any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


# Create FastAPI app with custom JSON encoder
app = FastAPI(
    title="Dyn365Hunter MVP",
    description="Lead intelligence engine for domain-based analysis",
    version="1.0.0",
    default_response_class=UTF8JSONResponse,
)

# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

# Health and auth routers (no versioning - infrastructure endpoints)
app.include_router(health.router)
app.include_router(auth.router)  # G19: Microsoft SSO

# API v1 routers (versioned API)
v1_router = APIRouter(prefix="/api/v1", tags=["v1"])
v1_router.include_router(ingest_v1.router, prefix="/ingest", tags=["ingest"])
v1_router.include_router(scan_v1.router, prefix="/scan", tags=["scan"])
v1_router.include_router(leads_v1.router, prefix="/leads", tags=["leads"])
v1_router.include_router(dashboard_v1.router, prefix="/dashboard", tags=["dashboard"])
v1_router.include_router(email_tools_v1.router, prefix="/email", tags=["email"])
v1_router.include_router(progress_v1.router, prefix="/jobs", tags=["progress"])
v1_router.include_router(admin_v1.router, prefix="/admin", tags=["admin"])
v1_router.include_router(notes_v1.router, prefix="/leads", tags=["notes"])
v1_router.include_router(tags_v1.router, prefix="/leads", tags=["tags"])
v1_router.include_router(favorites_v1.router, prefix="/leads", tags=["favorites"])
v1_router.include_router(pdf_v1.router, prefix="/leads", tags=["pdf"])
v1_router.include_router(rescan_v1.router, prefix="/scan", tags=["rescan"])
v1_router.include_router(alerts_v1.router, prefix="/alerts", tags=["alerts"])
app.include_router(v1_router)

# Legacy routers (backward compatibility - will be deprecated in future)
app.include_router(ingest.router, prefix="/ingest", tags=["ingest", "legacy"])
app.include_router(scan.router, prefix="/scan", tags=["scan", "legacy"])
app.include_router(leads.router, prefix="/leads", tags=["leads", "legacy"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard", "legacy"])
app.include_router(email_tools.router, prefix="/email", tags=["email", "legacy"])
app.include_router(progress.router, prefix="/jobs", tags=["progress", "legacy"])
app.include_router(admin.router, prefix="/admin", tags=["admin", "legacy"])
app.include_router(notes.router, prefix="/notes", tags=["notes", "legacy"])
app.include_router(tags.router, prefix="/leads", tags=["tags", "legacy"])  # Note: tags router uses /leads prefix
app.include_router(favorites.router, prefix="/leads", tags=["favorites", "legacy"])  # Note: favorites router uses /leads prefix
app.include_router(pdf.router, prefix="/leads", tags=["pdf", "legacy"])
app.include_router(rescan.router, prefix="/scan", tags=["rescan", "legacy"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts", "legacy"])

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
    app.mount(
        "/mini-ui", StaticFiles(directory=mini_ui_path, html=True), name="mini-ui"
    )


# Legacy health check endpoint moved to app/api/health.py
# Keeping for backward compatibility but redirecting to health router


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Dyn365Hunter MVP API", "version": "1.0.0", "docs": "/docs"}
