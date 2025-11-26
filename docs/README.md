# Documentation Structure

## 🗺️ Documentation Map (Quick Reference)

**"Hangi dokümana bakmalıyım?"** sorusuna hızlı cevap:

| Soru | Doküman |
|------|---------|
| **"Production'a çıkabilir miyim?"** | `docs/active/GO-NO-GO-CHECKLIST-v1.0.md` |
| **"Hunter'ın şu anki durumu ne?"** | `docs/active/HUNTER-STATE-v1.0.md` |
| **"G21 refactor'ın durumu ne?"** | `docs/active/G21-ROADMAP-CURRENT.md` |
| **"Post-MVP'de ne yapacağız?"** | `docs/active/POST-MVP-STRATEGY.md` |
| **"Sales Engine nasıl kullanılır?"** | `docs/sales/SALES-GUIDE.md` |
| **"Sales Engine v1.1 Intelligence Layer nedir?"** | `docs/active/SALES-ENGINE-V1.1.md` |
| **"CSP P-Model nedir? P1-P6 nasıl hesaplanıyor?"** | `docs/archive/2025-01-29-CSP-COMMERCIAL-SEGMENT-DESIGN.md` (tasarım) + `docs/archive/2025-01-29-CSP-P-MODEL-IMPLEMENTATION-PLAN.md` (implementation - completed) |
| **"Commercial Segment & Heat nedir?"** | `docs/archive/2025-01-29-CSP-COMMERCIAL-SEGMENT-DESIGN.md` |
| **"Segment ve priority nedir?"** | `docs/sales/SEGMENT-GUIDE.md` |
| **"Development environment nasıl kurulur?"** | `docs/reference/DEVELOPMENT-ENVIRONMENT.md` |
| **"Production deployment nasıl yapılır?"** | `docs/reference/PRODUCTION-DEPLOYMENT-GUIDE.md` |
| **"Production monitoring nasıl yapılır?"** | `docs/reference/PRODUCTION-MONITORING-WATCH.md` |
| **"Hangi branch'i kullanmalıyım?"** | `docs/reference/BRANCH-MANAGEMENT.md` |

---

## 📁 Folder Organization

```
docs/
├── active/          # Active documentation (current phase)
├── archive/         # Archived documentation (completed phases)
├── reference/       # Reference guides (development, setup, troubleshooting)
├── sales/           # Sales team documentation (guides, personas, training)
├── prompts/         # Important prompts, conversations, and architectural decisions
├── todos/           # TODO lists and task tracking
└── plans/           # Project plans and roadmaps
```

## 📋 Documentation Lifecycle

1. **Active** → Current phase documentation
2. **Archive** → Completed phase documentation
3. **Prompts** → Important prompts, conversations, and architectural decisions saved for reference
4. **Todos** → Task tracking and completion status

## 🔄 Archive Rules

- Move to `archive/` when phase is complete
- Keep only active documentation in `active/`
- Archive with date prefix: `YYYY-MM-DD-filename.md`

## 📝 Current Status

### Sales Documentation

**Location:** `docs/sales/`

Sales team documentation has been organized into a dedicated folder:
- `SALES-GUIDE.md` - Satış ekibi kullanım kılavuzu (quick start, API endpoints, scenarios)
- `SALES-PERSONA-v2.0.md` - Satışçı persona dokümantasyonu (v2.0: "Sistematik Avcı" - **Hedef Durum**, v1.0: MVP - **Bugünkü Gerçeklik**)
- `SALES-TRAINING.md` - Satış ekibi eğitim materyali (modüller, pratik egzersizler)
- `SALES-SCENARIOS.md` - Pratik senaryolar ve en iyi pratikler
- `SEGMENT-GUIDE.md` - Segment ve skor açıklamaları (**Kanonik Segment-Priority Matrisi** - Single Source of Truth)
- `SALES-ENGINE-REAL-WORLD-SMOKE-1.md` - Sales Engine real-world smoke test results
- `PHASE-2-1-SOFT-TUNING.md` - Sales Engine soft tuning mechanism (Tuning Factor: Tasarım aşamasında, production UI yok)
- `SALES-ENGINE-EXPECTED-OUTPUTS.md` - Sales Engine expected output skeletons
- `REALITY-CHECK-2025-01-28.md` - Dokümantasyon vs gerçek uygulama uyumsuzlukları ve düzeltmeleri

