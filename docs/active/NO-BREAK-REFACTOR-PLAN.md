# No-Break Refactor Plan: Hunter Architecture Slimming

**Date**: 2025-01-28  
**Status**: Planning  
**Priority**: P0 (Critical)  
**Estimated Duration**: 3-4 weeks  
**Risk Level**: 0-5% (with proper execution)

---

## Executive Summary

This plan implements the architectural decision to slim down Hunter to its core purpose: **"Thin, muscular signal engine that produces expensive signals."**

**Key Principle**: Zero-downtime, additive-first approach. No breaking changes.

**Total Risk**: 0-5% (with proper execution)

---

## Risk Matrix

| Phase | Risk | Description | Rollback |
|-------|------|-------------|----------|
| Faz 0 | 0/10 | Snapshot only | Not needed |
| Faz 1 | 1/10 | Deprecation warning | Remove decorator |
| Faz 2 | 0/10 | Additive, doesn't touch existing code | Delete new files |
| Faz 3 | 1/10 | Write disable, read works | Re-enable write |
| Faz 4 | 2/10 | Migration, external dependency | Revert from Dynamics |
| Faz 5 | 1/10 | Monitoring, documentation | Not needed |
| Faz 6 | 6/10 → 0/10 | Cleanup (after migration) | Rename tables back |

---

## Phase 0: Preparation & Snapshot (Risk: 0/10)

### Checklist

#### 1.1 System Snapshot
```bash
# Database backup
pg_dump dyn365hunter > backup_pre_refactor_$(date +%Y%m%d_%H%M%S).sql

# Code snapshot (git tag)
git tag pre-refactor-v1.0.0
git push origin pre-refactor-v1.0.0
```

#### 1.2 Current Usage Metrics
- [ ] Collect endpoint usage metrics:
  - `POST /leads/{domain}/notes` → calls/day
  - `POST /leads/{domain}/tags` → calls/day
  - `POST /leads/{domain}/favorite` → calls/day
  - `GET /leads/{domain}/notes` → calls/day
  - `GET /leads/{domain}/tags` → calls/day
  - `GET /leads?favorite=true` → calls/day

#### 1.3 Dependency Map
- [ ] Check Mini UI usage of Notes/Tags/Favorites
- [ ] Check Power Automate flows usage
- [ ] Check external API clients
- [ ] Check test suites

**Duration**: 1 day  
**Risk**: 0/10  
**Rollback**: Not needed

---

## Phase 1: Deprecation Annotations (Risk: 1/10)

### Checklist

#### 1.1 Create Deprecation Decorator
```python
# app/core/deprecation.py (NEW)
from functools import wraps
from fastapi import HTTPException
from datetime import datetime

DEPRECATION_DATE = datetime(2025, 2, 1)  # 30 days later
REMOVAL_DATE = datetime(2025, 3, 1)  # 60 days later

def deprecated_endpoint(
    reason: str,
    alternative: str,
    removal_date: datetime = REMOVAL_DATE
):
    """Mark endpoint as deprecated with warning."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Log deprecation warning
            logger.warning(
                f"Deprecated endpoint called: {func.__name__}",
                reason=reason,
                alternative=alternative,
                removal_date=removal_date.isoformat()
            )
            # Add deprecation headers
            response = await func(*args, **kwargs)
            response.headers["X-Deprecated"] = "true"
            response.headers["X-Deprecation-Reason"] = reason
            response.headers["X-Alternative"] = alternative
            response.headers["X-Removal-Date"] = removal_date.isoformat()
            return response
        return wrapper
    return decorator
```

#### 1.2 Deprecate Notes Endpoints
- [ ] `POST /leads/{domain}/notes` → deprecated
- [ ] `PUT /leads/{domain}/notes/{note_id}` → deprecated
- [ ] `DELETE /leads/{domain}/notes/{note_id}` → deprecated
- [ ] `GET /leads/{domain}/notes` → **NOT deprecated** (read-only, migration support)

#### 1.3 Deprecate Tags Endpoints
- [ ] `POST /leads/{domain}/tags` → deprecated (manual tags only)
- [ ] `DELETE /leads/{domain}/tags/{tag_id}` → deprecated (manual tags only)
- [ ] `GET /leads/{domain}/tags` → **NOT deprecated** (auto-tags needed)

#### 1.4 Deprecate Favorites Endpoints
- [ ] `POST /leads/{domain}/favorite` → deprecated
- [ ] `DELETE /leads/{domain}/favorite` → deprecated
- [ ] `GET /leads?favorite=true` → **NOT deprecated** (migration support)

