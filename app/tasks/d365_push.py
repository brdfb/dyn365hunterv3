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
from app.core.d365_metrics import track_push_success, track_push_failed
from app.core.retry_utils import compute_backoff_with_jitter
from app.core.priority import calculate_priority_score
from app.core.enrichment_service import build_infra_summary


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
    import time
    start_time = time.time()
    
    if not settings.d365_enabled:
        logger.warning(
            "d365_disabled",
            message="D365 integration is disabled",
            lead_id=lead_id
        )
        return {"status": "skipped", "reason": "d365_disabled"}
    
    # Use context manager for DB session to prevent leaks
    with SessionLocal() as db:
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
            
            # Idempotency check: If lead already exists in D365, skip
            if company.d365_lead_id:
                try:
                    client = D365Client()
                    existing_lead = asyncio.run(client._find_lead_by_id(company.d365_lead_id))
                    if existing_lead and existing_lead.get("leadid"):
                        logger.info(
                            "d365_lead_already_exists",
                            message="Lead already exists in D365, skipping push",
                            lead_id=lead_id,
                            d365_lead_id=company.d365_lead_id,
                            domain=domain
                        )
                        # Update sync status if needed
                        if company.d365_sync_status != "synced":
                            company.d365_sync_status = "synced"
                            company.d365_sync_error = None
                            db.commit()
                        
                        return {
                            "status": "skipped",
                            "reason": "already_exists",
                            "d365_lead_id": company.d365_lead_id,
                            "domain": domain
                        }
                except D365RateLimitError:
                    # Rate limit on verification - continue with push (will retry)
                    logger.warning(
                        "d365_lead_verification_rate_limit",
                        message="Rate limit during lead verification, proceeding with push",
                        lead_id=lead_id,
                        d365_lead_id=company.d365_lead_id
                    )
                except Exception as e:
                    # Verification failed - continue with push (will handle error later)
                    logger.warning(
                        "d365_lead_verification_failed",
                        message="Failed to verify existing lead, proceeding with push",
                        lead_id=lead_id,
                        d365_lead_id=company.d365_lead_id,
                    error=str(e)
                )
            
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
                c.d365_sync_last_at,
                c.d365_sync_error,
                c.d365_sync_attempt_count,
                pcr.referral_id,
                pcr.azure_tenant_id,
                pcr.referral_type
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
            
            # Calculate priority score (P0-1: Priority Score mapping)
            priority_score = calculate_priority_score(row.segment, row.readiness_score)
            
            # Build infrastructure summary (IP enrichment)
            infrastructure_summary = build_infra_summary(row.domain, db)
            
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
            "priority_score": priority_score,  # P0-1: Priority Score (1-7)
            "infrastructure_summary": infrastructure_summary,  # IP enrichment summary
            "technical_heat": row.technical_heat,
            "commercial_segment": row.commercial_segment,
            "commercial_heat": row.commercial_heat,
            "priority_category": row.priority_category,
            "priority_label": row.priority_label,
            "d365_sync_last_at": row.d365_sync_last_at if hasattr(row, "d365_sync_last_at") else None,
            "d365_sync_error": row.d365_sync_error if hasattr(row, "d365_sync_error") else None,
            "d365_sync_attempt_count": row.d365_sync_attempt_count if hasattr(row, "d365_sync_attempt_count") else None,
            "d365_sync_status": row.d365_sync_status if hasattr(row, "d365_sync_status") else None,
            "referral_id": row.referral_id if hasattr(row, "referral_id") else None,
            "azure_tenant_id": row.azure_tenant_id if hasattr(row, "azure_tenant_id") else None,  # P1-4: Partner Center enriched
            "referral_type": row.referral_type if hasattr(row, "referral_type") else None,  # P1-4: Partner Center enriched
            }
            
            # P0-3: Increment sync attempt count
            company.d365_sync_attempt_count = (company.d365_sync_attempt_count or 0) + 1
            
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
            sync_last_at = datetime.now()
            company.d365_sync_last_at = sync_last_at
            company.d365_sync_error = None
            db.commit()
            
            # Update D365 lead with post-push fields (hnt_d365leadid, hnt_lastsynctime)
            # These fields are set after push to maintain sync state in D365
            try:
                post_push_fields = {
                    "hnt_d365leadid": d365_lead_id,  # Self-reference: D365 Lead ID in D365
                    "hnt_lastsynctime": sync_last_at.isoformat(),  # Last sync timestamp
                }
                asyncio.run(client.update_lead_fields(d365_lead_id, post_push_fields))
                logger.debug(
                    "d365_post_push_update",
                    message="Post-push fields updated in D365",
                    lead_id=lead_id,
                    d365_lead_id=d365_lead_id
                )
            except Exception as e:
                # Non-critical: Post-push update failed, but push was successful
                logger.warning(
                    "d365_post_push_update_failed",
                    message="Post-push fields update failed (non-critical)",
                    lead_id=lead_id,
                    d365_lead_id=d365_lead_id,
                    error=str(e)
                )
                # Continue - push was successful, post-push update is optional
            
            # Phase 3: Track success metrics
            duration = time.time() - start_time
            track_push_success(duration)
            
            logger.info(
                "d365_push_success",
                message="Lead pushed to D365 successfully",
                lead_id=lead_id,
                domain=domain,
                d365_lead_id=d365_lead_id,
                duration=duration
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
            
            # Retry with exponential backoff + jitter + cap
            backoff = compute_backoff_with_jitter(
                base_seconds=60,
                attempt=self.request.retries,
                max_seconds=3600
            )
            raise self.retry(exc=e, countdown=backoff)
        
        except (D365AuthenticationError, D365APIError, D365DuplicateError) as e:
            # Non-retryable errors
            # Phase 3: Track failure metrics
            track_push_failed()
            
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
            # Phase 3: Track failure metrics (only on final failure, not retries)
            if self.request.retries >= self.max_retries:
                track_push_failed()
            
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
                # Retry with exponential backoff + jitter + cap
                backoff = compute_backoff_with_jitter(
                    base_seconds=60,
                    attempt=self.request.retries,
                    max_seconds=3600
                )
                raise self.retry(exc=e, countdown=backoff)
            else:
                raise
            # Context manager automatically closes session

