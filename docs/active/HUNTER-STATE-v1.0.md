# Hunter v1.0 — Sistem Durum Özeti

**Son güncelleme:** 2025-01-28  

**Durum:** Production-ready core engine (v1.0.0)

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

- IP enrichment (Level 1 exposure):

  - MaxMind

  - IP2Location

  - IP2Proxy

  - Çıktı: `infrastructure_summary` alanı

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

- **Partner Center Integration (Phase 1–2)**

  - API client, model ve pipeline kısmen hazır

  - Feature flag: OFF

  - UI entegrasyonu yok

  - Background sync (Celery task) yok

  - Scoring pipeline'a Azure Tenant ID / Co-sell sinyali tam entegre değil

- **Dynamics 365 Integration**

  - Hunter → D365 Sales:

    - Lead → Contact/Account → Opportunity mapping

  - İki yönlü sync yok

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

- Partner Center Phase 2 → **park edildi**

  - G21 Integration Roadmap ile yeniden çerçevelenecek

- CRM-lite → **deprecated**

  - Gerçek CRM fonksiyonları Dynamics 365'e taşınacak

- Enterprise-grade kalite hedefi:

  - Logging, Sentry, health checks, rate limiting, caching, test coverage

---

## 10. Versiyon & Çıkış Durumu

- **Tag:** `v1.0.0`

- **Durum:** Production-ready core engine

- **Checklist:** `docs/active/GO-NO-GO-CHECKLIST-v1.0.md` → tüm Must-Have maddeler ✅

- **Prod kararı:** GO (2025-01-28)

Bu doküman, Hunter v1.0 çekirdeğinin **tek resmi durum özeti** olarak kullanılmalıdır.

