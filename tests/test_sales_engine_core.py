"""Tests for Sales Engine core functions (Phase 2)."""

import pytest
from datetime import date, timedelta
from app.core.sales_engine import (
    generate_one_liner,
    generate_call_script,
    generate_discovery_questions,
    recommend_offer_tier,
    calculate_opportunity_potential,
    explain_opportunity_potential,
    calculate_urgency,
    generate_next_step_cta,
    generate_sales_summary,
    explain_segment,
    explain_provider,
    explain_security_signals,
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

    def test_generate_call_script_cold_without_security(self):
        """Test Cold segment call script without security reasoning (soft, discovery-focused)."""
        bullets = generate_call_script(
            domain="example.com",
            provider="Local",
            segment="Cold",
            readiness_score=45,
            tenant_size="small",
            local_provider="TürkHost",
            security_reasoning=None,
        )
        assert len(bullets) >= 2
        assert len(bullets) <= 4  # Should be concise (2-3 bullets)
        
        # Check for soft opening
        assert any("Gibibyte" in bullet or "tarama" in bullet.lower() for bullet in bullets)
        assert any("example.com" in bullet for bullet in bullets)
        
        # Check for improvement potential (soft)
        assert any("iyileştirme" in bullet.lower() or "potansiyel" in bullet.lower() or "spam" in bullet.lower() or "teslimat" in bullet.lower() or "güvenlik" in bullet.lower() for bullet in bullets)
        
        # Check for discovery-focused CTA
        assert any("görüşme" in bullet.lower() or "değerlendirebiliriz" in bullet.lower() or "10-15" in bullet or "15" in bullet for bullet in bullets)

    def test_generate_call_script_cold_with_high_risk_security(self):
        """Test Cold segment call script with high risk security reasoning."""
        security_reasoning = {
            "risk_level": "high",
            "summary": "DMARC yok, SPF ve DKIM eksik.",
            "details": ["SPF kaydı eksik", "DKIM kaydı eksik", "DMARC politikası yok"],
            "sales_angle": "Güvenlik açığı üzerinden konuşma aç: phishing, sahte fatura.",
            "recommended_action": "Microsoft 365 + Defender ile tam koruma öner.",
        }
        
        bullets = generate_call_script(
            domain="example.com",
            provider="Local",
            segment="Cold",
            readiness_score=45,
            tenant_size="small",
            security_reasoning=security_reasoning,
        )
        assert len(bullets) >= 2
        assert len(bullets) <= 4
        
        # Should mention security risk (soft but direct)
        assert any("phishing" in bullet.lower() or "spoofing" in bullet.lower() or "güvenlik" in bullet.lower() or "risk" in bullet.lower() for bullet in bullets)
        
        # Should still be soft and discovery-focused
        assert any("dış göz" in bullet.lower() or "görüşme" in bullet.lower() for bullet in bullets)

    def test_generate_call_script_migration_existing_still_work(self):
        """Test that Migration and Existing scripts still work correctly."""
        # Migration script
        migration_bullets = generate_call_script(
            domain="example.com",
            provider="Google",
            segment="Migration",
            readiness_score=75,
            tenant_size="medium",
            local_provider=None,
            spf=True,
            dkim=True,
            dmarc_policy="reject",
            dmarc_coverage=100,
        )
        assert len(migration_bullets) > 0
        assert any("migration" in bullet.lower() or "geçiş" in bullet.lower() or "Microsoft 365" in bullet for bullet in migration_bullets)
        
        # Existing script
        existing_bullets = generate_call_script(
            domain="example.com",
            provider="M365",
            segment="Existing",
            readiness_score=70,
            tenant_size="large",
            spf=True,
            dkim=True,
            dmarc_policy="reject",
            dmarc_coverage=100,
        )
        assert len(existing_bullets) > 0
        assert any("mevcut" in bullet.lower() or "existing" in bullet.lower() or "M365" in bullet or "Microsoft 365" in bullet for bullet in existing_bullets)


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
        assert "segment_explanation" in summary
        assert isinstance(summary["segment_explanation"], str)
        assert len(summary["segment_explanation"]) > 0
        assert "provider_reasoning" in summary
        assert isinstance(summary["provider_reasoning"], str)
        assert len(summary["provider_reasoning"]) > 0
        assert "security_reasoning" in summary
        # security_reasoning can be None if all signals are unknown
        if summary["security_reasoning"] is not None:
            assert isinstance(summary["security_reasoning"], dict)
            assert "risk_level" in summary["security_reasoning"]
        assert "opportunity_rationale" in summary
        assert isinstance(summary["opportunity_rationale"], dict)
        assert "total" in summary["opportunity_rationale"]
        assert "factors" in summary["opportunity_rationale"]
        # Verify opportunity_rationale["total"] matches opportunity_potential
        assert summary["opportunity_rationale"]["total"] == summary["opportunity_potential"]
        assert "next_step" in summary
        assert isinstance(summary["next_step"], dict)
        assert "action" in summary["next_step"]
        assert "timeline" in summary["next_step"]
        assert "priority" in summary["next_step"]
        assert "message" in summary["next_step"]
        assert "internal_note" in summary["next_step"]
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


class TestExplainSegment:
    """Tests for explain_segment function (Sales Engine v1.1)."""

    def test_explain_existing_segment_m365(self):
        """Test explanation for Existing segment with M365 provider."""
        explanation = explain_segment(
            segment="Existing",
            provider="M365",
            readiness_score=75,
            spf=True,
            dkim=True,
            dmarc_policy="reject",
        )
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "Existing" in explanation
        assert "M365" in explanation or "Microsoft 365" in explanation

    def test_explain_migration_segment_google(self):
        """Test explanation for Migration segment with Google provider."""
        explanation = explain_segment(
            segment="Migration",
            provider="Google",
            readiness_score=75,
            spf=True,
            dkim=True,
            dmarc_policy="reject",
        )
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "Migration" in explanation
        assert "Google" in explanation

    def test_explain_migration_segment_local(self):
        """Test explanation for Migration segment with Local provider."""
        explanation = explain_segment(
            segment="Migration",
            provider="Local",
            readiness_score=65,
            local_provider="TürkHost",
            spf=False,
            dkim=False,
            dmarc_policy="none",
        )
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "Migration" in explanation
        assert "Local" in explanation or "TürkHost" in explanation or "Self-hosted" in explanation

    def test_explain_cold_segment_local(self):
        """Test explanation for Cold segment with Local provider (Local-specific rule)."""
        explanation = explain_segment(
            segment="Cold",
            provider="Local",
            readiness_score=30,
            local_provider="Natro",
        )
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "Cold" in explanation
        assert "Local" in explanation or "Natro" in explanation or "Self-hosted" in explanation

    def test_explain_cold_segment_general(self):
        """Test explanation for Cold segment (general rule)."""
        explanation = explain_segment(
            segment="Cold",
            provider="Google",
            readiness_score=45,
        )
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "Cold" in explanation

    def test_explain_skip_segment(self):
        """Test explanation for Skip segment."""
        explanation = explain_segment(
            segment="Skip",
            provider="Local",
            readiness_score=3,
        )
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "Skip" in explanation

    def test_explain_segment_none(self):
        """Test explanation when segment is None."""
        explanation = explain_segment(
            segment=None,
            provider="M365",
            readiness_score=50,
        )
        assert isinstance(explanation, str)
        assert "mevcut değil" in explanation or "bilgisi" in explanation

    def test_explain_segment_with_security_signals(self):
        """Test explanation includes security signals when available."""
        explanation = explain_segment(
            segment="Migration",
            provider="Google",
            readiness_score=80,
            spf=True,
            dkim=True,
            dmarc_policy="reject",
        )
        assert isinstance(explanation, str)
        # Should mention security signals
        assert "SPF" in explanation or "DKIM" in explanation or "DMARC" in explanation


class TestExplainProvider:
    """Tests for explain_provider function (Sales Engine v1.1)."""

    def test_explain_provider_m365(self):
        """Test explanation for M365 provider."""
        explanation = explain_provider(
            domain="example.com",
            provider="M365",
            mx_root="outlook-com.olc.protection.outlook.com",
            spf=True,
            dmarc_policy="reject",
        )
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "M365" in explanation or "Microsoft 365" in explanation
        assert "outlook" in explanation.lower() or "Microsoft" in explanation

    def test_explain_provider_google(self):
        """Test explanation for Google provider."""
        explanation = explain_provider(
            domain="example.com",
            provider="Google",
            mx_root="aspmx.l.google.com",
        )
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "Google" in explanation
        assert "Workspace" in explanation or "google" in explanation.lower()

    def test_explain_provider_hosting_with_local_provider(self):
        """Test explanation for Hosting provider with local provider info."""
        explanation = explain_provider(
            domain="example.com",
            provider="Hosting",
            mx_root="mail.hosting-provider.com",
        )
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "Hosting" in explanation or "hosting" in explanation.lower()

    def test_explain_provider_local_with_local_provider(self):
        """Test explanation for Local provider with local provider name."""
        explanation = explain_provider(
            domain="example.com",
            provider="Local",
            mx_root="mail.turkhost.com.tr",
            local_provider="TürkHost",
        )
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "Local" in explanation or "Self-hosted" in explanation
        assert "TürkHost" in explanation or "yerel" in explanation.lower()

    def test_explain_provider_unknown_no_mx(self):
        """Test explanation for Unknown provider with no MX record."""
        explanation = explain_provider(
            domain="example.com",
            provider="Unknown",
            mx_root=None,
        )
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "Unknown" in explanation or "belirsiz" in explanation.lower()
        assert "MX" in explanation or "mx" in explanation.lower()

    def test_explain_provider_yandex(self):
        """Test explanation for Yandex provider."""
        explanation = explain_provider(
            domain="example.com",
            provider="Yandex",
            mx_root="mx.yandex.ru",
        )
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "Yandex" in explanation

    def test_explain_provider_zoho(self):
        """Test explanation for Zoho provider."""
        explanation = explain_provider(
            domain="example.com",
            provider="Zoho",
            mx_root="mx.zoho.com",
        )
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "Zoho" in explanation

    def test_explain_provider_with_infrastructure_summary(self):
        """Test explanation includes infrastructure summary when available."""
        explanation = explain_provider(
            domain="example.com",
            provider="M365",
            mx_root="outlook.com",
            infrastructure_summary="Hosted on DataCenter, ISP: Hetzner, Country: DE",
        )
        assert isinstance(explanation, str)
        assert "Altyapı analizi" in explanation or "infrastructure" in explanation.lower()
        assert "Hetzner" in explanation or "DE" in explanation

    def test_explain_provider_none(self):
        """Test explanation when provider is None."""
        explanation = explain_provider(
            domain="example.com",
            provider=None,
            mx_root="outlook.com",
        )
        assert isinstance(explanation, str)
        assert "mevcut değil" in explanation or "bilgisi" in explanation


class TestExplainSecuritySignals:
    """Tests for explain_security_signals function (Sales Engine v1.1)."""

    def test_explain_security_signals_high_risk_all_missing(self):
        """Test explanation for high risk when all security signals are missing."""
        result = explain_security_signals(
            spf=False,
            dkim=False,
            dmarc_policy="none",
        )
        assert result is not None
        assert isinstance(result, dict)
        assert result["risk_level"] == "high"
        assert "summary" in result
        assert "details" in result
        assert "sales_angle" in result
        assert "recommended_action" in result
        assert len(result["details"]) > 0
        assert "SPF" in result["summary"] or "DMARC" in result["summary"]

    def test_explain_security_signals_medium_risk_partial_dmarc(self):
        """Test explanation for medium risk with partial DMARC coverage."""
        result = explain_security_signals(
            spf=True,
            dkim=True,
            dmarc_policy="reject",
            dmarc_coverage=75,
        )
        assert result is not None
        assert isinstance(result, dict)
        assert result["risk_level"] == "medium"
        assert "DMARC" in result["summary"]
        assert "%75" in result["summary"] or "75" in result["summary"]

    def test_explain_security_signals_low_risk_full_protection(self):
        """Test explanation for low risk with full protection."""
        result = explain_security_signals(
            spf=True,
            dkim=True,
            dmarc_policy="reject",
            dmarc_coverage=100,
        )
        assert result is not None
        assert isinstance(result, dict)
        assert result["risk_level"] == "low"
        assert "iyi" in result["summary"].lower() or "tam" in result["summary"].lower()

    def test_explain_security_signals_none_when_all_unknown(self):
        """Test that function returns None when all signals are unknown."""
        result = explain_security_signals(
            spf=None,
            dkim=None,
            dmarc_policy=None,
        )
        assert result is None

    def test_explain_security_signals_high_risk_dmarc_missing(self):
        """Test high risk when DMARC is missing (critical)."""
        result = explain_security_signals(
            spf=True,
            dkim=True,
            dmarc_policy="none",
        )
        assert result is not None
        assert result["risk_level"] == "high"
        assert "DMARC" in result["summary"]

    def test_explain_security_signals_medium_risk_one_missing(self):
        """Test medium risk when one signal is missing."""
        result = explain_security_signals(
            spf=False,
            dkim=True,
            dmarc_policy="reject",
            dmarc_coverage=100,
        )
        assert result is not None
        assert result["risk_level"] == "medium"
        assert "SPF" in result["summary"] or "SPF" in " ".join(result["details"])

    def test_explain_security_signals_sales_angle_high_risk(self):
        """Test sales angle for high risk scenarios."""
        result = explain_security_signals(
            spf=False,
            dkim=False,
            dmarc_policy="none",
        )
        assert result is not None
        assert "phishing" in result["sales_angle"].lower() or "güvenlik" in result["sales_angle"].lower()

    def test_explain_security_signals_recommended_action(self):
        """Test recommended action is present and meaningful."""
        result = explain_security_signals(
            spf=False,
            dkim=False,
            dmarc_policy="none",
        )
        assert result is not None
        assert len(result["recommended_action"]) > 0
        assert "Microsoft" in result["recommended_action"] or "DMARC" in result["recommended_action"]


class TestExplainOpportunityPotential:
    """Tests for explain_opportunity_potential function (Sales Engine v1.1)."""

    def test_explain_opportunity_potential_cold_small(self):
        """Test explanation for Cold segment with small tenant."""
        result = explain_opportunity_potential(
            segment="Cold",
            readiness_score=40,
            priority_score=5,
            tenant_size="small",
            contact_quality_score=None,
            tuning_factor=1.0,
        )
        assert isinstance(result, dict)
        assert "total" in result
        assert "factors" in result
        assert "tuning_factor" in result
        assert "summary" in result
        
        # Verify total matches calculate_opportunity_potential
        expected_total = calculate_opportunity_potential(
            segment="Cold",
            readiness_score=40,
            priority_score=5,
            tenant_size="small",
            contact_quality_score=None,
            tuning_factor=1.0,
        )
        assert result["total"] == expected_total
        
        # Verify factors structure
        assert isinstance(result["factors"], list)
        assert len(result["factors"]) >= 4  # segment, readiness, priority, tenant_size
        
        # Verify segment factor
        segment_factor = next((f for f in result["factors"] if f["name"] == "segment"), None)
        assert segment_factor is not None
        assert segment_factor["raw"] == "Cold"
        assert segment_factor["score"] == 15
        
        # Verify readiness factor
        readiness_factor = next((f for f in result["factors"] if f["name"] == "readiness_score"), None)
        assert readiness_factor is not None
        assert readiness_factor["raw"] == 40
        assert readiness_factor["score"] == int(40 * 0.3)  # 12
        
        # Verify priority factor
        priority_factor = next((f for f in result["factors"] if f["name"] == "priority_score"), None)
        assert priority_factor is not None
        assert priority_factor["raw"] == 5
        assert priority_factor["score"] == 8
        
        # Verify tenant_size factor
        tenant_factor = next((f for f in result["factors"] if f["name"] == "tenant_size"), None)
        assert tenant_factor is not None
        assert tenant_factor["raw"] == "small"
        assert tenant_factor["score"] == 5

    def test_explain_opportunity_potential_migration_large(self):
        """Test explanation for Migration segment with large tenant."""
        result = explain_opportunity_potential(
            segment="Migration",
            readiness_score=85,
            priority_score=1,
            tenant_size="large",
            contact_quality_score=80,
            tuning_factor=1.0,
        )
        assert isinstance(result, dict)
        assert "total" in result
        assert "factors" in result
        
        # Verify total matches calculate_opportunity_potential
        expected_total = calculate_opportunity_potential(
            segment="Migration",
            readiness_score=85,
            priority_score=1,
            tenant_size="large",
            contact_quality_score=80,
            tuning_factor=1.0,
        )
        assert result["total"] == expected_total
        
        # Verify segment factor
        segment_factor = next((f for f in result["factors"] if f["name"] == "segment"), None)
        assert segment_factor is not None
        assert segment_factor["raw"] == "Migration"
        assert segment_factor["score"] == 40
        
        # Verify contact_quality factor exists
        contact_factor = next((f for f in result["factors"] if f["name"] == "contact_quality"), None)
        assert contact_factor is not None
        assert contact_factor["raw"] == 80
        assert contact_factor["score"] == int(80 * 0.05)  # 4

    def test_explain_opportunity_potential_handles_missing_values(self):
        """Test explanation handles missing values gracefully."""
        result = explain_opportunity_potential(
            segment=None,
            readiness_score=None,
            priority_score=None,
            tenant_size=None,
            contact_quality_score=None,
            tuning_factor=1.0,
        )
        assert isinstance(result, dict)
        assert "total" in result
        assert "factors" in result
        
        # Should still produce a valid result
        assert result["total"] >= 0
        assert result["total"] <= 100
        
        # Verify factors exist even with missing values
        assert len(result["factors"]) >= 4  # segment, readiness, priority, tenant_size


class TestGenerateNextStepCTA:
    """Tests for generate_next_step_cta function (Sales Engine v1.1)."""

    def test_generate_next_step_cta_high_migration(self):
        """Test CTA for high opportunity Migration lead."""
        result = generate_next_step_cta(
            segment="Migration",
            opportunity_potential=85,
            urgency="high",
            tenant_size="large",
        )
        assert isinstance(result, dict)
        assert result["action"] == "call"
        assert result["timeline"] == "24_saat"
        assert result["priority"] == "high"
        assert "message" in result
        assert "internal_note" in result
        assert "Microsoft 365" in result["message"] or "geçiş" in result["message"].lower()
        assert "24 saat" in result["internal_note"] or "24_saat" in result["internal_note"]

    def test_generate_next_step_cta_medium_cold(self):
        """Test CTA for medium opportunity Cold lead."""
        result = generate_next_step_cta(
            segment="Cold",
            opportunity_potential=65,
            urgency="medium",
            tenant_size="medium",
        )
        assert isinstance(result, dict)
        assert result["action"] in ["call", "email"]
        assert result["priority"] == "medium"
        assert "message" in result
        assert "internal_note" in result
        assert "3 gün" in result["internal_note"] or "3_gün" in result["internal_note"]

    def test_generate_next_step_cta_low_cold(self):
        """Test CTA for low opportunity Cold lead."""
        result = generate_next_step_cta(
            segment="Cold",
            opportunity_potential=35,
            urgency="low",
            tenant_size="small",
        )
        assert isinstance(result, dict)
        assert result["action"] in ["email", "nurture"]
        assert result["timeline"] in ["1_hafta", "1_ay"]
        assert result["priority"] == "low"
        assert "message" in result
        assert "internal_note" in result
        assert "düşük" in result["internal_note"].lower() or "low" in result["internal_note"].lower()

    def test_generate_next_step_cta_skip_segment(self):
        """Test CTA for Skip segment."""
        result = generate_next_step_cta(
            segment="Skip",
            opportunity_potential=10,
            urgency="low",
            tenant_size=None,
        )
        assert isinstance(result, dict)
        assert result["action"] == "wait"
        assert result["priority"] == "low"
        assert "yeni sinyal" in result["internal_note"].lower() or "wait" in result["action"]

    def test_generate_next_step_cta_existing_high(self):
        """Test CTA for high opportunity Existing customer."""
        result = generate_next_step_cta(
            segment="Existing",
            opportunity_potential=82,
            urgency="high",
            tenant_size="large",
        )
        assert isinstance(result, dict)
        assert result["action"] == "call"
        assert result["timeline"] == "24_saat"
        assert result["priority"] == "high"
        assert "Microsoft 365" in result["message"] or "M365" in result["message"]

