# 🔥 Hunter Codebase Roast Results — v1.0

**Date:** 2025-01-30  
**Mode:** Aggressive, blunt, expert-level  
**Scope:** `app/`, `integrations/`, `tasks/`, `api/`, `core/`, migrations, tests

---

## 1. 💣 BRUTAL ROAST (No Sugar-Coating)

### Dirty Abstractions

**`app/core/merger.py:upsert_companies()` — Race Condition Hell**
```10:90:app/core/merger.py
def upsert_companies(...)
```
- **Problem:** IntegrityError catch → retry pattern is a **band-aid on a bullet wound**
- **Why it's dirty:** Two concurrent requests for same domain → both try INSERT → one fails → retry → UPDATE. This is **not idempotent**, it's **hopeful retry logic**
- **Production risk:** Under load, you'll see duplicate key errors in logs, then "mysterious" updates that overwrite each other
- **Fix:** Use PostgreSQL `ON CONFLICT DO UPDATE` at the SQL level, not Python-level retry

**`app/integrations/d365/client.py:_find_lead_by_email()` — SQL Injection via String Interpolation**
```263:263:app/integrations/d365/client.py
filter_query = f"$filter=emailaddress1 eq '{email}'"
```
- **Problem:** Direct string interpolation in OData query
- **Why it's dirty:** If `email` contains `'` or `;`, you're **fucked**. OData injection is real.
- **Production risk:** Malicious email addresses can break queries or leak data
- **Fix:** Use OData parameter binding or proper escaping (httpx URL encoding)

**`app/core/referral_ingestion.py:sync_referrals_from_partner_center()` — 775 Lines of God Function**
```635:775:app/core/referral_ingestion.py
def sync_referrals_from_partner_center(db: Session) -> Dict[str, int]:
```
- **Problem:** Single function doing: fetch, parse, validate, extract, upsert, link, scan, track
- **Why it's dirty:** This is **not a function**, it's a **script masquerading as a function**
- **Production risk:** One bug = entire sync fails. Can't test individual steps. Can't reuse logic.
- **Fix:** Break into: `fetch_referrals()`, `extract_domain()`, `ingest_referral()`, `link_referral()`, `sync_referrals()` (orchestrator)

### Over-Engineered Parts

**`app/integrations/d365/mapping.py` — 118 Lines for 10 Field Mappings**
```7:117:app/integrations/d365/mapping.py
def map_lead_to_d365(lead_data: Dict[str, Any]) -> Dict[str, Any]:
```
- **Problem:** Separate function for email extraction, verbose logging, defensive None checks everywhere
- **Why it's over-engineered:** This is **data transformation**, not rocket science. Should be 30 lines max.
- **Production risk:** Maintenance burden. Every new field = 5 lines of code + tests.
- **Fix:** Use Pydantic model with field aliases, or dict comprehension with defaults

**`app/core/tasks.py:_bulk_metrics` — In-Memory Metrics That Will Disappear**
```30:41:app/core/tasks.py
_bulk_metrics = {
    "batch_success": 0,
    "batch_failure": 0,
    ...
}
```
- **Problem:** Global dict for metrics. Worker restart = metrics gone.
- **Why it's over-engineered:** You have Redis. Use it. Or use Prometheus. Or use DB.
- **Production risk:** Metrics are **lies** after worker restart. You'll think everything is fine.
- **Fix:** Move to Redis counters or Prometheus metrics

### Under-Engineered Fragile Spots

**`app/tasks/d365_push.py:push_lead_to_d365()` — No Idempotency Key**
```25:242:app/tasks/d365_push.py
@celery_app.task(bind=True, name="push_lead_to_d365", max_retries=3)
def push_lead_to_d365(self, lead_id: int):
```
- **Problem:** Task retries can create duplicate leads in D365
- **Why it's fragile:** If task fails after D365 create but before DB commit, retry = duplicate
- **Production risk:** Duplicate leads in D365, sales team confusion, data quality issues
- **Fix:** Use idempotency key (domain + timestamp) or check D365 before create

**`app/integrations/d365/client.py:_get_access_token()` — In-Memory Token Cache**
```51:109:app/integrations/d365/client.py
# Token cache (in-memory for now, can be persisted later)
self._token: Optional[str] = None
self._token_expires_at: Optional[datetime] = None
```
- **Problem:** "can be persisted later" = **technical debt**
- **Why it's fragile:** Multiple workers = multiple token acquisitions = rate limit hell
- **Production risk:** D365 rate limits on token endpoint. You'll hit it with 5 workers.
- **Fix:** Use Redis for token cache (shared across workers)

**`app/core/partner_center.py:_fetch_page()` — Retry Logic Without Jitter**
```177:298:app/core/partner_center.py
def _fetch_page(...)
```
- **Problem:** Exponential backoff without jitter = thundering herd
- **Why it's fragile:** All workers retry at same time → API still overloaded
- **Production risk:** Rate limit → all workers sleep 60s → all retry at once → rate limit again
- **Fix:** Add random jitter: `sleep(retry_after + random.uniform(0, 10))`

### Anti-Patterns

**`app/core/tasks.py:process_batch_with_retry()` — Transaction Timeout as Deadlock Prevention**
```296:297:app/core/tasks.py
# Set transaction timeout (30 seconds) for deadlock prevention
db.execute(text("SET statement_timeout = 30000"))
```
- **Problem:** Setting timeout per-transaction is **not deadlock prevention**, it's **deadlock tolerance**
- **Why it's anti-pattern:** Deadlocks still happen, you just fail faster. This doesn't prevent them.
- **Production risk:** You'll see timeout errors, think it's deadlocks, but it's actually slow queries
- **Fix:** Use row-level locking (`SELECT ... FOR UPDATE SKIP LOCKED`) or batch isolation

**`app/core/referral_ingestion.py` — Exception Swallowing in Loop**
```844:856:app/core/referral_ingestion.py
except Exception as e:
    logger.error(...)
    db.rollback()
    # Continue to next referral
