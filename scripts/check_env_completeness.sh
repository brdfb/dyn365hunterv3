#!/bin/bash

# .env Dosyası Eksiklik Kontrolü Scripti
# Bu script .env dosyasını kontrol eder ve eksik olan environment variable'ları gösterir.

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           .env Dosyası Eksiklik Kontrolü                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env dosyası bulunamadı!${NC}"
    echo ""
    echo "   .env.example'dan oluşturun:"
    echo "   ${BLUE}cp .env.example .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ .env dosyası mevcut${NC}"
echo ""

# Required variables (from .env.example)
REQUIRED_VARS=(
    "DATABASE_URL"
    "POSTGRES_USER"
    "POSTGRES_PASSWORD"
    "POSTGRES_DB"
    "REDIS_URL"
    "API_HOST"
    "API_PORT"
    "LOG_LEVEL"
    "ENVIRONMENT"
)

# Optional but recommended variables
OPTIONAL_VARS=(
    "HUNTER_SENTRY_DSN"
    "HUNTER_DB_POOL_SIZE"
    "HUNTER_DB_MAX_OVERFLOW"
)

# Feature flag variables
FEATURE_FLAG_VARS=(
    "HUNTER_PARTNER_CENTER_ENABLED"
    "HUNTER_D365_ENABLED"
    "HUNTER_ENRICHMENT_ENABLED"
)

# Partner Center variables (if enabled)
PC_VARS=(
    "HUNTER_PARTNER_CENTER_CLIENT_ID"
    "HUNTER_PARTNER_CENTER_TENANT_ID"
    "HUNTER_PARTNER_CENTER_API_URL"
)

# D365 variables (if enabled)
D365_VARS=(
    "HUNTER_D365_BASE_URL"
    "HUNTER_D365_CLIENT_ID"
    "HUNTER_D365_CLIENT_SECRET"
    "HUNTER_D365_TENANT_ID"
)

# IP Enrichment variables (if enabled)
ENRICHMENT_VARS=(
    "MAXMIND_CITY_DB"
    "IP2LOCATION_DB"
    "IP2PROXY_DB"
)

MISSING_REQUIRED=()
MISSING_OPTIONAL=()
MISSING_PC=()
MISSING_D365=()
MISSING_ENRICHMENT=()

# Check required variables
echo "🔍 Zorunlu Değişkenler Kontrolü..."
echo "----------------------------------------"
for var in "${REQUIRED_VARS[@]}"; do
    if grep -q "^${var}=" .env 2>/dev/null; then
        value=$(grep "^${var}=" .env | cut -d'=' -f2- | head -c 50)
        if [ -z "$value" ] || [ "$value" = "" ]; then
            echo -e "   ${RED}❌ ${var}: BOŞ${NC}"
            MISSING_REQUIRED+=("${var}")
        else
            echo -e "   ${GREEN}✅ ${var}: AYARLANMIŞ${NC}"
        fi
    else
        echo -e "   ${RED}❌ ${var}: EKSİK${NC}"
        MISSING_REQUIRED+=("${var}")
    fi
done

# Check optional variables
echo ""
echo "🔍 Opsiyonel Değişkenler Kontrolü..."
echo "----------------------------------------"
for var in "${OPTIONAL_VARS[@]}"; do
    if grep -q "^${var}=" .env 2>/dev/null; then
        echo -e "   ${GREEN}✅ ${var}: AYARLANMIŞ${NC}"
    else
        echo -e "   ${YELLOW}⚠️  ${var}: EKSİK (Önerilen)${NC}"
        MISSING_OPTIONAL+=("${var}")
    fi
done

# Check feature flags
echo ""
echo "🔍 Feature Flag'ler Kontrolü..."
echo "----------------------------------------"
for var in "${FEATURE_FLAG_VARS[@]}"; do
    if grep -q "^${var}=" .env 2>/dev/null; then
        value=$(grep "^${var}=" .env | cut -d'=' -f2)
        if [ "$value" = "true" ]; then
            echo -e "   ${GREEN}✅ ${var}: AKTİF${NC}"
        else
            echo -e "   ${YELLOW}⚠️  ${var}: KAPALI${NC}"
        fi
    else
        echo -e "   ${YELLOW}⚠️  ${var}: EKSİK (Default: false)${NC}"
    fi
done

# Check Partner Center variables (if enabled)
PC_ENABLED=$(grep -E "^HUNTER_PARTNER_CENTER_ENABLED=" .env | cut -d'=' -f2 || echo "false")
if [ "$PC_ENABLED" = "true" ]; then
    echo ""
    echo "🔍 Partner Center Değişkenleri (Feature Flag AKTİF)..."
    echo "----------------------------------------"
    for var in "${PC_VARS[@]}"; do
        if grep -q "^${var}=" .env 2>/dev/null; then
            value=$(grep "^${var}=" .env | cut -d'=' -f2- | head -c 50)
            if [ -z "$value" ] || [ "$value" = "" ] || [ "$value" = "YOUR_CLIENT_ID" ] || [ "$value" = "YOUR_TENANT_ID" ]; then
                echo -e "   ${RED}❌ ${var}: BOŞ veya PLACEHOLDER${NC}"
                MISSING_PC+=("${var}")
            else
                echo -e "   ${GREEN}✅ ${var}: AYARLANMIŞ${NC}"
            fi
        else
            echo -e "   ${RED}❌ ${var}: EKSİK${NC}"
            MISSING_PC+=("${var}")
        fi
    done
