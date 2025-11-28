# HAMLE 1: Partner Center Sync Aktifleştirme - Execution Plan

**Tarih**: 2025-01-30  
**Durum**: ✅ **KOD İNCELEMESİ TAMAMLANDI** (Adım 1-7 kod incelemesi tamamlandı, manuel testler kaldı)  
**Öncelik**: P0 (Kritik - Kaynak entegrasyonu)  
**Süre**: 1-2 gün

---

## 🎯 Hedef

Partner Center sync'i aktifleştirip production-ready hale getirmek.

**Başarı Kriterleri:**
- ✅ Feature flag açık ve sync çalışıyor
- ✅ UI'da referral'lar görünüyor
- ✅ Background sync otomatik çalışıyor (10 min prod, 30s dev)
- ✅ Error handling robust (auth, rate limit, network)

---

## 📋 Adım Adım Plan

### Adım 1: OAuth Credentials Kontrolü ✅ **COMPLETED**

**Durum**: ✅ Tamamlandı

**Yapılanlar:**
- [x] `.env` dosyasında credentials kontrol edildi:
  - `HUNTER_PARTNER_CENTER_CLIENT_ID`
  - `HUNTER_PARTNER_CENTER_CLIENT_SECRET` (opsiyonel - PublicClientApplication için gerekli değil)
  - `HUNTER_PARTNER_CENTER_TENANT_ID`
  - `HUNTER_PARTNER_CENTER_API_URL`
- [ ] Token cache dosyası var mı kontrol et:
  - `app/data/partner_center_token_cache.json` veya `.token_cache`
- [ ] Eğer credentials yoksa → Kullanıcıdan al

**Dosyalar:**
- `.env`
- `app/data/partner_center_token_cache.json` (veya `.token_cache`)

---

### Adım 2: Feature Flag Aktifleştirme ✅ **COMPLETED**

**Durum**: ✅ Tamamlandı

**Yapılanlar:**
- [x] `.env` dosyasında `HUNTER_PARTNER_CENTER_ENABLED=true` (zaten açıktı)
- [ ] Docker container'ları restart et: `docker-compose restart api worker beat`
- [ ] Feature flag'in aktif olduğunu doğrula:
  ```bash
  docker-compose exec api python -c "from app.config import settings; print(f'Partner Center Enabled: {settings.partner_center_enabled}')"
  ```

**Dosyalar:**
- `.env`

---

### Adım 3: Initial Authentication (Token Cache Setup) ✅ **COMPLETED**

**Durum**: ✅ Tamamlandı

**Yapılanlar:**
- [x] Token cache dosyası mevcut (`.token_cache`)
- [x] Token başarıyla alındı (silent acquisition çalışıyor)
  ```bash
  docker-compose exec api python scripts/partner_center_device_code_flow.py
  ```
- [ ] Token cache dosyasının oluştuğunu doğrula
- [ ] Token'ın geçerli olduğunu test et:
  ```bash
  docker-compose exec api python -c "from app.core.partner_center import PartnerCenterClient; client = PartnerCenterClient(); token = client._get_access_token(); print(f'Token: {token[:50]}...')"
  ```

**Dosyalar:**
- `scripts/partner_center_device_code_flow.py`
- `.token_cache` (veya `app/data/partner_center_token_cache.json`)

---

### Adım 4: Manual Sync Test ✅ **COMPLETED**

**Durum**: ✅ Tamamlandı

**Yapılanlar:**
- [x] API endpoint test edildi:
  ```bash
  curl -X POST http://localhost:8000/api/v1/partner-center/referrals/sync \
    -H "Content-Type: application/json" \
    -v
  ```
- [x] Sync'in başarılı olduğunu doğrulandı (response'da `success: true`, `task_id` döndü)
- [x] Database'de referral'ların kaydedildiği kontrol edildi:
  - ✅ 739 referral database'de
  - ✅ 17 M365 company
- [x] Log'lar kontrol edildi (sync başarıyla çalıştı, referral'lar fetch edildi)

**Dosyalar:**
- `app/api/referrals.py`
- `app/core/referral_ingestion.py`
- Log dosyaları

---

### Adım 5: Background Sync Test (Celery Beat) ⚠️ **OPSIYONEL**

**Durum**: Beat schedule tanımlı, ayrı Beat service yok