#### 1.5 Test
```bash
# Test deprecation warnings
curl -X POST http://localhost:8000/leads/example.com/notes \
  -H "Content-Type: application/json" \
  -d '{"note": "test"}'
# Response headers should include X-Deprecated: true
```

**Duration**: 1 day  
**Risk**: 1/10  
**Rollback**: Remove deprecation decorator

---

## Phase 2: Sales Engine (Additive) (Risk: 0/10)

### Checklist

#### 2.1 Create Sales Engine Core
```python
# app/core/sales_engine.py (NEW)
# Completely new file, doesn't touch existing code
```

**Functions to implement:**
- [ ] `generate_one_liner()` - 1-sentence sales summary
- [ ] `generate_call_script()` - Call script bullets
- [ ] `generate_discovery_questions()` - Discovery questions
- [ ] `recommend_offer_tier()` - Basic/Pro/Enterprise recommendation
- [ ] `calculate_opportunity_potential()` - Opportunity score (0-100)
- [ ] `calculate_urgency()` - Urgency level (low/medium/high)
- [ ] `generate_sales_summary()` - Complete sales intelligence summary

#### 2.2 Create Sales Summary API
```python
# app/api/sales_summary.py (NEW)
# Completely new endpoint, doesn't touch existing endpoints
```

**Endpoint:**
- [ ] `GET /api/v1/leads/{domain}/sales-summary` → Returns complete sales intelligence JSON

#### 2.3 Add to Main.py
```python
# app/main.py
from app.api import sales_summary

# v1 router
v1_router.include_router(sales_summary.router)

# Legacy router
app.include_router(sales_summary.router, tags=["sales", "legacy"])
```

#### 2.4 Test
```bash
# Test new endpoint
curl "http://localhost:8000/api/v1/leads/example.com/sales-summary"
# Verify existing endpoints still work
curl "http://localhost:8000/leads/example.com"
```

**Duration**: 3-5 days  
**Risk**: 0/10  
**Rollback**: Delete new files

---

## Phase 3: Read-Only Mode (Risk: 1/10)

### Checklist

#### 3.1 Disable Write Endpoints (Soft)
```python
# app/api/notes.py
@router.post("/{domain}/notes", ...)
async def create_note(...):
    # Soft disable: 410 Gone
    raise HTTPException(
        status_code=410,
        detail={
            "error": "This endpoint is deprecated and disabled.",
            "reason": "Notes are now managed in Dynamics 365.",
            "alternative": "Use Dynamics 365 Timeline/Notes API",
            "migration_guide": "/docs/migration/notes-to-dynamics"
        }
    )
```

#### 3.2 Add Monitoring
```python
# app/core/monitoring.py
# Log deprecated endpoint calls
# Collect metrics:
# - Deprecated endpoint call count
# - Which clients are using them
# - Which domains are affected
```

#### 3.3 Test
```bash
# Test write endpoints are disabled
curl -X POST http://localhost:8000/leads/example.com/notes \
  -H "Content-Type: application/json" \
  -d '{"note": "test"}'
# Should return 410 Gone

# Test read endpoints still work
curl "http://localhost:8000/leads/example.com/notes"
# Should return 200 OK
```

**Duration**: 1 day  
**Risk**: 1/10  
**Rollback**: Re-enable write endpoints

---

## Phase 4: Dynamics Migration (Risk: 2/10)

### Checklist

#### 4.1 Create Migration Script
```python
# scripts/migrate_notes_to_dynamics.py
# Notes → Dynamics Timeline/Notes
# Tags → Dynamics Tags (manual tags only)
# Favorites → Dynamics Favorite field
```

#### 4.2 Dual-Write (Optional)
- [ ] Write to both Hunter and Dynamics during migration
- [ ] After migration, write only to Dynamics

#### 4.3 Test Migration
```bash
# Test migration in test environment
python scripts/migrate_notes_to_dynamics.py --dry-run
python scripts/migrate_notes_to_dynamics.py --execute
```

#### 4.4 Verify Migration
```bash
# Verify migration success
# Hunter note count = Dynamics note count
# Hunter tag count = Dynamics tag count (manual only)
# Hunter favorite count = Dynamics favorite count
```

**Duration**: 1-2 weeks  
**Risk**: 2/10  
**Rollback**: Revert from Dynamics to Hunter

---

## Phase 5: Monitoring & Stabilization (Risk: 1/10)

