#!/bin/bash
# Demo script for Dyn365Hunter MVP - "Kahvelik" analysis flow
# Archived: 2025-11-12 (MVP completed, demo script no longer in active use)

set -e

API_URL="http://localhost:8000"

echo "🎬 Dyn365Hunter MVP Demo - Kahvelik Analysis Flow"
echo "=================================================="
echo ""

# Check if API is running
if ! curl -f -s "${API_URL}/healthz" > /dev/null; then
    echo "❌ API is not running. Please run: bash setup_dev.sh"
    exit 1
fi

echo "✅ API is running"
echo ""

# Demo domains
DOMAINS=("example.com" "google.com" "microsoft.com")

echo "📥 Step 1: Ingesting domains..."
for domain in "${DOMAINS[@]}"; do
    echo "   Ingesting: ${domain}"
    curl -s -X POST "${API_URL}/ingest/domain" \
        -H "Content-Type: application/json" \
        -d "{\"domain\": \"${domain}\", \"company_name\": \"${domain^} Inc\"}" \
        > /dev/null
done
echo "✅ ${#DOMAINS[@]} domains ingested"
echo ""

echo "🔍 Step 2: Scanning domains (this may take 10-15 seconds per domain)..."
for domain in "${DOMAINS[@]}"; do
    echo "   Scanning: ${domain}"
    curl -s -X POST "${API_URL}/scan/domain" \
        -H "Content-Type: application/json" \
        -d "{\"domain\": \"${domain}\"}" \
        | python3 -m json.tool 2>/dev/null | grep -E "(domain|score|segment|provider)" || true
    echo ""
done
echo "✅ Scanning complete"
echo ""

echo "📊 Step 3: Querying Migration leads (min_score=70)..."
curl -s "${API_URL}/leads?segment=Migration&min_score=70" \
    | python3 -m json.tool 2>/dev/null | head -30 || \
    curl -s "${API_URL}/leads?segment=Migration&min_score=70" | head -30
echo ""

echo "🎉 Demo complete!"
echo ""
echo "📋 Try these commands:"
echo "   curl \"${API_URL}/leads?segment=Migration&min_score=70\""
echo "   curl \"${API_URL}/lead/example.com\""
echo "   curl \"${API_URL}/docs\"  # API documentation"

