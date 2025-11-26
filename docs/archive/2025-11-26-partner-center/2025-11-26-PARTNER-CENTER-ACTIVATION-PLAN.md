# Partner Center Activation Plan - 3 Fazlı Doğrulama

**Date**: 2025-01-30  
**Status**: Active  
**Purpose**: Partner Center'ı production'a dağıtmadan önce 3 fazlı doğrulama

---

## 🎯 Genel Bakış

**3 Faz:**
1. **FAZ 0** - Ortam ve migration (zemin hazırlığı)
2. **FAZ 1** - Feature flag OFF doğrulama (kapalıyken güvenli mi?)
3. **FAZ 2** - Aktivasyon (ilk auth + token cache)
4. **FAZ 3** - Feature flag ON doğrulama (açınca çalışıyor mu?)

**Karar Kriteri**: Tüm fazlar PASS → ON yapılabilir

---

## 🔹 FAZ 0 – Ortam ve Migration

**Amaç:** Zemin temiz mi, tablo var mı?

### 1. Doğru Ortamda mısın? (DEV / LOCAL)

```bash
# .env dosyasını kontrol et
cat .env | grep PARTNER_CENTER

# Beklenen: Tüm değişkenler dolu
# - HUNTER_PARTNER_CENTER_ENABLED
# - HUNTER_PARTNER_CENTER_CLIENT_ID
# - HUNTER_PARTNER_CENTER_TENANT_ID
# - HUNTER_PARTNER_CENTER_API_URL
```

✅ **Kontrol**: Tüm değişkenler dolu mu?

---

### 2. DB Migration Çalıştır

```bash
docker-compose exec api alembic upgrade head
```

✅ **Kontrol**: Migration başarılı mı? (hata yok mu?)

---

### 3. Tabloyu Kontrol Et (Opsiyonel)

```bash
docker-compose exec postgres \
  psql -U dyn365hunter -d dyn365hunter -c "\d partner_center_referrals"
```

✅ **Kontrol**: Tablo görünüyor mu?

**Beklenen çıktı:**
```
                                    Table "public.partner_center_referrals"
      Column      |            Type             | Collation | Nullable | Default
------------------+-----------------------------+-----------+----------+---------
 referral_id      | character varying(255)     |           | not null |
 referral_type    | character varying(50)       |           |          |
 domain           | character varying(255)     |           |          |
 ...
```

❌ **Hata alırsan** → Önce bunu çöz, diğerlerine geçme.

---

👉 **FAZ 0 PASS Kriteri:**
- ✅ Ortam değişkenleri dolu
- ✅ Migration başarılı
- ✅ Tablo görünüyor

**Buraya kadar sorun yoksa FAZ 1'e geç.**

---

## 🔹 FAZ 1 – Feature Flag OFF Doğrulama

**Amaç:** "Kapalıyken hiçbir şey yapmıyor, sadece kibarca reddediyor" mu?

### 1. Flag'i Kapat + Restart

```bash
# .env dosyasında
HUNTER_PARTNER_CENTER_ENABLED=false

# Restart
docker-compose restart api worker
```

---

### 2. Health Check

```bash
curl http://localhost:8000/healthz | jq '.partner_center_enabled'

# Beklenen: false
```

✅ **Kontrol**: `false` dönüyor mu?

---

### 3. API Endpoint Testi (OFF)

```bash
curl -X POST http://localhost:8000/api/referrals/sync \
  -H "Content-Type: application/json" -v
```

✅ **Beklenen:**
- HTTP Status: `400 Bad Request`
- Body: `"Partner Center integration is disabled. Enable feature flag to use this endpoint."`

❌ **Yanlış ise**: 200 dönüyorsa veya farklı hata → OFF path'i düzelt.

---

### 4. Celery Task Testi (OFF)

```bash
docker-compose exec worker \
  celery -A app.core.celery_app call app.core.tasks.sync_partner_center_referrals_task
```

✅ **Beklenen JSON:**
```json
{
  "status": "skipped",
  "reason": "Feature flag disabled",
  "success_count": 0,
  "failure_count": 0,
  "skipped_count": 0
}
```

❌ **Yanlış ise**: Task çalışıyorsa veya farklı hata → OFF path'i düzelt.

---

### 5. Log Kontrolü

```bash
docker-compose logs worker | grep -i "partner.*center\|feature.*flag" | tail -20
```

✅ **Beklenen log mesajları:**
- `partner_center_sync_skipped`
- `feature_flag_disabled` veya `reason="feature_flag_disabled"`
- `feature_flag_state": false`

❌ **Yanlış ise**: Log'da "sync started" veya "enabled" görünüyorsa → OFF path'i düzelt.

---

👉 **FAZ 1 PASS Kriteri:**
- ✅ Health: `false`
- ✅ API: 400 + düzgün hata mesajı
- ✅ Task: `status="skipped"` + `reason="Feature flag disabled"`
- ✅ Log: "skip/feature_flag_disabled" görünüyor

**Bunların biri bile yanlışsa flag'i ON'a çevirmeyi düşünme, önce OFF path'i düzelt.**

---

