"""Score breakdown calculation for detailed score analysis (G19)."""

from typing import Dict, Any, Optional, List
from app.core.scorer import load_rules


class ScoreBreakdown:
    """Score breakdown components."""

    def __init__(self):
        self.base_score: int = 0
        self.provider_points: int = 0
        self.provider_name: Optional[str] = None
        self.signal_points: Dict[str, int] = {}
        self.risk_points: Dict[str, int] = {}
        self.total_score: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "base_score": self.base_score,
            "provider": {
                "name": self.provider_name,
                "points": self.provider_points,
            },
            "signal_points": self.signal_points,
            "risk_points": self.risk_points,
            "total_score": self.total_score,
        }


def calculate_score_breakdown(
    provider: str, signals: Dict[str, Any], mx_records: Optional[List[str]] = None
) -> ScoreBreakdown:
    """
    Calculate detailed score breakdown.

    Args:
        provider: Provider name (e.g., "M365", "Google", "Local")
        signals: Dictionary with signal data:
                 - spf: bool (SPF record exists)
                 - dkim: bool (DKIM record exists)
                 - dmarc_policy: str ("none", "quarantine", "reject", or None)
                 - spf_record: Optional[str] (full SPF record for risk analysis)
        mx_records: Optional list of MX records (for risk scoring)

    Returns:
        ScoreBreakdown with detailed components
    """
    rules = load_rules()
    breakdown = ScoreBreakdown()

    # Base score
    breakdown.base_score = rules.get("base_score", 0)

    # Provider points
    provider_points = rules.get("provider_points", {})
    breakdown.provider_points = provider_points.get(provider, 0)
    breakdown.provider_name = provider

    # Signal points (positive)
    signal_points = rules.get("signal_points", {})

    # SPF
    if signals.get("spf"):
        breakdown.signal_points["spf"] = signal_points.get("spf", 0)

    # DKIM
    if signals.get("dkim"):
        breakdown.signal_points["dkim"] = signal_points.get("dkim", 0)

    # DMARC
    dmarc_policy = signals.get("dmarc_policy")
    if dmarc_policy:
        dmarc_policy_lower = dmarc_policy.lower()
        if dmarc_policy_lower == "quarantine":
            breakdown.signal_points["dmarc_quarantine"] = signal_points.get(
                "dmarc_quarantine", 0
            )
        elif dmarc_policy_lower == "reject":
            breakdown.signal_points["dmarc_reject"] = signal_points.get(
                "dmarc_reject", 0
            )
        elif dmarc_policy_lower == "none":
            breakdown.signal_points["dmarc_none"] = signal_points.get(
                "dmarc_none", 0
            )

    # Risk points (negative)
    risk_points = rules.get("risk_points", {})

    # No SPF risk
    if not signals.get("spf"):
        breakdown.risk_points["no_spf"] = risk_points.get("no_spf", 0)

    # No DKIM risk
    if not signals.get("dkim"):
        breakdown.risk_points["no_dkim"] = risk_points.get("no_dkim", 0)
        # Additional penalty for DKIM none
        breakdown.risk_points["dkim_none"] = risk_points.get("dkim_none", 0)

    # DMARC none risk (additional to signal_points)
    if dmarc_policy and dmarc_policy.lower() == "none":
        breakdown.risk_points["dmarc_none"] = risk_points.get("dmarc_none", 0)

    # Hosting MX weak risk
    if provider == "Hosting" and not signals.get("spf") and not signals.get("dkim"):
        breakdown.risk_points["hosting_mx_weak"] = risk_points.get(
            "hosting_mx_weak", 0
        )

    # SPF multiple includes risk
    spf_record = signals.get("spf_record")
    if spf_record and isinstance(spf_record, str):
        include_count = spf_record.count("include:")
        if include_count > 3:
            breakdown.risk_points["spf_multiple_includes"] = risk_points.get(
                "spf_multiple_includes", 0
            )

    # Calculate total score
    breakdown.total_score = (
        breakdown.base_score
        + breakdown.provider_points
        + sum(breakdown.signal_points.values())
        + sum(breakdown.risk_points.values())
    )

    # Floor at 0, cap at 100
    breakdown.total_score = max(0, min(breakdown.total_score, 100))

    return breakdown

