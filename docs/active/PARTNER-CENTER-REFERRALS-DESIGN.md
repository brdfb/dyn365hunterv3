# Partner Center Referrals Sync v1 - Design Document

**Date Created**: 2025-11-26  
**Status**: 🔄 In Progress  
**Phase**: Partner Center Integration - Referrals Sync v1  
**Priority**: P1  
**API Reference**: [Microsoft Partner Referrals API](https://learn.microsoft.com/en-us/partner-center/developer/get-a-list-of-referrals)

---

## 🎯 Overview

Partner Center'dan referral'ları (leads/opportunities) çekip Hunter'a entegre etmek. Referral'lar otomatik olarak domain'e normalize edilecek, company olarak upsert edilecek ve domain scan tetiklenecek.

**API Contract**:
- **Base URL**: `https://api.partner.microsoft.com` (NOT `api.partnercenter.microsoft.com`)
- **Endpoint**: `/v1.0/engagements/referrals`
- **Scope**: `https://api.partner.microsoft.com/.default`
- **Auth**: MSAL Device Code Flow (delegated permissions)

**References**:
- [Get a list of leads and opportunities](https://learn.microsoft.com/en-us/partner-center/developer/get-a-list-of-referrals)
- [Referral resources](https://learn.microsoft.com/en-us/partner-center/developer/referral-resources)
- [Referrals API authentication](https://learn.microsoft.com/en-us/partner-center/developer/referral-api-authentication)

---

## 📋 Phase Breakdown

### Phase 1 – API Contract & Config (MVP)

#### 1.1: Base URL & Scope Finalization ✅ **COMPLETED**

**Status**: ✅ Completed (2025-11-26)

**Changes**:
- Base URL: `https://api.partnercenter.microsoft.com` → `https://api.partner.microsoft.com`
- Endpoint: `/v1/referrals` → `/v1.0/engagements/referrals`
- Scope: `https://api.partner.microsoft.com/.default` (already correct)

**Files**:
- `app/config.py` - `partner_center_api_url` default
- `app/core/partner_center.py` - Endpoint path
- `.env.example` - Updated default
- `docker-compose.yml` - Updated default

**Acceptance Criteria**:
- [x] Base URL updated to `https://api.partner.microsoft.com`
- [x] Endpoint updated to `/v1.0/engagements/referrals`
- [x] API returns 200 OK (verified 2025-11-26)

---

#### 1.2: Standard Query Template ✅ **COMPLETED**

**Status**: ✅ Completed (2025-01-30)

**Requirements**:
- Default OData parameters:
  - `$top` (default: 200, configurable via `HUNTER_PARTNER_CENTER_REFERRAL_DEFAULT_TOP`)
  - `$orderby=createdDateTime desc`
  - `$filter=direction eq '{direction}' and status eq '{status}'` (default: direction='Incoming', status='Active')

**Config Variables**:
- `HUNTER_PARTNER_CENTER_API_VERSION` (default: `v1.0`)
- `HUNTER_PARTNER_CENTER_REFERRAL_DEFAULT_DIRECTION` (default: `Incoming`)
- `HUNTER_PARTNER_CENTER_REFERRAL_DEFAULT_STATUS` (default: `Active`)
- `HUNTER_PARTNER_CENTER_REFERRAL_DEFAULT_TOP` (default: `200`)
- `HUNTER_PARTNER_CENTER_USERNAME` (optional, for future use)
- `HUNTER_PARTNER_CENTER_PASSWORD` (optional, for future use)

**Files**:
- `app/config.py` - Added config variables ✅
- `app/core/partner_center.py` - Added `build_referral_query()` helper and updated `get_referrals()` ✅

**Acceptance Criteria**:
- [x] Config variables added
- [x] Default filter applied
- [x] Query parameters configurable via env vars
- [x] Query builder helper function created (`build_referral_query()`)

---

#### 1.3: Pagination Support ✅ **COMPLETED**

**Status**: ✅ Completed (2025-01-30)

**Requirements**:
- Handle `@odata.nextLink` for page-by-page fetching
- Client logic:
  - First GET → `response["value"]`
  - If `@odata.nextLink` exists → loop until no more pages

**Config Variables**:
- `HUNTER_PARTNER_CENTER_REFERRAL_MAX_PAGES` (default: `10` pages = 2000 records with top=200)

**Files**:
- `app/config.py` - Added `partner_center_referral_max_pages` config ✅
- `app/core/partner_center.py` - Added pagination logic to `get_referrals()` ✅
  - `_fetch_page()` helper method for single page fetching with retry
  - Pagination loop with `@odata.nextLink` handling
  - Max pages limit enforcement

**Acceptance Criteria**:
- [x] Pagination loop implemented
- [x] All pages fetched when `@odata.nextLink` present
- [x] Max pages limit (configurable, default: 10 pages = 2000 records with top=200)
- [x] Rate limiting between pages (sleep(1))
- [x] Structured logging for pagination progress

---

### Phase 2 – Referral Client & Error Handling (MVP)

#### 2.1: `fetch_referrals()` Implementation ✅ **COMPLETED**

**Status**: ✅ Completed (basic implementation done, standard query template completed, pagination implemented)

**Current Implementation**:
- URL build: `/v1.0/engagements/referrals` ✅
- OData params: filter/orderby/top ✅
- Standard query template: `build_referral_query()` helper ✅ (2025-01-30)
- Config-based defaults: direction, status, top ✅ (2025-01-30)
- Pagination: ✅ Implemented (2025-01-30)
  - `@odata.nextLink` handling ✅
  - Max pages limit (configurable, default: 10) ✅
  - `_fetch_page()` helper with retry logic ✅
  - Rate limiting between pages ✅

**Files**:
- `app/core/partner_center.py` - `get_referrals()` method, `build_referral_query()` helper, `_fetch_page()` helper

**Acceptance Criteria**:
- [x] URL build correct
- [x] OData params applied
- [x] Standard query template implemented (Task 1.2)
- [x] Config-based defaults working
- [x] Pagination implemented (Task 1.3)
- [x] Returns flat list of dicts (referral JSONs)

---

#### 2.2: HTTP/Status Handling ✅ **COMPLETED**

**Status**: ✅ Completed (2025-01-30)

**Requirements**:
- 2xx → OK
- 4xx/5xx:
  - 401/403 → auth/log + `PartnerCenterAuthError`
  - 429 → retry/backoff (3 retry, exponential)
  - 5xx → retry + error log
- Log: `status_code`, `request_id`, `url`

**Files**:
- `app/core/exceptions.py` - Added `PartnerCenterAuthError` and `PartnerCenterRateLimitError` ✅
- `app/core/partner_center.py` - Enhanced error handling in `_fetch_page()` ✅
  - `_extract_request_id()` helper for request ID extraction
  - 401/403 → `PartnerCenterAuthError` with request ID
  - 429 → `PartnerCenterRateLimitError` with exponential backoff + Retry-After header support
  - 5xx → Retry with exponential backoff (max 3 retries)
  - Structured error logging with status_code, request_id, url

**Acceptance Criteria**:
- [x] 401/403 → proper exception (`PartnerCenterAuthError`)
- [x] 429 → retry with backoff (exponential + Retry-After header support)
- [x] 5xx → retry logic (exponential backoff, max 3 retries)
- [x] Structured error logging (status_code, request_id, url)
- [x] Request ID extraction from response headers

---

#### 2.3: Structured Logging & Metrics ✅ **COMPLETED**

**Status**: ✅ Completed (2025-01-30)

**Requirements**:
- Per sync run metrics:
  - `total_fetched`
  - `total_processed`
  - `total_skipped`
  - `total_inserted`
- Log events:
  - `partner_center_referrals_fetched`
  - `partner_center_referrals_ingested`
  - `partner_center_referrals_skipped`

**Files**:
- `app/core/partner_center.py` - `partner_center_referrals_fetched` log event ✅
- `app/core/referral_ingestion.py` - Enhanced metrics tracking ✅
  - Per-referral metrics: `total_fetched`, `total_processed`, `total_skipped`, `total_inserted`
  - Skipped reasons tracking: `domain_not_found`, `duplicate`
  - `partner_center_referral_ingested` log event for each successful ingestion
  - `partner_center_referral_skipped` log event with reason
  - `partner_center_sync_summary` log event at end of sync with all metrics

**Acceptance Criteria**:
- [x] Metrics tracked per sync run
- [x] Structured log events added
- [x] Summary log at end of sync (`partner_center_sync_summary`)
- [x] Per-referral ingestion logging (`partner_center_referral_ingested`)
- [x] Skipped referrals logging with reasons

---

### Phase 3 – Domain Extraction & Mapping (MVP CORE)

#### 3.1: Referral DTO / Mapping Plan ✅ **COMPLETED**

**Status**: ✅ Completed (2025-01-30)

**Required Fields from Microsoft Schema**:
- `id`, `engagementId`, `name`, `createdDateTime`, `updatedDateTime`
- `status`, `substatus`, `type`, `qualification`, `direction`
- `customerProfile.name`, `customerProfile.address.country`
- `details.dealValue`, `details.currency`

**Internal DTO**:
- `PartnerCenterReferralDTO` (Python dataclass) ✅

**Files**:
- `app/core/referral_ingestion.py` - Added DTO class ✅
  - `PartnerCenterReferralDTO` dataclass with all required fields
  - `from_dict()` class method for mapping from Partner Center API response
  - Datetime parsing for `createdDateTime` and `updatedDateTime`
  - Nested field extraction (customerProfile, details, address)

**Acceptance Criteria**:
- [x] DTO class created
- [x] All required fields mapped
- [x] Type validation (dataclass with type hints)

---

#### 3.2: Domain Extraction from CustomerProfile & Team ✅ **COMPLETED**

**Status**: ✅ Completed (2025-01-30)

**Requirements**:
- Extract domain from `CustomerProfile.Team` member emails
- Fallback: `customerProfile.ids.External` (if applicable)
- Skip consumer domains (gmail, outlook, yahoo, hotmail, etc.)

**Implementation**:
- `extract_domain_from_referral()` function updated ✅
- `is_consumer_domain()` helper function added ✅
- `CONSUMER_DOMAINS` set with common consumer email providers ✅

**Fallback Chain**:
1. CustomerProfile.Team member emails → extract domain, filter consumer domains ✅
2. customerProfile.ids.External (if applicable) ✅
3. Legacy fallback: website → email (for backward compatibility) ✅
4. Skip: Domain yoksa → None (log warning) ✅

**Files**:
- `app/core/referral_ingestion.py` - `extract_domain_from_referral()`, `is_consumer_domain()`, `CONSUMER_DOMAINS` ✅

**Acceptance Criteria**:
- [x] Domain extracted from Team emails
- [x] Consumer domains filtered (gmail, outlook, yahoo, hotmail, icloud, etc.)
- [x] Fallback logic implemented (Team → External ID → website → email)
- [x] Returns `None` if no valid domain

---

#### 3.3: URL-based Domain Fallback ⏳ **POST-MVP**

**Status**: ⏳ Post-MVP

**Note**: Not in current Microsoft schema, future enhancement.

---

#### 3.4: Domain Extraction Unit Tests ✅ **COMPLETED**

**Status**: ✅ Completed (2025-01-30)

**Test Cases**:
- Single contact email → `contoso.com` ✅
- Multiple contacts; one @gmail, one @company.com → `company.com` ✅
- No emails → `None` ✅
- Consumer domains → filtered out ✅
- Additional edge cases: empty emails, None emails, invalid formats, fallback chains ✅

**Files**:
- `tests/test_referral_ingestion.py` - Domain extraction tests ✅
  - `TestDomainExtraction`: 16 test cases covering all extraction scenarios
  - `TestConsumerDomainFiltering`: 9 test cases for consumer domain filtering
  - `TestPartnerCenterReferralDTO`: 5 test cases for DTO mapping

**Test Coverage**:
- Domain extraction from CustomerProfile.Team emails ✅
- Consumer domain filtering (gmail, outlook, yahoo, hotmail, icloud, etc.) ✅
- Fallback chains (Team → External ID → website → email) ✅
- Edge cases (empty emails, None values, invalid formats) ✅
- DTO mapping and datetime parsing ✅

**Acceptance Criteria**:
- [x] Unit tests for domain extraction (16 test cases)
- [x] Edge cases covered (empty emails, None values, invalid formats)
- [x] Consumer domain filtering tested (9 test cases)
- [x] DTO mapping tests (5 test cases)
- [x] All tests passing (30/30 tests ✅)

---

### Phase 4 – DB Schema & Ingestion Logic (MVP)

#### 4.1: DB Schema Revision/Validation 🔄 **IN PROGRESS**

**Status**: 🔄 In Progress

**Table**: `partner_center_referrals`

**Required Columns**:
- `id` (PK, referral ID)
- `engagement_id`
- `external_reference_id` (Dynamics ID mapping)
- `status`, `substatus`, `type`, `qualification`, `direction`
- `customer_name`, `customer_country`
- `deal_value`, `currency`
- `domain` (critical for Hunter)
- `raw_payload` (JSONB, optional but useful for debug)
- `created_at`, `updated_at` (local timestamps)

**Files**:
- `app/db/models.py` - `PartnerCenterReferral` model
- `alembic/versions/XXXX_add_partner_center_referrals.py` - Migration

**Acceptance Criteria**:
- [ ] Schema matches requirements
- [ ] All fields present
- [ ] Indexes optimized

---

#### 4.2: Upsert Strategy 🔄 **IN PROGRESS**

**Status**: 🔄 In Progress

**Requirements**:
- Key: `id` (unique per Microsoft docs)
- `ON CONFLICT (id) DO UPDATE`:
  - Update: `status`, `substatus`, `updatedDateTime`, `deal_value`
  - Idempotent: re-fetch same referral updates existing record

**Files**:
- `app/core/referral_ingestion.py` - Upsert logic

**Acceptance Criteria**:
- [ ] Upsert on `id` works
- [ ] Updates existing records
- [ ] Idempotent behavior verified

---

#### 4.3: Ingestion Filter Rules 🔄 **IN PROGRESS**

**Status**: 🔄 In Progress

**Requirements**:
- Only write to DB if:
  - `direction = 'Incoming'`
  - `status IN ('New', 'Active')`
  - `substatus NOT IN ('Declined','Lost','Expired','Error')`
  - `domain IS NOT NULL`
- Skip others with log:
  - `partner_center_referral_skipped`
  - `reason = "no_domain" | "status_closed" | "direction_outgoing"`

**Files**:
- `app/core/referral_ingestion.py` - Filter logic

**Acceptance Criteria**:
- [ ] Filter rules implemented
- [ ] Skip logging works
- [ ] Only valid referrals inserted

---

#### 4.4: Hunter Lead Pipeline Integration 🔄 **IN PROGRESS**

**Status**: 🔄 In Progress

**Requirements**:
- `partner_center_referrals.domain` → lookup in `domains`/`leads` tables
- If domain exists:
  - Link existing lead (`source='partner_center'`, `external_id = referral.id`)
- If not:
  - Create new lead candidate (`source='partner_center'`)

**Files**:
- `app/core/referral_ingestion.py` - Lead pipeline integration

**Acceptance Criteria**:
- [ ] Domain lookup works
- [ ] Existing leads linked
- [ ] New leads created

---

### Phase 5 – Observability & Safeguards (MVP++)

#### 5.1: Sync Run Summary Logging 🔄 **IN PROGRESS**

**Status**: 🔄 In Progress

**Requirements**:
- Single summary log at end of sync:
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

**Files**:
- `app/core/referral_ingestion.py` - Summary logging

**Acceptance Criteria**:
- [ ] Summary log at end of sync
- [ ] All metrics included
- [ ] Structured JSON format

---

#### 5.2: Health Endpoint Metrics ⏳ **POST-MVP**

**Status**: ⏳ Post-MVP

**Note**: Advanced health metrics, not required for MVP.

---

#### 5.3: Rate Limiting / Safety Guard ⏳ **POST-MVP**

**Status**: ⏳ Post-MVP

**Note**: Max pages per run limit, not required for MVP.

---

### Phase 6 – Test Suite & Docs (MVP)

#### 6.1: Unit Tests 🔄 **IN PROGRESS**

**Status**: 🔄 In Progress

**Test Cases**:
- `PartnerCenterClient.fetch_referrals`:
  - 200 OK + single page
  - 200 OK + `@odata.nextLink` pagination
  - 401/403 → proper exception
- Domain extraction tests (Phase 3.4)

**Files**:
- `tests/test_partner_center.py` - Client tests
- `tests/test_referral_ingestion.py` - Ingestion tests

**Acceptance Criteria**:
- [ ] Unit tests for client
- [ ] Unit tests for domain extraction
- [ ] Error handling tests

---

#### 6.2: Integration Tests (DEV Sandbox) 🔄 **IN PROGRESS**

**Status**: 🔄 In Progress

**Test Scenarios**:
- Happy path: X inbound pending referrals → Sync → X rows in DB
- Status change: New→Active→Closed → update works

**Files**:
- `tests/test_referral_integration.py` - Integration tests

**Acceptance Criteria**:
- [ ] Integration tests pass
- [ ] Status change handling verified

---

#### 6.3: Documentation ✅ **IN PROGRESS**

**Status**: ✅ In Progress (this document)

**Files**:
- `docs/active/PARTNER-CENTER-REFERRALS-DESIGN.md` - This document

**Acceptance Criteria**:
- [x] Design document created
- [ ] API contract documented
- [ ] DB schema documented
- [ ] Domain extraction rules documented
- [ ] Sync flow diagram added

---

## 🔄 Sync Flow Diagram

```
Partner Center API
    ↓
GET /v1.0/engagements/referrals
    ↓
PartnerCenterClient.fetch_referrals()
    ↓
Pagination Loop (@odata.nextLink)
    ↓
extract_domain_from_referral()
    ↓
Filter Rules (direction, status, domain)
    ↓
Upsert partner_center_referrals
    ↓
Link/Create Hunter Lead
    ↓
Trigger Domain Scan (if new domain)
    ↓
Summary Logging
```

---

## 📊 MVP vs Post-MVP

### ✅ MVP Requirements
- Phase 1: All tasks (1.1-1.3)
- Phase 2: All tasks (2.1-2.3)
- Phase 3: Tasks 3.1, 3.2, 3.4 (skip 3.3)
- Phase 4: All tasks (4.1-4.4)
- Phase 5: Task 5.1 only (skip 5.2-5.3)
- Phase 6: All tasks (6.1-6.3)

### ⏳ Post-MVP
- Phase 3.3: URL-based domain fallback
- Phase 5.2: Advanced health metrics
- Phase 5.3: Rate limiting tuning
- Analytics endpoint usage
- Status-change webhook optimization

---

## 🔗 References

- [Get a list of leads and opportunities](https://learn.microsoft.com/en-us/partner-center/developer/get-a-list-of-referrals)
- [Referral resources](https://learn.microsoft.com/en-us/partner-center/developer/referral-resources)
- [Referrals API authentication](https://learn.microsoft.com/en-us/partner-center/developer/referral-api-authentication)

