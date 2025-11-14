"""Change detection logic for domain signals and scores (G18)."""
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.models import (
    DomainSignal, LeadScore, Company,
    SignalChangeHistory, ScoreChangeHistory, Alert
)


def detect_signal_changes(
    domain: str,
    old_signal: Optional[DomainSignal],
    new_signal: DomainSignal,
    db: Session
) -> List[Dict]:
    """
    Detect changes in domain signals and create history records.
    
    Args:
        domain: Domain name
        old_signal: Previous domain signal (None if first scan)
        new_signal: New domain signal
        db: Database session
        
    Returns:
        List of detected changes with alert information
    """
    changes = []
    
    if not old_signal:
        # First scan, no changes to detect
        return changes
    
    # Detect SPF changes
    if old_signal.spf != new_signal.spf:
        change = SignalChangeHistory(
            domain=domain,
            signal_type="spf",
            old_value=str(old_signal.spf) if old_signal.spf is not None else None,
            new_value=str(new_signal.spf) if new_signal.spf is not None else None
        )
        db.add(change)
        changes.append({
            "type": "spf_changed",
            "old_value": old_signal.spf,
            "new_value": new_signal.spf
        })
    
    # Detect DKIM changes
    if old_signal.dkim != new_signal.dkim:
        change = SignalChangeHistory(
            domain=domain,
            signal_type="dkim",
            old_value=str(old_signal.dkim) if old_signal.dkim is not None else None,
            new_value=str(new_signal.dkim) if new_signal.dkim is not None else None
        )
        db.add(change)
        changes.append({
            "type": "dkim_changed",
            "old_value": old_signal.dkim,
            "new_value": new_signal.dkim
        })
    
    # Detect DMARC changes
    if old_signal.dmarc_policy != new_signal.dmarc_policy:
        change = SignalChangeHistory(
            domain=domain,
            signal_type="dmarc",
            old_value=old_signal.dmarc_policy,
            new_value=new_signal.dmarc_policy
        )
        db.add(change)
        
        # Check if DMARC was added (none -> quarantine/reject)
        if old_signal.dmarc_policy in (None, "none") and new_signal.dmarc_policy in ("quarantine", "reject"):
            changes.append({
                "type": "dmarc_added",
                "old_value": old_signal.dmarc_policy,
                "new_value": new_signal.dmarc_policy
            })
        else:
            changes.append({
                "type": "dmarc_changed",
                "old_value": old_signal.dmarc_policy,
                "new_value": new_signal.dmarc_policy
            })
    
    # Detect MX root changes
    if old_signal.mx_root != new_signal.mx_root:
        change = SignalChangeHistory(
            domain=domain,
            signal_type="mx",
            old_value=old_signal.mx_root,
            new_value=new_signal.mx_root
        )
        db.add(change)
        changes.append({
            "type": "mx_changed",
            "old_value": old_signal.mx_root,
            "new_value": new_signal.mx_root
        })
    
    # Detect expiry changes (expire soon)
    if new_signal.expires_at:
        days_until_expiry = (new_signal.expires_at - datetime.now().date()).days
        if 0 < days_until_expiry < 30:
            # Check if this is a new expiry warning
            if not old_signal.expires_at or (old_signal.expires_at - datetime.now().date()).days >= 30:
                changes.append({
                    "type": "expire_soon",
                    "days_until_expiry": days_until_expiry,
                    "expires_at": str(new_signal.expires_at)
                })
    
    return changes


def detect_score_changes(
    domain: str,
    old_score: Optional[LeadScore],
    new_score: LeadScore,
    db: Session
) -> List[Dict]:
    """
    Detect changes in scores and segments and create history records.
    
    Args:
        domain: Domain name
        old_score: Previous lead score (None if first scan)
        new_score: New lead score
        db: Database session
        
    Returns:
        List of detected changes with alert information
    """
    changes = []
    
    if not old_score:
        # First scan, no changes to detect
        return changes
    
    # Detect score or segment changes
    score_changed = old_score.readiness_score != new_score.readiness_score
    segment_changed = old_score.segment != new_score.segment
    
    if score_changed or segment_changed:
        change = ScoreChangeHistory(
            domain=domain,
            old_score=old_score.readiness_score,
            new_score=new_score.readiness_score,
            old_segment=old_score.segment,
            new_segment=new_score.segment
        )
        db.add(change)
        
        # Calculate priority score change (if applicable)
        from app.core.priority import calculate_priority_score
        old_priority = calculate_priority_score(old_score.segment, old_score.readiness_score)
        new_priority = calculate_priority_score(new_score.segment, new_score.readiness_score)
        
        if old_priority != new_priority:
            changes.append({
                "type": "priority_score_changed",
                "old_priority": old_priority,
                "new_priority": new_priority,
                "old_score": old_score.readiness_score,
                "new_score": new_score.readiness_score,
                "old_segment": old_score.segment,
                "new_segment": new_score.segment
            })
        elif segment_changed:
            changes.append({
                "type": "segment_changed",
                "old_segment": old_score.segment,
                "new_segment": new_score.segment,
                "old_score": old_score.readiness_score,
                "new_score": new_score.readiness_score
            })
    
    return changes


def create_alerts(
    domain: str,
    changes: List[Dict],
    db: Session
) -> List[Alert]:
    """
    Create alert records for detected changes.
    
    Args:
        domain: Domain name
        changes: List of detected changes
        db: Database session
        
    Returns:
        List of created Alert objects
    """
    alerts = []
    
    alert_type_map = {
        "mx_changed": "mx_changed",
        "dmarc_added": "dmarc_added",
        "expire_soon": "expire_soon",
        "priority_score_changed": "score_changed",
        "segment_changed": "score_changed"
    }
    
    for change in changes:
        change_type = change.get("type")
        if change_type not in alert_type_map:
            continue
        
        alert_type = alert_type_map[change_type]
        
        # Create alert message
        if change_type == "mx_changed":
            message = f"MX root changed from {change.get('old_value')} to {change.get('new_value')}"
        elif change_type == "dmarc_added":
            message = f"DMARC policy added: {change.get('new_value')}"
        elif change_type == "expire_soon":
            days = change.get("days_until_expiry", 0)
            message = f"Domain expires in {days} days"
        elif change_type == "priority_score_changed":
            message = f"Priority score changed from {change.get('old_priority')} to {change.get('new_priority')}"
        elif change_type == "segment_changed":
            message = f"Segment changed from {change.get('old_segment')} to {change.get('new_segment')}"
        else:
            message = f"Change detected: {change_type}"
        
        alert = Alert(
            domain=domain,
            alert_type=alert_type,
            alert_message=message,
            status="pending"
        )
        db.add(alert)
        alerts.append(alert)
    
    return alerts

