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
- `INTEGRATION-ROADMAP.md` - Integration Roadmap - ✅ **COMPLETED** (2025-01-30 - Production Ready)
  - ✅ Phase 1: Mini UI Stabilization (2025-01-28)
  - ✅ Phase 2: Partner Center Referrals (P1) - COMPLETED (2025-01-30)
  - ✅ Phase 3: Dynamics 365 Integration (P2) - **COMPLETED** (2025-01-30 - Production Ready)
    - ✅ Phase 2.5 (Backend): %94 completed
    - ✅ Phase 3 (UI): Completed
    - ✅ Roast Sprint: Completed (5/5 tasks)
    - ✅ D365 Lead Push PoC: Completed (2025-01-30) - End-to-end flow working
    - ✅ Phase 2.9 (E2E): ✅ COMPLETED (2025-01-30) - Production-grade E2E testleri (3 senaryo), Go/No-Go: ✅ GO
    - ✅ PROD Öncesi Kritik İşler: ✅ COMPLETED (2025-01-30) - Retry + Error Handling FINAL, Basic N+1 Optimization, UI Polish Minimum
    - ✅ Production Readiness: ✅ **PRODUCTION READY** → PROD SAFE MODE RELEASE hazır

**Recently Completed:**
- `PARTNER-CENTER-PHASE2.md` - Partner Center Phase 2 - ✅ Completed (2025-01-30) → Archived
- `PARTNER-CENTER-PHASE2-REFERRALS-V1.md` - Partner Center Referrals Sync v1 Productization - ✅ Completed (2025-01-30) → Archived
- `G20-IP-Enrichment-Production.md` - G20: IP Enrichment Production Activation - ✅ Completed (2025-01-28)
- `2025-01-28-STABILIZATION-SPRINT-stabilization.md` - Stabilization Sprint (3 gün) - ✅ Completed (2025-01-28)

**Archived TODOs:**
All completed TODO files have been moved to `docs/archive/`:
- `2025-01-30-PARTNER-CENTER-PHASE2.md` - Partner Center Phase 2 - ✅ Completed (2025-01-30)
- `2025-01-30-PARTNER-CENTER-PHASE2-REFERRALS-V1.md` - Partner Center Referrals Sync v1 Productization - ✅ Completed (2025-01-30)
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

