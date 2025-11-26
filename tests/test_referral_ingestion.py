"""Unit tests for Partner Center referral ingestion domain extraction."""

import pytest
from app.core.referral_ingestion import (
    extract_domain_from_referral,
    is_consumer_domain,
    PartnerCenterReferralDTO,
)


class TestDomainExtraction:
    """Test domain extraction from Partner Center referrals."""

    def test_single_contact_email_extracts_domain(self):
        """Test: Single contact email → domain extracted."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "team": [
                    {"email": "john.doe@contoso.com", "name": "John Doe"}
                ]
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "contoso.com"

    def test_multiple_contacts_consumer_and_company_returns_company_domain(self):
        """Test: Multiple contacts; one @gmail, one @company.com → company.com."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "team": [
                    {"email": "personal@gmail.com", "name": "Personal"},
                    {"email": "business@company.com", "name": "Business"},
                ]
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "company.com"

    def test_no_emails_returns_none(self):
        """Test: No emails → None."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "team": [
                    {"name": "John Doe"}  # No email
                ]
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain is None

    def test_consumer_domains_filtered_out(self):
        """Test: Consumer domains → filtered out."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "team": [
                    {"email": "user@gmail.com", "name": "User"},
                ]
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain is None

    def test_all_consumer_domains_filtered_returns_none(self):
        """Test: All consumer domains → None."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "team": [
                    {"email": "user@gmail.com", "name": "User"},
                    {"email": "user@outlook.com", "name": "User2"},
                    {"email": "user@yahoo.com", "name": "User3"},
                ]
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain is None

    def test_customer_profile_ids_external_fallback(self):
        """Test: customerProfile.ids.External fallback works."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "team": [],  # No team emails
                "ids": {
                    "External": "https://example.com"
                }
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "example.com"

    def test_legacy_website_fallback(self):
        """Test: Legacy website fallback works."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "team": [],  # No team emails
            },
            "website": "https://legacy-company.com",
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "legacy-company.com"

    def test_legacy_email_fallback(self):
        """Test: Legacy email fallback works (non-consumer)."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "team": [],  # No team emails
            },
            "contact": {
                "email": "contact@legacy-company.com"
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "legacy-company.com"

    def test_legacy_email_consumer_filtered(self):
        """Test: Legacy email fallback filters consumer domains."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "team": [],  # No team emails
            },
            "contact": {
                "email": "contact@gmail.com"
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain is None

    def test_empty_customer_profile_returns_none(self):
        """Test: Empty customerProfile → None."""
        referral = {
            "id": "ref-123",
            "customerProfile": {},
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain is None

    def test_no_customer_profile_returns_none(self):
        """Test: No customerProfile → None."""
        referral = {
            "id": "ref-123",
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain is None

    def test_team_with_empty_email_skipped(self):
        """Test: Team member with empty email string skipped."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "team": [
                    {"email": "", "name": "John Doe"},
                    {"email": "valid@company.com", "name": "Valid"},
                ]
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "company.com"

    def test_team_with_none_email_skipped(self):
        """Test: Team member with None email skipped."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "team": [
                    {"email": None, "name": "John Doe"},
                    {"email": "valid@company.com", "name": "Valid"},
                ]
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "company.com"

    def test_multiple_company_domains_returns_first(self):
        """Test: Multiple company domains → returns first valid."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "team": [
                    {"email": "user1@company1.com", "name": "User1"},
                    {"email": "user2@company2.com", "name": "User2"},
                ]
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "company1.com"

    def test_team_not_list_handled_gracefully(self):
        """Test: Team not a list → handled gracefully."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "team": "not-a-list",  # Invalid format
            },
            "website": "https://fallback.com",
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "fallback.com"

    def test_team_member_not_dict_handled_gracefully(self):
        """Test: Team member not a dict → handled gracefully."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "team": [
                    "not-a-dict",  # Invalid format
                    {"email": "valid@company.com", "name": "Valid"},
                ]
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "company.com"