```
- **Problem:** One bad referral = entire sync continues, but you lose that referral
- **Why it's anti-pattern:** Silent failures. No retry mechanism. No dead letter queue.
- **Production risk:** Referrals silently fail, you don't know until sales asks "where's my lead?"
- **Fix:** Dead letter queue (DB table) for failed referrals, retry mechanism, alerting

**`app/integrations/d365/client.py:create_or_update_lead()` — Lookup Then Create Pattern**
```145:195:app/integrations/d365/client.py
# Check for existing lead by email (if provided)
email = payload.get("emailaddress1")
if email:
    try:
        existing_lead = await self._find_lead_by_email(email)
```
- **Problem:** Two API calls (lookup + create) instead of one (upsert)
- **Why it's anti-pattern:** Race condition: lookup finds nothing → another worker creates → you create duplicate
- **Production risk:** Duplicate leads under concurrent load
- **Fix:** Use D365 `$batch` API for atomic upsert, or use external ID for idempotency

### Things That Will Explode in Production

1. **`app/core/tasks.py:bulk_scan_task()` — No Batch Size Limit**
   - **Problem:** Processes entire domain list in one task (could be 10,000 domains)
   - **Why it explodes:** Celery task timeout = 15 minutes. 10,000 domains × 15s = 41 hours.
   - **Fix:** Chunk into smaller batches, spawn sub-tasks

2. **`app/core/referral_ingestion.py:sync_referrals_from_partner_center()` — No Pagination**
   - **Problem:** Fetches all referrals in one go
   - **Why it explodes:** Partner Center returns 1000+ referrals → memory spike → OOM kill
   - **Fix:** Paginate API calls, process in batches

3. **`app/integrations/d365/client.py` — No Connection Pooling**
   - **Problem:** Creates new `httpx.AsyncClient` per request
   - **Why it explodes:** Under load, you'll exhaust file descriptors or connection limits
   - **Fix:** Reuse client (class-level or singleton)

---

## 2. 🔍 HIDDEN COMPLEXITY SCAN

### Implicit Coupling

**`app/tasks/d365_push.py` → `leads_ready` View Dependency**
```31:31:app/tasks/d365_push.py
# 1. Query lead data from leads_ready view (by company_id or domain)
```
- **Problem:** Task depends on view that may not have all columns (migration drift)
- **Hidden coupling:** View schema changes → task breaks silently (None values)
- **Fix:** Query base tables directly, or validate view columns at startup

**`app/core/referral_ingestion.py` → `app/core/tasks.py:scan_single_domain()`**
```581:632:app/core/referral_ingestion.py
def trigger_domain_scan(db: Session, domain: str) -> bool:
```
- **Problem:** Calls `scan_single_domain()` which has side effects (DB commits, cache writes)
- **Hidden coupling:** If `scan_single_domain()` changes behavior, referral ingestion breaks
- **Fix:** Extract scan logic into pure function, or use explicit interface

### Secret State Dependencies

**`app/core/celery_app.py` — Celery Config Scattered**
```15:31:app/core/celery_app.py
celery_app.conf.update(
    task_serializer="json",
    ...
)
```
- **Problem:** Config is in code, not environment variables
- **Secret state:** Different environments need different configs, but it's hardcoded
- **Fix:** Move to `app/config.py`, use `settings.celery_*` variables

**`app/integrations/d365/client.py` — Token Cache State**
```51:53:app/integrations/d365/client.py
# Token cache (in-memory for now, can be persisted later)
self._token: Optional[str] = None
self._token_expires_at: Optional[datetime] = None
```
- **Problem:** Token state is instance-level, but client is created per-request
- **Secret state:** Token expires between requests, but you don't know until API call fails
- **Fix:** Shared token cache (Redis) or singleton client

### Migration Drift Risks

**`app/db/models.py` — Missing Column Validation**
- **Problem:** Code assumes columns exist (e.g., `tenant_size`, `local_provider`, `dmarc_coverage`)
- **Migration drift:** If migration fails partially, code breaks with `AttributeError`
- **Fix:** Column existence check at startup, or use Alembic revision check

**`leads_ready` View — Dynamic Column Dependency**
- **Problem:** View includes columns that may not exist in base tables
- **Migration drift:** View creation fails if columns missing, but code doesn't check
- **Fix:** View creation in migration with `IF NOT EXISTS`, or validate at startup

### Celery + DB Interactions

**`app/tasks/d365_push.py` — DB Session Not Closed on Exception**
```241:242:app/tasks/d365_push.py
finally:
    db.close()
