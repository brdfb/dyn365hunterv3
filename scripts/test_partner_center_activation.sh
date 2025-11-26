#!/bin/bash
# Partner Center Activation Test Script
# 3 Fazlı doğrulama: FAZ 0 → FAZ 1 → FAZ 2 → FAZ 3

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="http://localhost:8000"
ENV_FILE=".env"

# Helper functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 command not found. Please install it first."
        exit 1
    fi
}

# Check prerequisites
check_command docker-compose
check_command curl

# Check for jq or python (for JSON parsing)
if command -v jq &> /dev/null; then
    JSON_PARSER="jq"
elif command -v python &> /dev/null || command -v python3 &> /dev/null; then
    JSON_PARSER="python"
else
    print_error "Neither jq nor python found. Please install one of them."
    exit 1
fi

# JSON parsing helper
parse_json() {
    local key=$1
    if [ "$JSON_PARSER" = "jq" ]; then
        jq -r "$key"
    else
        python -c "import sys, json; print(json.load(sys.stdin).get('$key', 'null'))"
    fi
}

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    print_error ".env file not found!"
    exit 1
fi

# ========================================
# FAZ 0 – Ortam ve Migration
# ========================================
print_header "FAZ 0 – Ortam ve Migration"

echo "1. Checking environment variables..."
if grep -q "HUNTER_PARTNER_CENTER_CLIENT_ID" "$ENV_FILE" && \
   grep -q "HUNTER_PARTNER_CENTER_TENANT_ID" "$ENV_FILE" && \
   grep -q "HUNTER_PARTNER_CENTER_API_URL" "$ENV_FILE"; then
    print_success "Environment variables found in .env"
else
    print_error "Missing Partner Center environment variables in .env"
    exit 1
fi

echo -e "\n2. Running database migration..."
if docker-compose exec -T api alembic upgrade head 2>&1 | grep -q "Running upgrade\|INFO"; then
    print_success "Database migration completed"
else
    print_error "Database migration failed"
    exit 1
fi

echo -e "\n3. Checking partner_center_referrals table..."
if docker-compose exec -T postgres psql -U dyn365hunter -d dyn365hunter -c "\d partner_center_referrals" 2>&1 | grep -q "referral_id"; then
    print_success "partner_center_referrals table exists"
else
    print_error "partner_center_referrals table not found"
    exit 1
fi

print_success "FAZ 0 PASSED"
read -p "Press Enter to continue to FAZ 1..."

# ========================================
# FAZ 1 – Feature Flag OFF Doğrulama
# ========================================
print_header "FAZ 1 – Feature Flag OFF Doğrulama"

echo "1. Setting feature flag to OFF..."
sed -i.bak 's/HUNTER_PARTNER_CENTER_ENABLED=true/HUNTER_PARTNER_CENTER_ENABLED=false/' "$ENV_FILE"
print_info "Feature flag set to false in .env"

echo -e "\n2. Restarting services..."
docker-compose restart api worker
sleep 5
print_info "Services restarted"

echo -e "\n3. Testing health check (should return false)..."
HEALTH_RESPONSE=$(curl -s "$API_URL/healthz")
if [ "$JSON_PARSER" = "jq" ]; then
    PARTNER_CENTER_ENABLED=$(echo "$HEALTH_RESPONSE" | jq -r '.partner_center_enabled // "null"')
else
    PARTNER_CENTER_ENABLED=$(echo "$HEALTH_RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('partner_center_enabled', 'null'))")
fi

if [ "$PARTNER_CENTER_ENABLED" = "false" ]; then
    print_success "Health check returns false"
else
    print_error "Health check returned: $PARTNER_CENTER_ENABLED (expected: false)"
    exit 1
fi

