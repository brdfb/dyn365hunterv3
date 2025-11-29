# Development Environment Guide - Hunter v1.0

**Tarih**: 2025-01-30  
**Versiyon**: v1.0.0  
**Status**: ✅ **Production Ready**  
**Kullanım**: Development environment setup, configuration, ve daily workflow rehberi

---

## 📋 İçindekiler

1. [Environment Architecture](#environment-architecture)
2. [Development Environment Setup](#development-environment-setup)
3. [Dev vs Prod Differences](#dev-vs-prod-differences)
4. [Environment Variables](#environment-variables)
5. [WSL2 Çalışma Rehberi](#wsl2-çalışma-rehberi)
6. [Common Commands](#common-commands)
7. [Daily Workflow](#daily-workflow)
8. [Troubleshooting](#troubleshooting)
9. [Production Environment](#production-environment)

---

## 🏗️ Environment Architecture

### Mevcut Ortam Yapısı

#### Host System
- **OS**: Windows 10/11 (NT 10.0-26200)
- **Shell**: Git Bash (MINGW64) veya WSL2 (Ubuntu)
- **Docker**: Docker Desktop (Windows)
- **Docker Context**: `desktop-linux` (WSL2 backend)

#### Container Runtime
- **Platform**: WSL2 (Windows Subsystem for Linux 2)
- **Linux Kernel**: `6.6.87.2-microsoft-standard-WSL2`
- **Architecture**: x86_64

### Host → Container Flow

```
Windows PC (Local)
    ↓
Docker Desktop (Windows)
    ↓
WSL2 (Linux Kernel 6.6.87.2)
    ↓
Docker Containers (Linux)
    ├── dyn365hunter-api (Linux)
    ├── dyn365hunter-postgres (Linux)
    ├── dyn365hunter-redis (Linux)
    └── dyn365hunter-worker (Linux)
```

### Docker Containers

#### Container Names (dyn365hunter-* prefix)

1. **dyn365hunter-api**
   - Image: `domainhunterv3-api`
   - Command: `uvicorn app.main:ap…`
   - Ports: `0.0.0.0:8000->8000/tcp`
   - Status: ✅ Healthy
   - Hostname: Linux container (WSL2)

2. **dyn365hunter-postgres**
   - Image: `postgres:15-alpine`
   - Ports: `0.0.0.0:5432->5432/tcp`
   - Status: ✅ Healthy

3. **dyn365hunter-redis**
   - Image: `redis:7-alpine`
   - Ports: `0.0.0.0:6379->6379/tcp`
   - Status: ✅ Healthy

4. **dyn365hunter-worker**
   - Image: `domainhunterv3-worker`
   - Command: `celery -A app.core.…`
   - Status: ✅ Running

#### Network
- **Network Name**: `dyn365hunter-network`
- **Type**: Docker bridge network
- **All containers connected**: ✅

### Network Access

- **From Windows Host**: `localhost:8000` → `dyn365hunter-api:8000`
- **From Windows Host**: `localhost:5432` → `dyn365hunter-postgres:5432`
- **From Windows Host**: `localhost:6379` → `dyn365hunter-redis:6379`
- **Container-to-Container**: `dyn365hunter-network` (internal Docker network)

---

## 🎯 Development Environment Setup

### Önerilen Ortam: WSL2 + Docker Desktop

#### Neden WSL2?

1. **Docker Compose Performansı**
   - WSL2'de Docker container'ları native Linux performansında çalışır
   - File system mount'ları daha hızlı
   - Volume performansı daha iyi

2. **Production'a Yakınlık**
   - Production ortamı Linux (container'lar)
   - CI/CD pipeline Linux'ta çalışıyor (GitHub Actions: `ubuntu-latest`)
   - Aynı ortamda test etmek = daha az sorun

3. **Python Venv Uyumluluğu**
   - Linux venv standart (`.venv/bin/activate`)
   - Windows venv karmaşası yok
   - Cross-platform uyumluluk sorunları yok

4. **Terminal Deneyimi**
   - Native Linux shell (bash)
   - Git komutları daha hızlı
   - Script'ler daha güvenilir çalışır

### Kurulum Adımları (WSL2)

#### 1. WSL2 Kurulumu
```bash
# Windows PowerShell (Admin)
wsl --install -d Ubuntu-22.04
# veya mevcut WSL'i güncelle
wsl --update
```

#### 2. Docker Desktop WSL2 Entegrasyonu
- Docker Desktop → Settings → General → "Use the WSL 2 based engine" ✅
- Docker Desktop → Settings → Resources → WSL Integration → Ubuntu-22.04 ✅

#### 3. Proje Kurulumu
```bash
# WSL terminalinde
cd ~/projects  # veya istediğiniz klasör
git clone https://github.com/brdfb/dyn365hunterv3.git
cd dyn365hunterv3

# Venv oluştur (Linux venv)
bash setup_venv.sh
source .venv/bin/activate

# Docker setup
bash setup_dev.sh
```

### Alternatif Ortamlar

#### Git Bash (Windows) - ⚠️ Önerilmez

**Avantajlar:**
- Hızlı başlangıç (WSL kurulumu gerekmez)
- Windows dosya sistemine direkt erişim

**Dezavantajlar:**
- Windows venv kullanır (`.venv/Scripts/activate`)
- Docker performansı daha düşük
- Production ortamından farklı
- File system mount sorunları olabilir

**Kullanım:**
```bash
# Git Bash'te
bash setup_venv.sh
source .venv/Scripts/activate  # Windows venv
bash setup_dev.sh
```

#### Windows Native (PowerShell/CMD) - ❌ Önerilmez

**Sorunlar:**
- Docker Compose performans sorunları
- Path separator farklılıkları (`\` vs `/`)
- Script uyumluluk sorunları
- Production ortamından çok farklı

### Sonuç

**En İyi Seçenek:** WSL2 + Docker Desktop + Linux venv

**Kabul Edilebilir:** Git Bash + Docker Desktop + Windows venv (sadece hızlı test için)

**Önerilmez:** Windows Native (PowerShell/CMD)

---

## 🔄 Dev vs Prod Differences

### Özet

**Kod seviyesinde:** ✅ **EŞİT** - Aynı kod, aynı branch  
**Konfigürasyon seviyesinde:** ⚠️ **FARKLI** - Environment variable'lar ve feature flag'ler farklı

### Feature Flags (Her İkisi de Default: `false`)

#### Partner Center Integration
- **Dev:** `HUNTER_PARTNER_CENTER_ENABLED=false` (default)
- **Prod:** `HUNTER_PARTNER_CENTER_ENABLED=false` (default)
- **Durum:** ✅ **EŞİT** - Her ikisi de kapalı (MVP-safe)

#### Dynamics 365 Integration
- **Dev:** `HUNTER_D365_ENABLED=false` (default)
- **Prod:** `HUNTER_D365_ENABLED=false` (default)
- **Durum:** ✅ **EŞİT** - Her ikisi de kapalı (MVP-safe)

#### IP Enrichment
- **Dev:** `HUNTER_ENRICHMENT_ENABLED=false` (default)
- **Prod:** `HUNTER_ENRICHMENT_ENABLED=false` (default)
- **Durum:** ✅ **EŞİT** - Her ikisi de kapalı (default)

### Environment-Based Differences

#### 1. Celery Sync Interval (Partner Center)

**Kod:** `app/core/celery_app.py` (lines 45-49)

```python
"schedule": (
    30.0 if settings.environment == "development" 
    else float(settings.partner_center_sync_interval)
),
```

- **Dev:** `30 saniye` (auto-override, test için)
- **Prod:** `600 saniye` (10 dakika, `HUNTER_PARTNER_CENTER_SYNC_INTERVAL` env var)
- **Durum:** ⚠️ **FARKLI** - Dev'de daha sık sync (test için)

#### 2. Log Level

**Kod:** `app/core/logging.py` (line 34)

```python
log_level = "DEBUG" if settings.environment == "development" else "INFO"
```

- **Dev:** `DEBUG` (detaylı loglar)
- **Prod:** `INFO` (sadece önemli loglar)
- **Durum:** ⚠️ **FARKLI** - Dev'de daha detaylı logging

#### 3. Log Format

**Kod:** `app/core/logging.py` (lines 20-23)

```python
if settings.environment == "production":
    _processors.append(structlog.processors.JSONRenderer())  # JSON output for production
else:
    _processors.append(structlog.dev.ConsoleRenderer())  # Pretty format for dev
```

- **Dev:** Pretty console format (okunabilir)
- **Prod:** JSON format (log aggregation için)
- **Durum:** ⚠️ **FARKLI** - Dev'de human-readable, Prod'da machine-readable

#### 4. Sentry Error Tracking

**Kod:** `app/core/error_tracking.py` (lines 12-22)

```python
if settings.environment in {"production", "staging"}:
    if hasattr(settings, "sentry_dsn") and settings.sentry_dsn:
        sentry_sdk.init(...)
```

- **Dev:** Sentry **disabled** (sentry_dsn kontrol edilmez)
- **Prod:** Sentry **enabled** (if `HUNTER_SENTRY_DSN` provided)
- **Durum:** ⚠️ **FARKLI** - Prod'da error tracking aktif

#### 5. Environment Variable

**Kod:** `app/config.py` (line 27)

```python
environment: str = "development"  # Default
```

- **Dev:** `ENVIRONMENT=development` (default)
- **Prod:** `ENVIRONMENT=production` (zorunlu)
- **Durum:** ⚠️ **FARKLI** - Environment name farklı

### Özet Tablo

| Özellik | Dev | Prod | Durum |
|---------|-----|------|-------|
| **Kod** | ✅ Aynı | ✅ Aynı | ✅ **EŞİT** |
| **Feature Flags** | `false` (default) | `false` (default) | ✅ **EŞİT** |
| **Partner Center Sync** | 30s | 600s | ⚠️ **FARKLI** |
| **Log Level** | `DEBUG` | `INFO` | ⚠️ **FARKLI** |
| **Log Format** | Pretty | JSON | ⚠️ **FARKLI** |
| **Sentry** | Disabled | Enabled (if DSN) | ⚠️ **FARKLI** |
| **Environment** | `development` | `production` | ⚠️ **FARKLI** |

---

## ⚙️ Environment Variables

### ✅ REQUIRED (Zorunlu)

#### Database
- `DATABASE_URL` - PostgreSQL connection string
  - Format: `postgresql://user:password@host:port/database`
  - Example: `postgresql://dyn365hunter:password123@postgres:5432/dyn365hunter`
  - **Production**: Use secure credentials, SSL enabled (`?sslmode=require`)

#### Redis
- `REDIS_URL` - Redis connection string
  - Format: `redis://host:port/db` or `redis://:password@host:port/db`
  - Example: `redis://redis:6379/0`
  - **Production**: Use secure credentials if password-protected

#### API Configuration
- `API_HOST` - API server host (default: `0.0.0.0`)
- `API_PORT` - API server port (default: `8000`)
- `LOG_LEVEL` - Logging level (default: `INFO`)
  - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
  - **Production**: `INFO` or `WARNING` (not `DEBUG`)
- `ENVIRONMENT` - Environment name (default: `development`)
  - **Production**: Must be `production`
  - Used for feature flags and environment-specific behavior

### ⚠️ OPTIONAL (Önerilen)

#### Error Tracking
- `HUNTER_SENTRY_DSN` - Sentry DSN for error tracking
  - Format: `https://<key>@<org>.ingest.sentry.io/<project>`
  - **Production**: Strongly recommended

#### Database Connection Pooling
- `HUNTER_DB_POOL_SIZE` - Connection pool size (default: `20`)
- `HUNTER_DB_MAX_OVERFLOW` - Max overflow connections (default: `10`)

### 🔒 FEATURE FLAGS (Post-MVP - Şimdilik OFF)

#### IP Enrichment
- `HUNTER_ENRICHMENT_ENABLED` - IP enrichment feature flag (default: `false`)

#### Partner Center Integration
- `HUNTER_PARTNER_CENTER_ENABLED` - Partner Center feature flag (default: `false`)
- **Production v1.0**: `false` (Post-MVP feature)

#### Dynamics 365 Integration
- `HUNTER_D365_ENABLED` - D365 feature flag (default: `false`)
- **Production v1.0**: `false` (Post-MVP feature)

### Production Environment Template

```bash
# Environment
ENVIRONMENT=production

# Database (Production - SSL enabled)
DATABASE_URL=postgresql://<user>:<password>@<db-host>:5432/<database>?sslmode=require

# Redis (Production)
REDIS_URL=redis://<redis-host>:6379/0
# Or with password: redis://:<password>@<redis-host>:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Error Tracking (Strongly Recommended)
HUNTER_SENTRY_DSN=https://<key>@<org>.ingest.sentry.io/<project>

# Database Connection Pooling (Optional - defaults are usually fine)
HUNTER_DB_POOL_SIZE=20
HUNTER_DB_MAX_OVERFLOW=10

# Feature Flags (Phase 1: Both OFF)
HUNTER_PARTNER_CENTER_ENABLED=false
HUNTER_D365_ENABLED=false
HUNTER_ENRICHMENT_ENABLED=false
```

---

## 🐧 WSL2 Çalışma Rehberi

### Proje Konumu

#### WSL2 Path
```
/home/beredhome/projects/dyn365hunterv3
```

#### Windows Path (Mapping)
```
C:\Users\beredhome\projects\dyn365hunterv3
```

#### Proje Dizinine Geçme
```bash
# WSL2 terminalinde
cd ~/projects/dyn365hunterv3
```

### Cursor'u WSL2'den Açma

#### Adım 1: WSL2 Terminalinde Proje Dizinine Geç
```bash
cd ~/projects/dyn365hunterv3
```

#### Adım 2: Cursor'u Aç
```bash
# Cursor'u Remote WSL modunda aç
cursor .  # veya code .
```

**Not**: İlk seferinde "Remote WSL" extension'ı yüklenmesi istenebilir. Yükle.

#### Adım 3: Doğrulama
- Cursor açıldığında sol alt köşede "WSL: Ubuntu" veya benzeri bir gösterge görünmeli
- Terminal otomatik olarak WSL2 terminali olmalı

### Docker Komutları

#### Container Durumunu Kontrol Et
```bash
# Container'ların durumunu göster
docker-compose ps
```

**Çıktı Örneği:**
```
NAME                    IMAGE                STATUS                   PORTS
dyn365hunter-api        dyn365hunterv3-api   Up X minutes (healthy)   0.0.0.0:8000->8000/tcp
dyn365hunter-postgres   postgres:15-alpine   Up X minutes (healthy)   0.0.0.0:5432->5432/tcp
```

#### Container'ları Başlat
```bash
# Detached mode (arka planda çalışır)
docker-compose up -d
```

#### Container'ları Durdur
```bash
# Container'ları durdur ve kaldır
docker-compose down
```

#### Container'ları Yeniden Başlat
```bash
# Önce durdur, sonra başlat
docker-compose down
docker-compose up -d
```

#### Logs Görüntüleme
```bash
# API container loglarını görüntüle (follow mode)
docker-compose logs -f api

# Tüm container loglarını görüntüle
docker-compose logs -f

# Son 50 satır log
docker-compose logs --tail=50 api
```

**Çıkış**: `Ctrl+C` ile log takibini durdur

### Health Check

#### API Health Check
```bash
# Health endpoint'ini kontrol et
curl http://localhost:8000/healthz
```

**Beklenen Çıktı:**
```json
{"status":"ok","database":"connected","environment":"development"}
```

#### PostgreSQL Kontrolü
```bash
# PostgreSQL container'ına bağlan
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter

# Tabloları listele
\dt

# VIEW'leri listele
\dv

# Çıkış
\q
```

---

## 📋 Common Commands

### Setup Dev Environment

**Usage:** `/setup-dev` or mention "setup dev environment"

**What it does:**
- Checks Docker/Docker Compose availability
- Copies `.env.example` to `.env` if not exists
- Runs `docker-compose up -d` (PostgreSQL, Redis, API, Worker)
- Waits for PostgreSQL and Redis healthcheck (max 30s)
- Runs schema migration automatically
- Verifies `/healthz` endpoint
- Prints access URLs (API, Mini UI)

**Command:**
```bash
bash setup_dev.sh
```

### Run Tests

**Usage:** `/run-tests` or mention "run tests"

**What it does:**
- Runs all tests in `tests/` directory
- Shows test coverage
- Validates core modules (normalizer, analyzer, scorer, ingest)

**Command (Docker - Recommended):**
```bash
bash scripts/run-tests-docker.sh
# Or directly:
docker-compose exec api pytest tests/ -v --tb=short
```

**Command (Local - requires venv):**
```bash
# Activate venv first
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Run tests
pytest tests/ -v --cov=app --cov-report=term
```

### Check Health

**Usage:** `/health` or mention "check health"

**What it does:**
- Tests `/healthz` endpoint
- Verifies database connection
- Returns status: `{"status": "ok", "database": "connected"}`

**Command:**
```bash
curl http://localhost:8000/healthz
```

### View Logs

**Usage:** `/logs` or mention "view logs"

**What it does:**
- Shows real-time logs from FastAPI container
- Filters for errors/warnings

**Command:**
```bash
docker-compose logs -f api
```

### Alembic Migration

**Usage:** Migration işlemleri için

**Commands:**
```bash
# Check current migration version
docker-compose exec api alembic current

# Run migrations
docker-compose exec api alembic upgrade head

# View migration history
docker-compose exec api alembic history
```

### API Versioning

**Commands:**
```bash
# API version kontrolü
curl http://localhost:8000/openapi.json | grep version

# Test v1 endpoint
curl http://localhost:8000/api/v1/leads

# Test legacy endpoint (backward compatibility)
curl http://localhost:8000/leads
```

---

## 🔄 Daily Workflow

### Günlük Geliştirme (WSL2)

```bash
# 1. WSL terminalini aç
wsl

# 2. Proje klasörüne git
cd ~/projects/dyn365hunterv3

# 3. Venv'i aktive et
source .venv/bin/activate

# 4. Docker servisleri çalışıyor mu kontrol et
docker-compose ps

# 5. Kod yaz, test et
pytest tests/ -v
curl http://localhost:8000/healthz

# 6. Değişiklikleri commit et
git add .
git commit -m "feat: new feature"
```

### Sabah Başlangıç
```bash
# 1. WSL2 terminalinde proje dizinine geç
cd ~/projects/dyn365hunterv3

# 2. Container'ları başlat
docker-compose up -d

# 3. Health check yap
curl http://localhost:8000/healthz

# 4. Cursor'u aç (eğer açık değilse)
cursor .
```

### Geliştirme Sırasında
```bash
# Logs takip et (ayrı terminal)
docker-compose logs -f api

# Container durumunu kontrol et
docker-compose ps

# Health check
curl http://localhost:8000/healthz
```

### Akşam Kapanış
```bash
# Container'ları durdur (veriler kalır, sadece container'lar durur)
docker-compose down
```

### Veritabanını Sıfırlama (DİKKAT: Tüm veriler silinir!)
```bash
# Container'ları ve volume'ları kaldır
docker-compose down -v

# Yeniden başlat (schema migration otomatik çalışır)
docker-compose up -d
```

---

## 🔧 Troubleshooting

### Sorun 1: Container'lar Başlamıyor

**Kontrol:**
```bash
# Docker çalışıyor mu?
docker --version

# Docker Compose çalışıyor mu?
docker-compose --version

# Port'lar kullanımda mı?
docker-compose ps
```

**Çözüm:**
```bash
# Eski container'ları temizle
docker-compose down

# Yeniden başlat
docker-compose up -d
```

### Sorun 2: Health Check Başarısız

**Kontrol:**
```bash
# API container loglarını kontrol et
docker-compose logs api

# PostgreSQL container loglarını kontrol et
docker-compose logs postgres
```

**Çözüm:**
```bash
# Container'ları yeniden başlat
docker-compose restart

# Veya tamamen yeniden başlat
docker-compose down
docker-compose up -d
```

### Sorun 3: Schema Migration Başarısız

**Kontrol:**
```bash
# Migration script'i manuel çalıştır
docker-compose exec api alembic upgrade head
```

**Çözüm:**
```bash
# Container'ları yeniden başlat (setup_dev.sh migration'ı tekrar çalıştırır)
docker-compose down
bash setup_dev.sh
```

### Sorun 4: Port Zaten Kullanımda

**Kontrol:**
```bash
# Port 8000 kullanımda mı?
netstat -tuln | grep 8000

# Port 5432 kullanımda mı?
netstat -tuln | grep 5432
```

**Çözüm:**
```bash
# Eski container'ları durdur
docker-compose down

# Veya port'u değiştir (docker-compose.yml'de)
# ports:
#   - "8001:8000"  # 8000 yerine 8001 kullan
```

### Sorun 5: Volume Mount Çalışmıyor

**Kontrol:**
```bash
# Container içinde dosyalar görünüyor mu?
docker-compose exec api ls -la /app/app
```

**Çözüm:**
```bash
# Container'ları yeniden başlat
docker-compose restart api

# Veya tamamen yeniden build et
docker-compose down
docker-compose build
docker-compose up -d
```

### Sorun 6: WSL2 Path Mapping

**Sorun:** Windows path'leri (`C:\...`) WSL'de farklı (`/mnt/c/...`)

**Çözüm:**
- WSL2'de proje klasörünü Linux file system'inde tutun (`~/projects/`)
- Windows file system'inde (`/mnt/c/...`) çalışmak performans sorunlarına yol açabilir

---

## 🚀 Production Environment

### Production Environment Status

#### Development Environment
- **Lokasyon**: Local (Docker Compose)
- **Database**: `postgres:5432` (Docker container)
- **Redis**: `redis:6379` (Docker container)
- **API**: `localhost:8000` (Docker container)
- **Worker**: Celery worker (Docker container)
- **Status**: ✅ **ÇALIŞIYOR**

#### Production Environment
- **Lokasyon**: ⚠️ **BELİRLENMEMİŞ**
- **Database**: ⚠️ **BELİRLENMEMİŞ**
- **Redis**: ⚠️ **BELİRLENMEMİŞ**
- **API**: ⚠️ **BELİRLENMEMİŞ**
- **Worker**: ⚠️ **BELİRLENMEMİŞ**
- **Status**: ❌ **HENÜZ SET EDİLMEDİ**

### Production Ortamı Belirleme

#### Seçenekler

1. **Docker Compose (Aynı Dev Ortamı)**
   - **Avantaj**: Hızlı setup, aynı konfigürasyon
   - **Dezavantaj**: Production için önerilmez (single point of failure)
   - **Kullanım**: Test/staging için uygun

2. **Cloud Provider (AWS/Azure/GCP)**
   - **Avantaj**: Scalable, managed services, production-ready
   - **Dezavantaj**: Setup complexity, cost
   - **Kullanım**: Production için önerilir

3. **VPS/Server**
   - **Avantaj**: Full control, cost-effective
   - **Dezavantaj**: Manual setup, maintenance
   - **Kullanım**: Small-scale production için uygun

### Production Setup Checklist

#### 1. Production Ortamı Belirle
- [ ] **Production server/hosting seç** (AWS/Azure/GCP/VPS)
- [ ] **Production domain belirle** (örn: `api.hunter.example.com`)
- [ ] **SSL certificate setup** (Let's Encrypt veya managed SSL)

#### 2. Production Database Setup
- [ ] **Production PostgreSQL instance oluştur**
  - Managed service (RDS, Azure Database, Cloud SQL) veya
  - Self-hosted PostgreSQL server
- [ ] **Database credentials oluştur**
  - User: `hunter_prod`
  - Password: Secure password (key vault'ta sakla)
  - Database: `hunter_prod`
- [ ] **SSL connection enable et** (`sslmode=require`)
- [ ] **Backup strategy belirle** (daily automated backups)

#### 3. Production Redis Setup
- [ ] **Production Redis instance oluştur**
  - Managed service (ElastiCache, Azure Cache, Cloud Memorystore) veya
  - Self-hosted Redis server
- [ ] **Redis credentials oluştur** (password-protected)
- [ ] **Persistence enable et** (RDB + AOF)

#### 4. Production Environment Variables
- [ ] **Production `.env` dosyası oluştur**
  - Template: `docs/active/PRE-DEPLOYMENT-STATUS.md`
  - Placeholders'ı gerçek değerlerle değiştir
- [ ] **Secrets management setup** (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault)
- [ ] **Environment variables set et**:
  ```bash
  ENVIRONMENT=production
  DATABASE_URL=postgresql://user:password@prod-db:5432/hunter_prod?sslmode=require
  REDIS_URL=redis://:password@prod-redis:6379/0
  LOG_LEVEL=INFO
  HUNTER_SENTRY_DSN=https://...
  ```

#### 5. Production Deployment
- [ ] **Deployment script çalıştır**:
  ```bash
  ENVIRONMENT=production FORCE_PRODUCTION=yes bash scripts/deploy_production.sh
  ```
- [ ] **Health checks verify et**
- [ ] **Smoke tests çalıştır**

---

## 📝 Önemli Notlar

### 1. WSL2 Path Mapping
- WSL2'de proje: `/home/beredhome/projects/dyn365hunterv3`
- Windows'ta görünür: `C:\Users\beredhome\projects\dyn365hunterv3`
- **Önemli**: WSL2'de çalışırken WSL2 path'lerini kullan

### 2. Docker Volume Mount
- `./app:/app/app` - Hot reload için
- Kod değişiklikleri otomatik container'a yansır
- Uvicorn `--reload` modu aktif

### 3. Database Persistence
- PostgreSQL data: `postgres_data` volume'unda saklanır
- `docker-compose down` → Veriler kalır
- `docker-compose down -v` → **Tüm veriler silinir!**

### 4. Schema Migration
- `setup_dev.sh` otomatik migration yapar
- Manuel migration: `docker-compose exec api alembic upgrade head`

### 5. Cursor Remote WSL
- Cursor'u WSL2'den açmak için "Remote WSL" extension gerekli
- Extension otomatik yüklenir (ilk seferinde)
- Sol alt köşede "WSL: Ubuntu" gösterge görünmeli

### 6. Venv Uyumluluğu
- WSL2'de Linux venv kullan (`source .venv/bin/activate`)
- Git Bash'te Windows venv kullan (`source .venv/Scripts/activate`)
- İki ortam arasında geçiş sorunlu - her ortamda ayrı venv oluşturun

---

## 🎯 Hızlı Başlangıç Checklist

- [ ] WSL2 terminalinde `cd ~/projects/dyn365hunterv3`
- [ ] `docker-compose up -d` ile container'ları başlat
- [ ] `curl http://localhost:8000/healthz` ile health check
- [ ] `cursor .` ile Cursor'u aç
- [ ] Geliştirmeye başla!

---

## 🔗 İlgili Dosyalar

- `docker-compose.yml` - Docker servisleri
- `setup_dev.sh` - Otomatik setup script
- `app/db/migrate.py` - Schema migration script
- `README.md` - Genel proje dokümantasyonu
- `docs/reference/PRODUCTION-DEPLOYMENT-GUIDE.md` - Production deployment guide
- `docs/reference/DEV-PROD-DIFFERENCES.md` - Dev vs Prod differences (detailed)
- `docs/reference/ENVIRONMENT-VARIABLES-CHECKLIST.md` - Environment variables checklist (detailed)

---

**Last Updated**: 2025-01-30  
**Status**: ✅ **Production Ready** - Comprehensive development environment guide
