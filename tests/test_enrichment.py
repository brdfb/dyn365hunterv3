"""Tests for lead enrichment logic."""

import pytest
from app.core.enrichment import (
    calculate_contact_quality_score,
    detect_linkedin_pattern,
    enrich_company_data,
)


def test_calculate_contact_quality_score_no_emails():
    """Test quality score with no emails."""
    score = calculate_contact_quality_score([], "example.com")
    assert score == 0


def test_calculate_contact_quality_score_single_email():
    """Test quality score with single email."""
    score = calculate_contact_quality_score(["john@example.com"], "example.com")
    assert 0 <= score <= 100
    assert score >= 10  # At least base score for 1 email


def test_calculate_contact_quality_score_multiple_emails():
    """Test quality score with multiple emails."""
    emails = ["john@example.com", "jane@example.com", "bob@example.com"]
    score = calculate_contact_quality_score(emails, "example.com")
    assert 0 <= score <= 100
    assert score > 10  # More emails = higher score


def test_calculate_contact_quality_score_domain_match():
    """Test quality score with domain matching emails."""
    emails = [
        "john@example.com",
        "jane@example.com",
        "bob@other.com",  # Different domain
    ]
    score = calculate_contact_quality_score(emails, "example.com")
    assert 0 <= score <= 100
    # Should have bonus for domain matches
    assert score >= 20


def test_calculate_contact_quality_score_many_emails():
    """Test quality score with many emails."""
    emails = [f"user{i}@example.com" for i in range(10)]
    score = calculate_contact_quality_score(emails, "example.com")
    assert score >= 60  # Should get high score for many emails


def test_detect_linkedin_pattern_firstname_lastname():
    """Test LinkedIn pattern detection: firstname.lastname."""
    emails = ["john.doe@example.com", "jane.smith@example.com"]
    pattern = detect_linkedin_pattern(emails)
    assert pattern == "firstname.lastname"


def test_detect_linkedin_pattern_f_lastname():
    """Test LinkedIn pattern detection: f.lastname."""
    emails = ["j.doe@example.com", "j.smith@example.com"]
    pattern = detect_linkedin_pattern(emails)
    assert pattern == "f.lastname"


def test_detect_linkedin_pattern_firstname():
    """Test LinkedIn pattern detection: firstname."""
    emails = ["john@example.com", "jane@example.com"]
    pattern = detect_linkedin_pattern(emails)
    assert pattern == "firstname"


def test_detect_linkedin_pattern_mixed():
    """Test LinkedIn pattern detection with mixed patterns."""
    emails = ["john.doe@example.com", "j.smith@example.com", "bob@example.com"]
    pattern = detect_linkedin_pattern(emails)
    # Should detect the most common pattern
    assert pattern in ["firstname.lastname", "f.lastname", "firstname"]


def test_detect_linkedin_pattern_no_pattern():
    """Test LinkedIn pattern detection with no clear pattern."""
    emails = ["admin@example.com", "info@example.com", "support@example.com"]
    pattern = detect_linkedin_pattern(emails)
    # Generic emails don't match patterns
    assert pattern is None


def test_detect_linkedin_pattern_empty():
    """Test LinkedIn pattern detection with empty list."""
    pattern = detect_linkedin_pattern([])
    assert pattern is None


def test_enrich_company_data():
    """Test full enrichment function."""
    emails = ["john.doe@example.com", "jane.smith@example.com", "bob@example.com"]
    result = enrich_company_data(emails, "example.com")

    assert "contact_emails" in result
    assert "contact_quality_score" in result
    assert "linkedin_pattern" in result

    assert len(result["contact_emails"]) == 3
    assert 0 <= result["contact_quality_score"] <= 100
    assert result["linkedin_pattern"] is not None


def test_enrich_company_data_deduplicates():
    """Test that enrichment deduplicates emails."""
    emails = [
        "john@example.com",
        "JOHN@example.com",  # Duplicate (case-insensitive)
        "jane@example.com",
    ]
    result = enrich_company_data(emails, "example.com")

    assert len(result["contact_emails"]) == 2  # Deduplicated


def test_enrich_company_data_normalizes():
    """Test that enrichment normalizes emails."""
    emails = ["  JOHN@EXAMPLE.COM  ", "jane@example.com"]  # Extra spaces, uppercase
    result = enrich_company_data(emails, "example.com")

    assert all(email.islower() for email in result["contact_emails"])
    assert all("  " not in email for email in result["contact_emails"])


def test_enrich_company_data_filters_invalid():
    """Test that enrichment filters invalid emails."""
    emails = [
        "valid@example.com",
        "",  # Empty
        None,  # None
        "invalid-email",  # No @
        "another@example.com",
    ]
    result = enrich_company_data(emails, "example.com")

    # Should only have valid emails
    assert len(result["contact_emails"]) == 2
    assert "valid@example.com" in result["contact_emails"]
    assert "another@example.com" in result["contact_emails"]
