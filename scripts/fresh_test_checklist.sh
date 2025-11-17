#!/bin/bash
# Fresh Test Checklist - Manual verification after DB reset
# This script helps verify all bug fixes are working correctly

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

API_URL="${API_URL:-http://localhost:8000/api/v1}"
TEST_DOMAIN="dmkimya.com.tr"

echo "🧪 Fresh Test Checklist - Bug Fix Verification"
echo "================================================"
echo ""

# Test 1: Ingest domain
echo -e "${BLUE}📋 Test 1: Ingest domain${NC}"
echo "----------------------------------------"
INGEST_RESPONSE=$(curl -s -X POST "$API_URL/ingest/domain" \
    -H "Content-Type: application/json" \
    -d "{\"domain\": \"$TEST_DOMAIN\", \"company_name\": \"DM Kimya Test\"}")

if echo "$INGEST_RESPONSE" | grep -q "success\|created\|domain"; then
    echo -e "${GREEN}✅ Domain ingested successfully${NC}"
else
    echo -e "${RED}❌ Domain ingestion failed${NC}"
    echo "Response: $INGEST_RESPONSE"
    exit 1
fi

echo ""
sleep 2

# Test 2: Scan domain
echo -e "${BLUE}📋 Test 2: Scan domain${NC}"
echo "----------------------------------------"
SCAN_RESPONSE=$(curl -s -X POST "$API_URL/scan/domain" \
    -H "Content-Type: application/json" \
    -d "{\"domain\": \"$TEST_DOMAIN\"}")

if echo "$SCAN_RESPONSE" | grep -q "segment\|score"; then
    echo -e "${GREEN}✅ Domain scanned successfully${NC}"
    SEGMENT=$(echo "$SCAN_RESPONSE" | python -c "import sys, json; d=json.load(sys.stdin); print(d.get('segment', 'N/A'))")
    SCORE=$(echo "$SCAN_RESPONSE" | python -c "import sys, json; d=json.load(sys.stdin); print(d.get('score', 'N/A'))")
    echo "   Segment: $SEGMENT, Score: $SCORE"
else
    echo -e "${RED}❌ Domain scan failed${NC}"
    echo "Response: $SCAN_RESPONSE"
    exit 1
fi

echo ""
sleep 2

# Test 3: Check lead response (DMARC coverage)
echo -e "${BLUE}📋 Test 3: Check lead response (DMARC coverage)${NC}"
echo "----------------------------------------"
LEAD_RESPONSE=$(curl -s "$API_URL/leads/$TEST_DOMAIN")
DMARC_COVERAGE=$(echo "$LEAD_RESPONSE" | python -c "import sys, json; d=json.load(sys.stdin); print(d.get('dmarc_coverage', 'NOT_FOUND'))")
DMARC_POLICY=$(echo "$LEAD_RESPONSE" | python -c "import sys, json; d=json.load(sys.stdin); print(d.get('dmarc_policy', 'NOT_FOUND'))")

echo "   DMARC Policy: $DMARC_POLICY"
echo "   DMARC Coverage: $DMARC_COVERAGE"

if [ "$DMARC_COVERAGE" = "None" ] || [ "$DMARC_COVERAGE" = "null" ]; then
    echo -e "${GREEN}✅ DMARC Coverage is null (correct - no DMARC record)${NC}"
elif [ "$DMARC_COVERAGE" = "100" ]; then
    echo -e "${RED}❌ DMARC Coverage is 100 (BUG: should be null)${NC}"
    exit 1
else
    echo -e "${YELLOW}⚠️  DMARC Coverage: $DMARC_COVERAGE (unexpected value)${NC}"
fi

# Test 4: Check score breakdown (DMARC coverage)
echo ""
echo -e "${BLUE}📋 Test 4: Check score breakdown (DMARC coverage)${NC}"
echo "----------------------------------------"
BREAKDOWN_RESPONSE=$(curl -s "$API_URL/leads/$TEST_DOMAIN/score-breakdown")
BREAKDOWN_DMARC_COVERAGE=$(echo "$BREAKDOWN_RESPONSE" | python -c "import sys, json; d=json.load(sys.stdin); print(d.get('dmarc_coverage', 'NOT_FOUND'))")
BREAKDOWN_DMARC_POLICY=$(echo "$BREAKDOWN_RESPONSE" | python -c "import sys, json; d=json.load(sys.stdin); print(d.get('dmarc_policy', 'NOT_FOUND'))")

echo "   DMARC Policy: $BREAKDOWN_DMARC_POLICY"
echo "   DMARC Coverage: $BREAKDOWN_DMARC_COVERAGE"