class TestConsumerDomainFiltering:
    """Test consumer domain filtering."""

    def test_gmail_is_consumer(self):
        """Test: gmail.com is consumer domain."""
        assert is_consumer_domain("gmail.com") is True

    def test_outlook_is_consumer(self):
        """Test: outlook.com is consumer domain."""
        assert is_consumer_domain("outlook.com") is True

    def test_yahoo_is_consumer(self):
        """Test: yahoo.com is consumer domain."""
        assert is_consumer_domain("yahoo.com") is True

    def test_hotmail_is_consumer(self):
        """Test: hotmail.com is consumer domain."""
        assert is_consumer_domain("hotmail.com") is True

    def test_icloud_is_consumer(self):
        """Test: icloud.com is consumer domain."""
        assert is_consumer_domain("icloud.com") is True

    def test_company_domain_is_not_consumer(self):
        """Test: Company domain is not consumer."""
        assert is_consumer_domain("contoso.com") is False
        assert is_consumer_domain("company.com") is False
        assert is_consumer_domain("example.org") is False

    def test_case_insensitive_consumer_check(self):
        """Test: Consumer domain check is case-insensitive."""
        assert is_consumer_domain("GMAIL.COM") is True
        assert is_consumer_domain("Gmail.Com") is True
        assert is_consumer_domain("gmail.com") is True

    def test_empty_domain_not_consumer(self):
        """Test: Empty domain is not consumer."""
        assert is_consumer_domain("") is False
        assert is_consumer_domain(None) is False

    def test_whitespace_stripped(self):
        """Test: Whitespace is stripped before check."""
        assert is_consumer_domain("  gmail.com  ") is True


class TestPartnerCenterReferralDTO:
    """Test PartnerCenterReferralDTO mapping."""

    def test_dto_from_dict_basic_fields(self):
        """Test: DTO maps basic fields correctly."""
        referral = {
            "id": "ref-123",
            "engagementId": "eng-456",
            "name": "Test Referral",
            "status": "Active",
            "substatus": "Pending",
            "type": "co-sell",
            "qualification": "Qualified",
            "direction": "Incoming",
        }
        
        dto = PartnerCenterReferralDTO.from_dict(referral)
        assert dto.id == "ref-123"
        assert dto.engagement_id == "eng-456"
        assert dto.name == "Test Referral"
        assert dto.status == "Active"
        assert dto.substatus == "Pending"
        assert dto.type == "co-sell"
        assert dto.qualification == "Qualified"
        assert dto.direction == "Incoming"

    def test_dto_from_dict_customer_profile(self):
        """Test: DTO maps customerProfile fields correctly."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "name": "Contoso Inc.",
                "address": {
                    "country": "US",
                },
            },
        }
        
        dto = PartnerCenterReferralDTO.from_dict(referral)
        assert dto.customer_name == "Contoso Inc."
        assert dto.customer_country == "US"
        assert dto.customer_profile is not None

    def test_dto_from_dict_details(self):
        """Test: DTO maps details fields correctly."""
        referral = {
            "id": "ref-123",
            "details": {
                "dealValue": 100000.50,
                "currency": "USD",
            },
        }
        
        dto = PartnerCenterReferralDTO.from_dict(referral)
        assert dto.deal_value == 100000.50
        assert dto.currency == "USD"
        assert dto.details is not None

    def test_dto_from_dict_datetime_parsing(self):
        """Test: DTO parses datetime strings correctly."""
        referral = {
            "id": "ref-123",
            "createdDateTime": "2025-01-30T10:00:00Z",
            "updatedDateTime": "2025-01-30T11:00:00Z",
        }
        
        dto = PartnerCenterReferralDTO.from_dict(referral)
        assert dto.created_date_time is not None
        assert dto.updated_date_time is not None

    def test_dto_from_dict_missing_fields(self):
        """Test: DTO handles missing fields gracefully."""
        referral = {
            "id": "ref-123",
        }
        
        dto = PartnerCenterReferralDTO.from_dict(referral)
        assert dto.id == "ref-123"
        assert dto.engagement_id is None
        assert dto.name is None
        assert dto.customer_profile == {}  # Empty dict when missing
        assert dto.details == {}  # Empty dict when missing

