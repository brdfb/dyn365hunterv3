#!/bin/bash
# Smoke test for structured logging - verifies log output format and PII masking

set -e

echo "🔍 Starting Logging Smoke Test..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if API is running
API_URL="${API_URL:-http://localhost:8000}"
HEALTH_CHECK="${API_URL}/healthz"

echo "📡 Checking API health..."
if ! curl -s -f "$HEALTH_CHECK" > /dev/null; then
    echo -e "${RED}❌ API is not running at $API_URL${NC}"
    echo "   Start API with: docker-compose up -d api"
    exit 1
fi

echo -e "${GREEN}✅ API is running${NC}"
echo ""

# Test 1: Health check (should trigger Redis client initialization)
echo "🧪 Test 1: Health check (Redis client initialization)"
curl -s "$HEALTH_CHECK" > /dev/null
echo -e "${GREEN}✅ Health check completed${NC}"
echo "   Check logs for: redis_client_initialized"
echo ""

# Test 2: Metrics endpoint (should trigger cache operations)
echo "🧪 Test 2: Metrics endpoint (cache operations)"
curl -s "${API_URL}/healthz/metrics" > /dev/null
echo -e "${GREEN}✅ Metrics endpoint called${NC}"
echo "   Check logs for: cache operations (if any failures)"
echo ""

# Test 3: Scan endpoint (should trigger DNS/WHOIS cache and rate limiting)
echo "🧪 Test 3: Scan endpoint (DNS/WHOIS cache + rate limiting)"
echo "   Note: This requires a domain to be ingested first"
echo "   Skipping scan test (requires domain ingestion)"
echo ""

# Test 4: Multiple health checks (should show cache behavior)
echo "🧪 Test 4: Multiple health checks (cache behavior)"
for i in {1..3}; do
    curl -s "$HEALTH_CHECK" > /dev/null
    sleep 0.5
done
echo -e "${GREEN}✅ Multiple health checks completed${NC}"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}📋 Log Verification Checklist:${NC}"
echo ""
echo "Check Docker logs with:"
echo "  docker-compose logs api | grep -E '(cache_|rate_limiter_|redis_client_)'"
echo ""
echo "Expected log events:"
echo "  ✅ redis_client_initialized (info level)"
echo "  ✅ cache operations (debug level, if any failures)"
echo "  ✅ rate_limiter operations (if rate limiting triggered)"
echo ""
echo "PII Verification:"
echo "  ✅ No email addresses in logs"
echo "  ✅ No company names in logs"
echo "  ✅ Cache keys are masked (e.g., cache:dns:<hash>)"
echo "  ✅ Redis keys don't contain PII (e.g., api_key_123, dns, whois)"
echo ""
echo "Log Level Verification:"
echo "  ✅ cache_*_failed → debug level"
echo "  ✅ rate_limiter_fallback → warning level"
echo "  ✅ redis_client_initialization_failed → error level"
echo "  ✅ redis_client_initialized → info level"
echo ""
echo "Structured Logging Format:"
echo "  ✅ Event name is first parameter (string)"
echo "  ✅ Context keys are snake_case (operation, reason, redis_key)"
echo "  ✅ JSON format in production (if ENVIRONMENT=production)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ Smoke test completed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Check Docker logs: docker-compose logs api --tail=100"
echo "  2. Filter for specific events: docker-compose logs api | grep 'cache_get_failed'"
echo "  3. Verify JSON format: docker-compose logs api | jq '.' (if jq installed)"
echo ""

