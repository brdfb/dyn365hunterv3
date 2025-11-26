# Partner Center Referrals Sync v1 - TODO

**Date Created**: 2025-11-26  
**Last Updated**: 2025-11-26  
**Status**: 🔄 In Progress  
**Phase**: Partner Center Integration - Referrals Sync v1 Productization  
**Priority**: P1  
**Estimated Duration**: 3-5 days  
**Risk Level**: 2/10 (external API dependency)  
**Branch**: `feature/partner-center-phase1`  
**Design Doc**: `docs/active/PARTNER-CENTER-REFERRALS-DESIGN.md`

---

## 🎯 Goal

Partner Center'dan referral'ları (leads/opportunities) çekip Hunter'a entegre etmek. Referral'lar otomatik olarak domain'e normalize edilecek, company olarak upsert edilecek ve domain scan tetiklenecek.

**API Contract**:
- Base URL: `https://api.partner.microsoft.com` ✅
- Endpoint: `/v1.0/engagements/referrals` ✅
- Scope: `https://api.partner.microsoft.com/.default` ✅

---

## 📋 Task List

### Phase 1 – API Contract & Config (MVP)

#### ✅ Task 1.1: Base URL & Scope Finalization
- [x] Base URL updated to `https://api.partner.microsoft.com`
- [x] Endpoint updated to `/v1.0/engagements/referrals`
- [x] API returns 200 OK (verified 2025-11-26)
- **Status**: ✅ **COMPLETED**

#### ✅ Task 1.2: Standard Query Template
- [x] Add config: `HUNTER_PARTNER_CENTER_API_VERSION` (default: `v1.0`)
- [x] Add config: `HUNTER_PARTNER_CENTER_REFERRAL_DEFAULT_DIRECTION` (default: `Incoming`)
- [x] Add config: `HUNTER_PARTNER_CENTER_REFERRAL_DEFAULT_STATUS` (default: `Active`)
- [x] Add config: `HUNTER_PARTNER_CENTER_REFERRAL_DEFAULT_TOP` (default: `200`)
- [x] Add config: `HUNTER_PARTNER_CENTER_USERNAME` (optional, for future use)
- [x] Add config: `HUNTER_PARTNER_CENTER_PASSWORD` (optional, for future use)
- [x] Default OData: `$top`, `$orderby=createdDateTime desc`, `$filter`
- [x] Create `build_referral_query()` helper function
- [x] Use config values in `get_referrals()`
- **Status**: ✅ **COMPLETED** (2025-01-30)

#### ✅ Task 1.3: Pagination Support
- [x] Handle `@odata.nextLink` in `get_referrals()`
- [x] Loop until no more pages
- [x] Add max pages limit (configurable, default: 10 pages = 2000 records with top=200)
- [x] Add `_fetch_page()` helper method for single page fetching with retry
- [x] Rate limiting between pages (sleep(1))
- [x] Structured logging for pagination progress
- **Status**: ✅ **COMPLETED** (2025-01-30)

---

### Phase 2 – Referral Client & Error Handling (MVP)

#### ✅ Task 2.1: Basic Client Implementation
- [x] URL build: `/v1.0/engagements/referrals`
- [x] OData params: filter/orderby/top
- [x] Standard query template: `build_referral_query()` helper ✅ (2025-01-30)
- [x] Config-based defaults: direction, status, top ✅ (2025-01-30)
- [x] Pagination (Task 1.3) ✅ (2025-01-30)
- **Status**: ✅ **COMPLETED** (2025-01-30)

#### ✅ Task 2.2: HTTP/Status Handling
- [x] 401/403 → `PartnerCenterAuthError` exception
- [x] 429 → retry with exponential backoff (3 retry) + Retry-After header support
- [x] 5xx → retry logic (exponential backoff, max 3 retries)
- [x] Log: `status_code`, `request_id`, `url`
- [x] Request ID extraction from response headers
- [x] Custom exception classes (`PartnerCenterAuthError`, `PartnerCenterRateLimitError`)
- **Status**: ✅ **COMPLETED** (2025-01-30)

#### ✅ Task 2.3: Structured Logging & Metrics
- [x] Track per sync: `total_fetched`, `total_processed`, `total_skipped`, `total_inserted`
- [x] Log events: `partner_center_referrals_fetched`, `partner_center_referrals_ingested`, `partner_center_referrals_skipped`
- [x] Summary log at end of sync (`partner_center_sync_summary`)
- [x] Skipped reasons tracking (`domain_not_found`, `duplicate`)
- [x] Per-referral ingestion logging (`partner_center_referral_ingested`)
- **Status**: ✅ **COMPLETED** (2025-01-30)

---

### Phase 3 – Domain Extraction & Mapping (MVP CORE)

#### ✅ Task 3.1: Referral DTO / Mapping Plan
- [x] Create `PartnerCenterReferralDTO` (dataclass)
- [x] Map required fields: `id`, `engagementId`, `name`, `status`, `substatus`, `type`, `direction`, `customerProfile`, `details`
- [x] Add `from_dict()` class method for mapping
- [x] Datetime parsing for `createdDateTime` and `updatedDateTime`
- **Status**: ✅ **COMPLETED** (2025-01-30)

#### ✅ Task 3.2: Domain Extraction from CustomerProfile & Team
- [x] Implement `extract_domain_from_referral()` with CustomerProfile.Team support
- [x] Extract from `CustomerProfile.Team` member emails
- [x] Filter consumer domains (gmail, outlook, yahoo, hotmail, icloud, etc.)
- [x] Fallback: `customerProfile.ids.External` (if applicable)
- [x] Legacy fallback: website → email (for backward compatibility)
- [x] Add `is_consumer_domain()` helper function
- [x] Add `CONSUMER_DOMAINS` set with common consumer email providers
- **Status**: ✅ **COMPLETED** (2025-01-30)

