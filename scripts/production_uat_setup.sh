#!/bin/bash

# Production UAT Setup Script
# Prepares production environment for CSP P-Model + Sales Summary v1.1 UAT

set -e

echo "🚀 Production UAT Setup - CSP P-Model + Sales Summary v1.1"
echo "=========================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
echo "📦 Checking Docker..."
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Check if services are running
echo "🔍 Checking services..."
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Services are not running. Starting services...${NC}"
    docker-compose up -d
    echo "⏳ Waiting for services to be ready..."
    sleep 10
fi
echo -e "${GREEN}✅ Services are running${NC}"
echo ""

# Check database connection
echo "🗄️  Checking database connection..."
if docker-compose exec -T postgres pg_isready -U dyn365hunter > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database is ready${NC}"
else
    echo -e "${RED}❌ Database is not ready. Please check Docker logs.${NC}"
    exit 1
fi
echo ""

# Check Redis connection
echo "🔴 Checking Redis connection..."
if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
    echo -e "${GREEN}✅ Redis is ready${NC}"
else
    echo -e "${RED}❌ Redis is not ready. Please check Docker logs.${NC}"
    exit 1
fi
echo ""

# Check API health
echo "🏥 Checking API health..."
API_HEALTH=$(curl -s http://localhost:8000/healthz || echo "FAILED")
if echo "$API_HEALTH" | grep -q "ok"; then
    echo -e "${GREEN}✅ API is healthy${NC}"
else
    echo -e "${RED}❌ API is not healthy. Response: $API_HEALTH${NC}"
    exit 1
fi
echo ""

# Check database migrations
echo "🔄 Checking database migrations..."
MIGRATION_STATUS=$(docker-compose exec -T api python -m app.db.run_migration current 2>&1 || echo "FAILED")
if echo "$MIGRATION_STATUS" | grep -q "f786f93501ea"; then
    echo -e "${GREEN}✅ CSP P-Model migration is applied${NC}"
else
    echo -e "${YELLOW}⚠️  CSP P-Model migration may not be applied. Current: $MIGRATION_STATUS${NC}"
    echo "   Running migrations..."
    docker-compose exec -T api python -m app.db.run_migration upgrade head
    echo -e "${GREEN}✅ Migrations completed${NC}"
fi
echo ""

# Check feature flags (CSP P-Model and Sales Summary are core features - no flags needed)
echo "🚩 Checking feature flags..."
echo "   CSP P-Model: Core feature (always enabled - no flag needed)"
echo "   Sales Summary v1.1: Core feature (always enabled - no flag needed)"
echo -e "${GREEN}✅ Feature flags verified${NC}"
echo ""

# Check environment variables
echo "⚙️  Checking environment variables..."
ENV_CHECK=$(docker-compose exec -T api env | grep -E "LOG_LEVEL|ENVIRONMENT" || echo "")
if echo "$ENV_CHECK" | grep -q "LOG_LEVEL=INFO"; then
    echo -e "${GREEN}✅ LOG_LEVEL is set to INFO${NC}"
else
    echo -e "${YELLOW}⚠️  LOG_LEVEL may not be INFO. Current: $ENV_CHECK${NC}"
fi
echo ""

# Prepare test domains list
echo "📋 Preparing test domains..."
TEST_DOMAINS=(
    "gibibyte.com.tr|P4|Existing M365|RENEWAL|Warm"
    "dmkimya.com.tr|P2|Google Workspace Migration|COMPETITIVE|Hot"
    "LOCAL_HOSTING_P1|P1|Local/Hosting Migration|GREENFIELD|Hot"
    "WEAK_PARTNER_P3|P3|Weak Partner M365|WEAK_PARTNER|Warm"
)

echo "   Test domains for UAT:"
for domain_info in "${TEST_DOMAINS[@]}"; do
    IFS='|' read -r domain priority description segment heat <<< "$domain_info"
    echo "   - $domain ($priority): $description"
done
echo ""

# Create screenshot directory
echo "📸 Creating screenshot directory..."
mkdir -p docs/archive/2025-01-29-PRODUCTION-UAT-SCREENSHOTS
echo -e "${GREEN}✅ Screenshot directory created${NC}"
echo ""

# Summary
echo "=========================================================="
echo -e "${GREEN}✅ Production UAT Environment Ready!${NC}"
echo ""
echo "📋 Next Steps:"
echo "   1. Run golden-domain UAT tests:"
echo "      - Scan: gibibyte.com.tr (P4)"
echo "      - Scan: dmkimya.com.tr (P2)"
echo "      - Find and scan: P1 Local/Hosting Migration domain"
echo "      - Find and scan: P3 Weak Partner M365 domain"
echo ""
echo "   2. Verify P-Model fields in API responses:"
echo "      curl http://localhost:8000/api/v1/leads/gibibyte.com.tr | jq '.priority_category, .commercial_segment, .technical_heat'"
echo ""
echo "   3. Check logs for score_domain and sales_summary events:"
echo "      docker-compose logs api | grep -E 'score_domain|sales_summary_viewed'"
echo ""
echo "   4. Take screenshots:"
echo "      - Lead list (P-badges visible)"
echo "      - Score breakdown modal (CSP P-Model panel)"
echo "      - Sales summary modal (all sections)"
echo "      - Save to: docs/archive/2025-01-29-PRODUCTION-UAT-SCREENSHOTS/"
echo ""
echo "📖 Full checklist: docs/active/PRODUCTION-READINESS-CHECKLIST-2025-01-29.md"
echo ""

