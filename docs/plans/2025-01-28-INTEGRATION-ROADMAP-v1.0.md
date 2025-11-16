# Integration Roadmap v1.0

**Date**: 2025-01-28  
**Status**: 🔄 **In Progress** (Phase 1: ✅ Completed, Phase 2: Next)  
**Priority**: P0.5 → P1 → P2  
**Estimated Duration**: 9-14 days total  
**Risk Level**: Low → Medium (with proper execution)

---

## Executive Summary

This roadmap implements the correct engineering sequence for Hunter integration with external systems:

> **Hunter CRM değil, CRM'e güç veren motor. Motora önce UI'yi sabitle, sonra dış veri kaynağını ekle, en son CRM'e bağla.**

**Key Principle**: UI stability → Data ingestion → CRM integration (one-way dependency chain)

**Total Risk**: Low-Medium (with proper execution)

---

## 🎯 Correct Sequence (Non-negotiable)

### **1️⃣ Mini UI Stabilization (P0.5) - FIRST**

**Why First?**
- Partner Center → Hunter → CRM flow: **UI is the most touched point**
- Bug fixes + polish + hardware must be done here first
- If not done: Sales team will say "what is this?" when new data enters Hunter
- UI works now, but **P1 polishing required before integration**

**Duration**: 1 day  
**Impact**: Very High  
**Risk**: 0 → Pure cosmetic + stability

> 🔥 *MUST STABILIZE UI BEFORE ENTERING DYNAMICS AND PARTNER CENTER.*

**Tasks**:
- Button fixes, modal bugs
- Score breakdown improvements
- Loading states optimization
- Filter bar UX fixes
- General UX polish

---

### **2️⃣ Partner Center Referrals Integration (P1) - SECOND**

**Why Before Dynamics?**
- Partner Center referral is **one-way** (PC → Hunter)
- Dynamics is **two-way** (Hunter ↔ CRM)
- Partner Center is simpler: "pull sync"
- Dynamics is complex: "pipeline & workflow integration"

**Engineering Principle**:
> **You bring water to your house first, then install the faucet.**

**Partner Center Flow** (Simple):
- Single endpoint → `GET referrals`
- Status → Active / In Progress / Won
- Companies + domains come in (nice)
- Hunter ingest → normalize → scan → score
- Show in UI, filter

**Duration**: 2-3 days  
**Risk**: Low  
**Impact**: Medium-High

**Benefits**:
- Hunter's data shown to sales team becomes richer
- Enter Dynamics integration with richer dataset

---

### **3️⃣ Dynamics 365 Integration (P2) - LAST**

**Why Last?**
- CRM side is *pipeline* work (Lead → Contact → Account → Opportunity)
- Data mapping, field normalization, pipeline rules, score → stage transformation...
- Doing this without UI and referral stability **creates technical debt**
- D365 requires **enterprise-grade** operations:
  - Token refresh
  - Rate limit handling
  - Batch request API
  - Lead duplicate detection
  - Account merge flow
  - Audit log
  - Retry mechanisms

**If done before UI + Partner Center**:
- Constant "how do we show this in UI?" questions
- "Should referrals come in or not?" confusion
- Pipeline mapping becomes messy

**Duration**: 6-10 days  
**Risk**: Medium-High  
**Impact**: Very High

---

## 📋 Phase Details

### Phase 1: Mini UI Stabilization (P0.5)

**Status**: ✅ **COMPLETED**  
**Duration**: 1 day  
**Risk**: 0/10  
**Priority**: P0.5 (Critical - blocks everything)

#### Tasks

**1.1 Button & Modal Fixes**
- [x] Fix button hover states
- [x] Fix modal backdrop click behavior
- [x] Fix modal ESC key handling
- [x] Fix modal scroll optimization

**1.2 Score Breakdown Improvements**
- [x] Fix score breakdown modal bugs
- [x] Improve tooltip positioning
- [x] Fix signal/risk display order
- [x] Add loading states for score breakdown

**1.3 Loading States**
- [x] Add loading spinner for table
- [x] Add loading states for filters
- [x] Add loading states for export buttons
- [x] Optimize loading transitions

**1.4 Filter Bar UX**
- [x] Fix filter bar layout
- [x] Improve filter dropdown UX
- [x] Add filter clear button
- [x] Add filter state persistence

**1.5 General UX Polish**
- [x] Fix table row hover effects
- [x] Improve pagination UX
- [x] Fix empty state messages
- [x] Add toast notification improvements

**Files to Modify**:
- `mini-ui/js/ui-leads.js`
- `mini-ui/styles.css`
- `mini-ui/index.html`

**Success Criteria**:
- [x] All modal bugs fixed
- [x] All loading states working
- [x] Filter bar fully functional
- [x] UX polish complete
- [x] Sales team can use UI without confusion

---

### Phase 2: Partner Center Referrals Integration (P1)

**Status**: 🔄 **NEXT** (Phase 1 completed)  
**Duration**: 2-3 days  
**Risk**: 2/10  
**Priority**: P1

#### Tasks

