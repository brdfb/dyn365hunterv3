# Partner Center Test Guide

**Date**: 2025-01-30  
**Status**: Active  
**Purpose**: Test Partner Center integration with feature flag ON/OFF

---

## 📋 Konfigürasyon Kontrolü

### ✅ Mevcut .env Konfigürasyonu

```bash
HUNTER_PARTNER_CENTER_ENABLED=true
HUNTER_PARTNER_CENTER_CLIENT_ID=1475ed28-175a-45f1-a299-e811147ad068
HUNTER_PARTNER_CENTER_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
HUNTER_PARTNER_CENTER_TENANT_ID=aa72d1fe-d762-49f7-b721-c7611d0a6934
HUNTER_PARTNER_CENTER_API_URL=https://api.partner.microsoft.com
HUNTER_PARTNER_CENTER_SYNC_INTERVAL=600
```

### ✅ Yeterli mi?

**Evet, yeterli!** Ancak şunları not edin:

1. **CLIENT_SECRET**: Kodda kullanılmıyor (PublicClientApplication kullanılıyor, Device Code Flow için gerekli değil)
   - Sorun değil, ileride ConfidentialClientApplication'a geçilirse kullanılabilir
   
2. **Optional değişkenler** (default değerler var):
   - `HUNTER_PARTNER_CENTER_SCOPE` → Default: `https://api.partner.microsoft.com/.default`
   - `HUNTER_PARTNER_CENTER_TOKEN_CACHE_PATH` → Default: `.token_cache`

3. **Eksik adımlar** (aktif etmek için):
   - ✅ Konfigürasyon: Tamam
   - ⚠️ Database migration: Çalıştırılmalı
   - ⚠️ Initial authentication: Device Code Flow ile token cache oluşturulmalı

---

## 🧪 Feature Flag OFF Durumunda Test

### Test 1: API Endpoint Test (Feature Flag OFF)

**Amaç**: Feature flag kapalıyken endpoint'in 400 döndüğünü doğrula

```bash
# 1. Feature flag'i kapat
# .env dosyasında:
HUNTER_PARTNER_CENTER_ENABLED=false

# 2. API container'ı restart et
docker-compose restart api

# 3. Endpoint'i test et
curl -X POST http://localhost:8000/api/referrals/sync \
  -H "Content-Type: application/json" \
  -v

# Beklenen sonuç:
# HTTP/1.1 400 Bad Request
# {
#   "detail": "Partner Center integration is disabled. Enable feature flag to use this endpoint."
# }
```

**✅ Başarı kriteri**: 400 Bad Request + açıklayıcı hata mesajı

---

### Test 2: Celery Task Test (Feature Flag OFF)

**Amaç**: Feature flag kapalıyken Celery task'ın skip edildiğini doğrula

```bash
# 1. Feature flag'i kapat
HUNTER_PARTNER_CENTER_ENABLED=false
docker-compose restart api worker

# 2. Celery task'ı manuel çalıştır
docker-compose exec worker celery -A app.core.celery_app call app.core.tasks.sync_partner_center_referrals_task

# Beklenen sonuç:
# {
#   "status": "skipped",
#   "reason": "Feature flag disabled",
#   "success_count": 0,
#   "failure_count": 0,
#   "skipped_count": 0
# }
```

**Alternatif**: Python ile test

```python
from app.core.tasks import sync_partner_center_referrals_task
from app.config import settings

# Feature flag'i kapat (test için)
settings.partner_center_enabled = False

# Task'ı çalıştır
result = sync_partner_center_referrals_task.apply().get()
print(result)
# Beklenen: {"status": "skipped", "reason": "Feature flag disabled", ...}
```

**✅ Başarı kriteri**: Task skip edildi, hata yok, structured log'da "feature_flag_disabled" görünüyor

---

### Test 3: PartnerCenterClient Initialization Test (Feature Flag OFF)

**Amaç**: Feature flag kapalıyken client'ın initialize olmadığını doğrula

```python
from app.core.partner_center import PartnerCenterClient
from app.config import settings

# Feature flag'i kapat
settings.partner_center_enabled = False

# Client'ı initialize etmeye çalış
try:
    client = PartnerCenterClient()
    print("ERROR: Client initialized when it shouldn't!")
except ValueError as e:
    print(f"✅ Expected error: {e}")
    # Beklenen: "Partner Center integration is disabled (feature flag off)"
```

**✅ Başarı kriteri**: ValueError raise edildi, açıklayıcı mesaj

---

### Test 4: Log Kontrolü (Feature Flag OFF)

**Amaç**: Log'larda feature flag durumunun göründüğünü doğrula

```bash
# Worker log'larını kontrol et
docker-compose logs worker | grep -i "partner.*center\|feature.*flag"

# Beklenen log mesajları:
# - "partner_center_sync_skipped" with "reason": "feature_flag_disabled"
# - "feature_flag_state": false
```

**✅ Başarı kriteri**: Structured log'da feature flag durumu görünüyor

---

## 🧪 Feature Flag ON Durumunda Test

### Test 5: API Endpoint Test (Feature Flag ON)

**Amaç**: Feature flag açıkken endpoint'in çalıştığını doğrula

