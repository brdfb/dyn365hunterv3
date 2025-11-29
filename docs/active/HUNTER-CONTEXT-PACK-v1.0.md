# 🧱 **HUNTER-CONTEXT-PACK v1.0**

**Master Product + Architecture + Integration + Operations Document**

**Last Updated:** 2025-01-30  
**Owner:** Bered  
**Version:** v1.0.0  
**Status:** Production-Ready Core Engine - **Development Roadmap Mode**  
**Production Go/No-Go:** ⏸ **INACTIVE** - Altyapı dokümanları hazır (arşivde), aktif süreç değil. Odak: Feature development.  
**Merkezi Roadmap**: `docs/active/DEVELOPMENT-ROADMAP.md` - Tüm aktif TODO'lar ve planlar

**Scope:** Hunter Core Engine → Sales Intelligence → Partner Center → Dynamics 365 → G21 Roadmap → Deployment Standards

---

## 📋 **Document Index**

1. [Vision & Purpose](#1-vision--purpose)
2. [System Overview](#2-system-overview)
3. [Architecture](#3-architecture)
4. [Data Model & Lead Schema](#4-data-model--lead-schema)
5. [Intelligence Engine](#5-intelligence-engine)
6. [Partner Center Integration](#6-partner-center-integration)
7. [Dynamics 365 Integration](#7-dynamics-365-integration)
8. [API Contract](#8-api-contract)
9. [UI Contract](#9-ui-contract)
10. [Background Jobs](#10-background-jobs)
11. [Feature Flags](#11-feature-flags)
12. [Operational Standards](#12-operational-standards)
13. [Roadmap (G21)](#13-roadmap-g21)
14. [Known Issues / Open Decisions](#14-known-issues--open-decisions)
15. [Version History](#15-version-history)

---

## 1) **Vision & Purpose**

### Hunter = Lead Intelligence Engine

**Amaç:**
- Domain bazlı sinyaller toplama →
- Provider analizi →
- M365 fit segmentation →
- Sales intelligence üretimi →
- CRM pipeline'a entegre edilebilir lead kalitesi sağlama

**Hunter'ın 3 Temel Çıktısı:**
1. **Migration / Existing / Cold** segmenti
2. **Final Score (0–100)**
3. **Sales-ready özet** (one-liner, urgency, potential)

**Core Principle:**
> **"Dışarıya çıkıp veri topluyorsa veya ağır analizse → Hunter."**  
> **"Zaten Dataverse + Dynamics ile yapılabiliyorsa → Hunter'a koyma."**

**Hunter'ın "Kutsal Alanı" (Sadece Bunları Yapsın):**
1. **Ağır / teknik / CRM'in yapamayacağı analizler**
   - DNS (MX/SPF/DKIM/DMARC)
   - WHOIS (expiry, registrar, nameserver)
   - Provider tespiti (M365 / Google / Hosting / Local / Hybrid)
   - IT olgunluk skoru
   - Migration / Existing / Skip segmenti
   - Risk flag'ler (DKIM yok, DMARC none, expiry yaklaşıyor vs.)

2. **Zekâ gerektiren özetler**
   - 1 cümlelik satış özeti
   - Call script / discovery soru seti
   - Basic–Pro–Enterprise teklif önerisi
   - Fırsat puanı (opportunity potential / urgency)

3. **Dış dünya ile konuşma**
   - DNS, WHOIS, SMTP check gibi "çıkışlı" işler
   - Bunlar CRM tarafında yapılamaz, burası Hunter'ın ekmeği

---

## 2) **System Overview**

### 2.1 Core Engine

**Durum:** ✅ **Ferrari seviyesinde** - DNS, scoring, enrichment, signals tam çalışıyor  
**Core Freeze:** ✅ **AKTİF** — Core modüller dokunulmaz koruma altında (2025-01-30)

**Analiz Yetkinlikleri:**
- **DNS Analysis**
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
  - Segment classification: Migration, Existing, Cold, Skip
  - Priority scoring: 1–7 (Migration her zaman öncelikli)

- **Domain Normalization**
  - Punycode decode
  - `www.` strip
  - Email → domain extraction
  - URL → domain extraction

- **Data Quality & Tracking**
  - Provider change tracking (history logging)
  - Duplicate prevention / cleanup
  - Invalid domain filtering
  - IP enrichment (Level 1 exposure): ✅ **PRODUCTION ACTIVE** (2025-01-28)
  - G20 Feature Set: DMARC coverage, Tenant size estimation, Local provider detection

### 2.2 Modules

1. **Hunter Core** (`app/core/`)
   - DNS/WHOIS analyzers
   - Scoring engine
   - Provider mapping
   - Sales engine
   - Enrichment service

2. **Sales Intelligence** (`app/core/sales_engine.py`)
   - One-liner özet
   - Call script generation
   - Discovery questions
   - Offer tier önerisi
   - Opportunity potential

3. **Partner Center Adapter** (`app/core/partner_center.py`, `app/core/referral_ingestion.py`)
   - OAuth client
   - Referral ingestion
   - Sync logic
   - Celery task

4. **Dynamics 365 Adapter** (`app/integrations/d365/`)
   - D365 Web API client
   - Lead mapping (24 fields)
   - Push logic
   - Retry mechanism

5. **Background Tasks** (`app/core/tasks.py`, `app/tasks/d365_push.py`)
   - Bulk scan
   - Daily rescan
   - Provider change detection
   - Partner Center sync
   - D365 push retry

6. **Mini UI** (`mini-ui/`)
   - Lead table
   - Score breakdown modal
   - Export functionality
   - Dashboard KPIs

### 2.3 Feature Flags

**Safety-first rollout:**
- `HUNTER_PARTNER_CENTER_ENABLED` = OFF (default: false)
- `HUNTER_D365_ENABLED` = OFF (default: false)
- `HUNTER_ENRICHMENT_ENABLED` = ON (production active)
- `HUNTER_SALES_ENGINE_ENABLED` = ON (always enabled)

---

## 3) **Architecture**

### 3.1 High-level

**Stack:**
- **API:** FastAPI (Dockerized)
- **DB:** PostgreSQL (5+ tables, VIEWs, Alembic migrations)
- **Cache:** Redis (DNS/WHOIS/Provider/Scoring caching)
- **Background:** Celery workers + Beat scheduler
- **Deployment:** Docker/K8s ready
- **Logging:** JSON structured (PII masking)
- **Metrics:** Prometheus (basic)
- **Error Tracking:** Sentry

**API Versioning:**
- `/api/v1/` aktif
- Backward compatibility korundu (legacy endpoints)

### 3.2 Core Data Flow

```
Domain → Normalize → DNS/WHOIS → Provider → Scoring → Enrichment → Lead Object
```

**Pipeline Stages:**
1. **Ingestion:** Domain input (CSV, webhook, manual)
2. **Normalization:** Domain cleaning & validation
3. **Analysis:** DNS + WHOIS lookup
4. **Classification:** Provider mapping
5. **Scoring:** Rule-based scoring engine
6. **Enrichment:** IP enrichment (optional, feature flag)
7. **Storage:** Lead object creation/update

### 3.3 Adapter Architecture

**Core Freeze Protocol:**
- Core modüller **dokunulmaz** (CODEOWNERS, CI regression job, feature flags)
- Yeni entegrasyonlar **adapter pattern** ile (`app/integrations/`)
- Fiziksel ayrım: Core (`app/core/`) vs Integration (`app/integrations/`)

**Dokunulmaz Core Modüller:**
- `app/core/scorer.py`
- `app/core/analyzer_*.py` (analyzer_dns, analyzer_whois, analyzer_enrichment)
- `app/core/normalizer.py`
- `app/core/provider_map.py`
- `app/core/priority.py`
- `app/core/sales_engine.py`
- `app/core/enrichment*.py`
- `app/core/ip_enrichment/`
- `tests/test_scorer_*.py`
- `tests/test_regression_dataset.py`
- `tests/test_sales_*.py`

**Integration Modules:**
- `app/integrations/d365/` - D365 adapter
- `app/core/partner_center.py` - Partner Center adapter
- `app/core/referral_ingestion.py` - Partner Center sync logic

### 3.4 Database Schema

**Core Tables:**
- `raw_leads` - Raw ingested data
- `companies` - Normalized company information (domain unique)
- `domain_signals` - DNS/WHOIS signals
- `lead_scores` - Scoring results (readiness_score, segment, priority_score)
- `provider_change_history` - Provider change tracking
- `ip_enrichment` - IP enrichment data (optional)

**Views:**
- `leads_ready` - Main lead view (JOIN of companies + domain_signals + lead_scores)

**Migrations:**
- Alembic migrations (`alembic/versions/`)
- Schema versioning
- ⚠️ **DEPRECATED:** `app/db/schema.sql` (outdated, missing G20 columns)

---

## 4) **Data Model & Lead Schema**

### 4.1 Hunter → D365 Lead Schema (24 Custom Fields)

**Publisher Prefix:** `hnt_` (confirmed from D365 Power Apps interface)

#### 4.1.1 Hunter Intelligence Fields (7 fields)

| Display Name | Logical Name | Data Type | Description | Source Field (Hunter) |
|-------------|--------------|-----------|-------------|---------------------|
| Hunter Final Score | `hnt_finalscore` | Whole Number | 0–100 arası final skor | `readiness_score` |
| Hunter Priority Score | `hnt_priorityscore` | Whole Number | İç öncelik skoru (1-7) | `priority_score` |
| Hunter Segment | `hnt_segment` | Choice (Option Set) | Migration/Existing/Cold/Skip | `segment` |
| Hunter Provider | `hnt_provider` | Single Line of Text | Provider name (M365, Google, etc.) | `provider` |
| Hunter Tenant Size | `hnt_huntertenantsize` | Choice (Option Set) | Small/Medium/Large | `tenant_size` |
| Hunter Infrastructure Summary | `hnt_infrasummary` | Multiple Lines of Text | Altyapı analizi özeti | `infrastructure_summary` |
| Hunter Confidence | `hnt_confidence` | Decimal | Skor güven seviyesi | Calculated |

#### 4.1.2 Partner Center Fields (6 fields)

| Display Name | Logical Name | Data Type | Description | Source Field (Hunter) |
|-------------|--------------|-----------|-------------|---------------------|
| Hunter Referral ID | `hnt_referralid` | Single Line of Text | PC referral kaydının ID'si | `referral_id` |
| Hunter Referral Type | `hnt_referraltype` | Choice (Option Set) | Co-sell, marketplace, solution workspace | `referral_type` |
| Hunter Tenant ID | `hnt_tenantid` | Single Line of Text | Azure Tenant GUID | `azure_tenant_id` |
| Hunter Source | `hnt_source` | Choice (Option Set) | Partner Center, Manual, Import | Calculated |
| Hunter M365 Fit Score | `hnt_m365fitscore` | Whole Number | M365 uyumluluk skoru | `readiness_score` (if provider == "M365") |
| Hunter M365 Match Tags | `hnt_m365matchtags` | Multiple Lines of Text | M365 workload eşleşme tagleri | None (Post-MVP) |

#### 4.1.3 Sync & Operations Fields (6 fields)

| Display Name | Logical Name | Data Type | Description | Source Field (Hunter) |
|-------------|--------------|-----------|-------------|---------------------|
| D365 Lead ID | `hnt_d365leadid` | Single Line of Text | D365 lead referansı | D365 Lead GUID |
| Hunter Last Sync Time | `hnt_lastsynctime` | Date and Time | Son sync timestamp | `d365_sync_last_at` |
| Hunter Sync Attempt Count | `hnt_syncattemptcount` | Whole Number | Sync deneme sayısı | `d365_sync_attempt_count` |
| Hunter Processing Status | `hnt_processingstatus` | Choice (Option Set) | Idle, Working, Completed, Error | `d365_sync_status` (mapped) |
| Hunter Sync Error Message | `hnt_syncerrormessage` | Multiple Lines of Text | Son hata mesajı | `d365_sync_error` |
| Hunter Push Status | `hnt_pushstatus` | Choice (Option Set) | Synced, Not Synced, Error | Calculated |

#### 4.1.4 Advanced Debug Fields (5 fields - Technical Only)

| Display Name | Logical Name | Data Type | Description | Source Field (Hunter) |
|-------------|--------------|-----------|-------------|---------------------|
| Hunter AutoScore Version | `hnt_HunterAutoScoreVersi...` | Single Line of Text | Scoring engine versiyonu | Version string |
| Hunter Domain | `hnt_domain` | Single Line of Text | Analiz edilen domain | `domain` |
| Hunter Is Re-Enriched | `hnt_isreenriched` | Yes/No (Boolean) | Tekrar enrich edildi mi? | Calculated |
| Hunter ML Weight JSON | `hnt_HunterMLWeightJSON` | Multiple Lines of Text | ML ağırlıklarının JSON'ı | ML weights JSON |
| Hunter Intelligence JSON | `hnt_intelligencejson` | Multiple Lines of Text | Tam ham JSON payload | Full lead JSON |

**Total Custom Fields:** 24 (confirmed in D365)

**Missing Fields (Post-MVP):**
- `hnt_prioritycategory` (priority_category)
- `hnt_prioritylabel` (priority_label)
- `hnt_technicalheat` (technical_heat)
- `hnt_commercialsegment` (commercial_segment)
- `hnt_commercialheat` (commercial_heat)
- `hnt_ispartnercenterreferral` (calculated from `hnt_referralid`)

### 4.2 Field Mapping Reference

**File:** `app/integrations/d365/mapping.py`  
**Function:** `map_lead_to_d365(lead_data: Dict[str, Any])`

**Mapping Logic:**
- Uses logical names with `hnt_` prefix (confirmed from D365)
- Option Set values mapped to integers (see `D365-OPTION-SET-MAPPING.md`)
- Only includes fields that exist in D365 (24 fields, Post-MVP: 6 fields excluded)

---

## 5) **Intelligence Engine**

### 5.1 Signal Categories

**DNS Signals:**
- MX records (validity, count)
- SPF record (exists, policy)
- DKIM record (exists)
- DMARC record (policy: none/quarantine/reject, coverage)

**WHOIS Signals:**
- Registrar name
- Expiry date
- Nameserver list

**Provider Signals:**
- Provider classification (M365, Google, Local, etc.)
- Local provider detection (G20)
- Tenant size heuristic (G20)

**Risk Signals:**
- No SPF
- No DKIM
- DMARC none
- Domain expiry soon
- Multiple MX records (potential migration)

### 5.2 Scoring Components

**Rule-based Scoring (rules.json):**
- **Base Score:** Starting point (default: 0)
- **Provider Points:** Provider-specific bonuses
- **Signal Points:** SPF/DKIM/DMARC bonuses
- **Risk Points:** Negative penalties (no SPF, no DKIM, etc.)
- **Hard-fail Rules:** Skip segment (score = 0)

**Score Calculation:**
```
score = base_score + provider_points + signal_points + risk_points
score = max(0, min(100, score))  # Clamp to 0-100
```

**Caching:**
- Redis-based caching (1 hour TTL)
- Cache key: domain + provider + signals hash
- Cache miss: Full scoring calculation

### 5.3 Segment Types

**Migration:**
- Provider != M365
- Score >= threshold
- High priority (priority_score = 1-3)

**Existing:**
- Provider == M365
- Score >= threshold
- Medium priority (priority_score = 4-5)

**Cold:**
- Low score
- No clear migration signal
- Low priority (priority_score = 6-7)

**Skip:**
- Hard-fail conditions (invalid domain, no MX, etc.)
- Score = 0
- Priority = 7

### 5.4 CSP P-Model Fields (Phase 2)

**Technical Heat:**
- `Hot` - Migration segment, high score
- `Warm` - Existing segment, medium score
- `Cold` - Cold segment, low score

**Commercial Segment:**
- `GREENFIELD` - Migration opportunity
- `COMPETITIVE` - Existing customer, competitive
- `WEAK_PARTNER` - Existing customer, weak partner
- `RENEWAL` - Existing customer, renewal opportunity
- `LOW_INTENT` - Low interest
- `NO_GO` - Not a target

**Commercial Heat:**
- `HIGH` - High commercial potential
- `MEDIUM` - Medium commercial potential
- `LOW` - Low commercial potential

**Priority Category:**
- `P1` - Highest priority
- `P2` - High priority
- `P3` - Medium-high priority
- `P4` - Medium priority
- `P5` - Low-medium priority
- `P6` - Low priority

**Priority Label:**
- Human-readable label (e.g., "High Potential Greenfield")

### 5.5 Confidence Calculation

**Variance-based:**
- Signal completeness
- Domain stability
- Provider confidence
- Score variance

**Confidence Levels:**
- High (3.0+): Complete signals, stable domain
- Medium (2.0-3.0): Partial signals, some uncertainty
- Low (<2.0): Incomplete signals, high uncertainty

---

## 6) **Partner Center Integration**

### 6.1 Status

**Backend:** ✅ **COMPLETED** (2025-01-30)  
**UI:** ✅ **COMPLETED** (2025-01-30)  
**Background Sync:** ✅ **COMPLETED** (2025-01-30)  
**Feature Flag:** OFF (MVP-safe, default: false)

**Durum:** ✅ **Kod bazında DONE, ürün bazında yeterince iyi seviyesinde**

### 6.2 Pipeline

```
PC API → OAuth Client → Referral Ingestion → Lead Creation/Update → DB → UI Indicator → Sync Status
```

**Components:**
- `app/core/partner_center.py` - OAuth client (MSAL)
- `app/core/referral_ingestion.py` - Sync logic
- `app/core/tasks.py` - Celery task (`sync_partner_center_referrals_task`)
- `app/api/referrals.py` - Referral detail endpoint

### 6.3 Referral Aggregation

**Multi-referral Support:**
- `referral_count` - Number of referrals
- `referral_types[]` - Array of referral types
- `referral_ids[]` - Array of referral IDs
- Primary referral: First active referral

**Referral Types:**
- `co-sell` - Co-sell referral
- `marketplace` - Marketplace referral
- `solution-provider` - Solution provider referral

**Link Status:**
- `linked` - All referrals linked
- `unlinked` - All referrals unlinked
- `mixed` - Mixed status (multiple referrals)

### 6.4 Sync Configuration

**Celery Beat Schedule:**
- Production: 600s (10 minutes)
- Development: 30s (auto-override for testing)

**OAuth Configuration:**
- Client ID: `HUNTER_PARTNER_CENTER_CLIENT_ID`
- Tenant ID: `HUNTER_PARTNER_CENTER_TENANT_ID`
- Scope: `https://api.partner.microsoft.com/.default`
- Token Cache: `.token_cache` (optional)

**API Configuration:**
- API URL: `https://api.partnercenter.microsoft.com`
- API Version: `v1.0`
- Default Direction: `Incoming`
- Default Status: `Active`
- Default Top: `200`
- Max Pages: `0` (unlimited)

### 6.5 UI Integration

**Lead Table:**
- Referral column (badge: "PC Referral")
- Referral type filter
- Sync button (header)
- Sync status indicator (right-top)

**Referral Detail Modal:**
- Detay butonu (referral ID)
- Modal content (referral details)
- Action buttons:
  - Copy referral ID
  - Send to D365
  - Open in Partner Center

### 6.6 Productization & Production Enablement

**Phase 4-6: Productization** ✅ **COMPLETED** (2025-01-30):
- DB schema revision (referral aggregation fields)
- Filter rules (referral type, link status)
- Upsert strategy (idempotent domain-based)
- Summary logging (sync summary events)
- Comprehensive tests (50 tests passing)

**Phase 7: Production Enablement** ✅ **COMPLETED** (2025-01-30):
- Feature flag validation (OFF/ON behavior tested)
- Logging review (PII-free, JSON-safe)
- Metrics exposure (`/healthz/metrics` endpoint)
- Background sync enablement (Celery Beat schedule respects feature flag)
- Production checklist (`docs/reference/PARTNER-CENTER-PRODUCTION-CHECKLIST.md`)

**Test Coverage**: 59/59 passing (37 domain extraction + 7 Phase 4 + 6 client + 6 Phase 5/6 + 3 Phase 3.3 URL-based + 10 Phase 7)

### 6.7 Known Issues

**Post-MVP Enhancements:**
- Scoring pipeline'a Azure Tenant ID / Co-sell sinyali tam entegre değil
- Referral type bazlı scoring adjustment (future enhancement)

---

## 7) **Dynamics 365 Integration**

### 7.1 Status

**Backend:** ✅ **100% COMPLETED** (Phase 2.5 - 2025-01-30)  
**UI:** ✅ **COMPLETED** (Phase 3 - 2025-01-30)  
**E2E Tests:** ✅ **COMPLETED** (Phase 2.9 - 2025-01-30)  
**Feature Flag:** OFF (MVP-safe, default: false)

**Durum:** ✅ **HAMLE 2 COMPLETED** - Production-grade E2E testleri tamamlandı (3 senaryo), Go/No-Go: ✅ GO

**Note:** Backend %94 → %100 (Phase 2.9 E2E testleri ile eksik %6 tamamlandı)

### 7.2 Pipeline Plan

```
Hunter Lead → map_lead_to_d365() → POST Lead → Return leadID → Update sync fields
```

**Components:**
- `app/integrations/d365/client.py` - D365 Web API client
- `app/integrations/d365/mapping.py` - Hunter → D365 field mapping (24 fields)
- `app/integrations/d365/dto.py` - D365 data transfer objects
- `app/integrations/d365/errors.py` - D365-specific exceptions
- `app/tasks/d365_push.py` - Celery task (`push_lead_to_d365`)

### 7.3 Required Steps (E2E Runbook)

**1. Azure AD App Registration:**
- Create App Registration
- Configure API permissions (D365 Web API)
- Generate client secret

**2. D365 Application User:**
- Create Application User
- Assign security role (Sales Manager or custom role)
- Grant D365 API access

**3. Hunter Configuration:**
- Set `HUNTER_D365_ENABLED=true`
- Configure D365 credentials (`.env`):
  - `HUNTER_D365_BASE_URL`
  - `HUNTER_D365_CLIENT_ID`
  - `HUNTER_D365_CLIENT_SECRET`
  - `HUNTER_D365_TENANT_ID`
  - `HUNTER_D365_APP_ID` (optional, for generating lead URLs)

**4. Custom Fields:**
- Verify 24 custom Hunter fields exist in D365
- Check Option Set values (see `D365-OPTION-SET-MAPPING.md`)

**5. Testing:**
- Happy path test (create lead)
- Idempotency test (duplicate detection)
- Edge case test (error handling)

**Reference:** `docs/reference/D365-PHASE-2.9-E2E-RUNBOOK.md`

### 7.4 Field Mapping

**24 Custom Fields:**
- Hunter Intelligence (7 fields)
- Partner Center (6 fields)
- Sync & Operations (6 fields)
- Advanced Debug (5 fields)

**Option Set Mapping:**
- Segment: Hunter (Migration/Existing/Cold/Skip) vs D365 (SMB/MidMarket/Enterprise) - **MISMATCH** (currently excluded)
- Tenant Size: Small (816940000), Medium (816940001), Large (816940002), Enterprise (816940003)
- Source: Partner Center (816940000), Manual (816940001), Import (816940002), Other (816940003)
- Processing Status: Idle (816940000), Working (816940001), Completed (816940002), Error (816940003)

**Reference:** `docs/reference/D365-OPTION-SET-MAPPING.md`

### 7.5 Error Handling & Retry

**Error Categorization:**
- `auth` - Authentication errors (OAuth, token expiry)
- `rate_limit` - Rate limit errors (429)
- `validation` - Validation errors (400, 422)
- `network` - Network errors (timeout, connection)
- `unknown` - Unknown errors

**Retry Strategy:**
- Transient errors: Retry with exponential backoff
- Permanent errors: No retry, log to DLQ
- Max retries: 3
- Retry delay: 60s, 120s, 240s

**Manual Retry Endpoints:**
- `POST /api/v1/d365/retry/{lead_id}` - Retry single lead
- `POST /api/v1/d365/retry-bulk` - Retry bulk leads

**Metrics:**
- Retry attempt tracking
- Retry success/failure tracking
- DLQ tracking (max retry sonrası)

### 7.6 UI Integration

**Lead Table:**
- D365 badge (synced/not synced/error)
- D365 link (opens lead in D365)

**Lead Detail Modal:**
- D365 panel (sync status, lead ID, last sync time)
- "Push to Dynamics" button
- Error message display

**Push Status:**
- `synced` - Successfully pushed to D365
- `not_synced` - Not yet pushed
- `error` - Push failed (with error message)

### 7.7 Known Issues

**Post-MVP Fields (6 fields not in D365 yet):**
- `hnt_prioritycategory` (priority_category)
- `hnt_prioritylabel` (priority_label)
- `hnt_technicalheat` (technical_heat)
- `hnt_commercialsegment` (commercial_segment)
- `hnt_commercialheat` (commercial_heat)
- `hnt_ispartnercenterreferral` (calculated from `hnt_referralid`)

**Segment Mapping Mismatch:**
- Hunter segment (Migration/Existing/Cold/Skip) vs D365 segment (SMB/MidMarket/Enterprise)
- Currently excluded from mapping (returns None)
- TODO: Fix mapping or use different field

---

## 8) **API Contract**

### 8.1 Main Endpoints

**Health:**
- `GET /healthz` - Health check and database status
- `GET /healthz/live` - Liveness probe (Kubernetes/Docker)
- `GET /healthz/ready` - Readiness probe (checks database and Redis)
- `GET /healthz/startup` - Startup probe
- `GET /healthz/metrics` - Metrics endpoint (cache, rate limit, bulk operations, errors)

**Ingest:**
- `POST /api/v1/ingest/domain` - Ingest single domain
- `POST /api/v1/ingest/csv` - Ingest domains from CSV/Excel file
- `POST /api/v1/ingest/webhook` - Webhook ingestion (API key required)

**Scan:**
- `POST /api/v1/scan/domain` - Analyze single domain (DNS + WHOIS + scoring)
- `POST /api/v1/scan/bulk` - Create bulk scan job (async)
- `GET /api/v1/scan/bulk/{job_id}` - Get bulk scan progress
- `POST /api/v1/scan/{domain}/rescan` - Re-scan domain with change detection

**Leads:**
- `GET /api/v1/leads` - Query leads (filters, sorting, pagination, search)
- `GET /api/v1/leads/{domain}` - Get single lead details
- `GET /api/v1/leads/{domain}/sales-summary` - Get sales intelligence summary
- `GET /api/v1/leads/{domain}/score-breakdown` - Get detailed score breakdown
- `POST /api/v1/leads/{domain}/enrich` - Manually enrich lead with contact emails
- `GET /api/v1/leads/export` - Export leads to CSV/Excel
- `GET /api/v1/leads/{domain}/summary.pdf` - Generate PDF account summary

**Dashboard:**
- `GET /api/v1/dashboard` - Get aggregated dashboard statistics (legacy)
- `GET /api/v1/dashboard/kpis` - Get dashboard KPIs (lightweight)

**Partner Center:**
- `POST /api/v1/partner-center/sync` - Manual sync Partner Center referrals
- `GET /api/v1/partner-center/referrals/{referral_id}` - Get single referral detail

**Dynamics 365:**
- `POST /api/v1/d365/push-lead` - Push lead to D365 (async)
- `POST /api/v1/d365/retry/{lead_id}` - Retry single lead push
- `POST /api/v1/d365/retry-bulk` - Retry bulk lead pushes

**Debug:**
- `GET /debug/ip-enrichment/{ip}` - Debug IP enrichment (internal/admin use)
- `GET /debug/ip-enrichment/config` - Check IP enrichment configuration status

**Interactive API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### 8.2 Response Contracts

**Lead Model:**
```json
{
  "company_id": 1,
  "canonical_name": "Example Inc",
  "domain": "example.com",
  "provider": "M365",
  "tenant_size": "medium",
  "readiness_score": 85,
  "segment": "Existing",
  "priority_score": 4,
  "technical_heat": "Warm",
  "commercial_segment": "RENEWAL",
  "commercial_heat": "MEDIUM",
  "priority_category": "P4",
  "priority_label": "Medium Priority Renewal",
  "infrastructure_summary": "IP enrichment summary",
  "referral_id": "abc123",
  "referral_type": "co-sell",
  "d365_sync_status": "synced",
  "d365_lead_id": "xyz789",
  "d365_lead_url": "https://...",
  ...
}
```

**Sales Summary Model:**
```json
{
  "one_liner": "M365 existing customer, renewal opportunity",
  "call_script": "...",
  "discovery_questions": ["...", "..."],
  "offer_tier": "Enterprise",
  "opportunity_potential": 85,
  "urgency": "Medium"
}
```

**Referral Model:**
```json
{
  "referral_id": "abc123",
  "referral_type": "co-sell",
  "azure_tenant_id": "xyz789",
  "link_status": "linked",
  "status": "Active",
  "direction": "Incoming",
  ...
}
```

### 8.3 Error Responses

**Standard Error Format:**
```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "code": "ERROR_CODE"
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `409` - Conflict (duplicate)
- `429` - Rate Limited
- `500` - Internal Server Error
- `503` - Service Unavailable

---

## 9) **UI Contract**

### 9.1 Lead Table

**Columns:**
- Domain
- Company Name
- Provider (badge)
- Segment (badge: Migration/Existing/Cold/Skip)
- Score (0-100)
- Priority Score (1-7)
- PC Referral (badge: "PC Referral" if referral_id exists)
- D365 Sync (badge: synced/not synced/error)
- Actions (View Details, Push to D365)

**Filters:**
- Segment (Migration, Existing, Cold, Skip)
- Provider (M365, Google, Local, etc.)
- Score range (min-max)
- Priority Score (1-7)
- Referral Type (co-sell, marketplace, solution-provider)
- D365 Sync Status (synced, not_synced, error)

**Sorting:**
- Default: Priority Score (ascending)
- Options: Score, Priority Score, Domain, Company Name

**Pagination:**
- Default: 50 per page
- Options: 25, 50, 100, 200

**Search:**
- Full-text search (domain, company name)

### 9.2 Modals

**Score Breakdown Modal:**
- Detailed score analysis
- Signal/risk display order: SPF → DKIM → DMARC → Risks
- IP enrichment display: Network & Location section
- Tooltips for signals and risks

**Lead Detail Modal:**
- Full lead information
- Score breakdown
- Partner Center referral details (if exists)
- D365 sync status panel
- Action buttons (Push to D365, Export, etc.)

**Referral Detail Modal:**
- Referral information (ID, type, status, etc.)
- Action buttons:
  - Copy referral ID
  - Send to D365
  - Open in Partner Center

### 9.3 Dashboard

**KPI Cards:**
- Total Leads
- Migration Leads
- High Priority Leads
- PC Referrals
- D365 Synced Leads

**Charts (Future):**
- Segment distribution
- Provider distribution
- Score distribution
- Trend analysis

### 9.4 Export

**Formats:**
- CSV
- Excel (XLSX)

**Options:**
- Export with filters
- Export selected leads
- Export all leads

### 9.5 UI Status

**Current State:**
- ✅ **Functional** - All features working
- ⚠️ **Esthetic** - Design system implemented (spacing, colors, buttons, loading states, error states, success feedback)
- ⏳ **Polish Pending** - UI Polish (Hamle 3) - Table view, modal, button, color scheme, typography, spacing/layout improvements

**Design System:**
- Spacing: 4px grid (xs: 4px, sm: 8px, md: 16px, lg: 24px, xl: 32px)
- Colors: Primary, Secondary, Success, Error, Warning
- Buttons: Primary, Secondary, Success, Error variants
- Loading: Spinner, skeleton loading animations
- Error: Error message styling
- Success: Toast notification animations

---

## 10) **Background Jobs**

### 10.1 Celery Configuration

**Broker:** Redis  
**Backend:** Redis  
**Task Serialization:** JSON  
**Timezone:** UTC

**Task Limits:**
- Time limit: 900s (15 minutes)
- Soft time limit: 870s (14.5 minutes)
- Max retries: 2 (for transient failures)
- Retry delay: 60s (exponential backoff)

**Worker Configuration:**
- Prefetch multiplier: 1 (disable prefetching for better load balancing)
- Max tasks per child: 50 (restart worker after 50 tasks for memory management)
- Task acks late: True (acknowledge tasks after completion)
- Task reject on worker lost: True (reject tasks if worker dies)

### 10.2 Scheduled Tasks (Celery Beat)

**Daily Rescan:**
- Task: `app.core.tasks.daily_rescan_task`
- Schedule: 86400s (24 hours)
- Purpose: Rescan all domains, detect changes, generate alerts

**Process Pending Alerts:**
- Task: `app.core.tasks.process_pending_alerts_task`
- Schedule: 300s (5 minutes)
- Purpose: Process pending alerts, send notifications

**Sync Partner Center Referrals:**
- Task: `app.core.tasks.sync_partner_center_referrals_task`
- Schedule: 600s (10 minutes) - Production, 30s - Development
- Purpose: Sync Partner Center referrals, create/update leads

### 10.3 Async Tasks

**Bulk Scan:**
- Task: `app.core.tasks.bulk_scan_task`
- Purpose: Process bulk scan job (batch processing)
- Rate Limiting: DNS (10 req/s), WHOIS (5 req/s) per worker
- Progress Tracking: Job ID, progress percentage, status

**D365 Push:**
- Task: `app.tasks.d365_push.push_lead_to_d365`
- Purpose: Push lead to D365 (async)
- Retry: Automatic retry with exponential backoff
- Error Handling: Categorization, DLQ tracking

**ReScan:**
- Task: `app.core.tasks.rescan_domain_task`
- Purpose: Re-scan domain with change detection
- Change Detection: Provider change, signal change, score change
- Alert Generation: Automatic alert creation for detected changes

### 10.4 Progress Tracking

**Job Status:**
- `pending` - Job created, waiting for processing
- `in_progress` - Job being processed
- `completed` - Job completed successfully
- `failed` - Job failed
- `cancelled` - Job cancelled

**Progress API:**
- `GET /api/v1/jobs/{job_id}` - Get job progress
- `GET /api/v1/jobs/{job_id}/results` - Get job results (completed jobs)

---

## 11) **Feature Flags**

### 11.1 Current Flags

**Partner Center Integration:**
- Flag: `HUNTER_PARTNER_CENTER_ENABLED`
- Default: `false` (MVP-safe)
- Status: ✅ Backend completed, UI completed, feature flag OFF
- Activation: Set `HUNTER_PARTNER_CENTER_ENABLED=true` in `.env`
- **UAT Profile Note:** UAT ortamında `HUNTER_PARTNER_CENTER_ENABLED=true`, `HUNTER_D365_ENABLED=true` olarak ayarlanabilir. Production'da default değerler (`false`) korunur.

**Dynamics 365 Integration:**
- Flag: `HUNTER_D365_ENABLED`
- Default: `false` (MVP-safe)
- Status: ✅ Backend 94% completed, UI completed, E2E tests completed, feature flag OFF
- Activation: Set `HUNTER_D365_ENABLED=true` in `.env`
- **UAT Profile Note:** UAT ortamında `HUNTER_PARTNER_CENTER_ENABLED=true`, `HUNTER_D365_ENABLED=true` olarak ayarlanabilir. Production'da default değerler (`false`) korunur.

**IP Enrichment:**
- Flag: `HUNTER_ENRICHMENT_ENABLED`
- Default: `false`
- Status: ✅ **PRODUCTION ACTIVE** (2025-01-28)
- Activation: Set `HUNTER_ENRICHMENT_ENABLED=true` in `.env` + configure DB paths

**Sales Engine:**
- Flag: `HUNTER_SALES_ENGINE_ENABLED`
- Default: Always enabled (no flag)
- Status: ✅ Always active

### 11.2 Flag Configuration

**Environment Variables:**
```bash
# Partner Center
HUNTER_PARTNER_CENTER_ENABLED=false
HUNTER_PARTNER_CENTER_CLIENT_ID=...
HUNTER_PARTNER_CENTER_TENANT_ID=...
HUNTER_PARTNER_CENTER_SYNC_INTERVAL=600

# Dynamics 365
HUNTER_D365_ENABLED=false
HUNTER_D365_BASE_URL=...
HUNTER_D365_CLIENT_ID=...
HUNTER_D365_CLIENT_SECRET=...
HUNTER_D365_TENANT_ID=...

# IP Enrichment
HUNTER_ENRICHMENT_ENABLED=true
MAXMIND_CITY_DB=...
IP2LOCATION_DB=...
IP2PROXY_DB=...
```

**Code Location:**
- `app/config.py` - Settings class with feature flags
- Feature flag checks in API endpoints and tasks

### 11.3 Safety-First Rollout

**Strategy:**
- All new integrations behind feature flags
- Default: `false` (MVP-safe)
- Gradual rollout: Dev → Staging → Production
- Monitoring: Error tracking, metrics, logs

**Activation Checklist:**
1. Verify backend implementation complete
2. Verify UI integration complete
3. Verify tests passing
4. Verify credentials configured
5. Set feature flag to `true`
6. Monitor for errors
7. Rollback if issues detected

---

## 12) **Operational Standards**

### 12.1 Deployment Checklist

**Pre-Deployment:**
- [ ] Environment variables configured
- [ ] Database migrations applied (`alembic upgrade head`)
- [ ] Database backup created
- [ ] Feature flags configured
- [ ] Credentials verified (OAuth, API keys)
- [ ] Health probes configured
- [ ] Monitoring configured (Sentry, metrics)
- [ ] Smoke tests prepared

**UAT Pre-Deployment (UAT Round için ek adımlar):**
- [ ] `scripts/sales_fresh_reset.sh` çalıştırıldı (tam sıfırlanmış demo ortamı)
- [ ] `scripts/sales_health_check.sh` temiz (API/DB/Redis ok)
- [ ] `.env` checker çalıştırıldı → tüm zorunlu değişkenler OK, Partner Center & D365 flag'leri istenen profilde
- [ ] UAT bugfix branch açıldı (örn. `bugfix/uat-2025-01-30`) ve baseline tag'lendi

**Deployment:**
- [ ] Docker images built
- [ ] Containers started
- [ ] Health checks passing (`/healthz/ready`)
- [ ] Smoke tests executed
- [ ] Safe mode rollout (feature flags OFF initially)

**Post-Deployment:**
- [ ] Monitor error logs
- [ ] Monitor metrics (cache hit rate, API latency, error rate)
- [ ] Verify background jobs running
- [ ] Verify API endpoints responding
- [ ] Verify UI accessible

**Reference:** `docs/reference/PRODUCTION-DEPLOYMENT-GUIDE.md`

### 12.2 Monitoring

**Prometheus Metrics:**
- Cache metrics (hits, misses, hit rate)
- Rate limit metrics (hits, acquired, circuit breaker state)
- Bulk operations metrics (batch success/failure, processing time, deadlock count)
- Error metrics (total errors, errors by component, error trends)

**Sentry Error Tracking:**
- Error categorization
- Stack traces
- Context (request ID, user, environment)
- PII masking (email, company_name)

**Health Probes:**
- `/healthz/live` - Liveness probe (Kubernetes/Docker)
- `/healthz/ready` - Readiness probe (checks database and Redis)
- `/healthz/startup` - Startup probe

**Logging:**
- Structured logging (JSON)
- Log levels: DEBUG (dev), INFO (prod)
- PII masking (email, company_name)
- Request ID tracking

### 12.3 Backup & Recovery

**Database Backup:**
- Daily backups (automated)
- Backup retention: 30 days
- Backup location: Secure storage

**Recovery Procedure:**
1. Stop application
2. Restore database from backup
3. Run migrations if needed (`alembic upgrade head`)
4. Verify data integrity
5. Start application
6. Monitor for errors

**Reference:** `docs/reference/PRODUCTION-DEPLOYMENT-GUIDE.md` - Backup & Recovery section

### 12.4 Performance Standards

**API Response Times:**
- Health check: <100ms
- Lead query: <1s
- Single domain scan: <15s (DNS + WHOIS)
- Bulk scan: Async (progress tracking)

**Database:**
- Connection pool: 20 (default), 50 (production)
- Max overflow: 10 (default), 20 (production)
- Query optimization: N+1 prevention, eager loading

**Caching:**
- DNS/WHOIS: 1 hour TTL
- Scoring: 1 hour TTL
- IP Enrichment: 24 hour TTL

**Rate Limiting:**
- DNS: 10 req/s per worker
- WHOIS: 5 req/s per worker
- API: Distributed rate limiting (Redis-based)

---

## 13) **Roadmap (G21)**

### 13.1 Completed Phases

**Phase 0: Preparation & Inventory** ✅
- Endpoint inventory
- CRM-lite feature identification
- UI/Backend/DB dependency mapping

**Phase 1: Deprecation Plan & Flags** ✅
- Feature flag infrastructure
- Deprecated endpoint tagging
- Logging warnings

**Phase 2: Sales Engine Layer** ✅
- Sales summary endpoint (`/api/v1/leads/{domain}/sales-summary`)
- Sales intelligence logic (one-liner, call script, discovery questions, offer tier, opportunity potential)

**Phase 3: Read-Only Mode for Deprecated** ✅
- Notes/Tags/Favorites write endpoints: 410 Gone
- Read endpoints: Migration support only
- UI CRM-lite actions removed

**Integration Roadmap Phase 2: Partner Center** ✅
- Backend: API client, referral ingestion, sync endpoint, Celery task
- UI: Referral column, referral type filter, sync button, sync status indicator, referral detail modal
- Background sync: Celery Beat schedule (10 min prod, 30s dev)
- Status: ✅ **COMPLETED** (2025-01-30) - Kod bazında DONE, ürün bazında yeterince iyi

**Integration Roadmap Phase 3: Dynamics 365** ✅
- Backend: D365 client, mapping (24 fields), push logic, retry mechanism
- UI: D365 badge, push button, lead detail modal D365 panel
- E2E Tests: Happy path, Idempotency, Edge case (3 senaryo)
- Status: ✅ **COMPLETED** (2025-01-30) - Production-grade E2E testleri tamamlandı, Go/No-Go: ✅ GO

### 13.2 Pending Phases

**Phase 4: Dynamics Migration** ⏸ **PAUSED**
- Overlaps with Integration Roadmap Phase 3
- Status: Integration Roadmap Phase 3 completed, Phase 4 paused

**Phase 5: Monitoring & Stabilization** ◻ **PARTIAL**
- Current: Sentry, structured logging, health probes, basic metrics
- Pending: Detailed service-level metrics, Hunter-specific KPIs, alerting rules

**Phase 6: Cleanup & Hard Cut** ◻ **OPEN**
- Remove deprecated endpoints
- Remove deprecated DB fields/tables
- Clean up code/documentation references
- Timing: After Dynamics integration and migration complete

### 13.3 Post-MVP Enhancements

**Partner Center:**
- Scoring pipeline integration (Azure Tenant ID, Co-sell boost)
- Referral type bazlı scoring adjustment

**Dynamics 365:**
- Post-MVP fields (6 fields) - D365'te oluşturulacak
- Option Set value verification (D365'teki gerçek value'lar)
- Bulk push endpoint
- Push status dashboard
- Push history/audit log

**UI Polish (Hamle 3):**
- Table view estetik iyileştirmeleri
- Modal'lar estetik iyileştirmeleri
- Button'lar estetik iyileştirmeleri
- Color scheme iyileştirmeleri
- Typography iyileştirmeleri
- Spacing/layout iyileştirmeleri

**Code Quality:**
- N+1 Query Prevention (eager loading, VIEW optimization)
- Sync-First Refactor (async → sync where appropriate)
- Repository/Service Layer (code organization)

**Reference:** `docs/active/G21-ROADMAP-CURRENT.md`

---

## 14) **Known Issues / Open Decisions**

### 14.1 Known Issues

**Leads 500 Bug Fix** ✅ **FIXED** (2025-01-30):
- **Problem**: `GET /api/v1/leads` endpoint 500 Internal Server Error
- **Root Cause**: `referral_type` parametresi `get_leads_v1` fonksiyonunda eksikti
- **Fix**: `referral_type` parametresi eklendi ve `get_leads` çağrısına geçirildi
- **Status**: ✅ **FIXED** - Production deployment için hazır
- **Reference**: `docs/active/LEADS-500-BUG-FIX.md`

**D365 Segment Mapping Mismatch:**
- Hunter segment (Migration/Existing/Cold/Skip) vs D365 segment (SMB/MidMarket/Enterprise)
- Currently excluded from mapping (returns None)
- TODO: Fix mapping or use different field

**D365 Post-MVP Fields:**
- 6 fields not in D365 yet (priority_category, priority_label, technical_heat, commercial_segment, commercial_heat, is_partner_center_referral)
- Action: Create fields in D365, add to mapping

**Partner Center Scoring Integration:**
- Azure Tenant ID / Co-sell sinyali scoring pipeline'a tam entegre değil
- Action: Future enhancement

**UI Esthetic:**
- UI çalışıyor ama estetik iyileştirme gerekiyor (Hamle 3: UI Polish)
- Action: Post-MVP enhancement

**N+1 Query Prevention:**
- Potential N+1 queries in `leads_ready` VIEW
- Action: Eager loading, VIEW optimization (P2 backlog)

### 14.2 Open Decisions

**CRM-lite Migration Path:**
- Notes/Tags/Favorites → D365 migration path needed
- Current: Read-only mode, migration support only

**Advanced Debug Tab:**
- Advanced Debug tab gelişecek (future enhancement)
- Current: Basic debug fields in D365

**Segment Field Usage:**
- Hunter segment vs D365 segment mismatch
- Decision: Exclude from mapping or create new field?

**Option Set Value Verification:**
- D365 Option Set values need verification (actual values from D365)
- Current: Default values used (0, 1, 2, 3)
- Action: Verify from D365 Power Apps interface

**Repository/Service Layer:**
- Current: Direct DB access
- Decision: Add repository/service layer for code organization?
- Priority: P2 backlog

### 14.3 Technical Debt

**Legacy SQL Migrations:**
- `app/db/migrations/legacy/*.sql` files deprecated
- Location: Moved to `docs/archive/legacy-migrations/` (historical reference only)
- Official way: Alembic migrations (`alembic/versions/`)

**Schema.sql Deprecated:**
- `app/db/schema.sql` is outdated (missing G20 columns, P-Model columns)
- Official way: Use `./scripts/reset_db_with_alembic.sh` or `Base.metadata.create_all()` + Alembic stamp

**Sync-First Refactor:**
- Some async functions could be sync (unnecessary async)
- Action: Post-MVP refactor (P2 backlog)

---

## 15) **Version History**

### v1.0.0 (2025-01-30)

**Initial Release:**
- ✅ Core engine production-ready (497 tests, 0 failures)
- ✅ Sales Intelligence layer (Phase 2)
- ✅ Partner Center integration (backend + UI, feature flag OFF)
- ✅ Dynamics 365 integration (backend 94% + UI + E2E tests, feature flag OFF)
- ✅ IP Enrichment (production active)
- ✅ Core Freeze protocol active
- ✅ G21 Phase 0-3 completed
- ✅ Integration Roadmap Phase 2-3 completed

**Key Features:**
- DNS/WHOIS analysis
- Rule-based scoring engine
- Provider mapping
- Sales intelligence (one-liner, call script, discovery questions)
- Partner Center referral sync
- Dynamics 365 lead push
- IP enrichment (MaxMind, IP2Location, IP2Proxy)
- Background jobs (Celery + Redis)
- Mini UI (lead table, score breakdown, export)

**Known Limitations:**
- UI esthetic improvements pending (Hamle 3)
- D365 segment mapping mismatch
- D365 post-MVP fields (6 fields) not in D365 yet
- Partner Center scoring integration incomplete

---

## 📝 **Document Maintenance**

**Update Frequency:**
- Major releases: Full update
- Feature additions: Delta update (relevant sections only)
- Bug fixes: Delta update (relevant sections only)

**Delta Update Format:**
- Add new sections as needed
- Update existing sections with new information
- Keep version history updated
- Archive old versions to `docs/archive/`

**Ownership:**
- Owner: Bered
- Reviewers: Core team
- Last Review: 2025-01-30

---

**End of HUNTER-CONTEXT-PACK v1.0**

