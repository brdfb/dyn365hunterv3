"""Tests for Notes, Tags, and Favorites endpoints (G17).

Phase 3 (Read-Only Mode): Write endpoints return 410 Gone, read endpoints still work.
"""

import pytest
from sqlalchemy.orm import Session
from app.db.models import Company, DomainSignal, LeadScore, Note, Tag, Favorite
from app.core.deprecated_monitoring import get_deprecated_metrics, reset_deprecated_metrics

# Use shared fixtures from conftest.py:
# - db_session: Transaction-based isolated database session
# - client: TestClient with database dependency override


@pytest.fixture
def test_domain(db_session: Session):
    """Create a test domain with scan data.
    
    Note: Changes are automatically rolled back after test due to transaction isolation.
    """
    domain = "test-notes.com"

    # Create company
    company = Company(canonical_name="Test Company", domain=domain, provider="M365")
    db_session.add(company)

    # Create domain signal
    signal = DomainSignal(
        domain=domain,
        spf=True,
        dkim=True,
        dmarc_policy="quarantine",
        mx_root="outlook.com",
        scan_status="success",
    )
    db_session.add(signal)

    # Create lead score
    score = LeadScore(
        domain=domain,
        readiness_score=75,
        segment="Migration",
        reason="High readiness score",
    )
    db_session.add(score)

    db_session.commit()
    return domain


def test_create_note_phase3_disabled(client, test_domain: str):
    """Test creating a note - Phase 3: Should return 410 Gone."""
    reset_deprecated_metrics()
    response = client.post(
        f"/leads/{test_domain}/notes", json={"note": "This is a test note"}
    )
    assert response.status_code == 410
    data = response.json()["detail"]
    assert "error" in data
    assert "deprecated" in data["error"].lower() or "disabled" in data["error"].lower()
    assert "alternative" in data
    
    # Check metrics tracking
    metrics = get_deprecated_metrics()
    assert metrics["total_calls"] == 1
    assert "POST /leads/{domain}/notes" in metrics["calls_by_endpoint"]


