# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Production Ready
- **CSP P-Model Integration + Sales Summary v1.1** (2025-01-29) - ✅ **DONE & PROD-READY**
  - **Core Engine**: ✅ Domain analysis, scoring, provider classification, segment determination
  - **CSP P-Model**: ✅ Phase 1-3 completed (Core Logic → DB + API → UI)
  - **DMARC/DNS/Cache**: ✅ All side-effects fixed (DMARC coverage, cache invalidation, rescan pipeline)
  - **Sales Summary v1.1**: ✅ Intelligence Layer with reasoning capabilities, UX polished
  - **Feature Flags**: No feature flags needed - Core features (always enabled)
  - **Pre-Production Checklist**: See `docs/active/PRODUCTION-READINESS-CHECKLIST-2025-01-29.md`
    - Feature flag verification (no flags needed - core features)
    - Golden-domain UAT (4 domains: gibibyte.com.tr, dmkimya.com.tr, P1 local/hosting, P3 weak-partner M365)
    - Monitoring verification (score_domain, sales_summary events, P-Model field logging)
  - **Status**: Ready for production UAT and deployment

### Fixed
- **leads_ready View Missing G20 Columns** (2025-01-29) - Fixed `leads_ready` view missing `tenant_size`, `local_provider`, and `dmarc_coverage` columns
  - Updated `leads_ready` view to include all G20 columns (`tenant_size`, `local_provider`, `dmarc_coverage`) and CSP P-Model columns
  - Updated API query to SELECT G20 columns from view (removed `getattr()` workaround)
  - Updated database reset script (`scripts/reset_db_with_alembic.sh`) to create view with all G20 columns
  - **Impact**: UI now correctly displays tenant size, local provider, and DMARC coverage in lead list
  - **Root Cause**: View was created without G20 columns during database reset
  - **Solution**: View now includes all G20 columns and CSP P-Model columns
  - Files: `app/api/leads.py`, `scripts/reset_db_with_alembic.sh`
  - Status: ✅ **Fixed and verified** - Tenant size now visible in UI lead list
- **DMARC Coverage Bug Fix** (2025-01-29) - Fixed DMARC coverage inconsistency between Score Breakdown and Sales Summary
  - Fixed `analyzer_dns.py` to return `None` for `dmarc_coverage` when no DMARC record exists (was incorrectly defaulting to 100)
  - Added cache invalidation in rescan pipeline (`use_cache=False` for fresh DNS data)
  - Fixed `domain_signals` table persistence during rescan
  - Files: `app/core/analyzer_dns.py`, `app/core/rescan.py`, `app/core/cache.py`
  - Script: `scripts/invalidate_scoring_cache.py` for manual cache invalidation
  - Status: ✅ **Fixed and verified** - All tests passing, DMARC coverage now consistent across all endpoints
- **Risk Summary Text Fix** (2025-01-29) - Fixed contradictory risk summary text in Sales Summary
  - Updated `explain_security_signals()` to accurately reflect SPF/DKIM status when DMARC is missing
  - Now correctly states "SPF ve DKIM mevcut" when both are present (was incorrectly saying "eksik")
  - Added 3-branch logic: SPF+DKIM present, one present, or none present
  - File: `app/core/sales_engine.py`
  - Status: ✅ **Fixed and verified** - Risk summary now accurate and consistent
- **Score Modal Description Fix** (2025-01-29) - Made score breakdown modal description provider-specific
  - Updated `showScoreBreakdown()` to dynamically generate description based on detected provider
  - M365 → "M365 kullanımı, DNS ve IP verilerine göre hesaplandı"
  - Google → "Google Workspace kullanımı, DNS ve IP verilerine göre hesaplandı"
  - Local/Hosting → "mevcut email sağlayıcınız, DNS ve IP verilerine göre hesaplandı"
  - File: `mini-ui/js/ui-leads.js`
  - Status: ✅ **Fixed and verified** - Description now accurate for each provider type

### Added
- **CSP P-Model Integration** (2025-01-29) - Global CSP Priority Model (P1-P6) implementation ✅ **FINAL & CLOSED (Production v1.1 Core Feature)**
  - Commercial Segment & Heat calculation - 6 commercial segments (GREENFIELD, COMPETITIVE, WEAK_PARTNER, RENEWAL, LOW_INTENT, NO_GO)
  - Technical Heat calculation - Hot/Warm/Cold classification based on technical segment and provider
  - Priority Category (P1-P6) - CSP-standard priority categories with human-readable labels
  - Rule-based architecture - All rules in `app/data/rules.json` (maintainable, configurable)
  - Database migration - New columns in `lead_scores` table: `technical_heat`, `commercial_segment`, `commercial_heat`, `priority_category`, `priority_label`
  - API response updates - New fields in `LeadResponse` and `ScoreBreakdownResponse` models (backward compatible, optional fields)
  - Core modules: `app/core/commercial.py`, `app/core/technical_heat.py`, `app/core/priority_category.py`
  - Integration: `app/core/scorer.py` updated to calculate CSP P-Model fields
  - Database: Alembic migration `f786f93501ea_add_csp_p_model_fields.py`
  - View update: `leads_ready` view updated to include new CSP P-Model fields
  - UI updates (Phase 3 - 2025-01-29): P1-P6 badge'leri (renk kodlu), priority_label tooltip'leri, score breakdown modalında P-model paneli
    - Lead listesinde P-Model priority badges (P1-P6 renkli badge'ler, priority_label tooltip'leri)
    - Score breakdown modal'da CSP P-Model paneli (technical_heat, commercial_segment, commercial_heat, priority_category, priority_label)
    - Provider-specific açıklama cümlesi (M365, Google, Local/Hosting için dinamik)
    - DMARC coverage null/undefined handling (DMARC yoksa gösterilmiyor)
  - CSS: P-badge stilleri eklendi (P1-P6 için renk kodları: P1=green, P2=red, P3=blue, P4=orange, P5=yellow, P6=gray)
  - Files: `mini-ui/js/ui-leads.js`, `mini-ui/styles.css`, `mini-ui/README-mini-ui.md`, `mini-ui/TEST-CHECKLIST.md`
  - Tested: Migration successful, API response verified, DB columns populated correctly, UI tested, all bug fixes verified
  - Documentation: `docs/active/CSP-COMMERCIAL-SEGMENT-DESIGN.md`, `docs/archive/2025-01-29-CSP-P-MODEL-IMPLEMENTATION-PLAN.md`
  - Status: ✅ **Phase 1 (Core Logic) + Phase 2 (DB + API) + Phase 3 (UI) completed** - Production v1.1 Core Feature
  - Post-MVP: Filtering & sorting (priority_category, commercial_segment) - İleride eklenecek
- **Sales Engine v1.1 - Intelligence Layer** (2025-01-28) - Reasoning capabilities for sales intelligence ✅ **COMPLETED + UX POLISHED**
  - Segment Explanation Engine - Explains why a lead belongs to a segment (Migration, Existing, Cold, Skip)
  - Provider Reasoning Layer - Explains why a provider is classified as M365/Google/Hosting/Local/Unknown
  - Security Signals Reasoning - Risk assessment (high/medium/low) with sales angle and recommended action
  - Cold Segment Call Script v1.1 - Soft, discovery-focused script for Cold leads
  - Opportunity Rationale - Explains why opportunity_potential is X (calculation breakdown with factors)
  - Next-step CTA - Clear, actionable next step recommendation (action, timeline, priority, message, internal_note)
  - API fields added: `segment_explanation`, `provider_reasoning`, `security_reasoning`, `opportunity_rationale`, `next_step` (all optional, backward-compatible)
  - 50+ new unit tests added, all passing
  - Documentation: `docs/active/SALES-ENGINE-V1.1.md`
  - API Contract: `docs/api/SALES-SUMMARY-V1-CONTRACT.md` (updated to v1.1.0)
  - **UX Polish (P1.5)** - Sales-ready UI improvements:
    - Security risk badges: "YÜKSEK RİSK" / "ORTA RİSK" / "DÜŞÜK RİSK" (Turkish labels)
    - Security section: 3-block layout (Risk Özeti, Teknik Durum, Satış Açısı + Aksiyon)
    - Provider section: "Mevcut Sağlayıcı Değerlendirmesi" (more professional title)
    - Next Step CTA: Pill-style badges ([ARAMA] [3 gün içinde] [Orta Öncelik])
    - Improved visual hierarchy and readability
  - Status: ✅ **6/6 features completed + UX polished** - Sales Engine v1.1 production-ready
- **IP Enrichment Production Activation** (2025-01-28) - G20 IP Enrichment feature activated in production
  - Feature flag enabled: `HUNTER_ENRICHMENT_ENABLED=true`
  - All DB files configured and validated (MaxMind, IP2Location, IP2Proxy)
  - API validation complete: `infrastructure_summary` field working in `/leads` endpoints
  - Debug endpoints validated: `/debug/ip-enrichment/config` and `/debug/ip-enrichment/{ip}`
  - Basic monitoring in place (health checks, Sentry, structured logging)
  - Documentation updated: Environment variables checklist, Hunter state, Post-MVP strategy

### Planned (Post-MVP)
- **Partner Center Integration - Phase 2** (🅿️ Parked) - API endpoints, background sync, UI integration, scoring pipeline integration
- **Dynamics 365 Integration - Phase 3** - CRM integration with two-way sync
- **G21 Phase 4-6** - Dynamics migration, monitoring, cleanup

---

## [1.0.0] - 2025-01-28

### 🎉 Production Release

Hunter v1.0 is the first production-ready release. This version includes all core functionality, performance optimizations, and enterprise-grade features required for production deployment.

### Added
- **Production Deployment Infrastructure**
  - Production deployment script (`scripts/deploy_production.sh`)
  - Environment variables checklist (`docs/active/ENVIRONMENT-VARIABLES-CHECKLIST.md`)
  - Alembic migration plan (`docs/active/ALEMBIC-MIGRATION-PLAN.md`)
  - Rollback plan (`docs/active/ROLLBACK-PLAN.md`)
  - Production deployment guide (`docs/active/PRODUCTION-DEPLOYMENT-GUIDE.md`)
  - Production checklist runbook (`docs/active/PRODUCTION-CHECKLIST-RUNBOOK.md`)
  - Smoke tests runbook (`docs/active/SMOKE-TESTS-RUNBOOK.md`)
  - Troubleshooting guide (`docs/active/TROUBLESHOOTING-GUIDE.md`)

