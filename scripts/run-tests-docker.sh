#!/bin/bash
# Run tests inside Docker container

set -e

echo "🧪 Running tests in Docker container..."

# Check if containers are running
if ! docker ps | grep -q dyn365hunter-api; then
    echo "⚠️  API container is not running. Starting containers..."
    docker-compose up -d || docker compose up -d
    
    echo "⏳ Waiting for containers to be ready..."
    sleep 10
fi

# Check if PostgreSQL is ready
echo "🔍 Checking PostgreSQL connection..."
if ! docker-compose exec -T postgres pg_isready -U dyn365hunter > /dev/null 2>&1; then
    echo "⚠️  PostgreSQL is not ready yet. Waiting..."
    sleep 5
fi

# Run tests
echo "🚀 Running tests..."
echo ""

docker-compose exec -T api pytest tests/ -v --tb=short || docker compose exec -T api pytest tests/ -v --tb=short

echo ""
echo "✅ Tests completed!"