**Documentation Consistency** (2025-01-28):
- ✅ Kanonik Segment-Priority Matrisi eklendi (SEGMENT-GUIDE.md)
- ✅ Cross-reference'lar eklendi (tüm sales docs → SEGMENT-GUIDE.md)
- ✅ v1.0 (MVP) vs v2.0 (Hedef) ayrımı netleştirildi
- ✅ Tuning Factor durumu açıklandı (tasarım aşamasında)

### API Documentation

**Location:** `docs/api/`

API contract documentation:
- `SALES-SUMMARY-V1-CONTRACT.md` - Sales Summary API v1 contract (stable, UI contract)

### Active Documentation

#### Core Status & Strategy Documents (v1.0)
- `GO-NO-GO-CHECKLIST-v1.0.md` - **Production Go/No-Go Checklist** - "Çıkabilir miyim?" sorusuna tek dosyadan cevap
- `HUNTER-STATE-v1.0.md` - **Sistem Durum Özeti** - Hunter v1.0'ın tek resmi durum dokümanı
- `G21-ROADMAP-CURRENT.md` - **G21 Architecture & Integration Roadmap** - Mimari refactor ve entegrasyon yol haritası (güncel durum)
- `POST-MVP-STRATEGY.md` - **Post-MVP Strategy** - v1.0 sonrası 3 ana iş paketi (IP Enrichment, Partner Center, Dynamics 365)

#### Reference Guides
**Location:** `docs/reference/`
- `DEVELOPMENT-ENVIRONMENT.md` - Development environment setup guide
- `WSL-GUIDE.md` - WSL2 setup and configuration guide
- `DOCKER-TROUBLESHOOTING.md` - Docker troubleshooting guide
- `IP-ENRICHMENT-DOCKER-SETUP.md` - IP enrichment Docker setup guide

#### Production Readiness Documentation
- `PRODUCTION-ENGINEERING-GUIDE-V1.md` - **Main SRE runbook** - Health checks, monitoring, deployment strategies (see Related Documents section for deployment guides)
- `PRODUCTION-DEPLOYMENT-GUIDE.md` - Step-by-step deployment guide
- `PRODUCTION-DEPLOYMENT-CHECKLIST.md` - Pre-deployment checklist
- `PRODUCTION-CHECKLIST-RUNBOOK.md` - Operational runbook (2-hour checklist)
- `PRODUCTION-MONITORING-WATCH.md` - Production monitoring watch guide (first 1-2 days after deployment)
- `ROLLBACK-PLAN.md` - Rollback procedures
- `SMOKE-TESTS-RUNBOOK.md` - Smoke tests runbook
- `TROUBLESHOOTING-GUIDE.md` - Troubleshooting guide
- `ENVIRONMENT-VARIABLES-CHECKLIST.md` - Environment variables checklist

#### Feature Documentation (Active)
- `SALES-ENGINE-V1.1.md` - Sales Engine v1.1 Intelligence Layer dokümantasyonu

#### Feature Documentation (Archived)
- ✅ **Archived** - `2025-01-29-CSP-COMMERCIAL-SEGMENT-DESIGN.md` - CSP Commercial Segment & Heat tasarımı (6 kategori, rule-based) - ✅ Completed (2025-01-29)

#### P1 Implementation Documentation
- ✅ **P1 Completed** (2025-01-28) - All P1 items completed
- ✅ **Archived** - `2025-01-28-P1-IMPLEMENTATION-PLAYBOOK.md` - P1 implementation guide (reference guide, archived)
- `KALAN-ISLER-PRIORITY.md` - P0/P1/P2 priority list and dependencies (✅ P0/P1 completed, P2 backlog)

#### Stabilization Sprint Documentation
- ✅ **Archived** - `2025-01-28-STABILIZATION-SPRINT-PLAN-v1.0.md` - Stabilization Sprint plan (3 gün) - ✅ Completed (2025-01-28)
- ✅ **Archived** - `2025-01-28-UI-STABILIZATION-CHECKLIST-v1.0.md` - UI stabilization checklist (Gün 3) - ✅ Completed (2025-01-28)

