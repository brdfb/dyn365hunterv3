#!/bin/bash

# Production UAT Log Check Script
# Verifies logging for P-Model and Sales Summary operations

set -e

echo "📋 Production UAT Log Check - CSP P-Model + Sales Summary v1.1"
echo "=========================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check for score_domain events
echo -e "${BLUE}1. Checking score_domain events...${NC}"
SCORE_EVENTS=$(docker-compose logs api 2>/dev/null | grep -i "score_domain" | tail -5 || echo "")
if [ -n "$SCORE_EVENTS" ]; then
    echo -e "${GREEN}✅ Found score_domain events${NC}"
    echo "$SCORE_EVENTS" | head -2
    echo ""
    
    # Check for P-Model fields in logs
    if echo "$SCORE_EVENTS" | grep -qE "priority_category|commercial_segment|technical_heat"; then
        echo -e "${GREEN}✅ P-Model fields found in logs${NC}"
    else
        echo -e "${YELLOW}⚠️  P-Model fields may not be logged${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No score_domain events found. Scan a domain first.${NC}"
fi
echo ""

# Check for sales_summary_viewed events
echo -e "${BLUE}2. Checking sales_summary_viewed events...${NC}"
SALES_EVENTS=$(docker-compose logs api 2>/dev/null | grep -i "sales_summary_viewed" | tail -5 || echo "")
if [ -n "$SALES_EVENTS" ]; then
    echo -e "${GREEN}✅ Found sales_summary_viewed events${NC}"
    echo "$SALES_EVENTS" | head -2
    echo ""
    
    # Check for structured fields
    if echo "$SALES_EVENTS" | grep -qE "segment|offer_tier|opportunity_potential|urgency"; then
        echo -e "${GREEN}✅ Structured fields found in logs${NC}"
    else
        echo -e "${YELLOW}⚠️  Structured fields may not be logged${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No sales_summary_viewed events found. View a sales summary first.${NC}"
fi
echo ""

# Check for PII leakage
echo -e "${BLUE}3. Checking for PII leakage...${NC}"
PII_CHECK=$(docker-compose logs api 2>/dev/null | grep -iE "email|company_name|@.*\." | head -5 || echo "")
if [ -n "$PII_CHECK" ]; then
    echo -e "${RED}❌ Potential PII found in logs!${NC}"
    echo "$PII_CHECK"
    echo ""
    echo -e "${YELLOW}⚠️  Review logs for PII leakage${NC}"
else
    echo -e "${GREEN}✅ No PII found in logs (domain-only logging)${NC}"
fi
echo ""

# Check log level
echo -e "${BLUE}4. Checking log level...${NC}"
LOG_LEVEL=$(docker-compose exec -T api env | grep "LOG_LEVEL" || echo "LOG_LEVEL=INFO")
echo "   $LOG_LEVEL"
if echo "$LOG_LEVEL" | grep -q "LOG_LEVEL=INFO"; then
    echo -e "${GREEN}✅ Log level is INFO${NC}"
else
    echo -e "${YELLOW}⚠️  Log level may not be INFO${NC}"
fi
echo ""

# Summary
echo "=========================================================="
echo -e "${GREEN}✅ Log Check Completed!${NC}"
echo ""
echo "📋 Expected Log Format:"
echo '   {'
echo '     "event": "score_domain",'
echo '     "domain": "example.com",'
echo '     "priority_category": "P2",'
echo '     "commercial_segment": "COMPETITIVE",'
echo '     "technical_heat": "Hot",'
echo '     "level": "INFO"'
echo '   }'
echo ""
echo "📖 For detailed log analysis, use:"
echo "   docker-compose logs api | jq '.'"
echo ""

