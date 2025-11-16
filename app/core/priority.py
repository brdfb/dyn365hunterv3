"""Priority score calculation for lead prioritization."""

from typing import Optional
from app.core.constants import (
    MIGRATION_READY_SCORE,
    PRIORITY_1_SCORE,
    PRIORITY_2_SCORE,
    PRIORITY_3_MIGRATION_SCORE,
    PRIORITY_4_MIGRATION_SCORE,
    PRIORITY_3_EXISTING_SCORE,
    PRIORITY_4_EXISTING_SCORE,
    PRIORITY_5_EXISTING_SCORE,
    PRIORITY_5_COLD_SCORE,
    PRIORITY_6_COLD_SCORE,
)


def calculate_priority_score(segment: Optional[str], score: Optional[int]) -> int:
    """
    Calculate priority score based on segment and readiness score combination.

    Priority Logic (Improved):
    - Migration + Score 80+ → Priority: 1 🔥 (En yüksek)
    - Migration + Score 70-79 → Priority: 2 ⭐
    - Migration + Score 60-69 → Priority: 3 🟡
    - Migration + Score 0-59 → Priority: 4 🟠 (Note: Migration segment requires min_score 60, so 0-59 is theoretical only)
    - Existing + Score 70+ → Priority: 3 🟡
    - Existing + Score 50-69 → Priority: 4 🟠
    - Existing + Score 30-49 → Priority: 5 ⚪
    - Existing + Score 0-29 → Priority: 6 ⚫
    - Cold + Score 40+ → Priority: 5 ⚪
    - Cold + Score 20-39 → Priority: 6 ⚫
    - Cold + Score 0-19 → Priority: 7 🔴
    - Skip → Priority: 7 🔴 (En düşük)

    Args:
        segment: Lead segment (Migration, Existing, Cold, Skip, or None)
        score: Readiness score (0-100, or None)

    Returns:
        Priority score (1-7), where 1 is highest priority and 7 is lowest
    """
    # Handle None cases
    if segment is None or score is None:
        return 7

    segment = segment.strip() if isinstance(segment, str) else None
    score = int(score) if score is not None else None

    if segment is None or score is None:
        return 7

    # Migration segment (highest priority - even low scores get priority)
    if segment == "Migration":
        if score >= PRIORITY_1_SCORE:
            return 1
        elif score >= PRIORITY_2_SCORE:
            return 2
        elif score >= PRIORITY_3_MIGRATION_SCORE:
            return 3
        else:
            return 4

    # Existing segment
    elif segment == "Existing":
        if score >= PRIORITY_3_EXISTING_SCORE:
            return 3
        elif score >= PRIORITY_4_EXISTING_SCORE:
            return 4
        elif score >= PRIORITY_5_EXISTING_SCORE:
            return 5
        else:
            return 6

    # Cold segment
    elif segment == "Cold":
        if score >= PRIORITY_5_COLD_SCORE:
            return 5
        elif score >= PRIORITY_6_COLD_SCORE:
            return 6
        else:
            return 7

    # Skip segment or any other segment (lowest priority)
    else:
        return 7
