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

### Phase 0: Preparation & Snapshot
- [x] Database backup script created (`scripts/g21_phase0_backup.sh`)
- [x] Git tag script created (`scripts/g21_phase0_git_tag.sh`)
- [x] Usage metrics collection script created (`scripts/g21_phase0_metrics.sh`)
- [x] Dependency map created (`docs/g21-phase0-metrics/DEPENDENCY-MAP.md`)
- [ ] **Execute**: Database backup (run `bash scripts/g21_phase0_backup.sh`)
- [ ] **Execute**: Git tag (run `bash scripts/g21_phase0_git_tag.sh`)
- [ ] **Execute**: Usage metrics collection (run `bash scripts/g21_phase0_metrics.sh`)
- [ ] **Manual**: Check Power Automate flows for Notes/Tags/Favorites usage
- [ ] **Manual**: Check external API clients (application logs)

### Phase 1: Deprecation Annotations
- [ ] Create `app/core/deprecation.py`
- [ ] Deprecate `POST /leads/{domain}/notes`
- [ ] Deprecate `PUT /leads/{domain}/notes/{note_id}`
- [ ] Deprecate `DELETE /leads/{domain}/notes/{note_id}`
- [ ] Deprecate `POST /leads/{domain}/tags` (manual tags)
- [ ] Deprecate `DELETE /leads/{domain}/tags/{tag_id}` (manual tags)
- [ ] Deprecate `POST /leads/{domain}/favorite`
- [ ] Deprecate `DELETE /leads/{domain}/favorite`
- [ ] Test deprecation warnings

### Phase 2: Sales Engine (Additive)
- [ ] Create `app/core/sales_engine.py`
  - [ ] `generate_one_liner()`
  - [ ] `generate_call_script()`
  - [ ] `generate_discovery_questions()`
  - [ ] `recommend_offer_tier()`
  - [ ] `calculate_opportunity_potential()`
  - [ ] `calculate_urgency()`
  - [ ] `generate_sales_summary()`
- [ ] Create `app/api/sales_summary.py`
  - [ ] `GET /api/v1/leads/{domain}/sales-summary`
- [ ] Add to `app/main.py`
- [ ] Test new endpoint

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

**Current Phase**: Phase 0 (Preparation)

**Completed**: 0/6 phases

**Next Steps**: 
1. Create database backup
2. Create git tag
3. Collect usage metrics

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