### Enhanced
- **Production Readiness** (G19 - P0 Hardening)
  - Database connection pooling (20 connections, 10 overflow)
  - API key security (bcrypt hashing)
  - Structured logging with PII masking
  - Error tracking (Sentry integration)
  - Health checks & probes (liveness/readiness/startup)

- **Performance Optimizations** (P1 - 2025-01-28)
  - Alembic migration system (collapsed history strategy)
  - Distributed rate limiting (Redis-based, multi-worker support)
  - Caching layer (DNS/WHOIS/Provider/Scoring - Redis-based)
  - Bulk operations optimization (batch processing, deadlock prevention)
  - API versioning (v1 + legacy backward compatibility)

- **Stabilization Sprint** (3 days - 2025-01-28)
  - Core stabilization (Alembic drift check, multi-worker rate limiting test)
  - Monitoring & metrics (cache hit metrics, rate limit metrics, error trend logging)
  - UI stabilization (table view cleanup, score breakdown modal, export/PDF basic)

- **Sales Engine** (G21 Phase 2 - 2025-01-28)
  - Sales intelligence layer (`app/core/sales_engine.py`)
  - Sales summary endpoint (`GET /api/v1/leads/{domain}/sales-summary`)
  - Features: One-liner, call script, discovery questions, offer tier, opportunity potential, urgency
  - 45 tests (38 core + 7 API), all passing
  - Real-world validation completed (3 domains tested)

- **Read-Only Mode** (G21 Phase 3 - 2025-01-28)
  - Write endpoints disabled (7 endpoints return 410 Gone)
  - Deprecated endpoint monitoring
  - Read endpoints verified (3 read endpoints still work)
  - Metrics integration (`/healthz/metrics`)

### Changed
- **Authentication**: Removed Microsoft SSO, switched to Internal Access Mode (network-level access control)
- **API Structure**: Added v1 API versioning (`/api/v1/*`) with backward compatibility
- **Migration System**: Migrated from manual SQL migrations to Alembic (collapsed history strategy)

### Fixed
- **Scoring Engine**: Fixed test failures, all 86 tests passing (0 failures)
- **Test Suite**: Improved test isolation, transaction-based fixtures
- **UI**: Fixed modal bugs, loading states, filter bar UX

### Security
- API key authentication with bcrypt hashing
- PII masking in logs
- Structured error tracking (Sentry)

### Documentation
- Production deployment documentation complete
- Troubleshooting guide added
- Runbooks for production operations
- Environment variables checklist

### Testing
- 86 scoring tests passing (0 failures)
- 497 total tests in suite
- Smoke tests runbook prepared
- Production checklist runbook prepared

### Notes
- **Partner Center Integration**: Feature flag disabled by default (Post-MVP)
- **IP Enrichment**: Feature flag disabled by default (optional feature)
- **G21 Phase 4**: Dynamics Migration paused, will merge with Integration Roadmap Phase 3 (Post-MVP)

---

## [Unreleased] (Pre-v1.0)

