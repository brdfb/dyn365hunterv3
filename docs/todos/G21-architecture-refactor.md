# G21: Architecture Refactor - Hunter Slimming

**Date Created**: 2025-01-28  
**Status**: In Progress  
**Phase**: G21 (Architecture Refactor)  
**Priority**: P0 (Critical)  
**Estimated Duration**: 3-4 weeks

---

## 🎯 Phase Goal

Refactor Hunter to its core purpose: **"Thin, muscular signal engine that produces expensive signals."**

Remove CRM-lite features (Notes/Tags/Favorites) and move them to Dynamics 365.

Add Sales Engine (sales intelligence layer).

---

## 📋 Tasks

### Phase 0: Preparation & Snapshot ✅ **COMPLETED** (2025-11-16)
- [x] Database backup script created (`scripts/g21_phase0_backup.sh`)
- [x] Git tag script created (`scripts/g21_phase0_git_tag.sh`)
- [x] Usage metrics collection script created (`scripts/g21_phase0_metrics.sh`)
- [x] Dependency map created (`docs/g21-phase0-metrics/DEPENDENCY-MAP.md`)
- [x] **Execute**: Database backup (✅ `backups/backup_pre_refactor_20251116_101321.sql` - 47K)
- [x] **Execute**: Git tag (✅ `pre-refactor-v1.0.0` - pushed to remote)
- [x] **Execute**: Usage metrics collection (✅ `docs/g21-phase0-metrics/usage_metrics_20251116_101559.json`)
- [x] **Analysis**: Notes/Tags/Favorites tables do NOT exist - features never used
- [x] **Analysis**: Mini UI does not use Notes/Tags/Favorites endpoints
- [x] **Analysis**: Test suite exists (will be updated in Phase 6)
- [ ] **Manual**: Check Power Automate flows for Notes/Tags/Favorites usage (non-blocking)
- [ ] **Manual**: Check external API clients (application logs) (non-blocking)

**Completion Report**: `docs/g21-phase0-metrics/PHASE0-COMPLETION.md`

### Phase 1: Deprecation Annotations ✅ **COMPLETED** (2025-11-16)
- [x] Create `app/core/deprecation.py` (✅ decorator with logging and response headers)
- [x] Deprecate `POST /leads/{domain}/notes` (✅ decorator added)
- [x] Deprecate `PUT /leads/{domain}/notes/{note_id}` (✅ decorator added)
- [x] Deprecate `DELETE /leads/{domain}/notes/{note_id}` (✅ decorator added)
- [x] Deprecate `POST /leads/{domain}/tags` (✅ decorator added - manual tags only)
- [x] Deprecate `DELETE /leads/{domain}/tags/{tag_id}` (✅ decorator added - manual tags only)
- [x] Deprecate `POST /leads/{domain}/favorite` (✅ decorator added)
- [x] Deprecate `DELETE /leads/{domain}/favorite` (✅ decorator added)
- [x] Test deprecation warnings (✅ decorator tested - note: tables don't exist, so endpoints return 500, but decorator is applied)

**Note**: Notes/Tags/Favorites tables don't exist (Phase 0 finding), so endpoints return 500 errors. Deprecation decorator is correctly applied and will log warnings when endpoints are called.

### Phase 2: Sales Engine (Additive) ✅ **COMPLETED** (2025-01-28)
- [x] Create `app/core/sales_engine.py`
  - [x] `generate_one_liner()` - 1-sentence sales summary
  - [x] `generate_call_script()` - Call script bullets
  - [x] `generate_discovery_questions()` - Discovery questions
  - [x] `recommend_offer_tier()` - Basic/Pro/Enterprise recommendation
  - [x] `calculate_opportunity_potential()` - Opportunity score (0-100)
  - [x] `calculate_urgency()` - Urgency level (low/medium/high)
  - [x] `generate_sales_summary()` - Complete sales intelligence summary
- [x] Create `app/api/sales_summary.py`
  - [x] `GET /api/v1/leads/{domain}/sales-summary` - Returns complete sales intelligence JSON
- [x] Create `app/api/v1/sales_summary.py` (v1 router)
- [x] Add to `app/main.py` (v1 router + legacy router)
- [x] Test new endpoint (verify existing endpoints still work)
- [x] Core unit tests (38 tests, all passing)
- [x] API integration tests (7 tests, all passing)
- [x] Real-world smoke test (3 domains, all validated)
- [x] API contract documentation (`docs/api/SALES-SUMMARY-V1-CONTRACT.md`)
- [x] Frontend type definitions (TypeScript + JSDoc)
- [x] Logging/telemetry (`sales_summary_viewed` event)
- [x] Tuning factor configuration (Phase 2.1)

### Phase 3: Read-Only Mode
- [ ] Disable write endpoints (soft - 410 Gone)
- [ ] Add monitoring for deprecated endpoints
- [ ] Test read endpoints still work
- [ ] Test write endpoints return 410

### Phase 4: Dynamics Migration
- [ ] Create `scripts/migrate_notes_to_dynamics.py`
- [ ] Migrate Notes → Dynamics Timeline/Notes
- [ ] Migrate Tags → Dynamics Tags (manual only)
- [ ] Migrate Favorites → Dynamics Favorite field
- [ ] Test migration (dry-run)
- [ ] Execute migration
- [ ] Verify migration success

### Phase 5: Monitoring & Stabilization
- [ ] Create monitoring dashboard
- [ ] Add alerting rules
- [ ] Update documentation
  - [ ] `docs/migration/notes-to-dynamics.md`
  - [ ] API documentation
  - [ ] Sales guide

### Phase 6: Cleanup
- [ ] Remove deprecated endpoints
- [ ] Archive database tables (rename, don't delete)
- [ ] Remove `app/api/pdf.py` (move to Dynamics)
- [ ] Remove `app/api/dashboard.py` (move to Power BI)
- [ ] Test all endpoints
- [ ] Update CHANGELOG.md
- [ ] Update README.md

---

## 📊 Progress Tracking

**Current Phase**: Phase 3 (Read-Only Mode) 🔄 **NEXT**

**Completed**: 3/7 phases (Phase 0 ✅, Phase 1 ✅, Phase 2 ✅)

**Phase 2 Status**: ✅ **COMPLETED** (2025-01-28)
- Core implementation: ✅
- Tests: ✅ (45 tests, all passing)
- Real-world validation: ✅ (3 domains tested)
- API contract: ✅ (frozen, UI-ready)
- Logging/telemetry: ✅
- Tuning mechanism: ✅ (Phase 2.1)

**Next Steps**: 
1. Phase 3: Read-Only Mode (disable write endpoints)
2. UI integration (Sales Intel tab in lead detail page)
3. Monitor sales feedback for tuning adjustments

---

## 🔗 Related Documents

- `docs/prompts/2025-01-28-hunter-architecture-refactor-decision.md` - Architectural decision
- `docs/active/NO-BREAK-REFACTOR-PLAN.md` - Detailed implementation plan

---

## ✅ Success Criteria

1. Zero downtime during refactoring
2. No breaking changes to existing integrations
3. All deprecated endpoints properly marked
4. Sales engine fully functional
5. Migration to Dynamics successful
6. Monitoring in place
7. Documentation updated
8. Cleanup completed

