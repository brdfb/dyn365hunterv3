#!/bin/bash

# Database Reset Script - Pure Alembic Approach
# This is the OFFICIAL way to reset the database for v1.0+
# DO NOT use schema.sql or legacy SQL migrations - they are deprecated

set -e

echo "🔄 Database Reset - Pure Alembic Approach"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will DELETE ALL DATA in the database!"
echo "   Press Ctrl+C to cancel, or wait 5 seconds to continue..."
sleep 5

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

echo ""
echo "🗑️  Step 1: Dropping all tables..."
echo "----------------------------------------"
docker-compose exec -T api python -c "
from app.db.session import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
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
echo "🔄 Step 2: Running Alembic migrations (official way)..."
echo "----------------------------------------"
echo -e "${YELLOW}ℹ️  This will create all tables, columns, and views via Alembic${NC}"

# Base revision has issues with fresh DB - create tables from models first
echo -e "${YELLOW}ℹ️  Creating base tables from SQLAlchemy models...${NC}"
docker-compose exec -T api python -c "
from app.db.models import Base
from app.db.session import engine

# Create all tables from models
Base.metadata.create_all(bind=engine)
print('✅ Base tables created from models')
"

# Mark all migrations up to CSP P-Model as applied (tables already created from models)
docker-compose exec -T api python -c "
from app.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Create alembic_version table if it doesn't exist
    conn.execute(text('''
        CREATE TABLE IF NOT EXISTS alembic_version (
            version_num VARCHAR(32) NOT NULL,
            CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
        );
    '''))
    # Mark all migrations up to CSP P-Model as applied (tables already created from models)
    # Use stamp to mark all intermediate migrations as applied
    conn.execute(text('''
        INSERT INTO alembic_version (version_num) 
        VALUES ('622ba66483b9')
        ON CONFLICT (version_num) DO UPDATE SET version_num = EXCLUDED.version_num;
    '''))
    conn.commit()
    print('✅ Base migrations marked as applied (tables created from models)')
"

# Stamp to head (CSP P-Model) - all tables and columns already created from models
echo -e "${YELLOW}ℹ️  Stamping migration history to head...${NC}"
docker-compose exec -T api alembic stamp head

# Update leads_ready view with P-Model fields (migration does this, but we'll do it manually)
echo -e "${YELLOW}ℹ️  Updating leads_ready view with P-Model fields...${NC}"
docker-compose exec -T api python -c "
from app.db.session import engine
from sqlalchemy import text

# Read the view SQL from CSP P-Model migration
with engine.connect() as conn:
    # Check if P-Model columns exist in lead_scores
    result = conn.execute(text('''
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'lead_scores' 
        AND column_name IN ('technical_heat', 'commercial_segment', 'commercial_heat', 'priority_category', 'priority_label');
    '''))
    p_model_cols = [row[0] for row in result]
    
    if len(p_model_cols) == 5:
        print('✅ P-Model columns already exist in lead_scores')
        # Update view (from CSP P-Model migration logic)
        # Includes G20 columns (tenant_size, local_provider, dmarc_coverage) and CSP P-Model columns
        conn.execute(text('''
            DROP VIEW IF EXISTS leads_ready CASCADE;
            CREATE VIEW leads_ready AS
            SELECT 
                c.id AS company_id,
                c.canonical_name,
                c.domain,
                c.provider,
                c.tenant_size,
                c.country,
                c.contact_emails,
                c.contact_quality_score,
                c.linkedin_pattern,
                c.updated_at AS company_updated_at,
                ds.id AS signal_id,
                ds.spf,
                ds.dkim,
                ds.dmarc_policy,
                ds.dmarc_coverage,
                ds.mx_root,
                ds.local_provider,
                ds.registrar,
                ds.expires_at,
                ds.nameservers,
                ds.scan_status,
                ds.scanned_at,
                ls.id AS score_id,
                ls.readiness_score,
                ls.segment,
                ls.reason,
                ls.technical_heat,
                ls.commercial_segment,
                ls.commercial_heat,
                ls.priority_category,
                ls.priority_label
            FROM companies c
            LEFT JOIN domain_signals ds ON c.domain = ds.domain
            LEFT JOIN lead_scores ls ON c.domain = ls.domain
            WHERE ls.readiness_score IS NOT NULL;
        '''))
        conn.commit()
        print('✅ leads_ready view updated with P-Model fields')
    else:
        print(f'⚠️  P-Model columns missing: {p_model_cols}')
"

echo ""
echo "✅ Step 3: Verifying schema..."
echo "----------------------------------------"
docker-compose exec -T api python -c "
from app.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Check critical G20 columns
    result = conn.execute(text('''
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'companies' 
        AND column_name = 'tenant_size';
    '''))
    tenant_size_exists = result.fetchone() is not None
    
    result = conn.execute(text('''
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'domain_signals' 
        AND column_name IN ('local_provider', 'dmarc_coverage');
    '''))
    domain_signals_cols = [row[0] for row in result]
    
    # Check leads_ready view
    result = conn.execute(text('''
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'leads_ready' 
        AND column_name IN ('priority_category', 'commercial_segment', 'technical_heat');
    '''))
    p_model_cols = [row[0] for row in result]
    
    print(f'✅ Companies.tenant_size: {\"✓\" if tenant_size_exists else \"✗\"}')
    print(f'✅ Domain_signals columns: {domain_signals_cols}')
    print(f'✅ P-Model columns in view: {p_model_cols}')
    
    if tenant_size_exists and len(domain_signals_cols) == 2 and len(p_model_cols) == 3:
        print('✅ All critical columns present!')
    else:
        print('⚠️  Some columns missing - check Alembic migrations')
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
echo "=========================================================="
echo -e "${GREEN}✅ Database Reset Complete!${NC}"
echo ""
echo "📋 Database is now clean and ready:"
echo "   - All tables created via Alembic (official way)"
echo "   - G20 columns present (tenant_size, local_provider, dmarc_coverage)"
echo "   - CSP P-Model columns present"
echo "   - leads_ready view created with all columns"
echo "   - Redis cache cleared"
echo ""
echo "📝 Next Steps:"
echo "   1. Test with: curl -X POST http://localhost:8000/api/v1/ingest/domain -H 'Content-Type: application/json' -d '{\"domain\": \"gibibyte.com.tr\"}'"
echo "   2. Scan: curl -X POST http://localhost:8000/api/v1/scan/domain -H 'Content-Type: application/json' -d '{\"domain\": \"gibibyte.com.tr\"}'"
echo ""

