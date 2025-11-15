#!/usr/bin/env python3
"""
Run a specific migration file against the database.
Usage: python -m app.db.run_migration g19_users_auth
"""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from app.config import settings


def run_migration_file(migration_name: str):
    """Run a specific migration file."""
    migrations_dir = Path(__file__).parent / "migrations"
    migration_file = migrations_dir / f"{migration_name}.sql"

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        sys.exit(1)

    # Read migration file
    try:
        with open(migration_file, "r", encoding="utf-8") as f:
            migration_sql = f.read()
    except Exception as e:
        print(f"❌ Failed to read migration file: {e}")
        sys.exit(1)

    # Create database engine
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
    except Exception as e:
        print(f"❌ Failed to create database engine: {e}")
        sys.exit(1)

    # Execute migration
    try:
        with engine.begin() as conn:
            conn.execute(text(migration_sql))
        print(f"✅ Migration '{migration_name}' completed successfully")
        return 0
    except Exception as e:
        print(f"❌ Migration '{migration_name}' failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.db.run_migration <migration_name>")
        print("Example: python -m app.db.run_migration g19_users_auth")
        sys.exit(1)

    migration_name = sys.argv[1]
    sys.exit(run_migration_file(migration_name))

