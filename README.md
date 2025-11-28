# Dyn365Hunter MVP

Lead intelligence engine for domain-based analysis and rule-based scoring.

[![CI/CD Pipeline](https://github.com/brdfb/dyn365hunterv3/actions/workflows/ci.yml/badge.svg)](https://github.com/brdfb/dyn365hunterv3/actions/workflows/ci.yml)
[![Code Quality](https://github.com/brdfb/dyn365hunterv3/actions/workflows/lint.yml/badge.svg)](https://github.com/brdfb/dyn365hunterv3/actions/workflows/lint.yml)

## Overview

Dyn365Hunter MVP is a FastAPI-based application that analyzes domains for lead intelligence. It performs DNS/WHOIS analysis and applies rule-based scoring to identify potential migration opportunities.

**Target**: ≤2 minute "kahvelik" analysis flow for sales team.

## 🚀 Production Status

**Hunter v1.1 is production-ready** (2025-01-29) - ✅ **DONE & PROD-READY**

- ✅ **P0 Hardening**: Completed (G19)
- ✅ **P1 Performance**: Completed (2025-01-28)
- ✅ **Stabilization Sprint**: Completed (3 days)
- ✅ **Sales Engine**: Completed (G21 Phase 2) + **v1.1 Intelligence Layer** (2025-01-29) - ✅ DONE & PROD-READY
- ✅ **CSP P-Model Integration**: Completed (2025-01-29) - ✅ DONE & PROD-READY
- ✅ **Production Bug Fixes**: Completed (2025-01-29) - ✅ DONE & PROD-READY
- ✅ **Read-Only Mode**: Completed (G21 Phase 3)

**Production Deployment**:
- 📋 [Production Readiness Checklist](docs/active/PRODUCTION-READINESS-CHECKLIST-2025-01-29.md) - **CSP P-Model + Sales Summary v1.1 Pre-Production Checklist**
- 📋 [Production Deployment Guide](docs/reference/PRODUCTION-DEPLOYMENT-GUIDE.md) - **Includes Script Safety Guards** (2025-01-30)
- 📋 [Production Deployment Checklist](docs/reference/PRODUCTION-DEPLOYMENT-CHECKLIST.md)
- 📋 [Smoke Tests Runbook](docs/reference/SMOKE-TESTS-RUNBOOK.md)
- 📋 [Troubleshooting Guide](docs/reference/TROUBLESHOOTING-GUIDE.md)

**Script Safety** (2025-01-30):
- 🔒 **Production Reset Protection**: `reset_db_with_alembic.sh` blocks production database resets (requires `FORCE_PRODUCTION_RESET=yes`)
- 🔒 **Production Deployment Guards**: `deploy_production.sh` requires `FORCE_PRODUCTION=yes` for production deployments
- 🔒 **Backup Integrity Check**: Automatic backup validation before deployment
- 📝 **Script Logging**: Critical scripts log to `./logs/scripts/` for audit trail

**D365 Integration Status** (2025-01-30):
- ✅ **D365 Lead Push PoC**: Completed - Hunter → D365 Lead Push working
  - End-to-end flow: API endpoint → Celery task → D365 API → Database sync
  - 8 fields successfully pushed (3 core + 5 custom Hunter fields)
  - Option Set value mapping implemented (string → integer)
  - Error handling, retry logic, and logging validated
  - **Reference**: `docs/archive/2025-01-30-D365-PUSH-POC-TASK-LIST.md`
- ✅ **HAMLE 2: D365 Phase 2.9 E2E Wiring** (2025-01-30) - ✅ **DEV TESTS COMPLETED**
  - Azure AD App Registration completed
  - D365 Application User created with security roles
  - Hunter configuration completed (D365 env vars set)
  - E2E Tests: Happy path ✅, Idempotency ✅, Edge case ✅ (all bugs fixed)
  - UI Badge & Link: Badge görünüyor ✅, D365 link çalışıyor ✅
  - Error Handling: Authentication error tested ✅, Rate limit & API error code verified ✅
  - **Go/No-Go Decision**: ✅ GO (production'a geçiş için hazır)
  - **Documentation**: `docs/active/HAMLE-2-EXECUTION-CHECKLIST.md`, `HAMLE-2-E2E-TEST-RESULTS.md`, `HAMLE-2-ERROR-HANDLING-TEST-RESULTS.md`, `HAMLE-2-UI-BADGE-LINK-TEST.md`, `HAMLE-2-GO-NOGO-DECISION.md`

**Post-MVP Roadmap**:
- 🅿️ **Partner Center Integration** (Phase 2) - Parked (Post-MVP)
- 🔄 **Dynamics 365 Integration** (Phase 3) - PoC Complete, Production Integration Pending
- 🔄 **G21 Phase 4-6** - Architecture refactor continuation (Post-MVP)

---

## Recent Updates (Last 6 Months)

**Unreleased** (2025-01-29):
- **CSP P-Model Integration + Sales Summary v1.1** (✅ **DONE & PROD-READY** - Production v1.1 Core Feature)
  - **CSP P-Model Integration**: Global CSP Priority Model (P1-P6) implementation
  - Commercial Segment & Heat: 6 commercial segments (GREENFIELD, COMPETITIVE, WEAK_PARTNER, RENEWAL, LOW_INTENT, NO_GO)
  - Technical Heat: Hot/Warm/Cold classification based on technical segment and provider
  - Priority Category (P1-P6): CSP-standard priority categories with human-readable labels
  - Rule-based architecture: All rules in `app/data/rules.json` (maintainable, configurable)
  - Database: New columns in `lead_scores` table, Alembic migration completed
  - API: New fields in `LeadResponse` and `ScoreBreakdownResponse` models (backward compatible)
  - UI: P1-P6 badge'leri (renk kodlu), priority_label tooltip'leri, score breakdown modalında P-model paneli
  - Status: ✅ **Phase 1 (Core Logic) + Phase 2 (DB + API) + Phase 3 (UI) completed** - Production v1.1 Core Feature
  - Post-MVP: Filtering & sorting (priority_category, commercial_segment) - İleride eklenecek
- **Bug Fixes** (2025-01-29) - Fixed 3 critical bugs for data consistency and accuracy
  - **DMARC Coverage Bug**: Fixed DMARC coverage inconsistency (was showing 100% when no DMARC record exists, now correctly returns `null`)
  - **Risk Summary Text**: Fixed contradictory risk summary text (now correctly states "SPF ve DKIM mevcut" when both are present)
  - **Score Modal Description**: Made score breakdown modal description provider-specific (M365, Google, Local/Hosting)
  - Files: `app/core/analyzer_dns.py`, `app/core/sales_engine.py`, `app/core/rescan.py`, `mini-ui/js/ui-leads.js`
  - Status: ✅ **All bugs fixed and verified** - All tests passing, data consistency verified
  - Documentation: `docs/active/CSP-COMMERCIAL-SEGMENT-DESIGN.md`, `docs/archive/2025-01-29-CSP-P-MODEL-IMPLEMENTATION-PLAN.md`

**Unreleased** (2025-01-28):
- **Sales Documentation Consistency** (✅ Completed) - Documentation cleanup and standardization
  - Kanonik Segment-Priority Matrisi added (single source of truth)
  - Cross-references added across all sales documentation
  - v1.0 (MVP) vs v2.0 (Target) distinction clarified
  - Tuning Factor status documented (design-only, not in production UI)
- **Partner Center Integration - Phase 2** (✅ Complete - Production-ready) - Partner Center referral ingestion and lifecycle tracking
  - Core components completed: API client (MSAL + Device Code Flow), database model, referral ingestion pipeline
  - Backend: API endpoints (`POST /api/referrals/sync`), Celery task, comprehensive testing (59/59 tests passing)
  - UI: Referral column in leads table with badge colors (co-sell: blue, marketplace: green, solution-provider: orange)
  - **UI Integration Complete** (2025-01-30): Referral type filter, sync button, sync status indicator, referral detail modal
    - Referral type filter: Filter bar dropdown (Co-sell, Marketplace, Solution Provider)
    - Sync button: Header button for manual Partner Center sync
    - Sync status: Right-top indicator showing last sync time and status (OK/FAIL/queued)
    - Toast notifications: "Sync queued" notification on sync trigger
    - **Referral Detail Modal** (2025-01-30): Complete referral detail view with action buttons
      - Detail button: "🔍 Detay" button in referrals table
      - Modal content: Company info, contact details, deal info, team members, raw JSON
      - Action buttons: Copy email/domain/deal value/referral ID, Send to Dynamics (placeholder), Open in Partner Center
      - Backend endpoint: `GET /api/v1/partner-center/referrals/{referral_id}` with `include_raw` parameter
      - Status: ✅ **Completed** - All features implemented and tested
  - Background Sync: Celery Beat schedule (10 min prod, 30s dev) for automatic referral synchronization
  - Phase 7: Production Enablement completed - Feature flag validation, logging review, metrics exposure, background sync enablement
  - Metrics: Partner Center metrics exposed via `/healthz/metrics` endpoint
  - Feature flag: `partner_center_enabled=False` (disabled by default, MVP-safe, production-ready)
  - Features: Lead type detection (Co-sell, Marketplace, Solution Provider), domain extraction fallback, Azure Tenant ID signal, idempotent domain scanning
  - **Solution 1 - Link Status & Referral ID Enhancement** (✅ Complete - 2025-01-30)
    - Backend: Added `link_status` (none/linked/unlinked/mixed) and `primary_referral_id` to Leads API
    - UI: Link status badges in Leads and Referrals tabs (consistent rendering)
    - Breakdown modal: Partner Center Referral section with referral type, link status, and referral ID
    - Export: Added `link_status` column to CSV/XLSX export
    - Tests: 9/9 passing (7 scenarios + 2 integration tests)
    - UI Consistency: Fixed badge rendering inconsistencies between Leads and Referrals tabs
  - **Solution 2 - Multiple Referrals Aggregate (MVP)** (✅ Complete - 2025-01-30)
    - Backend: Added `referral_count`, `referral_types[]`, `referral_ids[]` to Leads API (backward compatible)
    - UI: Referral count badge `(2)`, `(3+)` in Leads table with tooltip showing all referral types
    - Breakdown modal: "Partner Center Referrals (n)" section with aggregate info (total, types, IDs)
    - Export: Added `referral_count`, `referral_types` (comma-separated), `referral_ids` (comma-separated) columns
    - Tests: Extended test suite with Solution 2 aggregate field assertions (9/9 passing)
  - Status: ✅ **Production-ready** - All phases completed (Phase 1-7), 68/68 tests passing (59 referral + 9 link status), feature flag OFF (MVP-safe)
  - UI Status: ✅ **Complete** - All UI features implemented (referral column, filter, sync button, status indicator, link status badges)
  - Next: Post-MVP - Scoring Pipeline Integration (Future enhancement)
- **IP Enrichment Minimal UI** (✅ Completed) - Added IP enrichment to score breakdown and sales summary
  - Backend: IP enrichment integrated into score-breakdown and sales-summary endpoints
  - UI: Network & Location section added to score breakdown modal (country + proxy warning)
  - Sales Engine: IP context (country, proxy) integrated into sales intelligence text generation
  - Impact: Improves score accuracy, enhances sales intelligence, strengthens Hunter's positioning
- **IP Enrichment Validation** (✅ Completed) - Validation test script and status documentation
  - Test Script: Created validation script for 11 real-world domains (Türkiye hosting, M365, Global big tech)
  - Test Results: IP resolution 100% success (11/11), Enrichment 100% success (11/11) - Full validation completed
  - Status Documentation: Created comprehensive status tracking document
  - MVP Decision: ✅ ACCEPTED FOR MVP (country + city data quality acceptable)
  - Status: Production-ready (enrichment enabled, DB files available)
- **Mini UI v1.1 Polish** (✅ Completed - 7/10 tasks) - Sales-friendly UI improvements
  - Search Input: Optimized debounce (500ms → 400ms)
  - Empty State: Improved message with action buttons
  - Error Messages: Sales-friendly Turkish messages (technical details hidden)
  - Loading Indicators: Button disable + "Yükleniyor..." text
  - Score Breakdown Modal: Added "Neden bu skor?" header with explanation
  - Segment Tooltips: Sales-friendly explanations (Existing, Migration, Cold, Skip)
  - Location Info: More prominent display with "(IP bazlı tahmin)" note
  - Remaining: Dogfooding test, duplicate request detection, modal cache (pending manual testing)
- **Regression Dataset Rename & Expansion** (✅ Completed) - Renamed "golden dataset" to "silver regression dataset"
  - Renamed test file and variables for clarity (synthetic regression set, not ground truth)
  - Expanded regression dataset from 14-15 to 26 test cases
  - Added new test cases: M365+DMARC none, Google+DKIM broken, Multi-MX, Zoho, Amazon SES, SendGrid, etc.
  - Created Golden Dataset v1.0 Blueprint for future real-world validation dataset
- **Scoring Engine Test Fixes** (✅ Completed) - Critical test failures fixed, scoring engine fully validated
  - Fixed `dkim_none` risk penalty (-5) in test expectations
  - Fixed priority score ranges (Skip → 7, Existing → 3-6, Migration → 1-4)
  - All 86 scoring tests now passing (0 failures)
  - Impact: Production confidence restored, scoring engine validated
- **SSO Removal - Internal Access Mode** (✅ Completed) - Removed unused Microsoft SSO authentication, switched to Internal Access Mode
  - Removed SSO implementation (~400+ lines of code) - Not used in any core flows
  - Removed dependencies: `msal`, `python-jose`, `cryptography` (SSO-specific)
  - Removed `User` model and Azure AD configuration
  - Simplified authentication: Network-level access control for internal tool (3-10 users)
  - Impact: Reduced code complexity, removed maintenance burden
- **Integration Roadmap - Phase 1: Mini UI Stabilization** (✅ Completed) - UI polish and stability improvements
  - Button & Modal Fixes (Task 1.1 ✅) - Improved hover states, modal scroll optimization
  - Score Breakdown Improvements (Task 1.2 ✅) - Data flow fixes, tooltip positioning, signal order, loading states
  - Loading States (Task 1.3 ✅) - Table spinner, filter states, export button states
  - Filter Bar UX (Task 1.4 ✅) - Layout improvements, clear button, localStorage persistence
  - General UX Polish (Task 1.5 ✅) - Table hover effects, pagination UX, empty state, toast improvements

**Unreleased** (2025-01-27):
- **Test Suite Improvements** - Shared test fixtures with transaction-based isolation, standardized test isolation, conditional test execution for integration tests (Redis/Celery), 497 tests total

**v1.0.0** (2025-01-28):
- **Production Release** - First production-ready version
- **P0 Hardening** - Database pooling, API key security, logging, Sentry, health checks
- **P1 Performance** - Alembic, distributed rate limiting, caching, bulk operations, API versioning
- **Stabilization Sprint** - 3-day enterprise-ready stabilization
- **Sales Engine** - Sales intelligence layer with call scripts and discovery questions
- **Read-Only Mode** - CRM-lite features write endpoints disabled for Dynamics migration

**v0.5.0** (2025-11-14):
- **G18: ReScan + Alerts** - Automation and change detection
- **G17: Notes, Tags, Favorites + PDF** - CRM-lite features and PDF summaries
- **G16: Webhook + Lead Enrichment** - Webhook ingestion with API key authentication
- **G15: Bulk Scan & Async Queue** - Async bulk domain scanning with progress tracking
- **G14: CSV Export + Mini UI** - Lead data export and simple web interface

> 📋 **Full changelog**: See [CHANGELOG.md](CHANGELOG.md) for complete release history

## Features

### Core Functionality
- ✅ Docker Compose setup with PostgreSQL and FastAPI
- ✅ Database schema with 5 tables (companies, domain_signals, lead_scores, raw_leads, provider_change_history)
- ✅ Domain normalization (punycode, www stripping, email/URL extraction)
- ✅ Provider mapping (M365, Google, Yandex, Zoho, Amazon, SendGrid, Mailgun, Hosting, Local, Unknown)
- ✅ Rule-based scoring engine with segment classification
- ✅ Domain ingestion (CSV + Excel + single domain endpoints)
- ✅ Excel/CSV column auto-detection for OSB files

### Analysis & Scoring
- ✅ DNS analysis (MX/SPF/DKIM/DMARC with 10s timeout)
- ✅ **DMARC Coverage** (G20) - DMARC policy coverage percentage (pct parameter) ✨ YENİ
- ✅ WHOIS lookup (graceful fail with 5s timeout)
- ✅ Generic email generation for domains
- ✅ Email validation (syntax, MX, optional SMTP)
- ✅ Priority score calculation for lead prioritization
- ✅ **Tenant Size Estimation** (G20) - MX pattern-based tenant size for M365/Google (small/medium/large) ✨ YENİ
- ✅ **Local Provider Detection** (G20) - Specific local hosting provider identification (TürkHost, Natro, etc.) ✨ YENİ

### Data Quality & Tracking
- ✅ **Provider change tracking** - Automatic detection and history logging when domains switch providers
- ✅ **Duplicate prevention** - Automatic cleanup of duplicate LeadScore and DomainSignal records
- ✅ **Domain validation** - Enhanced validation to filter invalid domains (nan, web sitesi, etc.)
- ✅ **IP Enrichment** - IP geolocation, ASN, ISP, and proxy detection (MaxMind, IP2Location, IP2Proxy) ✨ YENİ
  - **Data Sources**: MaxMind GeoLite2 (City/Country/ASN), IP2Location LITE, IP2Proxy LITE
  - **Configuration**: Simplified env format (`MAXMIND_CITY_DB`, `MAXMIND_COUNTRY_DB`, `IP2LOCATION_DB`, `IP2PROXY_DB`)
  - **Country DB Support**: Optional `GeoLite2-Country.mmdb` as fallback for country-only lookups
  - **Level 1 Exposure** (2025-01-28): `infrastructure_summary` field in `/leads` and `/lead/{domain}` API responses
  - Human-readable summary: "Hosted on DataCenter, ISP: Hetzner, Country: DE"
  - Usage type mapping: DCH → DataCenter, COM → Commercial, RES → Residential, MOB → Mobile

### API & UI
- ✅ Lead segmentation API with filtering
- ✅ Dashboard endpoint with aggregated statistics
- ✅ CSV/Excel export endpoint (`GET /leads/export`) - Export leads with filters
- ✅ Mini UI (HTML + Vanilla JS) - Simple web interface for demo and internal use
  - **Phase 3 (2025-01-29)**: CSP P-Model Integration - P1-P6 badges, tooltips, score breakdown panel, provider-specific descriptions
  - **12+ features**: Upload, Scan, Table, Export, Search, Sorting, Pagination, Score Breakdown, Toast Notifications, Tooltips, P-Model Badges, CSP P-Model Panel
- ✅ **Progress tracking** - Real-time progress updates for CSV ingestion and scanning operations
- ✅ **Bulk Scan** - Async bulk domain scanning with progress tracking (G15)
- ✅ **G19: UI Upgrade** - Sorting, pagination, and full-text search for leads table
- ✅ **G19: Dashboard KPI** - New `/dashboard/kpis` endpoint with high priority leads count
- ✅ **G19: Score Breakdown** - Detailed score analysis with modal UI
- ✅ **UI Patch v1.1** - Skor detay modal ve UX iyileştirmeleri
  - DKIM çift gösterimi düzeltildi (tek satır: "DKIM Eksik: -15")
  - DMARC_NONE kategorisi düzeltildi (Pozitif Sinyaller'den çıkarıldı)
  - Sıralama tutarlılığı (SPF → DKIM → DMARC → Riskler)
  - Provider renkli badge'ler (M365, Google, Yandex, Local, vb.)
  - Sort ikonları iyileştirmeleri (tooltip + daha belirgin)
- ✅ **Stabilization Sprint - Gün 3: UI Stabilizasyon** (2025-01-28) - Enterprise-Ready / UI-Stable / Integration-Ready
  - Table view cleanup - Column width optimization, row hover effects, empty state with CTA, loading spinner, pagination improvements
  - Score breakdown modal - Enhanced close button, ESC key support, backdrop click, scroll optimization, tooltips for signals/risks
  - Header/Footer simplification - Compact header, footer with version info and links
  - Export/PDF basic - CSV/Excel export buttons, toast notifications, PDF export in modal
  - Tooltip + hover behavior - Generic tooltip system, smooth transitions, hover effects
  - UI %90+ stabil - Entegrasyona hazır
- ✅ **G21 Phase 2: Sales Engine** (2025-01-28) - Sales intelligence layer for lead qualification ✨ YENİ
  - Sales intelligence summary endpoint (`GET /api/v1/leads/{domain}/sales-summary`)
- ✅ **Sales Engine v1.1 - Intelligence Layer** (2025-01-28) - Reasoning capabilities for sales intelligence ✨ YENİ + UX POLISHED
  - **Segment Explanation Engine** - Explains why a lead belongs to a segment
  - **Provider Reasoning Layer** - Explains why a provider is classified as such
  - **Security Signals Reasoning** - Risk assessment with sales angle and recommended action
  - **Cold Segment Call Script v1.1** - Soft, discovery-focused script for Cold leads
  - **Opportunity Rationale** - Explains why opportunity_potential is X (calculation breakdown)
  - **Next-step CTA** - Clear, actionable next step recommendation
  - API fields: `segment_explanation`, `provider_reasoning`, `security_reasoning`, `opportunity_rationale`, `next_step`
  - Documentation: `docs/active/SALES-ENGINE-V1.1.md`
  - **UX Polish (P1.5)** - Sales-ready UI improvements:
    - Security risk badges: "YÜKSEK RİSK" / "ORTA RİSK" / "DÜŞÜK RİSK" (Turkish labels)
    - Security section: 3-block layout (Risk Özeti, Teknik Durum, Satış Açısı + Aksiyon)
    - Provider section: "Mevcut Sağlayıcı Değerlendirmesi" (more professional title)
    - Next Step CTA: Pill-style badges ([ARAMA] [3 gün içinde] [Orta Öncelik])
    - Improved visual hierarchy and readability
  - Segment-specific call scripts and discovery questions (Turkish)
  - Offer tier recommendations (Business Basic/Standard/Enterprise)
  - Opportunity potential scoring (0-100) with tuning factor support
  - Urgency level calculation (low/medium/high)
  - Frozen API contract (UI-ready, breaking change policy defined)
  - TypeScript and JSDoc type definitions for frontend integration
  - Logging and telemetry (`sales_summary_viewed` event)
- ✅ **G21 Phase 3: Read-Only Mode** (2025-01-28) - CRM-lite features write endpoints disabled ✨ YENİ
  - Write endpoints disabled (410 Gone) - Notes/Tags/Favorites write operations now return 410 Gone
  - Read endpoints remain available - Migration support for Dynamics 365 migration
  - Deprecated endpoint monitoring - Usage tracking via `GET /healthz/metrics` endpoint
  - Zero downtime migration support - Read-only mode enables safe migration to Dynamics 365

## Tech Stack

- **Backend**: FastAPI (Python 3.10)
- **Database**: PostgreSQL 15
- **Migration**: Alembic (P1) - Database migration management system
- **Queue**: Celery + Redis
- **Rate Limiting**: Redis-based distributed rate limiting (P1-2) - Multi-worker support with fallback
- **Caching**: Redis-based distributed caching (P1-3) - DNS, WHOIS, Provider, Scoring, Scan cache
- **Bulk Operations**: Batch processing optimization (P1-4) - Rate-limit aware batch processing with deadlock prevention
- **Retry Logic**: Exponential backoff with jitter (`app/core/retry_utils.py`) - Centralized retry utilities for D365 and Partner Center API calls, prevents thundering herd scenarios
- **Logging**: Structured logging with PII masking (2025-01-28) - JSON format in production, contextual logging, domain/email masking
- **DNS Analysis**: dnspython
- **WHOIS**: python-whois
- **Deployment**: Docker Compose

## Quick Start

### Prerequisites

**Recommended:**
- Docker Desktop (with WSL2 integration)
- WSL2 (Ubuntu 22.04 or later)
- Git

**Alternative (not recommended):**
- Docker Desktop (Windows)
- Git Bash or PowerShell
- Python 3.10+ (for local testing)

> 💡 **Recommendation:** Use WSL2 for best performance and production-like environment. See [Development Environment Guide](docs/active/DEVELOPMENT-ENVIRONMENT.md) for details.

### Setup

1. **Clone the repository:**
   
   **In WSL (Recommended):**
   ```bash
   cd ~/projects
   git clone https://github.com/brdfb/dyn365hunterv3.git
   cd dyn365hunterv3
   ```
   
   **In Windows (Git Bash):**
   ```bash
   git clone https://github.com/brdfb/dyn365hunterv3.git
   cd dyn365hunterv3
   ```
   
   **If project is already in Windows (`C:\CursorPro\DomainHunterv3`):**
   ```bash
   # In WSL, use Windows path:
   cd /mnt/c/CursorPro/DomainHunterv3
   # Or copy to Linux file system for better performance:
   cp -r /mnt/c/CursorPro/DomainHunterv3 ~/projects/dyn365hunterv3
   cd ~/projects/dyn365hunterv3
   ```

2. **Setup Python virtual environment (optional, recommended for local development):**
   
   **For Windows (Git Bash, CMD, PowerShell):**
   ```bash
   bash setup_venv.sh
   source .venv/Scripts/activate  # Git Bash
   # or
   .venv\Scripts\activate.bat     # CMD
   # or
   .venv\Scripts\Activate.ps1     # PowerShell
   ```
   
   **For WSL/Linux:**
   ```bash
   bash setup_venv.sh
   source .venv/bin/activate
   ```
   
   **Note:** If `python3-venv` is not installed, run: `sudo apt update && sudo apt install python3-venv`
   
   **Troubleshooting:** See [WSL Guide](docs/active/WSL-GUIDE.md) for common issues and solutions.

3. **Run setup script:**
   ```bash
   bash setup_dev.sh
   # Or with venv: bash setup_dev.sh --with-venv
   ```

   This will:
   - Check Docker availability
   - Create `.env` from `.env.example`
   - Start Docker Compose services (PostgreSQL, Redis, API, Worker)
   - Wait for PostgreSQL and Redis to be ready
   - Run database schema migration (via Alembic)
   - Verify `/healthz` endpoint

4. **Verify installation:**
   ```bash
   curl http://localhost:8000/healthz
   ```

   Expected response:
   ```json
   {
     "status": "ok",
     "database": "connected",
     "environment": "development"
   }
   ```

## Mini UI

A simple web interface for demo and internal use:

**Access**: `http://localhost:8000/mini-ui/`

**Features**:
- CSV/Excel file upload
- Single domain scan (with auto-ingest)
- Leads table with filters (segment, min score, provider, **referral type**)
- **Search, Sorting, Pagination** (G19) - Full-text search, sortable columns, page-based pagination
- **P-Model Priority Badges** (Phase 3 - 2025-01-29) - P1-P6 renkli badge'ler, priority_label tooltip'leri
- **Score Breakdown Modal** (G19 + Phase 3) - Detaylı skor analizi, CSP P-Model paneli, provider-specific açıklamalar
- **Partner Center Integration** (2025-01-30) - Referral column with badges, referral type filter, sync button, sync status indicator
- **HAMLE 1: Partner Center Sync Aktifleştirme** (2025-01-30) - 🔄 Kod incelemesi tamamlandı (~85% complete)
  - ✅ OAuth credentials, feature flag, authentication, manual sync test tamamlandı
  - ✅ UI HTML yapısı doğrulandı, error handling kod incelemesi tamamlandı
  - 🔄 UI JS functionality ve error handling manuel testleri kaldı
- CSV/Excel/PDF export
- Dashboard statistics (KPI)
- **13+ ana özellik** - Upload, Scan, Table, Export, Search, Sorting, Pagination, Score Breakdown, Toast Notifications, Tooltips, P-Model Badges, CSP P-Model Panel, Partner Center Integration

**Documentation**: See [mini-ui/README-mini-ui.md](mini-ui/README-mini-ui.md)

---

## API Endpoints

**API Versioning (P1-5):**
- **V1 Endpoints**: All API endpoints are available under `/api/v1/` prefix (e.g., `/api/v1/leads`, `/api/v1/scan/domain`)
- **Legacy Endpoints**: Legacy endpoints (e.g., `/leads`, `/scan/domain`) continue to work for backward compatibility
- **Infrastructure Endpoints**: Health check (`/healthz`) and authentication (`/auth/*`) endpoints are not versioned
- **Migration**: Clients can gradually migrate to v1 endpoints while legacy endpoints remain active

### Quick Reference

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| **Health** | `/healthz` | GET | Health check and database status |
| **Health** | `/healthz/metrics` | GET | Metrics (cache, rate limit, bulk operations, errors) |
| **Ingest** | `/ingest/domain` | POST | Ingest single domain |
| **Ingest** | `/ingest/csv` | POST | Ingest domains from CSV/Excel file |
| **Ingest** | `/ingest/webhook` | POST | Webhook ingestion (API key required) |
| **Scan** | `/scan/domain` | POST | Analyze single domain (DNS + WHOIS + scoring) |
| **Scan** | `/scan/bulk` | POST | Create bulk scan job (async) |
| **Scan** | `/scan/bulk/{job_id}` | GET | Get bulk scan progress |
| **Scan** | `/scan/{domain}/rescan` | POST | Re-scan domain with change detection |
| **Leads** | `/leads` | GET | Query leads (filters, sorting, pagination, search) |
| **Leads** | `/leads/{domain}` | GET | Get single lead details |
| **Leads** | `/leads/{domain}/sales-summary` | GET | Get sales intelligence summary (G21 Phase 2 + v1.1 Intelligence Layer) |
| **Leads** | `/leads/{domain}/score-breakdown` | GET | Get detailed score breakdown |
| **Leads** | `/leads/{domain}/enrich` | POST | Manually enrich lead with contact emails |
| **Leads** | `/leads/export` | GET | Export leads to CSV/Excel |
| **Leads** | `/leads/{domain}/summary.pdf` | GET | Generate PDF account summary |
| **Dashboard** | `/dashboard` | GET | Get aggregated dashboard statistics |
| **Dashboard** | `/dashboard/kpis` | GET | Get dashboard KPIs (lightweight) |
| **Admin** | `/admin/api-keys` | POST | Create API key |
| **Email** | `/email/generate` | POST | Generate generic email addresses |
| **Email** | `/email/generate-and-validate` | POST | Generate and validate emails |
| **Alerts** | `/alerts` | GET | List alerts with filters |
| **Alerts** | `/alerts/config` | POST | Configure alert preferences |
| **Debug** | `/debug/ip-enrichment/{ip}` | GET | Debug IP enrichment (internal/admin use) |
| **Debug** | `/debug/ip-enrichment/config` | GET | Check IP enrichment configuration status |

> 📖 **Detailed documentation**: See sections below for complete endpoint documentation with request/response examples

**Interactive API Documentation:**
- Swagger UI: `http://localhost:8000/docs` (interactive API explorer)
- ReDoc: `http://localhost:8000/redoc` (alternative documentation format)
- OpenAPI JSON: `http://localhost:8000/openapi.json` (machine-readable schema)
- Support: `http://localhost:8000/support` (support information endpoint)

### Health Check
- `GET /healthz` - Health check and database connection status
- `GET /healthz/live` - Liveness probe (Kubernetes/Docker)
- `GET /healthz/ready` - Readiness probe (checks database and Redis connections)
- `GET /healthz/startup` - Startup probe (checks if application has finished starting)
- `GET /healthz/metrics` - Metrics endpoint (Stabilization Sprint - Gün 2)
  - Returns: Cache metrics (hits, misses, hit rate), rate limit metrics (hits, acquired, circuit breaker state), bulk operations metrics (batch success/failure, processing time, deadlock count), error metrics (total errors, errors by component, error trends)
  - Example response: `{"cache": {...}, "rate_limit": {...}, "bulk_operations": {...}, "errors": {...}}`

### Ingest
- `POST /api/v1/ingest/domain` or `POST /ingest/domain` - Ingest single domain
  - Request body: `{"domain": "example.com", "company_name": "Example Inc", "email": "user@example.com", "website": "https://example.com"}`
  - Returns: `{"domain": "example.com", "company_id": 1, "message": "Domain ingested successfully"}`
- `POST /ingest/csv` - Ingest domains from CSV or Excel file
  - Multipart form data with CSV (.csv) or Excel (.xlsx, .xls) file
  - Query parameter: `auto_detect_columns` (optional, default: false) - Auto-detect company/domain columns for OSB Excel files
  - Required column: `domain` (when `auto_detect_columns=false`)
  - Optional columns: `company_name`, `email`, `website`
  - When `auto_detect_columns=true`: Automatically detects company and domain columns using heuristics
  - Returns: `{"ingested": 5, "total_rows": 5, "errors": null}`

### Scan
- `POST /scan/domain` - Analyze single domain (DNS + WHOIS + scoring)
  - Request body: `{"domain": "example.com"}`
  - Returns: `{"domain": "example.com", "score": 75, "segment": "Migration", "reason": "...", "provider": "M365", "tenant_size": "medium", "local_provider": null, "mx_root": "outlook.com", "spf": true, "dkim": true, "dmarc_policy": "reject", "dmarc_coverage": 100, "scan_status": "success"}`
  - Performs DNS analysis (MX, SPF, DKIM, DMARC) and WHOIS lookup
  - **G20**: Extracts DMARC coverage (pct), estimates tenant size (M365/Google), detects local provider ✨ YENİ
  - Calculates readiness score and determines segment
- `POST /scan/bulk` - Create bulk scan job for multiple domains (async)
  - Request body: `{"domain_list": ["example.com", "google.com", "microsoft.com"]}`
  - Returns: `{"job_id": "uuid", "message": "Bulk scan job created successfully", "total": 3}`
  - Creates async job that scans all domains in background
  - Max 1000 domains per job
  - Rate limiting: DNS (10 req/s), WHOIS (5 req/s)
  - Use `GET /scan/bulk/{job_id}` to check progress
- `GET /scan/bulk/{job_id}` - Get bulk scan job status and progress
  - Returns: `{"job_id": "uuid", "status": "running", "progress": 50, "total": 3, "processed": 1, "succeeded": 1, "failed": 0, "errors": []}`
  - Status: `pending`, `running`, `completed`, `failed`
  - Progress: 0-100 percentage
  - Polling-based (no HTTP timeout)
- `GET /scan/bulk/{job_id}/results` - Get bulk scan results (completed jobs only)
  - Returns: `{"job_id": "uuid", "total": 3, "succeeded": 2, "failed": 1, "results": [...]}`
  - Returns scan results for all successfully processed domains
  - Only available for completed jobs

### Leads
- `GET /leads` - Query leads with filters, sorting, pagination, and search (G19)
  - Query parameters:
    - `segment` (optional): Filter by segment (Migration, Existing, Cold, Skip)
    - `min_score` (optional): Minimum readiness score (0-100)
    - `provider` (optional): Filter by provider (M365, Google, etc.)
    - `favorite` (optional): Filter by favorites (true = only favorites, false = all leads)
    - `sort_by` (optional): Sort by field (domain, readiness_score, priority_score, segment, provider, scanned_at)
    - `sort_order` (optional): Sort order (asc or desc, default: asc)
    - `page` (optional): Page number (1-based, default: 1)
    - `page_size` (optional): Number of items per page (default: 50, max: 200)
    - `search` (optional): Full-text search in domain, canonical_name, and provider
  - Returns: Paginated response with `leads`, `total`, `page`, `page_size`, `total_pages`
  - Each lead includes `priority_score` field (1-7, where 1 is highest priority) and `infrastructure_summary` field (IP enrichment summary, e.g., "Hosted on DataCenter, ISP: Hetzner, Country: DE")
- `GET /leads/{domain}/score-breakdown` - Get detailed score breakdown for a domain (G19)
  - Returns: Score breakdown with base_score, provider points, signal points, risk points, and total_score
- `GET /leads/{domain}` - Get single lead details
  - Returns: Complete lead information including signals, scores, priority_score, enrichment data (contact_emails, contact_quality_score, linkedin_pattern), **G20 fields (tenant_size, local_provider, dmarc_coverage)**, **IP enrichment summary (infrastructure_summary)**, and metadata
- `POST /leads/{domain}/enrich` - Manually enrich a lead with contact emails
  - Request body: `{"contact_emails": ["john@example.com", "jane@example.com"]}`
  - Returns: Enrichment results (contact_emails, contact_quality_score, linkedin_pattern)
  - Calculates quality score and detects LinkedIn email patterns
- `GET /leads/export` - Export leads to CSV or Excel format
  - Query parameters:
    - `segment` (optional): Filter by segment (Migration, Existing, Cold, Skip)
    - `min_score` (optional): Minimum readiness score (0-100)
    - `provider` (optional): Filter by provider (M365, Google, etc.)
    - `format` (optional): Export format (`csv` or `xlsx`, default: `csv`)
  - Returns: CSV or Excel file download with lead data
  - File name format: `leads_YYYY-MM-DD_HH-MM-SS.csv` or `leads_YYYY-MM-DD_HH-MM-SS.xlsx`

### Sales Intelligence (G21 Phase 2 + v1.1 Intelligence Layer) ✨ YENİ
- `GET /api/v1/leads/{domain}/sales-summary` - Get complete sales intelligence summary for a lead (v1.1 with reasoning capabilities)
  - Returns: Sales intelligence summary with:
    - `one_liner` - One-sentence sales summary (Turkish)
    - `segment_explanation` - Explains why a lead belongs to a segment (v1.1)
    - `provider_reasoning` - Explains why a provider is classified as such (v1.1)
    - `security_reasoning` - Risk assessment with sales angle and recommended action (v1.1)
    - `opportunity_rationale` - Explains why opportunity_potential is X (calculation breakdown) (v1.1)
    - `next_step` - Clear, actionable next step recommendation (v1.1)
    - `call_script` - Call script bullets for sales outreach (Turkish)
    - `discovery_questions` - Discovery questions for sales qualification (Turkish)
    - `offer_tier` - Offer tier recommendation (Business Basic/Standard/Enterprise) with pricing details
    - `opportunity_potential` - Opportunity potential score (0-100)
    - `urgency` - Urgency level (low/medium/high)
    - `metadata` - Additional context (segment, provider, tenant_size, readiness_score, priority_score, etc.)
  - Example response:
    ```json
    {
      "domain": "example.com",
      "one_liner": "example.com - Migration fırsatı, yüksek hazırlık skoru (85), Enterprise teklif hazırlanabilir.",
      "call_script": ["Merhaba, example.com için email altyapınızı inceledik...", "..."],
      "discovery_questions": ["Şu anki email altyapınızdan memnun musunuz?", "..."],
      "offer_tier": {
        "tier": "Enterprise",
        "license": "Enterprise",
        "price_per_user_per_month": 20,
        "migration_fee": 10000,
        "defender_price_per_user_per_month": 10,
        "consulting_fee": 50000,
        "recommendation": "Enterprise çözümü önerilir..."
      },
      "opportunity_potential": 89,
      "urgency": "high",
      "metadata": {...}
    }
    ```
  - **API Contract**: Frozen contract (UI-ready) - See `docs/api/SALES-SUMMARY-V1-CONTRACT.md`
  - **Type Definitions**: TypeScript (`mini-ui/types/sales.ts`) and JSDoc (`mini-ui/types/sales.js`)
  - **Legacy Endpoint**: `GET /leads/{domain}/sales-summary` (backward compatible)

### Notes (G17: CRM-lite) ❌ **DISABLED** (G21 Phase 3)
- ❌ **Write endpoints disabled** (2025-01-28) - Returns 410 Gone (Read-Only Mode)
  - `POST /leads/{domain}/notes` - ❌ **Disabled (410 Gone)** - Create a note for a domain
    - Returns: 410 Gone with error message
    - **Reason**: Notes are now managed in Dynamics 365
    - **Alternative**: Use Dynamics 365 Timeline/Notes API
  - `PUT /leads/{domain}/notes/{note_id}` - ❌ **Disabled (410 Gone)** - Update a note
    - Returns: 410 Gone with error message
    - **Alternative**: Use Dynamics 365 Timeline/Notes API
  - `DELETE /leads/{domain}/notes/{note_id}` - ❌ **Disabled (410 Gone)** - Delete a note
    - Returns: 410 Gone with error message
    - **Alternative**: Use Dynamics 365 Timeline/Notes API
- ✅ **Read endpoint remains available** (migration support):
  - `GET /leads/{domain}/notes` - List all notes for a domain
    - Returns: Array of notes (ordered by created_at desc)
    - **Status**: Available for migration support until Phase 6

### Tags (G17: CRM-lite) ❌ **DISABLED** (G21 Phase 3)
- ❌ **Manual tag write endpoints disabled** (2025-01-28) - Returns 410 Gone (Read-Only Mode)
  - `POST /leads/{domain}/tags` - ❌ **Disabled (410 Gone)** (manual tags only) - Add a tag to a domain
    - Returns: 410 Gone with error message
    - **Reason**: Manual tags are now managed in Dynamics 365. Auto-tags (system-generated) remain available.
    - **Alternative**: Use Dynamics 365 Tags API for manual tag management
  - `DELETE /leads/{domain}/tags/{tag_id}` - ❌ **Disabled (410 Gone)** (manual tags only) - Remove a tag from a domain
    - Returns: 410 Gone with error message
    - **Alternative**: Use Dynamics 365 Tags API for manual tag management
- ✅ **Read endpoint remains available** (auto-tags needed):
  - `GET /leads/{domain}/tags` - List all tags for a domain
    - Returns: Array of tags (includes auto-tags and manual tags)
    - **Status**: Available for auto-tags (system-generated tags remain functional)
- **Auto-tagging**: Automatically applies tags after domain scan (✅ **Remains active**):
  - `security-risk`: No SPF + no DKIM
  - `migration-ready`: Migration segment + score >= 70
  - `expire-soon`: Domain expires in < 30 days
  - `weak-spf`: SPF exists but DMARC policy is 'none'
  - `google-workspace`: Provider is Google
  - `local-mx`: Provider is Local

### Favorites (G17: CRM-lite) ❌ **DISABLED** (G21 Phase 3)
- ❌ **Write endpoints disabled** (2025-01-28) - Returns 410 Gone (Read-Only Mode)
  - `POST /leads/{domain}/favorite` - ❌ **Disabled (410 Gone)** - Add a domain to favorites
    - Returns: 410 Gone with error message
    - **Reason**: Favorites are now managed in Dynamics 365
    - **Alternative**: Use Dynamics 365 Favorite field for favorite management
  - `DELETE /leads/{domain}/favorite` - ❌ **Disabled (410 Gone)** - Remove a domain from favorites
    - Returns: 410 Gone with error message
    - **Alternative**: Use Dynamics 365 Favorite field for favorite management
- ✅ **Read endpoint remains available** (migration support):
  - `GET /leads?favorite=true` - List favorite domains
    - Returns: Array of leads that are favorited by the current user
    - **Status**: Available for migration support until Phase 6

### PDF Summary (G17)
- `GET /leads/{domain}/summary.pdf` - Generate PDF account summary
  - Returns: PDF file download
  - Includes: Provider info, SPF/DKIM/DMARC status, expiry date, signals, scores, risks
  - File name: `{domain}_summary.pdf`
  - **Turkish Character Support**: Full UTF-8 support for Turkish characters (ı, ş, ğ, ü, ö, ç)

### ReScan (G18: Automation)
- `POST /scan/{domain}/rescan` - Re-scan a single domain and detect changes
  - Returns: Scan result with detected changes (signals, scores, alerts)
  - Detects: MX changes, DMARC changes, expiry warnings, score changes
  - Creates alerts for detected changes
- `POST /scan/bulk/rescan?domain_list=domain1.com,domain2.com` - Bulk rescan multiple domains
  - Returns: Job ID for async processing
  - Maximum 1000 domains per request
  - Uses same progress tracking as bulk scan

### Alerts (G18: Change Notifications)
- `GET /alerts` - List alerts with optional filters
  - Query parameters:
    - `domain` (optional): Filter by domain
    - `alert_type` (optional): Filter by alert type (mx_changed, dmarc_added, expire_soon, score_changed)
    - `status` (optional): Filter by status (pending, sent, failed)
    - `limit` (optional): Maximum number of alerts (default: 100)
  - Returns: List of alerts
- `POST /alerts/config` - Create or update alert configuration
  - Request body: `{"alert_type": "mx_changed", "notification_method": "webhook", "enabled": true, "frequency": "immediate", "webhook_url": "https://example.com/webhook"}`
  - Returns: Alert configuration
- `GET /alerts/config` - List alert configurations for current user
  - Returns: List of alert configurations
- **Notification methods**: Email (placeholder), Webhook (HTTP POST), Slack (optional)
- **Alert types**: MX changed, DMARC added, Domain expire soon, Score changed
- **Daily rescan**: Automatically runs daily via Celery Beat scheduler

### Dashboard
- `GET /dashboard` - Get aggregated dashboard statistics (legacy endpoint)
  - Returns: `{"total_leads": 150, "migration": 25, "existing": 50, "cold": 60, "skip": 15, "avg_score": 55.5, "max_score": 90, "high_priority": 10}`
  - Provides segment distribution, average score, max score, and high priority lead count
- `GET /dashboard/kpis` - Get dashboard KPIs (G19)
  - Returns: `{"total_leads": 150, "migration_leads": 25, "high_priority": 10}`
  - Lightweight endpoint for KPI cards (total leads, migration leads, high priority leads)

### Webhook Ingestion (G16)
- `POST /ingest/webhook` - Ingest data from webhook with API key authentication
  - **Authentication**: Requires `X-API-Key` header
  - Request body: `{"domain": "example.com", "company_name": "Example Inc", "contact_emails": ["john@example.com"]}`
  - Returns: `{"status": "success", "domain": "example.com", "ingested": true, "enriched": true, "message": "..."}`
  - Features:
    - API key authentication and rate limiting (per key)
    - Automatic domain normalization
    - Lead enrichment (contact emails, quality score, LinkedIn pattern detection)
    - Retry logic with exponential backoff for failed requests
    - Error logging and tracking

### Debug Endpoints (Internal/Admin Use)
- `GET /debug/ip-enrichment/{ip}` - Debug IP enrichment for a specific IP address
  - Query parameters:
    - `use_cache` (optional, default: true): Whether to use cache for enrichment lookup
  - Returns: Enrichment result from providers (MaxMind, IP2Location, IP2Proxy), cache status, and database record
  - Example: `GET /debug/ip-enrichment/8.8.8.8?use_cache=false`
- `GET /debug/ip-enrichment/config` - Check IP enrichment configuration status
  - Returns: Current configuration (feature flag, DB paths, availability status)
  - Useful for troubleshooting enrichment setup

### Admin (API Key Management)
- `POST /admin/api-keys` - Create a new API key
  - Request body: `{"name": "My API Key", "rate_limit_per_minute": 60, "created_by": "admin"}`
  - Returns: API key (shown only once - store securely!)
- `GET /admin/api-keys` - List all API keys (without showing actual keys)
- `PATCH /admin/api-keys/{key_id}/activate` - Activate an API key
- `PATCH /admin/api-keys/{key_id}/deactivate` - Deactivate an API key

### Email Tools
- `POST /email/generate` - Generate generic email addresses for a domain
  - Request body: `{"domain": "example.com"}`
  - Returns: `{"domain": "example.com", "emails": ["admin@example.com", "hr@example.com", "info@example.com", ...]}`
  - Generates common generic email addresses (info, sales, admin, iletisim, satis, etc.) for the given domain
  - Domain is normalized before generation (www prefix removed, lowercase, etc.)
- `POST /email/generate-and-validate` - Generate and validate generic email addresses for a domain
  - Request body: `{"domain": "example.com", "use_smtp": false}`
  - Returns: `{"domain": "example.com", "emails": [{"email": "info@example.com", "status": "valid", "confidence": "medium", "checks": {"syntax": true, "mx": true, "smtp": "skipped"}, "reason": "Valid syntax and MX records (SMTP not checked)"}, ...]}`
  - Generates generic emails and validates each one using:
    - Syntax validation (regex)
    - MX record validation (DNS)
    - Optional SMTP validation (if `use_smtp=true`, default: false)
  - Returns validation status ("valid", "invalid", "unknown"), confidence level ("high", "medium", "low"), and detailed checks

## Development

### Project Structure

```
dyn365hunterv3/
├── app/                    # FastAPI application
│   ├── api/               # API endpoints
│   ├── core/              # Core logic (normalizer, analyzer, scorer, celery, tasks)
│   ├── db/                # Database models and session
│   └── data/              # Configuration files (providers.json, rules.json)
├── tests/                 # Test files
├── docs/                  # Documentation
├── scripts/               # Utility scripts
│   └── start_celery_worker.sh  # Celery worker startup script
├── Dockerfile             # FastAPI container
├── docker-compose.yml     # Services configuration (PostgreSQL, Redis, API, Worker)
└── setup_dev.sh          # Development setup script
```

### Running Tests

**Test Suite:** 497 tests with transaction-based isolation and conditional execution for integration tests.

**Note:** For local testing (outside Docker), activate virtual environment first:
```bash
# Activate venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term

# Run specific test file
pytest tests/test_scan_single.py -v

# Run integration tests (requires Redis/Celery)
pytest tests/ -v -m requires_integration
```

**Test Infrastructure:**
- Shared fixtures (`tests/conftest.py`): Transaction-based database isolation, TestClient with dependency override
- Conditional execution: Integration tests automatically skip if Redis/Celery unavailable
- Test isolation: Each test runs in isolated transaction with automatic rollback

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type check
mypy app/
```

## CI/CD

The project includes GitHub Actions workflows:

- **CI Pipeline** (`ci.yml`): Runs tests, linting, Docker build, and Docker Compose tests
- **Code Quality** (`lint.yml`): Format and type checking

Workflows run on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

## Database Migrations

The project uses **Alembic** for database migration management (P1).

### Migration Commands

```bash
# Upgrade to latest migration
python -m app.db.run_migration upgrade

# Upgrade to specific revision
python -m app.db.run_migration upgrade <revision>

# Downgrade one step
python -m app.db.run_migration downgrade

# Show current revision
python -m app.db.run_migration current

# Show migration history
python -m app.db.run_migration history

# Check for schema drift
python -m app.db.run_migration check
```

### Creating New Migrations

```bash
# Create a new migration (autogenerate from models)
alembic revision --autogenerate -m "add_new_feature"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Migration Strategy

- **Base Revision**: `08f51db8dce0` represents the current production schema (includes all historical migrations g16-g20)
- **Legacy Migrations**: Historical SQL migration files are in `app/db/migrations/legacy/` for reference
- **Future Changes**: All schema changes will be managed through Alembic revisions

**Documentation**: See `docs/active/P1-ALEMBIC-STATUS.md` for detailed migration status and usage.

---

## Environment Variables

See `.env.example` for all available environment variables:

```bash
# Database
DATABASE_URL=postgresql://dyn365hunter:password123@postgres:5432/dyn365hunter
POSTGRES_USER=dyn365hunter
POSTGRES_PASSWORD=password123
POSTGRES_DB=dyn365hunter

# Redis (for Celery queue and progress tracking)
REDIS_URL=redis://redis:6379/0

# FastAPI
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Development
ENVIRONMENT=development

# IP Enrichment (Feature flag: disabled by default)
# HUNTER_ENRICHMENT_ENABLED=false

# MaxMind GeoIP Databases (new format - recommended)
MAXMIND_CITY_DB=app/data/maxmind/GeoLite2-City.mmdb
MAXMIND_COUNTRY_DB=app/data/maxmind/GeoLite2-Country.mmdb
# MAXMIND_ASN_DB=app/data/maxmind/GeoLite2-ASN.mmdb  # Optional - only add if you use ASN database

# IP2Location & IP2Proxy
IP2LOCATION_DB=app/data/ip2location/IP2LOCATION-LITE-DB11.BIN
IP2PROXY_DB=app/data/ip2proxy/IP2PROXY-LITE-PX11.BIN
```

## 🚀 Quick Start (Production)

### Production Deployment

```bash
# 1. Set environment variables
export DATABASE_URL="postgresql://user:password@host:port/database"
export REDIS_URL="redis://host:port/db"
export ENVIRONMENT="production"
export HUNTER_SENTRY_DSN="https://..."

# 2. Run deployment script
bash scripts/deploy_production.sh

# 3. Verify deployment
curl http://localhost:8000/healthz/ready
```

**See**: [Production Deployment Guide](docs/active/PRODUCTION-DEPLOYMENT-GUIDE.md) for complete instructions.

---

## Example Usage

### Complete Flow

```bash
# 1. Ingest a domain
curl -X POST http://localhost:8000/ingest/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "company_name": "Example Inc"}'

# 2. Scan the domain
curl -X POST http://localhost:8000/scan/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'

# 2b. Bulk scan multiple domains (async)
curl -X POST http://localhost:8000/scan/bulk \
  -H "Content-Type: application/json" \
  -d '{"domain_list": ["example.com", "google.com", "microsoft.com"]}'

# 2c. Check bulk scan progress
curl "http://localhost:8000/scan/bulk/{job_id}"

# 2d. Get bulk scan results (when completed)
curl "http://localhost:8000/scan/bulk/{job_id}/results"

# 3. Query leads
curl "http://localhost:8000/leads?segment=Migration&min_score=70"

# 4. Get single lead
curl "http://localhost:8000/leads/example.com"

# 5. Get dashboard statistics
curl "http://localhost:8000/dashboard"

# 6. Create API key for webhook
curl -X POST http://localhost:8000/admin/api-keys \
  -H "Content-Type: application/json" \
  -d '{"name": "My Webhook Key", "rate_limit_per_minute": 60}'

# 7. Ingest data via webhook
curl -X POST http://localhost:8000/ingest/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{"domain": "example.com", "company_name": "Example Inc", "contact_emails": ["john@example.com"]}'

# 8. Manually enrich a lead
curl -X POST http://localhost:8000/leads/example.com/enrich \
  -H "Content-Type: application/json" \
  -d '{"contact_emails": ["john@example.com", "jane@example.com"]}'
```

## Documentation

### For Sales Team
- [Sales Guide](docs/SALES-GUIDE.md) - Quick start guide for sales team (5 minutes)
- [Segment Guide](docs/SEGMENT-GUIDE.md) - Segment and score explanations
- [Sales Scenarios](docs/SALES-SCENARIOS.md) - Real-world usage scenarios
- [Sales Demo Script](scripts/sales-demo.sh) - Quick demo script

### For Developers

#### Feature Documentation
- [Provider Change Tracking](docs/active/PROVIDER-CHANGE-TRACKING.md) - Automatic detection and logging of provider changes
- [Duplicate Prevention](docs/active/DUPLICATE-PREVENTION.md) - Automatic cleanup of duplicate records
- [Domain Validation](docs/active/DOMAIN-VALIDATION.md) - Enhanced domain validation and filtering
- [IP Enrichment Implementation](docs/active/IP-ENRICHMENT-IMPLEMENTATION.md) - IP geolocation, ASN, ISP, and proxy detection with Level 1 API exposure
- [IP Enrichment Quick Start](docs/active/IP-ENRICHMENT-QUICK-START.md) - 10-minute setup guide for downloading DB files and enabling enrichment

#### Development Guides
- [Development Environment](docs/active/DEVELOPMENT-ENVIRONMENT.md) - Setup guide
- [WSL Guide](docs/active/WSL-GUIDE.md) - WSL2 setup and troubleshooting
- [Test Analysis](docs/active/TEST-ANALYSIS.md) - Test suite analysis and best practices
- [Application Status](docs/active/APPLICATION-STATUS.md) - Application health status report
- [Docker Troubleshooting](docs/active/DOCKER-TROUBLESHOOTING.md) - Common Docker issues and solutions
- [Production Engineering Guide](docs/active/PRODUCTION-ENGINEERING-GUIDE-V1.md) - SRE runbook with health checks, monitoring, deployment strategies
- [Mini UI README](mini-ui/README-mini-ui.md) - Mini UI usage guide and documentation

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

