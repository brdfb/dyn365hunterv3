# Partner Center Production GO/NO-GO Checklist

**Date**: 2025-01-30  
**Last Updated**: 2025-11-26  
**Status**: Active  
**Purpose**: Production'a geçmeden önce son kontrol listesi

---

## 🎯 Genel Bakış

Partner Center entegrasyonu **DEV ortamında test edildi ve çalışıyor**. Production'a geçmeden önce bu checklist'i tamamlayın.

**Test Durumu**:
- ✅ FAZ 0: Ortam ve Migration - PASSED
- ✅ FAZ 1: Feature Flag OFF - PASSED
- ✅ FAZ 2: Token Cache - PASSED
- ✅ FAZ 3: Feature Flag ON - PASSED
- ✅ Phase 7: Production Enablement - COMPLETED (2025-01-30)
  - ✅ Feature Flag Validation
  - ✅ Logging Review (PII-free, JSON-safe)
  - ✅ Metrics Exposure (`/healthz/metrics` endpoint)
  - ✅ Background Sync Enablement (Celery Beat schedule)
  - ✅ Production Checklist Entry

---

## ✅ Production Readiness Status

**Phase 7: Production Enablement - ✅ COMPLETED** (2025-01-30)

- [x] **Feature Flag Validation** - Flag OFF/ON behavior tested and verified
- [x] **Logging Review** - All logs are PII-free (using `mask_pii()`) and JSON-safe
- [x] **Metrics Exposure** - Partner Center metrics added to `/healthz/metrics` endpoint
- [x] **Background Sync Enablement** - Celery Beat schedule respects feature flag (skips when OFF)
- [x] **Production Checklist Entry** - This document updated with Phase 7 completion status

**Status**: ✅ **READY FOR PRODUCTION** (after completing Pre-Production Checklist below)

---

## 🔒 CRITICAL: Security Pre-Check (MUST DO BEFORE PUSH)

### ⚠️ Secret Rotation (MANDATORY)

**GitHub push protection hatası nedeniyle secret rotation şart:**

1. **Azure Portal → Entra ID → App registrations**
   - İlgili uygulamayı bul (Client ID: `1475ed28-175a-45f1-a299-e811147ad068`)
   - **Certificates & secrets** sekmesine git

2. **Yeni secret oluştur:**
   - "New client secret" → Açıklama ekle → Expire date seç
   - **Yeni secret değerini kopyala** (sadece bir kere gösterilir!)

3. **Eski secret'ı öldür:**
   - Eski secret'ı **Delete** et veya **Expire** et
   - ⚠️ **CRITICAL**: Eski secret artık geçersiz olmalı

4. **Config'leri güncelle:**
   - `.env` dosyasında yeni secret'ı kullan
   - KeyVault varsa orada da güncelle
   - Production environment variables'ı güncelle

5. **GitHub'da allow et:**
   - URL: `https://github.com/brdfb/dyn365hunterv3/security/secret-scanning/unblock-secret/3621gBQv7eoyvyPdOacIVgvf53V`
   - "Allow secret" seçeneğini kullan
   - ⚠️ **Not**: Secret zaten rotate edildi, eski secret artık geçersiz

6. **Push'u tamamla:**
   ```bash
   git push origin feature/partner-center-phase1
   ```

**Efor**: XS/S (10-20 dk)  
**Status**: ⚠️ **MANDATORY** - Production'a geçmeden önce mutlaka yapılmalı

---

## ✅ Pre-Production Checklist

### 1. Volume Mount Kontrolü

**Docker Compose / Kubernetes:**

- [ ] `docker-compose.yml` veya Kubernetes deployment'ta token cache volume mount tanımlı mı?
- [ ] Volume path doğru mu? (`./token_cache:/app/.token_cache` veya prod path)
- [ ] Volume permissions doğru mu? (container yazabilmeli)

**Kontrol Komutu:**
```bash
# Docker Compose
grep -A 10 "volumes:" docker-compose.yml | grep token_cache

# Kubernetes
kubectl describe deployment <deployment-name> | grep -i volume
```

---

### 2. Environment Variables Kontrolü

**Production `.env` veya Config:**

