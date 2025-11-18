# Partner Center Integration - Preparation Guide

**Date Created**: 2025-01-30  
**Last Updated**: 2025-01-30  
**Status**: ✅ **Phase 2 Complete**  
**Phase**: Integration Roadmap - Phase 2  
**Priority**: P1  
**Branch**: `feature/partner-center-phase1` (opened 2025-01-29)

---

## 🎯 Overview

This document provided comprehensive preparation steps for Partner Center Phase 2 integration. **All tasks are now completed** (100% progress). This document is kept for reference.

**Current Status**:
- ✅ Task 2.1: Partner Center API Client - COMPLETED (2025-01-28)
- ✅ Task 2.2: Referral Data Model - COMPLETED (2025-01-28)
- ✅ Task 2.3: Referral Ingestion - COMPLETED (2025-01-28)
- ✅ Task 2.4: API Endpoints - COMPLETED (2025-01-30) - 7/7 tests passing
- ✅ Task 2.5: UI Integration - COMPLETED (2025-01-30) - Referral column with badges
- ✅ Task 2.6: Background Sync - COMPLETED (2025-01-30) - Celery Beat schedule, 10/10 tests passing

---

## 📋 Pre-Flight Checklist

### Environment Setup

- [ ] **Azure AD App Registration**
  - [ ] Partner Center API permissions configured
  - [ ] Delegated permissions granted (application permissions not available)
  - [ ] Client ID and Tenant ID obtained
  - [ ] Device Code Flow tested (initial authentication)

- [ ] **Environment Variables**
  - [ ] `HUNTER_PARTNER_CENTER_ENABLED=false` (default, enable when ready)
  - [ ] `HUNTER_PARTNER_CENTER_CLIENT_ID` configured
  - [ ] `HUNTER_PARTNER_CENTER_TENANT_ID` configured
  - [ ] `HUNTER_PARTNER_CENTER_API_URL` configured
  - [ ] `HUNTER_PARTNER_CENTER_SCOPE` configured (default: `https://api.partner.microsoft.com/.default`)
  - [ ] `HUNTER_PARTNER_CENTER_TOKEN_CACHE_PATH` configured (optional, defaults to `.token_cache`)

- [ ] **Database Migration**
  - [ ] Alembic migration ready: `alembic/versions/622ba66483b9_add_partner_center_referrals.py`
  - [ ] Migration tested (upgrade/downgrade)
  - [ ] `partner_center_referrals` table created
  - [ ] Indexes verified

- [ ] **Dependencies**
  - [ ] `msal` package installed (`pip install msal`)
  - [ ] `httpx` package installed (already in requirements)
  - [ ] Token cache directory writable (`.token_cache` or custom path)

---

## 🔧 Implementation Preparation

### Task 2.4: API Endpoints - Preparation

**Files to Create**:
- `app/api/referrals.py` (NEW)

**Files to Modify**:
- `app/main.py` (router registration)

**Preparation Steps**:

1. **Review Existing API Patterns**
   - [ ] Study `app/api/leads.py` for response model patterns
   - [ ] Study `app/api/bulk_scan.py` for async task patterns
   - [ ] Study `app/api/webhook.py` for feature flag patterns

2. **Pydantic Models**
   - [ ] Create `SyncReferralsRequest` model (optional `force: bool`)
   - [ ] Create `SyncReferralsResponse` model (`success_count`, `failure_count`, `errors: List[str]`)

3. **Celery Task Integration**
   - [ ] Review `app/core/tasks.py` for task patterns
   - [ ] Review `app/core/celery_app.py` for task registration
   - [ ] Plan async execution strategy (long-running operation)

4. **Error Handling**
   - [ ] Plan 400 Bad Request (feature disabled)
   - [ ] Plan 500 Internal Server Error (sync failure)
   - [ ] Plan graceful degradation (partial success)

**Acceptance Criteria Checklist**:
- [ ] MVP endpoint works (`POST /api/referrals/sync`)
- [ ] Response model validated
- [ ] Error handling complete
- [ ] Endpoint registered in main app
- [ ] Feature flag check implemented
- [ ] Async task execution working

---

### Task 2.5: UI Integration - Preparation

**Files to Modify**:
- `app/api/leads.py` (add `referral_type` field)
- `mini-ui/js/ui-leads.js` (add referral column)
- `mini-ui/styles.css` (badge styling)

**Preparation Steps**:

1. **API Response Model Update**
   - [ ] Review `LeadResponse` model in `app/api/leads.py`
   - [ ] Plan `referral_type: Optional[str]` field addition
   - [ ] Plan SQL query update (LEFT JOIN `partner_center_referrals`)

