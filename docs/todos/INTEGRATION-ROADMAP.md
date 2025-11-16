# Integration Roadmap - TODO

**Date Created**: 2025-01-28  
**Status**: In Progress  
**Priority**: P0.5 → P1 → P2  
**Estimated Duration**: 9-14 days total  
**Risk Level**: Low → Medium (with proper execution)

---

## 🎯 Goal

Implement correct engineering sequence for Hunter integration with external systems:

> **Hunter CRM değil, CRM'e güç veren motor. Motora önce UI'yi sabitle, sonra dış veri kaynağını ekle, en son CRM'e bağla.**

**Key Principle**: UI stability → Data ingestion → CRM integration (one-way dependency chain)

---

## 📋 Phases

### Phase 1: Mini UI Stabilization (P0.5) ✅ **COMPLETED**

**Status**: ✅ **COMPLETED**  
**Duration**: 1 day  
**Risk**: 0/10  
**Priority**: P0.5 (Critical - blocks everything)  
**Branch**: `feature/ui-stabilization-v1.1`

#### Tasks

- [x] **Task 1.1**: Button & Modal Fixes
  - [x] Fix button hover states
  - [x] Fix modal backdrop click behavior
  - [x] Fix modal ESC key handling
  - [x] Fix modal scroll optimization

- [x] **Task 1.2**: Score Breakdown Improvements
  - [x] Fix score breakdown modal bugs
  - [x] Improve tooltip positioning
  - [x] Fix signal/risk display order
  - [x] Add loading states for score breakdown

- [x] **Task 1.3**: Loading States
  - [x] Add loading spinner for table
  - [x] Add loading states for filters
  - [x] Add loading states for export buttons
  - [x] Optimize loading transitions

- [x] **Task 1.4**: Filter Bar UX
  - [x] Fix filter bar layout
  - [x] Improve filter dropdown UX
  - [x] Add filter clear button
  - [x] Add filter state persistence

- [x] **Task 1.5**: General UX Polish
  - [x] Fix table row hover effects
  - [x] Improve pagination UX
  - [x] Fix empty state messages
  - [x] Add toast notification improvements

**Files to Modify**:
- `mini-ui/js/ui-leads.js`
- `mini-ui/styles.css`
- `mini-ui/index.html`

**Success Criteria**:
- [ ] All modal bugs fixed
- [ ] All loading states working
- [ ] Filter bar fully functional
- [ ] UX polish complete
- [ ] Sales team can use UI without confusion

---

### Phase 2: Partner Center Referrals Integration (P1) ⏳ **PENDING**

**Status**: ⏳ **Pending** (after Phase 1)  
**Duration**: 2-3 days  
**Risk**: 2/10  
**Priority**: P1  
**Branch**: `feature/partner-center-referrals`

#### Tasks

- [ ] **Task 2.1**: Partner Center API Client
  - [ ] Create `app/core/partner_center.py` - Partner Center API client
  - [ ] Implement authentication (OAuth 2.0 or API key)
  - [ ] Implement `get_referrals()` function
  - [ ] Handle rate limiting
  - [ ] Handle token refresh

- [ ] **Task 2.2**: Referral Data Model
  - [ ] Create `app/db/models.py` - `PartnerCenterReferral` model
  - [ ] Create Alembic migration for `partner_center_referrals` table
  - [ ] Fields: referral_id, company_name, domain, status, created_at, updated_at

- [ ] **Task 2.3**: Referral Ingestion
  - [ ] Create `app/core/referral_ingestion.py` - Referral ingestion logic
  - [ ] Implement referral → domain normalization
  - [ ] Implement referral → company upsert
  - [ ] Implement referral → domain scan trigger
  - [ ] Handle duplicate referrals

- [ ] **Task 2.4**: API Endpoints
  - [ ] Create `app/api/referrals.py` - Referral endpoints
  - [ ] `GET /referrals` - List referrals with filters
  - [ ] `POST /referrals/sync` - Manual sync from Partner Center
  - [ ] `GET /referrals/{referral_id}` - Get single referral

- [ ] **Task 2.5**: UI Integration
  - [ ] Add referrals section to Mini UI
  - [ ] Add referral status badges
  - [ ] Add referral filter to leads table
  - [ ] Add referral sync button

- [ ] **Task 2.6**: Background Sync
  - [ ] Create Celery task for periodic referral sync
  - [ ] Configure sync schedule (daily/hourly)
  - [ ] Handle sync errors gracefully

**Files to Create**:
- `app/core/partner_center.py`
- `app/core/referral_ingestion.py`
- `app/api/referrals.py`
- `alembic/versions/XXXX_add_partner_center_referrals.py`

**Files to Modify**:
- `app/db/models.py`
- `mini-ui/js/ui-leads.js`
- `mini-ui/index.html`
- `app/core/celery_app.py` (add sync task)

