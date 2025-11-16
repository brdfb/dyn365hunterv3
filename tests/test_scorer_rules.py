"""Tests for scoring rules and segment logic."""

import pytest
from app.core.scorer import (
    calculate_score,
    determine_segment,
    score_domain,
    load_rules,
    check_hard_fail,
)
from app.core.provider_map import classify_provider, load_providers


class TestScoringRules:
    """Test scoring rule calculations."""

    def test_load_rules(self):
        """Test loading rules from JSON."""
        rules = load_rules()

        assert "base_score" in rules
        assert "provider_points" in rules
        assert "signal_points" in rules
        assert "segment_rules" in rules

    def test_calculate_score_base(self):
        """Test base score calculation."""
        signals = {"spf": False, "dkim": False, "dmarc_policy": None}
        score = calculate_score("Unknown", signals)

        rules = load_rules()
        base_score = rules.get("base_score", 0)

        assert score == base_score

    def test_calculate_score_with_provider(self):
        """Test score calculation with provider points."""
        signals = {"spf": False, "dkim": False, "dmarc_policy": None}
        score_m365 = calculate_score("M365", signals)
        score_unknown = calculate_score("Unknown", signals)

        # M365 should have higher score than Unknown
        assert score_m365 > score_unknown

    def test_calculate_score_with_spf(self):
        """Test score calculation with SPF signal."""
        signals_no_spf = {"spf": False, "dkim": False, "dmarc_policy": None}
        signals_with_spf = {"spf": True, "dkim": False, "dmarc_policy": None}

        score_no_spf = calculate_score("M365", signals_no_spf)
        score_with_spf = calculate_score("M365", signals_with_spf)

        assert score_with_spf > score_no_spf

    def test_calculate_score_with_dkim(self):
        """Test score calculation with DKIM signal."""
        signals_no_dkim = {"spf": False, "dkim": False, "dmarc_policy": None}
        signals_with_dkim = {"spf": False, "dkim": True, "dmarc_policy": None}

        score_no_dkim = calculate_score("M365", signals_no_dkim)
        score_with_dkim = calculate_score("M365", signals_with_dkim)

        assert score_with_dkim > score_no_dkim

    def test_calculate_score_with_dmarc_reject(self):
        """Test score calculation with DMARC reject policy."""
        signals_none = {"spf": False, "dkim": False, "dmarc_policy": None}
        signals_reject = {"spf": False, "dkim": False, "dmarc_policy": "reject"}

        score_none = calculate_score("M365", signals_none)
        score_reject = calculate_score("M365", signals_reject)

        assert score_reject > score_none

    def test_calculate_score_capped_at_100(self):
        """Test that score is capped at 100."""
        signals = {"spf": True, "dkim": True, "dmarc_policy": "reject"}
        score = calculate_score("M365", signals)

        assert score <= 100


class TestSegmentLogic:
    """Test segment determination logic."""

    def test_determine_segment_existing(self):
        """Test Existing segment determination."""
        # M365 should always be Existing (regardless of score)
        segment, reason = determine_segment(85, "M365")

        # Segment should be Existing
        assert segment == "Existing"
        assert len(reason) > 0  # Reason should not be empty

        # Even low score M365 should be Existing
        segment2, _ = determine_segment(10, "M365")
        assert segment2 == "Existing"

    def test_determine_segment_migration(self):
        """Test Migration segment determination."""
        # High score with Google should be Migration
        segment, reason = determine_segment(75, "Google")

        # Segment should be Migration (reason content may vary)
        assert segment == "Migration"
        assert len(reason) > 0  # Reason should not be empty

    def test_determine_segment_cold(self):
        """Test Cold segment determination."""
        # Score 40-69 should be Cold
        segment, reason = determine_segment(50, "Unknown")

        assert segment == "Cold"

        # Score 40 should be Cold
        segment2, _ = determine_segment(40, "Unknown")
        assert segment2 == "Cold"

        # Score 69 should be Cold
        segment3, _ = determine_segment(69, "Unknown")
        assert segment3 == "Cold"

    def test_determine_segment_skip(self):
        """Test Skip segment determination."""
        # Score <40 should be Skip
        segment, reason = determine_segment(20, "Unknown")

        assert segment == "Skip"

        # Score 39 should be Skip
        segment2, _ = determine_segment(39, "Unknown")
        assert segment2 == "Skip"

    def test_segment_rules_order_matters(self):
        """Test that segment rules are evaluated in order."""
        # M365 should be Existing (first rule), not Migration
        segment1, _ = determine_segment(75, "M365")
        assert segment1 == "Existing"

        # Google with high score should be Migration
        segment2, _ = determine_segment(75, "Google")
        assert segment2 == "Migration"

        # Order matters: Existing is checked before Migration
        # So M365 never becomes Migration even with high score


