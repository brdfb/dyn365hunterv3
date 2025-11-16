"""Manual Partner Center referral sync script (internal use only).

Usage:
    docker-compose exec api python -m scripts.sync_partner_center

Note: This script requires PARTNER_CENTER_ENABLED=true in .env file.
If feature flag is disabled, script will exit safely with 0 synced.
"""

import sys
from app.db.session import SessionLocal
from app.core.referral_ingestion import sync_referrals_from_partner_center
from app.core.logging import logger


def main():
    """Sync referrals from Partner Center."""
    db = SessionLocal()
    try:
        logger.info("partner_center_script_started")
        result = sync_referrals_from_partner_center(db)
        
        success_count = result.get("success_count", 0)
        failure_count = result.get("failure_count", 0)
        skipped_count = result.get("skipped_count", 0)
        
        print(f"Partner Center sync completed:")
        print(f"  - Success: {success_count}")
        print(f"  - Failed: {failure_count}")
        print(f"  - Skipped: {skipped_count}")
        print(f"  - Total processed: {success_count + failure_count + skipped_count}")
        
        if success_count == 0 and failure_count == 0 and skipped_count == 0:
            print("\nNote: Feature flag may be disabled or no referrals found.")
            print("Check HUNTER_PARTNER_CENTER_ENABLED in .env file.")
        
        return 0
    except Exception as e:
        logger.error("partner_center_script_error", error=str(e), exc_info=True)
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())

