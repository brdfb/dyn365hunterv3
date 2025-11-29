# Hunter v1.0 — Sistem Durum Özeti

**Son güncelleme:** 2025-01-30 (Prod Go/No-Go inactive, roadmap moduna geçildi)  

**Durum:** Production-ready core engine (v1.0.0) - **Development Roadmap Mode**

**Önemli Notlar:**
- **Backend Engine:** ✅ Ferrari seviyesinde (DNS, scoring, enrichment, signals)
- **Core Freeze:** ✅ **AKTİF** — Core modüller dokunulmaz (CODEOWNERS, CI regression job, feature flags)
- **Partner Center:** ✅ **COMPLETED** (2025-01-30) - Kod bazında DONE, ürün bazında yeterince iyi seviyesinde
- **Dynamics 365:** ✅ **Backend %94 tamamlandı** (Phase 2.5), ✅ **Phase 3 (UI) tamamlandı** (2025-01-30), ✅ **Phase 2.9 (E2E) DEV TESTS COMPLETED** (2025-01-30 - HAMLE 2 dev testleri tamamlandı) (Adapter pattern ile implement edildi)
- **UI:** ✅ Çalışıyor, ⚠️ Estetik iyileştirme gerekiyor
- **Production Go/No-Go:** ⏸ **INACTIVE** - Altyapı dokümanları hazır, aktif süreç değil. Gerçek prod deployment yok, sadece roadmap modunda feature development.

**Aksiyon Planı:** Tüm detaylar ve 3 kritik hamle için `CRITICAL-3-HAMLE-PRODUCT-READY.md` dosyasına bakın.  
**Merkezi Roadmap**: `docs/active/DEVELOPMENT-ROADMAP.md` - Tüm aktif TODO'lar ve planlar  
**Core Freeze + D365 Plan:** `docs/archive/2025-01-30-CORE-FREEZE-D365-PUSH-PLAN.md` dosyasına bakın (archived).  
**Production Readiness Docs:** `docs/archive/2025-01-30-*` - Prod dokümanları arşivde, ihtiyaç olursa tekrar açılabilir.

---

## 1. Amaç ve Genel Tanım

Hunter, domain bazlı sinyal toplama ve kural tabanlı skorlamaya dayalı bir **lead intelligence engine**'dir.  

Ana hedef: Satışçının 2 dakikada, bir domain için:

- M365 kullanıyor mu / kullanmıyor mu?

- Migration fırsatı var mı?

- Ne kadar acil ve ne kadar büyük fırsat?

sorularına cevap verebilmesi.

---

## 2. Core Engine (Production-Ready)

**Durum:** ✅ **Ferrari seviyesinde** - DNS, scoring, enrichment, signals tam çalışıyor  
**Core Freeze:** ✅ **AKTİF** — Core modüller dokunulmaz koruma altında (2025-01-30)

### 2.0. Core Freeze Protokolü

**Amaç:** Core'a dokunursak enayi oluruz — 497 test, P0/P1/P-Stabilization hepsi yeşil.

**Koruma Mekanizmaları:**
- **CODEOWNERS:** Core modüller için 2 reviewer zorunlu
- **CI Regression Job:** Core testleri fail → merge yok
- **Feature Flags:** Yeni entegrasyonlar flag altında (`HUNTER_D365_ENABLED`, `HUNTER_PARTNER_CENTER_ENABLED`)
- **Fiziksel Ayrım:** Core (`app/core/`) vs Integration (`app/integrations/`)

**Dokunulmaz Core Modüller:**
- `app/core/scorer.py`
- `app/core/analyzer_*.py` (analyzer_dns, analyzer_whois, analyzer_enrichment)
- `app/core/normalizer.py`
- `app/core/provider_map.py`
- `app/core/priority.py`
- `app/core/sales_engine.py`
- `app/core/enrichment*.py`
- `app/core/ip_enrichment/` (L1 zaten prod active)
- `tests/test_scorer_*.py`
- `tests/test_regression_dataset.py`
- `tests/test_sales_*.py`

**Detaylar:** `docs/archive/2025-01-30-CORE-FREEZE-D365-PUSH-PLAN.md` dosyasına bakın (archived).

