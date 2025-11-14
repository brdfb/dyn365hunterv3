"""Celery tasks for async domain scanning."""
import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.core.celery_app import celery_app
from app.core.progress_tracker import get_progress_tracker
from app.core.rate_limiter import wait_for_dns_rate_limit, wait_for_whois_rate_limit
from app.core.normalizer import normalize_domain
from app.core.analyzer_dns import analyze_dns
from app.core.analyzer_whois import get_whois_info
from app.core.provider_map import classify_provider
from app.core.scorer import score_domain
from app.core.auto_tagging import apply_auto_tags
from app.db.session import SessionLocal
from app.db.models import Company, DomainSignal, LeadScore, ProviderChangeHistory

logger = logging.getLogger(__name__)


def scan_single_domain(domain: str, db: Session) -> Dict:
    """
    Scan a single domain (with rate limiting).
    
    This is a helper function that wraps the scan logic with rate limiting.
    It's used by both the sync endpoint and the async task.
    
    Args:
        domain: Domain name to scan
        db: Database session
        
    Returns:
        Dict with scan result or error
    """
    try:
        # Normalize domain
        normalized_domain = normalize_domain(domain)
        if not normalized_domain:
            return {
                "domain": domain,
                "error": "Invalid domain format",
                "success": False
            }
        
        # Check if company exists
        company = db.query(Company).filter(Company.domain == normalized_domain).first()
        if not company:
            return {
                "domain": normalized_domain,
                "error": "Domain not found. Please ingest first.",
                "success": False
            }
        
        # Rate limiting: DNS (10 req/s)
        wait_for_dns_rate_limit()
        
        # Perform DNS analysis
        dns_result = analyze_dns(normalized_domain)
        
        # Rate limiting: WHOIS (5 req/s)
        wait_for_whois_rate_limit()
        
        # Perform WHOIS lookup (optional, graceful fail)
        whois_result = get_whois_info(normalized_domain)
        
        # Determine scan status
        scan_status = dns_result.get("status", "success")
        if scan_status == "success" and whois_result is None:
            scan_status = "whois_failed"
        
        # Classify provider based on MX root
        mx_root = dns_result.get("mx_root")
        provider = classify_provider(mx_root)
        
        # Track provider changes
        previous_provider = company.provider
        provider_changed = False
        
        # Update company provider if we have new information
        if provider and provider != "Unknown":
            if previous_provider != provider:
                provider_changed = True
            company.provider = provider
            db.commit()
        
        # Prepare signals for scoring
        signals = {
            "spf": dns_result.get("spf", False),
            "dkim": dns_result.get("dkim", False),
            "dmarc_policy": dns_result.get("dmarc_policy")
        }
        
        # Calculate score and determine segment
        scoring_result = score_domain(
            domain=normalized_domain,
            provider=provider,
            signals=signals,
            mx_records=dns_result.get("mx_records", [])
        )
        
        # Delete any existing domain_signals for this domain (prevent duplicates)
        db.query(DomainSignal).filter(DomainSignal.domain == normalized_domain).delete()
        
        # Create new domain_signal
        domain_signal = DomainSignal(
            domain=normalized_domain,
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
        db.query(LeadScore).filter(LeadScore.domain == normalized_domain).delete()
        
        # Create new lead_score
        lead_score = LeadScore(
            domain=normalized_domain,
            readiness_score=scoring_result["score"],
            segment=scoring_result["segment"],
            reason=scoring_result["reason"]
        )
        db.add(lead_score)
        
        # Log provider change if detected
        if provider_changed and previous_provider:
            change_history = ProviderChangeHistory(
                domain=normalized_domain,
                previous_provider=previous_provider,
                new_provider=provider
            )
            db.add(change_history)
        
        # Commit all changes
        db.commit()
        db.refresh(domain_signal)
        db.refresh(lead_score)
        
        # Apply auto-tagging (G17)
        try:
            apply_auto_tags(normalized_domain, db)
            db.commit()
        except Exception as e:
            # Log error but don't fail the scan
            logger.warning(f"Auto-tagging failed for {normalized_domain}: {str(e)}")
        
        # Return success result
        return {
            "domain": normalized_domain,
            "success": True,
            "result": {
                "domain": normalized_domain,
                "score": scoring_result["score"],
                "segment": scoring_result["segment"],
                "reason": scoring_result["reason"],
                "provider": provider,
                "mx_root": mx_root,
                "spf": dns_result.get("spf", False),
                "dkim": dns_result.get("dkim", False),
                "dmarc_policy": dns_result.get("dmarc_policy"),
                "scan_status": scan_status
            }
        }
    
    except Exception as e:
        logger.error(f"Error scanning domain {domain}: {str(e)}", exc_info=True)
        db.rollback()
        return {
            "domain": domain,
            "error": str(e),
            "success": False
        }




@celery_app.task(bind=True)
def bulk_scan_task(self, job_id: str):
    """
    Celery task to process bulk scan job.
    
    This task processes all domains in a job sequentially (with rate limiting).
    
    Args:
        job_id: Bulk scan job ID
    """
    tracker = get_progress_tracker()
    db = SessionLocal()
    
    try:
        # Get job and domain list
        job = tracker.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        domain_list = tracker.get_domain_list(job_id)
        if not domain_list:
            logger.error(f"Domain list not found for job {job_id}")
            tracker.set_status(job_id, "failed")
            return
        
        # Set status to running
        tracker.set_status(job_id, "running")
        
        # Process each domain sequentially (with rate limiting)
        processed = 0
        succeeded = 0
        failed = 0
        
        for domain in domain_list:
            try:
                # Scan domain (with rate limiting)
                result = scan_single_domain(domain, db)
                
                processed += 1
                error = None
                if result["success"]:
                    succeeded += 1
                    # Store result
                    tracker.store_result(job_id, domain, result["result"])
                else:
                    failed += 1
                    # Store error
                    error = {
                        "domain": domain,
                        "error": result.get("error", "Unknown error"),
                        "timestamp": None  # Will be set by tracker
                    }
                
                # Update progress (once)
                tracker.update_progress(job_id, processed, succeeded, failed, error)
                
            except Exception as e:
                logger.error(f"Error scanning domain {domain} in job {job_id}: {str(e)}", exc_info=True)
                processed += 1
                failed += 1
                error = {
                    "domain": domain,
                    "error": str(e),
                    "timestamp": None
                }
                tracker.update_progress(job_id, processed, succeeded, failed, error)
        
        # Set status to completed
        tracker.set_status(job_id, "completed")
        logger.info(f"Bulk scan job {job_id} completed: {succeeded} succeeded, {failed} failed")
    
    except Exception as e:
        logger.error(f"Error in bulk scan task {job_id}: {str(e)}", exc_info=True)
        tracker.set_status(job_id, "failed")
        raise
    
    finally:
        db.close()


@celery_app.task(bind=True)
def daily_rescan_task(self):
    """
    Daily rescan task for all domains (G18: Scheduler).
    
    This task:
    - Gets all domains that have been scanned
    - Creates bulk rescan jobs for them
    - Processes changes and creates alerts
    """
    from app.db.models import Company, DomainSignal
    
    logger.info("Starting daily rescan task...")
    
    db = SessionLocal()
    
    try:
        # Get all domains that have been scanned (have domain_signals)
        domains_with_signals = db.query(DomainSignal.domain).distinct().all()
        domain_list = [row[0] for row in domains_with_signals]
        
        if not domain_list:
            logger.info("No domains to rescan")
            return {"status": "completed", "total": 0, "message": "No domains to rescan"}
        
        logger.info(f"Found {len(domain_list)} domains to rescan")
        
        # Process in batches of 100 to avoid overwhelming the system
        batch_size = 100
        total_processed = 0
        
        for i in range(0, len(domain_list), batch_size):
            batch = domain_list[i:i + batch_size]
            
            # Create bulk rescan job for this batch
            job_id = str(uuid.uuid4())
            tracker = get_progress_tracker()
            tracker.create_job(job_id, len(batch))
            
            # Start async task
            bulk_scan_task.delay(job_id, batch)
            
            total_processed += len(batch)
            logger.info(f"Created rescan job {job_id} for {len(batch)} domains (batch {i//batch_size + 1})")
        
        logger.info(f"Daily rescan task completed: {total_processed} domains queued for rescan")
        
        return {
            "status": "completed",
            "total": total_processed,
            "batches": (len(domain_list) + batch_size - 1) // batch_size,
            "message": f"Queued {total_processed} domains for rescan"
        }
    
    except Exception as e:
        logger.error(f"Error in daily rescan task: {str(e)}", exc_info=True)
        raise
    
    finally:
        db.close()

