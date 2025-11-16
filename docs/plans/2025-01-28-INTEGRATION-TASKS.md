# Integration Tasks - Exact Task List

**Date**: 2025-01-28  
**Status**: 🔄 **In Progress** (Phase 1: ✅ Completed, Phase 2: Next)  
**Sequence**: Phase 1 → Phase 2 → Phase 3 (non-negotiable)

---

## 🎯 Phase 1: Mini UI Stabilization (P0.5)

**Branch**: `feature/ui-stabilization-v1.1`  
**Duration**: 1 day  
**Priority**: P0.5 (CRITICAL - blocks everything)

### Task 1.1: Button & Modal Fixes

**Files**: `mini-ui/js/ui-leads.js`, `mini-ui/styles.css`

- [x] Fix button hover states (scale transform + color change)
- [x] Fix modal backdrop click behavior (only close on overlay click)
- [x] Fix modal ESC key handling (keyboard event listener)
- [x] Fix modal scroll optimization (max-height: 80vh, overflow-y: auto)

**Acceptance Criteria**:
- All buttons have smooth hover effects
- Modal closes on backdrop click (not on modal content)
- ESC key closes modal
- Modal scrolls smoothly when content is long

---

### Task 1.2: Score Breakdown Improvements

**Files**: `mini-ui/js/ui-leads.js`, `mini-ui/styles.css`

- [x] Fix score breakdown modal bugs (if any)
- [x] Improve tooltip positioning (CSS-based tooltip system)
- [x] Fix signal/risk display order (SPF → DKIM → DMARC → Risks)
- [x] Add loading states for score breakdown (spinner while fetching)

**Acceptance Criteria**:
- Score breakdown modal works flawlessly
- Tooltips appear in correct position
- Signal/risk order is consistent
- Loading spinner shows while fetching score breakdown

---

### Task 1.3: Loading States

**Files**: `mini-ui/js/ui-leads.js`, `mini-ui/styles.css`, `mini-ui/index.html`

- [x] Add loading spinner for table (show while fetching leads)
- [x] Add loading states for filters (disable during fetch)
- [x] Add loading states for export buttons (disable during export)
- [x] Optimize loading transitions (smooth fade-in/out)

**Acceptance Criteria**:
- Table shows spinner while loading
- Filters disabled during fetch
- Export buttons show loading state
- Transitions are smooth

---

### Task 1.4: Filter Bar UX

**Files**: `mini-ui/js/ui-leads.js`, `mini-ui/styles.css`, `mini-ui/index.html`

- [x] Fix filter bar layout (responsive, proper spacing)
- [x] Improve filter dropdown UX (better styling, hover effects)
- [x] Add filter clear button (clear all filters at once)
- [x] Add filter state persistence (remember filters in localStorage)

**Acceptance Criteria**:
- Filter bar looks good on all screen sizes
- Dropdowns are easy to use
- Clear button works
- Filters persist across page reloads

---

### Task 1.5: General UX Polish

**Files**: `mini-ui/js/ui-leads.js`, `mini-ui/styles.css`, `mini-ui/index.html`

- [x] Fix table row hover effects (smooth highlight)
- [x] Improve pagination UX (better button styling, page info)
- [x] Fix empty state messages (clear CTA)
- [x] Add toast notification improvements (better positioning, auto-dismiss)

**Acceptance Criteria**:
- Table rows highlight smoothly on hover
- Pagination is intuitive
- Empty state is helpful
- Toast notifications are non-intrusive

---

## 🔄 Phase 2: Partner Center Referrals Integration (P1)

**Branch**: `feature/partner-center-referrals`  
**Duration**: 2-3 days  
**Priority**: P1

### Task 2.1: Partner Center API Client

**Files**: `app/core/partner_center.py` (NEW)

- [ ] Create Partner Center API client class
- [ ] Implement OAuth 2.0 authentication (or API key if simpler)
- [ ] Implement `get_referrals()` function (GET referrals endpoint)
- [ ] Handle rate limiting (respect Partner Center rate limits)
- [ ] Handle token refresh (automatic token renewal)
- [ ] Add error handling (network errors, API errors)
- [ ] Add logging (structured logging with PII masking)

**Acceptance Criteria**:
- Can authenticate with Partner Center
- Can fetch referrals successfully
- Rate limiting respected
- Token refresh works automatically
- Errors handled gracefully

---

### Task 2.2: Referral Data Model

**Files**: `app/db/models.py`, `alembic/versions/XXXX_add_partner_center_referrals.py` (NEW)

- [ ] Create `PartnerCenterReferral` SQLAlchemy model
- [ ] Fields: `id`, `referral_id` (unique), `company_name`, `domain`, `status`, `created_at`, `updated_at`
- [ ] Create Alembic migration script
- [ ] Add indexes: `referral_id` (unique), `domain`, `status`
- [ ] Test migration (upgrade/downgrade)