### Added
- **Partner Center Integration - Phase 2** (2025-01-28) - Partner Center referral ingestion and lifecycle tracking
  - **Config**: Added Partner Center feature flag and OAuth configuration (`app/config.py`)
    - Feature flag: `partner_center_enabled` (disabled by default)
    - OAuth settings: Client ID, Tenant ID, API URL, scope, token cache path
    - Scoring settings: Co-sell bonus (+15), Azure Tenant score (55)
  - **API Client**: Minimal Partner Center API client (`app/core/partner_center.py`)
    - MSAL + Device Code Flow authentication (delegated permissions support)
    - `get_referrals()` function with basic rate limiting (`time.sleep(1)`)
    - Basic retry logic (2 attempts for transient failures)
    - Token expiry handling with silent token acquisition
    - Structured logging with PII masking
    - MVP approach: 50-70 lines minimal client
  - **Database Model**: Partner Center referral tracking (`app/db/models.py`)
    - `PartnerCenterReferral` model with lifecycle tracking
    - Fields: `referral_id` (unique), `referral_type`, `domain`, `azure_tenant_id`, `status`, `raw_data`
    - Indexes: domain, status, synced_at, referral_type, azure_tenant_id
    - Hybrid model: `raw_leads` ingestion + `partner_center_referrals` tracking
  - **Migration**: Alembic migration for `partner_center_referrals` table
    - Migration file: `alembic/versions/XXXX_add_partner_center_referrals.py`
    - Supports upgrade/downgrade operations
  - **Referral Ingestion**: Complete referral processing pipeline (`app/core/referral_ingestion.py`)
    - Lead type detection (Co-sell, Marketplace, Solution Provider)
    - Domain extraction fallback chain (website → email → skip)
    - Azure Tenant ID signal (Company.provider='M365' override during ingestion)
    - `raw_leads` ingestion (source='partnercenter', payload JSONB)
    - `partner_center_referrals` tracking (referral lifecycle)
    - Company upsert with provider override
    - Idempotent domain scan trigger (domain-based, not referral-based)
    - Independent referral processing (one error doesn't affect others)
    - `sync_referrals_from_partner_center()` main sync function
  - **Status**: ✅ Core components completed (Tasks 2.1, 2.2, 2.3)
  - **Next Steps**: API endpoints, background sync, UI integration, scoring pipeline integration
  - **Files Created**: `app/core/partner_center.py`, `app/core/referral_ingestion.py`
  - **Files Modified**: `app/config.py`, `app/db/models.py`
  - **Documentation**: `docs/todos/PARTNER-CENTER-PHASE2.md` - Complete task list and progress tracking

### Enhanced
- **Sales Documentation Consistency** (2025-01-28) - Documentation cleanup and standardization
  - **Kanonik Segment-Priority Matrisi**: Added single source of truth table in `SEGMENT-GUIDE.md`
    - Provider + Score Band → Segment + Priority mapping table
    - Segment Evaluation Order clearly documented
    - All other docs now reference this canonical matrix
  - **Cross-References**: Added links from all sales docs to canonical matrix
    - `REALITY-CHECK-2025-01-28.md` → SEGMENT-GUIDE.md
    - `PHASE-2-1-SOFT-TUNING.md` → SEGMENT-GUIDE.md
    - `SALES-GUIDE.md` → SEGMENT-GUIDE.md
  - **Version Clarity**: Added v1.0 (MVP - Today) vs v2.0 (Target) distinction
    - `SALES-PERSONA-v2.0.md` - Clear "Hedef Durum" vs "Bugünkü Gerçeklik" labels
    - `SALES-TRAINING.md` - Version separation in training materials
  - **Tuning Factor Status**: Clarified that Tuning Factor is design-only (not in production UI)
    - Added "Durum: Tasarım - Henüz production kodda yok" warning
    - Backend env var exists but no UI/admin interface
  - **Impact**: Eliminated documentation inconsistencies, single source of truth established
  - **Files Modified**: `docs/sales/SEGMENT-GUIDE.md`, `docs/sales/PHASE-2-1-SOFT-TUNING.md`, `docs/sales/REALITY-CHECK-2025-01-28.md`, `docs/sales/SALES-PERSONA-v2.0.md`, `docs/sales/SALES-TRAINING.md`, `docs/sales/SALES-GUIDE.md`
- **IP Enrichment Minimal UI** (2025-01-28) - Added IP enrichment data to score breakdown and sales summary
  - **Backend**: Added `ip_enrichment` field to `ScoreBreakdownResponse` model
  - **Backend**: Integrated IP enrichment into `get_score_breakdown` endpoint
  - **Backend**: Added `ip_context` parameter to `generate_sales_summary` function
  - **Backend**: Integrated IP enrichment into `get_sales_summary` endpoint
  - **Sales Engine**: IP context (country, proxy) integrated into `generate_one_liner` and `generate_call_script`
  - **UI**: Added "Network & Location" section to score breakdown modal (country + proxy warning)
  - **Impact**: Improves score accuracy, enhances sales intelligence, strengthens Hunter's "what CRM can't do" positioning
  - **Status**: ✅ Completed
  - **Files Modified**: `app/api/leads.py`, `app/core/sales_engine.py`, `app/api/sales_summary.py`, `mini-ui/js/ui-leads.js`
- **IP Enrichment Validation** (2025-01-28) - Validation test script and status documentation
  - **Test Script**: Created `scripts/test_ip_enrichment_validation.py` for comprehensive IP enrichment validation
    - Tests 11 real-world domains (5 Türkiye hosting/Local, 4 M365 Kurumsal, 2 Global big tech)
    - Validates IP resolution, enrichment, database records, error handling
    - Saves results to JSON file for analysis
  - **Status Documentation**: Created `docs/active/IP-ENRICHMENT-STATUS.md` for validation tracking
    - Test results summary (IP resolution: 11/11 success, Enrichment: pending)
    - Domain test results by category (Türkiye hosting, M365, Global big tech)
    - Error handling and logging validation
    - MVP decision tracking (pending full test with enrichment enabled)
  - **Validation Checklist**: Updated `docs/active/IP-ENRICHMENT-VALIDATION-CHECKLIST.md`
    - Test execution checklist
    - Next steps for full validation (requires enrichment enabled + DB files)
  - **Test Results**: `docs/active/IP-ENRICHMENT-VALIDATION-RESULTS.json` - JSON results from validation test
  - **Status**: ✅ Full validation completed (IP resolution ✅ 11/11, Enrichment ✅ 11/11)
  - **MVP Decision**: ✅ ACCEPTED FOR MVP (country + city data quality acceptable)
  - **Test Environment**: Docker (enrichment enabled, DB files available)
  - **Files Created**: `scripts/test_ip_enrichment_validation.py`, `docs/active/IP-ENRICHMENT-STATUS.md`, `docs/active/IP-ENRICHMENT-VALIDATION-RESULTS.json`
  - **Files Modified**: `docs/active/IP-ENRICHMENT-VALIDATION-CHECKLIST.md`
- **Mini UI v1.1 Polish** (2025-01-28) - Sales-friendly UI improvements and UX enhancements
  - **Search Input**: Optimized debounce from 500ms to 400ms for better UX
  - **Empty State**: Improved message and added two action buttons (CSV Upload, Domain Scan)
  - **Error Messages**: Sales-friendly error messages (converts technical errors to user-friendly Turkish messages)
    - Network errors: "Sunucuya ulaşamadık. Birkaç dakika sonra tekrar dene."
    - Server errors: "Bir şeyler ters gitti. Lütfen daha sonra tekrar dene."
    - Technical details logged to console, not shown to user
  - **Loading Indicators**: Button disable + "Yükleniyor..." text for all form buttons (CSV Upload, Domain Scan)
  - **Score Breakdown Modal**: Added header with "Neden bu skor?" title and explanation
    - Explains that score is calculated based on M365 usage, Google Workspace, DNS and IP data
  - **Segment Tooltips**: Added sales-friendly tooltips for segment badges
    - Existing: "M365 kullanıyor → yenileme / ek lisans fırsatı"
    - Migration: "Google Workspace kullanıyor → migration fırsatı"
    - Cold: "Email provider tespit edilemedi → yeni müşteri potansiyeli"
    - Skip: "Düşük skor / risk → düşük öncelik"
  - **Location Information**: Made location info more prominent in score breakdown modal
    - Shows country + city with "(IP bazlı tahmin)" note
    - Changed label from "Country" to "Konum" (Turkish)
  - **Status**: ✅ 7/10 tasks completed (search debounce, empty state, error messages, loading indicators, score breakdown header, segment tooltips, location info)
  - **Remaining**: Dogfooding test, duplicate request detection, modal cache (pending manual testing)
  - **Files Modified**: `mini-ui/js/app.js`, `mini-ui/js/ui-leads.js`, `mini-ui/js/ui-forms.js`, `mini-ui/index.html`
  - **Documentation**: `docs/active/MINI-UI-POLISH-NOTES.md` - Dogfooding notes and polish tracking

### Changed
- **Regression Dataset Rename** (2025-01-28) - Renamed "golden dataset" to "silver regression dataset" for clarity
  - **Renamed**: `test_golden_dataset.py` → `test_regression_dataset.py`
  - **Renamed**: `GOLDEN_DATASET` → `REGRESSION_DATASET`
  - **Updated**: Docstrings clarify this is a synthetic regression set, not ground truth
  - **Expanded**: Regression dataset from 14-15 to 26 test cases for better coverage
  - **New Cases**: M365+DMARC none, Google+DKIM broken, Hosting+External SPF, Multi-MX, Zoho, Amazon SES, SendGrid, etc.
  - **Reason**: Current dataset is valuable for regression prevention but not a true golden dataset (ground truth)
  - **Impact**: Clearer distinction between regression prevention (silver) and real-world validation (golden)
  - **Documentation**: Added `docs/plans/2025-01-28-GOLDEN-DATASET-CRITIQUE.md` and `docs/plans/2025-01-28-GOLDEN-DATASET-v1.0-BLUEPRINT.md`
  - **Status**: ✅ Completed

### Fixed
- **Scoring Engine Test Fixes** (2025-01-28) - Critical test failures fixed, scoring engine fully validated
  - **Fixed Tests**: 
    - `test_risk_scoring_no_dkim` - Accounted for `dkim_none` risk penalty (-5)
    - `test_risk_scoring_hosting_with_spf` - Accounted for `dkim_none` risk penalty (-5)
    - Golden dataset test cases (test_case3, test_case4, test_case6, test_case9, test_case11) - Updated expected scores and priority scores
    - `test_golden_dataset_priority_ordering` - Fixed priority score ranges (Skip → 7, Existing → 3-6, Migration → 1-4)
  - **Root Cause**: G18 Enhanced Scoring added `dkim_none` risk penalty (-5) but tests were not updated
  - **Impact**: Scoring engine now fully validated (86 tests passing, 0 failures)
  - **Status**: ✅ Completed
  - **Files Modified**: `tests/test_scorer_rules.py`, `tests/test_golden_dataset.py`
  - **Documentation**: `docs/active/TEST-FIXES-COMPLETED.md` - Complete test fix report

### Removed
- **Microsoft SSO Authentication (G19)** (2025-01-28) - Removed unused SSO implementation, switched to Internal Access Mode
  - **Removed Files**: `app/core/auth.py`, `app/api/auth.py`, `app/core/favorites_migration.py`, `tests/test_auth.py`
  - **Removed Dependencies**: `msal`, `python-jose`, `cryptography` (SSO-specific)
  - **Removed Models**: `User` model (SSO-specific)
  - **Removed Config**: Azure AD and JWT configuration from `app/config.py` and `.env.example`
  - **Updated Code**: `app/api/sales_summary.py` - Removed SSO fallback, using session-based user ID only
  - **Updated Tests**: `tests/test_integration_g19.py` - Removed SSO tests, kept UI upgrade tests
  - **Reason**: SSO was not used in any core flows (ingest, scan, leads, dashboard). Internal tool (3-10 users) doesn't require SSO complexity. Network-level authentication is sufficient.
  - **Impact**: Reduced code complexity (~400+ lines), removed maintenance burden, simplified authentication model
  - **Status**: ✅ Completed

### Enhanced
- **Mini UI - Production Improvements** (2025-01-28) - Code quality and error handling enhancements
  - **Production-Safe Logging**: Added logger utility (`mini-ui/js/logger.js`) with debug mode control
    - Console logs disabled in production (set `window.DEBUG = true` for development)
    - Improved performance by removing unnecessary console output
    - Error tracking ready for integration with external services
  - **Improved Error Handling**: Enhanced API error messages with user-friendly Turkish translations
    - HTTP status code-based error messages (400, 401, 403, 404, 409, 422, 429, 500, 503)
    - Better error extraction from API responses
    - Consistent error handling across all API functions
  - **Code Quality**: Replaced all `console.log/error/warn` calls with logger utility (16 instances)
    - Files updated: `app.js`, `ui-leads.js`, `ui-forms.js`, `api.js`
  - **Documentation**: Updated `README-mini-ui.md` and `TEST-CHECKLIST.md` with improvements
  - **Status**: ✅ Completed
- **Integration Roadmap - Phase 1: Mini UI Stabilization** (2025-01-28) - UI polish and stability improvements
  - **Button & Modal Fixes**: Improved button hover states with scale transform and color changes, optimized modal scroll with custom scrollbar styling
  - **Score Breakdown Improvements**: Fixed data flow (stale data prevention), improved tooltip positioning (centered CSS-only solution), fixed signal/risk display order (SPF → DKIM → DMARC → Risks), added modal-specific loading spinner
  - **Loading States**: Added table loading spinner with overlay, filter controls disabled during fetch, export buttons with loading state and spinner animation, smooth transitions (0.15s ease-out)
  - **Filter Bar UX**: Improved layout with row-based structure, enhanced dropdown/input styling with focus states, added "Clear all filters" button, implemented filter state persistence with localStorage
  - **General UX Polish**: Enhanced table row hover effects (subtle shadow, smooth transitions), improved pagination UX (active state styling, disabled state, smooth transitions), enhanced empty state messages (icon, better visual hierarchy), improved toast notifications (icons, better animations, stacking support, click-to-dismiss, hover pause)
  - **Files Modified**: `mini-ui/js/ui-leads.js`, `mini-ui/js/app.js`, `mini-ui/styles.css`, `mini-ui/index.html`
  - **Status**: ✅ Completed
- **IP Enrichment Configuration** (2025-01-28) - Improved environment variable format and Country DB support
  - **New Env Format**: Simplified environment variable names (`MAXMIND_CITY_DB`, `MAXMIND_COUNTRY_DB`, `IP2LOCATION_DB`, `IP2PROXY_DB`)
  - **Country DB Support**: Added optional `GeoLite2-Country.mmdb` as fallback for country-only lookups
  - **Backward Compatible**: Legacy format (`HUNTER_ENRICHMENT_DB_PATH_*`) still supported
  - **Documentation**: Updated `.env.example` and all IP enrichment documentation with new format
- **IP Enrichment** (2025-01-28) - Production readiness improvements
  - **Health Check**: Added `enrichment_enabled` flag to `/healthz` endpoint (read-only, no DB connection)
  - **Error Tracking**: Added Sentry tag `hunter_enrichment_error` for enrichment error monitoring
  - **Backlog**: Added `source` field enhancement to future tasks (for debugging IP origin: "mx-ip" vs "root-ip")
- **IP Enrichment - Level 1 Exposure** (2025-01-28) - Sales team infrastructure insights
  - **API Response**: Added `infrastructure_summary` field to `/leads` and `/lead/{domain}` endpoints
  - **Format**: Human-readable summary (e.g., "Hosted on DataCenter, ISP: Hetzner, Country: DE")
  - **Helper Functions**: 
    - `latest_ip_enrichment()` - Get most recent enrichment record for a domain
    - `build_infra_summary()` - Build human-readable summary from enrichment data
  - **Usage Type Mapping**: DCH → DataCenter, COM → Commercial, RES → Residential, MOB → Mobile
  - **Backward Compatible**: Field is optional (None if no enrichment data available)

### Added
- **IP Enrichment** (2025-01-28) - IP geolocation, ASN, ISP, and proxy detection
  - **Feature Flag**: `HUNTER_ENRICHMENT_ENABLED` (default: `false`) - No-break upgrade design
  - **Data Sources**: MaxMind GeoLite2 (ASN/City), IP2Location LITE, IP2Proxy LITE
  - **IP Resolution**: Automatic IP resolution from MX records and root domain A records
  - **Database**: New `ip_enrichment` table with UPSERT support (unique constraint on domain+ip)
  - **Caching**: 24-hour TTL for IP enrichment results (Redis-based)
  - **Thread Safety**: Thread-safe lazy loading of enrichment databases
  - **Fire-and-Forget**: Enrichment runs in separate DB session, doesn't affect scan transaction
  - **Graceful Degradation**: Missing DB files don't crash the app, enrichment is skipped
  - **Startup Validation**: Config validation at startup with warning logs for missing DB files
  - **Debug Endpoints**: 
    - `GET /debug/ip-enrichment/{ip}` - Debug IP enrichment (cache, providers, DB record)
    - `GET /debug/ip-enrichment/config` - Check enrichment configuration status
  - **Implementation Files**:
    - `app/core/analyzer_enrichment.py` - Core enrichment logic (MaxMind, IP2Location, IP2Proxy)
    - `app/core/enrichment_service.py` - Service layer with DB session management
    - `app/core/analyzer_dns.py` - IP resolution functions (`resolve_hostname_to_ip`, `resolve_domain_ip_candidates`)
    - `app/db/models.py` - `IpEnrichment` SQLAlchemy model
    - `app/api/debug.py` - Debug endpoints for troubleshooting
    - `alembic/versions/e7196f7e556b_add_ip_enrichment_table.py` - Database migration
  - **Documentation**: `docs/active/IP-ENRICHMENT-IMPLEMENTATION.md` - Complete implementation guide
- **Test Suite Improvements** (2025-01-27)
  - Shared test fixtures (`tests/conftest.py`) with transaction-based isolation
  - Standardized test isolation across all test files
  - Conditional test execution for integration tests (Redis/Celery availability checks)
  - Test analysis and application status reports
  - **Test Infrastructure**:
    - `db_session` fixture: Transaction-based isolated database session with automatic rollback
    - `client` fixture: TestClient with database dependency override
    - `redis_available`, `celery_available`, `redis_and_celery_available` fixtures for conditional execution
    - Pytest markers: `@pytest.mark.requires_redis`, `@pytest.mark.requires_celery`, `@pytest.mark.requires_integration`
  - **Test Fixes**:
    - Fixed test isolation in `test_notes_tags_favorites.py` and `test_rescan_alerts.py`
    - Activated skipped tests with conditional execution
    - Fixed Company model parameter usage (`company_name` → `canonical_name`)
    - Fixed note ordering test assertions
  - **Documentation**:
    - `docs/active/TEST-ANALYSIS.md` - Comprehensive test suite analysis
    - `docs/active/APPLICATION-STATUS.md` - Application health status report

## [1.1.0] - 2025-01-28

### Highlights
- **G21 Phase 2: Sales Engine** - Sales intelligence layer with call scripts, discovery questions, and offer tier recommendations
- **G21 Phase 3: Read-Only Mode** - CRM-lite features write endpoints disabled for Dynamics 365 migration
- **Stabilization Sprint** - 3-day enterprise-ready stabilization (UI, monitoring, core stability)
- **Core Logging Standardization** - Structured logging with PII masking across all modules

### Added
- **G21 Phase 3: Read-Only Mode** (2025-01-28) - Disabled write endpoints for CRM-lite features (Notes/Tags/Favorites)
  - **Deprecated Endpoint Monitoring** (`app/core/deprecated_monitoring.py`):
    - Track deprecated endpoint calls (total calls, calls by endpoint, calls by domain)
    - Daily and weekly call count tracking
    - Top endpoints and domains metrics
    - Metrics available via `GET /healthz/metrics` endpoint
  - **Write Endpoints Disabled** (410 Gone):
    - `POST /leads/{domain}/notes` - Returns 410 Gone (Notes now managed in Dynamics 365)
    - `PUT /leads/{domain}/notes/{note_id}` - Returns 410 Gone
    - `DELETE /leads/{domain}/notes/{note_id}` - Returns 410 Gone
    - `POST /leads/{domain}/tags` - Returns 410 Gone (Manual tags now managed in Dynamics 365)
    - `DELETE /leads/{domain}/tags/{tag_id}` - Returns 410 Gone
    - `POST /leads/{domain}/favorite` - Returns 410 Gone (Favorites now managed in Dynamics 365)
    - `DELETE /leads/{domain}/favorite` - Returns 410 Gone
  - **Read Endpoints Still Available** (200 OK):
    - `GET /leads/{domain}/notes` - Remains available (read-only, migration support)
    - `GET /leads/{domain}/tags` - Remains available (auto-tags needed)
    - `GET /leads?favorite=true` - Remains available (read-only, migration support)
  - **Metrics Integration**:
    - Deprecated endpoint metrics added to `GET /healthz/metrics` endpoint
    - Metrics include: total_calls, calls_by_endpoint, calls_by_domain, daily_call_count, weekly_call_count, top_endpoints, top_domains
  - **Test Coverage**:
    - Updated tests for Phase 3 behavior (write endpoints return 410, read endpoints return 200)
    - Metrics tracking tests added
    - Test file: `tests/test_notes_tags_favorites.py`
  - **Status**: ✅ Phase 3 completed - Read-only mode active, monitoring in place, all tests passing
  - **Benefits**: Zero downtime migration support, clear migration path to Dynamics 365, usage tracking for migration planning
- **G21 Phase 2: Sales Engine** (2025-01-28) - Sales intelligence layer for lead qualification
  - **Sales Engine Core** (`app/core/sales_engine.py`):
    - `generate_one_liner()` - One-sentence sales summary (Turkish)
    - `generate_call_script()` - Call script bullets for sales outreach (Turkish)
    - `generate_discovery_questions()` - Discovery questions for sales qualification (Turkish)
    - `recommend_offer_tier()` - Offer tier recommendation (Business Basic/Standard/Enterprise)
    - `calculate_opportunity_potential()` - Opportunity potential score (0-100) with tuning factor support
    - `calculate_urgency()` - Urgency level calculation (low/medium/high)
    - `generate_sales_summary()` - Complete sales intelligence summary generator
  - **Sales Summary API Endpoints**:
    - `GET /api/v1/leads/{domain}/sales-summary` - V1 endpoint for sales intelligence summary
    - `GET /leads/{domain}/sales-summary` - Legacy endpoint (backward compatible)
    - Response includes: domain, one_liner, call_script, discovery_questions, offer_tier, opportunity_potential, urgency, metadata
  - **API Contract Documentation** (`docs/api/SALES-SUMMARY-V1-CONTRACT.md`):
    - Frozen API contract (UI-ready, breaking change policy defined)
    - TypeScript and JSDoc type definitions (`mini-ui/types/sales.ts`, `mini-ui/types/sales.js`)
    - Field names and types frozen for UI compatibility
  - **Logging & Telemetry**:
    - `sales_summary_viewed` event logging with user tracking (auth + session fallback)
    - Structured logging: domain, segment, offer_tier, opportunity_potential, urgency, tenant_size, provider
  - **Tuning Mechanism** (Phase 2.1):
    - `HUNTER_SALES_ENGINE_OPPORTUNITY_FACTOR` config (default: 1.0, range: 0.0-2.0)
    - Fine-tuning capability for opportunity potential scores based on sales feedback
    - Documentation: `docs/active/PHASE-2-1-SOFT-TUNING.md`
  - **Test Coverage**:
    - Core unit tests: `tests/test_sales_engine_core.py` (38 tests, all passing)
    - API integration tests: `tests/test_sales_summary_api.py` (7 tests, all passing)
    - Real-world smoke test: 3 domains validated (Migration, Existing, Cold segments)
  - **Status**: ✅ Phase 2 completed - Production-ready, UI contract frozen, all tests passing
  - **Benefits**: Sales-ready intelligence, segment-specific call scripts, discovery questions, offer tier recommendations

### Deprecated
- **G21 Phase 1: Deprecation Annotations** (2025-11-16) - CRM-lite features (Notes/Tags/Favorites) write endpoints deprecated
  - **Notes endpoints** (write operations disabled):
    - `POST /leads/{domain}/notes` - ❌ Disabled (410 Gone) - Notes now managed in Dynamics 365
    - `PUT /leads/{domain}/notes/{note_id}` - ❌ Disabled (410 Gone)
    - `DELETE /leads/{domain}/notes/{note_id}` - ❌ Disabled (410 Gone)
    - `GET /leads/{domain}/notes` - ✅ Remains available (read-only, migration support)
  - **Tags endpoints** (manual tag write operations disabled):
    - `POST /leads/{domain}/tags` - ❌ Disabled (410 Gone) - Manual tags now managed in Dynamics 365
    - `DELETE /leads/{domain}/tags/{tag_id}` - ❌ Disabled (410 Gone)
    - `GET /leads/{domain}/tags` - ✅ Remains available (auto-tags needed)
  - **Favorites endpoints** (write operations disabled):
    - `POST /leads/{domain}/favorite` - ❌ Disabled (410 Gone) - Favorites now managed in Dynamics 365
    - `DELETE /leads/{domain}/favorite` - ❌ Disabled (410 Gone)
    - `GET /leads?favorite=true` - ✅ Remains available (read-only, migration support)
  - **Deprecated Endpoint Monitoring**:
    - All disabled endpoint calls are tracked via `app/core/deprecated_monitoring.py`
    - Metrics available via `GET /healthz/metrics` endpoint (deprecated_endpoints section)
    - Usage tracking for migration planning (total calls, calls by endpoint, calls by domain)
  - **Alternative**: Use Dynamics 365 Timeline/Notes API, Tags API, and Favorite field for CRM-lite features
  - **Migration**: Read endpoints remain available for migration support until Phase 6
  - **Status**: Phase 3 completed - Read-only mode active, monitoring in place, zero downtime

### Fixed
- **Core Logging Standardization** (2025-01-28) - Fixed logging inconsistencies across core modules
  - **Standardized logging imports**: All core modules now use `from app.core.logging import logger` instead of `logging.getLogger(__name__)`
  - **Structured logging format**: Converted all f-string logger calls to structured logging format
  - **PII masking**: Cache keys and sensitive data are now masked in logs (domain → hash, email → hash)
  - **Log level optimization**: Cache failures moved to debug level (frequent, non-critical), Redis initialization failures use error level (critical)
  - **Files updated**:
    - `app/core/cache.py` - Cache operations now use structured logging with PII masking (`cache_get_failed`, `cache_set_failed`, `cache_delete_failed`)
    - `app/core/distributed_rate_limiter.py` - Rate limiting operations now use structured logging (`circuit_breaker_opened`, `rate_limiter_fallback`, `redis_rate_limit_operation_failed`)
    - `app/core/redis_client.py` - Redis client operations now use structured logging (`redis_client_initialized`, `redis_client_initialization_failed`)
  - **Test coverage**:
    - `scripts/test_logging_output.py` - Unit tests for PII masking, log format, and structured logging
    - `scripts/smoke_test_logging.sh` - Integration tests for API-level logging verification
  - **Documentation**:
    - `docs/active/LOGGING-GOLDEN-SAMPLES.md` - Golden samples for structured logging format
    - `docs/active/LOGGING-SMOKE-TEST.md` - Smoke test guide and verification checklist
  - **Benefits**: Consistent JSON log format in production, better log aggregation, contextual logging with structured fields, PII protection
  - **Status**: ✅ All core modules now use structured logging consistently with PII masking

### Added
- **Stabilization Sprint - Gün 3: UI Stabilizasyon** (2025-01-28) - Satış ekibi için 2 dakikada kullanılabilir UI
  - Table view cleanup - Column width optimization (domain, provider, score, segment, priority, tenant-size, local-provider), row hover effect with smooth transition, empty state message with CTA button, loading state spinner with animation, pagination UI improvements (page numbers, prev/next, page info) (`mini-ui/js/ui-leads.js`, `mini-ui/styles.css`, `mini-ui/index.html`)
  - Score breakdown modal improvements - Close button more prominent (absolute positioning, hover effect), backdrop click to close (fixed to only close on overlay click), ESC key to close modal, modal scroll optimization (max-height: 80vh, overflow-y: auto), score breakdown tooltips for signals and risks (SPF, DKIM, DMARC, risk factors) (`mini-ui/js/ui-leads.js`, `mini-ui/styles.css`, `mini-ui/js/app.js`)
  - Header/Footer simplification - Header title more compact ("Dyn365Hunter Mini UI" → "Dyn365Hunter"), footer addition with version info (v1.1-stable) and links (Docs, Support), responsive footer for mobile layout (`mini-ui/index.html`, `mini-ui/styles.css`)
  - Export/PDF basic - CSV/Excel export buttons separated, export format selection, toast notification system for success/error messages, PDF export button in score breakdown modal (`mini-ui/js/ui-leads.js`, `mini-ui/js/app.js`, `mini-ui/js/api.js`, `mini-ui/styles.css`)
  - Tooltip + hover behavior - Generic tooltip system (CSS-based), tooltip positioning, score breakdown tooltips for signals and risks, table row hover (highlight with smooth transition), button hover (scale transform + color change), badge hover (opacity transition) (`mini-ui/styles.css`, `mini-ui/js/ui-leads.js`)
  - Favori/Tag UI improvements - Backend already supports favorites/tags, UI improvements completed through general style updates (hover effects, badge styling) (`mini-ui/js/ui-leads.js`, `mini-ui/styles.css`)
  - Status: ✅ Gün 3 tamamlandı - UI %90+ stabil, entegrasyona hazır
- **Stabilization Sprint - Gün 2: Monitoring ve Safety** (2025-01-28) - Observability ve güvenlik katmanları
  - Cache hit metrics - Redis cache hit/miss counter, hit rate calculation, TTL expiration tracking (`app/core/cache.py`)
  - Rate limit metrics - Rate limit hit counter, per-key metrics, circuit breaker state tracking (`app/core/distributed_rate_limiter.py`)
  - Bulk operations metrics - Batch success/failure rate, average processing time, deadlock count, partial commit recovery count (`app/core/tasks.py`)
  - Error trend logging - Sentry error categorization (component, severity, error_type), error grouping, daily/weekly error count tracking (`app/core/error_tracking.py`)
  - Metrics endpoint - `GET /healthz/metrics` - Unified metrics endpoint for cache, rate limit, bulk operations, and error metrics (`app/api/health.py`)
  - Deadlock simulation testleri (`tests/test_deadlock_prevention.py`) - Concurrent transaction test, deadlock detection, retry logic test, transaction timeout test, batch isolation test (5/5 passed)
  - Cache invalidation simulation testleri (`tests/test_cache_invalidation.py`) - Rescan cache invalidation, TTL expiration, cache key collision, cache consistency test (7/7 skipped - Redis yok, beklenen)
  - Redis skip mekanizması - Cache invalidation testleri Redis yoksa otomatik skip edilir (CI/local ortam uyumluluğu)
  - Test coverage: 12 yeni test eklendi (5 passed, 7 skipped - beklenen)
  - Status: ✅ Gün 2 tamamlandı ve kilitlendi
- **Stabilization Sprint - Gün 1: Core Stabilizasyon** (2025-01-28) - Test ve doğrulama katmanları
  - Alembic migration testleri (`tests/test_alembic.py`) - Schema drift detection, rollback testleri, run_migration.py wrapper testleri (10 passed, 1 skipped)
  - Distributed rate limiting testleri (`tests/test_distributed_rate_limiter.py`) - Multi-worker rate limiting, Redis fallback, circuit breaker recovery (11 passed)
  - Bulk operations test düzeltmeleri - Test isolation sorunları çözüldü, unique domain fixture'ları eklendi (11 passed, 2 skipped)
  - API backward compatibility testleri - Response format consistency, zero downtime deployment testleri eklendi (15/15 passed)
  - Redis health check - `/healthz/ready` endpoint'ine Redis ping eklendi, connection pool kullanımı
  - Router prefix düzeltmesi - `app/main.py`'de double prefix sorunu çözüldü (v1 ve legacy router'lar)
  - Test coverage: 47+ yeni test eklendi, tüm testler yeşil
  - Status: ✅ Gün 1 tamamlandı ve kilitlendi