```
- **Problem:** Session is closed, but what if exception happens before `finally`?
- **Celery + DB:** Long-running tasks can leak connections
- **Fix:** Use context manager: `with SessionLocal() as db:`

**`app/core/tasks.py:bulk_scan_task()` — Single DB Session for Entire Task**
```416:417:app/core/tasks.py
@celery_app.task(bind=True)
def bulk_scan_task(self, job_id: str, is_rescan: bool = False):
```
- **Problem:** One session for entire bulk scan (could be 1000+ domains)
- **Celery + DB:** Long transaction = lock contention, connection pool exhaustion
- **Fix:** Create new session per batch, or use connection pool with proper limits

### API Boundary Leaks

**`app/api/leads.py` — Direct SQL in API Endpoint**
```914:926:app/api/leads.py
db.execute(text("SELECT ..."))
db.commit()
```
- **Problem:** Raw SQL in API layer = business logic leak
- **API boundary:** API should call service layer, not execute SQL
- **Fix:** Move to `app/core/leads_service.py`, API calls service

**`app/core/referral_ingestion.py` — Business Logic in Ingestion Layer**
- **Problem:** Domain extraction, company linking, scanning all in one module
- **API boundary:** Should be: `ingestion` → `domain_service` → `company_service` → `scan_service`
- **Fix:** Extract services, use dependency injection

---

## 3. 🔌 ADAPTER LAYER AUDIT

### Is D365 Adapter Isolated Enough?

**✅ GOOD:** Separate `app/integrations/d365/` directory  
**❌ BAD:** Task calls client directly, no service layer

**`app/tasks/d365_push.py` — Direct Client Usage**
```13:14:app/tasks/d365_push.py
from app.integrations.d365.client import D365Client
from app.integrations.d365.mapping import map_lead_to_d365
```
- **Problem:** Task knows about D365 client and mapping
- **Isolation risk:** If you add another CRM (Salesforce), you need to change task code
- **Fix:** Create `app/integrations/crm_service.py` with interface, D365 implements it

### Mapping Layer Long-Term Risk

**`app/integrations/d365/mapping.py` — Hardcoded Field Names**
```49:60:app/integrations/d365/mapping.py
hunter_fields = {
    "hunter_score": lead_data.get("readiness_score"),
    "hunter_segment": lead_data.get("segment"),
    ...
}
```
- **Problem:** Field names are hardcoded strings
- **Long-term risk:** D365 schema changes → code breaks, no compile-time check
- **Fix:** Use Pydantic model with field aliases, or config file

**Missing Validation — None Values in Mapping**
```68:70:app/integrations/d365/mapping.py
for key, value in hunter_fields.items():
    if value is not None:
        d365_payload[key] = value