**Success Criteria**:
- [ ] Partner Center referrals sync working
- [ ] Referrals visible in UI
- [ ] Referrals trigger domain scans
- [ ] Background sync working
- [ ] Error handling complete

---

### Phase 3: Dynamics 365 Integration (P2) ⏳ **PENDING**

**Status**: ⏳ **Pending** (after Phase 2)  
**Duration**: 6-10 days  
**Risk**: 4/10  
**Priority**: P2  
**Branch**: `feature/dynamics365-integration`

#### Tasks

- [ ] **Task 3.1**: Dynamics 365 API Client
  - [ ] Create `app/core/dynamics365.py` - Dynamics 365 API client
  - [ ] Implement OAuth 2.0 authentication
  - [ ] Implement token refresh mechanism
  - [ ] Implement rate limiting handling
  - [ ] Implement batch request API

- [ ] **Task 3.2**: Data Mapping
  - [ ] Create `app/core/dynamics_mapping.py` - Data mapping logic
  - [ ] Map Hunter lead → Dynamics Lead
  - [ ] Map Hunter score → Dynamics Opportunity Stage
  - [ ] Map Hunter segment → Dynamics Lead Source
  - [ ] Map IP enrichment → Dynamics Custom Fields

- [ ] **Task 3.3**: Pipeline Integration
  - [ ] Create `app/core/dynamics_pipeline.py` - Pipeline logic
  - [ ] Implement Lead → Contact → Account → Opportunity flow
  - [ ] Implement duplicate detection
  - [ ] Implement account merge logic
  - [ ] Implement opportunity creation

- [ ] **Task 3.4**: Sync Mechanisms
  - [ ] Create `app/core/dynamics_sync.py` - Sync logic
  - [ ] Implement Hunter → Dynamics sync (push)
  - [ ] Implement Dynamics → Hunter sync (pull) - optional
  - [ ] Implement conflict resolution
  - [ ] Implement audit logging

- [ ] **Task 3.5**: API Endpoints
  - [ ] Create `app/api/dynamics.py` - Dynamics endpoints
  - [ ] `POST /dynamics/sync/{domain}` - Manual sync to Dynamics
  - [ ] `GET /dynamics/status/{domain}` - Check sync status
  - [ ] `POST /dynamics/bulk-sync` - Bulk sync to Dynamics

- [ ] **Task 3.6**: UI Integration
  - [ ] Add Dynamics sync button to Mini UI
  - [ ] Add Dynamics status indicator
  - [ ] Add Dynamics sync history
  - [ ] Add Dynamics error handling UI

- [ ] **Task 3.7**: Background Sync
  - [ ] Create Celery task for periodic Dynamics sync
  - [ ] Configure sync schedule
  - [ ] Handle sync errors and retries
  - [ ] Implement exponential backoff

**Files to Create**:
- `app/core/dynamics365.py`
- `app/core/dynamics_mapping.py`
- `app/core/dynamics_pipeline.py`
- `app/core/dynamics_sync.py`
- `app/api/dynamics.py`
- `app/db/models.py` - Dynamics sync tracking models
- `alembic/versions/XXXX_add_dynamics_sync_tables.py`

**Files to Modify**:
- `mini-ui/js/ui-leads.js`
- `mini-ui/index.html`
- `app/core/celery_app.py`

**Success Criteria**:
- [ ] Dynamics authentication working
- [ ] Data mapping complete
- [ ] Pipeline integration working
- [ ] Sync mechanisms working
- [ ] UI integration complete
- [ ] Error handling robust
- [ ] Audit logging complete

---

## 📊 Progress Tracking

**Current Phase**: Phase 1 (Mini UI Stabilization) ✅ **COMPLETED**

**Completed**: 1/3 phases

**Next Steps**:
1. ✅ Phase 1 completed - All tasks done (Task 1.1-1.5 ✅)
2. Start Phase 2: Partner Center Referrals Integration (P1)
3. Follow task list: `docs/plans/2025-01-28-INTEGRATION-TASKS.md`

---

## 🔗 Related Documents

- `docs/plans/2025-01-28-INTEGRATION-ROADMAP-v1.0.md` - Detailed roadmap
- `docs/plans/2025-01-28-INTEGRATION-TASKS.md` - Exact task list with acceptance criteria
- `docs/active/KALAN-ISLER-PRIORITY.md` - Priority list

---

## ✅ Success Criteria Summary

### Phase 1 (UI)
- [x] Zero UI bugs
- [x] Sales team feedback: Positive
- [x] UI 100% functional

### Phase 2 (Partner Center)
- [ ] Referrals syncing successfully
- [ ] Sync success rate > 95%
- [ ] Referrals visible in UI

### Phase 3 (Dynamics)
- [ ] Dynamics sync success rate > 90%
- [ ] Pipeline accuracy > 95%
- [ ] Error recovery automatic