- **P1-5: API Versioning** - API versioning structure with backward compatibility
  - API v1 router structure (`/api/v1/...`) - All API endpoints now available under `/api/v1/` prefix
  - Backward compatibility - Legacy endpoints (`/...`) continue to work for zero downtime migration
  - Dual-path routing - Both v1 and legacy endpoints active simultaneously
  - 13 versioned routers: ingest, scan, leads, dashboard, email_tools, progress, admin, notes, tags, favorites, pdf, rescan, alerts
  - Health and auth endpoints excluded from versioning (infrastructure endpoints)
  - Implementation files:
    - `app/api/v1/` - V1 router directory with proxy pattern handlers
    - `app/api/v1/__init__.py` - V1 router exports
    - `app/api/v1/*.py` - Individual v1 router files (13 routers)
    - `app/main.py` - Updated to register v1 routers and maintain legacy routers
  - Test coverage:
    - `tests/test_api_versioning.py` - API versioning tests (10 tests)
    - Backward compatibility tests
    - Dual-path routing tests
  - Status: ✅ Core implementation completed
  - Benefits: Future-proof API structure, zero downtime migration, backward compatibility
- **P1-4: Bulk Operations Optimization** - Batch processing optimization for bulk scan operations
  - Batch size calculation (rate-limit aware) - Optimal batch size based on DNS/WHOIS rate limits (default: 50 domains/batch)
  - Batch commit optimization - Reduces transaction overhead by batching commits instead of per-domain commits
  - Deadlock prevention - Transaction timeout (30s) and retry logic (3 attempts with exponential backoff) using tenacity
  - Partial commit log - Redis-based recovery mechanism for batch failures
  - Batch isolation - One batch failure doesn't affect other batches
  - Bulk log context - Structured logging with batch information (bulk_id, batch_no, total_batches, batch_size)
  - scan_single_domain commit=False support - Allows batch-level commit control for batch processing
  - Implementation files:
    - `app/core/bulk_operations.py` - Batch utilities (batch size calculation, partial commit log, bulk log context)
    - `app/core/tasks.py` - Updated bulk_scan_task with batch processing, process_batch_with_retry function
    - `requirements.txt` - Added tenacity>=8.2.3 for retry logic
  - Test coverage:
    - `tests/test_bulk_operations_p1.py` - Comprehensive P1-4 tests (13 tests)
    - Batch size calculation tests (5 tests)
    - Partial commit log tests (2 tests)
    - Bulk log context tests (1 test)
    - Integration tests (2 skipped - require Redis)
  - Status: ✅ Core implementation completed
  - Benefits: Significant performance improvement for bulk operations, reduced transaction overhead, better deadlock handling
