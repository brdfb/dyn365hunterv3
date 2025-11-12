"""Ingest endpoints for domain and CSV data ingestion."""
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from app.db.session import get_db
from app.db.models import RawLead
from app.core.normalizer import (
    normalize_domain,
    extract_domain_from_email,
    extract_domain_from_website
)
from app.core.merger import upsert_companies


router = APIRouter(prefix="/ingest", tags=["ingest"])


class DomainIngestRequest(BaseModel):
    """Request model for single domain ingestion."""
    domain: str = Field(..., description="Domain name (will be normalized)")
    company_name: Optional[str] = Field(None, description="Company name (optional)")
    email: Optional[str] = Field(None, description="Email address (optional)")
    website: Optional[str] = Field(None, description="Website URL (optional)")
    
    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Validate and normalize domain."""
        normalized = normalize_domain(v)
        if not normalized:
            raise ValueError("Invalid domain format")
        return normalized


class DomainIngestResponse(BaseModel):
    """Response model for domain ingestion."""
    domain: str
    company_id: int
    message: str


@router.post("/domain", response_model=DomainIngestResponse, status_code=201)
async def ingest_domain(
    request: DomainIngestRequest,
    db: Session = Depends(get_db)
):
    """
    Ingest a single domain.
    
    - Normalizes the domain
    - Extracts domain from email/website if provided
    - Creates/updates company record
    - Creates raw_lead record
    
    Args:
        request: Domain ingestion request
        db: Database session
        
    Returns:
        DomainIngestResponse with domain and company_id
    """
    # Determine the final domain to use
    final_domain = request.domain
    
    # If email is provided, try to extract domain from it
    if request.email:
        email_domain = extract_domain_from_email(request.email)
        if email_domain:
            final_domain = email_domain
    
    # If website is provided, try to extract domain from it
    if request.website:
        website_domain = extract_domain_from_website(request.website)
        if website_domain:
            final_domain = website_domain
    
    # Normalize the final domain
    final_domain = normalize_domain(final_domain)
    
    if not final_domain:
        raise HTTPException(
            status_code=400,
            detail="Could not determine valid domain from provided inputs"
        )
    
    try:
        # Upsert company
        company = upsert_companies(
            db=db,
            domain=final_domain,
            company_name=request.company_name
        )
        
        # Create raw_lead record
        raw_lead = RawLead(
            source="domain",
            company_name=request.company_name,
            email=request.email,
            website=request.website,
            domain=final_domain,
            payload={
                "original_domain": request.domain,
                "email": request.email,
                "website": request.website
            }
        )
        db.add(raw_lead)
        db.commit()
        db.refresh(raw_lead)
        
        return DomainIngestResponse(
            domain=final_domain,
            company_id=company.id,
            message=f"Domain {final_domain} ingested successfully"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/csv", status_code=201)
async def ingest_csv(
    file: UploadFile = File(..., description="CSV file to ingest"),
    db: Session = Depends(get_db)
):
    """
    Ingest domains from a CSV file.
    
    Expected CSV columns:
    - domain (required): Domain name
    - company_name (optional): Company name
    - email (optional): Email address
    - website (optional): Website URL
    
    Args:
        file: CSV file upload
        db: Database session
        
    Returns:
        Dictionary with ingestion results
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(contents))
        
        # Validate required columns
        if 'domain' not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="CSV must contain a 'domain' column"
            )
        
        # Normalize column names (case-insensitive)
        df.columns = df.columns.str.lower().str.strip()
        
        # Process each row
        ingested_count = 0
        errors: List[str] = []
        
        for idx, row in df.iterrows():
            try:
                # Get domain (required)
                domain = str(row.get('domain', '')).strip()
                if not domain:
                    errors.append(f"Row {idx + 1}: Empty domain")
                    continue
                
                # Normalize domain
                normalized_domain = normalize_domain(domain)
                if not normalized_domain:
                    errors.append(f"Row {idx + 1}: Invalid domain '{domain}'")
                    continue
                
                # Get optional fields
                company_name = str(row.get('company_name', '')).strip() or None
                email = str(row.get('email', '')).strip() or None
                website = str(row.get('website', '')).strip() or None
                
                # Determine final domain (from email/website if provided)
                final_domain = normalized_domain
                
                if email:
                    email_domain = extract_domain_from_email(email)
                    if email_domain:
                        final_domain = email_domain
                
                if website:
                    website_domain = extract_domain_from_website(website)
                    if website_domain:
                        final_domain = website_domain
                
                final_domain = normalize_domain(final_domain)
                
                # Upsert company
                company = upsert_companies(
                    db=db,
                    domain=final_domain,
                    company_name=company_name
                )
                
                # Create raw_lead record
                raw_lead = RawLead(
                    source="csv",
                    company_name=company_name,
                    email=email,
                    website=website,
                    domain=final_domain,
                    payload={
                        "original_domain": domain,
                        "row_index": int(idx),
                        "email": email,
                        "website": website
                    }
                )
                db.add(raw_lead)
                ingested_count += 1
                
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")
                continue
        
        # Commit all successful ingestions
        db.commit()
        
        return {
            "message": f"CSV ingestion completed",
            "ingested": ingested_count,
            "total_rows": len(df),
            "errors": errors if errors else None
        }
    
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

