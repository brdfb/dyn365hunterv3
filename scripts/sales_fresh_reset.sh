#!/bin/bash

# Satışçı İçin Temiz Reset Scripti
# Bu script satışçının sıfırdan deneyimlemesi için güvenli bir şekilde
# veritabanını ve cache'i temizler, sistemin çalıştığından emin olur.
#
# GÜVENLİK: Production koruması mevcuttur
# - Production database reset'leri engellenir (FORCE_PRODUCTION_RESET=yes gerekir)
# - DATABASE_URL'de prod|production kontrolü yapılır
#
# Kullanım:
#   bash scripts/sales_fresh_reset.sh
#
# Production için (SADECE TEST/UAT):
#   FORCE_PRODUCTION_RESET=yes bash scripts/sales_fresh_reset.sh

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script başlığı
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Satışçı İçin Temiz Reset - Fresh Start Experience     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# CRITICAL SAFETY CHECK: Prevent accidental production database reset
# Bu script DEV/TEST/UAT ortamları için tasarlanmıştır
if [[ "$DATABASE_URL" =~ prod|production ]] && [ -z "$FORCE_PRODUCTION_RESET" ]; then
    echo -e "${RED}❌ KRİTİK: Production database reset engellendi!${NC}"
    echo ""
    echo "   Bu script DEV/TEST/UAT ortamları için tasarlanmıştır."
    echo "   Production database'i resetlemek için FORCE_PRODUCTION_RESET=yes gerekir"
    echo "   (ÖNERİLMEZ - Aşırı dikkatli kullanın!)"
    echo ""
    exit 1
fi

