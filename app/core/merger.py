"""Company data merger utilities for upserting company records."""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.models import Company, RawLead
from app.core.normalizer import normalize_domain


def upsert_companies(
    db: Session,
    domain: str,
    company_name: Optional[str] = None,
    provider: Optional[str] = None,
    country: Optional[str] = None
) -> Company:
    """
    Upsert a company record based on domain (unique key).
    
    If company with domain exists, update it.
    If not, create a new company record.
    
    Args:
        db: SQLAlchemy database session
        domain: Normalized domain string (must be unique)
        company_name: Company name (optional, used for canonical_name)
        provider: Provider name (optional, e.g., "M365", "Google")
        country: ISO 3166-1 alpha-2 country code (optional)
        
    Returns:
        Company model instance (existing or newly created)
        
    Raises:
        ValueError: If domain is empty or invalid after normalization
        IntegrityError: If domain normalization fails or constraint violation
    """
    # Normalize domain
    normalized_domain = normalize_domain(domain)
    
    if not normalized_domain:
        raise ValueError(f"Invalid domain: {domain}")
    
    # Try to find existing company
    company = db.query(Company).filter(Company.domain == normalized_domain).first()
    
    if company:
        # Update existing company
        if company_name:
            company.canonical_name = company_name
        if provider is not None:
            company.provider = provider
        if country is not None:
            company.country = country
        # updated_at is automatically updated via onupdate
    else:
        # Create new company
        # Use company_name if provided, otherwise use domain as canonical_name
        canonical_name = company_name if company_name else normalized_domain
        
        company = Company(
            domain=normalized_domain,
            canonical_name=canonical_name,
            provider=provider,
            country=country
        )
        db.add(company)
    
    try:
        db.commit()
        db.refresh(company)
        return company
    except IntegrityError as e:
        db.rollback()
        # If we get an integrity error, it might be a race condition
        # Try to fetch the existing record
        company = db.query(Company).filter(Company.domain == normalized_domain).first()
        if company:
            # Update it
            if company_name:
                company.canonical_name = company_name
            if provider is not None:
                company.provider = provider
            if country is not None:
                company.country = country
            db.commit()
            db.refresh(company)
            return company
        else:
            # Re-raise if we can't recover
            raise

