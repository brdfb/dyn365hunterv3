"""Tags endpoints for domain tags (G17: CRM-lite)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field
from app.db.session import get_db
from app.db.models import Tag, Company
from app.core.normalizer import normalize_domain


router = APIRouter(prefix="/leads", tags=["tags"])


class TagCreate(BaseModel):
    """Request model for creating a tag."""
    tag: str = Field(..., description="Tag name", min_length=1, max_length=100)


class TagResponse(BaseModel):
    """Response model for a tag."""
    id: int
    domain: str
    tag: str
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/{domain}/tags", response_model=TagResponse, status_code=201)
async def create_tag(
    domain: str,
    request: TagCreate,
    db: Session = Depends(get_db)
):
    """
    Add a tag to a domain.
    
    Args:
        domain: Domain name (will be normalized)
        request: Tag creation request
        db: Database session
        
    Returns:
        TagResponse with created tag
        
    Raises:
        404: If domain not found
        400: If domain is invalid or tag already exists
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
            detail=f"Domain {normalized_domain} not found. Please ingest the domain first using /ingest/domain"
        )
    
    # Check if tag already exists
    existing_tag = db.query(Tag).filter(
        Tag.domain == normalized_domain,
        Tag.tag == request.tag
    ).first()
    
    if existing_tag:
        raise HTTPException(
            status_code=400,
            detail=f"Tag '{request.tag}' already exists for domain {normalized_domain}"
        )
    
    # Create tag
    tag = Tag(
        domain=normalized_domain,
        tag=request.tag
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    
    return TagResponse(
        id=tag.id,
        domain=tag.domain,
        tag=tag.tag,
        created_at=tag.created_at.isoformat()
    )


@router.get("/{domain}/tags", response_model=List[TagResponse])
async def list_tags(
    domain: str,
    db: Session = Depends(get_db)
):
    """
    List all tags for a domain.
    
    Args:
        domain: Domain name (will be normalized)
        db: Database session
        
    Returns:
        List of TagResponse objects
        
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
            detail=f"Domain {normalized_domain} not found. Please ingest the domain first using /ingest/domain"
        )
    
    # Get tags
    tags = db.query(Tag).filter(Tag.domain == normalized_domain).order_by(Tag.created_at.desc()).all()
    
    return [
        TagResponse(
            id=tag.id,
            domain=tag.domain,
            tag=tag.tag,
            created_at=tag.created_at.isoformat()
        )
        for tag in tags
    ]


@router.delete("/{domain}/tags/{tag_id}", status_code=204)
async def delete_tag(
    domain: str,
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove a tag from a domain.
    
    Args:
        domain: Domain name (will be normalized)
        tag_id: Tag ID
        db: Database session
        
    Raises:
        404: If domain or tag not found
        400: If domain is invalid
    """
    # Normalize domain
    normalized_domain = normalize_domain(domain)
    
    if not normalized_domain:
        raise HTTPException(status_code=400, detail="Invalid domain format")
    
    # Get tag
    tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.domain == normalized_domain
    ).first()
    
    if not tag:
        raise HTTPException(
            status_code=404,
            detail=f"Tag {tag_id} not found for domain {normalized_domain}"
        )
    
    # Delete tag
    db.delete(tag)
    db.commit()
    
    return None

