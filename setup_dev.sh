#!/bin/bash
# Dyn365Hunter MVP - Development Environment Setup Script

set -e  # Exit on error

echo "🚀 Setting up Dyn365Hunter MVP development environment..."

# Check if virtual environment setup is requested
if [ "$1" == "--with-venv" ] || [ "$1" == "-v" ]; then
    echo "🐍 Setting up Python virtual environment..."
    if [ -f "setup_venv.sh" ]; then
        bash setup_venv.sh
        echo ""
    else
        echo "⚠️  setup_venv.sh not found, skipping venv setup"
    fi
fi

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

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env from .env.example"
    else
        echo "⚠️  .env.example not found, creating basic .env"
        cat > .env << EOF
# Database
DATABASE_URL=postgresql://dyn365hunter:password123@postgres:5432/dyn365hunter
POSTGRES_USER=dyn365hunter
POSTGRES_PASSWORD=password123
POSTGRES_DB=dyn365hunter

# FastAPI
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Development
ENVIRONMENT=development
EOF
        echo "✅ Created basic .env file"
    fi
else
    echo "ℹ️  .env file already exists, skipping"
fi

# Start Docker Compose services
echo "🐳 Starting Docker Compose services..."

# Stop and remove existing containers (force remove if needed)
echo "🧹 Cleaning up existing containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null

# Also remove containers by name if they exist (from previous runs)
if docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "dyn365hunter-postgres"; then
    echo "   Removing existing dyn365hunter-postgres container..."
    docker rm -f dyn365hunter-postgres 2>/dev/null || true
fi
if docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "dyn365hunter-api"; then
    echo "   Removing existing dyn365hunter-api container..."
    docker rm -f dyn365hunter-api 2>/dev/null || true
fi

# Start services
echo "🚀 Starting Docker Compose services..."
docker-compose up -d || docker compose up -d

echo "⏳ Waiting for PostgreSQL to be ready (max 30s)..."
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

# Run schema migration if schema.sql exists
if [ -f app/db/schema.sql ]; then
    echo "📊 Running database schema migration..."
    # Try Python migration script first (preferred method)
    if [ -f app/db/migrate.py ]; then
        echo "   Using Python migration script..."
        if docker-compose exec -T api python3 -m app.db.migrate 2>/dev/null || \
           docker compose exec -T api python3 -m app.db.migrate 2>/dev/null; then
            echo "✅ Schema migration completed (via Python script)"
        else
            echo "⚠️  Python migration failed, trying direct SQL..."
            # Fallback to direct SQL execution
            if docker-compose exec -T postgres psql -U dyn365hunter -d dyn365hunter < app/db/schema.sql 2>/dev/null || \
               docker compose exec -T postgres psql -U dyn365hunter -d dyn365hunter < app/db/schema.sql 2>/dev/null; then
                echo "✅ Schema migration completed (via direct SQL)"
            else
                echo "❌ Schema migration failed"
                echo "   You can run it manually: docker-compose exec api python3 -m app.db.migrate"
                exit 1
            fi
        fi
    else
        # Fallback to direct SQL execution if migrate.py doesn't exist
        echo "   Using direct SQL execution..."
        if docker-compose exec -T postgres psql -U dyn365hunter -d dyn365hunter < app/db/schema.sql 2>/dev/null || \
           docker compose exec -T postgres psql -U dyn365hunter -d dyn365hunter < app/db/schema.sql 2>/dev/null; then
            echo "✅ Schema migration completed"
        else
            echo "❌ Schema migration failed"
            echo "   You can run it manually: docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter < app/db/schema.sql"
            exit 1
        fi
    fi
else
    echo "ℹ️  Schema migration skipped (app/db/schema.sql not found)"
fi

# Wait for FastAPI to be ready
echo "⏳ Waiting for FastAPI to be ready (max 30s)..."
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
    echo "⚠️  FastAPI may not be ready yet, but continuing..."
fi

# Verify /healthz endpoint
echo "🔍 Verifying /healthz endpoint..."
if curl -f http://localhost:8000/healthz > /dev/null 2>&1; then
    echo "✅ /healthz endpoint is responding"
    curl -s http://localhost:8000/healthz | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/healthz
else
    echo "❌ /healthz endpoint is not responding"
    echo "   Check logs: docker-compose logs api"
    exit 1
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Access URLs:"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/healthz"
echo ""
echo "📝 Useful commands:"
echo "   - View logs: docker-compose logs -f api"
echo "   - Stop services: docker-compose down"
echo "   - Restart services: docker-compose restart"
echo ""

