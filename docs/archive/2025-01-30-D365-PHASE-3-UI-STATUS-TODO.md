# Phase 3 — UI & Status (D365 Integration)

**Tarih**: 2025-01-30  
**Durum**: ✅ **TAMAMLANDI** (2025-01-30)  
**Öncelik**: P0 (Kritik - Kullanıcı görünürlüğü)  
**Efor**: M (Medium - ~1 gün)

---

## 🎯 Hedef

Satışçı / kullanıcı, Hunter ekranından şunu net görebilsin:

- ✅ Bu lead D365'e gönderildi mi?
- ✅ Ne zaman gönderildi?
- ✅ Hata varsa ne?

**Karar**: D365 tenant beklenmeyecek. Backend D365 Push v1 yeterince sağlam. Phase 3 hemen başlayabilir. E2E (Phase 2.9) ayrı bir "ops fazı" olarak tenant hazır olunca yapılacak.

---

## 📋 TODO Checklist

### 1. API: Companies/Leads Response'a D365 Alanlarını Ekle ✅

**Dosya**: `app/api/leads.py` (v1 proxy üzerinden)

- [x] `d365_sync_status` alanını response'a ekle ✅
  - Değerler: `not_synced`, `queued`, `in_progress`, `synced`, `error`
- [x] `d365_sync_last_at` alanını response'a ekle (timestamp) ✅
- [x] `d365_lead_id` alanını response'a ekle (opsiyonel, UI'de direkt gösterme, sadece link üretmek için) ✅
- [x] `d365_lead_url` alanını response'a ekle (jenerik URL üretilebilir: `base_url + id`) ✅
  - Config'den `HUNTER_D365_BASE_URL` alınacak
  - Format: `{base_url}/main.aspx?appid={app_id}&pagetype=entityrecord&etn=lead&id={d365_lead_id}`

**Not**: DB'de zaten `companies` tablosunda bu alanlar var (`d365_lead_id`, `d365_sync_status`, `d365_sync_last_at`). API response'a eklendi.

---

### 2. UI: Lead Listesine D365 Badge ✅

**Dosya**: `mini-ui/js/ui-leads.js`

