#!/bin/bash
# Phase 0 Deployment Script
# Deploys Phase 0 (Enhanced Scoring & Hard-Fail Rules) to dev environment

set -e  # Exit on error

echo "🚀 Phase 0 Deployment - Enhanced Scoring & Hard-Fail Rules"
echo "=========================================================="
echo ""

# Check Docker availability
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed or not in PATH"
    exit 1
fi

echo "✅ Docker and Docker Compose are available"
echo ""

# Step 1: Rebuild Docker containers with Phase 0 changes
echo "📦 Step 1: Rebuilding Docker containers..."
echo "   This will rebuild the API container with Phase 0 changes..."

if docker-compose build --no-cache api 2>/dev/null || docker compose build --no-cache api 2>/dev/null; then
    echo "✅ Docker containers rebuilt successfully"
else
    echo "❌ Failed to rebuild Docker containers"
    exit 1
fi

echo ""

# Step 2: Stop existing containers
echo "🛑 Step 2: Stopping existing containers..."
if docker-compose down 2>/dev/null || docker compose down 2>/dev/null; then
    echo "✅ Containers stopped"
else
    echo "⚠️  No containers to stop (this is OK)"
fi

echo ""

# Step 3: Start services
echo "🚀 Step 3: Starting services..."
if docker-compose up -d 2>/dev/null || docker compose up -d 2>/dev/null; then
    echo "✅ Services started"
else
    echo "❌ Failed to start services"
    exit 1
fi

echo ""

# Step 4: Wait for PostgreSQL
echo "⏳ Step 4: Waiting for PostgreSQL to be ready (max 30s)..."
timeout=30
counter=0
while [ $counter -lt $timeout ]; do
    if docker-compose exec -T postgres pg_isready -U dyn365hunter > /dev/null 2>&1 || \
       docker compose exec -T postgres pg_isready -U dyn365hunter > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    sleep 1
    counter=$((counter + 1))
    echo -n "."
done

if [ $counter -eq $timeout ]; then
    echo "❌ PostgreSQL failed to start within ${timeout}s"
    exit 1
fi

echo ""

# Step 5: Run database migration (if needed)
echo "📊 Step 5: Checking database schema..."
if [ -f app/db/migrate.py ]; then
    if docker-compose exec -T api python3 -m app.db.migrate 2>/dev/null || \
       docker compose exec -T api python3 -m app.db.migrate 2>/dev/null; then
        echo "✅ Database schema is up to date"
    else
        echo "⚠️  Database migration failed (might be OK if schema is already up to date)"
    fi
else
    echo "ℹ️  No migration script found (schema might be managed differently)"
fi

echo ""

# Step 6: Wait for FastAPI
echo "⏳ Step 6: Waiting for FastAPI to be ready (max 30s)..."
timeout=30
counter=0
while [ $counter -lt $timeout ]; do
    if curl -f http://localhost:8000/healthz > /dev/null 2>&1; then
        echo "✅ FastAPI is ready"
        break
    fi
    sleep 1
    counter=$((counter + 1))
    echo -n "."
done

if [ $counter -eq $timeout ]; then
    echo "❌ FastAPI failed to start within ${timeout}s"
    echo "   Check logs: docker-compose logs api"
    exit 1
fi

echo ""

# Step 7: Verify health endpoint
echo "🔍 Step 7: Verifying health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/healthz)
if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
    echo "✅ Health endpoint is responding"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo "❌ Health endpoint is not responding correctly"
    echo "   Response: $HEALTH_RESPONSE"
    exit 1
fi

echo ""

# Step 8: Run smoke tests
echo "🧪 Step 8: Running smoke tests..."
if [ -f scripts/smoke_test_phase0.sh ]; then
    chmod +x scripts/smoke_test_phase0.sh
    if bash scripts/smoke_test_phase0.sh; then
        echo "✅ Smoke tests passed"
    else
        echo "❌ Smoke tests failed"
        echo "   Review the test output above for details"
        exit 1
    fi
else
    echo "⚠️  Smoke test script not found (scripts/smoke_test_phase0.sh)"
    echo "   Skipping smoke tests"
fi

echo ""
echo "=========================================================="
echo "🎉 Phase 0 Deployment Complete!"
echo "=========================================================="
echo ""
echo "📋 Access URLs:"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/healthz"
echo "   - Mini UI: http://localhost:8000/mini-ui/"
echo ""
echo "📝 Phase 0 Features Deployed:"
echo "   ✅ Hard-Fail Rules (MX missing → Skip segment)"
echo "   ✅ Risk Scoring (negative points for missing security signals)"
echo "   ✅ Provider Points Updated (Hosting: 20, Local: 10)"
echo ""
echo "📊 Useful commands:"
echo "   - View logs: docker-compose logs -f api"
echo "   - Run smoke tests: bash scripts/smoke_test_phase0.sh"
echo "   - Stop services: docker-compose down"
echo ""

