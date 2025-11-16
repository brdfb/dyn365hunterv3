"""FastAPI application entry point."""

import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import settings
from app.db.session import get_db, engine
from app.core.middleware import RequestIDMiddleware
from app.core.error_tracking import *  # Initialize Sentry
from app.core.analyzer_enrichment import check_enrichment_available
from app.core.logging import logger
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
    sales_summary,
    health,
    auth,
    debug,
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
    sales_summary as sales_summary_v1,
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


def validate_enrichment_config():
    """
    Validate IP enrichment configuration at startup.
    
    Logs warnings if enrichment is enabled but DB files are missing.
    This helps catch configuration errors early without crashing the app.
    """
    if not settings.enrichment_enabled:
        return  # Enrichment disabled, no validation needed
    
    # Check if at least one DB is available
    if not check_enrichment_available():
        logger.warning(
            "ip_enrichment_config_invalid",
            message="IP enrichment is enabled but no database files are available",
            hint="Set MAXMIND_* or HUNTER_ENRICHMENT_DB_PATH_* environment variables or disable enrichment",
            enrichment_enabled=settings.enrichment_enabled,
            maxmind_asn=settings.enrichment_db_path_maxmind_asn,
            maxmind_city=settings.enrichment_db_path_maxmind_city,
            maxmind_country=settings.enrichment_db_path_maxmind_country,
            ip2location=settings.enrichment_db_path_ip2location,
            ip2proxy=settings.enrichment_db_path_ip2proxy,
        )
    else:
        logger.info(
            "ip_enrichment_config_valid",
            message="IP enrichment is enabled and at least one database is available"
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    validate_enrichment_config()
    yield
    # Shutdown (if needed in future)


# Create FastAPI app with custom JSON encoder and lifespan
app = FastAPI(
    title="Dyn365Hunter MVP",
    description="Lead intelligence engine for domain-based analysis",
    version="1.0.0",
    default_response_class=UTF8JSONResponse,
    lifespan=lifespan,
)

# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

# Health and auth routers (no versioning - infrastructure endpoints)
app.include_router(health.router)
app.include_router(auth.router)  # G19: Microsoft SSO
app.include_router(debug.router)  # Debug endpoints (internal/admin use)

# API v1 routers (versioned API)
# Note: v1 routers already have their own prefixes defined in their files
v1_router = APIRouter(prefix="/api/v1", tags=["v1"])
v1_router.include_router(ingest_v1.router)  # Already has /ingest prefix
v1_router.include_router(scan_v1.router)  # Already has /scan prefix
v1_router.include_router(leads_v1.router)  # Already has /leads prefix
v1_router.include_router(dashboard_v1.router)  # Already has /dashboard prefix
v1_router.include_router(email_tools_v1.router)  # Already has /email prefix
v1_router.include_router(progress_v1.router)  # Already has /jobs prefix
v1_router.include_router(admin_v1.router)  # Already has /admin prefix
v1_router.include_router(notes_v1.router)  # Already has /leads prefix
v1_router.include_router(tags_v1.router)  # Already has /leads prefix
v1_router.include_router(favorites_v1.router)  # Already has /leads prefix
v1_router.include_router(pdf_v1.router)  # Already has /leads prefix
v1_router.include_router(rescan_v1.router)  # Already has /scan prefix
v1_router.include_router(alerts_v1.router)  # Already has /alerts prefix
v1_router.include_router(sales_summary_v1.router)  # Already has /leads prefix
app.include_router(v1_router)

# Legacy routers (backward compatibility - will be deprecated in future)
# Note: Legacy routers already have their own prefixes defined in their files
app.include_router(ingest.router, tags=["ingest", "legacy"])  # Already has /ingest prefix
app.include_router(scan.router, tags=["scan", "legacy"])  # Already has /scan prefix
app.include_router(leads.router, tags=["leads", "legacy"])  # Already has /leads prefix
app.include_router(dashboard.router, tags=["dashboard", "legacy"])  # Already has /dashboard prefix
app.include_router(email_tools.router, tags=["email", "legacy"])  # Already has /email prefix
app.include_router(progress.router, tags=["progress", "legacy"])  # Already has /jobs prefix
app.include_router(admin.router, tags=["admin", "legacy"])  # Already has /admin prefix
app.include_router(notes.router, tags=["notes", "legacy"])  # Already has /notes prefix
app.include_router(tags.router, tags=["tags", "legacy"])  # Already has /leads prefix
app.include_router(favorites.router, tags=["favorites", "legacy"])  # Already has /leads prefix
app.include_router(pdf.router, tags=["pdf", "legacy"])  # Already has /leads prefix
app.include_router(rescan.router, tags=["rescan", "legacy"])  # Already has /scan prefix
app.include_router(alerts.router, tags=["alerts", "legacy"])  # Already has /alerts prefix
app.include_router(sales_summary.router, tags=["sales", "legacy"])  # Already has /leads prefix

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


@app.get("/support")
async def support():
    """Support information endpoint."""
    return {
        "message": "Dyn365Hunter MVP Support",
        "documentation": "/docs",
        "api_version": "1.0.0",
        "contact": "For support, please refer to the API documentation at /docs"
    }