```
- **Problem:** None values are skipped, but what if D365 requires the field?
- **Long-term risk:** D365 adds required field → mapping fails silently
- **Fix:** Validate required fields, or use D365 schema validation

### Client Retry/Backoff Correctness

**`app/integrations/d365/client.py` — No Retry Logic**
- **Problem:** Client doesn't retry on transient errors (timeout, 5xx)
- **Retry risk:** Network hiccup = task fails, needs Celery retry
- **Fix:** Add retry decorator to client methods, or use httpx retry middleware

**`app/tasks/d365_push.py` — Exponential Backoff Without Max**
```190:190:app/tasks/d365_push.py
raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
```
- **Problem:** `2 ** 3 = 8 minutes`, but what if retries = 10? (1024 minutes = 17 hours)
- **Backoff risk:** Task retries forever, clogs queue
- **Fix:** Cap backoff: `min(60 * (2 ** retries), 3600)` (max 1 hour)

### Feature Flag Safety

**`app/tasks/d365_push.py` — Feature Flag Check at Task Start**
```45:51:app/tasks/d365_push.py
if not settings.d365_enabled:
    logger.warning(...)
    return {"status": "skipped", "reason": "d365_disabled"}
```
- **Problem:** Task is queued even if feature flag is off
- **Feature flag risk:** Tasks accumulate in queue, waste resources
- **Fix:** Check feature flag before queuing task, or use Celery routing to skip disabled tasks

**`app/integrations/d365/client.py` — Feature Flag Check in Constructor**
```25:26:app/integrations/d365/client.py
if not settings.d365_enabled:
    raise ValueError("D365 integration is disabled (feature flag off)")
```
- **Problem:** Constructor raises exception, but task already queued
- **Feature flag risk:** Task fails immediately, but why was it queued?
- **Fix:** Check feature flag before creating client, or make client creation lazy

### Where Will It Break Under Load?

1. **Token Acquisition — No Rate Limiting**
   - **Problem:** Multiple workers acquire tokens simultaneously
   - **Break point:** 5 workers × 1 token/request = 5 token requests/second
   - **D365 limit:** ~10 requests/second, but you'll hit it under burst load
   - **Fix:** Token acquisition lock (Redis), or shared token cache

2. **Lead Lookup — N+1 Query Pattern**
   - **Problem:** `_find_lead_by_email()` called for every lead push
   - **Break point:** 100 leads/second = 100 API calls/second
   - **D365 limit:** ~50 requests/second (varies by tenant)
   - **Fix:** Batch lookup, or use external ID for idempotency

3. **Connection Pool Exhaustion**
   - **Problem:** New `httpx.AsyncClient` per request
   - **Break point:** 100 concurrent requests = 100 connections
   - **System limit:** Default 100 connections, but you'll hit it
   - **Fix:** Reuse client, or use connection pool

---

## 4. 🏢 PARTNER CENTER CRITIQUE

### Referral Ingestion Logic

**`app/core/referral_ingestion.py:extract_domain_from_referral()` — 200+ Lines of Fallback Chain**
```210:416:app/core/referral_ingestion.py
def extract_domain_from_referral(referral: Dict[str, Any]) -> Optional[str]:
```
- **Problem:** 6-step fallback chain with nested conditionals
- **Why it's fragile:** Each step can fail silently, hard to debug
- **Fix:** Extract each step into separate function, test individually

**Missing Validation — Consumer Domain Filter**
```49:64:app/core/referral_ingestion.py
def is_consumer_domain(domain: str) -> bool:
    ...
    return domain_lower in CONSUMER_DOMAINS
