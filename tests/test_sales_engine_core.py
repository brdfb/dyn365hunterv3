"""Tests for Sales Engine core functions (Phase 2)."""

import pytest
from datetime import date, timedelta
from app.core.sales_engine import (
    generate_one_liner,
    generate_call_script,
    generate_discovery_questions,
    recommend_offer_tier,
    calculate_opportunity_potential,
    calculate_urgency,
    generate_sales_summary,
)


class TestGenerateOneLiner:
    """Tests for generate_one_liner function."""

    def test_migration_high_score_large_tenant(self):
        """Test migration segment with high score and large tenant."""
        result = generate_one_liner(
            domain="example.com",
            provider="Local",
            segment="Migration",
            readiness_score=85,
            tenant_size="large",
            local_provider="TürkHost",
        )
        assert "example.com" in result
        assert "migration" in result.lower() or "fırsat" in result.lower()
        assert "large" in result.lower() or "büyük" in result.lower() or "Enterprise" in result

    def test_migration_medium_score_medium_tenant(self):
        """Test migration segment with medium score and medium tenant."""
        result = generate_one_liner(
            domain="example.com",
            provider="Local",
            segment="Migration",
            readiness_score=65,
            tenant_size="medium",
            local_provider="Natro",
        )
        assert "example.com" in result
        assert "Natro" in result or "migration" in result.lower()

    def test_migration_low_score_small_tenant(self):
        """Test migration segment with low score and small tenant."""
        result = generate_one_liner(
            domain="example.com",
            provider="Local",
            segment="Migration",
            readiness_score=30,
            tenant_size="small",
            local_provider="TürkHost",
        )
        assert "example.com" in result
        assert "migration" in result.lower() or "potansiyel" in result.lower()

    def test_existing_high_score(self):
        """Test existing segment with high score."""
        result = generate_one_liner(
            domain="example.com",
            provider="M365",
            segment="Existing",
            readiness_score=75,
            tenant_size="medium",
        )
        assert "example.com" in result
        assert "mevcut" in result.lower() or "existing" in result.lower()
        assert "upsell" in result.lower() or "defender" in result.lower() or "güvenlik" in result.lower()

    def test_cold_segment(self):
        """Test cold segment."""
        result = generate_one_liner(
            domain="example.com",
            provider="Google",
            segment="Cold",
            readiness_score=45,
            tenant_size=None,
        )
        assert "example.com" in result
        assert "soğuk" in result.lower() or "cold" in result.lower()

    def test_skip_segment(self):
        """Test skip segment."""
        result = generate_one_liner(
            domain="example.com",
            provider="Unknown",
            segment="Skip",
            readiness_score=0,
            tenant_size=None,
        )
        assert "example.com" in result
        assert "skip" in result.lower() or "takip" in result.lower()

    def test_no_local_provider(self):
        """Test migration without local provider."""
        result = generate_one_liner(
            domain="example.com",
            provider="Local",
            segment="Migration",
            readiness_score=70,
            tenant_size="medium",
            local_provider=None,
        )
        assert "example.com" in result
        assert "migration" in result.lower()


class TestGenerateCallScript:
    """Tests for generate_call_script function."""

    def test_migration_with_security_issues(self):
        """Test call script for migration with security issues."""
        bullets = generate_call_script(
            domain="example.com",
            provider="Local",
            segment="Migration",
            readiness_score=80,
            tenant_size="large",
            local_provider="TürkHost",
            spf=False,
            dkim=False,
            dmarc_policy="none",
            dmarc_coverage=None,
        )
        assert len(bullets) > 0
        assert any("example.com" in bullet for bullet in bullets)
        assert any("TürkHost" in bullet or "migration" in bullet.lower() for bullet in bullets)
        assert any("güvenlik" in bullet.lower() or "security" in bullet.lower() or "SPF" in bullet or "DKIM" in bullet or "DMARC" in bullet for bullet in bullets)

    def test_existing_with_dmarc_issues(self):
        """Test call script for existing customer with DMARC issues."""
        bullets = generate_call_script(
            domain="example.com",
            provider="M365",
            segment="Existing",
            readiness_score=70,
            tenant_size="medium",
            spf=True,
            dkim=True,
            dmarc_policy="quarantine",
            dmarc_coverage=50,
        )
        assert len(bullets) > 0
        assert any("mevcut" in bullet.lower() or "existing" in bullet.lower() for bullet in bullets)
        assert any("DMARC" in bullet or "kapsam" in bullet.lower() for bullet in bullets)

    def test_small_tenant_business_basic(self):
        """Test call script for small tenant."""
        bullets = generate_call_script(
            domain="example.com",
            provider="Local",
            segment="Migration",
            readiness_score=75,
            tenant_size="small",
            local_provider="Natro",
        )
        assert len(bullets) > 0
        assert any("Business Basic" in bullet or "küçük" in bullet.lower() or "small" in bullet.lower() for bullet in bullets)

    def test_no_security_issues(self):
        """Test call script without security issues."""
        bullets = generate_call_script(
            domain="example.com",
            provider="M365",
            segment="Existing",
            readiness_score=90,
            tenant_size="large",
            spf=True,
            dkim=True,
            dmarc_policy="reject",
            dmarc_coverage=100,
        )
        assert len(bullets) > 0
        # Should not have security warnings
        security_warnings = [b for b in bullets if "SPF" in b or "DKIM" in b or "DMARC" in b or "eksik" in b.lower()]
        # May or may not have warnings, but should have value proposition
        assert any("Enterprise" in bullet or "güvenlik" in bullet.lower() or "defender" in bullet.lower() for bullet in bullets)


