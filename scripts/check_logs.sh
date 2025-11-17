#!/bin/bash
# Log Kontrol Script'i
# Production öncesi log kontrolü için

echo "============================================================"
echo "Production Log Kontrolü"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker çalışmıyor. Docker container'ları başlatın.${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Son 50 log satırı:${NC}"
docker-compose logs --tail=50 api

echo ""
echo "============================================================"
echo -e "${YELLOW}🔍 ERROR Kontrolü:${NC}"
echo "============================================================"
ERROR_COUNT=$(docker-compose logs api | grep -i error | tail -20 | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ Son 20 satırda ERROR yok${NC}"
else
    echo -e "${RED}❌ Son 20 satırda $ERROR_COUNT ERROR bulundu:${NC}"
    docker-compose logs api | grep -i error | tail -20
fi

echo ""
echo "============================================================"
echo -e "${YELLOW}🔍 Cache/Rescan Log Kontrolü:${NC}"
echo "============================================================"
CACHE_LOGS=$(docker-compose logs api | grep -i "cache\|rescan" | tail -10)
if [ -z "$CACHE_LOGS" ]; then
    echo -e "${YELLOW}⚠️  Cache/rescan log'ları bulunamadı${NC}"
else
    echo "$CACHE_LOGS"
fi

echo ""
echo "============================================================"
echo -e "${YELLOW}🔍 DMARC/DNS Log Kontrolü:${NC}"
echo "============================================================"
DMARC_LOGS=$(docker-compose logs api | grep -i "dmarc\|dns" | tail -10)
if [ -z "$DMARC_LOGS" ]; then
    echo -e "${YELLOW}⚠️  DMARC/DNS log'ları bulunamadı${NC}"
else
    echo "$DMARC_LOGS"
fi

echo ""
echo "============================================================"
echo -e "${YELLOW}📊 Özet:${NC}"
echo "============================================================"
echo "Son 100 satır log kontrol edildi"
echo "Detaylı log için: docker-compose logs api | tail -100"
echo ""

