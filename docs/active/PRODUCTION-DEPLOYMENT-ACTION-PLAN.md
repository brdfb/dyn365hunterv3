# 🚀 Production Deployment Action Plan

**Tarih**: 2025-01-30  
**Durum**: 🔄 **IN PROGRESS**  
**Priority**: 🔴 **CRITICAL**

---

## ✅ Tamamlananlar

### 1. Bug Fixes
- ✅ **Leads Endpoint 500 Error**: FIXED
  - Root cause: `referral_type` parameter missing in `v1/leads.py`
  - Fix: Added parameter and passed to `get_leads` function
  - Status: ✅ All tests passing (200 OK)

### 2. Git & Documentation
- ✅ **Git Commit**: Leads 500 bug fix committed
- ✅ **Git Push**: Pushed to `feature/partner-center-phase1` branch
- ✅ **CHANGELOG**: Updated with bug fix
- ✅ **Documentation**: Created comprehensive bug fix documentation

---

## ⚠️ YAPILMASI GEREKENLER

### 🔴 CRITICAL - Production Blocker

#### 1. Production Environment Belirleme
**Status**: ❌ **YAPILMADI**

**Sorun**: Production ortamı henüz belirlenmemiş.

**Seçenekler**:
1. **Docker Compose (Aynı Dev)** - Test/staging için
2. **Cloud Provider** (AWS/Azure/GCP) - Production için önerilir
3. **VPS/Server** - Small-scale production için

**Action Required**:
- [ ] Production hosting seç (AWS/Azure/GCP/VPS)
- [ ] Production domain belirle
- [ ] SSL certificate setup

**Dosya**: `docs/active/PRODUCTION-ENVIRONMENT-STATUS.md`

---

#### 2. Production Environment Variables Setup
**Status**: ❌ **YAPILMADI**

**Action Required**:
- [ ] Production `.env` dosyası oluştur
  - Template: `docs/active/PRE-DEPLOYMENT-STATUS.md` (lines 41-102)
- [ ] Production database connection string set et
- [ ] Production Redis connection string set et
- [ ] Sentry DSN set et
- [ ] Feature flags set et (Phase 1: Both OFF)

**Commands**:
```bash
# Production .env template
cp .env.example .env.production

# Edit .env.production with production values
# - DATABASE_URL: Production PostgreSQL (SSL enabled)
# - REDIS_URL: Production Redis
# - ENVIRONMENT=production
# - LOG_LEVEL=INFO
# - HUNTER_SENTRY_DSN: Production Sentry DSN
# - HUNTER_PARTNER_CENTER_ENABLED=false (Phase 1)
# - HUNTER_D365_ENABLED=false (Phase 1)
```

---

#### 3. Production Database Setup
**Status**: ❌ **YAPILMADI**

**Action Required**:
- [ ] Production PostgreSQL instance oluştur
  - Managed service (RDS, Azure Database, Cloud SQL) veya
  - Self-hosted PostgreSQL server
- [ ] Database credentials oluştur
- [ ] SSL connection enable et (`sslmode=require`)
- [ ] Backup strategy belirle (daily automated backups)

**Commands**:
```bash
# Production database connection test
psql "postgresql://user:password@prod-db:5432/hunter_prod?sslmode=require" -c "SELECT version();"
```

---

#### 4. Production Redis Setup
**Status**: ❌ **YAPILMADI**

**Action Required**:
- [ ] Production Redis instance oluştur
  - Managed service (ElastiCache, Azure Cache, Cloud Memorystore) veya
  - Self-hosted Redis server
- [ ] Redis credentials oluştur (password-protected)
- [ ] Persistence enable et (RDB + AOF)

**Commands**:
```bash
# Production Redis connection test
redis-cli -h prod-redis -p 6379 -a password PING
# Expected: PONG
```

---

#### 5. Production Database Backup
**Status**: ❌ **YAPILMADI**

**Action Required**:
- [ ] Pre-deployment backup al
- [ ] Backup integrity verify et
- [ ] Backup location belirle (secure storage)

**Commands**:
```bash
# Production database backup
pg_dump "postgresql://user:password@prod-db:5432/hunter_prod?sslmode=require" \
  > backups/backup_pre_v1.0_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
ls -lh backups/backup_pre_v1.0_*.sql
head -20 backups/backup_pre_v1.0_*.sql  # Check SQL format
```

---

#### 6. Production Migration Test
**Status**: ❌ **YAPILMADI**

**Action Required**:
- [ ] Migration dry-run (staging/prod shadow)
- [ ] Current migration version check
- [ ] Rollback plan verify

**Commands**:
```bash
# Check current migration version
alembic current

# Dry-run migration (staging)
ENVIRONMENT=staging alembic upgrade head --sql

# Production migration (when ready)
ENVIRONMENT=production FORCE_PRODUCTION=yes alembic upgrade head
```

---

#### 7. Production Smoke Tests
**Status**: ❌ **YAPILMADI**

**Action Required**:
- [ ] Health checks verify
- [ ] Core endpoints test
- [ ] Database connection test
- [ ] Redis connection test

**Commands**:
```bash
# Health checks
curl http://prod-api:8000/healthz/live
curl http://prod-api:8000/healthz/ready
curl http://prod-api:8000/healthz/startup
curl http://prod-api:8000/healthz/metrics

# Core endpoints
curl http://prod-api:8000/api/v1/leads?limit=1
curl http://prod-api:8000/api/v1/companies?limit=1

# Use pre_deployment_check.sh
bash scripts/pre_deployment_check.sh
```

---

## 📋 Execution Order

### Phase 1: Environment Setup (1-2 saat)
1. ✅ Production environment belirle
2. ✅ Production database setup
3. ✅ Production Redis setup
4. ✅ Production environment variables set et

### Phase 2: Pre-Deployment (1 saat)
5. ✅ Production database backup al
6. ✅ Production migration test (dry-run)

### Phase 3: Deployment (30 dakika)
7. ✅ Production deployment script çalıştır
8. ✅ Production smoke tests çalıştır

---

## 🎯 Sonraki Adım

**IMMEDIATE ACTION**: Production ortamı belirleme

**Seçenekler**:
1. **Docker Compose** (Test/staging için) - Hızlı setup
2. **Cloud Provider** (AWS/Azure/GCP) - Production için önerilir
3. **VPS/Server** - Small-scale production için

**Karar verildikten sonra**:
- Production database setup
- Production Redis setup
- Production environment variables set et
- Production deployment çalıştır

---

## 📝 Notlar

- **Development**: Local Docker Compose (✅ çalışıyor)
- **Production**: Henüz belirlenmemiş (⚠️ **KARAR VERİLMELİ**)
- **WSL**: Windows üzerinde Git Bash kullanılıyor (WSL gerekli değil)
- **Git**: ✅ Committed & Pushed (`feature/partner-center-phase1`)

---

**Last Updated**: 2025-01-30  
**Status**: 🔄 **IN PROGRESS** - Production ortamı belirlenmeli