```
- **Problem:** Hardcoded list, what if new consumer domain appears?
- **Fix:** Use TLD-based detection, or configurable list

### Domain Merge

**`app/core/referral_ingestion.py:sync_referrals_from_partner_center()` — No Merge Strategy**
```754:771:app/core/referral_ingestion.py
if normalized_domain:
    linked_company = db.query(Company).filter(
        Company.domain == normalized_domain
    ).first()
```
- **Problem:** If domain exists, links referral. If not, creates company. But what if domain changes?
- **Merge risk:** Same company, different domains → duplicate companies
- **Fix:** Use canonical domain (company name + TLD), or merge strategy

### Sync Consistency

**`app/core/referral_ingestion.py` — No Transaction Wrapper**
```635:985:app/core/referral_ingestion.py
def sync_referrals_from_partner_center(db: Session) -> Dict[str, int]:
```
- **Problem:** Multiple `db.commit()` calls in one function
- **Consistency risk:** Partial sync if function fails mid-way
- **Fix:** Wrap entire sync in transaction, commit at end

**No Idempotency — Re-fetch Same Referral**
- **Problem:** Same referral fetched twice → duplicate tracking records
- **Consistency risk:** `partner_center_referrals` table has duplicates
- **Fix:** Use `ON CONFLICT (referral_id) DO UPDATE` in `upsert_referral_tracking()`

### Error Handling

**Exception Swallowing — Continue on Error**
```844:856:app/core/referral_ingestion.py
except Exception as e:
    logger.error(...)
    db.rollback()
    # Continue to next referral
