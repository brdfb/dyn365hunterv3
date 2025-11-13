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


def check_hard_fail(
    mx_records: Optional[List[str]],
    domain_signals: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Check hard-fail conditions that force Skip segment.
    
    Hard-fail rules are evaluated before scoring. If any hard-fail
    condition is met, the domain is immediately assigned Skip segment
    with score 0, regardless of other signals.
    
    Args:
        mx_records: List of MX record hostnames (or None/empty list)
        domain_signals: Optional domain signals (for future hard-fail rules)
    
    Returns:
        Reason string if hard-fail condition is met, None otherwise
    """
    rules = load_rules()
    hard_fail_rules = rules.get("hard_fail_rules", [])
    
    # Check each hard-fail rule
    for rule in hard_fail_rules:
        condition = rule.get("condition", "")
        description = rule.get("description", "")
        
        # MX missing check
        if condition == "mx_missing":
            if not mx_records or len(mx_records) == 0:
                return description or "MX kaydı yok"
    
    # Future: domain_valid, parked domain, whois_age checks (Phase 1+)
    
    return None


def calculate_score(
    provider: str,
    signals: Dict[str, Any],
    mx_records: Optional[List[str]] = None
) -> int:
    """
    Calculate readiness score based on provider and signals.
    
    Applies positive points (provider + signals) and negative points (risks).
    Score is floored at 0 and capped at 100.
    
    Args:
        provider: Provider name (e.g., "M365", "Google", "Local")
        signals: Dictionary with signal data:
                 - spf: bool (SPF record exists)
                 - dkim: bool (DKIM record exists)
                 - dmarc_policy: str ("none", "quarantine", "reject", or None)
        mx_records: Optional list of MX records (for risk scoring)
    
    Returns:
        Readiness score (0-100)
    """
    rules = load_rules()
    
    # Start with base score
    score = rules.get("base_score", 0)
    
    # Add provider points
    provider_points = rules.get("provider_points", {})
    score += provider_points.get(provider, 0)
    
    # Add signal points (positive)
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
    
    # Apply risk points (negative)
    risk_points = rules.get("risk_points", {})
    
    # No SPF risk
    if not signals.get("spf"):
        score += risk_points.get("no_spf", 0)
    
    # No DKIM risk
    if not signals.get("dkim"):
        score += risk_points.get("no_dkim", 0)
    
    # DMARC none risk (additional to signal_points)
    if dmarc_policy and dmarc_policy.lower() == "none":
        score += risk_points.get("dmarc_none", 0)
    
    # Hosting MX weak risk (Hosting provider + no SPF + no DKIM)
    if provider == "Hosting" and not signals.get("spf") and not signals.get("dkim"):
        score += risk_points.get("hosting_mx_weak", 0)
    
    # Floor at 0, cap at 100
    return max(0, min(score, 100))


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
    signals: Dict[str, Any],
    mx_records: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Calculate score and determine segment for a domain.
    
    Hard-fail rules are checked first. If any hard-fail condition
    is met, returns Skip segment with score 0 immediately.
    
    Args:
        domain: Domain name (for logging/reference)
        provider: Provider name from classify_provider()
        signals: Dictionary with signal data:
                 - spf: bool
                 - dkim: bool
                 - dmarc_policy: str or None
        mx_records: Optional list of MX record hostnames
    
    Returns:
        Dictionary with:
        - score: int (0-100)
        - segment: str ("Migration", "Existing", "Cold", "Skip")
        - reason: str (human-readable explanation)
    """
    # Check hard-fail conditions FIRST
    # But skip hard-fail check if domain is invalid (already filtered, but double-check)
    from app.core.normalizer import is_valid_domain
    if not is_valid_domain(domain):
        return {
            "score": 0,
            "segment": "Skip",
            "reason": f"Invalid domain format: {domain}"
        }
    
    hard_fail_reason = check_hard_fail(mx_records)
    if hard_fail_reason:
        return {
            "score": 0,
            "segment": "Skip",
            "reason": f"Hard-fail: {hard_fail_reason}"
        }
    
    # Calculate score (includes risk scoring)
    score = calculate_score(provider, signals, mx_records)
    
    # Determine segment
    segment, reason = determine_segment(score, provider)
    
    return {
        "score": score,
        "segment": segment,
        "reason": reason
    }

