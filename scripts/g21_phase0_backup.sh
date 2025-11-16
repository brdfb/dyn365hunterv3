#!/bin/bash
# G21 Phase 0: Database Backup Script
# Creates a database backup before refactoring

set -e

# Get current date/time for backup filename
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"
BACKUP_FILE="${BACKUP_DIR}/backup_pre_refactor_${BACKUP_DATE}.sql"

# Create backups directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

echo "🔄 G21 Phase 0: Creating database backup..."
echo "📁 Backup file: ${BACKUP_FILE}"

# Check if running in Docker
if [ -f /.dockerenv ] || [ -n "${DOCKER_CONTAINER}" ]; then
    # Running inside Docker - use docker-compose exec
    echo "🐳 Running in Docker environment..."
    docker-compose exec -T postgres pg_dump -U dyn365hunter dyn365hunter > "${BACKUP_FILE}"
else
    # Running locally - use pg_dump directly
    echo "💻 Running in local environment..."
    # Try to get database URL from .env
    if [ -f .env ]; then
        source .env
        pg_dump "${HUNTER_DATABASE_URL}" > "${BACKUP_FILE}"
    else
        echo "❌ Error: .env file not found. Please set HUNTER_DATABASE_URL manually."
        exit 1
    fi
fi

# Check if backup was successful
if [ -f "${BACKUP_FILE}" ] && [ -s "${BACKUP_FILE}" ]; then
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "✅ Backup created successfully!"
    echo "📊 Backup size: ${BACKUP_SIZE}"
    echo "📍 Location: ${BACKUP_FILE}"
else
    echo "❌ Error: Backup file is empty or not created!"
    exit 1
fi

echo ""
echo "✅ Phase 0.1: Database backup completed"
echo "📝 Next step: Create git tag (scripts/g21_phase0_git_tag.sh)"

