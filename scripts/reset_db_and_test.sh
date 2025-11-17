#!/bin/bash
# Database Reset and Fresh Test Script
# This script resets the database and runs fresh tests

set -e  # Exit on error

echo "🔄 Database Reset and Fresh Test"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "alembic.ini" ]; then
    echo -e "${RED}❌ Error: alembic.ini not found. Run this script from project root.${NC}"
    exit 1
fi

# Check if database URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${YELLOW}⚠️  DATABASE_URL not set, using default from config${NC}"
fi

echo "📋 Step 1: Check current database state"
echo "----------------------------------------"
python -m app.db.run_migration current || echo "No migrations found (expected for fresh DB)"

echo ""
echo "🗑️  Step 2: Drop all tables (if exists)"
echo "----------------------------------------"
python -c "
from app.db.session import engine
from sqlalchemy import text
from app.core.logging import logger

try:
    with engine.connect() as conn:
        # Drop all tables
        conn.execute(text('DROP SCHEMA public CASCADE;'))
        conn.execute(text('CREATE SCHEMA public;'))
        conn.execute(text('GRANT ALL ON SCHEMA public TO dyn365hunter;'))
        conn.execute(text('GRANT ALL ON SCHEMA public TO public;'))
        conn.commit()
    print('✅ Database dropped successfully')
except Exception as e:
    print(f'⚠️  Error dropping database (might be empty): {e}')
    logger.debug('db_reset_drop', error=str(e))
"

echo ""
echo "🔄 Step 3: Run migrations (fresh schema)"
echo "----------------------------------------"
python -m app.db.run_migration upgrade head

echo ""
echo "✅ Step 4: Verify schema"
echo "----------------------------------------"
python -c "
from app.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text(\"\"\"
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    \"\"\"))
    tables = [row[0] for row in result]
    print(f'✅ Found {len(tables)} tables:')
    for table in tables:
        print(f'   - {table}')
"

echo ""
echo "🧹 Step 5: Clear Redis cache (if available)"
echo "----------------------------------------"
python -c "
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
echo "✅ Database reset complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Add test domains: curl -X POST http://localhost:8000/api/v1/ingest/domain -H 'Content-Type: application/json' -d '{\"domain\": \"dmkimya.com.tr\", \"company_name\": \"Test Company\"}'"
echo "   2. Scan domain: curl -X POST http://localhost:8000/api/v1/scan/domain -H 'Content-Type: application/json' -d '{\"domain\": \"dmkimya.com.tr\"}'"
echo "   3. Check results: curl http://localhost:8000/api/v1/leads/dmkimya.com.tr"
echo ""

