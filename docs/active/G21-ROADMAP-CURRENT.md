# G21 — Architecture & Integration Roadmap (Current State)

**Son güncelleme:** 2025-01-30  

**Durum:** Phase 0–3 tamam, Phase 4 paused, Phase 5–6 pending  
**Integration Roadmap:** Phase 2 (Partner Center) ✅ Completed (2025-01-30)

---

## 1. Amaç

G21, Hunter'ı:

- "Core signal engine" olarak sadeleştirmek,

- CRM-lite yükünü azaltmak,

- Entegrasyonları (Sales Engine, Partner Center, Dynamics 365) **adapter** mantığıyla dışarı taşımak

için tasarlanmış mimari refactor ve entegrasyon yol haritasıdır.

**Not:** Integration Roadmap Phase 2 (Partner Center Referrals) ✅ **Completed** (2025-01-30) - Backend, UI, background sync tamamlandı. Partner Center entegrasyonu adapter pattern ile implement edildi.

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

- Temel şema ve mapping fikirleri hazır

- Uygulama: Post-MVP

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

- **Integration Roadmap Phase 2 (Partner Center)** ✅ **Completed** (2025-01-30):
  - Backend: API client, referral ingestion, sync endpoint, referral detail endpoint, Celery task
  - UI: Referral column, referral type filter, sync button, sync status indicator, referral detail modal
  - Referral Detail Modal: Detay butonu, modal content, action buttons (copy, send to D365, open in PC)
  - Background Sync: Celery Beat schedule (10 min prod, 30s dev)
  - Status: Production-ready, feature flag OFF (MVP-safe)

---

## 5. Son Durum Özeti

- Hunter v1.0 core engine **production-ready**.

- G21, mimari sadeleşme ve entegrasyon için ana şemsiye:

  - Phase 0–3 tamam → "Core clean-up & Sales Engine" bitti.

  - **Integration Roadmap Phase 2 (Partner Center)** ✅ **Completed** (2025-01-30) → Adapter pattern ile entegrasyon tamamlandı.

  - Phase 4–6 → Post-MVP entegrasyon ve temizlik işleri (Dynamics Migration Integration Roadmap Phase 3 ile birlikte).

Bu doküman, G21 kapsamının **tek güncel referans noktası** olarak kullanılmalıdır.

