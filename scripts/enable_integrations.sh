#!/bin/bash

# Partner Center ve D365 Entegrasyonlarını Aktifleştirme Scripti
# Bu script feature flag'leri aktifleştirir ve gerekli kontrolleri yapar.
#
# Kullanım:
#   bash scripts/enable_integrations.sh

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Partner Center & D365 Entegrasyon Aktifleştirme      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env dosyası bulunamadı. .env.example'dan oluşturuluyor...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env dosyası oluşturuldu${NC}"
fi

# Check current status
echo "🔍 Mevcut Durum Kontrolü..."
echo "----------------------------------------"

# Check Partner Center status
PC_ENABLED=$(grep -E "^HUNTER_PARTNER_CENTER_ENABLED=" .env | cut -d'=' -f2 || echo "false")
PC_CLIENT_ID=$(grep -E "^HUNTER_PARTNER_CENTER_CLIENT_ID=" .env | cut -d'=' -f2 || echo "")
PC_TENANT_ID=$(grep -E "^HUNTER_PARTNER_CENTER_TENANT_ID=" .env | cut -d'=' -f2 || echo "")

# Check D365 status
D365_ENABLED=$(grep -E "^HUNTER_D365_ENABLED=" .env | cut -d'=' -f2 || echo "false")
D365_BASE_URL=$(grep -E "^HUNTER_D365_BASE_URL=" .env | cut -d'=' -f2 || echo "")
D365_CLIENT_ID=$(grep -E "^HUNTER_D365_CLIENT_ID=" .env | cut -d'=' -f2 || echo "")
D365_CLIENT_SECRET=$(grep -E "^HUNTER_D365_CLIENT_SECRET=" .env | cut -d'=' -f2 || echo "")
D365_TENANT_ID=$(grep -E "^HUNTER_D365_TENANT_ID=" .env | cut -d'=' -f2 || echo "")

echo ""
echo "📊 Partner Center Durumu:"
if [ "$PC_ENABLED" = "true" ]; then
    echo -e "   ${GREEN}✅ Feature Flag: AKTİF${NC}"
else
    echo -e "   ${YELLOW}⚠️  Feature Flag: KAPALI${NC}"
fi

if [ -n "$PC_CLIENT_ID" ] && [ "$PC_CLIENT_ID" != "YOUR_CLIENT_ID" ] && [ "$PC_CLIENT_ID" != "" ]; then
    echo -e "   ${GREEN}✅ CLIENT_ID: AYARLANMIŞ${NC}"
else
    echo -e "   ${RED}❌ CLIENT_ID: AYARLANMAMIŞ${NC}"
fi

if [ -n "$PC_TENANT_ID" ] && [ "$PC_TENANT_ID" != "YOUR_TENANT_ID" ] && [ "$PC_TENANT_ID" != "" ]; then
    echo -e "   ${GREEN}✅ TENANT_ID: AYARLANMIŞ${NC}"
else
    echo -e "   ${RED}❌ TENANT_ID: AYARLANMAMIŞ${NC}"
fi

echo ""
echo "📊 Dynamics 365 Durumu:"
if [ "$D365_ENABLED" = "true" ]; then
    echo -e "   ${GREEN}✅ Feature Flag: AKTİF${NC}"
else
    echo -e "   ${YELLOW}⚠️  Feature Flag: KAPALI${NC}"
fi

if [ -n "$D365_BASE_URL" ] && [ "$D365_BASE_URL" != "https://YOUR_ORG.crm.dynamics.com" ] && [ "$D365_BASE_URL" != "" ]; then
    echo -e "   ${GREEN}✅ BASE_URL: AYARLANMIŞ${NC}"
else
    echo -e "   ${RED}❌ BASE_URL: AYARLANMAMIŞ${NC}"
fi

if [ -n "$D365_CLIENT_ID" ] && [ "$D365_CLIENT_ID" != "YOUR_CLIENT_ID" ] && [ "$D365_CLIENT_ID" != "" ]; then
    echo -e "   ${GREEN}✅ CLIENT_ID: AYARLANMIŞ${NC}"
else
    echo -e "   ${RED}❌ CLIENT_ID: AYARLANMAMIŞ${NC}"
fi

if [ -n "$D365_CLIENT_SECRET" ] && [ "$D365_CLIENT_SECRET" != "YOUR_CLIENT_SECRET" ] && [ "$D365_CLIENT_SECRET" != "" ]; then
    echo -e "   ${GREEN}✅ CLIENT_SECRET: AYARLANMIŞ${NC}"
else
    echo -e "   ${RED}❌ CLIENT_SECRET: AYARLANMAMIŞ${NC}"
fi

if [ -n "$D365_TENANT_ID" ] && [ "$D365_TENANT_ID" != "YOUR_TENANT_ID" ] && [ "$D365_TENANT_ID" != "" ]; then
    echo -e "   ${GREEN}✅ TENANT_ID: AYARLANMIŞ${NC}"
else
    echo -e "   ${RED}❌ TENANT_ID: AYARLANMAMIŞ${NC}"
fi

echo ""
echo "🔧 Feature Flag'leri Aktifleştiriliyor..."
echo "----------------------------------------"

