"""Celery tasks for async domain scanning."""

import time
from app.core.logging import logger
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import event, Engine, text
from app.core.celery_app import celery_app
from app.core.progress_tracker import get_progress_tracker
from app.core.rate_limiter import wait_for_dns_rate_limit, wait_for_whois_rate_limit
from app.core.cache import get_cached_scan, set_cached_scan, invalidate_scan_cache
from app.core.normalizer import normalize_domain
from app.core.analyzer_dns import analyze_dns, resolve_domain_ip_candidates
from app.core.analyzer_whois import get_whois_info
from app.core.provider_map import classify_provider
from app.core.scorer import score_domain
from app.core.auto_tagging import apply_auto_tags
from app.core.enrichment_service import spawn_enrichment
from app.db.session import SessionLocal
from app.db.models import Company, DomainSignal, LeadScore, ProviderChangeHistory
from app.core.bulk_operations import (
    calculate_optimal_batch_size,
    store_partial_commit_log,
    get_bulk_log_context,
)
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy.exc import OperationalError

# Bulk operations metrics tracking (in-memory counters)
_bulk_metrics = {
    "batch_success": 0,
    "batch_failure": 0,
    "deadlock_occurrences": 0,
    "partial_commit_recoveries": 0,
    "batch_processing_times": [],  # List of processing times in seconds
    "total_batches": 0,
    "total_domains_processed": 0,
    "total_domains_succeeded": 0,
    "total_domains_failed": 0,
}



