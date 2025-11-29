# 🚀 Pre-Deployment Checklist - Quick Start Guide

**Tarih**: 2025-01-30  
**Durum**: ✅ **Checklist Hazır** - Execution bekliyor  
**Süre**: 2-3 gün (6 saat toplam)

---

## 📋 Hızlı Başlangıç

Pre-deployment checklist'i tamamlamak için şu adımları takip edin:

### 1️⃣ Checklist'i İncele

**Ana Checklist**: `docs/active/PRE-DEPLOYMENT-CHECKLIST-EXECUTION.md`
- Day 1: Environment Setup (2 saat)
- Day 2: Migration & Backup (2 saat)
- Day 3: Deployment & Verification (2 saat)

### 2️⃣ Mevcut Durumu Kontrol Et

**Status Report**: `docs/active/PRE-DEPLOYMENT-STATUS.md`
- ✅ Tamamlananlar (Development ortamında)
- ⚠️ Yapılması gerekenler (Production için)
- 📋 Production environment variables template

### 3️⃣ Verification Script Çalıştır

```bash
# Development ortamında (mevcut durumu kontrol et)
bash scripts/pre_deployment_check.sh

# Production ortamında (deployment öncesi)
# Production .env dosyasını set ettikten sonra
bash scripts/pre_deployment_check.sh
```

---

## 🎯 Production İçin Yapılacaklar

### 🔴 CRITICAL (Production Blocker)

1. **Environment Variables Setup**
   - Production `.env` dosyası oluştur
   - Template: `docs/active/PRE-DEPLOYMENT-STATUS.md` (Production Environment Variables Template)
   - Placeholder'ları gerçek değerlerle değiştir

2. **Database Migration**
   - Alembic current check
   - Migration dry-run (staging'de)
   - Schema verification (G20 columns)

3. **Database Backup**
   - Pre-deployment backup al
   - Restore dry-run test (staging'de)

### 🟡 HIGH (Önerilen)

4. **Sentry Setup**
   - DSN verification
   - Test error generation
   - Dashboard verification

5. **Smoke Tests**
   - Core endpoints
   - Sales Engine
   - Bulk Ops
   - Rate Limiting
   - Cache

6. **API Versioning**
   - v1 endpoints test
   - Legacy endpoints decision

---

## 📝 Checklist Execution

### Day 1: Environment Setup (2 saat)

1. Environment variables set et (production .env)
2. Database connection test
3. Redis connection test
4. Sentry DSN verification

**Referans**: `docs/active/PRE-DEPLOYMENT-CHECKLIST-EXECUTION.md` - Section 1

### Day 2: Migration & Backup (2 saat)

1. Database backup al
2. Restore dry-run test (staging)
3. Migration test (dry-run)
4. Rollback plan test

**Referans**: `docs/active/PRE-DEPLOYMENT-CHECKLIST-EXECUTION.md` - Section 2

### Day 3: Deployment & Verification (2 saat)

1. Health checks verification
2. Deployment script dry-run
3. Smoke tests
4. Monitoring setup
5. API versioning verification

**Referans**: `docs/active/PRE-DEPLOYMENT-CHECKLIST-EXECUTION.md` - Section 3

---

## ✅ Completion Criteria

Tüm checklist tamamlandığında:

- ✅ All health endpoints return 200 OK
- ✅ Sentry test event visible in dashboard
- ✅ Backup command documented + restore tested
- ✅ Redis PING = PONG
- ✅ Database connection OK
- ✅ v1 endpoints working
- ✅ Legacy endpoints decision documented
- ✅ Migration dry-run successful
- ✅ Rollback plan tested
- ✅ Smoke tests passing

---

## 🔗 İlgili Dosyalar

### Checklist & Status
- `docs/active/PRE-DEPLOYMENT-CHECKLIST-EXECUTION.md` - Detaylı execution checklist
- `docs/active/PRE-DEPLOYMENT-STATUS.md` - Status report ve production template
- `docs/active/PRODUCTION-GO-NO-GO-ANALYSIS.md` - Go/No-Go analizi

### Scripts
- `scripts/pre_deployment_check.sh` - Verification script
- `scripts/deploy_production.sh` - Deployment script

### Reference Guides
- `docs/reference/PRODUCTION-CHECKLIST-RUNBOOK.md` - Detailed runbook (2 hours)
- `docs/reference/PRODUCTION-DEPLOYMENT-GUIDE.md` - Deployment guide
- `docs/reference/ENVIRONMENT-VARIABLES-CHECKLIST.md` - Environment variables
- `docs/reference/SMOKE-TESTS-RUNBOOK.md` - Smoke tests runbook

---

## 📞 Yardım

Sorun yaşarsanız:

1. **Verification script çalıştır**: `bash scripts/pre_deployment_check.sh`
2. **Status report kontrol et**: `docs/active/PRE-DEPLOYMENT-STATUS.md`
3. **Reference guides incele**: `docs/reference/` klasörü
4. **Troubleshooting guide**: `docs/reference/TROUBLESHOOTING-GUIDE.md`

---

**Last Updated**: 2025-01-30  
**Status**: ✅ **Checklist Hazır** - Production'da execution bekliyor

