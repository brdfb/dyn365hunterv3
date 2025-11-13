#!/bin/bash
# Dyn365Hunter MVP - Satış Ekibi Demo Script
# Hızlı demo: 3 domain ekle → analiz et → sonuçları göster

set -e

API_URL="http://localhost:8000"

echo "🎬 Dyn365Hunter - Satış Ekibi Demo"
echo "=================================="
echo ""

# Check if API is running
if ! curl -f -s "${API_URL}/healthz" > /dev/null 2>&1; then
    echo "❌ API çalışmıyor. Lütfen önce çalıştırın:"
    echo "   bash setup_dev.sh"
    exit 1
fi

echo "✅ API çalışıyor"
echo ""

# Demo domains
DOMAINS=("example.com" "google.com" "microsoft.com")
COMPANIES=("Example Inc" "Google" "Microsoft")

echo "📥 Adım 1: Domain'leri ekliyorum..."
echo "-----------------------------------"
for i in "${!DOMAINS[@]}"; do
    domain="${DOMAINS[$i]}"
    company="${COMPANIES[$i]}"
    echo "   → ${domain} (${company})"
    curl -s -X POST "${API_URL}/ingest/domain" \
        -H "Content-Type: application/json" \
        -d "{\"domain\": \"${domain}\", \"company_name\": \"${company}\"}" \
        > /dev/null
done
echo "✅ ${#DOMAINS[@]} domain eklendi"
echo ""

echo "🔍 Adım 2: Domain'leri analiz ediyorum (10-15 saniye sürebilir)..."
echo "-------------------------------------------------------------------"
for domain in "${DOMAINS[@]}"; do
    echo "   → ${domain} analiz ediliyor..."
    result=$(curl -s -X POST "${API_URL}/scan/domain" \
        -H "Content-Type: application/json" \
        -d "{\"domain\": \"${domain}\"}")
    
    score=$(echo "$result" | grep -o '"score":[0-9]*' | cut -d: -f2)
    segment=$(echo "$result" | grep -o '"segment":"[^"]*"' | cut -d'"' -f4)
    provider=$(echo "$result" | grep -o '"provider":"[^"]*"' | cut -d'"' -f4 || echo "N/A")
    
    echo "      Skor: ${score} | Segment: ${segment} | Provider: ${provider}"
done
echo "✅ Analiz tamamlandı"
echo ""

echo "📊 Adım 3: Migration segment'indeki yüksek skorlu lead'ler (min_score=70)"
echo "-------------------------------------------------------------------------"
migration_leads=$(curl -s "${API_URL}/leads?segment=Migration&min_score=70")
lead_count=$(echo "$migration_leads" | grep -o '"domain"' | wc -l || echo "0")

if [ "$lead_count" -gt 0 ]; then
    echo "✅ ${lead_count} adet Migration lead bulundu:"
    echo ""
    echo "$migration_leads" | python3 -m json.tool 2>/dev/null | head -50 || echo "$migration_leads" | head -50
else
    echo "⚠️  Migration segment'inde yüksek skorlu lead bulunamadı"
    echo "   Tüm lead'leri görmek için: curl \"${API_URL}/leads\""
fi
echo ""

echo "🎉 Demo tamamlandı!"
echo ""
echo "📋 Hızlı Komutlar:"
echo "   • Tüm lead'ler: curl \"${API_URL}/leads\""
echo "   • Migration lead'ler: curl \"${API_URL}/leads?segment=Migration&min_score=70\""
echo "   • Tek lead detayı: curl \"${API_URL}/leads/example.com\""
echo "   • API dokümantasyonu: ${API_URL}/docs"
echo ""

