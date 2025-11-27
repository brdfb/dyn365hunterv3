"""Celery task for pushing leads to Dynamics 365."""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.celery_app import celery_app
from app.core.logging import logger
from app.config import settings
from app.db.session import SessionLocal
from app.db.models import Company
from app.integrations.d365.client import D365Client
from app.integrations.d365.mapping import map_lead_to_d365
from app.integrations.d365.errors import (
    D365Error,
    D365AuthenticationError,
    D365APIError,
    D365RateLimitError,
    D365DuplicateError,
)


@celery_app.task(bind=True, name="push_lead_to_d365", max_retries=3)
def push_lead_to_d365(self, lead_id: int):
    """
    Push a lead to Dynamics 365.
    
    Flow:
    1. Query lead data from leads_ready view (by company_id or domain)
    2. Map Hunter lead to D365 Lead payload
    3. Call D365 client to create/update lead
    4. Update company record with D365 status and lead ID
    
    Args:
        lead_id: Company ID (from companies table)
        
    Returns:
        Dict with status and D365 lead ID if successful
    """
    if not settings.d365_enabled:
        logger.warning(
            "d365_disabled",
            message="D365 integration is disabled",
            lead_id=lead_id
        )
        return {"status": "skipped", "reason": "d365_disabled"}
    
    db = SessionLocal()
    
    try:
        logger.info(
            "d365_push_started",
            message="D365 push task started",
            lead_id=lead_id
        )
        
        # Get company by ID
        company = db.query(Company).filter(Company.id == lead_id).first()
        if not company:
            logger.error(
                "d365_company_not_found",
                message="Company not found",
                lead_id=lead_id
            )
            return {"status": "error", "error": "Company not found"}
        
        domain = company.domain
        
        # Query lead data from leads_ready view
        # Include D365 fields and Partner Center referral_id
        # Note: D365 fields may not exist if migration not run yet - use dynamic query
        query = """
            SELECT 
                lr.company_id,
                lr.canonical_name,
                lr.domain,
                lr.provider,
                lr.tenant_size,
                lr.country,
                lr.contact_emails,
                lr.readiness_score,
                lr.segment,
                lr.technical_heat,
                lr.commercial_segment,
                lr.commercial_heat,
                lr.priority_category,
                lr.priority_label,
                c.d365_lead_id,
                c.d365_sync_status,
                pcr.referral_id
            FROM leads_ready lr
            LEFT JOIN companies c ON lr.company_id = c.id
            LEFT JOIN partner_center_referrals pcr ON lr.domain = pcr.domain
            WHERE lr.company_id = :company_id
            LIMIT 1
        """
        
        result = db.execute(text(query), {"company_id": lead_id})
        row = result.fetchone()
        
        if not row:
            logger.error(
                "d365_lead_not_found",
                message="Lead not found in leads_ready view",
                lead_id=lead_id,
                domain=domain
            )
            return {"status": "error", "error": "Lead not found"}
        
        # Convert row to dict
        lead_data = {
            "company_id": row.company_id,
            "canonical_name": row.canonical_name,
            "domain": row.domain,
            "provider": row.provider,
            "tenant_size": row.tenant_size,
            "country": row.country,
            "contact_emails": row.contact_emails,
            "readiness_score": row.readiness_score,
            "segment": row.segment,
            "technical_heat": row.technical_heat,
            "commercial_segment": row.commercial_segment,
            "commercial_heat": row.commercial_heat,
            "priority_category": row.priority_category,
            "priority_label": row.priority_label,
            "referral_id": row.referral_id if hasattr(row, "referral_id") else None,
        }
        
        # Update status to in_progress
        company.d365_sync_status = "in_progress"
        company.d365_sync_error = None
        db.commit()
        
        # Map to D365 payload
        d365_payload = map_lead_to_d365(lead_data)
        
        # Call D365 client (async, need to run in event loop)
        client = D365Client()
        d365_result = asyncio.run(client.create_or_update_lead(d365_payload))
        
        # Extract D365 lead ID
        d365_lead_id = d365_result.get("leadid")
        if not d365_lead_id:
            raise D365APIError("D365 response missing leadid")
        
        # Update company with D365 status
        company.d365_lead_id = d365_lead_id
        company.d365_sync_status = "synced"
        company.d365_sync_last_at = datetime.now()
        company.d365_sync_error = None
        db.commit()
        
        logger.info(
            "d365_push_success",
            message="Lead pushed to D365 successfully",
            lead_id=lead_id,
            domain=domain,
            d365_lead_id=d365_lead_id
        )
        
        return {
            "status": "completed",
            "d365_lead_id": d365_lead_id,
            "domain": domain
        }
        
    except D365RateLimitError as e:
        # Rate limit - retry with exponential backoff
        logger.warning(
            "d365_rate_limit",
            message="D365 rate limit exceeded, will retry",
            lead_id=lead_id,
            error=str(e)
        )
        company.d365_sync_status = "error"
        company.d365_sync_error = f"Rate limit: {str(e)}"
        db.commit()
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        
    except (D365AuthenticationError, D365APIError, D365DuplicateError) as e:
        # Non-retryable errors
        logger.error(
            "d365_push_failed",
            message="D365 push failed (non-retryable)",
            lead_id=lead_id,
            error=str(e),
            error_type=type(e).__name__
        )
        company.d365_sync_status = "error"
        company.d365_sync_error = str(e)
        db.commit()
        
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }
        
    except Exception as e:
        logger.error(
            "d365_push_error",
            message="D365 push task failed (unexpected error)",
            lead_id=lead_id,
            error=str(e),
            exc_info=True
        )
        
        # Update status to error
        try:
            company.d365_sync_status = "error"
            company.d365_sync_error = str(e)
            db.commit()
        except:
            pass
        
        # Retry if we haven't exceeded max retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        else:
            raise
    
    finally:
        db.close()