#### ⏳ Task 3.3: URL-based Domain Fallback
- **Status**: ⏳ **POST-MVP** (not in current schema)

#### ✅ Task 3.4: Domain Extraction Unit Tests
- [x] Test: Single contact email → domain
- [x] Test: Multiple contacts (consumer + company) → company domain
- [x] Test: No emails → None
- [x] Test: Consumer domains filtered
- [x] Test: Edge cases (empty emails, None values, invalid formats)
- [x] Test: Fallback chains (Team → External ID → website → email)
- [x] Test: DTO mapping and datetime parsing
- [x] All tests passing (30/30 tests ✅)
- **Status**: ✅ **COMPLETED** (2025-01-30)

---

### Phase 4 – DB Schema & Ingestion Logic (MVP)

#### 🔄 Task 4.1: DB Schema Revision/Validation
- [ ] Verify `partner_center_referrals` table has all required columns:
  - `id`, `engagement_id`, `external_reference_id`
  - `status`, `substatus`, `type`, `qualification`, `direction`
  - `customer_name`, `customer_country`
  - `deal_value`, `currency`
  - `domain`, `raw_payload` (JSONB)
  - `created_at`, `updated_at`
- **Status**: 🔄 **IN PROGRESS**

#### 🔄 Task 4.2: Upsert Strategy
- [ ] Implement `ON CONFLICT (id) DO UPDATE`
- [ ] Update: `status`, `substatus`, `updatedDateTime`, `deal_value`
- [ ] Verify idempotent behavior
- **Status**: 🔄 **IN PROGRESS**

#### 🔄 Task 4.3: Ingestion Filter Rules
- [ ] Only insert if: `direction='Incoming'`, `status IN ('New','Active')`, `substatus NOT IN ('Declined','Lost','Expired','Error')`, `domain IS NOT NULL`
- [ ] Skip others with log: `partner_center_referral_skipped` + reason
- **Status**: 🔄 **IN PROGRESS**

#### 🔄 Task 4.4: Hunter Lead Pipeline Integration
- [ ] Lookup `partner_center_referrals.domain` in `domains`/`leads` tables
- [ ] If exists: Link existing lead (`source='partner_center'`, `external_id=referral.id`)
- [ ] If not: Create new lead candidate (`source='partner_center'`)
- **Status**: 🔄 **IN PROGRESS**

---

### Phase 5 – Observability & Safeguards (MVP++)

#### 🔄 Task 5.1: Sync Run Summary Logging
- [ ] Single summary log at end of sync:
  ```json
  {
    "event": "partner_center_sync_summary",
    "fetched": 50,
    "inserted": 30,
    "updated": 10,
    "skipped_no_domain": 8,
    "skipped_status": 2
  }
  ```
- **Status**: 🔄 **IN PROGRESS**

#### ⏳ Task 5.2: Health Endpoint Metrics
- **Status**: ⏳ **POST-MVP**

#### ⏳ Task 5.3: Rate Limiting / Safety Guard
- **Status**: ⏳ **POST-MVP**

---

### Phase 6 – Test Suite & Docs (MVP)

#### 🔄 Task 6.1: Unit Tests
- [ ] `PartnerCenterClient.fetch_referrals`: 200 OK + single page
- [ ] `PartnerCenterClient.fetch_referrals`: 200 OK + pagination
- [ ] `PartnerCenterClient.fetch_referrals`: 401/403 → exception
- [ ] Domain extraction tests (Task 3.4)
- **Status**: 🔄 **IN PROGRESS**

#### 🔄 Task 6.2: Integration Tests
- [ ] Happy path: X inbound pending → Sync → X rows in DB
- [ ] Status change: New→Active→Closed → update works
- **Status**: 🔄 **IN PROGRESS**

#### ✅ Task 6.3: Documentation
- [x] Design document created (`PARTNER-CENTER-REFERRALS-DESIGN.md`)
- [ ] API contract documented
- [ ] DB schema documented
- [ ] Domain extraction rules documented
- [ ] Sync flow diagram added
- **Status**: ✅ **PARTIALLY COMPLETED**

---

## 📊 Progress Summary

**MVP Requirements**:
- Phase 1: 3/3 tasks completed (1.1 ✅, 1.2 ✅, 1.3 ✅)
- Phase 2: 3/3 tasks completed (2.1 ✅, 2.2 ✅, 2.3 ✅)
- Phase 3: 3/4 tasks completed (3.1 ✅, 3.2 ✅, 3.3 ⏳, 3.4 ✅)
- Phase 4: 0/4 tasks completed (4.1-4.4 🔄)
- Phase 5: 0/1 tasks completed (5.1 🔄, 5.2-5.3 ⏳)
- Phase 6: 1/3 tasks partially completed (6.1-6.2 🔄, 6.3 ✅)

**Overall Progress**: ~45% (8 completed, 8 in progress, 3 post-MVP)

---

## 🔗 References

- Design Document: `docs/active/PARTNER-CENTER-REFERRALS-DESIGN.md`
- API Docs: [Get a list of leads and opportunities](https://learn.microsoft.com/en-us/partner-center/developer/get-a-list-of-referrals)
- Referral Resources: [Referral resources](https://learn.microsoft.com/en-us/partner-center/developer/referral-resources)
- Authentication: [Referrals API authentication](https://learn.microsoft.com/en-us/partner-center/developer/referral-api-authentication)

