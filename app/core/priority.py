"""Priority score calculation for lead prioritization."""
from typing import Optional


def calculate_priority_score(segment: Optional[str], score: Optional[int]) -> int:
    """
    Calculate priority score based on segment and readiness score combination.
    
    Priority Logic:
    - Migration + Score 80+ → Priority: 1 (En yüksek)
    - Migration + Score 70-79 → Priority: 2
    - Existing + Score 70+ → Priority: 3
    - Existing + Score 50-69 → Priority: 4
    - Cold + Score 40+ → Priority: 5
    - Diğerleri → Priority: 6
    
    Args:
        segment: Lead segment (Migration, Existing, Cold, Skip, or None)
        score: Readiness score (0-100, or None)
        
    Returns:
        Priority score (1-6), where 1 is highest priority and 6 is lowest
    """
    # Handle None cases
    if segment is None or score is None:
        return 6
    
    segment = segment.strip() if isinstance(segment, str) else None
    score = int(score) if score is not None else None
    
    if segment is None or score is None:
        return 6
    
    # Migration segment
    if segment == "Migration":
        if score >= 80:
            return 1
        elif score >= 70:
            return 2
        else:
            return 6
    
    # Existing segment
    elif segment == "Existing":
        if score >= 70:
            return 3
        elif score >= 50:
            return 4
        else:
            return 6
    
    # Cold segment
    elif segment == "Cold":
        if score >= 40:
            return 5
        else:
            return 6
    
    # Skip segment or any other segment
    else:
        return 6

