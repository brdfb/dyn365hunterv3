"""Tests for priority score calculation."""

import pytest
from app.core.priority import calculate_priority_score


class TestPriorityScore:
    """Test priority score calculation logic."""

    def test_priority_migration_high_score(self):
        """Test Migration segment with high score (80+)."""
        assert calculate_priority_score("Migration", 85) == 1
        assert calculate_priority_score("Migration", 100) == 1

    def test_priority_migration_medium_score(self):
        """Test Migration segment with medium score (70-79)."""
        assert calculate_priority_score("Migration", 75) == 2
        assert calculate_priority_score("Migration", 70) == 2

    def test_priority_migration_low_score(self):
        """Test Migration segment with low score (60-69)."""
        # Migration 60-69 → Priority 3 (Migration segment min_score = 60)
        assert calculate_priority_score("Migration", 69) == 3
        assert calculate_priority_score("Migration", 60) == 3
        # Migration 0-59 → Priority 4 (theoretical only, Migration segment requires min_score 60)
        assert calculate_priority_score("Migration", 59) == 4
        assert calculate_priority_score("Migration", 0) == 4

    def test_priority_existing_high_score(self):
        """Test Existing segment with high score (70+)."""
        assert calculate_priority_score("Existing", 80) == 3
        assert calculate_priority_score("Existing", 70) == 3

    def test_priority_existing_medium_score(self):
        """Test Existing segment with medium score (50-69)."""
        assert calculate_priority_score("Existing", 60) == 4
        assert calculate_priority_score("Existing", 50) == 4

    def test_priority_existing_low_score(self):
        """Test Existing segment with low score (<50)."""
        # Existing 30-49 → Priority 5
        assert calculate_priority_score("Existing", 40) == 5
        assert calculate_priority_score("Existing", 30) == 5
        # Existing 0-29 → Priority 6
        assert calculate_priority_score("Existing", 29) == 6
        assert calculate_priority_score("Existing", 0) == 6

    def test_priority_cold_high_score(self):
        """Test Cold segment with high score (40+)."""
        assert calculate_priority_score("Cold", 50) == 5
        assert calculate_priority_score("Cold", 40) == 5

    def test_priority_cold_low_score(self):
        """Test Cold segment with low score (<40)."""
        # Cold 20-39 → Priority 6
        assert calculate_priority_score("Cold", 30) == 6
        assert calculate_priority_score("Cold", 20) == 6
        # Cold 0-19 → Priority 7
        assert calculate_priority_score("Cold", 19) == 7
        assert calculate_priority_score("Cold", 0) == 7

    def test_priority_skip_segment(self):
        """Test Skip segment (always lowest priority)."""
        assert calculate_priority_score("Skip", 100) == 7
        assert calculate_priority_score("Skip", 0) == 7

    def test_priority_none_values(self):
        """Test None values (should return 7)."""
        assert calculate_priority_score(None, 80) == 7
        assert calculate_priority_score("Migration", None) == 7
        assert calculate_priority_score(None, None) == 7

    def test_priority_unknown_segment(self):
        """Test unknown segment (should return 7)."""
        assert calculate_priority_score("Unknown", 80) == 7
        assert calculate_priority_score("", 80) == 7
