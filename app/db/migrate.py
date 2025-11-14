#!/usr/bin/env python3
"""
Database schema migration script for Dyn365Hunter MVP.
Runs schema.sql against the database.
"""
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from app.config import settings


def run_migration():
    """Run schema.sql migration against the database."""

    # Get schema.sql path
    schema_file = Path(__file__).parent / "schema.sql"

    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        sys.exit(1)

    # Read schema.sql
    try:
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_sql = f.read()
    except Exception as e:
        print(f"❌ Failed to read schema file: {e}")
        sys.exit(1)

    # Create database engine
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
    except Exception as e:
        print(f"❌ Failed to create database engine: {e}")
        sys.exit(1)

    # Execute migration
    try:
        with engine.begin() as conn:  # begin() automatically commits on success
            # Execute schema.sql (PostgreSQL allows executing multiple statements)
            conn.execute(text(schema_sql))
        print("✅ Schema migration completed successfully")
        return 0
    except Exception as e:
        print(f"❌ Schema migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(run_migration())