```bash
# 1. Feature flag'i aç
HUNTER_PARTNER_CENTER_ENABLED=true
docker-compose restart api

# 2. Endpoint'i test et
curl -X POST http://localhost:8000/api/referrals/sync \
  -H "Content-Type: application/json" \
  -v

# Beklenen sonuç (token cache yoksa):
# HTTP/1.1 500 Internal Server Error
# {
#   "detail": "Failed to start referral sync: Token acquisition failed. Run setup script to authenticate."
# }

# Beklenen sonuç (token cache varsa):
# HTTP/1.1 200 OK
# {
#   "success": true,
#   "message": "Referral sync task enqueued. Check logs for results.",
#   "enqueued": true,
#   "task_id": "...",
#   "success_count": 0,
#   "failure_count": 0,
#   "skipped_count": 0,
#   "errors": []
# }
```

**⚠️ Not**: İlk çalıştırmada token cache olmadığı için hata alabilirsiniz. Bu normal!

---

### Test 6: Health Check (Feature Flag Status)

**Amaç**: Health endpoint'inde feature flag durumunu kontrol et

```bash
# Health check endpoint'ini çağır
curl http://localhost:8000/healthz | jq '.'

# Şu anda partner_center_enabled field'ı yok
# İleride eklenebilir:
# {
#   "status": "ok",
#   "database": "connected",
#   "redis": "connected",
#   "environment": "development",
#   "enrichment_enabled": false,
#   "partner_center_enabled": true  # <-- Bu eklenebilir
# }
```

**Not**: Health endpoint'ine `partner_center_enabled` field'ı eklenmemiş. İsterseniz ekleyebiliriz.

---

## 🔧 Eksik Adımlar (Aktif Etmek İçin)

### 1. Database Migration

```bash
# Migration'ı çalıştır
docker-compose exec api alembic upgrade head

# Kontrol et
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "\d partner_center_referrals"
```

**Beklenen**: `partner_center_referrals` table'ı oluşturulmuş olmalı

---

### 2. Initial Authentication (Device Code Flow)

**Amaç**: İlk authentication yapıp token cache oluştur

```bash
# Setup script'i çalıştır (eğer varsa)
docker-compose exec api python -m scripts.sync_partner_center

# VEYA manuel olarak Python ile:
docker-compose exec api python
```

```python
# Python shell'de
from app.core.partner_center import PartnerCenterClient
from msal import PublicClientApplication
from app.config import settings

# MSAL app oluştur
app = PublicClientApplication(
    client_id=settings.partner_center_client_id,
    authority=f"https://login.microsoftonline.com/{settings.partner_center_tenant_id}"
)

# Device code flow başlat
flow = app.initiate_device_flow(scopes=[settings.partner_center_scope])
print(f"Go to {flow['verification_uri']} and enter code: {flow['user_code']}")

# Kullanıcı login yaptıktan sonra
result = app.acquire_token_by_device_flow(flow)
if "access_token" in result:
    print("✅ Token acquired successfully!")
    # Token cache otomatik olarak .token_cache'e kaydedilir
else:
    print(f"❌ Error: {result.get('error_description')}")
```

**⚠️ Önemli**: Bu adım sadece bir kere yapılır. Sonrasında background job'lar silent token acquisition kullanır.

---

## 📊 Test Sonuçları Template

```
Test 1: API Endpoint (Feature Flag OFF)
- Status: [ ] PASS [ ] FAIL
- Response Code: ______
- Error Message: ______

Test 2: Celery Task (Feature Flag OFF)
- Status: [ ] PASS [ ] FAIL
- Task Status: ______
- Log Message: ______

Test 3: Client Initialization (Feature Flag OFF)
- Status: [ ] PASS [ ] FAIL
- Error Type: ______

Test 4: Log Kontrolü (Feature Flag OFF)
- Status: [ ] PASS [ ] FAIL
- Log Found: [ ] YES [ ] NO

Test 5: API Endpoint (Feature Flag ON)
- Status: [ ] PASS [ ] FAIL
- Response Code: ______
- Task ID: ______

Test 6: Health Check
- Status: [ ] PASS [ ] FAIL
- Feature Flag Field: [ ] EXISTS [ ] MISSING

Overall Status: [ ] PASS [ ] FAIL
```

---

## 🚨 Troubleshooting

### Problem: API endpoint 500 döndürüyor

**Olası nedenler**:
1. Token cache yok (ilk çalıştırma)
2. Azure AD credentials yanlış
3. Partner Center API permissions eksik

**Çözüm**:
1. Initial authentication yap (Device Code Flow)
2. Azure AD App Registration'ı kontrol et
3. Partner Center API permissions'ı kontrol et

---

### Problem: Celery task skip ediliyor

**Olası nedenler**:
1. Feature flag kapalı
2. Environment variable yüklenmemiş

**Çözüm**:
1. `.env` dosyasını kontrol et
2. `docker-compose restart api worker` yap
3. `docker-compose exec api env | grep PARTNER_CENTER` ile kontrol et

---

## 📝 Notlar

1. **CLIENT_SECRET**: Kodda kullanılmıyor (PublicClientApplication), ama .env'de tutmakta sorun yok
2. **Token Cache**: `.token_cache` dosyası container içinde oluşturulur (volume mount gerekebilir)
3. **Feature Flag**: Production'da default OFF, güvenli
4. **Migration**: Sadece bir kere çalıştırılır, idempotent

---

**Son Güncelleme**: 2025-01-30