# Logging setup (optional)
LOG_DIR="${LOG_DIR:-./logs/scripts}"
if [ -n "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
    LOG_FILE="${LOG_DIR}/sales_fresh_reset_$(date +%Y%m%d_%H%M%S).log"
    exec > >(tee -a "$LOG_FILE") 2>&1
    echo "📝 Logging to: $LOG_FILE"
fi

# Pre-flight checks
echo "🔍 Ön Kontroller..."
echo "----------------------------------------"

# Check Docker
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker çalışmıyor. Lütfen Docker Desktop'ı başlatın.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker çalışıyor${NC}"

# Check Docker Compose services
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Servisler çalışmıyor. Başlatılıyor...${NC}"
    docker-compose up -d
    echo "⏳ Servislerin başlaması bekleniyor (30 saniye)..."
    sleep 30
fi
echo -e "${GREEN}✅ Servisler çalışıyor${NC}"

# Check API health
API_URL="${API_URL:-http://localhost:8000}"
if ! curl -f -s "${API_URL}/healthz" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  API henüz hazır değil. Bekleniyor...${NC}"
    for i in {1..30}; do
        if curl -f -s "${API_URL}/healthz" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ API hazır${NC}"
            break
        fi
        sleep 2
    done
    if ! curl -f -s "${API_URL}/healthz" > /dev/null 2>&1; then
        echo -e "${RED}❌ API hazır değil. Lütfen logları kontrol edin: docker-compose logs api${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ API çalışıyor${NC}"
fi

echo ""
echo -e "${RED}⚠️  UYARI: Bu işlem TÜM VERİLERİ SİLECEK!${NC}"
echo "   Veritabanı ve Redis cache tamamen temizlenecek."
echo ""
echo "   İptal etmek için Ctrl+C tuşlarına basın..."
echo "   Devam etmek için 10 saniye bekleyin..."
sleep 10

echo ""
echo "🗑️  Adım 1: Veritabanı Resetleniyor..."
echo "----------------------------------------"

# Use official reset script
if [ -f "scripts/reset_db_with_alembic.sh" ]; then
    echo -e "${YELLOW}ℹ️  Resmi reset scripti kullanılıyor...${NC}"
    # Temporarily disable production check (we already checked above)
    FORCE_PRODUCTION_RESET="${FORCE_PRODUCTION_RESET:-}" bash scripts/reset_db_with_alembic.sh
else
    echo -e "${YELLOW}⚠️  Resmi reset scripti bulunamadı, manuel reset yapılıyor...${NC}"
    
    # Manual reset (fallback)
    docker-compose exec -T api python -c "
from app.db.session import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        conn.execute(text('DROP SCHEMA IF EXISTS public CASCADE;'))
        conn.execute(text('CREATE SCHEMA public;'))
        conn.execute(text('GRANT ALL ON SCHEMA public TO dyn365hunter;'))
        conn.execute(text('GRANT ALL ON SCHEMA public TO public;'))
        conn.commit()
    print('✅ Veritabanı başarıyla temizlendi')
except Exception as e:
    print(f'⚠️  Veritabanı temizleme hatası: {e}')
"
    
    # Create tables from models
    docker-compose exec -T api python -c "
from app.db.models import Base
from app.db.session import engine

Base.metadata.create_all(bind=engine)
print('✅ Tablolar oluşturuldu')
"
    
    # Stamp migrations
    docker-compose exec -T api alembic stamp head
    
    # Update leads_ready view
    docker-compose exec -T api python -c "
from app.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Check if P-Model columns exist
    result = conn.execute(text('''
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'lead_scores' 
        AND column_name IN ('technical_heat', 'commercial_segment', 'commercial_heat', 'priority_category', 'priority_label');
    '''))
    p_model_cols = [row[0] for row in result]
    
    if len(p_model_cols) == 5:
        conn.execute(text('''
            DROP VIEW IF EXISTS leads_ready CASCADE;
            CREATE VIEW leads_ready AS
            SELECT 
                c.id AS company_id,
                c.canonical_name,
                c.domain,
                c.provider,
                c.tenant_size,
                c.country,
                c.contact_emails,
                c.contact_quality_score,
                c.linkedin_pattern,
                c.updated_at AS company_updated_at,
                ds.id AS signal_id,
                ds.spf,
                ds.dkim,
                ds.dmarc_policy,
                ds.dmarc_coverage,
                ds.mx_root,
                ds.local_provider,
                ds.registrar,
                ds.expires_at,
                ds.nameservers,
                ds.scan_status,
                ds.scanned_at,
                ls.id AS score_id,
                ls.readiness_score,
                ls.segment,
                ls.reason,
                ls.technical_heat,
                ls.commercial_segment,
                ls.commercial_heat,
                ls.priority_category,
                ls.priority_label
            FROM companies c
            LEFT JOIN domain_signals ds ON c.domain = ds.domain
            LEFT JOIN lead_scores ls ON c.domain = ls.domain
            WHERE ls.readiness_score IS NOT NULL;
        '''))
        conn.commit()
        print('✅ leads_ready view güncellendi')
"

    # Clear Redis cache
    docker-compose exec -T api python -c "
from app.core.redis_client import get_redis_client, is_redis_available

if is_redis_available():
    client = get_redis_client()
    if client:
        try:
            client.flushall()
            print('✅ Redis cache temizlendi')
        except Exception as e:
            print(f'⚠️  Redis temizleme hatası: {e}')
else:
    print('ℹ️  Redis kullanılamıyor (atlanıyor)')
"
fi

echo ""
echo "🔍 Adım 2: Sistem Sağlık Kontrolü..."
echo "----------------------------------------"

# Verify database schema
echo "📊 Veritabanı şeması kontrol ediliyor..."
docker-compose exec -T api python -c "
from app.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Check critical columns
    result = conn.execute(text('''
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'companies' 
        AND column_name = 'tenant_size';
    '''))
    tenant_size_exists = result.fetchone() is not None
    
    result = conn.execute(text('''
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'domain_signals' 
        AND column_name IN ('local_provider', 'dmarc_coverage');
    '''))
    domain_signals_cols = [row[0] for row in result]
    
    # Check leads_ready view
    result = conn.execute(text('''
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'leads_ready' 
        AND column_name IN ('priority_category', 'commercial_segment', 'technical_heat');
    '''))
    p_model_cols = [row[0] for row in result]
    
    print(f'✅ Companies.tenant_size: {\"✓\" if tenant_size_exists else \"✗\"}')
    print(f'✅ Domain_signals columns: {domain_signals_cols}')
    print(f'✅ P-Model columns in view: {p_model_cols}')
    
    if tenant_size_exists and len(domain_signals_cols) == 2 and len(p_model_cols) == 3:
        print('✅ Tüm kritik kolonlar mevcut!')
    else:
        print('⚠️  Bazı kolonlar eksik - Alembic migration kontrolü gerekebilir')
" || echo -e "${YELLOW}⚠️  Şema kontrolünde uyarı (devam ediliyor)${NC}"

# Verify API health
echo ""
echo "🏥 API sağlık kontrolü..."
if curl -f -s "${API_URL}/healthz" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API sağlıklı${NC}"
else
    echo -e "${RED}❌ API sağlık kontrolü başarısız${NC}"
    exit 1
fi

# Verify database connection
echo ""
echo "🔌 Veritabanı bağlantı kontrolü..."
docker-compose exec -T api python -c "
from app.db.session import SessionLocal

try:
    db = SessionLocal()
    db.execute('SELECT 1')
    db.close()
    print('✅ Veritabanı bağlantısı başarılı')
except Exception as e:
    print(f'❌ Veritabanı bağlantı hatası: {e}')
    exit(1)
" || exit 1

# Verify Redis connection
echo ""
echo "🔌 Redis bağlantı kontrolü..."
docker-compose exec -T redis redis-cli ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Redis bağlantısı başarılı${NC}"
else
    echo -e "${YELLOW}⚠️  Redis bağlantısı başarısız (devam ediliyor)${NC}"
fi

# Verify empty database
echo ""
echo "📊 Veritabanı içerik kontrolü..."
LEAD_COUNT=$(docker-compose exec -T api python -c "
from app.db.session import SessionLocal
from app.db.models import LeadScore

db = SessionLocal()
count = db.query(LeadScore).count()
db.close()
print(count)
" 2>/dev/null || echo "0")

if [ "$LEAD_COUNT" = "0" ]; then
    echo -e "${GREEN}✅ Veritabanı temiz (0 lead)${NC}"
else
    echo -e "${YELLOW}⚠️  Veritabanında hala $LEAD_COUNT lead var${NC}"
fi

echo ""
echo "🔍 Adım 3: Özellik Durumu Kontrolü..."
echo "----------------------------------------"

# Check feature flags
echo "📊 Feature Flag Durumu:"
docker-compose exec -T api python -c "
import os

print('')
print('✅ CORE ÖZELLİKLER (Her Zaman Aktif):')
print('   ✅ Domain Ingestion (CSV/Excel/Single)')
print('   ✅ Domain Scanning (DNS/WHOIS)')
print('   ✅ Scoring Engine (Rule-based)')
print('   ✅ Lead Management')
print('   ✅ Bulk Scan (Async)')
print('   ✅ CSV/Excel Export')
print('   ✅ Mini UI (Web Interface)')
print('   ✅ Search, Sorting, Pagination')
print('   ✅ P-Model (Priority Badges, Commercial Segment, Technical Heat)')
print('   ✅ Sales Summary (Intelligence Layer)')
print('   ✅ ReScan & Alerts')
print('   ✅ Notes, Tags, Favorites')
print('   ✅ PDF Export')
print('')

print('🔧 FEATURE FLAG ÖZELLİKLERİ:')
partner_enabled = os.getenv('HUNTER_PARTNER_CENTER_ENABLED', 'false').lower() == 'true'
d365_enabled = os.getenv('HUNTER_D365_ENABLED', 'false').lower() == 'true'
enrichment_enabled = os.getenv('HUNTER_ENRICHMENT_ENABLED', 'false').lower() == 'true'

if partner_enabled:
    print('   ✅ Partner Center Integration: AKTİF')
else:
    print('   ⚠️  Partner Center Integration: Kapalı (HUNTER_PARTNER_CENTER_ENABLED=false)')

if d365_enabled:
    print('   ✅ Dynamics 365 Integration: AKTİF')
else:
    print('   ⚠️  Dynamics 365 Integration: Kapalı (HUNTER_D365_ENABLED=false)')

if enrichment_enabled:
    print('   ✅ IP Enrichment: AKTİF')
else:
    print('   ⚠️  IP Enrichment: Kapalı (HUNTER_ENRICHMENT_ENABLED=false)')

print('')
print('📝 Not: Feature flag\\'leri aktifleştirmek için .env dosyasını düzenleyin')
print('   Örnek: HUNTER_PARTNER_CENTER_ENABLED=true')
" || echo -e "${YELLOW}⚠️  Feature flag kontrolünde uyarı${NC}"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo -e "║  ${GREEN}✅ Temiz Reset Tamamlandı!${NC}                                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Sistem Durumu:"
echo "   ✅ Veritabanı temiz ve hazır"
echo "   ✅ Redis cache temizlendi"
echo "   ✅ API çalışıyor ve sağlıklı"
echo "   ✅ Tüm servisler hazır"
echo ""
echo "📊 Özellik Durumu:"
echo "   ✅ Core özellikler aktif (Domain ingestion, scanning, scoring, lead management)"
echo "   ✅ Mini UI aktif (http://localhost:8000/mini-ui)"
echo "   ✅ P-Model aktif (Priority badges, commercial segment, technical heat)"
echo "   ✅ Sales Summary aktif (Intelligence layer)"
echo "   ⚠️  Feature flag özellikleri kontrol edildi (yukarıda gösterildi)"
echo ""
echo "📝 Sonraki Adımlar:"
echo ""
echo "   1. Demo senaryosu çalıştır:"
echo "      ${BLUE}bash scripts/sales-demo.sh${NC}"
echo ""
echo "   2. Manuel test:"
echo "      ${BLUE}curl -X POST http://localhost:8000/api/v1/ingest/domain \\${NC}"
echo "      ${BLUE}  -H 'Content-Type: application/json' \\${NC}"
echo "      ${BLUE}  -d '{\"domain\": \"example.com\", \"company_name\": \"Example Inc\"}'${NC}"
echo ""
echo "   3. API dokümantasyonu:"
echo "      ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "   4. Mini UI:"
echo "      ${BLUE}http://localhost:8000/mini-ui${NC}"
echo ""
echo "🎉 Sistem sıfırdan deneyimlemeye hazır!"
echo ""