## 🔹 FAZ 2 – Aktivasyon (İlk Auth + Token Cache)

**Amaç:** "Bir kere login ol, ondan sonra sessiz çalışsın."

### 1. Device Code Flow ile İlk Login

> Bunu **api container içinde** yap.

```bash
docker-compose exec api python
```

Python shell'de:

```python
from msal import PublicClientApplication
from app.config import settings

# MSAL app oluştur
app = PublicClientApplication(
    client_id=settings.partner_center_client_id,
    authority=f"https://login.microsoftonline.com/{settings.partner_center_tenant_id}"
)

# Device code flow başlat
flow = app.initiate_device_flow(scopes=[settings.partner_center_scope])

# Kullanıcıya göster
print("\n" + "="*60)
print("Device Code Flow - Login Instructions")
print("="*60)
print(f"\n1. Go to: {flow['verification_uri']}")
print(f"2. Enter code: {flow['user_code']}")
print("\nWaiting for authentication...")
print("="*60 + "\n")

# Login bekleniyor (kullanıcı browser'da login yapacak)
result = app.acquire_token_by_device_flow(flow)

# Sonuç kontrolü
if "access_token" in result:
    print("✅ SUCCESS: Token acquired!")
    print(f"   Token expires in: {result.get('expires_in', 'N/A')} seconds")
    print(f"   Token cache saved to: .token_cache")
else:
    print("❌ ERROR: Token acquisition failed")
    print(f"   Error: {result.get('error', 'Unknown')}")
    print(f"   Description: {result.get('error_description', 'N/A')}")
```

**Adımlar:**
1. Script çıktısındaki URL'ye git
2. Verilen kodu gir
3. Login/consent ver (MFA dahil)
4. Python shell'de token gelene kadar bekle

✅ **Kontrol**: `✅ SUCCESS: Token acquired!` görünüyor mu?

---

### 2. Cache Gerçekten Çalışıyor mu? (Opsiyonel ama İyi Olur)

Python shell'de (aynı session):

```python
from app.core.partner_center import PartnerCenterClient

# Client'ı initialize et (feature flag OFF olsa bile test için)
# Not: Feature flag OFF ise ValueError alırsın, bu normal
# Bu test için feature flag'i geçici olarak açabilirsin veya
# direkt MSAL ile test edebilirsin

# Alternatif: Direkt MSAL ile silent acquisition test
accounts = app.get_accounts()
if accounts:
    account = accounts[0]
    result = app.acquire_token_silent(
        scopes=[settings.partner_center_scope],
        account=account
    )
    if result and "access_token" in result:
        print("✅ SUCCESS: Silent token acquisition works!")
        print(f"   Token: {result['access_token'][:20]}...")
    else:
        print("❌ ERROR: Silent token acquisition failed")
        print(f"   Error: {result.get('error', 'Unknown')}")
else:
    print("❌ ERROR: No accounts found in cache")
```

✅ **Kontrol**: Silent acquisition çalışıyor mu?

---

### 3. Token Cache Dosyası Kontrolü (Opsiyonel)

```bash
# Container içinde token cache dosyasını kontrol et
docker-compose exec api ls -la .token_cache 2>/dev/null || echo "Token cache not found"

# Veya Python ile
docker-compose exec api python -c "import os; print('Token cache exists:', os.path.exists('.token_cache'))"
```

✅ **Kontrol**: Token cache dosyası oluşmuş mu?

---

👉 **FAZ 2 PASS Kriteri:**
- ✅ Device Code Flow ile login başarılı
- ✅ `.token_cache` dosyası oluşmuş (container içinde)
- ✅ Silent token acquisition çalışıyor (opsiyonel ama önerilir)

**Biri patlıyorsa → flag'i asla ON yapma, önce auth sorununu çöz.**

---

## 🔹 FAZ 3 – Feature Flag ON Doğrulama

**Amaç:** "Açınca crash mi ediyor, düzgün task mı enqueue ediyor?"

### 1. Flag'i Aç + Restart

```bash
# .env dosyasında
HUNTER_PARTNER_CENTER_ENABLED=true

# Restart
docker-compose restart api worker
```

---

### 2. Health Check (ON)

```bash
curl http://localhost:8000/healthz | jq '.partner_center_enabled'

# Beklenen: true
```

✅ **Kontrol**: `true` dönüyor mu?

---

### 3. API Endpoint Testi (ON)

```bash
curl -X POST http://localhost:8000/api/referrals/sync \
  -H "Content-Type: application/json" -v
```

**Token cache DOĞRU ise beklenen:**
- HTTP Status: `200 OK`
- Body:
```json
{
  "success": true,
  "message": "Referral sync task enqueued. Check logs for results.",
  "enqueued": true,
  "task_id": "...",
  "success_count": 0,
  "failure_count": 0,
  "skipped_count": 0,
  "errors": []
}
```

**Token cache YOK / bozuk ise:**
- HTTP Status: `500 Internal Server Error`
- Body: `"Failed to start referral sync: Token acquisition failed. Run setup script to authenticate."`

→ Bu durumda **FAZ 2 başarısızdır; geri dön.**

