#!/bin/bash
# Smoke Tests for Hunter v1.0 Production
# Standalone smoke test script for production verification
#
# Usage:
#   bash scripts/smoke_tests.sh [API_URL] [API_KEY]
#
# Environment Variables:
#   API_URL    : API base URL (default: http://localhost:8000)
#   API_KEY    : API key for authenticated endpoints (optional)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
API_KEY="${API_KEY:-}"

# Test counter
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

log_error() {
    echo -e "${RED}❌ $1${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    TESTS_WARNED=$((TESTS_WARNED + 1))
}

# Test helper function
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_status="${3:-200}"
    
    log_info "Testing: $test_name"
    
    local status_code
    local response
    
    if response=$(eval "$test_command" 2>&1); then
        status_code=$(echo "$response" | grep -oP '(?<=HTTP/)[0-9]{3}' | tail -1 || echo "200")
        
        if [ "$status_code" = "$expected_status" ] || [ -z "$status_code" ]; then
            log_success "$test_name: OK (status: ${status_code:-200})"
            return 0
        else
            log_error "$test_name: FAILED (expected: $expected_status, got: $status_code)"
            return 1
        fi
    else
        log_error "$test_name: FAILED (command error)"
        return 1
    fi
}

# Main smoke tests
main() {
    echo ""
    echo "=========================================================="
    echo "🧪 Hunter v1.0 Production Smoke Tests"
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
    if curl -sf "$API_URL/healthz/live" > /dev/null 2>&1; then
        log_success "Liveness probe: OK"
    else
        log_error "Liveness probe: FAILED"
    fi
    
    # Readiness
    if curl -sf "$API_URL/healthz/ready" > /dev/null 2>&1; then
        log_success "Readiness probe: OK"
    else
        log_error "Readiness probe: FAILED"
    fi
    
    # Startup
    if curl -sf "$API_URL/healthz/startup" > /dev/null 2>&1; then
        log_success "Startup probe: OK"
    else
        log_warning "Startup probe: FAILED (may be normal if already started)"
    fi
    
    # Metrics
    if curl -sf "$API_URL/healthz/metrics" > /dev/null 2>&1; then
        log_success "Metrics endpoint: OK"
    else
        log_warning "Metrics endpoint: FAILED (may be optional)"
    fi
    
    echo ""
    
    # Test 2: Core Endpoints
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Test 2: Core Endpoints"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Leads endpoint
    if curl -sf "$API_URL/api/v1/leads?limit=1" > /dev/null 2>&1; then
        log_success "Leads endpoint: OK"
    else
        log_error "Leads endpoint: FAILED"
    fi
    
    # Leads with filters
    if curl -sf "$API_URL/api/v1/leads?limit=5&provider=M365" > /dev/null 2>&1; then
        log_success "Leads endpoint (with filters): OK"
    else
        log_warning "Leads endpoint (with filters): FAILED (may be normal if no M365 leads)"
    fi
    
    echo ""
    
    # Test 3: Sales Engine
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Test 3: Sales Engine Endpoint"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Test with a non-existent domain (should return 404)
    local status_code
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/v1/leads/test-nonexistent-$(date +%s).invalid/sales-summary" 2>/dev/null || echo "000")
    
    if [ "$status_code" = "404" ]; then
        log_success "Sales Engine endpoint: OK (404 for non-existent domain is expected)"
    elif [ "$status_code" = "200" ]; then
        log_warning "Sales Engine endpoint: OK (200 returned, domain may exist)"
    else
        log_error "Sales Engine endpoint: FAILED (status: $status_code)"
    fi
    
    echo ""
    
    # Test 4: Scan Endpoint (if API key provided)
    if [ -n "$API_KEY" ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 Test 4: Scan Endpoint (with API key)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        local scan_response
        scan_response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/v1/scan" \
            -H "Content-Type: application/json" \
            -H "X-API-Key: $API_KEY" \
            -d '{"domain": "example.com"}' 2>&1)
        
        local scan_status
        scan_status=$(echo "$scan_response" | tail -1)
        
        if [ "$scan_status" = "200" ] || [ "$scan_status" = "202" ]; then
            log_success "Scan endpoint: OK (status: $scan_status)"
        else
            log_warning "Scan endpoint: FAILED or RATE LIMITED (status: $scan_status)"
        fi
        
        echo ""
    else
        log_info "Skipping scan endpoint test (API_KEY not provided)"
        echo ""
    fi
    
    # Summary
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Test Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    echo -e "Warnings: ${YELLOW}$TESTS_WARNED${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ All critical smoke tests passed!${NC}"
        echo ""
        echo "Hunter v1.0 is ready for production use."
        exit 0
    else
        echo -e "${RED}❌ Some smoke tests failed${NC}"
        echo ""
        echo "Please review the errors above before proceeding with production deployment."
        exit 1
    fi
}

# Run main function
main