**Acceptance Criteria**:
- Model created with all required fields
- Migration script works
- Indexes created
- Migration can be rolled back

---

### Task 2.3: Referral Ingestion

**Files**: `app/core/referral_ingestion.py` (NEW)

- [ ] Create referral ingestion module
- [ ] Implement referral → domain normalization (`normalize_domain()`)
- [ ] Implement referral → company upsert (`upsert_companies()`)
- [ ] Implement referral → domain scan trigger (`scan_domain()`)
- [ ] Handle duplicate referrals (skip if already exists)
- [ ] Add logging (structured logging)

**Acceptance Criteria**:
- Referrals normalized correctly
- Companies upserted correctly
- Domain scans triggered automatically
- Duplicates handled gracefully

---

### Task 2.4: API Endpoints

**Files**: `app/api/referrals.py` (NEW), `app/main.py`

- [ ] Create referrals router
- [ ] `GET /referrals` - List referrals with filters (status, domain, date range)
- [ ] `POST /referrals/sync` - Manual sync from Partner Center
- [ ] `GET /referrals/{referral_id}` - Get single referral details
- [ ] Add response models (Pydantic)
- [ ] Add error handling (404, 400, 500)
- [ ] Register router in `app/main.py`

**Acceptance Criteria**:
- All endpoints work correctly
- Response models validated
- Error handling complete
- Endpoints registered in main app

---

### Task 2.5: UI Integration

**Files**: `mini-ui/js/ui-leads.js`, `mini-ui/index.html`, `mini-ui/styles.css`

- [ ] Add referrals section to Mini UI (new tab or section)
- [ ] Add referral status badges (Active, In Progress, Won)
- [ ] Add referral filter to leads table (filter by referral status)
- [ ] Add referral sync button (manual sync trigger)
- [ ] Add referral sync status indicator (last sync time)
- [ ] Style referral badges and UI elements

**Acceptance Criteria**:
- Referrals visible in UI
- Status badges work correctly
- Filter works
- Sync button triggers sync
- Status indicator shows last sync time

---

### Task 2.6: Background Sync

**Files**: `app/core/celery_app.py`, `app/core/tasks.py`