- [ ] `HUNTER_PARTNER_CENTER_ENABLED=true` (production'da açılacak)
- [ ] `HUNTER_PARTNER_CENTER_CLIENT_ID` → DEV ile aynı mı?
- [ ] `HUNTER_PARTNER_CENTER_CLIENT_SECRET` → **YENİ ROTATE EDİLMİŞ SECRET** (eski secret değil!)
- [ ] `HUNTER_PARTNER_CENTER_TENANT_ID` → DEV ile aynı mı?
- [ ] `HUNTER_PARTNER_CENTER_API_URL` → Doğru mu? (`https://api.partner.microsoft.com`)
- [ ] `HUNTER_PARTNER_CENTER_SCOPE` → Doğru mu? (default: `https://api.partner.microsoft.com/.default`)
- [ ] `HUNTER_PARTNER_CENTER_SYNC_INTERVAL` → Production için uygun mu? (default: 600 = 10 dakika)

**Kontrol Komutu:**
```bash
# Production ortamında
grep PARTNER_CENTER .env | grep -v "^#"
```

---

### 3. Initial Authentication (Device Code Flow)

**Production'da 1 kere çalıştırılmalı:**

- [ ] Production container'ına bağlan
- [ ] Device Code Flow script'ini çalıştır veya Python REPL'de MSAL kodu çalıştır
- [ ] Browser'da login + consent tamamla
- [ ] Token cache oluşturuldu mu kontrol et

**Komut:**
```bash
# Production container'a bağlan
docker-compose exec api python

# Python shell'de:
from msal import PublicClientApplication
from app.config import settings

authority = f'https://login.microsoftonline.com/{settings.partner_center_tenant_id}'
app = PublicClientApplication(
    client_id=settings.partner_center_client_id,
    authority=authority,
)

flow = app.initiate_device_flow(scopes=[settings.partner_center_scope])
print(f'URL: {flow["verification_uri"]}')
print(f'Code: {flow["user_code"]}')

# Browser'da login yap, sonra:
result = app.acquire_token_by_device_flow(flow)

if 'access_token' in result:
    print('✅ Token acquired!')
    accounts = app.get_accounts()
    if accounts:
        print(f'✅ Account cached: {accounts[0].get("username")}')
```

**Kontrol:**
```bash
# Token cache var mı?
docker-compose exec api ls -la .token_cache
```

---

### 4. Smoke Tests (Production)

**Feature Flag ON yaptıktan sonra:**

- [ ] Health check: `/healthz` → `partner_center_enabled: true`
- [ ] API endpoint: `POST /api/referrals/sync` → `200` + `enqueued: true`
- [ ] Worker log: 401/403 yok, sadece iş mantığı logları
- [ ] Task çalışıyor: Celery task başarıyla çalıştı mı?

**Test Komutları:**
```bash
# 1. Health check
curl https://<prod-url>/healthz | jq '.partner_center_enabled'
# Beklenen: true

# 2. API endpoint
curl -X POST https://<prod-url>/api/referrals/sync \
  -H "Content-Type: application/json"
# Beklenen: 200 + {"enqueued": true, "task_id": "..."}

# 3. Worker log kontrolü
docker-compose logs worker | grep -i "partner.*center" | tail -20
# Beklenen: "partner_center_sync_task_started", "referrals_fetched" vb.
# Olmaması gereken: 401, 403, "token acquisition failed"
```

---

## 🚦 GO/NO-GO Kararı

### ✅ GO (Tüm checklist geçti)

**Kriterler:**
- ✅ Volume mount tanımlı ve çalışıyor
- ✅ Environment variables doğru
- ✅ Device Code Flow tamamlandı, token cache oluşturuldu
- ✅ Smoke tests geçti (health check, API endpoint, worker log)

**Aksiyon:**
- Production'da `HUNTER_PARTNER_CENTER_ENABLED=true` yap
- Celery Beat schedule aktif (10 dakikada bir sync)
- Logları izle (ilk 24 saat)

---

### ❌ NO-GO (Bir veya daha fazla item fail)

**Yaygın Sorunlar:**

1. **Token cache yok:**
   - Device Code Flow tamamlanmamış
   - Volume mount yanlış veya eksik
   - **Çözüm**: Device Code Flow'u tekrar çalıştır, volume mount'u kontrol et

2. **401/403 hatası:**
   - Azure AD permissions eksik
   - Admin consent verilmemiş
   - **Çözüm**: Azure Portal'da App Registration permissions'ı kontrol et

3. **API endpoint 500:**
   - Token cache yok
   - Partner Center API credentials yanlış
   - **Çözüm**: Token cache'i kontrol et, credentials'ı doğrula

**Aksiyon:**
- Sorunları çöz
- Checklist'i tekrar çalıştır
- GO kriterleri sağlanana kadar production'a geçme

---

## 📊 Post-Deployment Monitoring

**İlk 24 saat:**

- [ ] Celery Beat schedule çalışıyor mu? (10 dakikada bir sync)
- [ ] Worker log'larında hata var mı?
- [ ] Token refresh çalışıyor mu? (silent acquisition)
- [ ] Referral'lar geliyor mu? (database'de `partner_center_referrals` tablosunu kontrol et)

**Kontrol Komutları:**
```bash
# Celery Beat schedule
docker-compose exec worker celery -A app.core.celery_app inspect scheduled

# Son sync log'ları
docker-compose logs worker | grep "partner_center_sync" | tail -20

# Database kontrolü
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "SELECT COUNT(*) FROM partner_center_referrals;"
```

---

## 🔧 Rollback Plan

**Sorun çıkarsa:**

1. **Feature flag'i kapat:**
   ```bash
   # .env
   HUNTER_PARTNER_CENTER_ENABLED=false
   
   # Restart
   docker-compose restart api worker
   ```

2. **Log'ları kontrol et:**
   ```bash
   docker-compose logs api worker | grep -i "partner.*center\|error" | tail -50
   ```

3. **Token cache'i temizle (gerekirse):**
   ```bash
   rm -rf token_cache/*
   ```

4. **Sorun çözüldükten sonra:**
   - Device Code Flow'u tekrar çalıştır
   - Checklist'i tekrar çalıştır
   - GO kriterleri sağlanınca tekrar ON yap

---

## 📝 Notlar

1. **Token Cache Kalıcılığı:**
   - Volume mount olmadan token cache container restart sonrası kaybolur
   - Production'da mutlaka volume mount kullan

2. **Device Code Flow:**
   - Sadece bir kere yapılır (initial authentication)
   - Sonrasında silent token acquisition kullanılır
   - Token expire olduğunda otomatik refresh edilir

3. **Sync Frequency:**
   - Production: 10 dakika (600 saniye) - `HUNTER_PARTNER_CENTER_SYNC_INTERVAL=600`
   - Development: 30-60 saniye (test için)

4. **Error Handling:**
   - Token acquisition başarısız olursa task skip edilir (crash etmez)
   - Log'larda `partner_center_token_acquisition_failed` görünür
   - Feature flag OFF ise task skip edilir

---

**Son Güncelleme**: 2025-01-30  
**Status**: ✅ Ready for Production (checklist tamamlandıktan sonra)

