# TODO Tracking

This folder contains TODO lists and task tracking documents.

## Current Status

**Active TODOs:**
- `G21-architecture-refactor.md` - G21: Architecture Refactor - Hunter Slimming - 🔄 In Progress (2025-01-28)
  - ✅ Phase 0: Preparation & Snapshot (2025-11-16)
  - ✅ Phase 1: Deprecation Annotations (2025-11-16)
  - ✅ Phase 2: Sales Engine (2025-01-28)
  - ✅ Phase 3: Read-Only Mode (2025-01-28)
  - 🔄 Phase 4: Dynamics Migration (PAUSED - Integration Roadmap Phase 3 overlaps)
- `INTEGRATION-ROADMAP.md` - Integration Roadmap - 🔄 In Progress (2025-01-28)
  - ✅ Phase 1: Mini UI Stabilization (2025-01-28)
  - ✅ Phase 2: Partner Center Referrals (P1) - COMPLETED (2025-01-30)
  - ⏳ Phase 3: Dynamics 365 Integration (P2) - Pending
- `PARTNER-CENTER-PHASE2.md` - Partner Center Phase 2 - ✅ **COMPLETED** (2025-01-30)
  - ✅ Task 2.1: Partner Center API Client - COMPLETED (2025-01-28)
  - ✅ Task 2.2: Referral Data Model - COMPLETED (2025-01-28)
  - ✅ Task 2.3: Referral Ingestion - COMPLETED (2025-01-28)
  - ✅ Task 2.4: API Endpoints - COMPLETED (2025-01-30) - 7/7 tests passing
  - ✅ Task 2.5: UI Integration - COMPLETED (2025-01-30) - Referral column with badges
  - ✅ Task 2.6: Background Sync - COMPLETED (2025-01-30) - Celery Beat schedule, 10/10 tests passing
  - **Status**: ✅ **COMPLETED** - All tasks completed, all tests passing
  - **Progress**: 100% (6/6 tasks completed)
  - **Feature Flag**: `partner_center_enabled=False` (disabled by default, MVP-safe)

**Recently Completed:**
- `G20-IP-Enrichment-Production.md` - G20: IP Enrichment Production Activation - ✅ Completed (2025-01-28)
- `2025-01-28-STABILIZATION-SPRINT-stabilization.md` - Stabilization Sprint (3 gün) - ✅ Completed (2025-01-28)

**Archived TODOs:**
All completed TODO files have been moved to `docs/archive/`:
- `G20-IP-Enrichment-Production.md` - G20: IP Enrichment Production Activation - ✅ Completed (2025-01-28)
- `2025-01-28-STABILIZATION-SPRINT-stabilization.md` - Stabilization Sprint (3 gün) - ✅ Completed (2025-01-28)
- `2025-01-28-P1-PREPARATION.md` - P1 Preparation: Alembic, Rate Limiting, Caching, Bulk Operations, API Versioning (✅ Completed)
- `2025-01-27-G11-importer-email.md` - G11-G13: Importer + Email Module Implementation (✅ Completed)
- `2025-11-14-G14-post-mvp-sprint1.md` - G14: Post-MVP Sprint 1: CSV Export + UI Mini (✅ Completed)
- `2025-11-14-G15-bulk-scan-async.md` - G15: Sprint 2: Bulk Scan & Async Queue (✅ Completed)
- `2025-11-14-G16-webhook-enrichment.md` - G16: Sprint 3: Webhook + Basit Lead Enrichment (✅ Completed)
- `2025-11-14-G17-notes-tags-pdf.md` - G17: Sprint 4: Notes/Tags/Favorites + Basit PDF (✅ Completed)

## Format

Each TODO file should follow this format:

```markdown
# TODO: [Phase/Feature Name]

**Date Created**: YYYY-MM-DD
**Status**: In Progress/Completed/Archived
**Phase**: G1/G2/G3/etc.

## Tasks

- [ ] Task 1
- [x] Task 2 (completed)
- [ ] Task 3

## Notes

[Any relevant notes]
```

## Archive Policy

- Move to `docs/archive/` when phase is complete
- Keep only active TODOs in root
- Use date prefix for archived TODOs: `YYYY-MM-DD-todo-name.md`