2. **SQL Query Pattern**
   - [ ] Review existing JOIN patterns in `app/api/leads.py`
   - [ ] Plan domain-based JOIN (domain matching)
   - [ ] Plan referral type extraction logic

3. **UI Column Integration**
   - [ ] Review `mini-ui/js/ui-leads.js` for column patterns
   - [ ] Plan referral column position (after domain/company)
   - [ ] Plan badge styling (Co-sell / Marketplace / SP)
   - [ ] Plan empty state handling ("-")

4. **Badge Styling**
   - [ ] Review existing badge patterns in `mini-ui/styles.css`
   - [ ] Plan referral type badge colors:
     - Co-sell: Blue/Primary
     - Marketplace: Green/Success
     - Solution Provider: Orange/Warning

5. **API Integration (Optional)**
   - [ ] Review `mini-ui/js/api.js` for API call patterns
   - [ ] Plan `syncReferrals()` function (POST /api/referrals/sync)
   - [ ] Plan toast notification (success/failure)

**Acceptance Criteria Checklist**:
- [ ] Leads API response includes `referral_type` field
- [ ] SQL JOIN working (domain-based matching)
- [ ] Lead list shows referral column
- [ ] Referral type displayed correctly (Co-sell / Marketplace / SP)
- [ ] Badge styling matches existing patterns
- [ ] Empty state handled ("-")
- [ ] Sync button works (optional, admin)

---

### Task 2.6: Background Sync - Preparation

**Files to Modify**:
- `app/core/celery_app.py` (beat_schedule)
- `app/core/tasks.py` (new task)

**Preparation Steps**:

1. **Celery Task Pattern**
   - [ ] Review `app/core/tasks.py` for task patterns
   - [ ] Review `app/core/celery_app.py` for beat_schedule patterns
   - [ ] Plan `sync_partner_center_referrals_task()` function

2. **Sync Schedule Configuration**
   - [ ] Production: 10 minutes (600 seconds) - configurable via `HUNTER_PARTNER_CENTER_SYNC_INTERVAL`
   - [ ] Development: 30-60 seconds (testable)
   - [ ] Plan environment-based override logic

