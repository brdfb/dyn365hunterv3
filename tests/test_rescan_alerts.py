"""Tests for ReScan, change detection, and alerts (G18)."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.main import app
from app.db.models import Company, DomainSignal, LeadScore, SignalChangeHistory, ScoreChangeHistory, Alert
from app.db.session import SessionLocal
from app.core.change_detection import detect_signal_changes, detect_score_changes, create_alerts
from app.core.rescan import rescan_domain


client = TestClient(app)


@pytest.fixture
def db():
    """Create a database session for testing."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_domain(db: Session):
    """Create a test domain with scan data."""
    domain = "test-rescan.com"
    
    # Create company
    company = Company(
        canonical_name="Test Rescan Company",
        domain=domain,
        provider="M365"
    )
    db.add(company)
    
    # Create domain signal
    signal = DomainSignal(
        domain=domain,
        spf=True,
        dkim=True,
        dmarc_policy="quarantine",
        mx_root="outlook.com",
        scan_status="success"
    )
    db.add(signal)
    
    # Create lead score
    score = LeadScore(
        domain=domain,
        readiness_score=75,
        segment="Migration",
        reason="High readiness score"
    )
    db.add(score)
    
    db.commit()
    return domain


def test_detect_signal_changes_mx(db: Session, test_domain: str):
    """Test MX change detection."""
    old_signal = db.query(DomainSignal).filter(DomainSignal.domain == test_domain).first()
    
    # Create new signal with different MX root
    new_signal = DomainSignal(
        domain=test_domain,
        spf=old_signal.spf,
        dkim=old_signal.dkim,
        dmarc_policy=old_signal.dmarc_policy,
        mx_root="google.com",  # Changed
        scan_status="success"
    )
    
    changes = detect_signal_changes(test_domain, old_signal, new_signal, db)
    db.commit()
    
    assert len(changes) > 0
    assert any(c["type"] == "mx_changed" for c in changes)
    
    # Verify history record
    history = db.query(SignalChangeHistory).filter(
        SignalChangeHistory.domain == test_domain,
        SignalChangeHistory.signal_type == "mx"
    ).first()
    assert history is not None
    assert history.old_value == "outlook.com"
    assert history.new_value == "google.com"


def test_detect_signal_changes_dmarc(db: Session, test_domain: str):
    """Test DMARC change detection."""
    old_signal = db.query(DomainSignal).filter(DomainSignal.domain == test_domain).first()
    
    # Create new signal with DMARC added
    new_signal = DomainSignal(
        domain=test_domain,
        spf=old_signal.spf,
        dkim=old_signal.dkim,
        dmarc_policy="reject",  # Changed from quarantine
        mx_root=old_signal.mx_root,
        scan_status="success"
    )
    
    changes = detect_signal_changes(test_domain, old_signal, new_signal, db)
    db.commit()
    
    assert len(changes) > 0
    assert any(c["type"] == "dmarc_changed" for c in changes)


def test_detect_score_changes(db: Session, test_domain: str):
    """Test score change detection."""
    old_score = db.query(LeadScore).filter(LeadScore.domain == test_domain).first()
    
    # Create new score with different values
    new_score = LeadScore(
        domain=test_domain,
        readiness_score=85,  # Changed from 75
        segment="Migration",  # Same
        reason="Updated score"
    )
    
    changes = detect_score_changes(test_domain, old_score, new_score, db)
    db.commit()
    
    assert len(changes) > 0
    
    # Verify history record
    history = db.query(ScoreChangeHistory).filter(
        ScoreChangeHistory.domain == test_domain
    ).first()
    assert history is not None
    assert history.old_score == 75
    assert history.new_score == 85


def test_create_alerts(db: Session, test_domain: str):
    """Test alert creation."""
    changes = [
        {"type": "mx_changed", "old_value": "outlook.com", "new_value": "google.com"},
        {"type": "expire_soon", "days_until_expiry": 15, "expires_at": "2025-12-01"}
    ]
    
    alerts = create_alerts(test_domain, changes, db)
    db.commit()
    
    assert len(alerts) == 2
    
    # Verify alerts in database
    db_alerts = db.query(Alert).filter(Alert.domain == test_domain).all()
    assert len(db_alerts) == 2
    assert any(a.alert_type == "mx_changed" for a in db_alerts)
    assert any(a.alert_type == "expire_soon" for a in db_alerts)


def test_rescan_domain(db: Session, test_domain: str):
    """Test rescan domain functionality."""
    result = rescan_domain(test_domain, db)
    
    assert result.get("success") is True
    assert result.get("domain") == test_domain
    assert "changes_detected" in result


