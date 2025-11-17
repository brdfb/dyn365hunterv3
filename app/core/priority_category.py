"""Priority category (P1-P6) calculation for CSP P-model."""

from typing import Dict, Optional, Tuple
from app.core.scorer import load_rules


def calculate_priority_category(
    technical_heat: str,
    commercial_heat: str,
    commercial_segment: str,
    readiness_score: Optional[int] = None,
) -> Tuple[str, str]:
    """
    Calculate Priority Category (P1-P6) based on technical heat, commercial heat, and commercial segment.
    
    Priority Categories:
    - P1: High Potential Greenfield (Cold + High + GREENFIELD)
    - P2: Competitive Takeover (Warm + High + COMPETITIVE)
    - P3: Existing Microsoft but Weak Partner (Hot + Medium/High + WEAK_PARTNER)
    - P4: Renewal Pressure (Hot + Medium + RENEWAL)
    - P5: Low Intent / Long Nurturing (Cold + Low + LOW_INTENT)
    - P6: No-Go / Archive (Cold + Low + NO_GO)
    
    Args:
        technical_heat: Technical heat (Hot, Warm, Cold)
        commercial_heat: Commercial heat (HIGH, MEDIUM, LOW)
        commercial_segment: Commercial segment (GREENFIELD, COMPETITIVE, etc.)
        readiness_score: Optional readiness score (for future use)
    
    Returns:
        Tuple of (category, label)
        category: P1 | P2 | P3 | P4 | P5 | P6
        label: Human-readable label (e.g., "High Potential Greenfield")
    """
    rules = load_rules()
    priority_category_rules = rules.get("priority_category_rules", [])
    
    # Evaluate rules in order (first match wins)
    for rule in priority_category_rules:
        category = rule.get("category", "")
        label = rule.get("label", "")
        condition = rule.get("condition", {})
        
        # Check technical_heat
        required_heat = condition.get("technical_heat")
        if required_heat is not None and technical_heat != required_heat:
            continue
        
        # Check commercial_heat
        required_commercial_heat = condition.get("commercial_heat")
        if required_commercial_heat is not None and commercial_heat != required_commercial_heat:
            continue
        
        # Check commercial_heat_in (list)
        commercial_heat_in = condition.get("commercial_heat_in")
        if commercial_heat_in is not None:
            if commercial_heat not in commercial_heat_in:
                continue
        
        # Check commercial_segment
        required_segment = condition.get("commercial_segment")
        if required_segment is not None and commercial_segment != required_segment:
            continue
        
        # This rule matches
        return (category, label)
    
    # Default fallback (P6 - No-Go)
    return ("P6", "No-Go / Archive")


def get_priority_label(category: str) -> str:
    """
    Get human-readable label for priority category.
    
    Args:
        category: Priority category (P1, P2, P3, P4, P5, P6)
    
    Returns:
        Human-readable label
    """
    labels = {
        "P1": "High Potential Greenfield",
        "P2": "Competitive Takeover",
        "P3": "Existing Microsoft but Weak Partner",
        "P4": "Renewal Pressure",
        "P5": "Low Intent / Long Nurturing",
        "P6": "No-Go / Archive",
    }
    return labels.get(category, "Unknown")

