"""
Golden Dataset Tests - Regression prevention for scoring model.

This test file contains a curated set of domain examples with expected scores,
segments, and priority scores. Any changes to scoring rules should be validated
against this dataset to prevent regressions.

Last Updated: 2025-01-28
"""

import pytest
from app.core.scorer import score_domain
from app.core.priority import calculate_priority_score


# Golden dataset: domain configurations with expected results
GOLDEN_DATASET = [
    {
        "name": "M365 Full (SPF+DKIM+DMARC reject)",
        "domain": "example-m365.com",
        "provider": "M365",
        "signals": {"spf": True, "dkim": True, "dmarc_policy": "reject"},
        "mx_records": ["mail.protection.outlook.com"],
        "expected": {
            "readiness_score": 90,  # 0 base + 50 M365 + 10 SPF + 10 DKIM + 20 DMARC reject
            "segment": "Existing",  # provider_in: ["M365"]
            "priority_score": 3,  # Existing + Score 70+
        },
    },
    {
        "name": "Google Full (SPF+DKIM+DMARC reject)",
        "domain": "example-google.com",
        "provider": "Google",
        "signals": {"spf": True, "dkim": True, "dmarc_policy": "reject"},
        "mx_records": ["aspmx.l.google.com"],
        "expected": {
            "readiness_score": 90,  # 0 base + 50 Google + 10 SPF + 10 DKIM + 20 DMARC reject
            "segment": "Migration",  # min_score 70 + provider_in: ["Google"]
            "priority_score": 1,  # Migration + Score 80+
        },
    },
    {
        "name": "Yandex Full (SPF+DKIM+DMARC reject)",
        "domain": "example-yandex.com",
        "provider": "Yandex",
        "signals": {"spf": True, "dkim": True, "dmarc_policy": "reject"},
        "mx_records": ["mx.yandex.ru"],
        "expected": {
            "readiness_score": 70,  # 0 base + 30 Yandex + 10 SPF + 10 DKIM + 20 DMARC reject
            "segment": "Migration",  # min_score 70 + provider_in: ["Yandex"]
            "priority_score": 2,  # Migration + Score 70-79
        },
    },
    {
        "name": "M365 Partial (SPF only)",
        "domain": "example-m365-partial.com",
        "provider": "M365",
        "signals": {"spf": True, "dkim": False, "dmarc_policy": None},
        "mx_records": ["mail.protection.outlook.com"],
        "expected": {
            "readiness_score": 50,  # 0 base + 50 M365 + 10 SPF - 10 no DKIM (DMARC None has no risk, only "none" has risk)
            "segment": "Existing",  # provider_in: ["M365"]
            "priority_score": 4,  # Existing + Score 50-69
        },
    },
    {
        "name": "Google Partial (SPF only)",
        "domain": "example-google-partial.com",
        "provider": "Google",
        "signals": {"spf": True, "dkim": False, "dmarc_policy": None},
        "mx_records": ["aspmx.l.google.com"],
        "expected": {
            "readiness_score": 50,  # 0 base + 50 Google + 10 SPF - 10 no DKIM (DMARC None has no risk, only "none" has risk)
            "segment": "Cold",  # min_score 40, max_score 69
            "priority_score": 5,  # Cold + Score 40+
        },
    },
    {
        "name": "Google High Score (SPF+DKIM+DMARC quarantine)",
        "domain": "example-google-high.com",
        "provider": "Google",
        "signals": {"spf": True, "dkim": True, "dmarc_policy": "quarantine"},
        "mx_records": ["aspmx.l.google.com"],
        "expected": {
            "readiness_score": 85,  # 0 base + 50 Google + 10 SPF + 10 DKIM + 15 DMARC quarantine
            "segment": "Migration",  # min_score 70 + provider_in: ["Google"]
            "priority_score": 1,  # Migration + Score 80+
        },
    },
    {
        "name": "Hosting Weak (no signals)",
        "domain": "example-hosting-weak.com",
        "provider": "Hosting",
        "signals": {"spf": False, "dkim": False, "dmarc_policy": None},
        "mx_records": ["mail.hosting-provider.com"],
        "expected": {
            "readiness_score": 0,  # 0 base + 20 Hosting - 10 no SPF - 10 no DKIM - 10 hosting_mx_weak (floored at 0)
            "segment": "Skip",  # max_score 39
            "priority_score": 6,  # Skip segment
        },
    },
    {
        "name": "Hosting Good (SPF+DKIM)",
        "domain": "example-hosting-good.com",
        "provider": "Hosting",
        "signals": {"spf": True, "dkim": True, "dmarc_policy": None},
        "mx_records": ["mail.hosting-provider.com"],
        "expected": {
            "readiness_score": 40,  # 0 base + 20 Hosting + 10 SPF + 10 DKIM (DMARC None has no risk, only "none" has risk)
            "segment": "Cold",  # min_score 40, max_score 69 (was Skip, now Cold due to score 40)
            "priority_score": 5,  # Cold + Score 40+
        },
    },
    {
        "name": "Hosting Excellent (SPF+DKIM+DMARC reject)",
        "domain": "example-hosting-excellent.com",
        "provider": "Hosting",
        "signals": {"spf": True, "dkim": True, "dmarc_policy": "reject"},
        "mx_records": ["mail.hosting-provider.com"],
        "expected": {
            "readiness_score": 60,  # 0 base + 20 Hosting + 10 SPF + 10 DKIM + 20 DMARC reject = 60 (Phase 0: Hosting=20)
            "segment": "Cold",  # min_score 40, max_score 69 (score 60 is in Cold range, not Migration)
            "priority_score": 5,  # Cold + Score 40+
        },
    },
    {
        "name": "Local Provider (SPF only)",
        "domain": "example-local.com",
        "provider": "Local",
        "signals": {"spf": True, "dkim": False, "dmarc_policy": None},
        "mx_records": ["mail.local-provider.com"],
        "expected": {
            "readiness_score": 10,  # 0 base + 10 Local + 10 SPF - 10 no DKIM (DMARC None has no risk, only "none" has risk)
            "segment": "Skip",  # max_score 39
            "priority_score": 6,  # Skip segment
        },
    },
    {
        "name": "Local Provider Excellent (SPF+DKIM+DMARC reject)",
        "domain": "example-local-excellent.com",
        "provider": "Local",
        "signals": {"spf": True, "dkim": True, "dmarc_policy": "reject"},
        "mx_records": ["mail.local-provider.com"],
        "expected": {
            "readiness_score": 50,  # 0 base + 10 Local + 10 SPF + 10 DKIM + 20 DMARC reject
            "segment": "Cold",  # min_score 40, max_score 69
            "priority_score": 5,  # Cold + Score 40+
        },
    },
    {
        "name": "MX Missing (hard fail)",
        "domain": "example-nomx.com",
        "provider": "Unknown",
        "signals": {"spf": False, "dkim": False, "dmarc_policy": None},
        "mx_records": None,  # No MX records = hard fail
        "expected": {"readiness_score": 0, "segment": "Skip", "priority_score": 6},
    },
    {
        "name": "M365 with DMARC none",
        "domain": "example-m365-dmarc-none.com",
        "provider": "M365",
        "signals": {"spf": True, "dkim": True, "dmarc_policy": "none"},
        "mx_records": ["mail.protection.outlook.com"],
        "expected": {
            "readiness_score": 60,  # 0 base + 50 M365 + 10 SPF + 10 DKIM + 0 DMARC none (signal) - 10 dmarc_none risk = 60
            "segment": "Existing",
            "priority_score": 4,  # Existing + Score 50-69
        },
    },
    {
        "name": "Existing High Score (M365 + all signals)",
        "domain": "example-existing-high.com",
        "provider": "M365",
        "signals": {"spf": True, "dkim": True, "dmarc_policy": "quarantine"},
        "mx_records": ["mail.protection.outlook.com"],
        "expected": {
            "readiness_score": 85,  # 0 base + 50 M365 + 10 SPF + 10 DKIM + 15 DMARC quarantine
            "segment": "Existing",
            "priority_score": 3,  # Existing + Score 70+
        },
    },
]