- **P1-3: Caching Layer** - Redis-based distributed caching for DNS, WHOIS, Provider, Scoring, and Scan results
  - Redis-based cache utilities (`app/core/cache.py`) with generic get/set/delete functions
  - DNS cache (1 hour TTL) - Reduces DNS queries and rate limit pressure
  - WHOIS cache migrated to Redis (24 hour TTL) - Replaced in-memory cache for multi-worker support
  - Provider mapping cache (24 hour TTL) - Caches MX root to provider mappings (most repeated pattern)
  - Scoring cache (1 hour TTL) - Caches scoring results with signals hash for stable cache keys
  - Domain-level full scan cache (1 hour TTL) - Caches complete scan results
  - Cache invalidation on rescan - Ensures fresh results when domains are re-scanned
  - Graceful fallback when Redis unavailable - All cache operations degrade gracefully
  - Implementation files:
    - `app/core/cache.py` - Redis-based cache utilities
    - `app/core/analyzer_dns.py` - Updated with DNS cache
    - `app/core/analyzer_whois.py` - Migrated to Redis cache (removed in-memory cache)
    - `app/core/provider_map.py` - Added provider mapping cache
    - `app/core/scorer.py` - Added scoring cache with signals hash
    - `app/core/tasks.py` - Added full scan cache
    - `app/core/rescan.py` - Added cache invalidation on rescan
    - `app/api/scan.py` - Updated to use cache
  - Test coverage:
    - `tests/test_cache.py` - Comprehensive cache tests (14 tests)
    - Cache hit/miss tests for all cache types
    - Redis unavailable fallback tests
    - Signals hash stability tests
  - Status: ✅ Core implementation completed
  - Benefits: Significant performance improvement, reduced DNS/WHOIS queries, better multi-worker support
- **P1-2: Distributed Rate Limiting** - Redis-based distributed rate limiting for multi-worker deployments
  - Redis client wrapper with connection pooling (`app/core/redis_client.py`)
  - DistributedRateLimiter class with Redis-based token bucket algorithm
  - Circuit breaker pattern for Redis availability (5 failure threshold, 60s recovery timeout)
  - Fallback to in-memory rate limiter when Redis is unavailable
  - Degrade mode logging (WARN level + Sentry tags) for monitoring
  - DNS rate limiter migrated to Redis (10 req/s, shared across all workers)
  - WHOIS rate limiter migrated to Redis (5 req/s, shared across all workers)
  - API key rate limiter migrated to Redis (per-key limits, shared across all workers)
  - Health check endpoint already includes Redis health check (`/healthz/ready`)
  - Implementation files:
    - `app/core/redis_client.py` - Redis client wrapper with connection pooling
    - `app/core/distributed_rate_limiter.py` - Distributed rate limiter with circuit breaker
    - `app/core/rate_limiter.py` - Updated to use DistributedRateLimiter
    - `app/core/api_key_auth.py` - Updated to use DistributedRateLimiter
  - Status: ✅ Core implementation completed
  - Benefits: Multi-worker deployments now share rate limits correctly, preventing rate limit bypass