#### Integration Roadmap Documentation (NEW - 2025-01-28)
- `2025-01-28-INTEGRATION-ROADMAP-v1.0.md` - Integration Roadmap: Correct sequence for external integrations
  - **Phase 1**: ✅ Completed - Mini UI Stabilization (P0.5) - 1 day (All tasks ✅)
  - **Phase 2**: ✅ **COMPLETED** - Partner Center Referrals (P1) - 100% completed (2025-01-30)
    - ✅ Core components completed (Tasks 2.1, 2.2, 2.3)
    - ✅ **API Endpoints completed** (Task 2.4 - 2025-01-30) - `POST /api/referrals/sync` + Celery task
    - ✅ **Backend tests completed** (Task 2.4 - 2025-01-30) - 7/7 tests passing (endpoint + Celery task tests)
    - ✅ **UI Integration completed** (Task 2.5 - 2025-01-30) - Referral column with badges (co-sell: blue, marketplace: green, solution-provider: orange)
    - ✅ **Background Sync completed** (Task 2.6 - 2025-01-30) - Celery Beat schedule (10 min prod, 30s dev)
    - ✅ **All tests passing** (10/10 referral sync tests, 3/3 referral_type API tests)
    - ✅ **Preparation guide created** (2025-01-30) - `docs/active/PARTNER-CENTER-PREPARATION.md`
    - **Status**: ✅ **Phase 2 Complete** - Backend, UI, and background sync fully implemented and tested
    - **Feature Flag**: `partner_center_enabled=False` (disabled by default, MVP-safe)
    - **Remaining**: Scoring Pipeline Integration (Azure Tenant ID override + Co-sell boost) - Future enhancement
  - **Phase 3**: ⏳ Pending - Dynamics 365 Integration (P2) - 6-10 days
  - **Key Principle**: UI stability → Data ingestion → CRM integration
- `PARTNER-CENTER-PREPARATION.md` - **Partner Center Integration Preparation Guide** (2025-01-30) - Comprehensive preparation checklist for Tasks 2.4, 2.5, 2.6
- `2025-01-28-INTEGRATION-TASKS.md` - Exact task list with branch names and acceptance criteria
- `2025-01-28-INTEGRATION-VS-STABILIZATION-CRITIQUE.md` - Critique of integration vs stabilization approach
- `IP-ENRICHMENT-UI-PATCH-PLAN.md` - IP enrichment UI integration patch plan (minimal approach)

#### Test & Validation Documentation
- ✅ **Archived** - `2025-01-28-TEST-FIXES-COMPLETED.md` - Test fixes completion report (✅ Completed - 2025-01-28)
  - Fixed `dkim_none` risk penalty in test expectations
  - Fixed priority score ranges
  - All 86 scoring tests passing (0 failures)

#### Mini UI Documentation
- ✅ **Archived** - `2025-01-30-MINI-UI-REFACTOR-PACKAGE-1.md` - Mini UI Refactor Package 1 (Code quality improvements: escapeHtml refactor, constants extraction, domain validation) - ✅ Completed & Tested (2025-01-30)
- ✅ **Archived** - `2025-01-28-MINI-UI-POLISH-NOTES.md` - Mini UI v1.1 Polish - Dogfooding notes (7/10 tasks completed) - ✅ Archived (2025-01-28)
- ✅ **Archived** - `2025-01-28-TODO-MINI-UI-POLISH.md` - Mini UI Polish test results (✅ Passed) - ✅ Archived (2025-01-28)
- ✅ **Archived** - `2025-01-28-QA-NETWORK-TEST.md` - Network tab duplicate request tests - ✅ Archived (2025-01-28)
- `IP-ENRICHMENT-UI-PATCH-PLAN.md` (2025-01-28) - IP enrichment UI integration patch plan
  - Minimal approach: Country + proxy warning in score breakdown modal
  - IP context integration in sales engine for intelligent text generation
  - Status: ✅ Completed (2025-01-28)
- ✅ **Archived** - `2025-01-28-IP-ENRICHMENT-STATUS.md` - IP Enrichment validation status (ACCEPTED FOR MVP) - ✅ Archived (2025-01-28)
- ✅ **Archived** - `2025-01-28-IP-ENRICHMENT-VALIDATION-CHECKLIST.md` - IP Enrichment validation checklist - ✅ Archived (2025-01-28)
- ✅ **Archived** - `2025-01-28-IP-ENRICHMENT-VALIDATION-RESULTS.json` - IP Enrichment validation test results (11 domains) - ✅ Archived (2025-01-28)
  - IP resolution results (11/11 success), enrichment results (11/11 success)
  - Status: ✅ Test completed (full results with enrichment enabled)
