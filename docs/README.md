# Documentation Structure

## 📁 Folder Organization

```
docs/
├── active/          # Active documentation (current phase)
├── archive/         # Archived documentation (completed phases)
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

### Active Documentation

#### Reference Guides
- `DEVELOPMENT-ENVIRONMENT.md` - Development environment setup guide
- `WSL-GUIDE.md` - WSL2 setup and configuration guide
- `TESTING.md` - Testing guide and troubleshooting
- `DOCKER-TROUBLESHOOTING.md` - Docker troubleshooting guide
- `TEST-COVERAGE-ANALYSIS.md` - Test coverage analysis report

#### Production Readiness Documentation
- `PRODUCTION-READINESS-CRITIQUE-V2.md` - P0/P1/P2 hardening checklist with code examples
- `PRODUCTION-ENGINEERING-GUIDE-V1.md` - SRE runbook with health checks, monitoring, deployment strategies
- `G19-PRE-FLIGHT-CHECKLIST.md` - G19 pre-flight checklist (✅ Completed - Production hardening)

**Note:** Active documentation contains reference guides and production readiness documentation. Feature documentation and completed phase documentation have been moved to `archive/`. Planning documentation is in `plans/`.

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
- `2025-01-28-PROVIDER-CHANGE-TRACKING.md` - Provider Change Tracking feature documentation (Completed)
- `2025-01-28-DOMAIN-VALIDATION.md` - Domain Validation feature documentation (Completed)
- `2025-01-28-DUPLICATE-PREVENTION.md` - Duplicate Prevention feature documentation (Completed)
- `2025-01-28-G19-PRE-FLIGHT-CHECKLIST.md` - G19 Pre-Flight Checklist: Production Hardening (✅ Completed - 2025-01-28)
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

### Project Plans

**Active Plans:**
- `2025-11-14-FINAL-ROADMAP.md` - **Final Roadmap - Post-MVP Sprint 2-6 (G15-G19)** - Active roadmap (G19 planned)

**Archived Plans:**
All completed planning documentation has been moved to `docs/archive/`:
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
- `G19-auth-ui-advanced.md` - Sprint 6: Auth + UI + Advanced Features (📋 Planned)

**Archived TODOs:**
All completed TODO files have been moved to `docs/archive/`:
- `2025-01-27-G11-importer-email.md` - G11-G13: Importer + Email Module Implementation (✅ Completed)
- `2025-11-14-G14-post-mvp-sprint1.md` - G14: Post-MVP Sprint 1: CSV Export + UI Mini (✅ Completed)
- `2025-11-14-G15-bulk-scan-async.md` - G15: Sprint 2: Bulk Scan & Async Queue (✅ Completed)
- `2025-11-14-G16-webhook-enrichment.md` - G16: Sprint 3: Webhook + Basit Lead Enrichment (✅ Completed)
- `2025-11-14-G17-notes-tags-pdf.md` - G17: Sprint 4: Notes/Tags/Favorites + Basit PDF (✅ Completed)
- `2025-11-14-G18-rescan-alerts-scoring.md` - G18: Sprint 5: ReScan + Alerts + Enhanced Scoring (✅ Completed)