- **P1: Alembic Migration System** - Database migration management system
  - Alembic setup and configuration (`alembic/`, `alembic.ini`, `alembic/env.py`)
  - Base revision created (`08f51db8dce0_base_revision.py`) representing current production schema
  - "Collapsed history" strategy: Base revision represents all historical migrations (g16-g20)
  - Legacy SQL migration files moved to `app/db/migrations/legacy/` for reference
  - Schema drift detection via `alembic check` command
  - `run_migration.py` script updated to use Alembic (wrapper for Alembic commands)
  - Docker integration: Alembic files included in Dockerfile and docker-compose.yml
  - Migration commands:
    - `python -m app.db.run_migration upgrade` - Upgrade to latest migration
    - `python -m app.db.run_migration downgrade` - Downgrade one step
    - `python -m app.db.run_migration current` - Show current revision
    - `python -m app.db.run_migration check` - Check for schema drift
  - Documentation:
    - `docs/active/P1-ALEMBIC-PREPARATION.md` - Preparation analysis
    - `docs/active/P1-ALEMBIC-STATUS.md` - Implementation status
    - `app/db/migrations/legacy/README.md` - Legacy migration reference
  - Implementation files:
    - `alembic/versions/08f51db8dce0_base_revision.py` - Base revision
    - `alembic/env.py` - Alembic environment configuration
    - `alembic.ini` - Alembic configuration file
    - `app/db/run_migration.py` - Migration runner script (updated)
    - `requirements.txt` - Alembic dependency added
    - `Dockerfile` - Alembic files included
    - `docker-compose.yml` - Alembic directory volume mount
  - Status: ✅ Core implementation completed
  - Strategy: All future schema changes will be managed through Alembic revisions
