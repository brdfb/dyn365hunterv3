"""Admin endpoints for API key management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field
from app.db.session import get_db
from app.db.models import ApiKey
from app.core.api_key_auth import hash_api_key, generate_api_key

router = APIRouter(prefix="/admin", tags=["admin"])


class CreateApiKeyRequest(BaseModel):
    """Request model for creating an API key."""
    name: str = Field(..., description="Human-readable name for the API key")
    rate_limit_per_minute: int = Field(60, ge=1, le=10000, description="Rate limit per minute (1-10000)")
    created_by: Optional[str] = Field(None, description="Who created the key (admin user)")


class ApiKeyResponse(BaseModel):
    """Response model for API key creation."""
    id: int
    name: str
    api_key: str  # Only shown once on creation
    key_hash: str
    rate_limit_per_minute: int
    is_active: bool
    created_at: str
    created_by: Optional[str]
    message: str


class ApiKeyListResponse(BaseModel):
    """Response model for listing API keys."""
    id: int
    name: str
    rate_limit_per_minute: int
    is_active: bool
    created_at: str
    last_used_at: Optional[str]
    created_by: Optional[str]


@router.post("/api-keys", response_model=ApiKeyResponse, status_code=201)
async def create_api_key(
    request: CreateApiKeyRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new API key for webhook authentication.
    
    **WARNING**: The API key is only shown once in the response. Store it securely.
    
    Args:
        request: API key creation request
        db: Database session
        
    Returns:
        ApiKeyResponse with the generated API key (shown only once)
        
    Raises:
        400: If name is empty or invalid
        500: If internal server error
    """
    try:
        # Generate API key
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)
        
        # Check if hash already exists (extremely unlikely, but check anyway)
        existing = db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()
        if existing:
            # Regenerate if collision (extremely unlikely)
            api_key = generate_api_key()
            key_hash = hash_api_key(api_key)
        
        # Create API key record
        api_key_record = ApiKey(
            key_hash=key_hash,
            name=request.name,
            rate_limit_per_minute=request.rate_limit_per_minute,
            is_active=True,
            created_by=request.created_by
        )
        db.add(api_key_record)
        db.commit()
        db.refresh(api_key_record)
        
        return ApiKeyResponse(
            id=api_key_record.id,
            name=api_key_record.name,
            api_key=api_key,  # Only shown once!
            key_hash=api_key_record.key_hash,
            rate_limit_per_minute=api_key_record.rate_limit_per_minute,
            is_active=api_key_record.is_active,
            created_at=api_key_record.created_at.isoformat(),
            created_by=api_key_record.created_by,
            message="API key created successfully. Store it securely - it will not be shown again."
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/api-keys", response_model=List[ApiKeyListResponse])
async def list_api_keys(
    db: Session = Depends(get_db)
):
    """
    List all API keys (without showing the actual keys).
    
    Args:
        db: Database session
        
    Returns:
        List of API key information (without actual keys)
    """
    try:
        api_keys = db.query(ApiKey).order_by(ApiKey.created_at.desc()).all()
        
        return [
            ApiKeyListResponse(
                id=key.id,
                name=key.name,
                rate_limit_per_minute=key.rate_limit_per_minute,
                is_active=key.is_active,
                created_at=key.created_at.isoformat(),
                last_used_at=key.last_used_at.isoformat() if key.last_used_at else None,
                created_by=key.created_by
            )
            for key in api_keys
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/api-keys/{key_id}/deactivate")
async def deactivate_api_key(
    key_id: int,
    db: Session = Depends(get_db)
):
    """
    Deactivate an API key.
    
    Args:
        key_id: API key ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        404: If API key not found
    """
    api_key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    api_key.is_active = False
    db.commit()
    
    return {"message": f"API key '{api_key.name}' deactivated successfully"}


@router.patch("/api-keys/{key_id}/activate")
async def activate_api_key(
    key_id: int,
    db: Session = Depends(get_db)
):
    """
    Activate an API key.
    
    Args:
        key_id: API key ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        404: If API key not found
    """
    api_key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    api_key.is_active = True
    db.commit()
    
    return {"message": f"API key '{api_key.name}' activated successfully"}