- `2025-01-28-GOLDEN-DATASET-CRITIQUE.md` (2025-01-28) - Critique of current "golden dataset"
  - Analysis: Current dataset is silver-level regression set, not ground truth
  - Action: Renamed to regression dataset, blueprint created for true golden dataset
  - Status: ✅ Completed
- `2025-01-28-GOLDEN-DATASET-v1.0-BLUEPRINT.md` (2025-01-28) - Golden Dataset v1.0 Blueprint
  - JSON schema for real-world validation dataset
  - Data collection pipeline plan (passive mode)
  - Human validation process
  - Versioning strategy
  - Status: 📋 Blueprint ready, implementation pending

#### Architecture Refactor Documentation
- `G21-ROADMAP-CURRENT.md` - **G21 Architecture & Integration Roadmap (Current State)** - Tek güncel referans noktası
  - Phase 0-3: ✅ Completed
  - Phase 4: ⏸ Paused (Dynamics Migration)
  - Phase 5-6: ◻ Pending
- `NO-BREAK-REFACTOR-PLAN.md` - No-Break Refactor Plan: Hunter Architecture Slimming (G21) - Detaylı uygulama planı
  - **Phase 0**: ✅ Completed (2025-11-16) - Preparation & Snapshot
  - **Phase 1**: ✅ Completed (2025-11-16) - Deprecation Annotations
  - **Phase 2**: ✅ Completed (2025-01-28) - Sales Engine (Additive)
  - **Phase 3**: ✅ Completed (2025-01-28) - Read-Only Mode (Write endpoints disabled - 410 Gone)
  - **Phase 4**: 🔄 PAUSED - Dynamics Migration (overlaps with Integration Roadmap Phase 3)
- `docs/g21-phase0-metrics/` - G21 Phase 0 & Phase 1 metrics and completion reports
  - `PHASE0-COMPLETION.md` - Phase 0 completion report (2025-11-16)
  - `PHASE1-COMPLETION.md` - Phase 1 completion report (2025-11-16)
  - `DEPENDENCY-MAP.md` - Dependency analysis for Notes/Tags/Favorites endpoints
  - `usage_metrics_*.json` - Usage metrics collection data

**Note:** Active documentation contains reference guides, production readiness documentation, and current priority/planning documents. Completed sprint plans and implementation playbooks have been moved to `archive/`. Sales Engine documentation has been moved to `docs/sales/`. Planning documentation is in `plans/`.

**Current Project Status:**
- ✅ **v1.0.0 Production-Ready**: Core engine production-ready (2025-01-28)
  - **Status Document**: `HUNTER-STATE-v1.0.md` - Tek resmi durum özeti
  - **Go/No-Go Checklist**: `GO-NO-GO-CHECKLIST-v1.0.md` - Tüm Must-Have maddeler ✅
- ✅ P0 Hardening: Completed (G19)
- ✅ P1 Performance: Completed (2025-01-28)
- ✅ Stabilization Sprint: Completed (2025-01-28) - v1.1-stable (Enterprise-Ready / UI-Stable / Integration-Ready)
- ✅ **Test Fixes**: Completed (2025-01-28) - Scoring engine fully validated (86 tests passing, 0 failures)
- 🔄 **G21 Architecture Refactor**: Phase 0-3 Completed, Phase 4-6 Pending
  - **Roadmap**: `G21-ROADMAP-CURRENT.md` - Tek güncel referans noktası
  - ✅ Phase 0: Preparation & Snapshot (2025-11-16)
  - ✅ Phase 1: Deprecation Annotations (2025-11-16)
  - ✅ Phase 2: Sales Engine (2025-01-28)
  - ✅ Phase 3: Read-Only Mode (2025-01-28) - Write endpoints disabled (410 Gone)
  - ⏸ Phase 4: Dynamics Migration (PAUSED - overlaps with Integration Roadmap Phase 3)
  - ◻ Phase 5-6: Monitoring & Cleanup (Pending)
- 📋 **Post-MVP Strategy**: `POST-MVP-STRATEGY.md` - 3 ana iş paketi
  1. IP Enrichment (G20) - Derinlik
  2. Partner Center Referrals Sync - Kaynak
  3. Dynamics 365 Sales Integration - Pipeline
