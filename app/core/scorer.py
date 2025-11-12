"""Rule-based scoring engine."""
import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


_RULES_CACHE: Optional[Dict] = None


def load_rules() -> Dict:
    """
    Load scoring rules from rules.json.
    
    Returns:
        Dictionary with 'base_score', 'provider_points', 'signal_points', 'segment_rules'
        
    Raises:
        FileNotFoundError: If rules.json not found
        json.JSONDecodeError: If JSON is invalid
    """
    global _RULES_CACHE
    
    if _RULES_CACHE is not None:
        return _RULES_CACHE
    
    # Get the path to rules.json
    current_dir = Path(__file__).parent.parent
    rules_path = current_dir / "data" / "rules.json"
    
    if not rules_path.exists():
        raise FileNotFoundError(f"rules.json not found at {rules_path}")
    
    with open(rules_path, 'r', encoding='utf-8') as f:
        _RULES_CACHE = json.load(f)
    
    return _RULES_CACHE


def calculate_score(
    provider: str,
    signals: Dict[str, Any]
) -> int:
    """
    Calculate readiness score based on provider and signals.
    
    Args:
        provider: Provider name (e.g., "M365", "Google", "Local")
        signals: Dictionary with signal data:
                 - spf: bool (SPF record exists)
                 - dkim: bool (DKIM record exists)
                 - dmarc_policy: str ("none", "quarantine", "reject", or None)
    
    Returns:
        Readiness score (0-100)
    """
    rules = load_rules()
    
    # Start with base score
    score = rules.get("base_score", 0)
    
    # Add provider points
    provider_points = rules.get("provider_points", {})
    score += provider_points.get(provider, 0)
    
    # Add signal points
    signal_points = rules.get("signal_points", {})
    
    # SPF
    if signals.get("spf"):
        score += signal_points.get("spf", 0)
    
    # DKIM
    if signals.get("dkim"):
        score += signal_points.get("dkim", 0)
    
    # DMARC
    dmarc_policy = signals.get("dmarc_policy")
    if dmarc_policy:
        dmarc_policy_lower = dmarc_policy.lower()
        if dmarc_policy_lower == "quarantine":
            score += signal_points.get("dmarc_quarantine", 0)
        elif dmarc_policy_lower == "reject":
            score += signal_points.get("dmarc_reject", 0)
        elif dmarc_policy_lower == "none":
            score += signal_points.get("dmarc_none", 0)
    
    # Cap score at 100
    return min(score, 100)


def determine_segment(score: int, provider: str) -> Tuple[str, str]:
    """
    Determine segment based on score and provider.
    
    Segment rules are evaluated in order (top to bottom).
    First matching rule wins.
    
    Args:
        score: Calculated readiness score (0-100)
        provider: Provider name
    
    Returns:
        Tuple of (segment, reason)
        segment: "Migration", "Existing", "Cold", or "Skip"
        reason: Human-readable explanation
    """
    rules = load_rules()
    segment_rules = rules.get("segment_rules", [])
    
    # Evaluate rules in order
    for rule in segment_rules:
        segment = rule.get("segment", "")
        condition = rule.get("condition", {})
        description = rule.get("description", "")
        
        # Check min_score
        min_score = condition.get("min_score")
        if min_score is not None and score < min_score:
            continue
        
        # Check max_score
        max_score = condition.get("max_score")
        if max_score is not None and score > max_score:
            continue
        
        # Check provider_in
        provider_in = condition.get("provider_in")
        if provider_in is not None:
            if provider not in provider_in:
                continue
        
        # This rule matches
        reason = f"{description}. Score: {score}, Provider: {provider}"
        return (segment, reason)
    
    # Default fallback (should not happen if rules are complete)
    return ("Skip", f"Score {score} with provider {provider} did not match any segment rule")


def score_domain(
    domain: str,
    provider: str,
    signals: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate score and determine segment for a domain.
    
    Args:
        domain: Domain name (for logging/reference)
        provider: Provider name from classify_provider()
        signals: Dictionary with signal data:
                 - spf: bool
                 - dkim: bool
                 - dmarc_policy: str or None
    
    Returns:
        Dictionary with:
        - score: int (0-100)
        - segment: str ("Migration", "Existing", "Cold", "Skip")
        - reason: str (human-readable explanation)
    """
    # Calculate score
    score = calculate_score(provider, signals)
    
    # Determine segment
    segment, reason = determine_segment(score, provider)
    
    return {
        "score": score,
        "segment": segment,
        "reason": reason
    }