echo -e "\n4. Testing API endpoint (should return 400)..."
API_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/referrals/sync" -H "Content-Type: application/json")
HTTP_CODE=$(echo "$API_RESPONSE" | tail -n1)
API_BODY=$(echo "$API_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "400" ]; then
    print_success "API endpoint returns 400 (expected)"
    if echo "$API_BODY" | grep -q "disabled"; then
        print_success "Error message contains 'disabled'"
    else
        print_warning "Error message might not be clear"
    fi
else
    print_error "API endpoint returned: $HTTP_CODE (expected: 400)"
    echo "Response: $API_BODY"
    exit 1
fi

echo -e "\n5. Testing Celery task (should return skipped)..."
TASK_RESPONSE=$(docker-compose exec -T worker celery -A app.core.celery_app call app.core.tasks.sync_partner_center_referrals_task 2>&1 | tail -n1)

if echo "$TASK_RESPONSE" | grep -q "skipped\|Feature flag disabled"; then
    print_success "Celery task returns skipped status"
else
    print_warning "Celery task response: $TASK_RESPONSE"
    print_warning "Expected: status='skipped' or 'Feature flag disabled'"
fi

echo -e "\n6. Checking worker logs..."
LOG_CHECK=$(docker-compose logs worker 2>&1 | grep -i "partner.*center\|feature.*flag" | tail -n5)
if echo "$LOG_CHECK" | grep -q "skipped\|feature_flag_disabled"; then
    print_success "Worker logs show skip/feature_flag_disabled"
else
    print_warning "Worker logs might not show expected messages"
    echo "Recent logs:"
    echo "$LOG_CHECK"
fi

print_success "FAZ 1 PASSED"
read -p "Press Enter to continue to FAZ 2..."

# ========================================
# FAZ 2 – Aktivasyon (İlk Auth + Token Cache)
# ========================================
print_header "FAZ 2 – Aktivasyon (İlk Auth + Token Cache)"

print_warning "FAZ 2 requires manual interaction!"
print_info "You need to run Device Code Flow authentication manually."
echo ""
echo "Run this command in a separate terminal:"
echo "  docker-compose exec api python"
echo ""
echo "Then run this Python code:"
cat << 'PYTHON_SCRIPT'
from msal import PublicClientApplication
from app.config import settings

app = PublicClientApplication(
    client_id=settings.partner_center_client_id,
    authority=f"https://login.microsoftonline.com/{settings.partner_center_tenant_id}"
)

flow = app.initiate_device_flow(scopes=[settings.partner_center_scope])
print("\n" + "="*60)
print("Device Code Flow - Login Instructions")
print("="*60)
print(f"\n1. Go to: {flow['verification_uri']}")
print(f"2. Enter code: {flow['user_code']}")
print("\nWaiting for authentication...")
print("="*60 + "\n")

result = app.acquire_token_by_device_flow(flow)

if "access_token" in result:
    print("✅ SUCCESS: Token acquired!")
    print(f"   Token expires in: {result.get('expires_in', 'N/A')} seconds")
else:
    print("❌ ERROR: Token acquisition failed")
    print(f"   Error: {result.get('error', 'Unknown')}")
PYTHON_SCRIPT

echo ""
read -p "Have you completed Device Code Flow authentication? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Please complete FAZ 2 authentication first"
    exit 1
fi

echo -e "\nChecking token cache..."
if docker-compose exec -T api test -f .token_cache 2>/dev/null; then
    print_success "Token cache file exists"
else
    print_warning "Token cache file not found (might be in different location)"
fi

print_success "FAZ 2 PASSED (assuming authentication completed)"
read -p "Press Enter to continue to FAZ 3..."

# ========================================
# FAZ 3 – Feature Flag ON Doğrulama
# ========================================
print_header "FAZ 3 – Feature Flag ON Doğrulama"

echo "1. Setting feature flag to ON..."
sed -i.bak 's/HUNTER_PARTNER_CENTER_ENABLED=false/HUNTER_PARTNER_CENTER_ENABLED=true/' "$ENV_FILE"
print_info "Feature flag set to true in .env"

echo -e "\n2. Restarting services..."
docker-compose restart api worker
sleep 5
print_info "Services restarted"

echo -e "\n3. Testing health check (should return true)..."
HEALTH_RESPONSE=$(curl -s "$API_URL/healthz")
if [ "$JSON_PARSER" = "jq" ]; then
    PARTNER_CENTER_ENABLED=$(echo "$HEALTH_RESPONSE" | jq -r '.partner_center_enabled // "null"')
else
    PARTNER_CENTER_ENABLED=$(echo "$HEALTH_RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('partner_center_enabled', 'null'))")
fi

if [ "$PARTNER_CENTER_ENABLED" = "true" ]; then
    print_success "Health check returns true"
else
    print_error "Health check returned: $PARTNER_CENTER_ENABLED (expected: true)"
    exit 1
fi

echo -e "\n4. Testing API endpoint (should return 200)..."
API_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/referrals/sync" -H "Content-Type: application/json")
HTTP_CODE=$(echo "$API_RESPONSE" | tail -n1)
API_BODY=$(echo "$API_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    print_success "API endpoint returns 200 (expected)"
    if [ "$JSON_PARSER" = "jq" ]; then
        TASK_ID=$(echo "$API_BODY" | jq -r '.task_id // "null"')
    else
        TASK_ID=$(echo "$API_BODY" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('task_id', 'null'))")
    fi
    if [ "$TASK_ID" != "null" ] && [ "$TASK_ID" != "" ]; then
        print_success "Task ID received: $TASK_ID"
    else
        print_warning "Task ID might be missing"
    fi
elif [ "$HTTP_CODE" = "500" ]; then
    print_error "API endpoint returned 500 (token cache might be missing)"
    echo "Response: $API_BODY"
    print_warning "Please check FAZ 2 - token cache might not be created"
    exit 1
else
    print_error "API endpoint returned: $HTTP_CODE (expected: 200)"
    echo "Response: $API_BODY"
    exit 1
fi

echo -e "\n5. Checking worker logs..."
sleep 3  # Wait for task to start
LOG_CHECK=$(docker-compose logs worker 2>&1 | grep -i "partner.*center\|referral" | tail -n10)
if echo "$LOG_CHECK" | grep -q "sync.*started\|fetching.*referrals"; then
    print_success "Worker logs show sync activity"
else
    print_warning "Worker logs might not show expected activity"
    echo "Recent logs:"
    echo "$LOG_CHECK"
fi

# Check for errors
if echo "$LOG_CHECK" | grep -qi "error\|exception\|traceback"; then
    print_error "Errors found in worker logs!"
    echo "Error logs:"
    echo "$LOG_CHECK" | grep -i "error\|exception\|traceback"
    exit 1
else
    print_success "No errors found in worker logs"
fi

print_success "FAZ 3 PASSED"

# ========================================
# Final Summary
# ========================================
print_header "Test Summary"

echo "✅ FAZ 0: Ortam ve Migration - PASSED"
echo "✅ FAZ 1: Feature Flag OFF Doğrulama - PASSED"
echo "✅ FAZ 2: Aktivasyon (İlk Auth + Token Cache) - PASSED"
echo "✅ FAZ 3: Feature Flag ON Doğrulama - PASSED"
echo ""
print_success "All phases passed! Partner Center activation is ready."
echo ""
print_info "Current environment: $(grep ENVIRONMENT "$ENV_FILE" | cut -d'=' -f2)"
echo ""
print_warning "Decision Matrix:"
echo "  - DEV: Flag can stay ON ✅"
echo "  - STAGING: Flag can be ON ✅"
echo "  - PROD: Decide based on your needs"
echo ""
print_info "Feature flag is currently: $(grep HUNTER_PARTNER_CENTER_ENABLED "$ENV_FILE" | cut -d'=' -f2)"