def scan_single_domain(
    domain: str, db: Session, use_cache: bool = True, commit: bool = True
) -> Dict:
    """
    Scan a single domain (with rate limiting and caching).

    This is a helper function that wraps the scan logic with rate limiting.
    It's used by both the sync endpoint and the async task.

    Uses Redis-based caching (1 hour TTL) for full scan results to reduce
    DNS/WHOIS queries and scoring calculations.

    Args:
        domain: Domain name to scan
        db: Database session
        use_cache: Whether to use cache (default: True)
        commit: Whether to commit transaction (default: True). Set to False for batch processing.

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

        # Perform DNS analysis (uses DNS cache internally)
        dns_result = analyze_dns(normalized_domain, use_cache=use_cache)

        # Rate limiting: WHOIS (5 req/s)
        wait_for_whois_rate_limit()

        # Perform WHOIS lookup (optional, graceful fail, uses WHOIS cache internally)
        whois_result = get_whois_info(normalized_domain, use_cache=use_cache)

        # Determine scan status
        scan_status = dns_result.get("status", "success")
        if scan_status == "success" and whois_result is None:
            scan_status = "whois_failed"

        # Classify provider based on MX root (uses provider cache internally)
        mx_root = dns_result.get("mx_root")
        provider = classify_provider(mx_root, use_cache=use_cache)

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
            if commit:
                db.commit()

        # Prepare signals for scoring
        signals = {
            "spf": dns_result.get("spf", False),
            "dkim": dns_result.get("dkim", False),
            "dmarc_policy": dns_result.get("dmarc_policy"),
        }

        # Calculate score and determine segment (uses scoring cache internally)
        scoring_result = score_domain(
            domain=normalized_domain,
            provider=provider,
            signals=signals,
            mx_records=dns_result.get("mx_records", []),
            use_cache=use_cache,
        )

        # Cache full scan result (for future reference, but DB is source of truth)
        if use_cache:
            scan_cache_data = {
                "dns_result": dns_result,
                "whois_result": whois_result,
                "provider": provider,
                "local_provider": local_provider,
                "tenant_size": tenant_size,
                "scoring_result": scoring_result,
                "scan_status": scan_status,
                "mx_root": mx_root,
            }
            set_cached_scan(normalized_domain, scan_cache_data)

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

        # Commit all changes (if commit=True)
        if commit:
            db.commit()
            db.refresh(domain_signal)
            db.refresh(lead_score)

            # Apply auto-tagging (G17) - only if committing
            try:
                apply_auto_tags(normalized_domain, db)
                db.commit()
            except Exception as e:
                # Log error but don't fail the scan
                logger.warning("auto_tagging_failed", domain=normalized_domain, error=str(e))

        # IP Enrichment (fire-and-forget, separate DB session)
        # Resolve IP addresses from MX records and root domain
        mx_records = dns_result.get("mx_records", [])
        ip_candidates = resolve_domain_ip_candidates(normalized_domain, mx_records)
        ip_address = ip_candidates[0] if ip_candidates else None
        
        if ip_address:
            # Spawn enrichment in background (separate session, won't affect scan)
            spawn_enrichment(normalized_domain, ip_address)

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


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    retry=retry_if_exception_type(OperationalError),
    reraise=True,
)
def process_batch_with_retry(
    batch: List[str],
    job_id: str,
    batch_no: int,
    total_batches: int,
    is_rescan: bool,
    db: Session,
) -> Tuple[int, int, List[Dict], List[Dict]]:
    """
    Process a batch of domains with retry logic for deadlock prevention.

    Args:
        batch: List of domains to process
        job_id: Bulk scan job ID
        batch_no: Batch number
        total_batches: Total number of batches
        is_rescan: If True, use rescan_domain, else use scan_single_domain
        db: Database session

    Returns:
        Tuple of (succeeded_count, failed_count, committed_results, failed_results)
    """
    from app.core.rescan import rescan_domain
    from datetime import datetime

    tracker = get_progress_tracker()
    succeeded = 0
    failed = 0
    committed = []
    failed_results = []

    # Set transaction timeout (30 seconds) for deadlock prevention
    db.execute(text("SET statement_timeout = 30000"))  # 30 seconds in milliseconds

    batch_start_time = time.time()
    try:
        # Process each domain in batch (with commit=False for batch commit)
        for domain in batch:
            try:
                if is_rescan:
                    # For rescan, we need to handle it differently since rescan_domain
                    # doesn't support commit=False yet. For now, we'll use commit=True
                    # but batch the auto-tagging separately.
                    result = rescan_domain(domain, db)
                    if result.get("success"):
                        result_dict = result.get("result", {})
                        result_dict["changes_detected"] = result.get(
                            "changes_detected", False
                        )
                        result_dict["signal_changes"] = result.get("signal_changes", 0)
                        result_dict["score_changes"] = result.get("score_changes", 0)
                        result_dict["alerts_created"] = result.get("alerts_created", 0)
                        # Update result with enhanced data
                        result["result"] = result_dict
                else:
                    # Use commit=False for batch processing
                    result = scan_single_domain(domain, db, commit=False)

                if result["success"]:
                    succeeded += 1
                    committed.append(
                        {
                            "domain": domain,
                            "status": "success",
                            "result": result.get("result", {}),
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                else:
                    failed += 1
                    failed_results.append(
                        {
                            "domain": domain,
                            "status": "error",
                            "error": result.get("error", "Unknown error"),
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

            except Exception as e:
                logger.error(
                    "scan_domain_error",
                    domain=domain,
                    job_id=job_id,
                    batch_no=batch_no,
                    error=str(e),
                    exc_info=True,
                )
                failed += 1
                failed_results.append(
                    {
                        "domain": domain,
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

        # Batch commit (only if not rescan, since rescan commits individually)
        if not is_rescan:
            db.commit()

            # Apply auto-tagging for all succeeded domains in batch
            for committed_item in committed:
                try:
                    apply_auto_tags(committed_item["domain"], db)
                except Exception as e:
                    logger.warning(
                        "auto_tagging_failed",
                        domain=committed_item["domain"],
                        error=str(e),
                    )
            db.commit()

        # Track batch success and processing time
        batch_processing_time = time.time() - batch_start_time
        _bulk_metrics["batch_success"] += 1
        _bulk_metrics["batch_processing_times"].append(batch_processing_time)
        # Keep only last 100 processing times to avoid memory issues
        if len(_bulk_metrics["batch_processing_times"]) > 100:
            _bulk_metrics["batch_processing_times"] = _bulk_metrics["batch_processing_times"][-100:]

        return succeeded, failed, committed, failed_results

    except Exception as e:
        db.rollback()
        # Check if it's a deadlock/lock error
        error_str = str(e).lower()
        if "deadlock" in error_str or "lock" in error_str or "timeout" in error_str:
            logger.warning(
                "batch_deadlock_detected",
                job_id=job_id,
                batch_no=batch_no,
                error=str(e),
            )
            _bulk_metrics["deadlock_occurrences"] += 1
            raise  # Retry
        else:
            # Non-deadlock error, don't retry
            logger.error(
                "batch_processing_error",
                job_id=job_id,
                batch_no=batch_no,
                error=str(e),
                exc_info=True,
            )
            _bulk_metrics["batch_failure"] += 1
            raise


@celery_app.task(bind=True)
def bulk_scan_task(self, job_id: str, is_rescan: bool = False):
    """
    Celery task to process bulk scan job with batch processing optimization (P1-4).

    This task processes domains in batches (rate-limit aware) with:
    - Batch commit optimization (reduces transaction overhead)
    - Deadlock prevention (transaction timeout, retry logic)
    - Partial commit log (for recovery)
    - Batch isolation (one batch failure doesn't affect others)

    Args:
        job_id: Bulk scan job ID
        is_rescan: If True, use rescan_domain (with change detection), else use scan_single_domain
    """
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

        # Calculate optimal batch size (rate-limit aware)
        optimal_batch_size = calculate_optimal_batch_size(
            dns_rate_limit=10.0,  # req/s
            whois_rate_limit=5.0,  # req/s
            batch_duration=10.0,  # seconds
            max_batch_size=100,
        )

        # Process domains in batches
        total_batches = (len(domain_list) + optimal_batch_size - 1) // optimal_batch_size
        processed = 0
        total_succeeded = 0
        total_failed = 0

        for batch_no in range(total_batches):
            batch_start = batch_no * optimal_batch_size
            batch_end = min(batch_start + optimal_batch_size, len(domain_list))
            batch = domain_list[batch_start:batch_end]

            # Get bulk log context for structured logging
            log_context = get_bulk_log_context(
                bulk_id=job_id,
                batch_no=batch_no + 1,
                total_batches=total_batches,
                batch_size=len(batch),
            )

            logger.info(
                "bulk_scan_batch_started",
                **log_context,
                scan_type="rescan" if is_rescan else "scan",
            )

            try:
                # Process batch with retry logic (deadlock prevention)
                succeeded, failed, committed, failed_results = process_batch_with_retry(
                    batch=batch,
                    job_id=job_id,
                    batch_no=batch_no + 1,
                    total_batches=total_batches,
                    is_rescan=is_rescan,
                    db=db,
                )

                # Store partial commit log
                store_partial_commit_log(
                    bulk_id=job_id,
                    batch_no=batch_no + 1,
                    total_batches=total_batches,
                    committed=committed,
                    failed=failed_results,
                )

                # Track partial commit recovery if there were failures
                if failed > 0:
                    _bulk_metrics["partial_commit_recoveries"] += 1

                # Update progress tracker
                processed += len(batch)
                total_succeeded += succeeded
                total_failed += failed
                
                # Update bulk metrics
                _bulk_metrics["total_batches"] += 1
                _bulk_metrics["total_domains_processed"] += len(batch)
                _bulk_metrics["total_domains_succeeded"] += succeeded
                _bulk_metrics["total_domains_failed"] += failed

                # Store results for succeeded domains
                for committed_item in committed:
                    domain = committed_item["domain"]
                    result_data = committed_item.get("result", {})
                    # Store the actual scan result
                    tracker.store_result(job_id, domain, result_data)

                # Store errors for failed domains
                for failed_item in failed_results:
                    error = {
                        "domain": failed_item["domain"],
                        "error": failed_item.get("error", "Unknown error"),
                        "timestamp": failed_item.get("timestamp"),
                    }
                    tracker.update_progress(
                        job_id, processed, total_succeeded, total_failed, error
                    )

                logger.info(
                    "bulk_scan_batch_completed",
                    **log_context,
                    succeeded=succeeded,
                    failed=failed,
                )

            except Exception as e:
                # Batch failed (after retries), log and continue with next batch
                logger.error(
                    "bulk_scan_batch_failed",
                    **log_context,
                    error=str(e),
                    exc_info=True,
                )
                # Mark all domains in batch as failed
                for domain in batch:
                    error = {
                        "domain": domain,
                        "error": f"Batch processing failed: {str(e)}",
                        "timestamp": None,
                    }
                    processed += 1
                    total_failed += 1
                    tracker.update_progress(
                        job_id, processed, total_succeeded, total_failed, error
                    )

        # Set status to completed
        tracker.set_status(job_id, "completed")
        logger.info(
            "bulk_scan_completed",
            job_id=job_id,
            scan_type="rescan" if is_rescan else "scan",
            succeeded=total_succeeded,
            failed=total_failed,
            total_batches=total_batches,
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


def get_bulk_metrics() -> Dict[str, Any]:
    """
    Get bulk operations metrics (batch success/failure rate, processing time, deadlock count, etc.).
    
    Returns:
        Dictionary with bulk operations metrics
    """
    processing_times = _bulk_metrics["batch_processing_times"]
    avg_processing_time = (
        sum(processing_times) / len(processing_times) if processing_times else 0.0
    )
    
    total_batches = _bulk_metrics["batch_success"] + _bulk_metrics["batch_failure"]
    batch_success_rate = (
        (_bulk_metrics["batch_success"] / total_batches * 100) if total_batches > 0 else 0.0
    )
    
    total_domains = _bulk_metrics["total_domains_processed"]
    domain_success_rate = (
        (_bulk_metrics["total_domains_succeeded"] / total_domains * 100) if total_domains > 0 else 0.0
    )
    
    return {
        "batch_success": _bulk_metrics["batch_success"],
        "batch_failure": _bulk_metrics["batch_failure"],
        "batch_success_rate_percent": round(batch_success_rate, 2),
        "deadlock_occurrences": _bulk_metrics["deadlock_occurrences"],
        "partial_commit_recoveries": _bulk_metrics["partial_commit_recoveries"],
        "average_batch_processing_time_seconds": round(avg_processing_time, 3),
        "total_batches": _bulk_metrics["total_batches"],
        "total_domains_processed": _bulk_metrics["total_domains_processed"],
        "total_domains_succeeded": _bulk_metrics["total_domains_succeeded"],
        "total_domains_failed": _bulk_metrics["total_domains_failed"],
        "domain_success_rate_percent": round(domain_success_rate, 2),
    }


def reset_bulk_metrics():
    """Reset bulk operations metrics (for testing)."""
    global _bulk_metrics
    _bulk_metrics = {
        "batch_success": 0,
        "batch_failure": 0,
        "deadlock_occurrences": 0,
        "partial_commit_recoveries": 0,
        "batch_processing_times": [],
        "total_batches": 0,
        "total_domains_processed": 0,
        "total_domains_succeeded": 0,
        "total_domains_failed": 0,
    }
