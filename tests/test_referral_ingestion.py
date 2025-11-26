"""Unit tests for Partner Center referral ingestion domain extraction."""

import pytest
from unittest.mock import patch, MagicMock
from app.core.referral_ingestion import (
    extract_domain_from_referral,
    is_consumer_domain,
    PartnerCenterReferralDTO,
    upsert_referral_tracking,
    sync_referrals_from_partner_center,
)
from app.db.models import PartnerCenterReferral, RawLead, Company


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

    def test_url_based_customer_profile_website(self):
        """Test: Phase 3.3 - customerProfile.website → domain extracted."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "website": "https://www.contoso.com",
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "contoso.com"

    def test_url_based_customer_profile_company_website(self):
        """Test: Phase 3.3 - customerProfile.companyWebsite → domain extracted."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "companyWebsite": "http://example.org",
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "example.org"

    def test_url_based_preference_order(self):
        """Test: Phase 3.3 - URL fields checked in preference order (customerProfile.website preferred)."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "website": "https://preferred.com",  # Should be preferred
                "companyWebsite": "https://fallback.com",
            },
            "website": "https://last-resort.com",
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "preferred.com"

    def test_url_based_details_website(self):
        """Test: Phase 3.3 - details.website → domain extracted."""
        referral = {
            "id": "ref-123",
            "details": {
                "website": "https://details.example.com",
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "details.example.com"

    def test_url_based_invalid_domain_filtered(self):
        """Test: Phase 3.3 - Invalid domain from URL filtered out."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "website": "https://invalid",  # Invalid domain (no TLD)
            },
        }
        
        domain = extract_domain_from_referral(referral)
        # Should return None because invalid domain is filtered
        assert domain is None

    def test_url_based_url_with_path(self):
        """Test: Phase 3.3 - URL with path → domain extracted correctly."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "website": "https://www.example.com/path/to/page?query=value",
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "example.com"

    def test_url_based_url_without_scheme(self):
        """Test: Phase 3.3 - URL without scheme → domain extracted correctly."""
        referral = {
            "id": "ref-123",
            "customerProfile": {
                "website": "www.example.com",
            },
        }
        
        domain = extract_domain_from_referral(referral)
        assert domain == "example.com"

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


# Test fixtures for database tests
@pytest.fixture
def db_session():
    """Create a test database session."""
    import os
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.exc import OperationalError
    from app.db.models import Base
    
    TEST_DATABASE_URL = os.getenv(
        "TEST_DATABASE_URL",
        os.getenv(
            "HUNTER_DATABASE_URL",
            os.getenv(
                "DATABASE_URL",
                "postgresql://dyn365hunter:password123@localhost:5432/dyn365hunter",
            ),
        ),
    )
    
    engine = create_engine(TEST_DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
    except OperationalError as e:
        pytest.skip(f"Test database not available: {TEST_DATABASE_URL} - {e}")
    
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        transaction.rollback()
        session.close()
        connection.close()
        engine.dispose()


class TestIngestionFilterRules:
    """Test Phase 4.3: Ingestion Filter Rules."""
    
    def test_direction_outgoing_skipped(self, db_session):
        """Test: direction='Outgoing' → skipped."""
        referral = {
            "id": "ref-123",
            "direction": "Outgoing",
            "status": "Active",
            "substatus": "Pending",
            "customerProfile": {
                "team": [{"email": "user@company.com"}]
            }
        }
        
        with patch("app.core.referral_ingestion.PartnerCenterClient") as mock_client:
            mock_client.return_value.get_referrals.return_value = [referral]
            with patch("app.config.settings") as mock_settings:
                mock_settings.partner_center_enabled = True
                
                result = sync_referrals_from_partner_center(db_session)
                
                assert result["skipped_count"] == 1
                assert result["success_count"] == 0
    
    def test_status_closed_skipped(self, db_session):
        """Test: status='Closed' → skipped."""
        referral = {
            "id": "ref-123",
            "direction": "Incoming",
            "status": "Closed",
            "substatus": "Pending",
            "customerProfile": {
                "team": [{"email": "user@company.com"}]
            }
        }
        
        with patch("app.core.referral_ingestion.PartnerCenterClient") as mock_client:
            mock_client.return_value.get_referrals.return_value = [referral]
            with patch("app.config.settings") as mock_settings:
                mock_settings.partner_center_enabled = True
                
                result = sync_referrals_from_partner_center(db_session)
                
                assert result["skipped_count"] == 1
                assert result["success_count"] == 0
    
    def test_substatus_declined_skipped(self, db_session):
        """Test: substatus='Declined' → skipped."""
        referral = {
            "id": "ref-123",
            "direction": "Incoming",
            "status": "Active",
            "substatus": "Declined",
            "customerProfile": {
                "team": [{"email": "user@company.com"}]
            }
        }
        
        with patch("app.core.referral_ingestion.PartnerCenterClient") as mock_client:
            mock_client.return_value.get_referrals.return_value = [referral]
            with patch("app.config.settings") as mock_settings:
                mock_settings.partner_center_enabled = True
                
                result = sync_referrals_from_partner_center(db_session)
                
                assert result["skipped_count"] == 1
                assert result["success_count"] == 0
    
    def test_valid_referral_processed(self, db_session):
        """Test: Valid referral (Incoming, Active, no excluded substatus) → processed."""
        referral = {
            "id": "ref-123",
            "direction": "Incoming",
            "status": "Active",
            "substatus": "Pending",
            "customerProfile": {
                "team": [{"email": "user@company.com"}],
                "name": "Test Company",
            },
            "details": {
                "dealValue": 10000.50,
                "currency": "USD",
            }
        }
        
        with patch("app.core.referral_ingestion.PartnerCenterClient") as mock_client:
            mock_client.return_value.get_referrals.return_value = [referral]
            with patch("app.config.settings") as mock_settings:
                mock_settings.partner_center_enabled = True
                with patch("app.core.referral_ingestion.upsert_companies") as mock_upsert:
                    mock_upsert.return_value = Company(domain="company.com", id=1)
                    
                    result = sync_referrals_from_partner_center(db_session)
                    
                    assert result["success_count"] == 1
                    assert result["skipped_count"] == 0


class TestUpsertStrategy:
    """Test Phase 4.2: Upsert Strategy."""
    
    def test_upsert_creates_new_referral(self, db_session):
        """Test: New referral → creates record."""
        referral = {
            "id": "ref-123",
            "engagementId": "eng-456",
            "status": "Active",
            "substatus": "Pending",
            "type": "co-sell",
            "qualification": "Qualified",
            "direction": "Incoming",
            "customerProfile": {
                "name": "Test Company",
                "address": {"country": "US"},
            },
            "details": {
                "dealValue": 10000.50,
                "currency": "USD",
            }
        }
        
        result = upsert_referral_tracking(db_session, referral, "company.com")
        
        assert result.referral_id == "ref-123"
        assert result.engagement_id == "eng-456"
        assert result.status == "Active"
        assert result.substatus == "Pending"
        assert result.type == "co-sell"
        assert result.qualification == "Qualified"
        assert result.direction == "Incoming"
        assert result.customer_name == "Test Company"
        assert result.customer_country == "US"
        assert float(result.deal_value) == 10000.50
        assert result.currency == "USD"
        
        # Verify in DB
        db_referral = db_session.query(PartnerCenterReferral).filter(
            PartnerCenterReferral.referral_id == "ref-123"
        ).first()
        assert db_referral is not None
        assert db_referral.status == "Active"
    
    def test_upsert_updates_existing_referral(self, db_session):
        """Test: Existing referral → updates record."""
        # Create initial referral
        initial_referral = PartnerCenterReferral(
            referral_id="ref-123",
            status="New",
            substatus="Pending",
            deal_value=5000.00,
        )
        db_session.add(initial_referral)
        db_session.commit()
        
        # Update referral
        updated_referral = {
            "id": "ref-123",
            "status": "Active",
            "substatus": "Qualified",
            "details": {
                "dealValue": 15000.00,
                "currency": "EUR",
            }
        }
        
        result = upsert_referral_tracking(db_session, updated_referral, "company.com")
        
        assert result.referral_id == "ref-123"
        assert result.status == "Active"  # Updated
        assert result.substatus == "Qualified"  # Updated
        assert float(result.deal_value) == 15000.00  # Updated
        assert result.currency == "EUR"  # Updated
        
        # Verify only one record exists
        count = db_session.query(PartnerCenterReferral).filter(
            PartnerCenterReferral.referral_id == "ref-123"
        ).count()
        assert count == 1


class TestSyncSummaryLogging:
    """Test Phase 5.1: Sync Run Summary Logging."""
    
    def test_sync_summary_logs_all_metrics(self, db_session):
        """Test: partner_center_sync_summary log includes all metrics."""
        import structlog
        from unittest.mock import patch
        
        # Create test referrals
        referrals = [
            {
                "id": "ref-1",
                "direction": "Incoming",
                "status": "Active",
                "substatus": "Pending",
                "customerProfile": {
                    "team": [{"email": "user1@company1.com"}],
                    "name": "Company 1",
                },
            },
            {
                "id": "ref-2",
                "direction": "Outgoing",  # Will be skipped
                "status": "Active",
                "substatus": "Pending",
                "customerProfile": {
                    "team": [{"email": "user2@company2.com"}],
                },
            },
            {
                "id": "ref-3",
                "direction": "Incoming",
                "status": "Closed",  # Will be skipped
                "substatus": "Pending",
                "customerProfile": {
                    "team": [{"email": "user3@company3.com"}],
                },
            },
            {
                "id": "ref-4",
                "direction": "Incoming",
                "status": "Active",
                "substatus": "Declined",  # Will be skipped
                "customerProfile": {
                    "team": [{"email": "user4@company4.com"}],
                },
            },
            {
                "id": "ref-5",
                "direction": "Incoming",
                "status": "Active",
                "substatus": "Pending",
                "customerProfile": {
                    "team": [],  # No domain → will be skipped
                },
            },
        ]
        
        with patch("app.core.referral_ingestion.PartnerCenterClient") as mock_client:
            mock_client.return_value.get_referrals.return_value = referrals
            with patch("app.config.settings") as mock_settings:
                mock_settings.partner_center_enabled = True
                with patch("app.core.referral_ingestion.upsert_companies") as mock_upsert:
                    mock_upsert.return_value = Company(domain="company1.com", id=1)
                    
                    # Capture log calls
                    log_calls = []
                    original_info = structlog.get_logger().info
                    
                    def capture_log(*args, **kwargs):
                        if args and "partner_center_sync_summary" in args[0]:
                            log_calls.append(kwargs)
                        return original_info(*args, **kwargs)
                    
                    with patch("app.core.referral_ingestion.logger.info", side_effect=capture_log):
                        result = sync_referrals_from_partner_center(db_session)
                    
                    # Verify summary log was called
                    assert len(log_calls) > 0
                    summary_log = log_calls[-1]  # Last log should be summary
                    
                    # Verify all metrics are present
                    assert "total_fetched" in summary_log
                    assert "total_processed" in summary_log
                    assert "total_inserted" in summary_log
                    assert "total_skipped" in summary_log
                    assert "skipped_no_domain" in summary_log
                    assert "skipped_duplicate" in summary_log
                    assert "skipped_direction_outgoing" in summary_log
                    assert "skipped_status_closed" in summary_log
                    assert "skipped_substatus_excluded" in summary_log
                    assert "failure_count" in summary_log
                    
                    # Verify metrics match result
                    assert summary_log["total_fetched"] == 5
                    assert summary_log["total_inserted"] == result["success_count"]
                    assert summary_log["total_skipped"] == result["skipped_count"]
                    assert summary_log["skipped_direction_outgoing"] == 1
                    assert summary_log["skipped_status_closed"] == 1
                    assert summary_log["skipped_substatus_excluded"] == 1
                    assert summary_log["skipped_no_domain"] == 1
    
    def test_sync_summary_metrics_accuracy(self, db_session):
        """Test: Summary metrics accurately reflect sync results."""
        referrals = [
            {
                "id": "ref-1",
                "direction": "Incoming",
                "status": "Active",
                "substatus": "Pending",
                "customerProfile": {
                    "team": [{"email": "user@company.com"}],
                },
            },
        ]
        
        with patch("app.core.referral_ingestion.PartnerCenterClient") as mock_client:
            mock_client.return_value.get_referrals.return_value = referrals
            with patch("app.config.settings") as mock_settings:
                mock_settings.partner_center_enabled = True
                with patch("app.core.referral_ingestion.upsert_companies") as mock_upsert:
                    mock_upsert.return_value = Company(domain="company.com", id=1)
                    
                    result = sync_referrals_from_partner_center(db_session)
                    
                    # Verify metrics
                    assert result["success_count"] == 1
                    assert result["skipped_count"] == 0
                    assert result["failure_count"] == 0
                    
                    # Verify DB state
                    db_referral = db_session.query(PartnerCenterReferral).filter(
                        PartnerCenterReferral.referral_id == "ref-1"
                    ).first()
                    assert db_referral is not None
                    assert db_referral.status == "Active"


class TestIntegrationIngestionPipeline:
    """Test Phase 6.2: Integration tests with fake client."""
    
    def test_happy_path_incoming_active_inserted(self, db_session):
        """Test: Happy path - Incoming + Active → inserted."""
        referrals = [
            {
                "id": "ref-happy-1",
                "engagementId": "eng-1",
                "direction": "Incoming",
                "status": "Active",
                "substatus": "Pending",
                "type": "co-sell",
                "qualification": "Qualified",
                "customerProfile": {
                    "name": "Happy Company",
                    "team": [{"email": "user@happy.com"}],
                    "address": {"country": "US"},
                },
                "details": {
                    "dealValue": 50000.00,
                    "currency": "USD",
                },
            },
        ]
        
        with patch("app.core.referral_ingestion.PartnerCenterClient") as mock_client:
            mock_client.return_value.get_referrals.return_value = referrals
            with patch("app.config.settings") as mock_settings:
                mock_settings.partner_center_enabled = True
                with patch("app.core.referral_ingestion.upsert_companies") as mock_upsert:
                    mock_upsert.return_value = Company(domain="happy.com", id=1)
                    
                    result = sync_referrals_from_partner_center(db_session)
                    
                    # Verify success
                    assert result["success_count"] == 1
                    assert result["skipped_count"] == 0
                    
                    # Verify DB records
                    db_referral = db_session.query(PartnerCenterReferral).filter(
                        PartnerCenterReferral.referral_id == "ref-happy-1"
                    ).first()
                    assert db_referral is not None
                    assert db_referral.direction == "Incoming"
                    assert db_referral.status == "Active"
                    assert db_referral.substatus == "Pending"
                    assert db_referral.customer_name == "Happy Company"
                    assert db_referral.customer_country == "US"
                    assert float(db_referral.deal_value) == 50000.00
                    assert db_referral.currency == "USD"
                    
                    # Verify raw_lead created
                    db_raw_lead = db_session.query(RawLead).filter(
                        RawLead.domain == "happy.com"
                    ).first()
                    assert db_raw_lead is not None
                    assert db_raw_lead.source == "partnercenter"
    
    def test_filtered_path_outgoing_skipped(self, db_session):
        """Test: Filtered path - Outgoing → skipped."""
        referrals = [
            {
                "id": "ref-outgoing-1",
                "direction": "Outgoing",
                "status": "Active",
                "substatus": "Pending",
                "customerProfile": {
                    "team": [{"email": "user@outgoing.com"}],
                },
            },
        ]
        
        with patch("app.core.referral_ingestion.PartnerCenterClient") as mock_client:
            mock_client.return_value.get_referrals.return_value = referrals
            with patch("app.config.settings") as mock_settings:
                mock_settings.partner_center_enabled = True
                
                result = sync_referrals_from_partner_center(db_session)
                
                # Verify skipped
                assert result["success_count"] == 0
                assert result["skipped_count"] == 1
                
                # Verify no DB record
                db_referral = db_session.query(PartnerCenterReferral).filter(
                    PartnerCenterReferral.referral_id == "ref-outgoing-1"
                ).first()
                assert db_referral is None
    
    def test_filtered_path_declined_skipped(self, db_session):
        """Test: Filtered path - Declined substatus → skipped."""
        referrals = [
            {
                "id": "ref-declined-1",
                "direction": "Incoming",
                "status": "Active",
                "substatus": "Declined",
                "customerProfile": {
                    "team": [{"email": "user@declined.com"}],
                },
            },
        ]
        
        with patch("app.core.referral_ingestion.PartnerCenterClient") as mock_client:
            mock_client.return_value.get_referrals.return_value = referrals
            with patch("app.config.settings") as mock_settings:
                mock_settings.partner_center_enabled = True
                
                result = sync_referrals_from_partner_center(db_session)
                
                # Verify skipped
                assert result["success_count"] == 0
                assert result["skipped_count"] == 1
                
                # Verify no DB record
                db_referral = db_session.query(PartnerCenterReferral).filter(
                    PartnerCenterReferral.referral_id == "ref-declined-1"
                ).first()
                assert db_referral is None
    
    def test_mixed_referrals_some_inserted_some_skipped(self, db_session):
        """Test: Mixed referrals - some inserted, some skipped."""
        referrals = [
            {
                "id": "ref-valid-1",
                "direction": "Incoming",
                "status": "Active",
                "substatus": "Pending",
                "customerProfile": {
                    "team": [{"email": "user@valid.com"}],
                },
            },
            {
                "id": "ref-outgoing-1",
                "direction": "Outgoing",  # Skip
                "status": "Active",
                "substatus": "Pending",
                "customerProfile": {
                    "team": [{"email": "user@outgoing.com"}],
                },
            },
            {
                "id": "ref-closed-1",
                "direction": "Incoming",
                "status": "Closed",  # Skip
                "substatus": "Pending",
                "customerProfile": {
                    "team": [{"email": "user@closed.com"}],
                },
            },
            {
                "id": "ref-valid-2",
                "direction": "Incoming",
                "status": "New",  # Valid
                "substatus": "Pending",
                "customerProfile": {
                    "team": [{"email": "user@valid2.com"}],
                },
            },
        ]
        
        with patch("app.core.referral_ingestion.PartnerCenterClient") as mock_client:
            mock_client.return_value.get_referrals.return_value = referrals
            with patch("app.config.settings") as mock_settings:
                mock_settings.partner_center_enabled = True
                with patch("app.core.referral_ingestion.upsert_companies") as mock_upsert:
                    mock_upsert.return_value = Company(domain="valid.com", id=1)
                    
                    result = sync_referrals_from_partner_center(db_session)
                    
                    # Verify metrics
                    assert result["success_count"] == 2  # 2 valid referrals
                    assert result["skipped_count"] == 2  # 2 skipped (outgoing + closed)
                    
                    # Verify valid referrals in DB
                    valid_1 = db_session.query(PartnerCenterReferral).filter(
                        PartnerCenterReferral.referral_id == "ref-valid-1"
                    ).first()
                    assert valid_1 is not None
                    
                    valid_2 = db_session.query(PartnerCenterReferral).filter(
                        PartnerCenterReferral.referral_id == "ref-valid-2"
                    ).first()
                    assert valid_2 is not None
                    
                    # Verify skipped referrals not in DB
                    outgoing = db_session.query(PartnerCenterReferral).filter(
                        PartnerCenterReferral.referral_id == "ref-outgoing-1"
                    ).first()
                    assert outgoing is None
                    
                    closed = db_session.query(PartnerCenterReferral).filter(
                        PartnerCenterReferral.referral_id == "ref-closed-1"
                    ).first()
                    assert closed is None

    
    def test_upsert_idempotent_behavior(self, db_session):
        """Test: Re-fetch same referral → updates existing (idempotent)."""
        referral = {
            "id": "ref-123",
            "status": "Active",
            "substatus": "Pending",
            "customerProfile": {
                "team": [{"email": "user@company.com"}]
            }
        }
        
        # First upsert
        result1 = upsert_referral_tracking(db_session, referral, "company.com")
        referral_id_1 = result1.id
        
        # Second upsert (same referral)
        result2 = upsert_referral_tracking(db_session, referral, "company.com")
        referral_id_2 = result2.id
        
        # Should be same record (updated, not new)
        assert referral_id_1 == referral_id_2
        
        # Verify only one record
        count = db_session.query(PartnerCenterReferral).filter(
            PartnerCenterReferral.referral_id == "ref-123"
        ).count()
        assert count == 1

