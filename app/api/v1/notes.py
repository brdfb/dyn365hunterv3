"""API v1 notes endpoints - Proxy to legacy handlers."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.api.notes import (
    create_note,
    list_notes,
    update_note,
    delete_note,
    NoteCreate,
    NoteUpdate,
    NoteResponse,
)
from app.db.session import get_db

router = APIRouter(prefix="/leads", tags=["notes", "v1"])


@router.post("/{domain}/notes", status_code=410)
async def create_note_v1(
    domain: str, request: NoteCreate, db: Session = Depends(get_db)
):
    """
    V1 endpoint - Create a note for a domain.
    
    ⚠️ DEPRECATED: This endpoint is disabled (410 Gone) as of Phase 3.
    Notes are now managed in Dynamics 365.
    """
    return await create_note(domain=domain, request=request, db=db)


@router.get("/{domain}/notes", response_model=List[NoteResponse])
async def list_notes_v1(domain: str, db: Session = Depends(get_db)):
    """V1 endpoint - List all notes for a domain."""
    return await list_notes(domain=domain, db=db)


@router.put("/{domain}/notes/{note_id}", status_code=410)
async def update_note_v1(
    domain: str, note_id: int, request: NoteUpdate, db: Session = Depends(get_db)
):
    """
    V1 endpoint - Update a note.
    
    ⚠️ DEPRECATED: This endpoint is disabled (410 Gone) as of Phase 3.
    Notes are now managed in Dynamics 365.
    """
    return await update_note(domain=domain, note_id=note_id, request=request, db=db)


@router.delete("/{domain}/notes/{note_id}", status_code=410)
async def delete_note_v1(domain: str, note_id: int, db: Session = Depends(get_db)):
    """
    V1 endpoint - Delete a note.
    
    ⚠️ DEPRECATED: This endpoint is disabled (410 Gone) as of Phase 3.
    Notes are now managed in Dynamics 365.
    """
    return await delete_note(domain=domain, note_id=note_id, db=db)

