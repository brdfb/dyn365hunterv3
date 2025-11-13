#!/bin/bash
# Cleanup Docker containers and resources for Dyn365Hunter

set -e

echo "🧹 Cleaning up Dyn365Hunter Docker resources..."

# Stop and remove containers
echo "📦 Stopping and removing containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# Force remove containers by name (handles name conflicts)
echo "🗑️  Force removing containers..."
docker rm -f dyn365hunter-postgres 2>/dev/null || true
docker rm -f dyn365hunter-api 2>/dev/null || true

# Also try removing by pattern (in case names are different)
docker ps -a --format '{{.Names}}' 2>/dev/null | grep -E "dyn365hunter|domainhunter" | xargs -r docker rm -f 2>/dev/null || true

# Optional: Remove volumes (uncomment if you want to delete data)
# echo "🗑️  Removing volumes..."
# docker volume rm domainhunterv3_postgres_data 2>/dev/null || true

# Optional: Remove network (uncomment if you want to delete network)
# echo "🌐 Removing network..."
# docker network rm domainhunterv3_dyn365hunter-network 2>/dev/null || true

echo "✅ Cleanup complete!"
echo ""
echo "To start fresh:"
echo "  bash setup_dev.sh"

