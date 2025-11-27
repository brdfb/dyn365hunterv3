# Phase 3 — UI & Status (D365 Integration)

**Tarih**: 2025-01-30  
**Durum**: In Progress  
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

### 1. API: Companies/Leads Response'a D365 Alanlarını Ekle

**Dosya**: `app/api/v1/leads.py`

- [ ] `d365_sync_status` alanını response'a ekle
  - Değerler: `not_synced`, `queued`, `in_progress`, `synced`, `error`
- [ ] `d365_sync_last_at` alanını response'a ekle (timestamp)
- [ ] `d365_lead_id` alanını response'a ekle (opsiyonel, UI'de direkt gösterme, sadece link üretmek için)
- [ ] `d365_lead_url` alanını response'a ekle (jenerik URL üretilebilir: `base_url + id`)
  - Config'den `HUNTER_D365_BASE_URL` alınacak
  - Format: `{base_url}/main.aspx?appid={app_id}&pagetype=entityrecord&etn=lead&id={d365_lead_id}`

**Not**: DB'de zaten `companies` tablosunda bu alanlar var (`d365_lead_id`, `d365_sync_status`, `d365_sync_last_at`). Sadece API response'a eklemek gerekiyor.

---

### 2. UI: Lead Listesine D365 Badge

**Dosya**: `mini-ui/js/ui-leads.js` (veya ilgili UI dosyası)

- [ ] Lead tablosuna `D365` kolonu ekle
- [ ] Badge'ler:
  - **Not Synced**: Gri badge (varsayılan)
  - **Queued/In Progress**: Sarı badge (spinner/loading icon)
  - **Synced**: Yeşil badge (checkmark icon)
  - **Error**: Kırmızı badge (X icon, hover'da kısa mesaj göster)
- [ ] Badge'ler tıklanabilir → Lead detail modal açılır (D365 bölümüne scroll)

**Design**: Badge'ler küçük, renkli, icon'lu olmalı. Hover tooltip'ler eklenmeli.

---

### 3. UI: "Push to Dynamics" Aksiyonu

**Dosya**: `mini-ui/js/d365_actions.js` (yeni dosya veya mevcut UI dosyası)

- [ ] Lead satırında buton veya row action ekle:
  - **Single push**: `POST /api/v1/d365/push-lead` (lead_id ile)
  - **Bulk push**: Multiple lead_id'ler için batch endpoint (opsiyonel, Phase 3'te tek tek yeterli)
- [ ] Feature flag check:
  - `HUNTER_D365_ENABLED=false` → buton gizli veya disabled tooltip'li
  - Tooltip: "D365 integration is disabled"
- [ ] Request success → badge hemen `queued` olsun (optimistic UI)
- [ ] Error handling:
  - API error → toast notification
  - Badge `error` state'e geçsin
  - Error mesajı tooltip'te gösterilsin

**UX**: Buton tıklandığında loading state göster, success/error feedback ver.

---

### 4. UI: Lead Detail View'da Detaylı D365 Kutusu

**Dosya**: `mini-ui/js/ui-leads.js` (lead detail modal)

- [ ] "Dynamics 365" paneli ekle:
  - **Status**: Badge (synced/error/queued/in_progress/not_synced)
  - **Last sync time**: Timestamp (human-readable format: "2 hours ago", "2025-01-30 14:30")
  - **"Open in Dynamics" link**: Eğer `d365_lead_id` varsa, link göster
    - Link format: `{HUNTER_D365_BASE_URL}/main.aspx?appid={app_id}&pagetype=entityrecord&etn=lead&id={d365_lead_id}`
  - **Error message**: Eğer `d365_sync_status = error` ise, error mesajı göster
- [ ] "Push to Dynamics" butonu (eğer not_synced veya error ise)

**Design**: Panel, lead detail modal içinde ayrı bir section olmalı. Visual hierarchy: Status → Last sync → Actions.

---

### 5. Monitoring / Logging (Minimum)

**Dosya**: `app/api/v1/d365_routes.py`, `app/tasks/d365_push.py`

- [ ] Metric counters (Prometheus veya mevcut metrics endpoint):
  - `d365_push_requested_total` (counter)
  - `d365_push_success_total` (counter)
  - `d365_push_failed_total` (counter)
- [ ] Log context:
  - `event="d365_push_request"`, `company_id`, `domain`, `status`
  - Structured logging (JSON format)

**Not**: Mevcut logging yapısı zaten var (`app/core/logging.py`). Sadece metric'leri eklemek gerekiyor.

---

## ✅ Başarı Kriterleri

- ✅ Lead listesinde D365 badge görünüyor
- ✅ Badge'ler doğru status'u gösteriyor (synced/error/queued/in_progress/not_synced)
- ✅ "Push to Dynamics" butonu çalışıyor (feature flag check ile)
- ✅ Lead detail modal'da D365 paneli görünüyor
- ✅ "Open in Dynamics" linki çalışıyor (eğer lead_id varsa)
- ✅ Optimistic UI çalışıyor (buton tıklandığında badge hemen queued oluyor)
- ✅ Error handling çalışıyor (toast notification, error badge, tooltip)
- ✅ Metrics endpoint'te D365 metrikleri görünüyor

---

## 📁 Dosyalar

### Yeni Dosyalar:
- `mini-ui/js/d365_actions.js` (opsiyonel, mevcut UI dosyasına da eklenebilir)

### Modifiye Edilecek Dosyalar:
- `app/api/v1/leads.py` - D365 alanlarını response'a ekle
- `mini-ui/js/ui-leads.js` - D365 badge, lead detail modal D365 paneli
- `mini-ui/index.html` - D365 kolonu HTML'i (eğer gerekirse)
- `app/api/v1/d365_routes.py` - Metrics ekle (opsiyonel)
- `app/tasks/d365_push.py` - Metrics ekle (opsiyonel)
- `app/config.py` - `HUNTER_D365_BASE_URL` config ekle (eğer yoksa)

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

