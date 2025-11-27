# Phase 2.9 — D365 Environment Wiring & Real E2E

**Tarih**: 2025-01-30  
**Durum**: Pending (D365 Tenant Hazır Olunca)  
**Öncelik**: P0 (Kritik - Production E2E)  
**Efor**: S-M (Small-Medium - ~0.5-1 gün, ops işi)

---

## 🎯 Hedef

D365 tenant hazır olduğunda, gerçek environment ile E2E test yapmak ve production'a hazır hale getirmek.

**Karar**: Bu faz, koddan bağımsız, tamamen environment/ops işi. UI (Phase 3) bu fazı beklemeden başlayabilir.

---

## 📋 Checklist

### Tenant'ta Yapılacaklar:

- [ ] **App Registration**:
  - Azure AD'de app registration oluşturuldu
  - Client ID, Client Secret, Tenant ID alındı
  - API permissions: `Dynamics CRM user_impersonation` (veya gerekli izinler)
  
- [ ] **Application User**:
  - D365'te Application User oluşturuldu
  - App registration ile bağlandı
  
- [ ] **Role + İzinler**:
  - Application User'a gerekli security role atandı (Lead create/update)
  - Custom hunter_* alanları için field-level security kontrol edildi
  
- [ ] **Custom hunter_* Alanları**:
  - `hunter_score` (decimal)
  - `hunter_segment` (text)
  - `hunter_priority` (text)
  - `hunter_technical_heat` (text)
  - `hunter_commercial_segment` (text)
  - `hunter_commercial_heat` (text)
  - `hunter_priority_category` (text)
  - `hunter_priority_label` (text)
  - `hunter_domain` (text, unique identifier)
  - `hunter_referral_id` (text, opsiyonel)
  
- [ ] **D365 Base URL**:
  - Organization URL alındı (örn: `https://org.crm.dynamics.com`)
  - App ID (eğer custom app kullanılıyorsa) alındı

---

### Hunter'da Yapılacaklar:

- [ ] **.env → D365 Config'leri Doldur**:
  ```bash
  HUNTER_D365_ENABLED=true
  HUNTER_D365_CLIENT_ID=<client_id>
  HUNTER_D365_CLIENT_SECRET=<client_secret>
  HUNTER_D365_TENANT_ID=<tenant_id>
  HUNTER_D365_BASE_URL=https://org.crm.dynamics.com
  HUNTER_D365_APP_ID=<app_id>  # Opsiyonel, eğer custom app varsa
  ```

- [ ] **Feature Flag Aktifleştirme**:
  - `HUNTER_D365_ENABLED=true` (önce sadece dev'de test et)
  - Production'a geçmeden önce dev'de 2-3 lead push test et

---

### Manual E2E Test:

- [ ] **2-3 Lead Push**:
  - Hunter'dan 2-3 lead seç (farklı segment'lerden: Migration, Existing, Cold)
  - "Push to Dynamics" butonuna tıkla
  - Celery task log'larını kontrol et
  - D365'te lead'lerin göründüğünü doğrula

- [ ] **D365'te Görünürlük**:
  - Lead'ler D365'te doğru formatta mı? (field mapping kontrol)
  - Custom hunter_* alanları dolu mu?
  - "Open in Dynamics" linki çalışıyor mu?

- [ ] **Hunter DB'de Status + ID Güncel**:
  - `companies.d365_sync_status = 'synced'` mı?
  - `companies.d365_lead_id` dolu mu?
  - `companies.d365_sync_last_at` timestamp doğru mu?

- [ ] **Error Handling Test**:
  - D365 down simülasyonu (network disconnect veya invalid credentials)
  - Error badge UI'da görünüyor mu?
  - Error mesajı doğru mu?

- [ ] **Duplicate Detection Test**:
  - Aynı lead'i 2 kez push et
  - D365'te duplicate oluşmadı mı? (upsert çalışıyor mu?)

---

## ✅ Başarı Kriterleri

- ✅ D365 tenant'ta app registration ve application user hazır
- ✅ Custom hunter_* alanları D365'te mevcut
- ✅ Hunter .env config'leri dolu ve test edildi
- ✅ 2-3 lead push başarılı (D365'te görünüyor)
- ✅ Hunter DB'de status ve lead_id güncel
- ✅ "Open in Dynamics" linki çalışıyor
- ✅ Error handling test edildi ve çalışıyor
- ✅ Duplicate detection test edildi ve çalışıyor

---

## 📁 İlgili Dosyalar

- `.env` - D365 config'leri
- `app/config.py` - Config validation
- `app/integrations/d365/client.py` - D365 client (token, API calls)
- `app/integrations/d365/mapping.py` - Field mapping
- `app/tasks/d365_push.py` - Celery task
- `app/api/v1/d365_routes.py` - API endpoint

---

## 🔗 İlgili Dokümanlar

- `CRITICAL-3-HAMLE-PRODUCT-READY.md` - Hamle 2 (D365 Push) genel planı
- `CORE-FREEZE-D365-PUSH-PLAN.md` - D365 mimari planı
- `D365-PHASE-2.5-VALIDATION-CHECKLIST.md` - Backend validation checklist
- `D365-PHASE-3-UI-STATUS-TODO.md` - UI & Status fazı

---

## 📝 Notlar

- **Ops Fazı**: Bu faz tamamen environment/ops işi. Kod değişikliği yok (sadece config).
- **Timing**: D365 tenant hazır olunca yapılacak. UI (Phase 3) bu fazı beklemeden başlayabilir.
- **Test Ortamı**: Önce dev'de test et, sonra production'a geç.
- **Rollback Plan**: Eğer sorun çıkarsa, `HUNTER_D365_ENABLED=false` yaparak feature'ı kapat.