class TestGoldenDataset:
    """Test scoring consistency against golden dataset."""

    @pytest.mark.parametrize("test_case", GOLDEN_DATASET)
    def test_golden_dataset_scoring(self, test_case):
        """
        Test that scoring produces expected results for golden dataset.

        This test ensures that any changes to scoring rules don't break
        expected behavior for common domain configurations.
        """
        # Calculate score and segment
        result = score_domain(
            domain=test_case["domain"],
            provider=test_case["provider"],
            signals=test_case["signals"],
            mx_records=test_case["mx_records"],
        )

        # Calculate priority score
        priority_score = calculate_priority_score(result["segment"], result["score"])

        # Assert readiness score
        assert result["score"] == test_case["expected"]["readiness_score"], (
            f"{test_case['name']}: Expected readiness_score {test_case['expected']['readiness_score']}, "
            f"got {result['score']}"
        )

        # Assert segment
        assert result["segment"] == test_case["expected"]["segment"], (
            f"{test_case['name']}: Expected segment {test_case['expected']['segment']}, "
            f"got {result['segment']}"
        )

        # Assert priority score
        assert priority_score == test_case["expected"]["priority_score"], (
            f"{test_case['name']}: Expected priority_score {test_case['expected']['priority_score']}, "
            f"got {priority_score}"
        )

    def test_golden_dataset_priority_ordering(self):
        """
        Test that priority ordering works correctly.

        Migration leads with high scores should have priority 1-2,
        Existing leads should have priority 3-4,
        Cold leads should have priority 5,
        Skip leads should have priority 6.
        """
        # Test Migration high priority
        migration_high = [
            tc
            for tc in GOLDEN_DATASET
            if tc["expected"]["segment"] == "Migration"
            and tc["expected"]["priority_score"] == 1
        ]
        assert len(migration_high) > 0, "Should have Migration leads with priority 1"

        # Test Existing priority
        existing = [
            tc for tc in GOLDEN_DATASET if tc["expected"]["segment"] == "Existing"
        ]
        assert len(existing) > 0, "Should have Existing leads"

        # Verify priority scores are in expected ranges
        for test_case in GOLDEN_DATASET:
            priority = test_case["expected"]["priority_score"]
            segment = test_case["expected"]["segment"]

            if segment == "Migration":
                assert priority in [
                    1,
                    2,
                    6,
                ], f"Migration should have priority 1, 2, or 6, got {priority}"
            elif segment == "Existing":
                assert priority in [
                    3,
                    4,
                    6,
                ], f"Existing should have priority 3, 4, or 6, got {priority}"
            elif segment == "Cold":
                assert priority in [
                    5,
                    6,
                ], f"Cold should have priority 5 or 6, got {priority}"
            elif segment == "Skip":
                assert priority == 6, f"Skip should have priority 6, got {priority}"
