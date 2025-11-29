#!/bin/bash
# Pre-Deployment Verification Script
# Checks all required environment variables and connections before production deployment
#
# Usage:
#   bash scripts/pre_deployment_check.sh
#
# This script checks:
#   - Environment variables (required + optional)
#   - Database connection
#   - Redis connection
#   - Health endpoints
#   - Sentry configuration

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    PASSED=$((PASSED + 1))
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    WARNINGS=$((WARNINGS + 1))
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    FAILED=$((FAILED + 1))
}

# Check function
check() {
    local name="$1"
    local command="$2"
    local expected="$3"
    
    log_info "Checking: $name"
    
    if eval "$command" > /dev/null 2>&1; then
        log_success "$name: OK"
        return 0
    else
        log_error "$name: FAILED (Expected: $expected)"
        return 1
    fi
}

echo "=========================================="
echo "Pre-Deployment Verification Script"
echo "=========================================="
echo ""

# 1. Environment Variables
echo "=== 1. Environment Variables ==="

# Required
if [ -z "$ENVIRONMENT" ]; then
    log_error "ENVIRONMENT: NOT SET (Required: production)"
else
    if [ "$ENVIRONMENT" = "production" ]; then
        log_success "ENVIRONMENT: $ENVIRONMENT"
    else
        log_warning "ENVIRONMENT: $ENVIRONMENT (Expected: production)"
    fi
fi

if [ -z "$DATABASE_URL" ]; then
    log_error "DATABASE_URL: NOT SET (Required)"
else
    log_success "DATABASE_URL: SET (${DATABASE_URL:0:20}...)"
fi

if [ -z "$REDIS_URL" ]; then
    log_error "REDIS_URL: NOT SET (Required)"
else
    log_success "REDIS_URL: SET (${REDIS_URL:0:20}...)"
fi

if [ -z "$LOG_LEVEL" ]; then
    log_warning "LOG_LEVEL: NOT SET (Default: INFO)"
else
    if [ "$LOG_LEVEL" = "INFO" ] || [ "$LOG_LEVEL" = "WARNING" ]; then
        log_success "LOG_LEVEL: $LOG_LEVEL"
    else
        log_warning "LOG_LEVEL: $LOG_LEVEL (Recommended: INFO or WARNING for production)"
    fi
fi

# Optional (but recommended)
if [ -z "$HUNTER_SENTRY_DSN" ]; then
    log_warning "HUNTER_SENTRY_DSN: NOT SET (Strongly recommended for production)"
else
    log_success "HUNTER_SENTRY_DSN: SET"
fi

# Feature Flags
if [ -z "$HUNTER_PARTNER_CENTER_ENABLED" ]; then
    log_info "HUNTER_PARTNER_CENTER_ENABLED: NOT SET (Default: false)"
else
    log_info "HUNTER_PARTNER_CENTER_ENABLED: $HUNTER_PARTNER_CENTER_ENABLED"
fi

if [ -z "$HUNTER_D365_ENABLED" ]; then
    log_info "HUNTER_D365_ENABLED: NOT SET (Default: false)"
else
    log_info "HUNTER_D365_ENABLED: $HUNTER_D365_ENABLED"
fi

echo ""

# 2. Database Connection
echo "=== 2. Database Connection ==="

if command -v docker-compose > /dev/null 2>&1; then
    # Check PostgreSQL is ready
    if docker-compose exec -T postgres pg_isready -U dyn365hunter > /dev/null 2>&1; then
        log_success "PostgreSQL: Ready"
    else
        log_error "PostgreSQL: Not ready"
    fi
    
    # Test database connection from application
    if docker-compose exec -T api python -c "
from app.db.session import SessionLocal
try:
    db = SessionLocal()
    db.execute('SELECT 1')
    print('OK')
except Exception as e:
    print(f'FAILED: {e}')
    exit(1)
" > /dev/null 2>&1; then
        log_success "Database Connection: OK"
    else
        log_error "Database Connection: FAILED"
    fi
else
    log_warning "docker-compose not found, skipping database connection test"
fi

echo ""

# 3. Redis Connection
echo "=== 3. Redis Connection ==="

if command -v docker-compose > /dev/null 2>&1; then
    # Redis PING
    if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
        log_success "Redis PING: PONG"
    else
        log_error "Redis PING: FAILED"
    fi
    
    # Redis connection from application
    if docker-compose exec -T api python -c "
from app.core.redis_client import get_redis_client
try:
    r = get_redis_client()
    if r.ping():
        print('OK')
    else:
        print('FAILED')
        exit(1)
except Exception as e:
    print(f'FAILED: {e}')
    exit(1)
" > /dev/null 2>&1; then
        log_success "Redis Connection (from app): OK"
    else
        log_error "Redis Connection (from app): FAILED"
    fi
else
    log_warning "docker-compose not found, skipping Redis connection test"
fi

echo ""

# 4. Health Endpoints
echo "=== 4. Health Endpoints ==="

API_URL="${API_URL:-http://localhost:8000}"

# Liveness
if curl -s -f "$API_URL/healthz/live" > /dev/null 2>&1; then
    log_success "Health Check (Liveness): OK"
else
    log_error "Health Check (Liveness): FAILED"
fi

# Readiness
if curl -s -f "$API_URL/healthz/ready" > /dev/null 2>&1; then
    log_success "Health Check (Readiness): OK"
else
    log_error "Health Check (Readiness): FAILED"
fi

# Startup
if curl -s -f "$API_URL/healthz/startup" > /dev/null 2>&1; then
    log_success "Health Check (Startup): OK"
else
    log_error "Health Check (Startup): FAILED"
fi

# Metrics
if curl -s -f "$API_URL/healthz/metrics" > /dev/null 2>&1; then
    log_success "Health Check (Metrics): OK"
else
    log_warning "Health Check (Metrics): FAILED (Optional)"
fi

echo ""

# 5. Summary
echo "=========================================="
echo "Summary"
echo "=========================================="
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✅ All checks passed! Ready for deployment.${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  All critical checks passed, but there are warnings. Review before deployment.${NC}"
        exit 0
    fi
else
    echo -e "${RED}❌ Some checks failed. Please fix issues before deployment.${NC}"
    exit 1
fi

