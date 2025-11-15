"""Celery tasks for async domain scanning."""

from app.core.logging import logger
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
                "success": False,
            }

        # Check if company exists
        company = db.query(Company).filter(Company.domain == normalized_domain).first()
        if not company:
            return {
                "domain": normalized_domain,
                "error": "Domain not found. Please ingest first.",
                "success": False,
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

        # G20: Classify local provider (if provider is Local)
        local_provider = None
        if provider == "Local" and mx_root:
            from app.core.provider_map import classify_local_provider
            local_provider = classify_local_provider(mx_root)

        # G20: Estimate tenant size (for M365 and Google)
        tenant_size = None
        if provider in ["M365", "Google"] and mx_root:
            from app.core.provider_map import estimate_tenant_size
            tenant_size = estimate_tenant_size(provider, mx_root)

        # Track provider changes
        previous_provider = company.provider
        provider_changed = False

        # Update company provider and tenant_size if we have new information
        if provider and provider != "Unknown":
            if previous_provider != provider:
                provider_changed = True
            company.provider = provider
            if tenant_size:
                company.tenant_size = tenant_size
            db.commit()

        # Prepare signals for scoring
        signals = {
            "spf": dns_result.get("spf", False),
            "dkim": dns_result.get("dkim", False),
            "dmarc_policy": dns_result.get("dmarc_policy"),
        }

        # Calculate score and determine segment
        scoring_result = score_domain(
            domain=normalized_domain,
            provider=provider,
            signals=signals,
            mx_records=dns_result.get("mx_records", []),
        )

        # Delete any existing domain_signals for this domain (prevent duplicates)
        db.query(DomainSignal).filter(DomainSignal.domain == normalized_domain).delete()

        # Create new domain_signal
        domain_signal = DomainSignal(
            domain=normalized_domain,
            spf=dns_result.get("spf", False),
            dkim=dns_result.get("dkim", False),
            dmarc_policy=dns_result.get("dmarc_policy"),
            dmarc_coverage=dns_result.get("dmarc_coverage"),  # G20: DMARC coverage
            mx_root=mx_root,
            local_provider=local_provider,  # G20: Local provider name
            registrar=whois_result.get("registrar") if whois_result else None,
            expires_at=whois_result.get("expires_at") if whois_result else None,
            nameservers=whois_result.get("nameservers") if whois_result else None,
            scan_status=scan_status,
        )
        db.add(domain_signal)

        # Delete any existing lead_scores for this domain (prevent duplicates)
        db.query(LeadScore).filter(LeadScore.domain == normalized_domain).delete()

        # Create new lead_score
        lead_score = LeadScore(
            domain=normalized_domain,
            readiness_score=scoring_result["score"],
            segment=scoring_result["segment"],
            reason=scoring_result["reason"],
        )
        db.add(lead_score)

        # Log provider change if detected
        if provider_changed and previous_provider:
            change_history = ProviderChangeHistory(
                domain=normalized_domain,
                previous_provider=previous_provider,
                new_provider=provider,
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
            logger.warning("auto_tagging_failed", domain=normalized_domain, error=str(e))

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
                "local_provider": local_provider,  # G20: Local provider name
                "tenant_size": tenant_size,  # G20: Tenant size estimate
                "mx_root": mx_root,
                "spf": dns_result.get("spf", False),
                "dkim": dns_result.get("dkim", False),
                "dmarc_policy": dns_result.get("dmarc_policy"),
                "dmarc_coverage": dns_result.get("dmarc_coverage"),  # G20: DMARC coverage
                "scan_status": scan_status,
            },
        }

    except Exception as e:
        logger.error("scan_error", domain=domain, error=str(e), exc_info=True)
        db.rollback()
        return {"domain": domain, "error": str(e), "success": False}