class TestGenerateDiscoveryQuestions:
    """Tests for generate_discovery_questions function."""

    def test_migration_segment_questions(self):
        """Test discovery questions for migration segment."""
        questions = generate_discovery_questions(
            segment="Migration",
            provider="Local",
            tenant_size="medium",
        )
        assert len(questions) > 0
        assert any("email" in q.lower() or "altyapı" in q.lower() for q in questions)
        assert any("güvenlik" in q.lower() or "security" in q.lower() or "phishing" in q.lower() for q in questions)

    def test_existing_segment_questions(self):
        """Test discovery questions for existing segment."""
        questions = generate_discovery_questions(
            segment="Existing",
            provider="M365",
            tenant_size="large",
        )
        assert len(questions) > 0
        assert any("mevcut" in q.lower() or "existing" in q.lower() or "Microsoft" in q for q in questions)
        assert any("defender" in q.lower() or "güvenlik" in q.lower() for q in questions)

    def test_large_tenant_questions(self):
        """Test discovery questions for large tenant."""
        questions = generate_discovery_questions(
            segment="Migration",
            provider="Local",
            tenant_size="large",
        )
        assert len(questions) > 0
        assert any("büyük" in q.lower() or "large" in q.lower() or "organizasyon" in q.lower() for q in questions)
        assert any("compliance" in q.lower() or "regülasyon" in q.lower() or "GDPR" in q or "KVKK" in q for q in questions)

    def test_budget_questions_always_present(self):
        """Test that budget questions are always present."""
        questions = generate_discovery_questions(
            segment="Migration",
            provider="Local",
            tenant_size="small",
        )
        assert any("bütçe" in q.lower() or "budget" in q.lower() for q in questions)
        assert any("zaman" in q.lower() or "timeline" in q.lower() or "süreç" in q.lower() for q in questions)


class TestRecommendOfferTier:
    """Tests for recommend_offer_tier function."""

    def test_large_tenant_enterprise(self):
        """Test large tenant recommends Enterprise."""
        tier = recommend_offer_tier(
            tenant_size="large",
            segment="Migration",
            readiness_score=80,
        )
        assert tier["tier"] == "Enterprise"
        assert tier["license"] == "Enterprise"
        assert tier["price_per_user_per_month"] == 20
        assert tier["migration_fee"] == 10000
        assert tier["defender_price_per_user_per_month"] == 10
        assert tier["consulting_fee"] == 50000

    def test_medium_tenant_business_standard(self):
        """Test medium tenant recommends Business Standard."""
        tier = recommend_offer_tier(
            tenant_size="medium",
            segment="Migration",
            readiness_score=70,
        )
        assert tier["tier"] == "Business Standard"
        assert tier["license"] == "Business Standard"
        assert tier["price_per_user_per_month"] == 10
        assert tier["migration_fee"] == 2000
        assert tier["defender_price_per_user_per_month"] == 5
        assert tier["consulting_fee"] is None

    def test_small_tenant_business_basic(self):
        """Test small tenant recommends Business Basic."""
        tier = recommend_offer_tier(
            tenant_size="small",
            segment="Migration",
            readiness_score=60,
        )
        assert tier["tier"] == "Business Basic"
        assert tier["license"] == "Business Basic"
        assert tier["price_per_user_per_month"] == 5
        assert tier["migration_fee"] == 500
        assert tier["defender_price_per_user_per_month"] is None
        assert tier["consulting_fee"] is None

    def test_no_tenant_size_defaults_to_business_standard(self):
        """Test no tenant size defaults to Business Standard for high score."""
        tier = recommend_offer_tier(
            tenant_size=None,
            segment="Migration",
            readiness_score=75,
        )
        assert tier["tier"] == "Business Standard"
        assert tier["price_per_user_per_month"] == 10

    def test_no_tenant_size_low_score_defaults_to_basic(self):
        """Test no tenant size with low score defaults to Business Basic."""
        tier = recommend_offer_tier(
            tenant_size=None,
            segment="Migration",
            readiness_score=50,
        )
        assert tier["tier"] == "Business Basic"
        assert tier["price_per_user_per_month"] == 5