- [ ] Create Celery task `sync_partner_center_referrals()`
- [ ] Configure sync schedule (daily/hourly via Celery Beat)
- [ ] Handle sync errors gracefully (log, don't crash)
- [ ] Add sync progress tracking (Redis-based)
- [ ] Add sync result logging (success/failure counts)

**Acceptance Criteria**:
- Sync task runs on schedule
- Errors handled gracefully
- Progress tracked
- Results logged

---

## ⚡ Phase 3: Dynamics 365 Integration (P2)

**Branch**: `feature/dynamics365-integration`  
**Duration**: 6-10 days  
**Priority**: P2

### Task 3.1: Dynamics 365 API Client

**Files**: `app/core/dynamics365.py` (NEW)

- [ ] Create Dynamics 365 API client class
- [ ] Implement OAuth 2.0 authentication (Azure AD)
- [ ] Implement token refresh mechanism (automatic renewal)
- [ ] Implement rate limiting handling (respect Dynamics limits)
- [ ] Implement batch request API (efficient bulk operations)
- [ ] Add error handling (network, API, authentication errors)
- [ ] Add logging (structured logging)

**Acceptance Criteria**:
- Can authenticate with Dynamics 365
- Token refresh works automatically
- Rate limiting respected
- Batch requests work
- Errors handled gracefully

---

### Task 3.2: Data Mapping

**Files**: `app/core/dynamics_mapping.py` (NEW)

- [ ] Create data mapping module
- [ ] Map Hunter lead → Dynamics Lead (field mapping)
- [ ] Map Hunter score → Dynamics Opportunity Stage (score thresholds)
- [ ] Map Hunter segment → Dynamics Lead Source (segment mapping)
- [ ] Map IP enrichment → Dynamics Custom Fields (infrastructure data)
- [ ] Handle missing fields gracefully (default values)
- [ ] Add mapping validation (required fields check)

**Acceptance Criteria**:
- All Hunter fields mapped to Dynamics
- Score → Stage mapping accurate
- Segment → Source mapping correct
- IP enrichment data included
- Validation works

---

### Task 3.3: Pipeline Integration

**Files**: `app/core/dynamics_pipeline.py` (NEW)

- [ ] Create pipeline integration module
- [ ] Implement Lead → Contact → Account → Opportunity flow
- [ ] Implement duplicate detection (check existing records)
- [ ] Implement account merge logic (merge if exists)
- [ ] Implement opportunity creation (from Hunter lead)
- [ ] Handle pipeline errors (rollback on failure)
- [ ] Add transaction logging (audit trail)

**Acceptance Criteria**:
- Pipeline flow works end-to-end
- Duplicates detected and handled
- Account merge works correctly
- Opportunities created successfully
- Errors handled with rollback

---

### Task 3.4: Sync Mechanisms

**Files**: `app/core/dynamics_sync.py` (NEW), `app/db/models.py`

- [ ] Create sync module
- [ ] Implement Hunter → Dynamics sync (push leads to Dynamics)
- [ ] Implement Dynamics → Hunter sync (pull updates from Dynamics) - optional
- [ ] Implement conflict resolution (last-write-wins or manual)
- [ ] Implement audit logging (sync history table)
- [ ] Add sync status tracking (synced, failed, pending)
- [ ] Create sync tracking models (DynamicsSyncLog)

**Acceptance Criteria**:
- Push sync works
- Pull sync works (if implemented)
- Conflicts resolved correctly
- Audit log complete
- Status tracking accurate

---

### Task 3.5: API Endpoints

**Files**: `app/api/dynamics.py` (NEW), `app/main.py`

- [ ] Create Dynamics router
- [ ] `POST /dynamics/sync/{domain}` - Manual sync to Dynamics
- [ ] `GET /dynamics/status/{domain}` - Check sync status
- [ ] `POST /dynamics/bulk-sync` - Bulk sync to Dynamics
- [ ] Add response models (Pydantic)
- [ ] Add error handling (404, 400, 500)
- [ ] Register router in `app/main.py`

**Acceptance Criteria**:
- All endpoints work correctly
- Response models validated
- Error handling complete
- Endpoints registered in main app

---

### Task 3.6: UI Integration

**Files**: `mini-ui/js/ui-leads.js`, `mini-ui/index.html`, `mini-ui/styles.css`

- [ ] Add Dynamics sync button to Mini UI (per lead)
- [ ] Add Dynamics status indicator (synced, failed, pending)
- [ ] Add Dynamics sync history (last sync time, status)
- [ ] Add Dynamics error handling UI (show errors to user)
- [ ] Add bulk sync button (sync all leads)
- [ ] Style Dynamics UI elements

**Acceptance Criteria**:
- Sync button works
- Status indicator accurate
- Sync history visible
- Errors shown to user
- Bulk sync works

---

### Task 3.7: Background Sync

**Files**: `app/core/celery_app.py`, `app/core/tasks.py`

- [ ] Create Celery task `sync_to_dynamics365()`
- [ ] Configure sync schedule (daily/hourly via Celery Beat)
- [ ] Handle sync errors and retries (exponential backoff)
- [ ] Implement exponential backoff (retry with increasing delay)
- [ ] Add sync progress tracking (Redis-based)
- [ ] Add sync result logging (success/failure counts)

**Acceptance Criteria**:
- Sync task runs on schedule
- Errors retried with backoff
- Progress tracked
- Results logged

---

## 📝 Branch Strategy

### Phase 1 Branch
```bash
git checkout -b feature/ui-stabilization-v1.1
# Work on UI fixes
git commit -m "feat: UI stabilization - button fixes, modal improvements"
git push origin feature/ui-stabilization-v1.1
# Create PR → merge to main
```

### Phase 2 Branch
```bash
git checkout -b feature/partner-center-referrals
# Work on Partner Center integration
git commit -m "feat: Partner Center referrals integration"
git push origin feature/partner-center-referrals
# Create PR → merge to main
```

### Phase 3 Branch
```bash
git checkout -b feature/dynamics365-integration
# Work on Dynamics 365 integration
git commit -m "feat: Dynamics 365 integration - pipeline and sync"
git push origin feature/dynamics365-integration
# Create PR → merge to main
```

---

## ✅ Success Criteria Summary

### Phase 1 (UI)
- [ ] Zero UI bugs
- [ ] Sales team feedback: Positive
- [ ] UI 100% functional

### Phase 2 (Partner Center)
- [ ] Referrals syncing successfully
- [ ] Sync success rate > 95%
- [ ] Referrals visible in UI

### Phase 3 (Dynamics)
- [ ] Dynamics sync success rate > 90%
- [ ] Pipeline accuracy > 95%
- [ ] Error recovery automatic

---

## 🔗 Related Documents

- `docs/plans/2025-01-28-INTEGRATION-ROADMAP-v1.0.md` - Detailed roadmap
- `docs/active/KALAN-ISLER-PRIORITY.md` - Priority list
- `docs/active/NO-BREAK-REFACTOR-PLAN.md` - G21 Architecture Refactor (overlaps with Phase 3)

