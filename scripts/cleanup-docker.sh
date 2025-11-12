#!/bin/bash
# Cleanup Docker containers and resources for Dyn365Hunter

set -e

echo "🧹 Cleaning up Dyn365Hunter Docker resources..."

# Stop and remove containers
echo "📦 Stopping and removing containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# Remove containers by name if they exist
if docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "dyn365hunter-postgres"; then
    echo "   Removing dyn365hunter-postgres container..."
    docker rm -f dyn365hunter-postgres 2>/dev/null || true
fi

if docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "dyn365hunter-api"; then
    echo "   Removing dyn365hunter-api container..."
    docker rm -f dyn365hunter-api 2>/dev/null || true
fi

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

