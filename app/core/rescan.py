"""ReScan engine for domain re-scanning with change detection (G18)."""

from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.db.models import DomainSignal, LeadScore, Company
from app.core.tasks import scan_single_domain
from app.core.change_detection import (
    detect_signal_changes,
    detect_score_changes,
    create_alerts,
)
from app.core.auto_tagging import apply_auto_tags
from app.core.logging import logger
import copy


def rescan_domain(domain: str, db: Session) -> Dict:
    """
    Re-scan a domain and detect changes.

    Args:
        domain: Domain name (normalized)
        db: Database session

    Returns:
        Dictionary with scan result and detected changes
    """
    # Get old signal and score for comparison (before scan)
    old_signal = db.query(DomainSignal).filter(DomainSignal.domain == domain).first()
    old_score = db.query(LeadScore).filter(LeadScore.domain == domain).first()

    # Create copies for comparison (since scan will delete and recreate)
    old_signal_copy = None
    old_score_copy = None
    if old_signal:
        old_signal_copy = DomainSignal(
            domain=old_signal.domain,
            spf=old_signal.spf,
            dkim=old_signal.dkim,
            dmarc_policy=old_signal.dmarc_policy,
            mx_root=old_signal.mx_root,
            expires_at=old_signal.expires_at,
        )
    if old_score:
        old_score_copy = LeadScore(
            domain=old_score.domain,
            readiness_score=old_score.readiness_score,
            segment=old_score.segment,
        )

    # Perform scan
    scan_result = scan_single_domain(domain, db)

    if not scan_result.get("success"):
        return scan_result

    # Get new signal and score (after scan)
    new_signal = db.query(DomainSignal).filter(DomainSignal.domain == domain).first()
    new_score = db.query(LeadScore).filter(LeadScore.domain == domain).first()

    if not new_signal or not new_score:
        return {"success": False, "error": "Failed to retrieve scan results"}

    # Detect changes (use copies since originals were deleted)
    signal_changes = detect_signal_changes(domain, old_signal_copy, new_signal, db)
    score_changes = detect_score_changes(domain, old_score_copy, new_score, db)

    # Create alerts for changes
    all_changes = signal_changes + score_changes
    alerts = create_alerts(domain, all_changes, db)

    # Apply auto-tagging (may create new tags based on new signals)
    try:
        apply_auto_tags(domain, db)
    except Exception as e:
        # Log but don't fail
        logger.warning("auto_tagging_failed", domain=domain, error=str(e))

    # Commit all changes
    db.commit()

    # Trigger alert notification processing (async, non-blocking)
    # Alerts will be processed by the scheduled task, but we can also trigger it immediately
    # for faster notification delivery
    try:
        from app.core.tasks import process_pending_alerts_task

        # Trigger async task to process alerts (non-blocking)
        process_pending_alerts_task.delay()
    except Exception as e:
        # Log but don't fail - alerts will be processed by scheduled task
        logger.warning("alert_processing_trigger_failed", error=str(e))

    return {
        "success": True,
        "domain": domain,
        "result": scan_result.get("result", {}),
        "changes_detected": len(all_changes) > 0,
        "signal_changes": len(signal_changes),
        "score_changes": len(score_changes),
        "alerts_created": len(alerts),
        "changes": all_changes,
    }