- [x] Lead tablosuna `D365` kolonu ekle ✅
- [x] Badge'ler: ✅
  - **Not Synced**: Gri badge (varsayılan)
  - **Queued/In Progress**: Sarı badge (spinner/loading icon)
  - **Synced**: Yeşil badge (checkmark icon)
  - **Error**: Kırmızı badge (X icon, hover'da kısa mesaj göster)
- [x] Badge'ler tıklanabilir → Lead detail modal açılır (D365 bölümüne scroll) ✅

**Design**: Badge'ler küçük, renkli, icon'lu olmalı. Hover tooltip'ler eklenmeli. ✅

---

### 3. UI: "Push to Dynamics" Aksiyonu ✅

**Dosya**: `mini-ui/js/ui-leads.js` (handleD365Push fonksiyonu)

- [x] Lead detail modal'da buton eklendi ✅
  - **Single push**: `POST /api/v1/d365/push-lead` (company_id ile)
  - Bulk push: Phase 3'te tek tek yeterli (gelecekte eklenebilir)
- [x] Feature flag check: ✅
  - `HUNTER_D365_ENABLED=false` → buton disabled (API seviyesinde kontrol)
  - Error handling ile kullanıcıya bilgi veriliyor
- [x] Request success → badge hemen `queued` olsun (optimistic UI) ✅
- [x] Error handling: ✅
  - API error → toast notification
  - Badge `error` state'e geçsin
  - Error mesajı tooltip'te gösterilsin

**UX**: Buton tıklandığında loading state göster, success/error feedback ver. ✅

---

### 4. UI: Lead Detail View'da Detaylı D365 Kutusu ✅

**Dosya**: `mini-ui/js/ui-leads.js` (loadD365Panel, renderD365Panel fonksiyonları)

- [x] "Dynamics 365" paneli eklendi ✅
  - **Status**: Badge (synced/error/queued/in_progress/not_synced)
  - **Last sync time**: Timestamp (human-readable format: "2 hours ago", "2025-01-30 14:30")
  - **"Open in Dynamics" link**: Eğer `d365_lead_id` varsa, link göster ✅
    - Link format: `{HUNTER_D365_BASE_URL}/main.aspx?appid={app_id}&pagetype=entityrecord&etn=lead&id={d365_lead_id}`
  - **Error message**: Eğer `d365_sync_status = error` ise, error mesajı göster (tooltip'te)
- [x] "Push to Dynamics" butonu (eğer not_synced veya error ise) ✅

**Design**: Panel, lead detail modal içinde ayrı bir section olmalı. Visual hierarchy: Status → Last sync → Actions. ✅

---

### 5. Monitoring / Logging (Minimum) ⚠️

**Dosya**: `app/api/v1/d365_routes.py`, `app/tasks/d365_push.py`

- [ ] Metric counters (Prometheus veya mevcut metrics endpoint): ⚠️ **Opsiyonel - Post-MVP**
  - `d365_push_requested_total` (counter)
  - `d365_push_success_total` (counter)
  - `d365_push_failed_total` (counter)
- [x] Log context: ✅
  - Structured logging mevcut (`app/core/logging.py`)
  - D365 push işlemleri loglanıyor

**Not**: Mevcut logging yapısı zaten var (`app/core/logging.py`). Metric'ler opsiyonel ve post-MVP'ye bırakılabilir.

---

## ✅ Başarı Kriterleri

- ✅ Lead listesinde D365 badge görünüyor
- ✅ Badge'ler doğru status'u gösteriyor (synced/error/queued/in_progress/not_synced)
- ✅ "Push to Dynamics" butonu çalışıyor (feature flag check ile)
- ✅ Lead detail modal'da D365 paneli görünüyor
- ✅ "Open in Dynamics" linki çalışıyor (eğer lead_id varsa)
- ✅ Optimistic UI çalışıyor (buton tıklandığında badge hemen queued oluyor)
- ✅ Error handling çalışıyor (toast notification, error badge, tooltip)
- ⚠️ Metrics endpoint'te D365 metrikleri görünüyor (opsiyonel - post-MVP)

**Phase 3 Tamamlandı**: 2025-01-30 - Tüm kritik özellikler implement edildi. Metrics opsiyonel olarak post-MVP'ye bırakıldı.

---

## 📁 Dosyalar

### Yeni Dosyalar:
- `mini-ui/js/d365_actions.js` (opsiyonel, mevcut UI dosyasına da eklenebilir)

### Modifiye Edilen Dosyalar (✅ Tamamlandı):
- ✅ `app/api/leads.py` - D365 alanlarını response'a eklendi (d365_sync_status, d365_sync_last_at, d365_lead_id, d365_lead_url)
- ✅ `mini-ui/js/ui-leads.js` - D365 badge (getD365Badge), lead detail modal D365 paneli (loadD365Panel, renderD365Panel, handleD365Push)
- ✅ `mini-ui/js/api.js` - D365 push API çağrısı (pushLeadToD365)
- ⚠️ `app/api/v1/d365_routes.py` - Metrics ekle (opsiyonel - post-MVP)
- ⚠️ `app/tasks/d365_push.py` - Metrics ekle (opsiyonel - post-MVP)
- ✅ `app/config.py` - `HUNTER_D365_BASE_URL` config mevcut

---

## 🔗 İlgili Dokümanlar

- `CRITICAL-3-HAMLE-PRODUCT-READY.md` - Hamle 2 (D365 Push) genel planı
- `CORE-FREEZE-D365-PUSH-PLAN.md` - D365 mimari planı
- `D365-PHASE-2.5-VALIDATION-CHECKLIST.md` - Backend validation checklist
- `D365-PHASE-2.9-E2E-WIRING.md` - E2E ops fazı (tenant hazır olunca)

---

## 📝 Notlar

- **Backend Hazır**: D365 push backend'i zaten tamamlanmış (Phase 2.5). Sadece UI katmanı eksik.
- **Feature Flag**: `HUNTER_D365_ENABLED` flag'i ile kontrol edilecek. False ise UI'da buton gizli/disabled olacak.
- **Optimistic UI**: Kullanıcı deneyimi için buton tıklandığında badge hemen `queued` olmalı, backend response'u beklenmeden.
- **Error Handling**: D365 down olsa bile Hunter core çalışmaya devam etmeli. UI'da error badge gösterilmeli.

