"""Notes endpoints for domain notes (G17: CRM-lite).

⚠️ DEPRECATED: Write endpoints (POST, PUT, DELETE) are deprecated as of 2025-11-16.
Read endpoint (GET) remains available for migration support.
Notes will be managed in Dynamics 365 in the future.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.db.session import get_db
from app.db.models import Note, Company
from app.core.normalizer import normalize_domain
from app.core.deprecation import deprecated_endpoint


router = APIRouter(prefix="/leads", tags=["notes"])


class NoteCreate(BaseModel):
    """Request model for creating a note."""

    note: str = Field(..., description="Note content", min_length=1)


class NoteUpdate(BaseModel):
    """Request model for updating a note."""

    note: str = Field(..., description="Note content", min_length=1)


class NoteResponse(BaseModel):
    """Response model for a note."""

    id: int
    domain: str
    note: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.post("/{domain}/notes", response_model=NoteResponse, status_code=201)
@deprecated_endpoint(
    reason="Notes are now managed in Dynamics 365. This endpoint will be removed in Phase 6.",
    alternative="Use Dynamics 365 Timeline/Notes API for note management.",
)
async def create_note(domain: str, request: NoteCreate, db: Session = Depends(get_db)):
    """
    Create a note for a domain.

    Args:
        domain: Domain name (will be normalized)
        request: Note creation request
        db: Database session

    Returns:
        NoteResponse with created note

    Raises:
        404: If domain not found
        400: If domain is invalid
    """
    # Normalize domain
    normalized_domain = normalize_domain(domain)

    if not normalized_domain:
        raise HTTPException(status_code=400, detail="Invalid domain format")

    # Check if domain exists
    company = db.query(Company).filter(Company.domain == normalized_domain).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Domain {normalized_domain} not found. Please ingest the domain first using /ingest/domain",
        )

    # Create note
    note = Note(domain=normalized_domain, note=request.note)
    db.add(note)
    db.commit()
    db.refresh(note)

    return NoteResponse(
        id=note.id,
        domain=note.domain,
        note=note.note,
        created_at=note.created_at.isoformat(),
        updated_at=note.updated_at.isoformat(),
    )


@router.get("/{domain}/notes", response_model=List[NoteResponse])
async def list_notes(domain: str, db: Session = Depends(get_db)):
    """
    List all notes for a domain.

    Args:
        domain: Domain name (will be normalized)
        db: Database session

    Returns:
        List of NoteResponse objects

    Raises:
        404: If domain not found
        400: If domain is invalid
    """
    # Normalize domain
    normalized_domain = normalize_domain(domain)

    if not normalized_domain:
        raise HTTPException(status_code=400, detail="Invalid domain format")

    # Check if domain exists
    company = db.query(Company).filter(Company.domain == normalized_domain).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Domain {normalized_domain} not found. Please ingest the domain first using /ingest/domain",
        )

    # Get notes
    notes = (
        db.query(Note)
        .filter(Note.domain == normalized_domain)
        .order_by(Note.created_at.desc())
        .all()
    )

    return [
        NoteResponse(
            id=note.id,
            domain=note.domain,
            note=note.note,
            created_at=note.created_at.isoformat(),
            updated_at=note.updated_at.isoformat(),
        )
        for note in notes
    ]


@router.put("/{domain}/notes/{note_id}", response_model=NoteResponse)
@deprecated_endpoint(
    reason="Notes are now managed in Dynamics 365. This endpoint will be removed in Phase 6.",
    alternative="Use Dynamics 365 Timeline/Notes API for note management.",
)
async def update_note(
    domain: str, note_id: int, request: NoteUpdate, db: Session = Depends(get_db)
):
    """
    Update a note.

    Args:
        domain: Domain name (will be normalized)
        note_id: Note ID
        request: Note update request
        db: Database session

    Returns:
        NoteResponse with updated note

    Raises:
        404: If domain or note not found
        400: If domain is invalid
    """
    # Normalize domain
    normalized_domain = normalize_domain(domain)

    if not normalized_domain:
        raise HTTPException(status_code=400, detail="Invalid domain format")

    # Get note
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.domain == normalized_domain)
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail=f"Note {note_id} not found for domain {normalized_domain}",
        )

    # Update note
    note.note = request.note
    db.commit()
    db.refresh(note)

    return NoteResponse(
        id=note.id,
        domain=note.domain,
        note=note.note,
        created_at=note.created_at.isoformat(),
        updated_at=note.updated_at.isoformat(),
    )


@router.delete("/{domain}/notes/{note_id}", status_code=204)
@deprecated_endpoint(
    reason="Notes are now managed in Dynamics 365. This endpoint will be removed in Phase 6.",
    alternative="Use Dynamics 365 Timeline/Notes API for note management.",
)
async def delete_note(domain: str, note_id: int, db: Session = Depends(get_db)):
    """
    Delete a note.

    Args:
        domain: Domain name (will be normalized)
        note_id: Note ID
        db: Database session

    Raises:
        404: If domain or note not found
        400: If domain is invalid
    """
    # Normalize domain
    normalized_domain = normalize_domain(domain)

    if not normalized_domain:
        raise HTTPException(status_code=400, detail="Invalid domain format")

    # Get note
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.domain == normalized_domain)
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=404,
            detail=f"Note {note_id} not found for domain {normalized_domain}",
        )

    # Delete note
    db.delete(note)
    db.commit()

    return None
