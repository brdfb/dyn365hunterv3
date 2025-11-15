#!/usr/bin/env python3
"""
Alembic migration runner - Wrapper for Alembic commands.

This script provides a convenient interface to run Alembic migrations.
Legacy SQL migration files have been moved to app/db/migrations/legacy/ for reference.

Usage:
    # Upgrade to latest migration
    python -m app.db.run_migration upgrade

    # Upgrade to specific revision
    python -m app.db.run_migration upgrade <revision>

    # Downgrade one step
    python -m app.db.run_migration downgrade

    # Show current revision
    python -m app.db.run_migration current

    # Show migration history
    python -m app.db.run_migration history

    # Check for schema drift
    python -m app.db.run_migration check
"""
import sys
import subprocess
from pathlib import Path


def run_alembic_command(command: str, *args):
    """Run Alembic command via subprocess."""
    alembic_cmd = ["alembic"] + [command] + list(args)
    
    try:
        result = subprocess.run(alembic_cmd, check=False, capture_output=False)
        return result.returncode
    except FileNotFoundError:
        print("❌ Alembic not found. Make sure Alembic is installed and in PATH.")
        print("   Install: pip install alembic")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to run Alembic command: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    # Validate command
    valid_commands = ["upgrade", "downgrade", "current", "history", "check", "stamp", "revision"]
    if command not in valid_commands:
        print(f"❌ Unknown command: {command}")
        print(f"   Valid commands: {', '.join(valid_commands)}")
        sys.exit(1)

    # Special handling for upgrade (default to 'head')
    if command == "upgrade" and not args:
        args = ["head"]

    # Run Alembic command
    exit_code = run_alembic_command(command, *args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