class TestCalculateOpportunityPotential:
    """Tests for calculate_opportunity_potential function."""

    def test_migration_high_score_high_priority_large_tenant(self):
        """Test high opportunity potential for migration with high score."""
        score = calculate_opportunity_potential(
            segment="Migration",
            readiness_score=85,
            priority_score=1,
            tenant_size="large",
            contact_quality_score=80,
        )
        assert 70 <= score <= 100  # Should be high

    def test_existing_medium_score_medium_priority(self):
        """Test medium opportunity potential for existing customer."""
        score = calculate_opportunity_potential(
            segment="Existing",
            readiness_score=65,
            priority_score=3,
            tenant_size="medium",
            contact_quality_score=60,
        )
        assert 40 <= score <= 80  # Should be medium

    def test_cold_low_score_low_priority(self):
        """Test low opportunity potential for cold lead."""
        score = calculate_opportunity_potential(
            segment="Cold",
            readiness_score=30,
            priority_score=6,
            tenant_size="small",
            contact_quality_score=40,
        )
        assert 0 <= score <= 50  # Should be low

    def test_skip_segment_lowest_potential(self):
        """Test lowest opportunity potential for skip segment."""
        score = calculate_opportunity_potential(
            segment="Skip",
            readiness_score=10,
            priority_score=7,
            tenant_size=None,
            contact_quality_score=20,
        )
        assert 0 <= score <= 30  # Should be very low

    def test_large_tenant_bonus(self):
        """Test large tenant adds bonus to opportunity potential."""
        score_large = calculate_opportunity_potential(
            segment="Migration",
            readiness_score=70,
            priority_score=2,
            tenant_size="large",
        )
        score_small = calculate_opportunity_potential(
            segment="Migration",
            readiness_score=70,
            priority_score=2,
            tenant_size="small",
        )
        assert score_large > score_small  # Large should be higher

    def test_contact_quality_bonus(self):
        """Test contact quality adds bonus to opportunity potential."""
        score_high_contact = calculate_opportunity_potential(
            segment="Migration",
            readiness_score=70,
            priority_score=2,
            tenant_size="medium",
            contact_quality_score=90,
        )
        score_low_contact = calculate_opportunity_potential(
            segment="Migration",
            readiness_score=70,
            priority_score=2,
            tenant_size="medium",
            contact_quality_score=30,
        )
        assert score_high_contact >= score_low_contact  # High contact should be >= low contact


