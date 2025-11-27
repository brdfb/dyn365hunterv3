"""Tests for D365 mapping functions."""

import pytest
from app.integrations.d365.mapping import map_lead_to_d365, _extract_primary_email


def test_map_lead_to_d365_basic():
    """Test basic mapping with minimal data."""
    lead_data = {
        "domain": "example.com",
        "canonical_name": "Example Inc",
    }
    
    result = map_lead_to_d365(lead_data)
    
    assert result["subject"] == "Hunter: example.com"
    assert result["companyname"] == "Example Inc"
    assert result["websiteurl"] == "https://example.com"
    assert "hunter_score" not in result  # None values excluded


def test_map_lead_to_d365_full():
    """Test mapping with all fields."""
    lead_data = {
        "domain": "example.com",
        "canonical_name": "Example Inc",
        "provider": "M365",
        "tenant_size": "large",
        "readiness_score": 85,
        "segment": "Migration",
        "priority_category": "P1",
        "priority_label": "High Potential Greenfield",
        "technical_heat": "Hot",
        "commercial_segment": "GREENFIELD",
        "commercial_heat": "HIGH",
        "contact_emails": ["admin@example.com"],
        "referral_id": "ref-123",
    }
    
    result = map_lead_to_d365(lead_data)
    
    assert result["subject"] == "Hunter: example.com"
    assert result["companyname"] == "Example Inc"
    assert result["websiteurl"] == "https://example.com"
    assert result["emailaddress1"] == "admin@example.com"
    assert result["hunter_score"] == 85
    assert result["hunter_segment"] == "Migration"
    assert result["hunter_priority_category"] == "P1"
    assert result["hunter_priority_label"] == "High Potential Greenfield"
    assert result["hunter_provider"] == "M365"
    assert result["hunter_tenant_size"] == "large"
    assert result["hunter_technical_heat"] == "Hot"
    assert result["hunter_commercial_segment"] == "GREENFIELD"
    assert result["hunter_commercial_heat"] == "HIGH"
    assert result["hunter_referral_id"] == "ref-123"


def test_map_lead_to_d365_missing_domain():
    """Test mapping fails without domain."""
    lead_data = {
        "canonical_name": "Example Inc",
    }
    
    with pytest.raises(ValueError, match="Domain is required"):
        map_lead_to_d365(lead_data)


def test_map_lead_to_d365_none_values_excluded():
    """Test that None values are excluded from payload."""
    lead_data = {
        "domain": "example.com",
        "canonical_name": "Example Inc",
        "readiness_score": None,
        "segment": None,
    }
    
    result = map_lead_to_d365(lead_data)
    
    assert "hunter_score" not in result
    assert "hunter_segment" not in result


def test_extract_primary_email_from_array():
    """Test extracting email from contact_emails array."""
    lead_data = {
        "contact_emails": ["admin@example.com", "info@example.com"],
    }
    
    email = _extract_primary_email(lead_data)
    assert email == "admin@example.com"


def test_extract_primary_email_from_dict_array():
    """Test extracting email from contact_emails array with dicts."""
    lead_data = {
        "contact_emails": [
            {"email": "admin@example.com"},
            {"email": "info@example.com"},
        ],
    }
    
    email = _extract_primary_email(lead_data)
    assert email == "admin@example.com"


def test_extract_primary_email_from_direct_field():
    """Test extracting email from primary_email field."""
    lead_data = {
        "primary_email": "admin@example.com",
    }
    
    email = _extract_primary_email(lead_data)
    assert email == "admin@example.com"


def test_extract_primary_email_not_found():
    """Test extracting email when not available."""
    lead_data = {}
    
    email = _extract_primary_email(lead_data)
    assert email is None