### Checklist

#### 5.1 Monitoring Dashboard
- [ ] Deprecated endpoint usage metrics
  - Daily call count
  - Which clients are using them
  - Error rate
  - Response time

#### 5.2 Alerting
- [ ] If deprecated endpoint usage < 10% → Migration successful, can proceed to cleanup
- [ ] If deprecated endpoint usage > 50% → Migration not complete, don't cleanup yet

#### 5.3 Update Documentation
- [ ] `docs/migration/notes-to-dynamics.md` - Migration guide
- [ ] API documentation updates
- [ ] Sales guide updates

**Duration**: 1 week  
**Risk**: 1/10  
**Rollback**: Not needed

---

## Phase 6: Cleanup (Risk: 6/10 → 0/10 after migration)

### Checklist

#### 6.1 Remove Deprecated Endpoints
- [ ] Remove `POST /leads/{domain}/notes`
- [ ] Remove `PUT /leads/{domain}/notes/{note_id}`
- [ ] Remove `DELETE /leads/{domain}/notes/{note_id}`
- [ ] Keep `GET /leads/{domain}/notes` (read-only, migration support)

- [ ] Remove `POST /leads/{domain}/tags` (manual tags)
- [ ] Remove `DELETE /leads/{domain}/tags/{tag_id}` (manual tags)
- [ ] Keep `GET /leads/{domain}/tags` (auto-tags needed)

- [ ] Remove `POST /leads/{domain}/favorite`
- [ ] Remove `DELETE /leads/{domain}/favorite`
- [ ] Keep `GET /leads?favorite=true` (migration support)

#### 6.2 Archive Database Tables
```sql
-- Don't delete, just rename
ALTER TABLE notes RENAME TO notes_archived_20250201;
ALTER TABLE tags RENAME TO tags_archived_20250201;
ALTER TABLE favorites RENAME TO favorites_archived_20250201;

-- OR: Remove write permissions only
REVOKE INSERT, UPDATE, DELETE ON notes FROM app_user;
REVOKE INSERT, UPDATE, DELETE ON tags FROM app_user;
REVOKE INSERT, UPDATE, DELETE ON favorites FROM app_user;
```

#### 6.3 Test
```bash
# Test all endpoints still work
# Verify read-only endpoints work
# Verify write endpoints return 404
```

**Duration**: 1 day  
**Risk**: 6/10 (after migration → 0/10)  
**Rollback**: Rename tables back, restore endpoints

---

## Monitoring Checklist

### After Each Phase

- [ ] API response time < 500ms
- [ ] Error rate < 0.1%
- [ ] Deprecated endpoint usage decreasing?
- [ ] Read endpoints working?
- [ ] Write endpoints disabled?
- [ ] Migration successful?
- [ ] UI not broken?

### Alerting

```python
# If deprecated endpoint usage > 50%
# → Alert: Migration not complete, don't cleanup yet

# If deprecated endpoint usage < 10%
# → Alert: Migration successful, can proceed to cleanup

# If error rate > 1%
# → Alert: Consider rollback
```

---

## Implementation Files

### New Files
- `app/core/deprecation.py` - Deprecation decorator
- `app/core/sales_engine.py` - Sales intelligence engine
- `app/api/sales_summary.py` - Sales summary endpoint
- `scripts/migrate_notes_to_dynamics.py` - Migration script
- `docs/migration/notes-to-dynamics.md` - Migration guide

### Modified Files
- `app/api/notes.py` - Add deprecation annotations
- `app/api/tags.py` - Add deprecation annotations
- `app/api/favorites.py` - Add deprecation annotations
- `app/main.py` - Add sales_summary router
- `app/core/monitoring.py` - Add deprecated endpoint metrics

### Files to Remove (Phase 6)
- `app/api/pdf.py` - PDF generation (move to Dynamics)
- `app/api/dashboard.py` - Dashboard (move to Power BI)

---

## Success Criteria

1. ✅ Zero downtime during refactoring
2. ✅ No breaking changes to existing integrations
3. ✅ All deprecated endpoints properly marked
4. ✅ Sales engine fully functional
5. ✅ Migration to Dynamics successful
6. ✅ Monitoring in place
7. ✅ Documentation updated
8. ✅ Cleanup completed

---

## Related Documents

- `docs/prompts/2025-01-28-hunter-architecture-refactor-decision.md` - Architectural decision
- `docs/todos/G21-architecture-refactor.md` - TODO list