@celery_app.task(bind=True)
def bulk_scan_task(self, job_id: str, is_rescan: bool = False):
    """
    Celery task to process bulk scan job.

    This task processes all domains in a job sequentially (with rate limiting).
    Supports both regular scan and rescan (with change detection).

    Args:
        job_id: Bulk scan job ID
        is_rescan: If True, use rescan_domain (with change detection), else use scan_single_domain
    """
    from app.core.rescan import rescan_domain

    tracker = get_progress_tracker()
    db = SessionLocal()

    try:
        # Get job and domain list
        job = tracker.get_job(job_id)
        if not job:
            logger.error("job_not_found", job_id=job_id)
            return

        domain_list = tracker.get_domain_list(job_id)
        if not domain_list:
            logger.error("domain_list_not_found", job_id=job_id)
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
                # Scan or rescan domain (with rate limiting)
                if is_rescan:
                    result = rescan_domain(domain, db)
                    # For rescan, result structure is different - extract result dict
                    if result.get("success"):
                        result_dict = result.get("result", {})
                        # Include change information in stored result
                        result_dict["changes_detected"] = result.get(
                            "changes_detected", False
                        )
                        result_dict["signal_changes"] = result.get("signal_changes", 0)
                        result_dict["score_changes"] = result.get("score_changes", 0)
                        result_dict["alerts_created"] = result.get("alerts_created", 0)
                else:
                    result = scan_single_domain(domain, db)

                processed += 1
                error = None
                if result["success"]:
                    succeeded += 1
                    # Store result
                    if is_rescan:
                        tracker.store_result(job_id, domain, result.get("result", {}))
                    else:
                        tracker.store_result(job_id, domain, result["result"])
                else:
                    failed += 1
                    # Store error
                    error = {
                        "domain": domain,
                        "error": result.get("error", "Unknown error"),
                        "timestamp": None,  # Will be set by tracker
                    }

                # Update progress (once)
                tracker.update_progress(job_id, processed, succeeded, failed, error)

            except Exception as e:
                logger.error(
                    "scan_domain_error",
                    domain=domain,
                    job_id=job_id,
                    error=str(e),
                    exc_info=True,
                )
                processed += 1
                failed += 1
                error = {"domain": domain, "error": str(e), "timestamp": None}
                tracker.update_progress(job_id, processed, succeeded, failed, error)

        # Set status to completed
        tracker.set_status(job_id, "completed")
        logger.info(
            "bulk_scan_completed",
            job_id=job_id,
            scan_type="rescan" if is_rescan else "scan",
            succeeded=succeeded,
            failed=failed,
        )

    except Exception as e:
        logger.error(
            "bulk_scan_error",
            job_id=job_id,
            scan_type="rescan" if is_rescan else "scan",
            error=str(e),
            exc_info=True,
        )
        tracker.set_status(job_id, "failed")
        raise

    finally:
        db.close()


@celery_app.task(bind=True)
def process_pending_alerts_task(self):
    """
    Process pending alerts and send notifications (G18: Alert processing).

    This task:
    - Gets all pending alerts
    - Sends notifications based on alert configuration
    - Updates alert status
    """
    import asyncio
    from app.core.notifications import process_pending_alerts

    logger.info("pending_alerts_task_started")

    db = SessionLocal()

    try:
        # Process pending alerts (async function, need to run in event loop)
        processed = asyncio.run(process_pending_alerts(db))
        logger.info("pending_alerts_processed", processed=processed)
        return {"status": "completed", "processed": processed}

    except Exception as e:
        logger.error("pending_alerts_task_error", error=str(e), exc_info=True)
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

    logger.info("daily_rescan_task_started")

    db = SessionLocal()

    try:
        # Get all domains that have been scanned (have domain_signals)
        domains_with_signals = db.query(DomainSignal.domain).distinct().all()
        domain_list = [row[0] for row in domains_with_signals]

        if not domain_list:
            logger.info("daily_rescan_no_domains")
            return {
                "status": "completed",
                "total": 0,
                "message": "No domains to rescan",
            }

        logger.info("daily_rescan_domains_found", count=len(domain_list))

        # Process in batches of 100 to avoid overwhelming the system
        batch_size = 100
        total_processed = 0

        for i in range(0, len(domain_list), batch_size):
            batch = domain_list[i : i + batch_size]

            # Create bulk rescan job for this batch (creates job_id automatically)
            tracker = get_progress_tracker()
            job_id = tracker.create_job(batch)

            # Start async rescan task (with is_rescan=True for change detection)
            bulk_scan_task.delay(job_id, is_rescan=True)

            total_processed += len(batch)
            logger.info(
                "rescan_job_created",
                job_id=job_id,
                batch_size=len(batch),
                batch_number=i//batch_size + 1,
            )

        logger.info(
            "daily_rescan_completed",
            total_processed=total_processed,
        )

        return {
            "status": "completed",
            "total": total_processed,
            "batches": (len(domain_list) + batch_size - 1) // batch_size,
            "message": f"Queued {total_processed} domains for rescan",
        }

    except Exception as e:
        logger.error("daily_rescan_error", error=str(e), exc_info=True)
        raise

    finally:
        db.close()