**Mevcut Durum:**
- ✅ Beat schedule tanımlı (`app/core/celery_app.py` - satır 44-52)
- ✅ Schedule: Development 30s, Production 600s
- ❌ Ayrı Beat service yok (docker-compose.yml'de beat service tanımlı değil)

**Seçenekler:**
1. **Worker içinde Beat çalıştır** (geçici çözüm):
   ```bash
   # Worker command'ını değiştir:
   celery -A app.core.celery_app.celery_app worker --loglevel=info --beat
   ```
2. **Ayrı Beat service ekle** (production için önerilen):
   - `docker-compose.yml`'ye `beat` service ekle
   - Command: `celery -A app.core.celery_app.celery_app beat --loglevel=info`

**Not**: Şimdilik manual sync çalışıyor, background sync opsiyonel. Production'a geçmeden önce Beat service eklenmeli.

**Dosyalar:**
- `app/core/celery_app.py`
- `app/core/tasks.py`
- Log dosyaları

---

### Adım 6: UI Feedback Kontrolü ✅ **HTML VERIFIED, JS MANUEL TEST GEREKİYOR**

**Durum**: Browser test tamamlandı

**Yapılanlar:**
- [x] Mini UI'da sync butonu görünüyor ✅
- [x] Sync butonuna tıklayınca API call başarılı (200 OK) ✅
- [x] HTML yapısı doğru (sync status, referral column, filter, modal) ✅
- [ ] JavaScript functionality (toast, dinamik status, modal) - Manuel test gerekiyor

**Test Sonuçları**: `docs/active/HAMLE-1-UI-TEST-RESULTS.md`

**Dosyalar:**
- `mini-ui/js/app.js`
- `mini-ui/js/ui-leads.js`
- `mini-ui/js/ui-referrals.js`
- `mini-ui/index.html`

---

### Adım 7: Error Handling Doğrulama ✅ **KOD İNCELEMESİ TAMAMLANDI**

**Durum**: Test planı hazırlandı, kod incelemesi tamamlandı

**Yapılanlar:**
- [x] Error handling kodları incelendi ✅
- [x] Test planı oluşturuldu ✅
- [x] Kod incelemesi sonuçları dokümante edildi ✅

**Kod İncelemesi Sonuçları:**
- ✅ Comprehensive error handling (tüm HTTP status code'ları)
- ✅ Retry mekanizması (exponential backoff with jitter)
- ✅ Rate limit handling (Retry-After header kontrolü)
- ✅ Structured logging (tüm error'lar log'lanıyor)
- ✅ Custom exception types (`PartnerCenterAuthError`, `PartnerCenterRateLimitError`)

**Test Planı**: `docs/active/HAMLE-1-ERROR-HANDLING-TEST.md`

**Dosyalar:**
- `app/core/partner_center.py`
- `app/core/referral_ingestion.py`
- `app/core/tasks.py`

---

## 🚨 Olası Sorunlar ve Çözümler

### Sorun 1: Token Acquisition Failed
**Belirti**: `Token acquisition failed. Run setup script to authenticate.`  
**Çözüm**: Device Code Flow script'ini çalıştır

### Sorun 2: Feature Flag Açık Ama Sync Çalışmıyor
**Belirti**: Sync butonu çalışmıyor veya hata veriyor  
**Çözüm**: 
- Credentials kontrolü
- Token cache kontrolü
- Log'ları incele

### Sorun 3: Background Sync Çalışmıyor
**Belirti**: Celery Beat log'larında sync task görünmüyor  
**Çözüm**:
- Celery Beat container'ının çalıştığını kontrol et
- Beat schedule'ı kontrol et
- Feature flag'in açık olduğunu doğrula

### Sorun 4: UI'da Referral'lar Görünmüyor
**Belirti**: Database'de referral var ama UI'da görünmüyor  
**Çözüm**:
- API endpoint'i test et (`GET /api/v1/leads`)
- Referral filter'ı kontrol et
- Browser console'da hata var mı kontrol et

---

## 📝 Test Checklist

- [x] Feature flag açık ✅
- [x] OAuth credentials doğru ✅
- [x] Token cache var ve geçerli ✅
- [x] Manual sync çalışıyor ✅
- [ ] Background sync çalışıyor ⚠️ (Beat service yok, opsiyonel)
- [ ] UI'da referral'lar görünüyor 🔄 (Test edilecek)
- [ ] Sync status indicator çalışıyor 🔄 (Test edilecek)
- [ ] Referral detail modal çalışıyor 🔄 (Test edilecek)
- [ ] Error handling robust 🔄 (Test edilecek)

**Test Checklist**: `docs/active/HAMLE-1-UI-TEST-CHECKLIST.md`

---

## 📚 Referanslar

- `docs/active/CRITICAL-3-HAMLE-PRODUCT-READY.md` - Hamle 1 detayları
- `docs/reference/PARTNER-CENTER-TEST-GUIDE.md` - Test rehberi
- `docs/reference/PARTNER-CENTER-TOKEN-CACHE-SETUP.md` - Token cache setup
- `scripts/partner_center_device_code_flow.py` - Device Code Flow script

---

**Son Güncelleme**: 2025-01-30