class TestScoreDomain:
    """Test complete domain scoring."""

    def test_score_domain_complete(self):
        """Test complete domain scoring with all signals."""
        signals = {"spf": True, "dkim": True, "dmarc_policy": "reject"}

        result = score_domain("example.com", "M365", signals)

        assert "score" in result
        assert "segment" in result
        assert "reason" in result
        assert 0 <= result["score"] <= 100
        assert result["segment"] in ["Migration", "Existing", "Cold", "Skip"]

    def test_score_domain_minimal_signals(self):
        """Test domain scoring with minimal signals."""
        signals = {"spf": False, "dkim": False, "dmarc_policy": None}

        result = score_domain("example.com", "Unknown", signals)

        assert result["score"] >= 0
        assert result["segment"] in ["Migration", "Existing", "Cold", "Skip"]


class TestProviderMapping:
    """Test provider classification."""

    def test_load_providers(self):
        """Test loading providers from JSON."""
        providers = load_providers()

        assert "providers" in providers
        assert len(providers["providers"]) > 0

    def test_classify_provider_m365(self):
        """Test M365 provider classification."""
        provider = classify_provider("outlook-com.olc.protection.outlook.com")

        assert provider == "M365"

    def test_classify_provider_google(self):
        """Test Google provider classification."""
        provider = classify_provider("aspmx.l.google.com")

        assert provider == "Google"

    def test_classify_provider_unknown(self):
        """Test Unknown provider classification."""
        provider = classify_provider(None)

        assert provider == "Unknown"

    def test_classify_provider_local(self):
        """Test Local provider classification."""
        provider = classify_provider("mail.example.com")

        # Should be Local if not matching any known provider
        assert provider in ["Local", "Unknown"]


class TestScorerEdgeCases:
    """Test edge cases for scorer."""

    def test_calculate_score_missing_mx(self):
        """Test scoring when MX is missing."""
        signals = {"spf": False, "dkim": False, "dmarc_policy": None}
        score = calculate_score("Unknown", signals)

        # Should still calculate a score
        assert score >= 0

    def test_determine_segment_fallback(self):
        """Test segment determination fallback."""
        # Very unusual score/provider combination
        segment, reason = determine_segment(999, "UnknownProvider")

        # Should return a valid segment (likely "Skip")
        assert segment in ["Migration", "Existing", "Cold", "Skip"]
        assert "Skip" in reason or segment == "Skip"


class TestHardFailRules:
    """Test hard-fail rules that force Skip segment."""

    def test_hard_fail_mx_missing(self):
        """Test hard-fail when MX records are missing."""
        result = score_domain(
            domain="example.com",
            provider="Unknown",
            signals={"spf": False, "dkim": False, "dmarc_policy": None},
            mx_records=[],  # No MX records
        )
        assert result["segment"] == "Skip"
        assert "Hard-fail" in result["reason"]
        assert result["score"] == 0

    def test_hard_fail_mx_none(self):
        """Test hard-fail when mx_records is None."""
        result = score_domain(
            domain="example.com",
            provider="Unknown",
            signals={"spf": False, "dkim": False, "dmarc_policy": None},
            mx_records=None,  # None instead of empty list
        )
        assert result["segment"] == "Skip"
        assert "Hard-fail" in result["reason"]
        assert result["score"] == 0

    def test_check_hard_fail_function(self):
        """Test check_hard_fail() function directly."""
        # MX missing
        reason = check_hard_fail([])
        assert reason is not None
        assert "MX" in reason or "mx" in reason.lower()

        # MX present
        reason = check_hard_fail(["mail.example.com"])
        assert reason is None