```
- **Problem:** One bad referral = entire sync continues, but referral is lost
- **Error handling risk:** No retry, no dead letter queue, no alerting
- **Fix:** Dead letter queue (DB table), retry mechanism, alerting

### DB Schema Correctness

**`partner_center_referrals` — Nullable Domain**
```473:473:app/core/referral_ingestion.py
normalized_domain: Normalized domain string (nullable in Phase 1)
```
- **Problem:** Domain is nullable, but foreign key to `companies` requires domain
- **Schema risk:** Referrals without domain can't be linked, but table allows it
- **Fix:** Make domain NOT NULL, or add separate `unlinked_referrals` table

---

## 5. 🎨 UI/FRONTEND ROAST

### Latent UX Issues

**`mini-ui/js/ui-leads.js` — No Loading States**
- **Problem:** API calls are async, but UI doesn't show loading
- **UX risk:** User clicks button → nothing happens → clicks again → duplicate request
- **Fix:** Disable button during request, show spinner

**No Error Handling in UI**
- **Problem:** API errors are logged to console, but user doesn't see them
- **UX risk:** User thinks action failed, but it actually succeeded (or vice versa)
- **Fix:** Show error toast/alert, or inline error messages

### Mini UI Technical Debt

**Vanilla JavaScript — No Framework**
- **Problem:** 1000+ lines of vanilla JS, hard to maintain
- **Technical debt:** Adding features = more spaghetti code
- **Fix:** Use React/Vue, or at least use modules (ES6 imports)

**No Type Safety**
- **Problem:** TypeScript types exist (`mini-ui/types/sales.ts`), but JS doesn't use them
- **Technical debt:** Runtime errors instead of compile-time errors
- **Fix:** Convert to TypeScript, or use JSDoc types

**Global State Management**
- **Problem:** State is in global variables, no single source of truth
- **Technical debt:** State can be inconsistent across components
- **Fix:** Use state management (Redux, Zustand, or simple event bus)

### Refactor Priorities

1. **Extract API Client** — `mini-ui/js/api.js` is 500+ lines
   - **Priority:** HIGH
   - **Why:** API changes require updating multiple places
   - **Fix:** Create `ApiClient` class, use dependency injection

2. **Component Architecture** — No component boundaries
   - **Priority:** MEDIUM
   - **Why:** Hard to test, hard to reuse
   - **Fix:** Extract components (LeadCard, ReferralCard, etc.)

3. **Error Handling** — No centralized error handling
   - **Priority:** HIGH
   - **Why:** Errors are silent, user doesn't know what happened
   - **Fix:** Error boundary, toast notifications

### "Things You Will Regret in 3 Months"

1. **No State Persistence** — Refresh = lost state
   - **Regret:** User filters leads, refreshes page → filters gone
   - **Fix:** Use localStorage or URL params

2. **No Pagination UI** — Loads all leads at once
   - **Regret:** 1000+ leads = slow page load, memory issues
   - **Fix:** Implement pagination, virtual scrolling

3. **Hardcoded API URLs** — No environment config
   - **Regret:** Can't use different API for dev/staging/prod
   - **Fix:** Use config file, or environment variables

---

## 6. ✅ ACTIONABLE FIX LIST (Top 10)

### Short-Term (This Week)

1. **🔴 CRITICAL: Fix SQL Injection in D365 Client**
   - **File:** `app/integrations/d365/client.py:263`
   - **Fix:** Use URL encoding: `filter_query = f"$filter=emailaddress1 eq {urllib.parse.quote(email)}"`
   - **Impact:** Security vulnerability, can leak data
   - **Effort:** 5 minutes

2. **🔴 CRITICAL: Add Idempotency to D365 Push Task**
   - **File:** `app/tasks/d365_push.py:25`
   - **Fix:** Use idempotency key (domain + timestamp), check D365 before create
   - **Impact:** Prevents duplicate leads in D365
   - **Effort:** 2 hours

3. **🟡 HIGH: Move Token Cache to Redis**
   - **File:** `app/integrations/d365/client.py:51`
   - **Fix:** Use Redis for token cache, shared across workers
   - **Impact:** Prevents rate limit on token endpoint
   - **Effort:** 4 hours

4. **🟡 HIGH: Add Jitter to Retry Backoff**
   - **File:** `app/core/partner_center.py:288`
   - **Fix:** `sleep(retry_after + random.uniform(0, 10))`
   - **Impact:** Prevents thundering herd on retry
   - **Effort:** 30 minutes

5. **🟡 HIGH: Fix DB Session Leaks in Celery Tasks**
   - **File:** `app/tasks/d365_push.py:53`, `app/core/tasks.py:416`
   - **Fix:** Use context manager: `with SessionLocal() as db:`
   - **Impact:** Prevents connection pool exhaustion
   - **Effort:** 1 hour

### Long-Term (This Month)

6. **🟢 MEDIUM: Break Down `sync_referrals_from_partner_center()`**
   - **File:** `app/core/referral_ingestion.py:635`
   - **Fix:** Extract into: `fetch_referrals()`, `extract_domain()`, `ingest_referral()`, `link_referral()`
   - **Impact:** Better testability, maintainability
   - **Effort:** 1 day

7. **🟢 MEDIUM: Add Dead Letter Queue for Failed Referrals**
   - **File:** `app/core/referral_ingestion.py:844`
   - **Fix:** Create `failed_referrals` table, retry mechanism
   - **Impact:** No silent failures, better observability
   - **Effort:** 1 day

8. **🟢 MEDIUM: Use PostgreSQL `ON CONFLICT` in `upsert_companies()`**
   - **File:** `app/core/merger.py:10`
   - **Fix:** Replace Python retry with SQL `ON CONFLICT DO UPDATE`
   - **Impact:** Eliminates race conditions, better performance
   - **Effort:** 2 hours

9. **🟢 MEDIUM: Extract D365 Adapter to Service Layer**
   - **File:** `app/tasks/d365_push.py:13`
   - **Fix:** Create `app/integrations/crm_service.py`, D365 implements interface
   - **Impact:** Better isolation, easier to add other CRMs
   - **Effort:** 1 day

10. **🟢 LOW: Convert Mini UI to TypeScript**
    - **File:** `mini-ui/js/*.js`
    - **Fix:** Convert to TypeScript, use types from `mini-ui/types/sales.ts`
    - **Impact:** Better developer experience, fewer runtime errors
    - **Effort:** 3 days

---

## 📊 Summary

- **Critical Issues:** 2 (SQL injection, duplicate leads)
- **High Priority:** 3 (token cache, retry jitter, DB leaks)
- **Medium Priority:** 4 (refactoring, dead letter queue, service layer)
- **Low Priority:** 1 (TypeScript conversion)

**Total Estimated Effort:** ~2 weeks (if done sequentially)

**Recommendation:** Fix critical issues immediately, then tackle high-priority items before D365 integration goes live.

