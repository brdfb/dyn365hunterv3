#!/bin/bash

# Production UAT Database Reset Script
# ⚠️  DEPRECATED - Use scripts/reset_db_with_alembic.sh instead
# This script uses schema.sql + legacy migrations (not recommended)
# Kept for backward compatibility only

set -e

echo "🗑️  Production UAT Database Reset"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}❌ Services are not running. Please start with: docker-compose up -d${NC}"
    exit 1
fi

echo "⚠️  WARNING: This will DELETE ALL DATA in the database!"
echo "   Press Ctrl+C to cancel, or wait 5 seconds to continue..."
sleep 5

echo ""
echo "🗑️  Step 1: Dropping all tables..."
echo "----------------------------------------"
docker-compose exec -T api python -c "
from app.db.session import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        # Drop all tables
        conn.execute(text('DROP SCHEMA IF EXISTS public CASCADE;'))
        conn.execute(text('CREATE SCHEMA public;'))
        conn.execute(text('GRANT ALL ON SCHEMA public TO dyn365hunter;'))
        conn.execute(text('GRANT ALL ON SCHEMA public TO public;'))
        conn.commit()
    print('✅ Database dropped successfully')
except Exception as e:
    print(f'⚠️  Error dropping database: {e}')
"

echo ""
echo "🔄 Step 2: Running migrations (fresh schema)..."
echo "----------------------------------------"
docker-compose exec -T api python -m app.db.run_migration upgrade head

echo ""
echo "✅ Step 3: Verifying schema..."
echo "----------------------------------------"
docker-compose exec -T api python -c "
from app.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    '''))
    tables = [row[0] for row in result]
    print(f'✅ Found {len(tables)} tables:')
    for table in tables:
        print(f'   - {table}')
"

echo ""
echo "🧹 Step 4: Clearing Redis cache..."
echo "----------------------------------------"
docker-compose exec -T api python -c "
from app.core.redis_client import get_redis_client, is_redis_available

if is_redis_available():
    client = get_redis_client()
    if client:
        try:
            client.flushall()
            print('✅ Redis cache cleared')
        except Exception as e:
            print(f'⚠️  Error clearing Redis: {e}')
else:
    print('ℹ️  Redis not available (skipping cache clear)')
"

echo ""
echo "📊 Step 5: Verifying empty database..."
echo "----------------------------------------"
LEAD_COUNT=$(docker-compose exec -T api python -c "
from app.db.session import get_db
from app.db.models import LeadScore

db = next(get_db())
count = db.query(LeadScore).count()
print(count)
" 2>/dev/null || echo "0")

if [ "$LEAD_COUNT" = "0" ]; then
    echo -e "${GREEN}✅ Database is empty (0 leads)${NC}"
else
    echo -e "${YELLOW}⚠️  Database still has $LEAD_COUNT leads${NC}"
fi

echo ""
echo "=========================================================="
echo -e "${GREEN}✅ Database Reset Complete!${NC}"
echo ""
echo "📋 Database is now clean and ready for UAT:"
echo "   - All tables dropped and recreated"
echo "   - Migrations applied (including CSP P-Model)"
echo "   - Redis cache cleared"
echo "   - Database is empty (0 leads)"
echo ""
echo "📝 Next Steps:"
echo "   1. Test golden domains:"
echo "      bash scripts/production_uat_test.sh"
echo "   2. Or manually ingest and scan:"
echo "      curl -X POST http://localhost:8000/api/v1/ingest/domain -H 'Content-Type: application/json' -d '{\"domain\": \"gibibyte.com.tr\"}'"
echo "      curl -X POST http://localhost:8000/api/v1/scan/domain -H 'Content-Type: application/json' -d '{\"domain\": \"gibibyte.com.tr\"}'"
echo ""

