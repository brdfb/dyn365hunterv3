#!/usr/bin/env python3
"""
Database Reset and Fresh Test Script
This script resets the database and runs fresh tests
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import engine
from sqlalchemy import text
from app.core.logging import logger
from app.core.redis_client import get_redis_client, is_redis_available


def reset_database():
    """Reset database by dropping all tables and recreating schema."""
    print("🔄 Step 1: Dropping all tables...")
    
    try:
        with engine.connect() as conn:
            # Drop all tables
            conn.execute(text('DROP SCHEMA IF EXISTS public CASCADE;'))
            conn.execute(text('CREATE SCHEMA public;'))
            conn.execute(text('GRANT ALL ON SCHEMA public TO dyn365hunter;'))
            conn.execute(text('GRANT ALL ON SCHEMA public TO public;'))
            conn.commit()
        print("✅ Database dropped successfully")
        return True
    except Exception as e:
        print(f"⚠️  Error dropping database (might be empty or permissions issue): {e}")
        logger.debug("db_reset_drop", error=str(e))
        return False


def run_migrations():
    """Run Alembic migrations to create fresh schema."""
    print("\n🔄 Step 2: Running migrations...")
    
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "app.db.run_migration", "upgrade", "head"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Migrations completed successfully")
        return True
    else:
        print(f"❌ Migration failed: {result.stderr}")
        return False


def verify_schema():
    """Verify that schema was created correctly."""
    print("\n✅ Step 3: Verifying schema...")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")
            return True
    except Exception as e:
        print(f"❌ Schema verification failed: {e}")
        return False


def clear_redis_cache():
    """Clear Redis cache if available."""
    print("\n🧹 Step 4: Clearing Redis cache...")
    
    if is_redis_available():
        client = get_redis_client()
        if client:
            try:
                client.flushall()
                print("✅ Redis cache cleared")
                return True
            except Exception as e:
                print(f"⚠️  Error clearing Redis: {e}")
                return False
    else:
        print("ℹ️  Redis not available (skipping cache clear)")
        return True


def main():
    """Main entry point."""
    print("=" * 60)
    print("🔄 Database Reset and Fresh Test")
    print("=" * 60)
    print()
    
    # Step 1: Reset database
    if not reset_database():
        print("\n⚠️  Database reset had issues, but continuing...")
    
    # Step 2: Run migrations
    if not run_migrations():
        print("\n❌ Migration failed. Exiting.")
        sys.exit(1)
    
    # Step 3: Verify schema
    if not verify_schema():
        print("\n❌ Schema verification failed. Exiting.")
        sys.exit(1)
    
    # Step 4: Clear Redis cache
    clear_redis_cache()
    
    print("\n" + "=" * 60)
    print("✅ Database reset complete!")
    print("=" * 60)
    print()
    print("📝 Next steps:")
    print("   1. Run test checklist: python scripts/fresh_test_checklist.py")
    print("   2. Or manually test:")
    print("      - Ingest: curl -X POST http://localhost:8000/api/v1/ingest/domain -H 'Content-Type: application/json' -d '{\"domain\": \"dmkimya.com.tr\", \"company_name\": \"Test Company\"}'")
    print("      - Scan: curl -X POST http://localhost:8000/api/v1/scan/domain -H 'Content-Type: application/json' -d '{\"domain\": \"dmkimya.com.tr\"}'")
    print("      - Check: curl http://localhost:8000/api/v1/leads/dmkimya.com.tr")
    print()


if __name__ == "__main__":
    main()