- **Sales Persona v2.0: "Sistematik Avcı"** - Comprehensive sales persona documentation and training materials
  - **Persona v2.0 Documentation** (`docs/active/SALES-PERSONA-v2.0.md`):
    - Hunter-native satışçı profili (G17, G18, G20 özelliklerini kullanan)
    - CRM-integrated workflow (Hunter → Dynamics CRM pipeline mapping)
    - Multi-threaded outreach stratejisi (IT Direktörü, CFO, Genel Müdür, CTO)
    - Rejection handling senaryoları (3 senaryo: "İlgilenmiyoruz", "Başka çözüm", "Bütçe yok")
    - Competition awareness (Google Workspace → M365, Local Provider → M365)
    - Pricing strategy (Tenant size'a göre pricing, value-based pricing)
    - Günlük çalışma akışı (4 zaman dilimi: Sabah, Öğle Öncesi, Öğleden Sonra, Gün Sonu)
  - **Persona Critique** (`docs/active/SALES-PERSONA-CRITIQUE.md`):
    - v1.0 persona'nın eleştirel analizi
    - Eksik özellikler ve geliştirme önerileri
    - Hunter özelliklerini tam kullanma stratejisi
    - CRM entegrasyonu detayları
  - **Training Material** (`docs/active/SALES-TRAINING.md`):
    - 7 modüllük eğitim programı (Hunter Temelleri, Hunter-native Özellikler, CRM Entegrasyonu, Multi-Threaded Outreach, Rejection Handling, Pricing Strategy, Competition Awareness)
    - Her modül için pratik egzersizler
    - Değerlendirme testleri
    - Eğitim tamamlama checklist'i
  - **Sales Guide Integration** (`docs/SALES-GUIDE.md`):
    - Persona v2.0 bölümü eklendi (özet)
    - Günlük çalışma akışı
    - Hunter-native özellikler
    - CRM pipeline mapping tablosu
    - Rejection handling stratejisi
    - Pricing strategy
  - **Sales Scenarios v2.0** (`docs/SALES-SCENARIOS.md`):
    - Senaryo 10.1: Alert Tabanlı Proaktif Satış
    - Senaryo 10.2: Multi-Threaded Outreach
    - Senaryo 10.3: Rejection Handling - "Şu An İlgilenmiyoruz"
    - Senaryo 10.4: Rejection Handling - "Zaten Başka Bir Çözüm Kullanıyoruz"
    - Senaryo 10.5: Pricing Strategy - Tenant Size'a Göre Teklif
    - Senaryo 10.6: Competition Awareness - Google Workspace → M365 Migration
    - Senaryo 10.7: Competition Awareness - Local Provider → M365 Migration
  - Documentation structure:
    - Persona v2.0: `docs/active/SALES-PERSONA-v2.0.md` (tam dokümantasyon)
    - Persona Critique: `docs/active/SALES-PERSONA-CRITIQUE.md` (eleştirel analiz)
    - Training Material: `docs/active/SALES-TRAINING.md` (eğitim materyali)
    - Sales Guide: `docs/SALES-GUIDE.md` (özet bölüm eklendi)
    - Sales Scenarios: `docs/SALES-SCENARIOS.md` (7 yeni senaryo eklendi)
- **UI Patch v1.1** - Skor detay modal ve UX iyileştirmeleri
  - Skor detay modal iyileştirmeleri:
    - DKIM çift gösterimi düzeltildi: `no_dkim` (-10) ve `dkim_none` (-5) tek satırda birleştirildi → "DKIM Eksik: -15"
    - DMARC_NONE kategorisi düzeltildi: 0 puanlı `dmarc_none` "Pozitif Sinyaller" bölümünden çıkarıldı, sadece "Risk Faktörleri" bölümünde görünüyor
    - Sıralama tutarlılığı: Signal ve risk faktörleri sabit sırada gösteriliyor (SPF → DKIM → DMARC → Riskler)
    - Kullanıcı dostu label'lar: Teknik terimler yerine anlaşılır Türkçe label'lar (örn: "SPF Eksik", "DKIM Eksik")
  - Provider renkli badge'ler:
    - M365 → Mavi (#0078d4)
    - Google → Kırmızı (#ea4335)
    - Yandex → Turuncu (#fc3f1d)
    - Local → Koyu gri (#343a40)
    - Tüm provider'lar için renkli badge'ler eklendi
  - Sort ikonları iyileştirmeleri:
    - İkon boyutu artırıldı (0.7rem → 0.85rem)
    - Active durumda daha belirgin (0.9rem, bold)
    - Hover tooltip'ler eklendi (kolon başlıklarına)
    - Hover'da renk değişimi eklendi
  - Dosyalar:
    - `mini-ui/js/ui-leads.js` - `showScoreBreakdown()` fonksiyonu yeniden yazıldı, helper fonksiyonlar eklendi
    - `mini-ui/styles.css` - Provider badge CSS'leri ve sort icon iyileştirmeleri eklendi
    - `mini-ui/index.html` - Sort column'larına tooltip'ler eklendi
  - Plan: `.cursor/plans/UI-PATCH-PLAN-v1.1.md`
- **Priority Score Improvements** - Enhanced priority scoring system
  - Extended priority range from 1-6 to 1-7 for better granularity
  - Migration segment now always gets priority (even with low scores: Priority 3-4)
  - Improved priority distribution:
    - Migration + Score 50-69 → Priority 3 (was Priority 6)
    - Migration + Score 0-49 → Priority 4 (was Priority 6)
    - Existing + Score 30-49 → Priority 5 (was Priority 6)
    - Existing + Score 0-29 → Priority 6 (was Priority 6)
    - Cold + Score 20-39 → Priority 6 (was Priority 6)
    - Cold + Score 0-19 → Priority 7 (new)
    - Skip → Priority 7 (was Priority 6)
  - Enhanced UI visualization:
    - Each priority level now has unique visual indicator (🔥⭐🟡🟠⚪⚫🔴)
    - Tooltip support for priority badges with detailed information
  - Updated constants and thresholds in `app/core/constants.py`
  - Updated priority calculation logic in `app/core/priority.py`
  - Updated UI components in `mini-ui/js/ui-leads.js`
  - Updated API default values (Priority 6 → 7)
  - Updated test suite in `tests/test_priority.py`
  - Updated documentation (SEGMENT-GUIDE.md, SALES-GUIDE.md, SALES-SCENARIOS.md, README.md)
- **G19: Microsoft SSO Authentication + UI Upgrade** - Authentication and enhanced UI features
  - Microsoft SSO Authentication:
    - `GET /auth/login` - Initiate Azure AD OAuth 2.0 login
    - `GET /auth/callback` - OAuth callback handler
    - `GET /auth/me` - Get current user information
    - `POST /auth/refresh` - Refresh access token
    - `POST /auth/logout` - Logout and revoke tokens
    - JWT token management (access + refresh tokens)
    - User management (users table with Azure AD integration)
    - Security hardening:
      - OAuth state/nonce storage (Redis)
      - Token revocation table
      - Refresh token encryption (Fernet)
    - Favorites migration: Session-based → user-based (on first login)
    - Setup guide: `docs/archive/2025-11-15-G19-AZURE-AD-SETUP.md` (archived after completion)
  - UI Upgrade (Lead Table):
    - Sorting: Sort by domain, readiness_score, priority_score, segment, provider, scanned_at
    - Pagination: Page-based pagination with configurable page size (default: 50, max: 200)
    - Full-text search: Search in domain, canonical_name, and provider fields
    - Frontend: Clickable table headers, pagination UI, search input with debounce
  - Dashboard KPI:
    - `GET /dashboard/kpis` - New lightweight endpoint for KPI cards
    - Returns: total_leads, migration_leads, high_priority
    - Frontend: 4 KPI cards (Total, Migration, High Priority, Max Score)
  - Score Breakdown:
    - `GET /leads/{domain}/score-breakdown` - Detailed score analysis
    - Returns: base_score, provider points, signal points, risk points, total_score
    - Frontend: Modal UI with clickable score cells
  - Tests: Comprehensive test suite
    - `tests/test_ui_upgrade.py` - UI upgrade tests (sorting, pagination, search) - 20+ test cases
    - `tests/test_integration_g19.py` - Integration tests (auth e2e, UI upgrade e2e, protected routes) - 15+ test cases
    - `tests/test_auth.py` - Auth tests (OAuth flow, token generation, user management) - 22 test cases
  - Post-MVP Sprint 6 feature (authentication + UI enhancement)
- Production readiness documentation:
  - `PRODUCTION-READINESS-CRITIQUE-V2.md` - P0/P1/P2 hardening checklist with code examples
  - `PRODUCTION-ENGINEERING-GUIDE-V1.md` - SRE runbook with health checks, monitoring, deployment strategies

### Documentation
- Added comprehensive production readiness critique (v2) with health checks & probes
- Added production engineering guide (v1) with SRE practices and incident response runbook
- Added Azure AD setup guide (G19) with step-by-step instructions
- Archived completed phase documentation to `docs/archive/`

## [1.0.0] - 2025-11-14

### Added
- **Support Endpoint** (2025-11-15) - Added `/support` endpoint for support information
  - Returns support information with API documentation links
  - Footer link in Mini UI now functional
- **G18: ReScan + Alerts + Enhanced Scoring** - Automation and change detection
  - ReScan infrastructure:
    - `POST /scan/{domain}/rescan` - Manual rescan with change detection
    - `POST /scan/bulk/rescan` - Bulk rescan for multiple domains
    - Change detection for signals (SPF, DKIM, DMARC, MX) and scores
    - History tables: `signal_change_history`, `score_change_history`
  - Alerts system:
    - `GET /alerts` - List alerts with filters
    - `POST /alerts/config` - Configure alert preferences
    - `GET /alerts/config` - List alert configurations
    - Alert types: MX changed, DMARC added, Domain expire soon, Score changed
    - Notification methods: Email (placeholder), Webhook (HTTP POST), Slack (optional)
    - Alert configuration: Immediate or daily digest frequency
  - Enhanced scoring (AI-free):
    - DKIM none penalty (additional risk point)
    - SPF multiple includes risk detection
    - Enhanced risk scoring for security signals
  - Scheduler:
    - Daily rescan task via Celery Beat
    - Automatic change detection and alert generation
    - Configurable schedule (daily, weekly, monthly)
  - Database migration: `app/db/migrations/g18_rescan_alerts_scoring.sql`
  - Implementation:
    - `app/core/change_detection.py` - Change detection logic
    - `app/core/rescan.py` - ReScan engine
    - `app/core/notifications.py` - Notification engine
    - `app/api/rescan.py` - ReScan endpoints
    - `app/api/alerts.py` - Alerts endpoints
    - `app/db/models.py` - History and alert models
    - `app/core/celery_app.py` - Celery Beat schedule
    - `app/core/tasks.py` - Daily rescan task
  - Tests: Comprehensive test suite
    - `tests/test_rescan_alerts.py` - ReScan, change detection, and alerts tests
  - Post-MVP Sprint 5 feature (automation + change alerts)
  - **Bug Fixes (2025-11-14)**:
    - Fixed bulk rescan change detection (now uses `rescan_domain` with change detection)
    - Fixed alert notification processing (added Celery Beat task for pending alerts)
    - Fixed daily rescan change detection (now properly detects changes)
    - Added immediate alert processing trigger after rescan
- **G17: Notes, Tags, Favorites + PDF Summary** - CRM-lite features and PDF account summaries
  - Notes system:
    - `POST /leads/{domain}/notes` - Create a note for a domain
    - `GET /leads/{domain}/notes` - List all notes for a domain
    - `PUT /leads/{domain}/notes/{note_id}` - Update a note
    - `DELETE /leads/{domain}/notes/{note_id}` - Delete a note
    - Database table: `notes` with domain foreign key
  - Tags system:
    - `POST /leads/{domain}/tags` - Add a tag to a domain
    - `GET /leads/{domain}/tags` - List all tags for a domain
    - `DELETE /leads/{domain}/tags/{tag_id}` - Remove a tag from a domain
    - Database table: `tags` with domain foreign key and unique constraint
    - Auto-tagging: Automatically applies tags after domain scan:
      - `security-risk`: No SPF + no DKIM
      - `migration-ready`: Migration segment + score >= 70
      - `expire-soon`: Domain expires in < 30 days
      - `weak-spf`: SPF exists but DMARC policy is 'none'
      - `google-workspace`: Provider is Google
      - `local-mx`: Provider is Local
  - Favorites system:
    - `POST /leads/{domain}/favorite` - Add a domain to favorites
    - `GET /leads?favorite=true` - List favorite domains (session-based)
    - `DELETE /leads/{domain}/favorite` - Remove a domain from favorites
    - Database table: `favorites` with domain and user_id (session-based)
  - PDF Summary:
    - `GET /leads/{domain}/summary.pdf` - Generate PDF account summary
    - Includes: Provider info, SPF/DKIM/DMARC status, expiry date, signals, scores, risks
    - Uses ReportLab for PDF generation
  - Database migration: `app/db/migrations/g17_notes_tags_favorites.sql`
  - Implementation:
    - `app/core/auto_tagging.py` - Auto-tagging logic
    - `app/api/notes.py` - Notes endpoints
    - `app/api/tags.py` - Tags endpoints
    - `app/api/favorites.py` - Favorites endpoints
    - `app/api/pdf.py` - PDF summary endpoint
    - `app/db/models.py` - Note, Tag, Favorite models
  - Tests: Comprehensive test suite
    - `tests/test_notes_tags_favorites.py` - Notes, tags, favorites, and auto-tagging tests
    - `tests/test_pdf.py` - PDF generation tests
  - Post-MVP Sprint 4 feature (CRM-lite + PDF summary)
- **G16: Webhook + Lead Enrichment** - Webhook ingestion with API key authentication and lead enrichment
  - `POST /ingest/webhook` endpoint for webhook data ingestion
    - API key authentication via `X-API-Key` header
    - Rate limiting per API key (configurable, default: 60 requests/minute)
    - Automatic domain normalization and company upsert
    - Lead enrichment with contact emails, quality score, and LinkedIn pattern detection
    - Retry logic with exponential backoff for failed requests (max 3 retries)
    - Error logging and webhook failure tracking
  - `POST /admin/api-keys` endpoint for API key generation
    - Generate secure API keys (SHA-256 hashed)
    - Configurable rate limits per key
    - Key activation/deactivation support
  - `GET /admin/api-keys` endpoint for listing API keys
  - `PATCH /admin/api-keys/{key_id}/activate` and `/deactivate` endpoints
  - `POST /leads/{domain}/enrich` endpoint for manual lead enrichment
  - Database schema updates:
    - `api_keys` table for API key management
    - `webhook_retries` table for retry tracking
    - `companies.contact_emails` (JSONB array) for contact email storage
    - `companies.contact_quality_score` (integer, 0-100) for quality scoring
    - `companies.linkedin_pattern` (string) for LinkedIn email pattern detection
  - Lead enrichment features:
    - Contact quality score calculation (based on email count and domain matching)
    - LinkedIn email pattern detection (firstname.lastname, f.lastname, firstname)
    - Email deduplication and normalization
  - Implementation:
    - `app/core/api_key_auth.py` - API key authentication and rate limiting
    - `app/core/enrichment.py` - Lead enrichment logic
    - `app/core/webhook_retry.py` - Retry logic with exponential backoff
    - `app/api/admin.py` - Admin endpoints for API key management
    - `app/api/ingest.py` - Webhook endpoint
    - `app/api/leads.py` - Enrichment endpoint and updated GET /leads/{domain}
    - `app/db/migrations/g16_webhook_enrichment.sql` - Database migration script
  - Tests: Comprehensive test suite (20+ test cases)
    - `tests/test_webhook.py` - Webhook endpoint tests (10 tests)
    - `tests/test_enrichment.py` - Enrichment logic tests (10 tests)
    - `tests/test_api_key_auth.py` - API key authentication tests
  - Post-MVP Sprint 3 feature (webhook infrastructure + basic enrichment)
- **G15: Bulk Scan & Async Queue** - Async bulk domain scanning with progress tracking
  - `POST /scan/bulk` endpoint for creating bulk scan jobs (up to 1000 domains)
  - `GET /scan/bulk/{job_id}` endpoint for checking job status and progress
  - `GET /scan/bulk/{job_id}/results` endpoint for retrieving scan results
  - Celery + Redis integration for async task processing
  - Rate limiting: DNS (10 req/s), WHOIS (5 req/s) per worker
  - Progress tracking with Redis (job status, progress percentage, error tracking)
  - Error handling: Partial failure support, retry logic, exponential backoff
  - Worker configuration: 5 concurrent tasks, 15s per-domain timeout, 2 max retries
  - Docker Compose: Redis service and Celery worker service added
  - Implementation:
    - `app/core/celery_app.py` - Celery application configuration
    - `app/core/rate_limiter.py` - Rate limiting utilities (token bucket algorithm)
    - `app/core/progress_tracker.py` - Redis-based progress tracking
    - `app/core/tasks.py` - Celery tasks for bulk scanning
    - `app/api/scan.py` - Bulk scan API endpoints
  - Tests: Comprehensive test suite (19+ test cases)
    - `tests/test_rate_limiter.py` - Rate limiting tests (9 tests)
    - `tests/test_progress_tracker.py` - Progress tracking tests (10 tests)
    - `tests/test_error_handling.py` - Error handling tests
    - `tests/test_bulk_scan.py` - Integration tests for bulk scan API
  - Worker startup script: `scripts/start_celery_worker.sh`
  - Post-MVP Sprint 2 feature (core infrastructure)
- **G14: CSV Export** - Lead data export to CSV and Excel formats
  - `GET /leads/export` endpoint for exporting leads to CSV or Excel format
  - Filter parameters: `segment`, `min_score`, `provider` (same as GET /leads)
  - Format parameter: `csv` (default) or `xlsx`
  - Timestamped filename: `leads_YYYY-MM-DD_HH-MM-SS.csv` or `.xlsx`
  - Export includes all lead fields: domain, company_name, provider, segment, scores, signals, etc.
  - Implementation: Export endpoint added to `app/api/leads.py` router
  - Tests: `tests/test_export.py` - Comprehensive export tests (9 test cases)
  - Post-MVP feature (low-risk, core-independent)
- **G14: Mini UI** - Simple web interface for demo and internal use
  - HTML + Vanilla JavaScript + CSS (no framework)
  - `mini-ui/` directory structure with modular JS (api.js, ui-leads.js, ui-forms.js, app.js)
  - Features:
    - CSV/Excel file upload with auto-detect columns option
    - Single domain scan with auto-ingest (if company name provided)
    - Leads table with filters (segment, min score, provider)
    - CSV export button
    - Dashboard statistics (KPI: total leads, migration count, max score)
  - Static file serving via FastAPI (`app.mount("/mini-ui", ...)`)
  - Responsive design (mobile-friendly)
  - BEM CSS pattern for maintainability
  - API-first approach (all business logic in backend)
  - Documentation: `mini-ui/README-mini-ui.md`, `mini-ui/TEST-CHECKLIST.md`
  - Post-MVP feature (low-risk, core-independent, demo-ready)

### Fixed
- **G20: Scan Endpoint Missing Fields** (2025-11-15) - Fixed missing G20 fields in `/scan/domain` endpoint
  - Added `tenant_size` calculation and saving for M365/Google providers
  - Added `local_provider` detection and saving for Local providers
  - Added `dmarc_coverage` saving from DNS analysis
  - Response model now includes all G20 fields (tenant_size, local_provider, dmarc_coverage)
  - Fixes issue where tenant_size and local_provider were not populated during domain scanning
- **PDF Turkish Character Support** (2025-11-15) - Fixed Turkish character encoding in PDF generation
  - Table cells now use Paragraph objects for UTF-8 support
  - Turkish characters (ı, ş, ğ, ü, ö, ç) now display correctly in PDF
  - Fixed "Zayıf sinyaller" → "Zay f sinyaller" issue
  - Applied to all tables: Domain Information, Security Status, Scores, Signals
  - Analysis section now properly displays Turkish text

## [0.5.0] - 2025-01-27

### Added
- **Hard-Fail Rules**: Domains with missing MX records are automatically assigned Skip segment
  - `check_hard_fail()` function in `app/core/scorer.py`
  - Hard-fail check happens before scoring calculation
  - Returns Skip segment with score 0 and clear reason message

- **Risk Scoring**: Negative points for missing security signals
  - `risk_points` section in `app/data/rules.json`
  - Risk penalties: no SPF (-10), no DKIM (-10), DMARC none (-10), hosting MX weak (-10)
  - Risk scoring applied in `calculate_score()` function

### Changed
- **Provider Points**: Updated provider point values
  - Hosting: 10 → **20** (better reflects hosting provider value)
  - Local: 0 → **10** (self-hosted domains have some value)

- **Scoring Logic**: Enhanced scoring calculation
  - `calculate_score()` now applies risk points (negative)
  - Score is floored at 0 and capped at 100
  - `score_domain()` checks hard-fail conditions first

- **API**: Updated `POST /scan/domain` endpoint
  - Now passes `mx_records` to `score_domain()` for hard-fail checking

### Testing
- Added comprehensive tests for hard-fail rules (`TestHardFailRules`)
- Added comprehensive tests for risk scoring (`TestRiskScoring`)
- Added tests for updated provider points (`TestProviderPointsUpdate`)
- All 33 tests passing

### Documentation
- Updated `docs/SEGMENT-GUIDE.md` with risk scoring and hard-fail rules
- Updated `docs/plans/2025-01-27-phase0-hotfix-scoring.md` with implementation plan

## [0.4.0] - 2025-01-27

### Added
- Dashboard endpoint (`GET /dashboard`)
  - `app/api/dashboard.py` - Dashboard statistics endpoint
  - Segment distribution (Migration, Existing, Cold, Skip counts)
  - Average readiness score calculation
  - High priority leads count (Migration + score >= 70)
  - Empty database handling
  - Uses `leads_ready` VIEW for efficient aggregation

- Priority Score feature
  - `app/core/priority.py` - Priority score calculation module
  - `calculate_priority_score()` - Priority scoring logic based on segment and score
  - Priority levels: 1 (highest) to 6 (lowest)
  - Integration with `GET /leads` and `GET /leads/{domain}` endpoints
  - `LeadResponse` model updated with `priority_score` field

### Changed
- **API**: Updated `app/main.py` to register dashboard router
- **API**: Updated `app/api/leads.py` to include priority score in responses
- **Models**: Added `priority_score: Optional[int]` to `LeadResponse` model

## [0.3.0] - 2025-01-27

### Changed
- **Documentation**: Organized and archived completed MVP documentation
  - Archived: MVP-TRIMMED-ROADMAP.md, GO-NO-GO-CHECKLIST.md, PROJECT-EVALUATION.md, SALES-TEAM-EVALUATION.md, CRITIQUE.md
  - Active: SALES-FEATURE-REQUESTS.md, SALES-FEATURE-REQUESTS-CRITIQUE.md (MVP scope features)
  - Active: DEVELOPMENT-ENVIRONMENT.md, WSL-GUIDE.md (setup guides)

## [0.2.0] - 2025-11-12

### Added
- G4: Ingest Endpoints (CSV + Domain)
  - `app/core/merger.py` - Company upsert utilities (upsert_companies with domain unique key)
  - `app/api/ingest.py` - Ingest endpoints:
    - `POST /ingest/domain` - Single domain ingestion
    - `POST /ingest/csv` - CSV file ingestion with pandas
  - Domain extraction from email and website URLs
  - Idempotent company upsert (domain unique constraint)
  - Added `pandas==2.1.3` and `python-multipart==0.0.6` dependencies

- G5: DNS Analyzer
  - `app/core/analyzer_dns.py` - DNS analysis utilities:
    - `get_mx_records()` - MX record retrieval (sorted by priority)
    - `check_spf()` - SPF record validation
    - `check_dkim()` - DKIM record validation
    - `check_dmarc()` - DMARC policy extraction
    - `analyze_dns()` - Complete DNS analysis
  - MX root domain extraction
  - 10s timeout handling for DNS queries
  - Graceful error handling for DNS failures

- G6: WHOIS Analyzer
  - `app/core/analyzer_whois.py` - WHOIS lookup utilities:
    - `get_whois_info()` - WHOIS information retrieval
    - Registrar, expiration date, and nameservers extraction
  - 5s timeout handling
  - Graceful fail (WHOIS failures don't break scoring)

- G7: Scan Endpoint & Scoring Integration
  - `app/api/scan.py` - Domain scanning endpoint:
    - `POST /scan/domain` - Complete domain analysis (DNS + WHOIS + scoring)
  - Integration with DNS and WHOIS analyzers
  - Provider classification integration
  - Scoring and segment determination
  - Results saved to `domain_signals` and `lead_scores` tables

- G8: Leads API
  - `app/api/leads.py` - Lead query endpoints:
    - `GET /leads` - Filtered lead list (segment, min_score, provider filters)
    - `GET /leads/{domain}` - Single lead details
  - Uses `leads_ready` VIEW for efficient querying
  - Response time <1s for filtered queries

- G9: Tests & Edge Cases
  - `tests/test_scan_single.py` - DNS/WHOIS analyzer tests with mocks
  - `tests/test_scorer_rules.py` - Scoring rules and segment logic tests
  - `tests/test_ingest_csv.py` - CSV parsing and normalization tests
  - `tests/test_api_endpoints.py` - API endpoint integration tests (ingest, scan, leads)
  - Edge case coverage: timeouts, invalid domains, malformed CSV, missing MX records
  - Test coverage: 71% (75 tests passed, target ≥70% achieved)

- G10: Documentation & Demo
  - Complete README.md with setup instructions, API documentation, and example usage
  - WSL2 + Docker setup guide
  - Virtual environment setup instructions
  - Complete API endpoint documentation with examples
  - Demo scenario: 3 domain ingest → scan → leads query workflow
  - Development environment guide (`docs/active/DEVELOPMENT-ENVIRONMENT.md`)
  - WSL guide (`docs/active/WSL-GUIDE.md`)

- CI/CD Pipeline
  - `.github/workflows/ci.yml` - Complete CI pipeline:
    - Test execution with PostgreSQL service
    - Code coverage reporting
    - Docker image build
    - Docker Compose integration tests
  - `.github/workflows/lint.yml` - Code quality checks:
    - Black formatting check
    - Flake8 linting
    - MyPy type checking

### Changed
- **Dependencies**: Updated `requirements.txt` to include `idna`, `pandas`, `python-multipart`, `httpx` for ingestion and testing
- **API**: Updated `app/main.py` to register all API routers (ingest, scan, leads)
- **Documentation**: 
  - Updated README.md with complete API documentation and example usage
  - Updated documentation paths to reflect `docs/active/` structure
- **Development Tools**:
  - Enhanced `.gitignore` and `.cursorignore` with comprehensive Python, testing, and IDE exclusions
  - Added virtual environment setup script (`setup_venv.sh`) with Windows/Linux/Mac compatibility
  - Updated `setup_dev.sh` to support optional venv setup with `--with-venv` flag
  - Updated `docker-compose.yml` to mount `tests/` directory for container-based testing
- **Testing**: Improved test isolation: API endpoint tests use transaction rollback instead of table drops

### Fixed
- WHOIS analyzer exception handling (graceful fail for all exceptions)
- DNS analyzer timeout handling (proper status reporting)
- Virtual environment setup script Windows compatibility (python3 vs python command detection)
- Pip upgrade in venv script for cross-platform compatibility

### Removed
- Removed duplicate `scripts/wsl-setup-venv.sh` (functionality merged into `setup_venv.sh`)
- Consolidated WSL documentation: merged 3 separate files into single `docs/active/WSL-GUIDE.md`
- Simplified `setup_venv.sh`: removed redundant Python detection logic and WSL-specific warnings

### Deprecated
- N/A

### Security
- N/A

## [0.1.0] - 2025-11-12

### Added
- G1: Foundation & Docker Setup
  - Docker Compose setup with PostgreSQL 15 and FastAPI
  - FastAPI application skeleton with `/healthz` endpoint
  - Database connection and session management
  - Development setup script (`setup_dev.sh`)
  - Environment configuration (`.env.example`)

- G2: Database Schema & Models
  - PostgreSQL schema (`app/db/schema.sql`) with 4 tables and 1 view:
    - `raw_leads` - Raw ingested data
    - `companies` - Normalized company information (domain unique)
    - `domain_signals` - DNS and WHOIS analysis results
    - `lead_scores` - Calculated readiness scores and segments
    - `leads_ready` - View for querying ready leads
  - SQLAlchemy models (`app/db/models.py`): RawLead, Company, DomainSignal, LeadScore
  - Automatic schema migration script (`app/db/migrate.py`)

- G3: Domain Normalization & Data Files
  - `app/core/normalizer.py` - Domain normalization utilities:
    - `normalize_domain()` - Punycode decode, www stripping, lowercase
    - `extract_domain_from_email()` - Domain extraction from email addresses
    - `extract_domain_from_website()` - Domain extraction from website URLs
  - `app/core/provider_map.py` - Provider classification:
    - `load_providers()` - Load provider definitions from JSON
    - `classify_provider()` - Classify provider from MX root domain
  - `app/core/scorer.py` - Rule-based scoring engine:
    - `load_rules()` - Load scoring rules from JSON
    - `calculate_score()` - Calculate readiness score
    - `determine_segment()` - Determine lead segment (Migration, Existing, Cold, Skip)
    - `score_domain()` - Complete scoring workflow
  - `app/data/providers.json` - Provider definitions (10+ providers: M365, Google, Yandex, Zoho, Amazon, SendGrid, Mailgun, Hosting, Local, Unknown)
  - `app/data/rules.json` - Scoring rules (base_score, provider_points, signal_points, segment_rules)

### Changed
- N/A

### Fixed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Security
- N/A