- ✅ **Integration Roadmap**: Phase 2 Complete (2025-01-30) - Correct sequence for external integrations
  - ✅ Phase 1: Mini UI Stabilization (P0.5) - Completed (1 day)
  - ✅ Phase 2: Partner Center Referrals (P1) - **Completed** (Branch: feature/partner-center-phase1, opened 2025-01-29, completed 2025-01-30)
    - ✅ Core components completed (Tasks 2.1, 2.2, 2.3)
    - ✅ **API Endpoints completed** (Task 2.4 - 2025-01-30) - `POST /api/referrals/sync` + Celery task
    - ✅ **Backend tests completed** (Task 2.4 - 2025-01-30) - 7/7 tests passing
    - ✅ **UI Integration completed** (Task 2.5 - 2025-01-30) - Referral column with badges
    - ✅ **Background Sync completed** (Task 2.6 - 2025-01-30) - Celery Beat schedule
    - ✅ **Phase 4-6 Productization** (2025-01-30) - DB schema revision, filter rules, upsert strategy, summary logging, comprehensive tests (49 tests passing)
    - ✅ **All tests passing** (49/49 tests: 30 domain extraction + 7 Phase 4 + 6 client + 6 Phase 5/6)
    - **Status**: ✅ **Phase 2 Complete** - Backend, UI, background sync, and productization fully implemented
    - **Feature Flag**: `partner_center_enabled=False` (disabled by default, MVP-safe)
    - **Remaining**: Scoring Pipeline Integration (Future enhancement)
  - ⏳ Phase 3: Dynamics 365 Integration (P2) - Pending (6-10 days)
- 📋 P2 Backlog: Sync-first refactor, Repository pattern, N+1 query prevention

### Archived Documentation
- **CSP P-Model Implementation** (2025-01-29) - ✅ **FINAL & CLOSED**
  - `2025-01-29-CSP-P-MODEL-IMPLEMENTATION-PLAN.md` - CSP P-Model entegrasyon planı (Phase 1, 2 & 3 completed - Production v1.1 Core Feature)
  - `2025-01-29-CSP-COMMERCIAL-SEGMENT-DESIGN.md` - CSP Commercial Segment & Heat tasarımı (6 kategori, rule-based)
  - `2025-01-29-DMARC-CACHE-FIX.md` - DMARC cache bug fix (analyzer_dns.py, cache invalidation)
  - `2025-01-29-DMKIMYA-ANALYSIS.md` - dmkimya.com.tr domain analysis (P-Model validation)
  - `2025-01-29-DMKIMYA-BUG-FIXES.md` - Bug fixes documentation (3 bugs fixed: DMARC coverage, risk summary, score modal)
  - `2025-01-29-FRESH-TEST-MANUAL-GUIDE.md` - Fresh test manual guide (DB reset & verification)
  - `2025-01-29-FRESH-TEST-RESULTS.md` - Fresh test results (all tests passed ✅)
  - `2025-01-29-PRODUCTION-READINESS-CHECKLIST-2025-01-29.md` - Production readiness checklist (✅ DONE & PROD-READY)
  - `2025-01-29-PRODUCTION-UAT-GUIDE-2025-01-29.md` - Production UAT guide (✅ DONE & PROD-READY)
- **Script Safety Guards** (2025-01-30) - ✅ **IMPLEMENTED**
  - Production database reset protection
  - Production deployment guards
  - Backup integrity checks
  - Script logging for audit trail
  - Reference: `docs/reference/PRODUCTION-DEPLOYMENT-GUIDE.md` (Safety Guards section)
- `2025-01-28-DEPLOYMENT-READY-SUMMARY.md` - Deployment ready summary (Completed - 2025-01-28)
- `2025-01-28-24-SAATLIK-YOL-HARITASI.md` - 24-hour roadmap analysis (Completed - 2025-01-28)
- `2025-01-28-ALEMBIC-MIGRATION-PLAN.md` - Alembic migration plan (P1 completed - 2025-01-28)
- `2025-01-27-MVP-TRIMMED-ROADMAP.md` - 10-day implementation roadmap (Completed)
- `2025-11-12-G1-foundation.md` - G1: Foundation & Docker Setup (Completed)
- `2025-11-12-G2-database-schema.md` - G2: Database Schema & Models (Completed)
- `2025-11-12-G3-domain-normalization.md` - G3: Domain Normalization & Data Files (Completed)
- `2025-01-27-G11-importer-email.md` - G11-G13: Importer + Email Module Implementation (Completed)
  - G11: Importer Module - Excel/CSV column auto-detection
  - G12: Email Generator - Generic email generation
  - G13: Email Validator - Light email validation (syntax, MX, optional SMTP)
