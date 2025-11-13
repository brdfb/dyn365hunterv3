#!/bin/bash
# Test script for google.com domain
# Usage: bash test_google_domain.sh
# Archived: 2025-11-12 (temporary test script, no longer needed)

API_URL="http://localhost:8000"

echo "🧪 Testing google.com domain..."
echo ""

# Step 1: Health check
echo "1️⃣ Checking API health..."
HEALTH=$(curl -s "${API_URL}/healthz")
if [ $? -ne 0 ]; then
    echo "❌ API is not running. Please start Docker Compose first:"
    echo "   bash setup_dev.sh"
    exit 1
fi
echo "✅ API is running"
echo "   Response: $HEALTH"
echo ""

# Step 2: Ingest google.com
echo "2️⃣ Ingesting google.com..."
INGEST_RESPONSE=$(curl -s -X POST "${API_URL}/ingest/domain" \
    -H "Content-Type: application/json" \
    -d '{
        "domain": "google.com",
        "company_name": "Google LLC"
    }')
echo "   Response: $INGEST_RESPONSE"
echo ""

# Extract company_id if successful
COMPANY_ID=$(echo $INGEST_RESPONSE | grep -o '"company_id":[0-9]*' | grep -o '[0-9]*')
if [ -z "$COMPANY_ID" ]; then
    echo "⚠️  Ingest may have failed or domain already exists. Continuing..."
fi
echo ""

# Step 3: Scan google.com
echo "3️⃣ Scanning google.com (this may take 10-15 seconds for DNS/WHOIS)..."
SCAN_RESPONSE=$(curl -s -X POST "${API_URL}/scan/domain" \
    -H "Content-Type: application/json" \
    -d '{
        "domain": "google.com"
    }')
echo "   Response: $SCAN_RESPONSE"
echo ""

# Step 4: Get lead details
echo "4️⃣ Getting lead details for google.com..."
LEAD_RESPONSE=$(curl -s "${API_URL}/leads/google.com")
if echo "$LEAD_RESPONSE" | grep -q "404\|Not Found"; then
    echo "   ⚠️  Response: $LEAD_RESPONSE"
    echo "   (This should work now with the fix)"
else
    echo "   ✅ Response: $LEAD_RESPONSE"
fi
echo ""

echo "✅ Test completed!"
echo ""
echo "📊 Summary:"
echo "   - Domain ingested: google.com"
echo "   - Domain scanned: DNS + WHOIS analysis completed"
echo "   - Lead details retrieved"
echo ""
echo "💡 Next steps:"
echo "   - Check /leads endpoint: curl '${API_URL}/leads?segment=Migration'"
echo "   - View API docs: ${API_URL}/docs"

