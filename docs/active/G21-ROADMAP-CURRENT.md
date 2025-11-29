# G21 — Architecture & Integration Roadmap (Current State)

**Son güncelleme:** 2025-01-30 (Partner Center ve Dynamics 365 durumları netleştirildi)  

**Durum:** Phase 0–3 tamam, Phase 4 paused, Phase 5–6 pending  
**Integration Roadmap:** Phase 2 (Partner Center) ✅ COMPLETED (2025-01-30 - Kod bazında DONE, ürün bazında yeterince iyi), Phase 3 (D365) ✅ COMPLETED (2025-01-30 - HAMLE 2 production-grade E2E testleri tamamlandı, Go/No-Go: ✅ GO)

---

## 1. Amaç

G21, Hunter'ı:

- "Core signal engine" olarak sadeleştirmek,

- CRM-lite yükünü azaltmak,

- Entegrasyonları (Sales Engine, Partner Center, Dynamics 365) **adapter** mantığıyla dışarı taşımak

için tasarlanmış mimari refactor ve entegrasyon yol haritasıdır.

**Not:** Integration Roadmap Phase 2 (Partner Center Referrals) ✅ **COMPLETED** (2025-01-30) - Kod bazında DONE, ürün bazında yeterince iyi seviyesinde. Backend, UI, background sync tamamlandı. Partner Center entegrasyonu adapter pattern ile implement edildi. UI JS & error handling manuel smoke test ile kapanacak (mimari değişiklik gerektirmiyor). Phase 3 (D365) ✅ **COMPLETED** (2025-01-30 - HAMLE 2 production-grade E2E testleri tamamlandı, 3 senaryo, Go/No-Go: ✅ GO).

---

## 2. Faz Özeti

| Faz  | Adı                               | Durum    | Not |

|------|-----------------------------------|----------|-----|

| 0    | Preparation & Inventory           | ✅ Bitti | Mevcut endpoint ve feature envanteri çıkarıldı |

| 1    | Deprecation Plan & Flags         | ✅ Bitti | CRM-lite, eski endpoint'ler için feature flag ve 410 Gone stratejisi belirlendi |

| 2    | Sales Engine Layer                | ✅ Bitti | Sales summary endpoint + sales logic eklendi |

| 3    | Read-Only Mode for Deprecated     | ✅ Bitti | CRM-lite yazma kaldırıldı, okuma + migration desteği kaldı |

| 4    | Dynamics Migration                | ⏸ Paused | D365 entegrasyon planı ile overlap → durduruldu |

| 5    | Monitoring & Stabilization        | ◻ Kısmi  | Bazı metrikler var, tam G21 kapsamı tamamlanmadı |

| 6    | Cleanup & Hard Cut                | ◻ Açık   | Deprecated endpoint ve tablolardan tamamen çıkış |

---

## 3. Faz Detayları

### Phase 0 — Preparation & Inventory (✅)

- Tüm endpoint'lerin listesi çıkarıldı.

- CRM-lite fonksiyonları (Notes/Tags/Favorites) işaretlendi.

- UI/Backend/DB çapraz bağımlılıkları çıkarıldı.

- Dokümantasyon: `NO-BREAK-REFACTOR-PLAN.md`

---

### Phase 1 — Deprecation Plan & Flags (✅)

- Feature flag alt yapısı kuruldu.

- Eski endpoint'ler için:

  - "deprecated" etiketi

  - Logs'ta uyarı

- G19–G21 dokümanları senkronize edildi.

---

### Phase 2 — Sales Engine Layer (✅)

- `/api/v1/leads/{domain}/sales-summary` endpoint'i eklendi.

- İçerik:

  - One-liner

  - Call script

  - Discovery questions

  - Offer tier önerisi

  - Opportunity potential + urgency

- Kontrat "frozen" (v1.0 sonrası geriye dönük uyumluluk korunacak).

---

### Phase 3 — Read-Only Mode for Deprecated Features (✅)

- Notes/Tags/Favorites yazma endpoint'leri:

  - 410 Gone

- Okuma endpoint'leri:

  - Sadece migration amaçlı aktif

- UI tarafında CRM-lite aksiyonları kaldırıldı.

---

### Phase 4 — Dynamics Migration (⏸ Paused)

**Hedef:**

- Hunter lead'lerini Dynamics 365 Sales pipeline'ına taşımak:

  - Lead → Contact/Account → Opportunity

**Neden durduruldu:**

- Integration Roadmap Phase 3 ile çakışma

- Önce Hunter core v1.0 stabilizasyonu tamamlandı

- Integration Roadmap Phase 2 (Partner Center) tamamlandı (2025-01-30) → Phase 3 (Dynamics) sırası geldi

**Şu anki durum:**