- `2025-11-14-G14-post-mvp-sprint1.md` - G14: Post-MVP Sprint 1: CSV Export + UI Mini (Completed)
- `2025-11-14-G15-bulk-scan-async.md` - G15: Sprint 2: Bulk Scan & Async Queue (Completed)
- `2025-11-14-G16-webhook-enrichment.md` - G16: Sprint 3: Webhook + Basit Lead Enrichment (Completed)
- `2025-11-14-G17-notes-tags-pdf.md` - G17: Sprint 4: Notes/Tags/Favorites + Basit PDF (Completed)
- `2025-11-14-G18-rescan-alerts-scoring.md` - G18: Sprint 5: ReScan + Alerts + Enhanced Scoring (Completed)
- `2025-11-15-G19-auth-ui-advanced.md` - G19: Sprint 6: UI Upgrade (✅ Completed - 2025-11-15) - **Note**: SSO removed (2025-01-28), switched to Internal Access Mode
- `2025-11-15-G19-AZURE-AD-SETUP.md` - G19: Azure AD Setup Guide (Archived - SSO removed 2025-01-28)
- `2025-11-15-G19-IMPLEMENTATION-PLAN.md` - G19: Implementation Plan (Archived - SSO removed 2025-01-28)
- `2025-11-15-G19-TEST-SUMMARY.md` - G19: Test Summary (Archived - SSO removed 2025-01-28)
- `2025-01-28-PROVIDER-CHANGE-TRACKING.md` - Provider Change Tracking feature documentation (Completed)
- `2025-01-28-DOMAIN-VALIDATION.md` - Domain Validation feature documentation (Completed)
- `2025-01-28-DUPLICATE-PREVENTION.md` - Duplicate Prevention feature documentation (Completed)
- `2025-01-28-IP-ENRICHMENT-IMPLEMENTATION.md` - IP Enrichment feature documentation (Completed - 2025-01-28)
  - Complete implementation guide with configuration, testing checklist, deployment strategy
  - Feature flag: `HUNTER_ENRICHMENT_ENABLED` (default: `false`)
  - No-break upgrade design - can be deployed with flag disabled
  - **Configuration** (2025-01-28): Simplified env format (`MAXMIND_CITY_DB`, `MAXMIND_COUNTRY_DB`, `IP2LOCATION_DB`, `IP2PROXY_DB`)
  - **Country DB Support** (2025-01-28): Optional `GeoLite2-Country.mmdb` as fallback for country-only lookups
  - **Backward Compatible**: Legacy format (`HUNTER_ENRICHMENT_DB_PATH_*`) still supported
  - **Level 1 Exposure** (2025-01-28): `infrastructure_summary` field in `/leads` and `/lead/{domain}` API responses
    - Human-readable summary: "Hosted on DataCenter, ISP: Hetzner, Country: DE"
    - Usage type mapping: DCH → DataCenter, COM → Commercial, RES → Residential, MOB → Mobile
    - Backward compatible: Optional field (None if no enrichment data available)
- `2025-01-28-IP-ENRICHMENT-QUICK-START.md` - IP Enrichment quick setup guide (Completed - 2025-01-28)
  - Step-by-step guide for downloading DB files and enabling enrichment
  - 10-minute setup: Download DB files → Place in project → Update .env (new format) → Restart
  - New env format: `MAXMIND_CITY_DB`, `MAXMIND_COUNTRY_DB`, `IP2LOCATION_DB`, `IP2PROXY_DB`
  - Country DB setup instructions (optional fallback)
  - Troubleshooting guide and verification checklist
