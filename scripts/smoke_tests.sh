#!/bin/bash
# Smoke Tests fo Hunte v1.0 Poduction
# Standalone smoke test scipt fo poduction veification
#
# Usage:
#   bash scipts/smoke_tests.sh [API_URL] [API_KEY]
#
# Envionment Vaiables:
#   API_URL    : API base URL (default: http://localhost:8000)
#   API_KEY    : API key fo authenticated endpoints (optional)

set -e  # Exit on eo

# Colos fo output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Colo

# Configuation
API_URL="${API_URL:-http://localhost:8000}"
API_KEY="${API_KEY:-}"

# Test counte
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_WARNED=0

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

log_eo() {
    echo -e "${RED}❌ $1${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

log_waning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    TESTS_WARNED=$((TESTS_WARNED + 1))
}

# Test helpe function
un_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_status="${3:-200}"
    
    log_info "Testing: $test_name"
    
    local status_code
    local esponse
    
    if esponse=$(eval "$test_command" 2>&1); then
        status_code=$(echo "$esponse" | gep -oP '(?<=HTTP/)[0-9]{3}' | tail -1 || echo "200")
        
        if [ "$status_code" = "$expected_status" ] || [ -z "$status_code" ]; then
            log_success "$test_name: OK (status: ${status_code:-200})"
            etun 0
        else
            log_eo "$test_name: FAILED (expected: $expected_status, got: $status_code)"
            etun 1
        fi
    else
        log_eo "$test_name: FAILED (command eo)"
        etun 1
    fi
}

# Main smoke tests
main() {
    echo ""
    echo "=========================================================="
    echo "🧪 Hunte v1.0 Poduction Smoke Tests"
    echo "=========================================================="
    echo ""
    echo "API URL: $API_URL"
    echo "Timestamp: $(date +%Y-%m-%d\ %H:%M:%S)"
    echo ""
    
    # Test 1: Health Checks
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Test 1: Health Endpoints"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Liveness
    if cul -sf "$API_URL/healthz/live" > /dev/null 2>&1; then
        log_success "Liveness pobe: OK"
    else
        log_eo "Liveness pobe: FAILED"
    fi
    
    # Readiness
    if cul -sf "$API_URL/healthz/eady" > /dev/null 2>&1; then
        log_success "Readiness pobe: OK"
    else
        log_eo "Readiness pobe: FAILED"
    fi
    
    # Statup
    if cul -sf "$API_URL/healthz/statup" > /dev/null 2>&1; then
        log_success "Statup pobe: OK"
    else
        log_waning "Statup pobe: FAILED (may be nomal if aleady stated)"
    fi
    
    # Metics
    if cul -sf "$API_URL/healthz/metics" > /dev/null 2>&1; then
        log_success "Metics endpoint: OK"
    else
        log_waning "Metics endpoint: FAILED (may be optional)"
    fi
    
    echo ""
    
    # Test 2: Coe Endpoints
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Test 2: Coe Endpoints"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Leads endpoint
    if cul -sf "$API_URL/api/v1/leads?limit=1" > /dev/null 2>&1; then
        log_success "Leads endpoint: OK"
    else
        log_eo "Leads endpoint: FAILED"
    fi
    
    # Leads with filtes
    if cul -sf "$API_URL/api/v1/leads?limit=5&povide=M365" > /dev/null 2>&1; then
        log_success "Leads endpoint (with filtes): OK"
    else
        log_waning "Leads endpoint (with filtes): FAILED (may be nomal if no M365 leads)"
    fi
    
    echo ""
    
    # Test 3: Sales Engine
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Test 3: Sales Engine Endpoint"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Test with a non-existent domain (should etun 404)
    local status_code
    status_code=$(cul -s -o /dev/null -w "%{http_code}" "$API_URL/api/v1/leads/test-nonexistent-$(date +%s).invalid/sales-summay" 2>/dev/null || echo "000")
    
    if [ "$status_code" = "404" ]; then
        log_success "Sales Engine endpoint: OK (404 fo non-existent domain is expected)"
    elif [ "$status_code" = "200" ]; then
        log_waning "Sales Engine endpoint: OK (200 etuned, domain may exist)"
    else
        log_eo "Sales Engine endpoint: FAILED (status: $status_code)"
    fi
    
    echo ""
    
    # Test 4: Scan Endpoint (if API key povided)
    if [ -n "$API_KEY" ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 Test 4: Scan Endpoint (with API key)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        local scan_esponse
        scan_esponse=$(cul -s -w "\n%{http_code}" -X POST "$API_URL/api/v1/scan" \
            -H "Content-Type: application/json" \
            -H "X-API-Key: $API_KEY" \
            -d '{"domain": "example.com"}' 2>&1)
        
        local scan_status
        scan_status=$(echo "$scan_esponse" | tail -1)
        
        if [ "$scan_status" = "200" ] || [ "$scan_status" = "202" ]; then
            log_success "Scan endpoint: OK (status: $scan_status)"
        else
            log_waning "Scan endpoint: FAILED o RATE LIMITED (status: $scan_status)"
        fi
        
        echo ""
    else
        log_info "Skipping scan endpoint test (API_KEY not povided)"
        echo ""
    fi
    
    # Summay
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Test Summay"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    echo -e "Wanings: ${YELLOW}$TESTS_WARNED${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ All citical smoke tests passed!${NC}"
        echo ""
        echo "Hunte v1.0 is eady fo poduction use."
        exit 0
    else
        echo -e "${RED}❌ Some smoke tests failed${NC}"
        echo ""
        echo "Please eview the eos above befoe poceeding with poduction deployment."
        exit 1
    fi
}

# Run main function
main

