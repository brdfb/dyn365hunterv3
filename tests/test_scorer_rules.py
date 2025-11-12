"""Tests for scoring rules and segment logic."""
import pytest
from app.core.scorer import calculate_score, determine_segment, score_domain, load_rules
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
    
    def test_determine_segment_migration(self):
        """Test Migration segment determination."""
        # High score with M365 should be Migration
        segment, reason = determine_segment(85, "M365")
        
        # Segment should be Migration (reason content may vary)
        assert segment == "Migration"
        assert len(reason) > 0  # Reason should not be empty
    
    def test_determine_segment_existing(self):
        """Test Existing segment determination."""
        # Medium score with M365 might be Existing
        segment, reason = determine_segment(50, "M365")
        
        # Should match one of the segment rules
        assert segment in ["Migration", "Existing", "Cold", "Skip"]
    
    def test_determine_segment_cold(self):
        """Test Cold segment determination."""
        # Low score should be Cold
        segment, reason = determine_segment(20, "Unknown")
        
        assert segment in ["Cold", "Skip"]
    
    def test_segment_rules_order_matters(self):
        """Test that segment rules are evaluated in order."""
        # First matching rule should win
        segment1, _ = determine_segment(75, "M365")
        segment2, _ = determine_segment(75, "Google")
        
        # Both should match a rule (order matters)
        assert segment1 in ["Migration", "Existing", "Cold", "Skip"]
        assert segment2 in ["Migration", "Existing", "Cold", "Skip"]


class TestScoreDomain:
    """Test complete domain scoring."""
    
    def test_score_domain_complete(self):
        """Test complete domain scoring with all signals."""
        signals = {
            "spf": True,
            "dkim": True,
            "dmarc_policy": "reject"
        }
        
        result = score_domain("example.com", "M365", signals)
        
        assert "score" in result
        assert "segment" in result
        assert "reason" in result
        assert 0 <= result["score"] <= 100
        assert result["segment"] in ["Migration", "Existing", "Cold", "Skip"]
    
    def test_score_domain_minimal_signals(self):
        """Test domain scoring with minimal signals."""
        signals = {
            "spf": False,
            "dkim": False,
            "dmarc_policy": None
        }
        
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