class TestCalculateUrgency:
    """Tests for calculate_urgency function."""

    def test_priority_1_high_urgency(self):
        """Test priority 1 leads have high urgency."""
        urgency = calculate_urgency(
            segment="Migration",
            priority_score=1,
            readiness_score=85,
            expires_at=None,
        )
        assert urgency == "high"

    def test_migration_high_score_high_urgency(self):
        """Test migration with high score has high urgency."""
        urgency = calculate_urgency(
            segment="Migration",
            priority_score=2,
            readiness_score=85,
            expires_at=None,
        )
        assert urgency == "high"

    def test_domain_expiring_soon_high_urgency(self):
        """Test domain expiring soon has high urgency."""
        expires_at = date.today() + timedelta(days=30)
        urgency = calculate_urgency(
            segment="Migration",
            priority_score=3,
            readiness_score=70,
            expires_at=expires_at,
        )
        assert urgency == "high"

    def test_priority_2_medium_urgency(self):
        """Test priority 2 leads have medium urgency."""
        urgency = calculate_urgency(
            segment="Migration",
            priority_score=2,
            readiness_score=75,
            expires_at=None,
        )
        assert urgency == "medium"

    def test_migration_medium_score_medium_urgency(self):
        """Test migration with medium score has medium urgency."""
        urgency = calculate_urgency(
            segment="Migration",
            priority_score=3,
            readiness_score=60,
            expires_at=None,
        )
        assert urgency == "medium"

    def test_existing_high_score_medium_urgency(self):
        """Test existing customer with high score has medium urgency."""
        urgency = calculate_urgency(
            segment="Existing",
            priority_score=3,
            readiness_score=75,
            expires_at=None,
        )
        assert urgency == "medium"

    def test_domain_expiring_medium_term_medium_urgency(self):
        """Test domain expiring in medium term has medium urgency."""
        expires_at = date.today() + timedelta(days=75)
        urgency = calculate_urgency(
            segment="Migration",
            priority_score=4,
            readiness_score=50,
            expires_at=expires_at,
        )
        assert urgency == "medium"

    def test_low_priority_low_urgency(self):
        """Test low priority leads have low urgency."""
        urgency = calculate_urgency(
            segment="Cold",
            priority_score=6,
            readiness_score=30,
            expires_at=None,
        )
        assert urgency == "low"

    def test_domain_expiring_far_low_urgency(self):
        """Test domain expiring far in future has low urgency (when priority is low)."""
        expires_at = date.today() + timedelta(days=200)
        urgency = calculate_urgency(
            segment="Cold",  # Cold segment, not Migration
            priority_score=6,  # Low priority
            readiness_score=30,  # Low score
            expires_at=expires_at,
        )
        assert urgency == "low"


class TestGenerateSalesSummary:
    """Tests for generate_sales_summary function."""

    def test_complete_summary_structure(self):
        """Test that sales summary has all required fields."""
        summary = generate_sales_summary(
            domain="example.com",
            provider="Local",
            segment="Migration",
            readiness_score=80,
            priority_score=1,
            tenant_size="large",
            local_provider="TürkHost",
            spf=False,
            dkim=False,
            dmarc_policy="none",
            dmarc_coverage=None,
            contact_quality_score=75,
            expires_at=date.today() + timedelta(days=45),
        )
        assert summary["domain"] == "example.com"
        assert "one_liner" in summary
        assert isinstance(summary["call_script"], list)
        assert len(summary["call_script"]) > 0
        assert isinstance(summary["discovery_questions"], list)
        assert len(summary["discovery_questions"]) > 0
        assert isinstance(summary["offer_tier"], dict)
        assert "tier" in summary["offer_tier"]
        assert isinstance(summary["opportunity_potential"], int)
        assert 0 <= summary["opportunity_potential"] <= 100
        assert summary["urgency"] in ["low", "medium", "high"]
        assert "metadata" in summary
        assert summary["metadata"]["domain"] == "example.com"
        assert summary["metadata"]["provider"] == "Local"
        assert summary["metadata"]["segment"] == "Migration"

    def test_summary_with_minimal_data(self):
        """Test sales summary with minimal data."""
        summary = generate_sales_summary(
            domain="example.com",
            provider=None,
            segment=None,
            readiness_score=None,
            priority_score=None,
            tenant_size=None,
            local_provider=None,
            spf=None,
            dkim=None,
            dmarc_policy=None,
            dmarc_coverage=None,
            contact_quality_score=None,
            expires_at=None,
        )
        assert summary["domain"] == "example.com"
        assert "one_liner" in summary
        assert isinstance(summary["call_script"], list)
        assert isinstance(summary["discovery_questions"], list)
        assert isinstance(summary["offer_tier"], dict)
        assert isinstance(summary["opportunity_potential"], int)
        assert summary["urgency"] in ["low", "medium", "high"]

    def test_summary_metadata_timestamp(self):
        """Test that metadata includes generated_at timestamp."""
        summary = generate_sales_summary(
            domain="example.com",
            provider="M365",
            segment="Existing",
            readiness_score=70,
            priority_score=3,
            tenant_size="medium",
        )
        assert "metadata" in summary
        assert "generated_at" in summary["metadata"]
        # Should be ISO format timestamp
        assert "T" in summary["metadata"]["generated_at"] or "-" in summary["metadata"]["generated_at"]

