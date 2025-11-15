#!/bin/bash
# Azure AD Authentication Test Script
# Tests Azure AD authentication endpoints

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
AUTH_BASE="${AUTH_BASE:-${BASE_URL}/auth}"

echo "=========================================="
echo "Azure AD Authentication Test"
echo "=========================================="
echo "Base URL: ${BASE_URL}"
echo "Auth Base: ${AUTH_BASE}"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health check
echo -e "${YELLOW}Test 1: Health Check${NC}"
if curl -s -f "${BASE_URL}/healthz" > /dev/null; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not running. Please start the backend first.${NC}"
    echo "  Run: docker-compose up api"
    echo "  Or: python -m uvicorn app.main:app --reload"
    exit 1
fi
echo ""

# Test 2: Check Azure AD client status
echo -e "${YELLOW}Test 2: Azure AD Client Status${NC}"
response=$(curl -s "${AUTH_BASE}/login" -w "\n%{http_code}" || echo "000")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "503" ]; then
    echo -e "${RED}✗ Azure AD is not configured${NC}"
    echo "  Check .env file for:"
    echo "    - HUNTER_AZURE_CLIENT_ID"
    echo "    - HUNTER_AZURE_CLIENT_SECRET"
    echo "    - HUNTER_AZURE_TENANT_ID"
    exit 1
elif [ "$http_code" = "302" ] || [ "$http_code" = "307" ]; then
    echo -e "${GREEN}✓ Azure AD is configured and redirecting${NC}"
    redirect_url=$(echo "$response" | grep -i "location:" | cut -d' ' -f2 || echo "")
    if [ -n "$redirect_url" ]; then
        echo "  Redirect URL: $redirect_url"
        if echo "$redirect_url" | grep -q "login.microsoftonline.com"; then
            echo -e "${GREEN}✓ Redirect URL points to Microsoft login${NC}"
        else
            echo -e "${YELLOW}⚠ Redirect URL doesn't look like Microsoft login${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠ Unexpected response: HTTP $http_code${NC}"
fi
echo ""

# Test 3: Get authorization URL (check redirect)
echo -e "${YELLOW}Test 3: Login Endpoint (Authorization URL)${NC}"
response=$(curl -s -L -w "\n%{http_code}" "${AUTH_BASE}/login" 2>&1 || echo "000")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Login endpoint redirects correctly${NC}"
    echo "  Note: Full OAuth flow requires browser interaction"
elif [ "$http_code" = "302" ] || [ "$http_code" = "307" ]; then
    echo -e "${GREEN}✓ Login endpoint redirects to Azure AD${NC}"
    redirect_url=$(echo "$response" | grep -i "location:" | cut -d' ' -f2 || echo "")
    if [ -n "$redirect_url" ]; then
        echo "  Redirect to: $redirect_url"
    fi
else
    echo -e "${YELLOW}⚠ Unexpected response: HTTP $http_code${NC}"
fi
echo ""

# Test 4: Callback endpoint (should fail without code)
echo -e "${YELLOW}Test 4: Callback Endpoint (without code)${NC}"
response=$(curl -s "${AUTH_BASE}/callback" -w "\n%{http_code}" || echo "000")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "400" ]; then
    echo -e "${GREEN}✓ Callback endpoint correctly rejects requests without code${NC}"
else
    echo -e "${YELLOW}⚠ Unexpected response: HTTP $http_code${NC}"
    echo "  Response: $(echo "$response" | head -n1)"
fi
echo ""

# Test 5: Check /auth/me endpoint (requires token)
echo -e "${YELLOW}Test 5: /auth/me Endpoint (requires authentication)${NC}"
response=$(curl -s "${AUTH_BASE}/me" -w "\n%{http_code}" || echo "000")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
    echo -e "${GREEN}✓ /auth/me correctly requires authentication${NC}"
else
    echo -e "${YELLOW}⚠ Unexpected response: HTTP $http_code${NC}"
fi
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Open browser and navigate to: ${AUTH_BASE}/login"
echo "2. Complete Microsoft login"
echo "3. You should be redirected to: ${AUTH_BASE}/callback"
echo "4. After successful login, you'll be redirected to frontend with tokens"
echo ""
echo "Manual Test:"
echo "  curl -v ${AUTH_BASE}/login"
echo "  # Follow redirects to complete OAuth flow"
echo ""