def test_list_notes(client, db_session: Session, test_domain: str):
    """Test listing notes."""
    # Create notes
    note1 = Note(domain=test_domain, note="Test note 1")
    db_session.add(note1)
    note2 = Note(domain=test_domain, note="Test note 2")
    db_session.add(note2)
    db_session.commit()

    response = client.get(f"/leads/{test_domain}/notes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Verify both notes exist (order may vary due to timestamp precision)
    note_texts = [n["note"] for n in data]
    assert "Test note 1" in note_texts
    assert "Test note 2" in note_texts
    
    # Verify response structure
    assert all("id" in n for n in data)
    assert all("domain" in n for n in data)
    assert all("note" in n for n in data)
    assert all("created_at" in n for n in data)


def test_update_note_phase3_disabled(client, db_session: Session, test_domain: str):
    """Test updating a note - Phase 3: Should return 410 Gone."""
    # Create a note first (directly in DB for testing)
    note = Note(domain=test_domain, note="Original note")
    db_session.add(note)
    db_session.commit()
    note_id = note.id

    reset_deprecated_metrics()
    response = client.put(
        f"/leads/{test_domain}/notes/{note_id}", json={"note": "Updated note"}
    )
    assert response.status_code == 410
    data = response.json()["detail"]
    assert "error" in data
    assert "deprecated" in data["error"].lower() or "disabled" in data["error"].lower()
    
    # Check metrics tracking
    metrics = get_deprecated_metrics()
    assert metrics["total_calls"] == 1
    assert "PUT /leads/{domain}/notes/{note_id}" in metrics["calls_by_endpoint"]


def test_delete_note_phase3_disabled(client, db_session: Session, test_domain: str):
    """Test deleting a note - Phase 3: Should return 410 Gone."""
    # Create a note first (directly in DB for testing)
    note = Note(domain=test_domain, note="Note to delete")
    db_session.add(note)
    db_session.commit()
    note_id = note.id

    reset_deprecated_metrics()
    response = client.delete(f"/leads/{test_domain}/notes/{note_id}")
    assert response.status_code == 410
    data = response.json()["detail"]
    assert "error" in data
    assert "deprecated" in data["error"].lower() or "disabled" in data["error"].lower()
    
    # Verify note is NOT deleted (read-only mode)
    assert db_session.query(Note).filter(Note.id == note_id).first() is not None
    
    # Check metrics tracking
    metrics = get_deprecated_metrics()
    assert metrics["total_calls"] == 1
    assert "DELETE /leads/{domain}/notes/{note_id}" in metrics["calls_by_endpoint"]


def test_create_tag_phase3_disabled(client, test_domain: str):
    """Test creating a tag - Phase 3: Should return 410 Gone."""
    reset_deprecated_metrics()
    response = client.post(f"/leads/{test_domain}/tags", json={"tag": "important"})
    assert response.status_code == 410
    data = response.json()["detail"]
    assert "error" in data
    assert "deprecated" in data["error"].lower() or "disabled" in data["error"].lower()
    
    # Check metrics tracking
    metrics = get_deprecated_metrics()
    assert metrics["total_calls"] == 1
    assert "POST /leads/{domain}/tags" in metrics["calls_by_endpoint"]


def test_list_tags(client, db_session: Session, test_domain: str):
    """Test listing tags."""
    # Create tags first
    tag1 = Tag(domain=test_domain, tag="tag1")
    db_session.add(tag1)
    tag2 = Tag(domain=test_domain, tag="tag2")
    db_session.add(tag2)
    db_session.commit()

    response = client.get(f"/leads/{test_domain}/tags")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {t["tag"] for t in data} == {"tag1", "tag2"}


def test_delete_tag_phase3_disabled(client, db_session: Session, test_domain: str):
    """Test deleting a tag - Phase 3: Should return 410 Gone."""
    # Create a tag first (directly in DB for testing)
    tag = Tag(domain=test_domain, tag="tag-to-delete")
    db_session.add(tag)
    db_session.commit()
    tag_id = tag.id

    reset_deprecated_metrics()
    response = client.delete(f"/leads/{test_domain}/tags/{tag_id}")
    assert response.status_code == 410
    data = response.json()["detail"]
    assert "error" in data
    assert "deprecated" in data["error"].lower() or "disabled" in data["error"].lower()
    
    # Verify tag is NOT deleted (read-only mode)
    assert db_session.query(Tag).filter(Tag.id == tag_id).first() is not None
    
    # Check metrics tracking
    metrics = get_deprecated_metrics()
    assert metrics["total_calls"] == 1
    assert "DELETE /leads/{domain}/tags/{tag_id}" in metrics["calls_by_endpoint"]


def test_add_favorite_phase3_disabled(client, test_domain: str):
    """Test adding a favorite - Phase 3: Should return 410 Gone."""
    reset_deprecated_metrics()
    response = client.post(f"/leads/{test_domain}/favorite")
    assert response.status_code == 410
    data = response.json()["detail"]
    assert "error" in data
    assert "deprecated" in data["error"].lower() or "disabled" in data["error"].lower()
    
    # Check metrics tracking
    metrics = get_deprecated_metrics()
    assert metrics["total_calls"] == 1
    assert "POST /leads/{domain}/favorite" in metrics["calls_by_endpoint"]


def test_list_favorites(client, db_session: Session, test_domain: str):
    """Test listing favorites."""
    # Add a favorite first
    favorite = Favorite(domain=test_domain, user_id="test-user")
    db_session.add(favorite)
    db_session.commit()

    # Note: favorites endpoint uses session-based user_id
    # For testing, we'll need to mock the session
    response = client.get("/leads?favorite=true")
    # This will work if the session cookie is set, otherwise it will return empty
    assert response.status_code == 200


def test_remove_favorite_phase3_disabled(client, db_session: Session, test_domain: str):
    """Test removing a favorite - Phase 3: Should return 410 Gone."""
    # Add a favorite first (directly in DB for testing)
    favorite = Favorite(domain=test_domain, user_id="test-user")
    db_session.add(favorite)
    db_session.commit()
    favorite_id = favorite.id

    reset_deprecated_metrics()
    response = client.delete(f"/leads/{test_domain}/favorite")
    assert response.status_code == 410
    data = response.json()["detail"]
    assert "error" in data
    assert "deprecated" in data["error"].lower() or "disabled" in data["error"].lower()
    
    # Verify favorite is NOT deleted (read-only mode)
    assert db_session.query(Favorite).filter(Favorite.id == favorite_id).first() is not None
    
    # Check metrics tracking
    metrics = get_deprecated_metrics()
    assert metrics["total_calls"] == 1
    assert "DELETE /leads/{domain}/favorite" in metrics["calls_by_endpoint"]


def test_auto_tagging_security_risk(db_session: Session, test_domain: str):
    """Test auto-tagging for security-risk tag."""
    from app.core.auto_tagging import apply_auto_tags

    # Update domain signal to have no SPF and no DKIM
    signal = db_session.query(DomainSignal).filter(DomainSignal.domain == test_domain).first()
    signal.spf = False
    signal.dkim = False
    db_session.commit()

    # Apply auto-tags
    applied_tags = apply_auto_tags(test_domain, db_session)
    db_session.commit()

    assert "security-risk" in applied_tags

    # Verify tag was created
    tag = (
        db_session.query(Tag)
        .filter(Tag.domain == test_domain, Tag.tag == "security-risk")
        .first()
    )
    assert tag is not None


def test_auto_tagging_migration_ready(db_session: Session, test_domain: str):
    """Test auto-tagging for migration-ready tag."""
    from app.core.auto_tagging import apply_auto_tags

    # Domain already has Migration segment and score >= 70
    # Apply auto-tags
    applied_tags = apply_auto_tags(test_domain, db_session)
    db_session.commit()

    assert "migration-ready" in applied_tags

    # Verify tag was created
    tag = (
        db_session.query(Tag)
        .filter(Tag.domain == test_domain, Tag.tag == "migration-ready")
        .first()
    )
    assert tag is not None
