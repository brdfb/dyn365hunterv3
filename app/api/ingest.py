"""Ingest endpoints for domain and CSV data ingestion."""
import pandas as pd
import asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
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
from app.core.importer import guess_company_column, guess_domain_column
from app.core.analyzer_dns import analyze_dns
from app.core.analyzer_whois import get_whois_info
from app.core.provider_map import classify_provider
from app.core.scorer import score_domain
from app.db.models import Company, DomainSignal, LeadScore, ProviderChangeHistory
from app.api.jobs import create_job, update_job_progress, start_job, complete_job, JobStatus


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


@router.post("/csv", status_code=202)
async def ingest_csv(
    file: UploadFile = File(..., description="CSV or Excel file to ingest"),
    auto_detect_columns: bool = Query(False, description="Auto-detect company/domain columns (for OSB Excel files)"),
    auto_scan: bool = Query(True, description="Automatically scan domains after ingestion (creates leads)"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Ingest domains from a CSV or Excel file.
    
    Supported formats:
    - CSV (.csv)
    - Excel (.xlsx, .xls)
    
    Expected columns (when auto_detect_columns=False):
    - domain (required): Domain name
    - company_name (optional): Company name
    - email (optional): Email address
    - website (optional): Website URL
    
    When auto_detect_columns=True:
    - Automatically detects company and domain columns using heuristics
    - Useful for OSB Excel files with varying column names
    
    Args:
        file: CSV or Excel file upload
        auto_detect_columns: If True, auto-detect company/domain columns
        db: Database session
        
    Returns:
        Dictionary with ingestion results
    """
    # Validate file type
    filename_lower = file.filename.lower() if file.filename else ""
    is_excel = filename_lower.endswith(('.xlsx', '.xls'))
    is_csv = filename_lower.endswith('.csv')
    
    if not (is_csv or is_excel):
        raise HTTPException(
            status_code=400,
            detail="File must be CSV (.csv) or Excel (.xlsx, .xls)"
        )
    
    try:
        # Read file
        contents = await file.read()
        
        if is_excel:
            df = pd.read_excel(pd.io.common.BytesIO(contents))
        else:
            df = pd.read_csv(pd.io.common.BytesIO(contents))
        
        # Column detection (if auto_detect_columns=True)
        if auto_detect_columns:
            company_col = guess_company_column(df)
            domain_col = guess_domain_column(df)
            
            if not company_col or not domain_col:
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not detect columns. Company: {company_col}, Domain: {domain_col}. "
                           f"Available columns: {list(df.columns)}"
                )
            
            # Rename columns to standard names for processing
            df = df.rename(columns={company_col: 'company_name', domain_col: 'domain'})
        
        # Normalize column names (case-insensitive)
        df.columns = df.columns.str.lower().str.strip()
        
        # Validate required columns
        if 'domain' not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="CSV must contain a 'domain' column (or use auto_detect_columns=true)"
            )
        
        # Create job for progress tracking
        total_domains = len(df) + (len(df) if auto_scan else 0)  # Ingest + scan
        job_id = create_job(total_domains, "CSV ingestion and scanning")
        start_job(job_id)
        
        # Process each row
        ingested_count = 0
        scanned_count = 0
        errors: List[str] = []
        scanned_domains: List[str] = []
        
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
                    errors.append(f"Row {idx + 1}: Invalid domain format '{domain}' (geçersiz domain formatı)")
                    continue
                
                # Additional validation: check if normalized domain is still valid
                from app.core.normalizer import is_valid_domain
                if not is_valid_domain(normalized_domain):
                    errors.append(f"Row {idx + 1}: Invalid domain after normalization '{normalized_domain}' (normalizasyon sonrası geçersiz)")
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
                scanned_domains.append(final_domain)
                
                # Update progress
                update_job_progress(
                    job_id,
                    processed=ingested_count,
                    successful=ingested_count,
                    message=f"İşleniyor: {ingested_count}/{len(df)} domain yüklendi"
                )
                
            except Exception as e:
                error_msg = f"Row {idx + 1}: {str(e)}"
                errors.append(error_msg)
                update_job_progress(
                    job_id,
                    processed=ingested_count + len(errors),
                    failed=len(errors),
                    error=error_msg
                )
                continue
        
        # Commit all successful ingestions
        db.commit()
        update_job_progress(
            job_id,
            processed=ingested_count,
            message=f"Yükleme tamamlandı: {ingested_count} domain. Scan başlıyor..."
        )
        
        # Auto-scan domains if requested
        if auto_scan and scanned_domains:
            scan_index = 0
            for domain in scanned_domains:
                scan_index += 1
                try:
                    # Perform DNS analysis
                    dns_result = analyze_dns(domain)
                    
                    # Perform WHOIS lookup (optional, graceful fail)
                    whois_result = get_whois_info(domain)
                    
                    # Determine scan status
                    scan_status = dns_result.get("status", "success")
                    if scan_status == "success" and whois_result is None:
                        scan_status = "whois_failed"
                    
                    # Classify provider based on MX root
                    mx_root = dns_result.get("mx_root")
                    provider = classify_provider(mx_root)
                    
                    # Update company provider if we have new information
                    company = db.query(Company).filter(Company.domain == domain).first()
                    previous_provider = company.provider if company else None
                    provider_changed = False
                    
                    if company and provider and provider != "Unknown":
                        if previous_provider != provider:
                            provider_changed = True
                        company.provider = provider
                    
                    # Prepare signals for scoring
                    signals = {
                        "spf": dns_result.get("spf", False),
                        "dkim": dns_result.get("dkim", False),
                        "dmarc_policy": dns_result.get("dmarc_policy")
                    }
                    
                    # Calculate score and determine segment
                    scoring_result = score_domain(
                        domain=domain,
                        provider=provider,
                        signals=signals,
                        mx_records=dns_result.get("mx_records", [])
                    )
                    
                    # Delete any existing domain_signals for this domain (prevent duplicates)
                    db.query(DomainSignal).filter(DomainSignal.domain == domain).delete()
                    
                    # Create new domain_signal
                    domain_signal = DomainSignal(
                        domain=domain,
                        spf=dns_result.get("spf", False),
                        dkim=dns_result.get("dkim", False),
                        dmarc_policy=dns_result.get("dmarc_policy"),
                        mx_root=mx_root,
                        registrar=whois_result.get("registrar") if whois_result else None,
                        expires_at=whois_result.get("expires_at") if whois_result else None,
                        nameservers=whois_result.get("nameservers") if whois_result else None,
                        scan_status=scan_status
                    )
                    db.add(domain_signal)
                    
                    # Delete any existing lead_scores for this domain (prevent duplicates)
                    db.query(LeadScore).filter(LeadScore.domain == domain).delete()
                    
                    # Create new lead_score
                    lead_score = LeadScore(
                        domain=domain,
                        readiness_score=scoring_result["score"],
                        segment=scoring_result["segment"],
                        reason=scoring_result["reason"]
                    )
                    db.add(lead_score)
                    
                    # Log provider change if detected
                    if provider_changed and previous_provider:
                        change_history = ProviderChangeHistory(
                            domain=domain,
                            previous_provider=previous_provider,
                            new_provider=provider
                        )
                        db.add(change_history)
                    
                    scanned_count += 1
                    
                    # Update progress
                    total_processed = ingested_count + scan_index
                    update_job_progress(
                        job_id,
                        processed=total_processed,
                        successful=ingested_count + scanned_count,
                        message=f"Taranıyor: {scan_index}/{len(scanned_domains)} domain scan edildi"
                    )
                    
                except Exception as e:
                    error_msg = f"Scan error for {domain}: {str(e)}"
                    errors.append(error_msg)
                    total_processed = ingested_count + scan_index
                    update_job_progress(
                        job_id,
                        processed=total_processed,
                        failed=len(errors),
                        error=error_msg
                    )
                    continue
            
            # Commit all scan results
            db.commit()
        
        # Complete job
        complete_job(job_id, success=True)
        update_job_progress(
            job_id,
            message=f"Tamamlandı! {ingested_count} domain yüklendi, {scanned_count} domain scan edildi."
        )
        
        return {
            "job_id": job_id,
            "message": f"CSV ingestion completed",
            "ingested": ingested_count,
            "scanned": scanned_count if auto_scan else 0,
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

