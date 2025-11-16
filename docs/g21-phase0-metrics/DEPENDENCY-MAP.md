# G21 Phase 0: Dependency Map

**Date**: 2025-01-28  
**Status**: Phase 0 - Preparation  
**Purpose**: Map all dependencies on Notes/Tags/Favorites endpoints before refactoring

---

## 📋 Endpoint Inventory

### Notes Endpoints

#### Write Endpoints (To be deprecated)
- `POST /leads/{domain}/notes` - Create note
- `PUT /leads/{domain}/notes/{note_id}` - Update note
- `DELETE /leads/{domain}/notes/{note_id}` - Delete note

#### Read Endpoints (To remain for migration support)
- `GET /leads/{domain}/notes` - List notes

**API Files:**
- `app/api/notes.py` - Legacy router
- `app/api/v1/notes.py` - V1 router (proxy to legacy)

**Database:**
- `notes` table (columns: id, domain, note, created_at, updated_at)

---

### Tags Endpoints

#### Write Endpoints (Manual tags only - To be deprecated)
- `POST /leads/{domain}/tags` - Add manual tag
- `DELETE /leads/{domain}/tags/{tag_id}` - Remove manual tag

#### Read Endpoints (To remain - Auto-tags needed)
- `GET /leads/{domain}/tags` - List tags (includes auto-tags)

**API Files:**
- `app/api/tags.py` - Legacy router
- `app/api/v1/tags.py` - V1 router (proxy to legacy)

**Database:**
- `tags` table (columns: id, domain, tag, created_at)
- Auto-tagging: `app/core/auto_tagging.py` (applies tags after scan)

**Auto-Tags (System-generated, will remain):**
- `security-risk` - No SPF + no DKIM
- `migration-ready` - Migration segment + score >= 70
- `expire-soon` - Domain expires in < 30 days
- `weak-spf` - SPF exists but DMARC policy is 'none'
- `google-workspace` - Provider is Google
- `local-mx` - Provider is Local

---

### Favorites Endpoints

#### Write Endpoints (To be deprecated)
- `POST /leads/{domain}/favorite` - Add favorite
- `DELETE /leads/{domain}/favorite` - Remove favorite

#### Read Endpoints (To remain for migration support)
- `GET /leads?favorite=true` - List favorites (handled in `app/api/leads.py`)

**API Files:**
- `app/api/favorites.py` - Legacy router
- `app/api/v1/favorites.py` - V1 router (proxy to legacy)
- `app/api/leads.py` - GET /leads?favorite=true endpoint

**Database:**
- `favorites` table (columns: id, domain, user_id, created_at)
- Session-based (no auth yet) - uses `session_id` cookie

---

## 🔍 Dependency Analysis

### 1. Mini UI Usage

**Status**: ✅ **NO USAGE FOUND**

**Analysis:**
- Searched `mini-ui/` directory for Notes/Tags/Favorites usage
- No API calls found in:
  - `mini-ui/index.html`
  - `mini-ui/js/ui-leads.js`
  - `mini-ui/js/app.js`
  - `mini-ui/js/api.js`
  - `mini-ui/js/ui-forms.js`

**Conclusion**: Mini UI does not use Notes/Tags/Favorites endpoints. Safe to deprecate.

---

### 2. Test Suite Usage

**Status**: ⚠️ **TESTS EXIST**

**Test File**: `tests/test_notes_tags_favorites.py`

**Test Coverage:**
- Notes: 4 tests (create, list, update, delete)
- Tags: 3 tests (create, list, delete)
- Favorites: 3 tests (add, list, remove)
- Auto-tagging: 2 tests (security-risk, migration-ready)

**Action Required:**
- Tests will need to be updated/removed in Phase 6 (Cleanup)
- For now, tests remain to verify deprecation warnings work

---

### 3. Power Automate Flows

**Status**: ❓ **UNKNOWN** (Requires manual check)

**Action Required:**
- Check Power Automate flows for API calls to Notes/Tags/Favorites endpoints
- Document any flows that use these endpoints
- Plan migration strategy for affected flows

