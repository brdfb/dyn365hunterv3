#!/bin/bash

# Hunter Fresh Start Script - Son Kullanıcı İçin Temiz Başlangıç
# Bu script yeni bir ortam için temiz bir kurulum yapar
#
# Kullanım:
#   bash scripts/fresh_start.sh

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Hunter - Temiz Başlangıç Kurulumu                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${CYAN}📋 ADIM 1: Ön Gereksinimler Kontrolü${NC}"
echo "----------------------------------------"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker bulunamadı. Lütfen Docker Desktop'ı yükleyin.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker mevcut${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose bulunamadı. Lütfen Docker Compose'u yükleyin.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose mevcut${NC}"

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker çalışmıyor. Lütfen Docker Desktop'ı başlatın.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker çalışıyor${NC}"
echo ""

# Step 2: Environment setup
echo -e "${CYAN}📋 ADIM 2: Environment Dosyası Hazırlama${NC}"
echo "----------------------------------------"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ .env dosyası .env.example'dan oluşturuldu${NC}"
        echo -e "${YELLOW}⚠️  Lütfen .env dosyasını düzenleyip gerekli değerleri ayarlayın${NC}"
    else
        echo -e "${RED}❌ .env.example dosyası bulunamadı${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  .env dosyası zaten mevcut${NC}"
    # Non-interactive mode: if FORCE_RESET_ENV is set, reset .env
    if [ "${FORCE_RESET_ENV}" = "yes" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ .env dosyası sıfırlandı (FORCE_RESET_ENV=yes)${NC}"
    else
        # Interactive mode: ask user
        if [ -t 0 ]; then
            read -p "   .env dosyasını sıfırlamak istiyor musunuz? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                cp .env.example .env
                echo -e "${GREEN}✅ .env dosyası sıfırlandı${NC}"
            else
                echo -e "${BLUE}ℹ️  Mevcut .env dosyası korunuyor${NC}"
            fi
        else
            echo -e "${BLUE}ℹ️  Mevcut .env dosyası korunuyor (non-interactive mode)${NC}"
        fi
    fi
fi
echo ""

# Step 3: Environment variables check
echo -e "${CYAN}📋 ADIM 3: Environment Değişkenleri Kontrolü${NC}"
echo "----------------------------------------"

if [ -f "scripts/check_env_completeness.sh" ]; then
    bash scripts/check_env_completeness.sh
    echo ""
    # Non-interactive mode: skip prompt
    if [ -t 0 ]; then
        read -p "   Environment değişkenleri doğru mu? Devam etmek için Enter'a basın... "
        echo ""
    else
        echo -e "${BLUE}ℹ️  Non-interactive mode: devam ediliyor...${NC}"
        echo ""
    fi
else
    echo -e "${YELLOW}⚠️  check_env_completeness.sh bulunamadı, atlanıyor${NC}"
fi

# Step 4: Docker services
echo -e "${CYAN}📋 ADIM 4: Docker Servisleri Başlatma${NC}"
echo "----------------------------------------"

# Stop existing containers
echo "🧹 Mevcut container'lar temizleniyor..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true
echo -e "${GREEN}✅ Temizlik tamamlandı${NC}"

# Build and start services
echo "🔨 Container'lar build ediliyor..."
docker-compose build --no-cache || docker compose build --no-cache
echo -e "${GREEN}✅ Build tamamlandı${NC}"

echo "🚀 Servisler başlatılıyor..."
docker-compose up -d || docker compose up -d
echo -e "${GREEN}✅ Servisler başlatıldı${NC}"

# Wait for services
echo "⏳ Servislerin hazır olması bekleniyor (15 saniye)..."
sleep 15
echo ""

# Step 5: Health checks
echo -e "${CYAN}📋 ADIM 5: Servis Sağlık Kontrolleri${NC}"
echo "----------------------------------------"

# Check PostgreSQL
echo "🗄️  PostgreSQL kontrol ediliyor..."
if docker-compose exec -T postgres pg_isready -U dyn365hunter > /dev/null 2>&1 || docker compose exec -T postgres pg_isready -U dyn365hunter > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL hazır${NC}"
else
    echo -e "${RED}❌ PostgreSQL hazır değil. Logları kontrol edin: docker-compose logs postgres${NC}"
    exit 1
fi

# Check Redis
echo "🔴 Redis kontrol ediliyor..."
if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG" || docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo -e "${GREEN}✅ Redis hazır${NC}"
else
    echo -e "${RED}❌ Redis hazır değil. Logları kontrol edin: docker-compose logs redis${NC}"
    exit 1
fi

# Check API
echo "🏥 API kontrol ediliyor..."
sleep 5
API_HEALTH=$(curl -s http://localhost:8000/healthz 2>/dev/null || echo "FAILED")
if echo "$API_HEALTH" | grep -q "ok"; then
    echo -e "${GREEN}✅ API hazır${NC}"
else
    echo -e "${YELLOW}⚠️  API henüz hazır değil. Birkaç saniye bekleyip tekrar deneyin:${NC}"
    echo "   curl http://localhost:8000/healthz"
fi
echo ""

# Step 6: Database reset (optional)
echo -e "${CYAN}📋 ADIM 6: Veritabanı Temizleme (Opsiyonel)${NC}"
echo "----------------------------------------"

# Check if database reset is requested
if [ "${RESET_DATABASE}" = "yes" ]; then
    echo -e "${YELLOW}⚠️  Veritabanı sıfırlanacak (TÜM VERİLER SİLİNECEK!)${NC}"
    if [ -f "scripts/reset_db_with_alembic.sh" ]; then
        echo "🔄 Resmi reset scripti çalıştırılıyor..."
        FORCE_PRODUCTION_RESET="${FORCE_PRODUCTION_RESET:-}" bash scripts/reset_db_with_alembic.sh
        echo -e "${GREEN}✅ Veritabanı temizlendi${NC}"
    else
        echo -e "${YELLOW}⚠️  Reset scripti bulunamadı, manuel temizleme yapılıyor...${NC}"
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
    print('✅ Veritabanı temizlendi')
except Exception as e:
    print(f'⚠️  Hata: {e}')
" || docker compose exec -T api python -c "
from app.db.session import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        conn.execute(text('DROP SCHEMA IF EXISTS public CASCADE;'))
        conn.execute(text('CREATE SCHEMA public;'))
        conn.execute(text('GRANT ALL ON SCHEMA public TO dyn365hunter;'))
        conn.execute(text('GRANT ALL ON SCHEMA public TO public;'))
        conn.commit()
    print('✅ Veritabanı temizlendi')
except Exception as e:
    print(f'⚠️  Hata: {e}')
"
        echo -e "${GREEN}✅ Veritabanı temizlendi${NC}"
    fi
else
    # Interactive mode: ask user
    if [ -t 0 ]; then
        read -p "   Veritabanını temizlemek istiyor musunuz? (TÜM VERİLER SİLİNECEK!) (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [ -f "scripts/reset_db_with_alembic.sh" ]; then
                echo "🔄 Resmi reset scripti çalıştırılıyor..."
                FORCE_PRODUCTION_RESET="${FORCE_PRODUCTION_RESET:-}" bash scripts/reset_db_with_alembic.sh
                echo -e "${GREEN}✅ Veritabanı temizlendi${NC}"
            else
                echo -e "${YELLOW}⚠️  Reset scripti bulunamadı, manuel temizleme yapılıyor...${NC}"
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
    print('✅ Veritabanı temizlendi')
except Exception as e:
    print(f'⚠️  Hata: {e}')
" || docker compose exec -T api python -c "
from app.db.session import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        conn.execute(text('DROP SCHEMA IF EXISTS public CASCADE;'))
        conn.execute(text('CREATE SCHEMA public;'))
        conn.execute(text('GRANT ALL ON SCHEMA public TO dyn365hunter;'))
        conn.execute(text('GRANT ALL ON SCHEMA public TO public;'))
        conn.commit()
    print('✅ Veritabanı temizlendi')
except Exception as e:
    print(f'⚠️  Hata: {e}')
"
                echo -e "${GREEN}✅ Veritabanı temizlendi${NC}"
            fi
        else
            echo -e "${BLUE}ℹ️  Veritabanı temizleme atlandı${NC}"
        fi
    else
        echo -e "${BLUE}ℹ️  Veritabanı temizleme atlandı (non-interactive mode, RESET_DATABASE=yes ile aktifleştirebilirsiniz)${NC}"
    fi
fi
echo ""

# Step 7: Database migrations
echo -e "${CYAN}📋 ADIM 7: Veritabanı Migrasyonları${NC}"
echo "----------------------------------------"

echo "🔄 Alembic migrasyonları çalıştırılıyor..."
if docker-compose exec -T api alembic upgrade head > /dev/null 2>&1 || docker compose exec -T api alembic upgrade head > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Migrasyonlar tamamlandı${NC}"
else
    echo -e "${YELLOW}⚠️  Migrasyon hatası olabilir. Logları kontrol edin:${NC}"
    echo "   docker-compose logs api | grep alembic"
fi
echo ""

# Step 8: Integration setup (optional)
echo -e "${CYAN}📋 ADIM 8: Entegrasyon Kurulumu (Opsiyonel)${NC}"
echo "----------------------------------------"

if [ -f "scripts/enable_integrations.sh" ]; then
    # Non-interactive mode: if ENABLE_INTEGRATIONS is set, enable them
    if [ "${ENABLE_INTEGRATIONS}" = "yes" ]; then
        bash scripts/enable_integrations.sh
    else
        # Interactive mode: ask user
        if [ -t 0 ]; then
            read -p "   Partner Center ve D365 entegrasyonlarını aktifleştirmek istiyor musunuz? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                bash scripts/enable_integrations.sh
            else
                echo -e "${BLUE}ℹ️  Entegrasyon kurulumu atlandı${NC}"
            fi
        else
            echo -e "${BLUE}ℹ️  Entegrasyon kurulumu atlandı (non-interactive mode, ENABLE_INTEGRATIONS=yes ile aktifleştirebilirsiniz)${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  enable_integrations.sh bulunamadı, atlanıyor${NC}"
fi
echo ""

# Step 9: Final verification
echo -e "${CYAN}📋 ADIM 9: Son Doğrulama${NC}"
echo "----------------------------------------"

echo "🔍 Sistem durumu kontrol ediliyor..."
echo ""

# API Health
API_STATUS=$(curl -s http://localhost:8000/healthz 2>/dev/null || echo "FAILED")
if echo "$API_STATUS" | grep -q "ok"; then
    echo -e "${GREEN}✅ API: Çalışıyor${NC}"
else
    echo -e "${RED}❌ API: Çalışmıyor${NC}"
fi

# Database connection
if docker-compose exec -T postgres pg_isready -U dyn365hunter > /dev/null 2>&1 || docker compose exec -T postgres pg_isready -U dyn365hunter > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database: Bağlı${NC}"
else
    echo -e "${RED}❌ Database: Bağlı değil${NC}"
fi

# Redis connection
if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG" || docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo -e "${GREEN}✅ Redis: Bağlı${NC}"
else
    echo -e "${RED}❌ Redis: Bağlı değil${NC}"
fi

echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    KURULUM TAMAMLANDI                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Hunter başarıyla kuruldu!${NC}"
echo ""
echo "📝 Sonraki Adımlar:"
echo "----------------------------------------"
echo ""
echo "1. API'yi test edin:"
echo "   ${CYAN}curl http://localhost:8000/healthz${NC}"
echo ""
echo "2. Logları kontrol edin:"
echo "   ${CYAN}docker-compose logs -f api${NC}"
echo ""
echo "3. Veritabanını temizlemek için (tüm veriler silinir):"
echo "   ${CYAN}RESET_DATABASE=yes bash scripts/fresh_start.sh${NC}"
echo "   veya:"
echo "   ${CYAN}bash scripts/reset_db_with_alembic.sh${NC}"
echo ""
echo "4. Entegrasyonları aktifleştirmek için:"
echo "   ${CYAN}bash scripts/enable_integrations.sh${NC}"
echo ""
echo "5. Partner Center için ilk authentication:"
echo "   ${CYAN}docker-compose exec api python -m app.tools.partner_center_device_code_flow${NC}"
echo ""
echo "6. Mini UI'ya erişin:"
echo "   ${CYAN}http://localhost:8000${NC}"
echo ""
echo "📚 Daha fazla bilgi için:"
echo "   - ${CYAN}docs/reference/DEVELOPMENT-ENVIRONMENT.md${NC}"
echo "   - ${CYAN}docs/reference/TOOLS-USAGE.md${NC}"
echo "   - ${CYAN}docs/reference/INTEGRATIONS-ENABLED-STATUS.md${NC}"
echo ""
echo -e "${GREEN}🎉 İyi çalışmalar!${NC}"
echo ""

