# Sales Fresh Reset Guide

**Tarih**: 2025-01-30  
**Versiyon**: v1.0.0  
**Status**: ✅ **Active** - UAT Round için hazır

---

## 📋 Genel Bakış

Sales Fresh Reset sistemi, **tam sıfırlanmış demo ortamı** yaratmak için tasarlanmıştır. UAT Round öncesi veya demo senaryoları için kullanılır.

**Scripts:**
- `scripts/sales_fresh_reset.sh` - Tam reset (DB + Redis + health check)
- `scripts/sales_health_check.sh` - Sistem sağlık kontrolü (API/DB/Redis)
- `scripts/check_env_completeness.sh` - Environment variables kontrolü

---

## 🚀 Kullanım Senaryosu: UAT

**Tam sıfırlanmış demo ortamı yaratmak için adım adım:**

### 1. Reset Script

```bash
bash scripts/sales_fresh_reset.sh
```

**Ne yapar:**
- Veritabanını tamamen temizler (Alembic migrations ile)
- Redis cache'i temizler
- Tüm servisleri kontrol eder (Docker, API, DB, Redis)
- Health check yapar
- Feature flag durumlarını gösterir

**Güvenlik:**
- Production database reset'leri engellenir (FORCE_PRODUCTION_RESET=yes gerekir)
- DATABASE_URL'de `prod|production` kontrolü yapılır

### 2. Health Check

```bash
bash scripts/sales_health_check.sh
```

**Ne yapar:**
- API sağlık kontrolü (`/healthz/ready`)
- Database bağlantı kontrolü
- Redis bağlantı kontrolü
- Tüm servislerin durumunu raporlar

### 3. Env Check

```bash
bash scripts/check_env_completeness.sh
```

**Ne yapar:**
- Zorunlu environment variables kontrolü
- Opsiyonel variables kontrolü (Sentry, DB pool size, etc.)
- Feature flag'ler kontrolü (Partner Center, D365, Enrichment)
- Koşullu variables kontrolü (flag aktifse ilgili credentials)

**Not:** Partner Center & D365 flag'leri UAT'te aktifse, reset sonrası da aktif kalır.

### 4. UAT Branch'e Geç

```bash
# Baseline tag oluştur
git tag uat-2025-01-30-baseline -m "UAT baseline: Pre-UAT full reset state"
git push origin uat-2025-01-30-baseline

# UAT branch aç
git checkout -b bugfix/uat-2025-01-30
```

---

## 📊 Reset Sonrası Durum

**Sistem Durumu:**
- ✅ Veritabanı temiz ve hazır
- ✅ Redis cache temizlendi
- ✅ API çalışıyor ve sağlıklı
- ✅ Tüm servisler hazır

**Özellik Durumu:**
- ✅ Core özellikler aktif (Domain ingestion, scanning, scoring, lead management)
- ✅ Mini UI aktif (http://localhost:8000/mini-ui)
- ✅ P-Model aktif (Priority badges, commercial segment, technical heat)
- ✅ Sales Summary aktif (Intelligence layer)
- ⚠️ Feature flag özellikleri kontrol edildi (yukarıda gösterildi)

---

## 🔧 Env Checker Entegrasyonu

**Reset sonrası recommended step:**

```bash
bash scripts/check_env_completeness.sh
```

**Kontrol Edilenler:**

**Zorunlu:**
- `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `REDIS_URL`, `API_HOST`, `API_PORT`, `LOG_LEVEL`, `ENVIRONMENT`

**Opsiyonel (Önerilen):**
- `HUNTER_SENTRY_DSN`
- `HUNTER_DB_POOL_SIZE`
- `HUNTER_DB_MAX_OVERFLOW`

**Feature Flag'ler:**
- `HUNTER_PARTNER_CENTER_ENABLED` (default: false)
- `HUNTER_D365_ENABLED` (default: false)
- `HUNTER_ENRICHMENT_ENABLED` (default: false)

**Koşullu (Flag aktifse):**
- Partner Center: `HUNTER_PARTNER_CENTER_CLIENT_ID`, `HUNTER_PARTNER_CENTER_TENANT_ID`, `HUNTER_PARTNER_CENTER_API_URL`
- D365: `HUNTER_D365_BASE_URL`, `HUNTER_D365_CLIENT_ID`, `HUNTER_D365_CLIENT_SECRET`, `HUNTER_D365_TENANT_ID`
- IP Enrichment: `MAXMIND_CITY_DB`, `IP2LOCATION_DB`, `IP2PROXY_DB`

**Not:** Partner Center & D365 flag'leri UAT'te aktifse, reset sonrası da aktif kalır.

---

## 🎯 Sonraki Adımlar

**Reset sonrası:**

1. **Demo senaryosu çalıştır:**
   ```bash
   bash scripts/sales-demo.sh
   ```

2. **Manuel test:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/ingest/domain \
     -H 'Content-Type: application/json' \
     -d '{"domain": "example.com", "company_name": "Example Inc"}'
   ```

3. **API dokümantasyonu:**
   - http://localhost:8000/docs

4. **Mini UI:**
   - http://localhost:8000/mini-ui

---

## 📝 Güvenlik Notları

**Production Protection:**
- Production database reset'leri engellenir
- `FORCE_PRODUCTION_RESET=yes` flag'i gerekir (SADECE TEST/UAT)
- DATABASE_URL'de `prod|production` kontrolü yapılır

**Logging:**
- Script logları `./logs/scripts/` dizinine kaydedilir
- Logging'i devre dışı bırakmak için: `LOG_DIR=""`

---

## 🔗 İlgili Dokümanlar

- `docs/reference/SALES-RESET-SUMMARY.md` - Reset özeti
- `docs/reference/SALES-RESET-ANALYSIS.md` - Reset analizi
- `docs/archive/2025-01-28-GO-NO-GO-CHECKLIST-v1.0.md` - UAT Round ek adımları
- `docs/active/HUNTER-CONTEXT-PACK-v1.0.md` - Operational Standards / Deployment Checklist

---

**Last Updated**: 2025-01-30  
**Version**: v1.0.0  
**Status**: ✅ **Active** - UAT Round için hazır