# Enable Partner Center
if [ "$PC_ENABLED" != "true" ]; then
    echo "📝 Partner Center feature flag aktifleştiriliyor..."
    if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # macOS/Linux
        sed -i.bak 's/^HUNTER_PARTNER_CENTER_ENABLED=false/HUNTER_PARTNER_CENTER_ENABLED=true/' .env
    else
        # Windows (Git Bash)
        sed -i 's/^HUNTER_PARTNER_CENTER_ENABLED=false/HUNTER_PARTNER_CENTER_ENABLED=true/' .env
    fi
    echo -e "${GREEN}✅ Partner Center feature flag aktifleştirildi${NC}"
else
    echo -e "${GREEN}✅ Partner Center feature flag zaten aktif${NC}"
fi

# Enable D365
if [ "$D365_ENABLED" != "true" ]; then
    echo "📝 Dynamics 365 feature flag aktifleştiriliyor..."
    if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # macOS/Linux
        sed -i.bak 's/^HUNTER_D365_ENABLED=false/HUNTER_D365_ENABLED=true/' .env
    else
        # Windows (Git Bash)
        sed -i 's/^HUNTER_D365_ENABLED=false/HUNTER_D365_ENABLED=true/' .env
    fi
    echo -e "${GREEN}✅ Dynamics 365 feature flag aktifleştirildi${NC}"
else
    echo -e "${GREEN}✅ Dynamics 365 feature flag zaten aktif${NC}"
fi

echo ""
echo "⚠️  ÖNEMLİ UYARILAR:"
echo "----------------------------------------"

# Partner Center warnings
if [ -z "$PC_CLIENT_ID" ] || [ "$PC_CLIENT_ID" = "YOUR_CLIENT_ID" ] || [ "$PC_CLIENT_ID" = "" ]; then
    echo -e "${YELLOW}⚠️  Partner Center: CLIENT_ID ayarlanmalı (.env dosyasında)${NC}"
fi

if [ -z "$PC_TENANT_ID" ] || [ "$PC_TENANT_ID" = "YOUR_TENANT_ID" ] || [ "$PC_TENANT_ID" = "" ]; then
    echo -e "${YELLOW}⚠️  Partner Center: TENANT_ID ayarlanmalı (.env dosyasında)${NC}"
fi

# D365 warnings
if [ -z "$D365_BASE_URL" ] || [ "$D365_BASE_URL" = "https://YOUR_ORG.crm.dynamics.com" ] || [ "$D365_BASE_URL" = "" ]; then
    echo -e "${YELLOW}⚠️  Dynamics 365: BASE_URL ayarlanmalı (.env dosyasında)${NC}"
fi

if [ -z "$D365_CLIENT_ID" ] || [ "$D365_CLIENT_ID" = "YOUR_CLIENT_ID" ] || [ "$D365_CLIENT_ID" = "" ]; then
    echo -e "${YELLOW}⚠️  Dynamics 365: CLIENT_ID ayarlanmalı (.env dosyasında)${NC}"
fi

if [ -z "$D365_CLIENT_SECRET" ] || [ "$D365_CLIENT_SECRET" = "YOUR_CLIENT_SECRET" ] || [ "$D365_CLIENT_SECRET" = "" ]; then
    echo -e "${YELLOW}⚠️  Dynamics 365: CLIENT_SECRET ayarlanmalı (.env dosyasında)${NC}"
fi

if [ -z "$D365_TENANT_ID" ] || [ "$D365_TENANT_ID" = "YOUR_TENANT_ID" ] || [ "$D365_TENANT_ID" = "" ]; then
    echo -e "${YELLOW}⚠️  Dynamics 365: TENANT_ID ayarlanmalı (.env dosyasında)${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo -e "║  ${GREEN}✅ Feature Flag'ler Aktifleştirildi!${NC}                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 Sonraki Adımlar:"
echo ""
echo "   1. .env dosyasını düzenleyin ve credential'ları girin:"
echo "      ${BLUE}nano .env${NC}  # veya ${BLUE}code .env${NC}"
echo ""
echo "   2. Partner Center için gerekli credential'lar:"
echo "      ${BLUE}HUNTER_PARTNER_CENTER_CLIENT_ID=<your-client-id>${NC}"
echo "      ${BLUE}HUNTER_PARTNER_CENTER_TENANT_ID=<your-tenant-id>${NC}"
echo ""
echo "   3. Dynamics 365 için gerekli credential'lar:"
echo "      ${BLUE}HUNTER_D365_BASE_URL=https://yourorg.crm.dynamics.com${NC}"
echo "      ${BLUE}HUNTER_D365_CLIENT_ID=<your-client-id>${NC}"
echo "      ${BLUE}HUNTER_D365_CLIENT_SECRET=<your-client-secret>${NC}"
echo "      ${BLUE}HUNTER_D365_TENANT_ID=<your-tenant-id>${NC}"
echo ""
echo "   4. Servisleri yeniden başlatın:"
echo "      ${BLUE}docker-compose restart api worker${NC}"
echo ""
echo "   5. Partner Center için ilk authentication:"
echo "      ${BLUE}docker-compose exec api python -m app.tools.partner_center_device_code_flow${NC}"
echo ""
echo "🎉 Feature flag'ler aktifleştirildi!"
echo ""

