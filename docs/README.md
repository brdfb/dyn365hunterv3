# Documentation Structure

## 📁 Folder Organization

```
docs/
├── active/          # Active documentation (current phase)
├── archive/         # Archived documentation (completed phases)
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
- `SALES-PERSONA-v2.0.md` - Satışçı persona dokümantasyonu (v2.0: "Sistematik Avcı")
- `SALES-TRAINING.md` - Satış ekibi eğitim materyali (modüller, pratik egzersizler)
- `SALES-SCENARIOS.md` - Pratik senaryolar ve en iyi pratikler
- `SEGMENT-GUIDE.md` - Segment ve skor açıklamaları
- `SALES-ENGINE-REAL-WORLD-SMOKE-1.md` - Sales Engine real-world smoke test results
- `PHASE-2-1-SOFT-TUNING.md` - Sales Engine soft tuning mechanism
- `SALES-ENGINE-EXPECTED-OUTPUTS.md` - Sales Engine expected output skeletons

### API Documentation

**Location:** `docs/api/`

API contract documentation:
- `SALES-SUMMARY-V1-CONTRACT.md` - Sales Summary API v1 contract (stable, UI contract)

### Active Documentation

#### Reference Guides
- `DEVELOPMENT-ENVIRONMENT.md` - Development environment setup guide
- `WSL-GUIDE.md` - WSL2 setup and configuration guide
- `DOCKER-TROUBLESHOOTING.md` - Docker troubleshooting guide

#### Production Readiness Documentation
- `PRODUCTION-ENGINEERING-GUIDE-V1.md` - SRE runbook with health checks, monitoring, deployment strategies

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
  - **Phase 2**: 🔄 NEXT - Partner Center Referrals (P1) - 2-3 days
  - **Phase 3**: ⏳ Pending - Dynamics 365 Integration (P2) - 6-10 days
  - **Key Principle**: UI stability → Data ingestion → CRM integration
- `2025-01-28-INTEGRATION-TASKS.md` - Exact task list with branch names and acceptance criteria
- `2025-01-28-INTEGRATION-VS-STABILIZATION-CRITIQUE.md` - Critique of integration vs stabilization approach
- `IP-ENRICHMENT-UI-PATCH-PLAN.md` - IP enrichment UI integration patch plan (minimal approach)

#### Test & Validation Documentation
- `TEST-FIXES-COMPLETED.md` (2025-01-28) - Test fixes completion report
  - Fixed `dkim_none` risk penalty in test expectations
  - Fixed priority score ranges
  - All 86 scoring tests passing (0 failures)
  - Status: ✅ Completed

#### IP Enrichment Documentation
- `IP-ENRICHMENT-UI-PATCH-PLAN.md` (2025-01-28) - IP enrichment UI integration patch plan
  - Minimal approach: Country + proxy warning in score breakdown modal
  - IP context integration in sales engine for intelligent text generation
  - Status: ✅ Completed (2025-01-28)
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
- `NO-BREAK-REFACTOR-PLAN.md` - No-Break Refactor Plan: Hunter Architecture Slimming (G21) - 🔄 IN PROGRESS
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
- ✅ P0 Hardening: Completed (G19)
- ✅ P1 Performance: Completed (2025-01-28)
- ✅ Stabilization Sprint: Completed (2025-01-28) - v1.1-stable (Enterprise-Ready / UI-Stable / Integration-Ready)
- ✅ **Test Fixes**: Completed (2025-01-28) - Scoring engine fully validated (86 tests passing, 0 failures)
- 🔄 **Integration Roadmap**: In Progress (2025-01-28) - Correct sequence for external integrations
  - ✅ Phase 1: Mini UI Stabilization (P0.5) - Completed (1 day)
  - 🔄 Phase 2: Partner Center Referrals (P1) - NEXT (2-3 days)
  - ⏳ Phase 3: Dynamics 365 Integration (P2) - Pending (6-10 days)
- 🔄 G21: Architecture Refactor: In Progress (2025-01-28) - Hunter Slimming to Core Signal Engine
  - ✅ Phase 0: Preparation & Snapshot (2025-11-16)
  - ✅ Phase 1: Deprecation Annotations (2025-11-16)
  - ✅ Phase 2: Sales Engine (2025-01-28)
  - ✅ Phase 3: Read-Only Mode (2025-01-28) - Write endpoints disabled (410 Gone)
  - 🔄 Phase 4: Dynamics Migration (PAUSED - overlaps with Integration Roadmap Phase 3)
- 📋 P2 Backlog: Sync-first refactor, Repository pattern, N+1 query prevention

### Archived Documentation
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
  - **Phase 1**: 🔄 Next - Mini UI Stabilization (P0.5) - 1 day
  - **Phase 2**: ⏳ Pending - Partner Center Referrals (P1) - 2-3 days
  - **Phase 3**: ⏳ Pending - Dynamics 365 Integration (P2) - 6-10 days
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