- `2025-01-28-STABILIZATION-SPRINT-PLAN-v1.0.md` - Stabilization Sprint plan (3 gün) - ✅ Completed (2025-01-28)
- `2025-01-28-UI-STABILIZATION-CHECKLIST-v1.0.md` - UI stabilization checklist - ✅ Completed (2025-01-28)
- `2025-01-28-P1-IMPLEMENTATION-PLAYBOOK.md` - P1 implementation playbook (reference guide) - ✅ Completed (2025-01-28)
- `2025-01-28-P1-BULK-OPERATIONS-PREPARATION.md` - P1-4: Bulk Operations Optimization preparation (✅ Completed - 2025-01-28)
- `2025-01-28-G19-PRE-FLIGHT-CHECKLIST.md` - G19 Pre-Flight Checklist: Production Hardening (✅ Completed - 2025-01-28)
- `2025-11-15-G19-PRE-FLIGHT-CHECKLIST.md` - G19 Pre-Flight Checklist: Production Hardening (✅ Completed - 2025-11-15)
- `2025-01-28-TEST-COVERAGE-ANALYSIS.md` - Test coverage analysis report (Archived)
- `2025-01-28-TESTING.md` - Testing guide and troubleshooting (Archived)
- `2025-01-27-DOCUMENTATION-RULES-UPDATE-SUMMARY.md` - Documentation rules update summary (Archived - 2025-01-27)
- `2025-01-27-DOCUMENTATION-STATUS-ANALYSIS.md` - Kapsamlı dokümantasyon durum analizi (Archived - 2025-01-27)
- `2025-01-27-DOCUMENTATION-READINESS-REPORT.md` - Documentation readiness report (Archived - 2025-01-27)
- `2025-01-27-LOGGING-GOLDEN-SAMPLES.md` - Logging golden samples (Archived - 2025-01-27)
- `2025-01-27-LOGGING-SMOKE-TEST.md` - Logging smoke test (Archived - 2025-01-27)
- `2025-01-27-ACTIVE-DOCS-SUMMARY.md` - Active documentation summary (Archived - 2025-01-27)
- `2025-01-27-TEST-ANALYSIS.md` - Test suite analysis report (Archived - 2025-01-27)
- `2025-01-28-APPLICATION-STATUS.md` - Application health status report (Archived - 2025-01-28)
- `2025-01-28-IP-ENRICHMENT-STATUS.md` - IP Enrichment validation status (ACCEPTED FOR MVP) - ✅ Archived (2025-01-28)
- `2025-01-28-IP-ENRICHMENT-VALIDATION-CHECKLIST.md` - IP Enrichment validation checklist - ✅ Archived (2025-01-28)
- `2025-01-28-IP-ENRICHMENT-VALIDATION-RESULTS.json` - IP Enrichment validation test results (11 domains) - ✅ Archived (2025-01-28)
- `2025-01-28-MINI-UI-POLISH-NOTES.md` - Mini UI v1.1 Polish - Dogfooding notes (7/10 tasks completed) - ✅ Archived (2025-01-28)
- `2025-01-28-TODO-MINI-UI-POLISH.md` - Mini UI Polish test results (✅ Passed) - ✅ Archived (2025-01-28)
- `2025-01-28-QA-NETWORK-TEST.md` - Network tab duplicate request tests - ✅ Archived (2025-01-28)
- `2025-11-12-PATCH-SUGGESTIONS.diff` - Plan patch suggestions (archived)
- `2025-11-12-ACTIONS.json` - Implementation action items (all completed, archived)
- `2025-11-12-test-google-domain.sh` - Temporary test script (archived)
- `2025-11-12-demo-script.sh` - Demo script (archived)

**Note:** 
- All MVP phases (G1-G10) are completed (see CHANGELOG.md for details)
- MVP scope features (Dashboard, Priority Score) completed in v0.4.0
- Phase documentation for G4-G10 was not created as separate TODO files, but all work is documented in CHANGELOG.md
- G11-G13 (Importer + Email modules) completed in 2025-01-27

### Important Prompts & Decisions
- `2025-11-12-initial-setup.md` - Initial project setup
- `2025-11-12-alembic-decision.md` - [DECISION] Alembic migration approach
- `2025-11-12-phase-completion-workflow.md` - Phase completion workflow enhancement
- `2025-01-28-hunter-architecture-refactor-decision.md` - [DECISION] Hunter Architecture Refactor - Slimming to core signal engine

### Project Plans

**Active Plans:**
- (No active plans - All sprints completed, see KALAN-ISLER-PRIORITY.md for current backlog)

