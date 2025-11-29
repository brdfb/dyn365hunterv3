# Fresh Start Guide - Son Kullanıcı İçin Temiz Başlangıç

**Tarih**: 2025-01-30  
**Versiyon**: v1.0.0  
**Amaç**: Yeni bir ortam için temiz kurulum rehberi

---

## 🎯 Genel Bakış

Bu rehber, Hunter'ı sıfırdan kurmak isteyen son kullanıcılar için hazırlanmıştır. Tüm adımlar otomatik script ile yapılabilir veya manuel olarak takip edilebilir.

---

## 🚀 Hızlı Başlangıç (Otomatik)

### Tek Komutla Kurulum

```bash
bash scripts/fresh_start.sh
```

Bu script şunları yapar:
1. ✅ Ön gereksinimleri kontrol eder (Docker, Docker Compose)
2. ✅ `.env` dosyasını hazırlar
3. ✅ Environment değişkenlerini kontrol eder
4. ✅ Docker servislerini başlatır
5. ✅ Servis sağlık kontrollerini yapar
6. ✅ Veritabanı migrasyonlarını çalıştırır
7. ✅ Entegrasyon kurulumunu (opsiyonel) yapar
8. ✅ Son doğrulamayı yapar

**Süre**: ~5-10 dakika (Docker build'e bağlı)

---

## 📋 Manuel Kurulum (Adım Adım)

### ADIM 1: Ön Gereksinimler

#### Docker Kurulumu

**Windows:**
- [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop) indirin ve kurun
- Docker Desktop'ı başlatın ve çalıştığını doğrulayın

**macOS:**
- [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop) indirin ve kurun
- Docker Desktop'ı başlatın

**Linux:**
```bash
# Docker kurulumu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose kurulumu
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Doğrulama

```bash
docker --version
docker-compose --version
# veya
docker compose version
```

---

### ADIM 2: Projeyi Klonlama

```bash
# Projeyi klonlayın
git clone https://github.com/brdfb/dyn365hunterv3.git
cd dyn365hunterv3
```

---

### ADIM 3: Environment Dosyası Hazırlama

```bash
# .env dosyasını oluşturun
cp .env.example .env

# .env dosyasını düzenleyin (gerekli değerleri ayarlayın)
# Önemli: Production için mutlaka değiştirin:
# - DATABASE_URL
# - POSTGRES_PASSWORD
# - HUNTER_PARTNER_CENTER_CLIENT_ID (opsiyonel)
# - HUNTER_PARTNER_CENTER_TENANT_ID (opsiyonel)
# - HUNTER_D365_* (opsiyonel)
```

**Minimum Gerekli Değişkenler:**
```bash
DATABASE_URL=postgresql://dyn365hunter:password123@postgres:5432/dyn365hunter
POSTGRES_USER=dyn365hunter
POSTGRES_PASSWORD=password123  # ⚠️ Production'da mutlaka değiştirin!
POSTGRES_DB=dyn365hunter
REDIS_URL=redis://redis:6379/0
ENVIRONMENT=development  # veya production
```

---

### ADIM 4: Environment Kontrolü

```bash
# Environment değişkenlerini kontrol edin
bash scripts/check_env_completeness.sh
```

Bu script:
- ✅ Zorunlu değişkenleri kontrol eder
- ✅ Feature flag'leri kontrol eder
- ✅ Entegrasyon credential'larını kontrol eder
- ✅ Eksik değişkenleri listeler

---

### ADIM 5: Docker Servislerini Başlatma

```bash
# Container'ları build et ve başlat
docker-compose build
docker-compose up -d

# Servislerin hazır olmasını bekleyin (15-30 saniye)
sleep 15

# Servis durumunu kontrol edin
docker-compose ps
```

**Beklenen Çıktı:**
```
NAME                    STATUS
dyn365hunter-postgres   Up
dyn365hunter-redis      Up
dyn365hunter-api        Up
dyn365hunter-worker     Up
```

---

### ADIM 6: Servis Sağlık Kontrolleri

```bash
# PostgreSQL kontrolü
docker-compose exec postgres pg_isready -U dyn365hunter

# Redis kontrolü
docker-compose exec redis redis-cli ping
# Beklenen: PONG

# API kontrolü
curl http://localhost:8000/healthz
# Beklenen: {"status":"ok","database":"connected","environment":"development"}
```

---

### ADIM 7: Veritabanı Migrasyonları

```bash
# Alembic migrasyonlarını çalıştır
docker-compose exec api alembic upgrade head

# Migrasyon durumunu kontrol et
docker-compose exec api alembic current
```

**Beklenen:** `08f51db8dce0 (head)` veya daha yeni bir revision

---

### ADIM 8: Entegrasyon Kurulumu (Opsiyonel)

#### Partner Center Entegrasyonu

```bash
# Feature flag'i aktifleştir ve credential'ları kontrol et
bash scripts/enable_integrations.sh

# İlk authentication (Device Code Flow)
docker-compose exec api python -m app.tools.partner_center_device_code_flow
```

**Gereksinimler:**
- `HUNTER_PARTNER_CENTER_CLIENT_ID` (Azure AD App Registration)
- `HUNTER_PARTNER_CENTER_TENANT_ID` (Azure AD Tenant ID)
- `HUNTER_PARTNER_CENTER_ENABLED=true`

#### Dynamics 365 Entegrasyonu

```bash
# Feature flag'i aktifleştir ve credential'ları kontrol et
bash scripts/enable_integrations.sh
```

**Gereksinimler:**
- `HUNTER_D365_BASE_URL` (D365 Web API URL)
- `HUNTER_D365_CLIENT_ID` (Azure AD App Registration)
- `HUNTER_D365_CLIENT_SECRET` (Azure AD App Secret)
- `HUNTER_D365_TENANT_ID` (Azure AD Tenant ID)
- `HUNTER_D365_ENABLED=true`

---

## ✅ Kurulum Sonrası Doğrulama

### 1. API Health Check

```bash
curl http://localhost:8000/healthz
```

**Beklenen:**
```json
{
  "status": "ok",
  "database": "connected",
  "environment": "development"
}
```

### 2. Mini UI Erişimi

Tarayıcıda açın:
```
http://localhost:8000
```

### 3. Log Kontrolü

```bash
# API logları
docker-compose logs -f api

# Worker logları
docker-compose logs -f worker

# Tüm servisler
docker-compose logs -f
```

---

## 🔧 Sorun Giderme

### Docker Servisleri Başlamıyor

```bash
# Logları kontrol edin
docker-compose logs

# Container'ları temizleyip yeniden başlatın
docker-compose down
docker-compose up -d --build
```

### Database Bağlantı Hatası

```bash
# PostgreSQL'in hazır olduğunu kontrol edin
docker-compose exec postgres pg_isready -U dyn365hunter

# .env dosyasındaki DATABASE_URL'i kontrol edin
grep DATABASE_URL .env
```

### API Health Check Başarısız

```bash
# API container'ının çalıştığını kontrol edin
docker-compose ps api

# API loglarını kontrol edin
docker-compose logs api

# Container'ı yeniden başlatın
docker-compose restart api
```

### Migrasyon Hataları

```bash
# Migrasyon durumunu kontrol edin
docker-compose exec api alembic current

# Migrasyon geçmişini kontrol edin
docker-compose exec api alembic history

# Veritabanını sıfırlamak isterseniz (⚠️ DİKKAT: Veri kaybı!)
bash scripts/reset_db_with_alembic.sh
```

---

## 📚 İlgili Dokümantasyon

- **Development Environment**: `docs/reference/DEVELOPMENT-ENVIRONMENT.md`
- **Tools Usage**: `docs/reference/TOOLS-USAGE.md`
- **Integrations Status**: `docs/reference/INTEGRATIONS-ENABLED-STATUS.md`
- **Production Deployment**: `docs/reference/PRODUCTION-DEPLOYMENT-GUIDE.md`
- **Docker Troubleshooting**: `docs/reference/DOCKER-TROUBLESHOOTING.md`

---

## 🎯 Sonraki Adımlar

1. ✅ **Kurulum tamamlandı** → API'yi test edin
2. ✅ **Entegrasyonlar** → Partner Center ve D365'ı aktifleştirin
3. ✅ **İlk Domain** → Bir domain ingest edip scan edin
4. ✅ **UI Test** → Mini UI'da sonuçları kontrol edin

---

**Son Güncelleme**: 2025-01-30  
**Durum**: ✅ **Production Ready**