**Endpoints to Check:**
- `POST /leads/{domain}/notes`
- `GET /leads/{domain}/notes`
- `POST /leads/{domain}/tags`
- `GET /leads/{domain}/tags`
- `POST /leads/{domain}/favorite`
- `GET /leads?favorite=true`

---

### 4. External API Clients

**Status**: ❓ **UNKNOWN** (Requires manual check)

**Action Required:**
- Check application logs for external API clients
- Document any clients using Notes/Tags/Favorites endpoints
- Plan migration strategy for affected clients

**Log Analysis:**
- Check Sentry/error tracking for endpoint usage
- Check application logs for API call patterns
- Check rate limiting metrics (if available)

---

### 5. Internal Code Dependencies

**Status**: ✅ **ANALYZED**

#### Notes
- **Used by**: None (standalone feature)
- **Dependencies**: `app/core/normalizer.py` (domain normalization)

#### Tags
- **Used by**: 
  - `app/core/auto_tagging.py` - Auto-tagging after scan
  - `app/api/leads.py` - Tags included in lead response
- **Dependencies**: 
  - `app/core/auto_tagging.py` - Will remain (auto-tags needed)
  - `app/api/leads.py` - Tags display (read-only, will remain)

#### Favorites
- **Used by**: 
  - `app/api/leads.py` - GET /leads?favorite=true filter
- **Dependencies**: 
  - `app/api/leads.py` - Favorites filter (read-only, will remain for migration)

---

## 📊 Database Schema

### Notes Table
```sql
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    note TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (domain) REFERENCES companies(domain)
);
```

### Tags Table
```sql
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    tag VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (domain) REFERENCES companies(domain),
    UNIQUE(domain, tag)
);
```

### Favorites Table
```sql
CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (domain) REFERENCES companies(domain),
    UNIQUE(domain, user_id)
);
```

---

## 🎯 Migration Impact Assessment

### Low Risk (Read-only endpoints remain)
- `GET /leads/{domain}/notes` - Migration support
- `GET /leads/{domain}/tags` - Auto-tags needed
- `GET /leads?favorite=true` - Migration support

### Medium Risk (Write endpoints deprecated)
- `POST /leads/{domain}/notes` - No known usage (Mini UI doesn't use)
- `PUT /leads/{domain}/notes/{note_id}` - No known usage
- `DELETE /leads/{domain}/notes/{note_id}` - No known usage
- `POST /leads/{domain}/tags` - Manual tags only (auto-tags remain)
- `DELETE /leads/{domain}/tags/{tag_id}` - Manual tags only
- `POST /leads/{domain}/favorite` - Session-based (no known external usage)
- `DELETE /leads/{domain}/favorite` - Session-based

### High Risk (Requires verification)
- Power Automate flows (unknown usage)
- External API clients (unknown usage)

---

## ✅ Phase 0 Completion Checklist

- [x] Database backup script created
- [x] Git tag script created
- [x] Usage metrics collection script created
- [x] Dependency map created
- [ ] Database backup executed
- [ ] Git tag created
- [ ] Usage metrics collected
- [ ] Power Automate flows checked (manual)
- [ ] External API clients checked (manual)

---

## 📝 Next Steps

1. **Execute Phase 0 scripts:**
   - `bash scripts/g21_phase0_backup.sh`
   - `bash scripts/g21_phase0_git_tag.sh`
   - `bash scripts/g21_phase0_metrics.sh`

2. **Manual verification:**
   - Check Power Automate flows for Notes/Tags/Favorites usage
   - Check application logs for external API clients
   - Update dependency map with findings

3. **Proceed to Phase 1:**
   - Create deprecation decorator
   - Add deprecation warnings to write endpoints
   - Test deprecation warnings

---

## 🔗 Related Documents

- `docs/active/NO-BREAK-REFACTOR-PLAN.md` - Detailed refactor plan
- `docs/todos/G21-architecture-refactor.md` - TODO list
- `docs/prompts/2025-01-28-hunter-architecture-refactor-decision.md` - Architectural decision