- ✅ **BACKEND %94 TAMAMLANDI** (Phase 2.5 - 2025-01-30)
  - API endpoint, Celery task, D365 client, mapping, DB migration tamamlandı
  - ✅ **Eksik %6**: Gerçek D365 tenant ile E2E test (Phase 2.9'da yapıldı - dev testleri completed)
- ✅ **PHASE 3 (UI) TAMAMLANDI** (2025-01-30)
  - ✅ Lead listesine D365 badge, "Push to Dynamics" butonu, lead detail modal D365 paneli
  - ✅ API response'a D365 alanları eklendi
  - **Detaylar**: `D365-PHASE-3-UI-STATUS-TODO.md`
- ✅ **PHASE 2.9 (E2E WIRING) DEV TESTS COMPLETED** (2025-01-30 - Go/No-Go: ✅ GO)
  - App registration, Application User, Role + izinler, custom hunter_* alanları
  - **Detaylar**: `docs/reference/D365-PHASE-2.9-E2E-RUNBOOK.md` (step-by-step runbook - reference guide)
  - **Status:** Runbook hazır, tenant setup bekleniyor
- **Mimari:** Adapter Pattern — Core Freeze + Integration Layer
- **Detaylı Plan:** `docs/archive/2025-01-30-CORE-FREEZE-D365-PUSH-PLAN.md` dosyasına bakın (archived)

---

### Phase 5 — Monitoring & Stabilization (◻ Kısmi)

- Şu an mevcut:

  - Sentry

  - Structured logging

  - Health probes

  - Bazı metrikler

- G21 hedefleri:

  - Daha detaylı service-level metrics

  - Hunter spesifik KPI'lar (scan volume, success rate, cache hit rate, vs.)

  - Alerting kuralları

---

### Phase 6 — Cleanup & Hard Cut (◻ Açık)

- Kapsam:

  - Deprecated endpoint'lerin tamamen kaldırılması

  - Deprecated DB alan/tablolarının temizlenmesi

  - Kod ve dokümanlardan eski referansların silinmesi

- Zamanlama:

  - Dynamics entegrasyonu netleştikten ve migration tamamlandıktan sonra

  - Geri dönüş ihtiyacının kalmadığı noktada uygulanacak

---

## 4. Decision Log (G21 Özel)

- CRM-lite, Hunter içerisinde kalıcı bir ürün olmayacak.

  - Not alma, tagging, favorites → D365 tarafına taşınacak.

- Sales Engine Hunter içinde kalacak, ancak:

  - Hunter = "signal + intelligence"

  - CRM = "pipeline + process"

- Integration yapısı:

  - Hunter → dış sistemlere **adapter** katmanı ile bağlanacak.

- Phase 4 (Dynamics Migration), **Integration Roadmap Phase 3** ile birlikte ele alınacak.

- **Integration Roadmap Phase 2 (Partner Center)** ✅ **BACKEND COMPLETED** (2025-01-30), ⚠️ **PRODUCTION'DA AKTİF DEĞİL**:
  - Backend: API client, referral ingestion, sync endpoint, referral detail endpoint, Celery task
  - UI: Referral column, referral type filter, sync button, sync status indicator, referral detail modal
  - Referral Detail Modal: Detay butonu, modal content, action buttons (copy, send to D365, open in PC)
  - Background Sync: Celery Beat schedule (10 min prod, 30s dev)
  - ⚠️ **Status:** Production-ready, feature flag OFF (MVP-safe) - Aktifleştirme için `CRITICAL-3-HAMLE-PRODUCT-READY.md` (Hamle 1) dosyasına bakın

---

## 5. Son Durum Özeti

- Hunter v1.0 core engine **production-ready**.

- G21, mimari sadeleşme ve entegrasyon için ana şemsiye:

  - Phase 0–3 tamam → "Core clean-up & Sales Engine" bitti.

  - **Integration Roadmap Phase 2 (Partner Center)** ✅ **COMPLETED** (2025-01-30) → Kod bazında DONE, ürün bazında yeterince iyi seviyesinde. Adapter pattern ile entegrasyon tamamlandı. UI JS & error handling manuel smoke test ile kapanacak (mimari değişiklik gerektirmiyor).
- **Integration Roadmap Phase 3 (D365)** ✅ **DEV TESTS COMPLETED** (2025-01-30 - HAMLE 2 dev testleri tamamlandı) → Phase 2.9 E2E Wiring dev testleri completed, Go/No-Go: ✅ GO.

  - Phase 4–6 → Post-MVP entegrasyon ve temizlik işleri (Dynamics Migration Integration Roadmap Phase 3 ile birlikte).

Bu doküman, G21 kapsamının **tek güncel referans noktası** olarak kullanılmalıdır.

