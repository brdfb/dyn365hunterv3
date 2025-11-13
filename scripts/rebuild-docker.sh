#!/bin/bash
# Rebuild Docker containers with latest requirements

set -e

echo "🔨 Rebuilding Docker containers..."

# Stop and remove containers
echo "🧹 Stopping and removing containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null

# Remove old images (optional, uncomment if needed)
# echo "🗑️  Removing old images..."
# docker rmi dyn365hunterv3-api 2>/dev/null || true

# Rebuild without cache to ensure fresh install
echo "🔨 Rebuilding containers (no cache)..."
docker-compose build --no-cache || docker compose build --no-cache

# Start services
echo "🚀 Starting services..."
docker-compose up -d || docker compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if containers are running
if docker ps | grep -q dyn365hunter-api; then
    echo "✅ API container is running"
else
    echo "❌ API container failed to start"
    exit 1
fi

if docker ps | grep -q dyn365hunter-postgres; then
    echo "✅ PostgreSQL container is running"
else
    echo "❌ PostgreSQL container failed to start"
    exit 1
fi

echo ""
echo "✅ Rebuild complete! Containers are running."
echo "📝 To check logs: docker-compose logs -f api"
echo "🧪 To run tests: docker-compose exec api pytest tests/ -v"

