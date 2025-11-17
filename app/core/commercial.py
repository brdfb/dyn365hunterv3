"""Commercial segment and heat calculation for CSP P-model."""

from typing import Dict, Optional, Any
from app.core.scorer import load_rules


def calculate_commercial_segment(
    technical_segment: str,
    provider: str,
    readiness_score: int,
    tenant_size: Optional[str] = None,
) -> str:
    """
    Calculate Commercial Segment based on technical segment, provider, and score.
    
    Commercial Segments:
    - GREENFIELD: Self-hosted → M365 migration
    - COMPETITIVE: Cloud-to-cloud migration (Google/Zoho/Yandex → EXO)
    - WEAK_PARTNER: M365 var ama partner zayıf
    - RENEWAL: M365 var, partner güçlü, renewal/upsell
    - LOW_INTENT: Düşük sinyal, uzun nurturing
    - NO_GO: Arşiv, arama yok
    
    Args:
        technical_segment: Technical segment (Migration, Existing, Cold, Skip)
        provider: Provider name (M365, Google, Local, etc.)
        readiness_score: Readiness score (0-100)
        tenant_size: Optional tenant size (small, medium, large)
    
    Returns:
        Commercial segment: GREENFIELD | COMPETITIVE | WEAK_PARTNER | RENEWAL | LOW_INTENT | NO_GO
    """
    rules = load_rules()
    commercial_segment_rules = rules.get("commercial_segment_rules", [])
    
    # Evaluate rules in order (first match wins)
    for rule in commercial_segment_rules:
        segment = rule.get("segment", "")
        condition = rule.get("condition", {})
        
        # Check technical_segment
        required_segment = condition.get("technical_segment")
        if required_segment is not None and technical_segment != required_segment:
            continue
        
        # Check provider_in
        provider_in = condition.get("provider_in")
        if provider_in is not None:
            if provider not in provider_in:
                continue
        
        # Check min_score
        min_score = condition.get("min_score")
        if min_score is not None and readiness_score < min_score:
            continue
        
        # Check max_score
        max_score = condition.get("max_score")
        if max_score is not None and readiness_score > max_score:
            continue
        
        # This rule matches
        return segment
    
    # Default fallback (should not happen if rules are complete)
    return "NO_GO"


def calculate_commercial_heat(
    commercial_segment: str,
    readiness_score: int,
    tenant_size: Optional[str] = None,
) -> str:
    """
    Calculate Commercial Heat based on commercial segment and additional factors.
    
    Commercial Heat Levels:
    - HIGH: Hemen aksiyon (48 saat - 3 gün)
    - MEDIUM: Soft nurturing (5 gün - 2 hafta)
    - LOW: Uzun nurturing veya arşiv
    
    Args:
        commercial_segment: Commercial segment (GREENFIELD, COMPETITIVE, etc.)
        readiness_score: Readiness score (0-100)
        tenant_size: Optional tenant size (small, medium, large)
    
    Returns:
        Commercial heat: HIGH | MEDIUM | LOW
    """
    rules = load_rules()
    commercial_heat_rules = rules.get("commercial_heat_rules", [])
    
    # Evaluate rules in order (first match wins)
    for rule in commercial_heat_rules:
        heat = rule.get("heat", "")
        condition = rule.get("condition", {})
        
        # Check commercial_segment
        required_segment = condition.get("commercial_segment")
        if required_segment is not None and commercial_segment != required_segment:
            continue
        
        # Check commercial_segment_in (list)
        segment_in = condition.get("commercial_segment_in")
        if segment_in is not None:
            if commercial_segment not in segment_in:
                continue
        
        # Check min_score
        min_score = condition.get("min_score")
        if min_score is not None and readiness_score < min_score:
            continue
        
        # Check max_score
        max_score = condition.get("max_score")
        if max_score is not None and readiness_score > max_score:
            continue
        
        # This rule matches
        return heat
    
    # Default fallback
    return "LOW"