**2.1 Partner Center API Client**
- [ ] Create `app/core/partner_center.py` - Partner Center API client
- [ ] Implement authentication (OAuth 2.0 or API key)
- [ ] Implement `get_referrals()` function
- [ ] Handle rate limiting
- [ ] Handle token refresh

**2.2 Referral Data Model**
- [ ] Create `app/db/models.py` - `PartnerCenterReferral` model
- [ ] Create Alembic migration for `partner_center_referrals` table
- [ ] Fields: referral_id, company_name, domain, status, created_at, updated_at

**2.3 Referral Ingestion**
- [ ] Create `app/core/referral_ingestion.py` - Referral ingestion logic
- [ ] Implement referral → domain normalization
- [ ] Implement referral → company upsert
- [ ] Implement referral → domain scan trigger
- [ ] Handle duplicate referrals

**2.4 API Endpoints**
- [ ] Create `app/api/referrals.py` - Referral endpoints
- [ ] `GET /referrals` - List referrals with filters
- [ ] `POST /referrals/sync` - Manual sync from Partner Center
- [ ] `GET /referrals/{referral_id}` - Get single referral

**2.5 UI Integration**
- [ ] Add referrals section to Mini UI
- [ ] Add referral status badges
- [ ] Add referral filter to leads table
- [ ] Add referral sync button

**2.6 Background Sync**
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

### Phase 3: Dynamics 365 Integration (P2)

**Status**: ⏳ **Pending** (after Phase 2)  
**Duration**: 6-10 days  
**Risk**: 4/10  
**Priority**: P2

#### Tasks

**3.1 Dynamics 365 API Client**
- [ ] Create `app/core/dynamics365.py` - Dynamics 365 API client
- [ ] Implement OAuth 2.0 authentication
- [ ] Implement token refresh mechanism
- [ ] Implement rate limiting handling
- [ ] Implement batch request API

**3.2 Data Mapping**
- [ ] Create `app/core/dynamics_mapping.py` - Data mapping logic
- [ ] Map Hunter lead → Dynamics Lead
- [ ] Map Hunter score → Dynamics Opportunity Stage
- [ ] Map Hunter segment → Dynamics Lead Source
- [ ] Map IP enrichment → Dynamics Custom Fields

**3.3 Pipeline Integration**
- [ ] Create `app/core/dynamics_pipeline.py` - Pipeline logic
- [ ] Implement Lead → Contact → Account → Opportunity flow
- [ ] Implement duplicate detection
- [ ] Implement account merge logic
- [ ] Implement opportunity creation

**3.4 Sync Mechanisms**
- [ ] Create `app/core/dynamics_sync.py` - Sync logic
- [ ] Implement Hunter → Dynamics sync (push)
- [ ] Implement Dynamics → Hunter sync (pull) - optional
- [ ] Implement conflict resolution
- [ ] Implement audit logging

**3.5 API Endpoints**
- [ ] Create `app/api/dynamics.py` - Dynamics endpoints
- [ ] `POST /dynamics/sync/{domain}` - Manual sync to Dynamics
- [ ] `GET /dynamics/status/{domain}` - Check sync status
- [ ] `POST /dynamics/bulk-sync` - Bulk sync to Dynamics

**3.6 UI Integration**
- [ ] Add Dynamics sync button to Mini UI
- [ ] Add Dynamics status indicator
- [ ] Add Dynamics sync history
- [ ] Add Dynamics error handling UI

**3.7 Background Sync**
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

## Risk Matrix

| Phase | Risk | Description | Rollback |
|-------|------|-------------|----------|
| Phase 1 | 0/10 | UI polish only | Not needed |
| Phase 2 | 2/10 | External API dependency | Disable sync |
| Phase 3 | 4/10 | Complex pipeline integration | Disable sync, revert mapping |

---

## Dependencies

```
Phase 1 (UI) → Phase 2 (Partner Center) → Phase 3 (Dynamics)
     ↓                    ↓                        ↓
  No deps          Requires UI stable      Requires UI + PC stable
```

---

## Success Metrics

### Phase 1 Success
- [ ] UI bug count: 0
- [ ] Sales team feedback: Positive
- [ ] UI usability: 100% functional

### Phase 2 Success
- [ ] Referrals synced: > 0
- [ ] Sync success rate: > 95%
- [ ] UI shows referrals: Yes

### Phase 3 Success
- [ ] Dynamics sync success rate: > 90%
- [ ] Pipeline accuracy: > 95%
- [ ] Error recovery: Automatic

---

## Related Documents

- `docs/active/KALAN-ISLER-PRIORITY.md` - Priority list
- `docs/active/NO-BREAK-REFACTOR-PLAN.md` - G21 Architecture Refactor (Phase 4 overlaps with Phase 3)
- `docs/todos/G21-architecture-refactor.md` - G21 TODO

---

## Notes

- **Phase 1 is CRITICAL**: Must complete before Phase 2/3
- **Phase 2 simplifies Phase 3**: Richer dataset helps Dynamics mapping
- **Phase 3 is complex**: Requires careful planning and testing
- **G21 Phase 4 overlaps**: Dynamics Migration (G21) can be merged with Phase 3 (this plan)