**Archived Plans:**
All completed planning documentation has been moved to `docs/archive/`:
- `2025-01-28-FINAL-ROADMAP.md` - **Final Roadmap - Post-MVP Sprint 2-6 (G15-G19)** - All sprints completed (✅ G15-G19 completed)
- `2025-01-27-phase0-hotfix-scoring.md` - Phase 0: Enhanced Scoring & Hard-Fail Rules (Completed)
- `2025-01-27-SALES-FEATURE-REQUESTS.md` - Sales team feature requests (Completed)
- `2025-01-27-SALES-FEATURE-REQUESTS-CRITIQUE.md` - Technical review of feature requests (Completed)
- `2025-01-27-IMPORTER-EMAIL-IMPLEMENTATION-PLAN.md` - Importer + Email Module Implementation Plan (Completed)
- `2025-01-27-IMPORTER-EMAIL-MODULE-CRITIQUE.md` - Design critique and alternative approaches (Completed)
- `2025-01-28-POST-MVP-SPRINT1-PLAN.md` - Post-MVP Sprint 1: CSV Export + UI Mini (Completed)
- `2025-01-28-MINI-UI-IMPLEMENTATION-PLAN.md` - Mini UI Implementation Plan (Completed)
- `2025-01-28-MINI-UI-CRITIQUE.md` - Mini UI Approach Critique and Alternatives (Completed)
- `2025-11-14-ROADMAP-CRITIQUE.md` - Critical evaluation of Sprint 2-6 roadmap (Completed)

### TODOs

**Active TODOs:**
- `INTEGRATION-ROADMAP.md` - Integration Roadmap: UI Stabilization → Partner Center → Dynamics 365 - 🔄 In Progress (2025-01-28)
  - **Phase 1**: ✅ Completed - Mini UI Stabilization (P0.5) - 1 day
  - **Phase 2**: ✅ Completed - Partner Center Referrals (P1) - 2-3 days (2025-01-30)
  - **Phase 3**: ⏳ Pending - Dynamics 365 Integration (P2) - 6-10 days
- `PARTNER-CENTER-PHASE2.md` - Partner Center Phase 2 - ✅ **COMPLETED** (2025-01-30) - All tasks completed (2.1-2.6), all tests passing
- `G21-architecture-refactor.md` - G21: Architecture Refactor - Hunter Slimming - 🔄 In Progress (2025-01-28)

**Archived TODOs:**
All completed TODO files have been moved to `docs/archive/`:
- `2025-01-27-G11-importer-email.md` - G11-G13: Importer + Email Module Implementation (✅ Completed)
- `2025-11-14-G14-post-mvp-sprint1.md` - G14: Post-MVP Sprint 1: CSV Export + UI Mini (✅ Completed)
- `2025-11-14-G15-bulk-scan-async.md` - G15: Sprint 2: Bulk Scan & Async Queue (✅ Completed)
- `2025-11-14-G16-webhook-enrichment.md` - G16: Sprint 3: Webhook + Basit Lead Enrichment (✅ Completed)
- `2025-11-14-G17-notes-tags-pdf.md` - G17: Sprint 4: Notes/Tags/Favorites + Basit PDF (✅ Completed)
- `2025-11-14-G18-rescan-alerts-scoring.md` - G18: Sprint 5: ReScan + Alerts + Enhanced Scoring (✅ Completed)
- `2025-11-15-G19-auth-ui-advanced.md` - G19: Sprint 6: UI Upgrade (✅ Completed - 2025-11-15) - **Note**: SSO removed (2025-01-28), switched to Internal Access Mode

**P1 Implementation Status:**
- `P1-PREPARATION.md` - P1 Preparation (Pre-Implementation) - ✅ Completed (2025-01-28)
  - All 5 preparation documents created (Alembic, Caching, Rate Limiting, Bulk Operations, API Versioning)
- **P1-1: Alembic Migration** - ✅ Core Implementation Completed (2025-01-28)
- **P1-2: Distributed Rate Limiting** - ✅ Core Implementation Completed (2025-01-28)
- **P1-3: Caching Layer** - ✅ Core Implementation Completed (2025-01-28)
- **P1-4: Bulk Operations Optimization** - ✅ Core Implementation Completed (2025-01-28)
  - Batch size calculation (rate-limit aware) - Optimal batch size based on DNS/WHOIS rate limits
  - Batch commit optimization - Reduces transaction overhead
  - Deadlock prevention - Transaction timeout and retry logic with tenacity
  - Partial commit log - Redis-based recovery mechanism
  - Batch isolation - One batch failure doesn't affect other batches
  - Bulk log context - Structured logging with batch information
  - Implementation files: `app/core/bulk_operations.py`, `app/core/tasks.py`
  - Test coverage: `tests/test_bulk_operations_p1.py` (13 tests)
  - Documentation: `docs/active/P1-ALEMBIC-STATUS.md`