fi

# Check D365 variables (if enabled)
D365_ENABLED=$(grep -E "^HUNTER_D365_ENABLED=" .env | cut -d'=' -f2 || echo "false")
if [ "$D365_ENABLED" = "true" ]; then
    echo ""
    echo "🔍 Dynamics 365 Değişkenleri (Feature Flag AKTİF)..."
    echo "----------------------------------------"
    for var in "${D365_VARS[@]}"; do
        if grep -q "^${var}=" .env 2>/dev/null; then
            value=$(grep "^${var}=" .env | cut -d'=' -f2- | head -c 50)
            if [ -z "$value" ] || [ "$value" = "" ] || [ "$value" = "YOUR_CLIENT_ID" ] || [ "$value" = "YOUR_CLIENT_SECRET" ] || [ "$value" = "YOUR_TENANT_ID" ] || [ "$value" = "https://YOUR_ORG.crm.dynamics.com" ]; then
                echo -e "   ${RED}❌ ${var}: BOŞ veya PLACEHOLDER${NC}"
                MISSING_D365+=("${var}")
            else
                echo -e "   ${GREEN}✅ ${var}: AYARLANMIŞ${NC}"
            fi
        else
            echo -e "   ${RED}❌ ${var}: EKSİK${NC}"
            MISSING_D365+=("${var}")
        fi
    done
fi

# Check IP Enrichment variables (if enabled)
ENRICHMENT_ENABLED=$(grep -E "^HUNTER_ENRICHMENT_ENABLED=" .env | cut -d'=' -f2 || echo "false")
if [ "$ENRICHMENT_ENABLED" = "true" ]; then
    echo ""
    echo "🔍 IP Enrichment Değişkenleri (Feature Flag AKTİF)..."
    echo "----------------------------------------"
    for var in "${ENRICHMENT_VARS[@]}"; do
        if grep -q "^${var}=" .env 2>/dev/null; then
            value=$(grep "^${var}=" .env | cut -d'=' -f2- | head -c 50)
            if [ -z "$value" ] || [ "$value" = "" ]; then
                echo -e "   ${RED}❌ ${var}: BOŞ${NC}"
                MISSING_ENRICHMENT+=("${var}")
            else
                echo -e "   ${GREEN}✅ ${var}: AYARLANMIŞ${NC}"
            fi
        else
            echo -e "   ${RED}❌ ${var}: EKSİK${NC}"
            MISSING_ENRICHMENT+=("${var}")
        fi
    done
fi

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    ÖZET                                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [ ${#MISSING_REQUIRED[@]} -eq 0 ] && [ ${#MISSING_PC[@]} -eq 0 ] && [ ${#MISSING_D365[@]} -eq 0 ] && [ ${#MISSING_ENRICHMENT[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ Tüm zorunlu değişkenler ayarlanmış!${NC}"
    echo ""
    if [ ${#MISSING_OPTIONAL[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Opsiyonel değişkenler eksik (önerilen):${NC}"
        for var in "${MISSING_OPTIONAL[@]}"; do
            echo "   - ${var}"
        done
    fi
else
    echo -e "${RED}❌ Eksik değişkenler bulundu:${NC}"
    echo ""
    
    if [ ${#MISSING_REQUIRED[@]} -gt 0 ]; then
        echo -e "${RED}Zorunlu Değişkenler:${NC}"
        for var in "${MISSING_REQUIRED[@]}"; do
            echo "   - ${var}"
        done
        echo ""
    fi
    
    if [ ${#MISSING_PC[@]} -gt 0 ]; then
        echo -e "${RED}Partner Center (Feature Flag AKTİF):${NC}"
        for var in "${MISSING_PC[@]}"; do
            echo "   - ${var}"
        done
        echo ""
    fi
    
    if [ ${#MISSING_D365[@]} -gt 0 ]; then
        echo -e "${RED}Dynamics 365 (Feature Flag AKTİF):${NC}"
        for var in "${MISSING_D365[@]}"; do
            echo "   - ${var}"
        done
        echo ""
    fi
    
    if [ ${#MISSING_ENRICHMENT[@]} -gt 0 ]; then
        echo -e "${RED}IP Enrichment (Feature Flag AKTİF):${NC}"
        for var in "${MISSING_ENRICHMENT[@]}"; do
            echo "   - ${var}"
        done
        echo ""
    fi
    
    if [ ${#MISSING_OPTIONAL[@]} -gt 0 ]; then
        echo -e "${YELLOW}Opsiyonel Değişkenler (Önerilen):${NC}"
        for var in "${MISSING_OPTIONAL[@]}"; do
            echo "   - ${var}"
        done
    fi
fi

echo ""
echo "📝 Not: .env.example dosyasına bakarak eksik değişkenleri ekleyebilirsiniz."
echo ""