class TestRiskScoring:
    """Test risk scoring (negative points)."""

    def test_risk_scoring_no_spf(self):
        """Test risk scoring when SPF is missing."""
        # Provider: Local (10 points)
        # No SPF: -10 risk
        # Expected: 10 - 10 = 0
        result = score_domain(
            domain="example.com",
            provider="Local",
            signals={"spf": False, "dkim": False, "dmarc_policy": None},
            mx_records=["mail.example.com"],
        )
        assert result["score"] == 0  # 10 (Local) - 10 (no_spf) = 0

    def test_risk_scoring_no_dkim(self):
        """Test risk scoring when DKIM is missing."""
        # Provider: Local (10 points)
        # SPF present: +10
        # No DKIM: -10 risk (no_dkim)
        # DKIM none: -5 risk (dkim_none) - Additional penalty (G18: Enhanced scoring)
        # Expected: 10 + 10 - 10 - 5 = 5
        result = score_domain(
            domain="example.com",
            provider="Local",
            signals={"spf": True, "dkim": False, "dmarc_policy": None},
            mx_records=["mail.example.com"],
        )
        assert result["score"] == 5  # 10 (Local) + 10 (SPF) - 10 (no_dkim) - 5 (dkim_none) = 5

    def test_risk_scoring_dmarc_none(self):
        """Test risk scoring when DMARC policy is 'none'."""
        # Provider: Local (10 points)
        # SPF present: +10
        # DKIM present: +10
        # DMARC none: -10 risk (in addition to signal_points which is 0)
        # Expected: 10 + 10 + 10 - 10 = 20
        result = score_domain(
            domain="example.com",
            provider="Local",
            signals={"spf": True, "dkim": True, "dmarc_policy": "none"},
            mx_records=["mail.example.com"],
        )
        assert result["score"] == 20  # 10 + 10 + 10 - 10 = 20

    def test_risk_scoring_hosting_mx_weak(self):
        """Test risk scoring for weak hosting MX."""
        # Provider: Hosting (20 points)
        # No SPF: -10 risk
        # No DKIM: -10 risk
        # Hosting MX weak: -10 risk
        # Expected: 20 - 10 - 10 - 10 = -10 → 0 (floored)
        result = score_domain(
            domain="example.com",
            provider="Hosting",
            signals={"spf": False, "dkim": False, "dmarc_policy": None},
            mx_records=["mail.hosting.com"],
        )
        assert result["score"] == 0  # 20 - 10 - 10 - 10 = -10 → 0

    def test_risk_scoring_hosting_with_spf(self):
        """Test that hosting_mx_weak risk doesn't apply if SPF exists."""
        # Provider: Hosting (20 points)
        # SPF present: +10
        # No DKIM: -10 risk (no_dkim)
        # DKIM none: -5 risk (dkim_none) - Additional penalty (G18: Enhanced scoring)
        # Hosting MX weak: NOT applied (SPF exists)
        # Expected: 20 + 10 - 10 - 5 = 15
        result = score_domain(
            domain="example.com",
            provider="Hosting",
            signals={"spf": True, "dkim": False, "dmarc_policy": None},
            mx_records=["mail.hosting.com"],
        )
        assert result["score"] == 15  # 20 + 10 - 10 (no_dkim) - 5 (dkim_none) = 15


class TestProviderPointsUpdate:
    """Test updated provider points."""

    def test_provider_points_hosting_updated(self):
        """Test that Hosting provider points are updated to 20."""
        rules = load_rules()
        provider_points = rules.get("provider_points", {})
        assert provider_points.get("Hosting") == 20

    def test_provider_points_local_updated(self):
        """Test that Local provider points are updated to 10."""
        rules = load_rules()
        provider_points = rules.get("provider_points", {})
        assert provider_points.get("Local") == 10

    def test_provider_points_hosting_scoring(self):
        """Test scoring with updated Hosting provider points."""
        # Provider: Hosting (20 points)
        # SPF present: +10
        # DKIM present: +10
        # DMARC reject: +20
        # Expected: 20 + 10 + 10 + 20 = 60
        result = score_domain(
            domain="example.com",
            provider="Hosting",
            signals={"spf": True, "dkim": True, "dmarc_policy": "reject"},
            mx_records=["mail.hosting.com"],
        )
        assert result["score"] == 60

    def test_provider_points_local_scoring(self):
        """Test scoring with updated Local provider points."""
        # Provider: Local (10 points)
        # SPF present: +10
        # DKIM present: +10
        # Expected: 10 + 10 + 10 = 30
        result = score_domain(
            domain="example.com",
            provider="Local",
            signals={"spf": True, "dkim": True, "dmarc_policy": None},
            mx_records=["mail.example.com"],
        )
        assert result["score"] == 30
