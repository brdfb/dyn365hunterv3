"""API v1 routers - Versioned API endpoints."""

from app.api.v1 import (
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
)

__all__ = [
    "ingest",
    "scan",
    "leads",
    "dashboard",
    "email_tools",
    "progress",
    "admin",
    "notes",
    "tags",
    "favorites",
    "pdf",
    "rescan",
    "alerts",
]