### 2.1. Analiz Yetkinlikleri

- **DNS Analizi**

  - MX / SPF / DKIM / DMARC

  - 10s timeout

  - Graceful fail (hata durumunda skor pipeline'ı çökmez)

- **WHOIS Lookup**

  - Registrar

  - Expiry tarihi

  - Nameserver listesi

  - 5s timeout

  - Graceful fail + caching

- **Provider Mapping**

  - M365, Google, Yandex, Zoho, Amazon, SendGrid, Mailgun, Hosting, Local, Unknown

  - MX root → provider sınıflandırması

  - Local provider detection (G20)

- **Scoring Engine**

  - Rule-based (rules.json)

  - Base score + provider points + signal points

  - 86 adet scoring testi (0 failure)

  - Segment classification:

    - Migration

    - Existing

    - Cold

    - Skip

  - Priority scoring: 1–7 (Migration her zaman öncelikli)

- **Domain Normalization**

  - Punycode decode

  - `www.` strip

  - Email → domain extraction

  - URL → domain extraction

---

### 2.2. Data Quality & Tracking

- Provider change tracking (history logging)

- Duplicate prevention / cleanup

- Invalid domain filtering

- IP enrichment (Level 1 exposure): ✅ **PRODUCTION ACTIVE** (2025-01-28)

  - MaxMind

  - IP2Location

  - IP2Proxy

  - Çıktı: `infrastructure_summary` alanı

  - Feature flag: `HUNTER_ENRICHMENT_ENABLED=true`

- G20 Feature Set:

  - DMARC coverage

  - Tenant size estimation (heuristic)

  - Local provider detection

---

## 3. API & Altyapı

### 3.1. Backend & DB

- **Backend:** FastAPI (Dockerized)

- **Database:** PostgreSQL

  - 5+ tablo

  - VIEW'ler

  - Alembic migrations (schema versioning)

- **API Versioning**

  - `/api/v1/` aktif

  - Backward compatibility korundu (eski endpoint'ler için)

### 3.2. Performans & Dayanıklılık

- **Rate Limiting**

  - Distributed (Redis-based)

  - Multi-worker destekli

- **Caching**

  - DNS/WHOIS/Provider/Scoring sonuçları

  - Redis cache layer

- **Bulk Operations**

  - Batch processing

  - Deadlock prevention

  - Retry stratejileri

- **Health Checks**

  - `/healthz/live`

  - `/healthz/ready`

  - `/healthz/startup`

- **Logging & Monitoring**

  - Structured logging (JSON)

  - PII masking (email/company_name log'ta yok)

  - Sentry error tracking

  - Metrics endpoint (basic)

---

## 4. Sales Intelligence Katmanı

- **Sales Engine**

  - One-liner özet

  - Call script

  - Discovery questions

  - Offer tier önerisi

  - Opportunity potential (puanlama)

  - Urgency sinyalleri

- **Sales Summary API**

  - Endpoint: `/api/v1/leads/{domain}/sales-summary`

  - Kontrat: "frozen" (v1.0 itibarıyla değişmez çekirdek)

- **Score Breakdown**

  - Detaylı analiz view'ı (API + UI)

  - Segment tooltips (sales-friendly açıklamalar)

  - IP enrichment bilgisi entegre

---

## 5. UI (Mini UI v1.1)

**Durum:** ✅ **Çalışıyor** - ⚠️ **Estetik iyileştirme gerekiyor** (Hamle 3: UI Polish)

- Lead table:

  - Sorting

  - Pagination

  - Full-text search

  - Segment/score/provider filtreleri

- Score breakdown modal:

  - Detaylı sinyaller

  - Segment açıklamaları

  - IP enrichment özeti

- Export:

  - CSV/Excel export

- Dashboard:

  - KPI cards:

    - Toplam lead

    - Migration lead sayısı

    - High-priority lead'ler

- UX:

  - Türkçe hata mesajları

  - Loading state'ler

  - Empty state'ler

  - Sales-friendly metinler

**Not:** UI çalışıyor ancak estetik iyileştirme gerekiyor (design system, component library, UX improvements). Detaylar için `CRITICAL-3-HAMLE-PRODUCT-READY.md` (Hamle 3) dosyasına bakın.

---

## 6. Background Jobs

- **Celery + Redis**

  - Async task processing

- **Bulk Scan**

  - Progress tracking

  - Rate limiting:

    - DNS: ~10 req/s

    - WHOIS: ~5 req/s

- **ReScan**

  - Provider / sinyal değişimi tespiti

  - Alert üretimi

- **Daily Rescan**

  - Celery Beat scheduler ile zamanlanmış işler

---

## 7. Test Suite & Kalite

- Toplam: **497 test**

  - 86 scoring testi (tamamı geçiyor)

  - API + integration testleri

  - Redis / Celery availability kontrolleri

  - Regression dataset: 26 case

- İzolasyon:

  - Transaction-based test isolation

  - Conditional execution (Redis/Celery yoksa ilgili testler otomatik skip)

---

## 8. Henüz Yapılmayanlar (Bilinçli Olarak Post-MVP)

- **Partner Center Integration (Phase 1–2)** → ✅ **COMPLETED** (2025-01-30)

  - ✅ API client, model ve pipeline tamamlandı

  - ✅ UI entegrasyonu tamamlandı (referral column, referral type filter, sync button, sync status indicator)

  - ✅ **Referral Detail Modal** (2025-01-30): Detay butonu, modal, action buttons (copy, send to D365, open in PC) tamamlandı

  - ✅ Background sync (Celery task) tamamlandı

  - ✅ **HAMLE 1 Tamamlandı** (2025-01-30): Kod bazında DONE, ürün bazında yeterince iyi seviyesinde. UI JS & error handling manuel smoke test ile kapanacak (mimari değişiklik gerektirmiyor).

  - ⏳ Scoring pipeline'a Azure Tenant ID / Co-sell sinyali tam entegre değil (future enhancement)
  - ✅ **Phase 4-6: Productization** (2025-01-30) - DB schema revision, filter rules, upsert strategy, summary logging, comprehensive tests (50 tests passing)
  - ✅ **Phase 7: Production Enablement** (2025-01-30) - Feature flag validation, logging review, metrics exposure, background sync enablement, production checklist
  - **Test Coverage**: 59/59 passing (37 domain extraction + 7 Phase 4 + 6 client + 6 Phase 5/6 + 3 Phase 3.3 URL-based + 10 Phase 7)

- **Dynamics 365 Integration** → ✅ **HAMLE 2 COMPLETED** (2025-01-30) - Backend %100 (Phase 2.5), UI (Phase 3), Production-grade E2E (Phase 2.9 - 3 senaryo), Go/No-Go: ✅ GO

  - ✅ **Phase 2.5 (Backend Validation)**: Backend tamamlandı (%94)
    - API endpoint: `POST /api/v1/d365/push-lead`
    - Celery task: `push_lead_to_d365`
    - D365 client: `app/integrations/d365/client.py`
    - Mapping: `app/integrations/d365/mapping.py`
    - DB migration: `d365_sync_status`, `d365_lead_id`, `d365_sync_last_at` alanları
    - ✅ **Eksik %6**: Gerçek D365 tenant ile E2E test (Phase 2.9'da yapıldı - dev testleri completed) → Backend %94 → %100
  - ✅ **Phase 3 (UI & Status)**: Tamamlandı (2025-01-30)
    - ✅ Lead listesine D365 badge eklendi
    - ✅ "Push to Dynamics" butonu eklendi
    - ✅ Lead detail modal'da D365 paneli eklendi
    - ✅ API response'a D365 alanları eklendi (d365_sync_status, d365_lead_id, d365_lead_url)
    - **Detaylar**: `D365-PHASE-3-UI-STATUS-TODO.md`
  - ✅ **Phase 2.9 (E2E Wiring)**: ✅ **COMPLETED** (2025-01-30 - HAMLE 2 production-grade E2E testleri tamamlandı)
    - App registration, Application User, Role + izinler ✅
    - Custom hunter_* alanları ✅
    - Production-grade E2E testler (3 senaryo: Happy path ✅, Idempotency ✅, Edge case ✅)
    - UI Badge & Link test ✅
    - Error Handling testler ✅
    - Go/No-Go Decision: ✅ GO
    - **Detaylar**: `docs/reference/D365-PHASE-2.9-E2E-RUNBOOK.md` (step-by-step runbook - reference guide)
  - **Mimari:** Adapter Pattern — Core'a dokunmadan yan taraftan takma
  - Plan: Hunter → D365 Sales:
    - Lead → D365 Lead mapping (tek yönlü push)
    - Duplicate detection (upsert by domain/email)
    - Custom hunter fields (`hunter_score`, `hunter_segment`, vb.)
  - İki yönlü sync yok (planlanmış değil)
  - **Detaylar:** 
    - `CRITICAL-3-HAMLE-PRODUCT-READY.md` (Hamle 2 - revize edildi)
    - `docs/archive/2025-01-30-CORE-FREEZE-D365-PUSH-PLAN.md` (Mimari plan - archived)

- **G21 Architecture Refactor (Phase 4–6)**

  - Phase 0–3 tamam

  - Phase 4: Dynamics Migration → **paused**

  - Phase 5: Monitoring & Stabilization → kısmen

  - Phase 6: Cleanup (deprecated endpoint/table remove) → beklemede

- **CRM-lite features**

  - Notes/Tags/Favorites yazma endpoint'leri: **410 Gone**

  - Okuma modunda, sadece migration destekli

---

## 9. Karar Logu (Kritik Mimari Kararlar)

- SSO (Azure AD OAuth) → **kaldırıldı**

  - Yerine: Internal Access Mode (network-level erişim)

- Partner Center Phase 2 → ✅ **COMPLETED** (2025-01-30)

  - All tasks completed (Tasks 2.1-2.6)
  - Backend: API client, referral ingestion, sync endpoint, Celery task
  - UI: Referral column with badges, referral type filter, sync button (header), sync status indicator (right-top)
  - Background sync: Celery Beat schedule (10 min prod, 30s dev)
  - ✅ **Phase 4-6: Productization** (2025-01-30) - DB schema revision, filter rules, upsert strategy, summary logging, comprehensive tests (50 tests passing)
  - ✅ **Phase 7: Production Enablement** (2025-01-30) - Feature flag validation, logging review, metrics exposure, background sync enablement, production checklist
  - All tests passing (59/59 tests: 37 domain extraction + 7 Phase 4 + 6 client + 6 Phase 5/6 + 3 Phase 3.3 URL-based + 10 Phase 7)
  - ✅ **HAMLE 1 Tamamlandı** (2025-01-30): Kod bazında DONE, ürün bazında yeterince iyi seviyesinde

- CRM-lite → **deprecated**

  - Gerçek CRM fonksiyonları Dynamics 365'e taşınacak

- Enterprise-grade kalite hedefi:

  - Logging, Sentry, health checks, rate limiting, caching, test coverage

---

## 10. Versiyon & Çıkış Durumu

- **Tag:** `v1.0.0`

- **Durum:** Production-ready core engine - **Development Roadmap Mode**

- **Production Go/No-Go:** ⏸ **INACTIVE** (2025-01-30)
  - Prod readiness dokümanları hazır (arşivde: `docs/archive/2025-01-30-*`)
  - Aktif prod deployment süreci yok
  - Odak: Feature development (Leads 500 fix ✅, D365 entegrasyonu ✅, PC Phase 4-5 ✅, UI düzeni ⏳)
  - Prod konuşmaları "inactive" modda - ihtiyaç olursa tekrar açılır

- **Leads 500 Bug Fix** → ✅ **FIXED** (2025-01-30)
  - **Problem**: `GET /api/v1/leads` endpoint 500 Internal Server Error
  - **Root Cause**: `referral_type` parametresi `get_leads_v1` fonksiyonunda eksikti
  - **Fix**: `referral_type` parametresi eklendi ve `get_leads` çağrısına geçirildi
  - **Status**: ✅ **FIXED** - Production deployment için hazır
  - **Reference**: `docs/active/LEADS-500-BUG-FIX.md`

- **Roadmap:** `docs/active/G21-ROADMAP-CURRENT.md` - Aktif development roadmap

Bu doküman, Hunter v1.0 çekirdeğinin **tek resmi durum özeti** olarak kullanılmalıdır.