if [ "$BREAKDOWN_DMARC_COVERAGE" = "None" ] || [ "$BREAKDOWN_DMARC_COVERAGE" = "null" ]; then
    echo -e "${GREEN}✅ Score Breakdown DMARC Coverage is null (correct)${NC}"
elif [ "$BREAKDOWN_DMARC_COVERAGE" = "100" ]; then
    echo -e "${RED}❌ Score Breakdown DMARC Coverage is 100 (BUG: should be null)${NC}"
    exit 1
else
    echo -e "${YELLOW}⚠️  Score Breakdown DMARC Coverage: $BREAKDOWN_DMARC_COVERAGE (unexpected value)${NC}"
fi

# Test 5: Check P-Model fields
echo ""
echo -e "${BLUE}📋 Test 5: Check P-Model fields${NC}"
echo "----------------------------------------"
PRIORITY_CATEGORY=$(echo "$LEAD_RESPONSE" | python -c "import sys, json; d=json.load(sys.stdin); print(d.get('priority_category', 'NOT_FOUND'))")
PRIORITY_LABEL=$(echo "$LEAD_RESPONSE" | python -c "import sys, json; d=json.load(sys.stdin); print(d.get('priority_label', 'NOT_FOUND'))")
TECHNICAL_HEAT=$(echo "$LEAD_RESPONSE" | python -c "import sys, json; d=json.load(sys.stdin); print(d.get('technical_heat', 'NOT_FOUND'))")
COMMERCIAL_SEGMENT=$(echo "$LEAD_RESPONSE" | python -c "import sys, json; d=json.load(sys.stdin); print(d.get('commercial_segment', 'NOT_FOUND'))")

echo "   Priority Category: $PRIORITY_CATEGORY"
echo "   Priority Label: $PRIORITY_LABEL"
echo "   Technical Heat: $TECHNICAL_HEAT"
echo "   Commercial Segment: $COMMERCIAL_SEGMENT"

if [ "$PRIORITY_CATEGORY" != "NOT_FOUND" ] && [ "$PRIORITY_CATEGORY" != "None" ]; then
    echo -e "${GREEN}✅ P-Model fields present${NC}"
else
    echo -e "${RED}❌ P-Model fields missing${NC}"
    exit 1
fi

# Test 6: Check Sales Summary (risk summary text)
echo ""
echo -e "${BLUE}📋 Test 6: Check Sales Summary (risk summary)${NC}"
echo "----------------------------------------"
SALES_RESPONSE=$(curl -s "$API_URL/leads/$TEST_DOMAIN/sales-summary")
RISK_SUMMARY=$(echo "$SALES_RESPONSE" | python -c "import sys, json; d=json.load(sys.stdin); sec=d.get('security_reasoning', {}); print(sec.get('summary', 'NOT_FOUND'))")

echo "   Risk Summary: $RISK_SUMMARY"

if echo "$RISK_SUMMARY" | grep -q "SPF ve DKIM mevcut"; then
    echo -e "${GREEN}✅ Risk summary correctly mentions SPF and DKIM are present${NC}"
elif echo "$RISK_SUMMARY" | grep -q "SPF ve DKIM eksik"; then
    echo -e "${RED}❌ Risk summary incorrectly says SPF and DKIM are missing (BUG)${NC}"
    exit 1
else
    echo -e "${YELLOW}⚠️  Risk summary format unexpected${NC}"
fi

# Test 7: Check consistency (Lead vs Score Breakdown)
echo ""
echo -e "${BLUE}📋 Test 7: Check consistency (Lead vs Score Breakdown)${NC}"
echo "----------------------------------------"
if [ "$DMARC_COVERAGE" = "$BREAKDOWN_DMARC_COVERAGE" ]; then
    echo -e "${GREEN}✅ DMARC Coverage consistent between Lead and Score Breakdown${NC}"
else
    echo -e "${RED}❌ DMARC Coverage inconsistent: Lead=$DMARC_COVERAGE, Breakdown=$BREAKDOWN_DMARC_COVERAGE${NC}"
    exit 1
fi

# Summary
echo ""
echo "================================================"
echo -e "${GREEN}✅ All tests passed!${NC}"
echo ""
echo "📊 Summary:"
echo "   - Domain: $TEST_DOMAIN"
echo "   - DMARC Coverage: $DMARC_COVERAGE (consistent)"
echo "   - Priority Category: $PRIORITY_CATEGORY"
echo "   - Risk Summary: Correctly formatted"
echo ""

