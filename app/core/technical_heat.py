"""Technical heat calculation for CSP P-model."""

from typing import Dict, Optional
from app.core.scorer import load_rules


def calculate_technical_heat(
    technical_segment: str,
    provider: str,
    readiness_score: Optional[int] = None,
) -> str:
    """
    Calculate Technical Heat based on technical segment and provider.
    
    Technical Heat Levels:
    - Hot: Zaten M365 kullanıyor, değişime açık
    - Warm: Cloud-to-cloud migration (Google/Zoho/Yandex → EXO)
    - Cold: Self-hosted → cloud migration veya düşük sinyal
    
    Args:
        technical_segment: Technical segment (Migration, Existing, Cold, Skip)
        provider: Provider name (M365, Google, Local, etc.)
        readiness_score: Optional readiness score (for future use)
    
    Returns:
        Technical heat: Hot | Warm | Cold
    """
    rules = load_rules()
    technical_heat_rules = rules.get("technical_heat_rules", [])
    
    # Evaluate rules in order (first match wins)
    for rule in technical_heat_rules:
        heat = rule.get("heat", "")
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
        
        # This rule matches
        return heat
    
    # Default fallback
    return "Cold"