✅ **Kontrol**: 200 + task_id dolu mu?

---

### 4. Worker Log Kontrolü

```bash
docker-compose logs worker | grep -i "partner.*center\|referral" | tail -50
```

✅ **Beklenen log mesajları:**
- `partner_center_sync_task_started`
- `partner_center_sync_started`
- `partner_center_fetching_referrals`
- `partner_center_referrals_fetched` (referral varsa)
- Exception yok (ya da sadece "no referrals" gibi soft durumlar)

❌ **Yanlış ise**: Crash ediyorsa veya exception görünüyorsa → ON path'i düzelt.

---

### 5. Task Status Kontrolü (Opsiyonel)

```bash
# Task ID'yi al (API response'dan)
TASK_ID="<task_id_from_api_response>"

# Task status'unu kontrol et
docker-compose exec worker celery -A app.core.celery_app inspect task $TASK_ID
```

✅ **Kontrol**: Task başarıyla çalıştı mı?

---

👉 **FAZ 3 PASS Kriteri:**
- ✅ Health: `true`
- ✅ API: 200 + "task enqueued" + task_id dolu
- ✅ Worker log: Task çalışıyor, exception yok (ya da sadece "no referrals" gibi soft durumlar)

**Şu an gerçek referral gelmese bile önemli olan crash etmemesi, düzgün request atıp düzgün loglaması.**

---

## 🔚 ON'a Çekme Kararı (Karar Matrisi)

**ON yap / bırak** diyebileceğin senaryo:

### ✅ Tüm Fazlar PASS

- ✅ **FAZ 0**: Ortam + migration temiz
- ✅ **FAZ 1**: OFF path tamamen temiz
- ✅ **FAZ 2**: Auth + token cache sorunsuz
- ✅ **FAZ 3**: ON path 200 dönüyor, worker log'ları crash etmiyor

### Ortam Bazlı Karar

**DEV ortamı için:**
- ✅ Flag **rahatlıkla ON kalabilir**
- ✅ Gerçek referral'ları test edebilirsin
- ✅ Background sync çalışıyor (10 dakikada bir)

**STAGING ortamı için:**
- ✅ Flag ON yapılabilir
- ✅ Production'a geçmeden önce son testler
- ✅ Gerçek Partner Center API ile test

**PROD için:**
- ⚠️ **Dikkatli karar ver:**
  - Eğer şu an gerçekten Partner Center referrals'ı işlemek istiyorsan → **ON**
  - "Daha sadece deniyorum, production'da kullanmayacağım" diyorsan → **PROD'da OFF bırak**, sadece DEV/TEST'te ON tut

---

## 📊 Test Sonuçları Template

```
FAZ 0 - Ortam ve Migration
- [ ] Ortam değişkenleri dolu
- [ ] Migration başarılı
- [ ] Tablo görünüyor
- Status: [ ] PASS [ ] FAIL

FAZ 1 - Feature Flag OFF Doğrulama
- [ ] Health: false
- [ ] API: 400 + düzgün hata
- [ ] Task: status="skipped"
- [ ] Log: "skip/feature_flag_disabled" görünüyor
- Status: [ ] PASS [ ] FAIL

FAZ 2 - Aktivasyon (İlk Auth + Token Cache)
- [ ] Device Code Flow başarılı
- [ ] Token cache oluşmuş
- [ ] Silent token acquisition çalışıyor
- Status: [ ] PASS [ ] FAIL

FAZ 3 - Feature Flag ON Doğrulama
- [ ] Health: true
- [ ] API: 200 + task enqueued
- [ ] Worker log: Task çalışıyor, exception yok
- Status: [ ] PASS [ ] FAIL

Overall Status: [ ] PASS [ ] FAIL
ON Yapılabilir: [ ] YES [ ] NO
```

---

## 🚨 Troubleshooting

### FAZ 1 Başarısız

**Problem**: OFF path'i çalışmıyor
- API 200 dönüyor → Feature flag check'i çalışmıyor
- Task çalışıyor → Celery task'ta feature flag check'i çalışmıyor
- Log'da "enabled" görünüyor → Logging yanlış

**Çözüm**: Feature flag check'lerini kontrol et (`app/api/referrals.py`, `app/core/tasks.py`)

---

### FAZ 2 Başarısız

**Problem**: Token acquisition başarısız
- Device Code Flow hata veriyor → Azure AD credentials yanlış
- Silent acquisition çalışmıyor → Token cache oluşmamış

**Çözüm**: 
1. Azure AD App Registration'ı kontrol et
2. Partner Center API permissions'ı kontrol et
3. Device Code Flow'u tekrar çalıştır

---

### FAZ 3 Başarısız

**Problem**: ON path'i crash ediyor
- API 500 dönüyor → Token cache yok veya bozuk
- Worker exception veriyor → Partner Center API'ye erişemiyor

**Çözüm**:
1. Token cache'i kontrol et (FAZ 2'ye geri dön)
2. Partner Center API credentials'ı kontrol et
3. Network connectivity kontrol et

---

**Son Güncelleme**: 2025-01-30

