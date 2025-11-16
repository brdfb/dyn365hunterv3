#!/bin/bash
# Sales Engine Smoke Test Script
# Tests real domains across different segments

echo "=========================================="
echo "Sales Engine Smoke Test"
echo "=========================================="
echo ""

BASE_URL="${BASE_URL:-http://localhost:8000}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test domains (update these with real domains from your database)
MIGRATION_DOMAIN="${MIGRATION_DOMAIN:-migration-test.com}"
EXISTING_DOMAIN="${EXISTING_DOMAIN:-existing-test.com}"
COLD_DOMAIN="${COLD_DOMAIN:-cold-test.com}"

echo "Testing domains:"
echo "  Migration: $MIGRATION_DOMAIN"
echo "  Existing:  $EXISTING_DOMAIN"
echo "  Cold:      $COLD_DOMAIN"
echo ""

# Function to test a domain
test_domain() {
    local domain=$1
    local expected_segment=$2
    local description=$3
    
    echo "----------------------------------------"
    echo "Testing: $description"
    echo "Domain: $domain"
    echo "Expected Segment: $expected_segment"
    echo "----------------------------------------"
    
    response=$(curl -s "${BASE_URL}/api/v1/leads/${domain}/sales-summary")
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to connect to API${NC}"
        return 1
    fi
    
    # Check if response is valid JSON (try to parse, but continue even if jq fails)
    echo "$response" | jq . > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        # Try to extract fields without jq if jq fails
        echo -e "${YELLOW}⚠ jq parse warning, trying alternative parsing${NC}"
    fi
    
    # Extract key fields
    segment=$(echo "$response" | jq -r '.metadata.segment // "N/A"')
    offer_tier=$(echo "$response" | jq -r '.offer_tier.tier // "N/A"')
    opportunity_potential=$(echo "$response" | jq -r '.opportunity_potential // "N/A"')
    urgency=$(echo "$response" | jq -r '.urgency // "N/A"')
    one_liner=$(echo "$response" | jq -r '.one_liner // "N/A"')
    call_script_count=$(echo "$response" | jq '.call_script | length')
    questions_count=$(echo "$response" | jq '.discovery_questions | length')
    
    echo ""
    echo "Results:"
    echo "  Segment: $segment"
    echo "  Offer Tier: $offer_tier"
    echo "  Opportunity Potential: $opportunity_potential"
    echo "  Urgency: $urgency"
    echo "  Call Script Bullets: $call_script_count"
    echo "  Discovery Questions: $questions_count"
    echo ""
    echo "One-liner:"
    echo "  $one_liner"
    echo ""
    
    # Validation checks
    local issues=0
    
    if [ "$segment" != "$expected_segment" ]; then
        echo -e "${YELLOW}⚠ Segment mismatch: Expected $expected_segment, got $segment${NC}"
        issues=$((issues + 1))
    else
        echo -e "${GREEN}✓ Segment matches expected${NC}"
    fi
    
    if [ "$offer_tier" == "N/A" ] || [ -z "$offer_tier" ]; then
        echo -e "${YELLOW}⚠ Offer tier is missing${NC}"
        issues=$((issues + 1))
    else
        echo -e "${GREEN}✓ Offer tier present: $offer_tier${NC}"
    fi
    
    if [ "$opportunity_potential" == "N/A" ] || [ -z "$opportunity_potential" ]; then
        echo -e "${YELLOW}⚠ Opportunity potential is missing${NC}"
        issues=$((issues + 1))
    else
        if [ "$opportunity_potential" -ge 0 ] && [ "$opportunity_potential" -le 100 ]; then
            echo -e "${GREEN}✓ Opportunity potential valid: $opportunity_potential${NC}"
        else
            echo -e "${RED}✗ Opportunity potential out of range: $opportunity_potential${NC}"
            issues=$((issues + 1))
        fi
    fi
    
    if [ "$urgency" != "low" ] && [ "$urgency" != "medium" ] && [ "$urgency" != "high" ]; then
        echo -e "${RED}✗ Invalid urgency value: $urgency${NC}"
        issues=$((issues + 1))
    else
        echo -e "${GREEN}✓ Urgency valid: $urgency${NC}"
    fi
    
    if [ "$call_script_count" -lt 1 ]; then
        echo -e "${YELLOW}⚠ Call script is empty${NC}"
        issues=$((issues + 1))
    else
        echo -e "${GREEN}✓ Call script has $call_script_count bullets${NC}"
    fi
    
    if [ "$questions_count" -lt 1 ]; then
        echo -e "${YELLOW}⚠ Discovery questions are empty${NC}"
        issues=$((issues + 1))
    else
        echo -e "${GREEN}✓ Discovery questions has $questions_count items${NC}"
    fi
    
    echo ""
    if [ $issues -eq 0 ]; then
        echo -e "${GREEN}✓ All checks passed for $domain${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Found $issues issue(s) for $domain${NC}"
        return 1
    fi
}

# Run tests
total_issues=0

test_domain "$MIGRATION_DOMAIN" "Migration" "Migration Segment (Local → M365)"
total_issues=$((total_issues + $?))

test_domain "$EXISTING_DOMAIN" "Existing" "Existing Segment (M365 Customer)"
total_issues=$((total_issues + $?))

test_domain "$COLD_DOMAIN" "Cold" "Cold Segment (Unknown/Google)"
total_issues=$((total_issues + $?))

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
if [ $total_issues -eq 0 ]; then
    echo -e "${GREEN}✓ All smoke tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ Found issues in $total_issues domain(s)${NC}"
    echo "Review the output above for details"
    exit 1
fi