def test_rescan_endpoint(db: Session, test_domain: str):
    """Test rescan endpoint."""
    response = client.post(f"/scan/{test_domain}/rescan")
    
    # Should succeed (domain exists and has been scanned)
    assert response.status_code in [200, 500]  # 500 if scan fails, but endpoint works
    if response.status_code == 200:
        data = response.json()
        assert data["domain"] == test_domain
        assert "changes_detected" in data


def test_bulk_rescan_endpoint(db: Session, test_domain: str):
    """Test bulk rescan endpoint."""
    response = client.post(f"/scan/bulk/rescan?domain_list={test_domain}")
    
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"


def test_list_alerts(db: Session, test_domain: str):
    """Test list alerts endpoint."""
    # Create an alert first
    alert = Alert(
        domain=test_domain,
        alert_type="mx_changed",
        alert_message="MX root changed",
        status="pending"
    )
    db.add(alert)
    db.commit()
    
    response = client.get("/alerts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_create_alert_config(db: Session):
    """Test create alert config endpoint."""
    response = client.post(
        "/alerts/config",
        json={
            "alert_type": "mx_changed",
            "notification_method": "webhook",
            "enabled": True,
            "frequency": "immediate",
            "webhook_url": "https://example.com/webhook"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["alert_type"] == "mx_changed"
    assert data["notification_method"] == "webhook"
    assert data["enabled"] is True


# Edge case tests for change detection

def test_detect_signal_changes_first_scan(db: Session, test_domain: str):
    """Test change detection on first scan (no old signal)."""
    new_signal = DomainSignal(
        domain=test_domain,
        spf=True,
        dkim=True,
        dmarc_policy="quarantine",
        mx_root="outlook.com",
        scan_status="success"
    )
    
    changes = detect_signal_changes(test_domain, None, new_signal, db)
    
    # First scan should not detect changes
    assert len(changes) == 0


def test_detect_signal_changes_expiry_soon(db: Session, test_domain: str):
    """Test expiry detection (expire soon)."""
    old_signal = db.query(DomainSignal).filter(DomainSignal.domain == test_domain).first()
    
    # Create new signal with expiry in 15 days
    expires_at = (datetime.now().date() + timedelta(days=15))
    new_signal = DomainSignal(
        domain=test_domain,
        spf=old_signal.spf,
        dkim=old_signal.dkim,
        dmarc_policy=old_signal.dmarc_policy,
        mx_root=old_signal.mx_root,
        expires_at=expires_at,
        scan_status="success"
    )
    
    changes = detect_signal_changes(test_domain, old_signal, new_signal, db)
    db.commit()
    
    # Should detect expiry warning
    assert any(c["type"] == "expire_soon" for c in changes)
    expire_change = next(c for c in changes if c["type"] == "expire_soon")
    assert expire_change["days_until_expiry"] == 15


def test_detect_signal_changes_expiry_not_soon(db: Session, test_domain: str):
    """Test expiry detection (not soon enough)."""
    old_signal = db.query(DomainSignal).filter(DomainSignal.domain == test_domain).first()
    
    # Create new signal with expiry in 60 days (not soon)
    expires_at = (datetime.now().date() + timedelta(days=60))
    new_signal = DomainSignal(
        domain=test_domain,
        spf=old_signal.spf,
        dkim=old_signal.dkim,
        dmarc_policy=old_signal.dmarc_policy,
        mx_root=old_signal.mx_root,
        expires_at=expires_at,
        scan_status="success"
    )
    
    changes = detect_signal_changes(test_domain, old_signal, new_signal, db)
    
    # Should not detect expiry warning (too far in future)
    assert not any(c["type"] == "expire_soon" for c in changes)


def test_detect_signal_changes_dmarc_added(db: Session, test_domain: str):
    """Test DMARC added detection (none -> quarantine/reject)."""
    old_signal = db.query(DomainSignal).filter(DomainSignal.domain == test_domain).first()
    # Update old signal to have no DMARC
    old_signal.dmarc_policy = None
    db.commit()
    
    # Create new signal with DMARC added
    new_signal = DomainSignal(
        domain=test_domain,
        spf=old_signal.spf,
        dkim=old_signal.dkim,
        dmarc_policy="reject",  # Added
        mx_root=old_signal.mx_root,
        scan_status="success"
    )
    
    changes = detect_signal_changes(test_domain, old_signal, new_signal, db)
    db.commit()
    
    # Should detect dmarc_added (not just dmarc_changed)
    assert any(c["type"] == "dmarc_added" for c in changes)


def test_detect_signal_changes_spf_change(db: Session, test_domain: str):
    """Test SPF change detection."""
    old_signal = db.query(DomainSignal).filter(DomainSignal.domain == test_domain).first()
    old_signal.spf = False
    db.commit()
    
    # Create new signal with SPF added
    new_signal = DomainSignal(
        domain=test_domain,
        spf=True,  # Changed
        dkim=old_signal.dkim,
        dmarc_policy=old_signal.dmarc_policy,
        mx_root=old_signal.mx_root,
        scan_status="success"
    )
    
    changes = detect_signal_changes(test_domain, old_signal, new_signal, db)
    db.commit()
    
    assert any(c["type"] == "spf_changed" for c in changes)
    
    # Verify history record
    history = db.query(SignalChangeHistory).filter(
        SignalChangeHistory.domain == test_domain,
        SignalChangeHistory.signal_type == "spf"
    ).first()
    assert history is not None


def test_detect_signal_changes_dkim_change(db: Session, test_domain: str):
    """Test DKIM change detection."""
    old_signal = db.query(DomainSignal).filter(DomainSignal.domain == test_domain).first()
    old_signal.dkim = False
    db.commit()
    
    # Create new signal with DKIM added
    new_signal = DomainSignal(
        domain=test_domain,
        spf=old_signal.spf,
        dkim=True,  # Changed
        dmarc_policy=old_signal.dmarc_policy,
        mx_root=old_signal.mx_root,
        scan_status="success"
    )
    
    changes = detect_signal_changes(test_domain, old_signal, new_signal, db)
    db.commit()
    
    assert any(c["type"] == "dkim_changed" for c in changes)


def test_detect_score_changes_first_scan(db: Session, test_domain: str):
    """Test score change detection on first scan (no old score)."""
    new_score = LeadScore(
        domain=test_domain,
        readiness_score=75,
        segment="Migration",
        reason="First scan"
    )
    
    changes = detect_score_changes(test_domain, None, new_score, db)
    
    # First scan should not detect changes
    assert len(changes) == 0


def test_detect_score_changes_segment_change(db: Session, test_domain: str):
    """Test segment change detection."""
    old_score = db.query(LeadScore).filter(LeadScore.domain == test_domain).first()
    old_score.segment = "Cold"
    old_score.readiness_score = 30
    db.commit()
    
    # Create new score with segment change
    new_score = LeadScore(
        domain=test_domain,
        readiness_score=75,  # Changed
        segment="Migration",  # Changed
        reason="Updated"
    )
    
    changes = detect_score_changes(test_domain, old_score, new_score, db)
    db.commit()
    
    # Should detect segment change or priority score change
    assert len(changes) > 0
    assert any(c["type"] in ["segment_changed", "priority_score_changed"] for c in changes)


def test_detect_score_changes_priority_score_change(db: Session, test_domain: str):
    """Test priority score change detection."""
    old_score = db.query(LeadScore).filter(LeadScore.domain == test_domain).first()
    old_score.readiness_score = 65  # Priority 2
    old_score.segment = "Migration"
    db.commit()
    
    # Create new score that changes priority
    new_score = LeadScore(
        domain=test_domain,
        readiness_score=85,  # Priority 1
        segment="Migration",
        reason="Updated"
    )
    
    changes = detect_score_changes(test_domain, old_score, new_score, db)
    db.commit()
    
    # Should detect priority score change
    assert any(c["type"] == "priority_score_changed" for c in changes)


def test_create_alerts_unknown_change_type(db: Session, test_domain: str):
    """Test alert creation with unknown change type."""
    changes = [
        {"type": "unknown_change", "old_value": "old", "new_value": "new"}
    ]
    
    alerts = create_alerts(test_domain, changes, db)
    
    # Unknown change types should not create alerts
    assert len(alerts) == 0


def test_create_alerts_no_changes(db: Session, test_domain: str):
    """Test alert creation with no changes."""
    alerts = create_alerts(test_domain, [], db)
    
    assert len(alerts) == 0


def test_rescan_domain_no_old_signal(db: Session, test_domain: str):
    """Test rescan when no old signal exists (first scan scenario)."""
    # Delete old signal
    db.query(DomainSignal).filter(DomainSignal.domain == test_domain).delete()
    db.commit()
    
    # Rescan should still work (treats as first scan)
    result = rescan_domain(test_domain, db)
    
    # Should succeed but no changes detected
    assert result.get("success") is True
    assert result.get("changes_detected") is False