3. **Error Handling**
   - [ ] Plan graceful error handling (log, don't crash)
   - [ ] Plan structured logging (success/failure counts)
   - [ ] Plan task expiry (1 hour if not picked up)

4. **Feature Flag Check**
   - [ ] Plan feature flag check in task (skip if disabled)
   - [ ] Plan graceful skip (log info, no error)

**Acceptance Criteria Checklist**:
- [ ] Sync task scheduled in beat_schedule
- [ ] Production interval: 10 minutes
- [ ] Development interval: 30-60 seconds (testable)
- [ ] Errors handled gracefully (log, don't crash)
- [ ] Progress tracked (success/failure counts)
- [ ] Results logged (structured logging)
- [ ] Feature flag check working (skip if disabled)

---

### Scoring Pipeline Integration - Preparation

**Status**: ⏳ **PENDING** (Task 2.3.8)

**Files to Modify**:
- `app/core/scorer.py` (Azure Tenant ID override, Co-sell boost)

**Preparation Steps**:

1. **Azure Tenant ID Override**
   - [ ] Review `determine_segment()` function in `app/core/scorer.py`
   - [ ] Plan `azure_tenant_id` parameter addition
   - [ ] Plan segment override logic:
     - If `azure_tenant_id` exists → `segment = 'Existing'`
     - `reason = 'M365 existing customer (Azure Tenant ID)'`
     - Score override: 55 (configurable via `partner_center_azure_tenant_score`)

2. **Co-sell Priority Boost**
   - [ ] Review `score_domain()` function in `app/core/scorer.py`
   - [ ] Plan `referral_type` parameter addition
   - [ ] Plan Co-sell boost logic:
     - If `referral_type == 'co-sell'` → `score += settings.partner_center_cosell_bonus` (default: 15)

3. **Config Integration**
   - [ ] Config already added (`app/config.py`):
     - `partner_center_cosell_bonus: int = 15` ✅
     - `partner_center_azure_tenant_score: int = 55` ✅

4. **Integration Points**
   - [ ] Review `app/core/referral_ingestion.py` for scoring call points
   - [ ] Plan scoring call updates (pass `azure_tenant_id`, `referral_type`)

**Acceptance Criteria Checklist**:
- [ ] Azure Tenant ID override working (Segment='Existing', Score=55)
- [ ] Co-sell boost working (+15 priority boost)
- [ ] Config values used (not hardcoded)
- [ ] Scoring pipeline integration complete
- [ ] Tests updated (scoring tests with Azure Tenant ID, Co-sell)

---

## 🧪 Testing Preparation

### Unit Tests

- [ ] **Partner Center Client Tests**
  - [ ] Test OAuth authentication (Device Code Flow)
  - [ ] Test token refresh (silent acquisition)
  - [ ] Test `get_referrals()` function
  - [ ] Test rate limiting (`time.sleep(1)`)
  - [ ] Test retry logic (2 attempts)
  - [ ] Test error handling (network errors, API errors)

- [ ] **Referral Ingestion Tests**
  - [ ] Test lead type detection (Co-sell, Marketplace, SP)
  - [ ] Test domain extraction fallback (website → email → skip)
  - [ ] Test Azure Tenant ID signal (Company.provider='M365')
  - [ ] Test raw_leads ingestion
  - [ ] Test partner_center_referrals tracking
  - [ ] Test company upsert (Azure Tenant ID override)
  - [ ] Test domain scan trigger (idempotent)

### Integration Tests

- [ ] **API Endpoint Tests**
  - [ ] Test `POST /api/referrals/sync` (feature flag disabled)
  - [ ] Test `POST /api/referrals/sync` (feature flag enabled)
  - [ ] Test response model validation
  - [ ] Test error handling (400, 500)

- [ ] **UI Integration Tests**
  - [ ] Test Leads API response (referral_type field)
  - [ ] Test SQL JOIN (domain-based matching)
  - [ ] Test referral column display
  - [ ] Test badge styling

- [ ] **Background Sync Tests**
  - [ ] Test Celery task execution
  - [ ] Test beat_schedule configuration
  - [ ] Test feature flag check (skip if disabled)
  - [ ] Test error handling (graceful degradation)

### E2E Tests

- [ ] **Full Sync Flow**
  - [ ] Test Partner Center → Hunter sync (manual)
  - [ ] Test referral ingestion → domain normalization
  - [ ] Test company upsert → domain scan
  - [ ] Test scoring pipeline (Azure Tenant ID, Co-sell)
  - [ ] Test UI display (referral column)

- [ ] **Background Sync Flow**
  - [ ] Test scheduled sync (10 minutes prod, 30s dev)
  - [ ] Test duplicate handling
  - [ ] Test error recovery

---

## 📝 Documentation Updates

### Code Documentation

- [ ] **API Endpoints**
  - [ ] Add docstrings to `app/api/referrals.py`
  - [ ] Add request/response model documentation
  - [ ] Add error handling documentation

- [ ] **UI Integration**
  - [ ] Add comments to `mini-ui/js/ui-leads.js` (referral column)
  - [ ] Add CSS comments for badge styling

- [ ] **Background Sync**
  - [ ] Add docstrings to Celery task
  - [ ] Add beat_schedule documentation

### User Documentation

- [ ] **README.md Updates**
  - [ ] Add Partner Center integration section
  - [ ] Add API endpoint documentation (`POST /api/referrals/sync`)
  - [ ] Add environment variables documentation

- [ ] **CHANGELOG.md Updates**
  - [ ] Add Task 2.4 completion (API Endpoints)
  - [ ] Add Task 2.5 completion (UI Integration)
  - [ ] Add Task 2.6 completion (Background Sync)
  - [ ] Add Scoring Pipeline Integration completion

- [ ] **docs/README.md Updates**
  - [ ] Update Integration Roadmap status
  - [ ] Mark Phase 2 as completed when done

---

## 🚀 Deployment Preparation

### Feature Flag Strategy

- [ ] **Default State**: `HUNTER_PARTNER_CENTER_ENABLED=false` (disabled by default)
- [ ] **Gradual Rollout**: Enable feature flag in staging first
- [ ] **Production Enablement**: Enable after staging validation
- [ ] **Rollback Plan**: Disable feature flag if issues occur

### Database Migration

- [ ] **Pre-Deployment**
  - [ ] Backup database
  - [ ] Test migration on staging
  - [ ] Verify `partner_center_referrals` table creation
  - [ ] Verify indexes creation

- [ ] **Deployment**
  - [ ] Run `alembic upgrade head` (migration already created)
  - [ ] Verify migration success
  - [ ] Verify table structure

- [ ] **Post-Deployment**
  - [ ] Verify table accessible
  - [ ] Verify indexes working
  - [ ] Test referral ingestion (manual sync)

### Monitoring

- [ ] **Logging**
  - [ ] Verify structured logging (PII masking)
  - [ ] Verify sync success/failure counts
  - [ ] Verify error logging

- [ ] **Metrics**
  - [ ] Plan sync frequency monitoring
  - [ ] Plan referral count tracking
  - [ ] Plan error rate tracking

---

## ✅ Success Criteria

### Functional

- [ ] Partner Center referrals sync working (polling, 10 minutes prod, 30s dev)
- [ ] Lead types detected correctly (Co-sell, Marketplace, Solution Provider)
- [ ] Azure Tenant ID signal working (Company.provider='M365' override)
- [ ] Domain extraction fallback working (website → email → skip)
- [ ] Referrals saved to raw_leads (source='partnercenter')
- [ ] Referrals saved to partner_center_referrals (lifecycle tracking)
- [ ] Referrals normalized to domain
- [ ] Companies upserted automatically (Azure Tenant ID override)
- [ ] Domain scan idempotent (same domain not rescanned)
- [ ] Scoring pipeline integration working:
  - [ ] Azure Tenant ID → Segment='Existing', Score=55
  - [ ] Co-sell → Priority boost +15
- [ ] Background sync working (polling, 10 minutes prod, 30s dev)
- [ ] Manual sync working (API endpoint)
- [ ] Lead list shows referral column (Co-sell / Marketplace / SP)

### Technical

- [ ] Feature flag working (disabled by default, production deployable)
- [ ] Error handling complete (graceful degradation)
- [ ] Structured logging (PII masking)
- [ ] Basic rate limiting working (`sleep(1)` between requests)
- [ ] Basic retry working (2 attempts)
- [ ] Token expiry control working (refresh when needed)
- [ ] Migration script working (upgrade/downgrade)
- [ ] Hybrid database model working (raw_leads + partner_center_referrals)
- [ ] Polling sync working (10 minutes prod, 30s dev - testable)
- [ ] API endpoint working (sync endpoint, MVP)
- [ ] Scoring pipeline integration working (Azure Tenant ID + Co-sell boost)

### Testing

- [ ] Unit tests passing (partner_center.py, referral_ingestion.py)
- [ ] Integration tests passing (API endpoints)
- [ ] E2E tests passing (UI integration)
- [ ] Migration tests passing (upgrade/downgrade)

---

## 🔗 Related Documents

- `docs/todos/PARTNER-CENTER-PHASE2.md` - TODO tracking (current status)
- `docs/plans/2025-01-28-INTEGRATION-ROADMAP-v1.0.md` - Integration roadmap
- `docs/active/KALAN-ISLER-PRIORITY.md` - Priority list (Phase 2: Partner Center Referrals)
- `docs/todos/INTEGRATION-ROADMAP.md` - Integration Roadmap TODO
- `docs/archive/2025-01-29-partner-center-phase2-task-list.md` - Detailed task list (archived)

---

## 📝 Notes

1. **Feature Flag**: Partner Center integration controlled by feature flag (disabled by default). **Production deployable but default OFF**. Can be enabled gradually, rollback mechanism available.

2. **Sync Strategy**: **MVP Primary = Scheduled Polling** (10 minutes prod, 30 seconds dev - testable). Webhook endpoint future enhancement (post-MVP).

3. **Database Model**: **Hybrid approach** - Ingestion via `raw_leads` (existing pattern, source='partnercenter'), tracking via `partner_center_referrals` (referral lifecycle).

4. **Azure Tenant ID Signal**: 
   - Ingestion: Company.provider='M365' override
   - Scoring: Segment='Existing', Score=55 (scoring pipeline)

5. **Lead Types**: Co-sell → priority boost (+15, scoring pipeline), Marketplace/Solution Provider → normal scoring.

6. **Domain Extraction**: Fallback chain (website → email → skip). Domain missing → referral skipped (log warning).

7. **Domain Scan Idempotent**: Same domain not rescanned (domain-based, not referral-based).

8. **Scoring Pipeline Integration**: Azure Tenant ID override and Co-sell boost in **scoring pipeline** (not ingestion).

9. **API Client**: MVP minimal (50-70 lines). OAuth + basic retry + sleep(1) rate limiting sufficient.

10. **API Endpoints**: MVP only `POST /api/referrals/sync`. List/get endpoints nice-to-have (post-MVP).

11. **UI Integration**: MVP only lead list column (Referral type: Co-sell / Marketplace / SP). New tab + modal + filter post-MVP.

12. **Error Handling**: Each referral processed independently. One referral error doesn't affect others.

---

**Last Updated**: 2025-01-30  
**Status**: 🔄 Preparation Phase - Ready for Task 2.4, 2.5, 2.6 implementation

