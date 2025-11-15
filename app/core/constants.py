"""Business logic constants and thresholds."""

# Priority & Migration Score Thresholds
MIGRATION_READY_SCORE = 70  # Migration segment + score >= 70
HIGH_PRIORITY_SCORE = 70  # Migration + score >= 70 (for dashboard)

# Priority Score Thresholds
PRIORITY_1_SCORE = 80  # Migration + score >= 80 → Priority: 1
PRIORITY_2_SCORE = 70  # Migration + score >= 70 → Priority: 2
PRIORITY_3_MIGRATION_SCORE = 50  # Migration + score >= 50 → Priority: 3
PRIORITY_4_MIGRATION_SCORE = 0  # Migration + score >= 0 → Priority: 4
PRIORITY_3_EXISTING_SCORE = 70  # Existing + score >= 70 → Priority: 3
PRIORITY_4_EXISTING_SCORE = 50  # Existing + score >= 50 → Priority: 4
PRIORITY_5_EXISTING_SCORE = 30  # Existing + score >= 30 → Priority: 5
PRIORITY_5_COLD_SCORE = 40  # Cold + score >= 40 → Priority: 5
PRIORITY_6_COLD_SCORE = 20  # Cold + score >= 20 → Priority: 6

# Domain Expiry Thresholds
EXPIRE_SOON_DAYS = 30  # Domain expires in < 30 days

# Bulk Operations Limits
MAX_BULK_SCAN_DOMAINS = 1000  # Maximum domains per bulk scan/rescan
