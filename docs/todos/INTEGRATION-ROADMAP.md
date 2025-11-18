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

### Phase 2: Partner Center Referrals Integration (P1) 🅿️ **PARK EDİLDİ**

**Status**: 🅿️ **PARK EDİLDİ** (MVP-safe mode, 50% completed)  
**Duration**: 2-3 days (core components completed, remaining tasks post-MVP)  
**Risk**: 2/10  
**Priority**: P1  
**Branch**: `feature/partner-center-phase1` (opened 2025-01-29, active)

**MVP Yaklaşımı**: Minimal API client (50-70 satır), polling (10 min prod, 30s dev), sadece sync endpoint, lead listesine 1 kolon.

**Progress**: 50% (3/6 tasks completed)
- ✅ Task 2.1: Partner Center API Client - COMPLETED (2025-01-28)
- ✅ Task 2.2: Referral Data Model - COMPLETED (2025-01-28)
- ✅ Task 2.3: Referral Ingestion - COMPLETED (2025-01-28) - Scoring pipeline integration PENDING
- ⏳ Task 2.4: API Endpoints - PENDING (post-MVP)
- ⏳ Task 2.5: UI Integration - PENDING (post-MVP)
- ⏳ Task 2.6: Background Sync - PENDING (post-MVP)

**Status Note**: 🅿️ **MVP'ye etkisi YOK** - Feature flag default OFF, kod hazır ama aktif değil. Post-MVP sprint'inde tamamlanacak.

#### Tasks

- [x] **Task 2.1**: Partner Center API Client (MVP: Minimal) ✅ **COMPLETED** (2025-01-28)
  - [x] Create `app/core/partner_center.py` - Partner Center API client (50-70 satır, minimal)
  - [x] Implement minimal OAuth 2.0 authentication (MSAL + Device Code Flow)
  - [x] Implement `get_referrals()` function
  - [x] Basic rate limiting: `time.sleep(1)` between requests
  - [x] Basic retry: 2 deneme (transient failures için)
  - [x] Token expiry kontrolü (MSAL silent token acquisition)
  - [x] Error handling (network errors, API errors, token refresh errors)
  - [x] Structured logging (PII masking ile)

- [x] **Task 2.2**: Referral Data Model (raw_leads + partner_center_referrals hybrid) ✅ **COMPLETED** (2025-01-28)
  - [x] `raw_leads` table'ını kullan (source='partnercenter', payload JSONB)
  - [x] Create `app/db/models.py` - `PartnerCenterReferral` model
  - [x] Create Alembic migration for `partner_center_referrals` table
  - [x] Fields: referral_id (unique), referral_type, company_name, domain, azure_tenant_id, status, raw_data, synced_at, created_at, updated_at
  - [x] Indexes: referral_id, domain, status, synced_at, referral_type, azure_tenant_id

- [x] **Task 2.3**: Referral Ingestion ✅ **COMPLETED** (2025-01-28) - Scoring pipeline integration PENDING
  - [x] Create `app/core/referral_ingestion.py` - Referral ingestion logic
  - [x] Lead tipi detection (Co-sell, Marketplace, Solution Provider)
  - [x] Domain extraction fallback (website → email → skip)
  - [x] Azure Tenant ID → Company provider override (M365 signal)
  - [x] Implement referral → domain normalization
  - [x] Implement referral → company upsert
  - [x] Implement referral → domain scan trigger (idempotent - domain bazlı)
  - [ ] Scoring pipeline entegrasyonu (Azure Tenant ID override + Co-sell boost) - ⏳ **PENDING**
  - [x] Handle duplicate referrals

- [ ] **Task 2.4**: API Endpoints (MVP: Sadece Sync)
  - [ ] Create `app/api/referrals.py` - Referral endpoints
  - [ ] **MVP**: `POST /api/referrals/sync` - Manual sync from Partner Center
  - [ ] ⏳ **Future Enhancement**: `GET /api/referrals` - List referrals with filters (post-MVP)
  - [ ] ⏳ **Future Enhancement**: `GET /api/referrals/{referral_id}` - Get single referral (post-MVP)

- [ ] **Task 2.5**: UI Integration (MVP: Sadece Lead Listesine Kolon)
  - [ ] Leads API'ye referral bilgisi ekle (`referral_type` field)
  - [ ] Lead listesine "Referral" kolonu ekle (Co-sell / Marketplace / SP)
  - [ ] ⏳ **Future Enhancement**: Referrals section to Mini UI (post-MVP)
  - [ ] ⏳ **Future Enhancement**: Referral status badges (post-MVP)
  - [ ] ⏳ **Future Enhancement**: Referral filter to leads table (post-MVP)
  - [ ] Sync button (opsiyonel, admin için)

- [ ] **Task 2.6**: Background Sync (MVP: Polling, Dev Override)
  - [ ] Create Celery task for periodic referral sync
  - [ ] Configure sync schedule: **Production 10 minutes, Development 30-60 seconds** (test edilebilir)
  - [ ] Handle sync errors gracefully

**Files to Create**:
- `app/core/partner_center.py` (MVP: 50-70 satır, minimal)
- `app/core/referral_ingestion.py`
- `app/api/referrals.py` (MVP: sadece sync endpoint)
- `alembic/versions/XXXX_add_partner_center_referrals.py`

**Files to Modify**:
- `app/db/models.py` (PartnerCenterReferral model + hybrid raw_leads)
- `app/core/scorer.py` (Azure Tenant ID override + Co-sell boost)
- `app/api/leads.py` (referral_type field ekle)
- `mini-ui/js/ui-leads.js` (sadece referral kolonu)
- `app/core/celery_app.py` (add sync task, dev override)

**Success Criteria**:
- [ ] Partner Center referrals sync working (polling, 10 min prod, 30s dev)
- [ ] Referrals visible in UI (lead listesinde referral kolonu)
- [ ] Referrals trigger domain scans (idempotent, domain bazlı)
- [ ] Background sync working
- [ ] Error handling complete
- [ ] Scoring pipeline entegrasyonu çalışıyor (Azure Tenant ID + Co-sell boost)

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

**Current Phase**: Phase 2 (Partner Center Referrals) 🅿️ **PARK EDİLDİ**

**Completed**: 1/3 phases (Phase 1 ✅ Completed 2025-01-28)

**Phase 1 Status**: ✅ **COMPLETED** (2025-01-28)
- All tasks done (Task 1.1-1.5 ✅)
- UI stabilization complete
- Sales team feedback: Positive

**Phase 2 Status**: 🅿️ **PARK EDİLDİ** (MVP-safe mode, 50% completed)
- Core components completed (Tasks 2.1, 2.2, 2.3 ✅)
- Remaining tasks: API endpoints, UI integration, Background sync, Scoring pipeline
- **Status**: MVP'ye etkisi YOK (feature flag default OFF, kod hazır ama aktif değil)
- **Next Sprint**: Post-MVP (G21-G22)

**Next Steps**:
1. ✅ Phase 1 completed - All tasks done (Task 1.1-1.5 ✅)
2. 🅿️ Phase 2: Partner Center Referrals - **PARK EDİLDİ** (post-MVP sprint'inde tamamlanacak)
3. ⏳ Phase 3: Dynamics 365 Integration - Pending (after Phase 2 completion)

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

