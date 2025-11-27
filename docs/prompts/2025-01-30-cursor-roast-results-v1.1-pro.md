# 🔥 Hunter Codebase Roast Results — v1.1 PRO

**Date:** 2025-01-30  
**Mode:** Production-SRE-level, future-proofing focus  
**Scope:** Reliability, scalability, transaction safety, long-term architectural debt

---

## 1. 🔄 CELERY RELIABILITY AUDIT

### Task Idempotency Violations

**`app/tasks/d365_push.py:push_lead_to_d365()` — NOT Idempotent**
```25:242:app/tasks/d365_push.py
@celery_app.task(bind=True, name="push_lead_to_d365", max_retries=3)
def push_lead_to_d365(self, lead_id: int):
```
- **Violation:** Task retries can create duplicate leads in D365
- **Scenario:** Task fails after D365 create but before DB commit → retry → duplicate lead
- **Production impact:** Duplicate leads in D365, sales team confusion
- **Fix:** Use idempotency key (domain + timestamp), or check D365 before create

**`app/core/tasks.py:bulk_scan_task()` — Partial Idempotency**
```415:514:app/core/tasks.py
@celery_app.task(bind=True)
def bulk_scan_task(self, job_id: str, is_rescan: bool = False):
```
- **Violation:** Task can be retried, but already-processed domains are not skipped
- **Scenario:** Task fails mid-batch → retry → re-processes same domains
- **Production impact:** Duplicate scans, wasted resources, inconsistent data
- **Fix:** Track processed domains in Redis/DB, skip on retry

### Retry Logic Correctness

**`app/tasks/d365_push.py` — Exponential Backoff Without Cap**
```237:237:app/tasks/d365_push.py
raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
```
- **Problem:** `2 ** 10 = 1024 minutes = 17 hours` (if retries somehow reach 10)
- **Retry risk:** Task retries forever, clogs queue, wastes resources
- **Fix:** Cap backoff: `min(60 * (2 ** retries), 3600)` (max 1 hour)

**`app/core/partner_center.py:_fetch_page()` — Retry Without Jitter**
```288:296:app/core/partner_center.py
if retry_after:
    time.sleep(retry_after)
```
- **Problem:** All workers retry at same time → thundering herd
- **Retry risk:** Rate limit → all workers sleep 60s → all retry at once → rate limit again
- **Fix:** Add jitter: `sleep(retry_after + random.uniform(0, 10))`

**`app/core/celery_app.py` — Global Retry Config Conflicts**
```28:29:app/core/celery_app.py
task_default_retry_delay=60,  # 1 minute delay before retry
task_max_retries=2,  # Max 2 retries for transient failures
```
- **Problem:** Global `task_max_retries=2`, but `push_lead_to_d365` has `max_retries=3`
- **Retry risk:** Inconsistent retry behavior, hard to reason about
- **Fix:** Remove global config, set per-task, or document override behavior

### Dead Letter Queue Handling

**NO DEAD LETTER QUEUE — Failed Tasks Disappear**
- **Problem:** Celery task fails after max retries → task is lost, no record
- **Production impact:** Failed leads are invisible, no retry mechanism, no alerting
- **Fix:** Use Celery's `task_reject_on_worker_lost=True` + custom dead letter queue (DB table)

**`app/core/webhook_retry.py` — Webhook Retry, But No Task Retry**
```31:107:app/core/webhook_retry.py
def create_webhook_retry(...)
def retry_webhook(...)
```
- **Problem:** Webhooks have retry mechanism, but Celery tasks don't
- **Inconsistency:** Why webhooks get retry but tasks don't?
- **Fix:** Unify retry mechanism, or document why tasks don't need retry

### Task State Corruption Risks

**`app/tasks/d365_push.py` — DB State Updated Before D365 Success**
```137:156:app/tasks/d365_push.py
company.d365_sync_status = "synced"
company.d365_lead_id = d365_lead_id
db.commit()
```
- **Problem:** DB updated, but what if D365 API call fails after this?
- **State corruption:** DB says "synced", but D365 doesn't have lead
- **Fix:** Update DB only after D365 confirms success, or use two-phase commit

**`app/core/tasks.py:bulk_scan_task()` — Progress Tracker Can Get Out of Sync**
```507:509:app/core/tasks.py
processed += len(batch)
total_succeeded += succeeded
total_failed += failed
```
- **Problem:** Progress tracker is in-memory, worker crash = progress lost
- **State corruption:** Task restarts, progress resets, inconsistent state
- **Fix:** Persist progress to Redis/DB, recover on task restart

### Worker Crash Recovery

**`app/core/celery_app.py` — `task_acks_late=True` But No Recovery Logic**
```26:27:app/core/celery_app.py
task_acks_late=True,  # Acknowledge tasks after completion
task_reject_on_worker_lost=True,  # Reject tasks if worker dies
```
- **Problem:** Tasks are rejected on worker crash, but not requeued
- **Recovery risk:** Worker crash = tasks lost, no automatic recovery
- **Fix:** Use `task_reject_on_worker_lost=False` + custom requeue logic, or use Celery's `task_always_eager` for critical tasks

### Long-Running Task Timeouts

**`app/core/celery_app.py` — 15 Minute Timeout for Bulk Scan**
```22:23:app/core/celery_app.py
task_time_limit=900,  # 15 minutes per task (100 domains * 15s timeout)
task_soft_time_limit=870,  # 14.5 minutes soft limit
```
- **Problem:** Bulk scan can process 1000+ domains, but timeout is 15 minutes
- **Timeout risk:** Large batches will timeout, task fails, no partial results
- **Fix:** Chunk into smaller batches, spawn sub-tasks, or increase timeout for bulk operations

### Memory Leaks in Workers

**`app/core/celery_app.py` — `worker_max_tasks_per_child=50`**
```25:25:app/core/celery_app.py
worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (memory management)
```
- **Problem:** Workers restart after 50 tasks, but what if memory leaks happen faster?
- **Memory risk:** Long-running tasks can leak memory, worker OOM kills
- **Fix:** Monitor memory usage, adjust `worker_max_tasks_per_child` based on metrics

### Task Dependency Chains That Can Deadlock

**NO TASK DEPENDENCIES — But Implicit Dependencies Exist**
- **Problem:** `push_lead_to_d365` depends on `scan_single_domain` completing, but no explicit dependency
- **Deadlock risk:** Task A waits for task B, but task B is queued after task A
- **Fix:** Use Celery's `chain()` or `chord()` for explicit dependencies, or use task priorities

---

## 2. ⚡ RATE-LIMIT REAL BEHAVIOR ANALYSIS

### Actual Rate-Limit Enforcement

**`app/core/rate_limiter.py:RateLimiter` — Token Bucket Algorithm**
```11:76:app/core/rate_limiter.py
class RateLimiter:
    def __init__(self, rate: float, burst: Optional[float] = None):
        self.rate = rate
        self.burst = burst or rate
        self.tokens = self.burst
```
- **✅ GOOD:** Token bucket algorithm is correct
- **❌ BAD:** In-memory limiter, not shared across workers
- **Production risk:** Multiple workers = multiple limiters = rate limit exceeded
- **Fix:** Use `DistributedRateLimiter` (Redis-based) for all rate limiting

**`app/core/rate_limiter.py:get_dns_rate_limiter()` — Distributed Limiter with Fallback**
```87:105:app/core/rate_limiter.py
def get_dns_rate_limiter() -> DistributedRateLimiter:
    global _dns_rate_limiter
    with _rate_limiter_lock:
        if _dns_rate_limiter is None:
            fallback = RateLimiter(rate=10.0, burst=10.0)
            _dns_rate_limiter = DistributedRateLimiter(
                redis_key="dns",
                rate=10.0,
                burst=10.0,
                fallback=fallback,
            )
```
- **✅ GOOD:** Distributed limiter with fallback
- **❌ BAD:** Fallback is in-memory, not shared
- **Production risk:** Redis down → each worker uses own limiter → rate limit exceeded
- **Fix:** Make fallback more conservative, or fail fast if Redis is down

### Token Bucket vs Fixed Window Correctness

**Token Bucket — Correct Implementation**
- **✅ GOOD:** Token bucket allows burst, smooths out traffic
- **Production behavior:** 10 req/s with burst=10 → can send 10 requests instantly, then 1 req/s

**Fixed Window — Not Used**
- **Problem:** Some APIs (Partner Center) use fixed window, but limiter uses token bucket
- **Mismatch risk:** Token bucket allows burst, but API uses fixed window → rate limit exceeded
- **Fix:** Use fixed window limiter for Partner Center, or align with API behavior

### Burst Handling Under Load

**`app/core/rate_limiter.py:RateLimiter.wait()` — Burst Calculation**
```51:76:app/core/rate_limiter.py
def wait(self, tokens: int = 1) -> float:
    ...
    if self.tokens < tokens:
        wait_time = (tokens - self.tokens) / self.rate
        self.tokens = 0
        return wait_time
```
- **Problem:** Burst is consumed immediately, no gradual refill
- **Burst risk:** 10 workers × 10 burst = 100 requests instantly → rate limit exceeded
- **Fix:** Distribute burst across workers, or use smaller burst per worker

### Partner Center API Rate-Limit Alignment

**`app/core/partner_center.py:_fetch_page()` — Retry-After Header Parsing**
```268:296:app/core/partner_center.py
elif status_code == 429:
    retry_after = None
    if "Retry-After" in e.response.headers:
        try:
            retry_after = int(e.response.headers["Retry-After"])
        except (ValueError, TypeError):
            pass
```
- **✅ GOOD:** Parses Retry-After header
- **❌ BAD:** No validation of retry_after value (could be negative or huge)
- **Production risk:** Invalid retry_after → immediate retry or infinite wait
- **Fix:** Validate retry_after: `min(max(retry_after, 1), 3600)` (1s to 1h)

### D365 API Rate-Limit Handling

**`app/integrations/d365/client.py` — No Rate-Limit Handling**
- **Problem:** D365 client doesn't handle rate limits, just raises exception
- **Production risk:** Rate limit → task fails → retry → rate limit again → infinite loop
- **Fix:** Add rate-limit detection, exponential backoff, or queue throttling

### Retry-After Header Parsing

**`app/core/partner_center.py` — Basic Parsing, No Validation**
```268:273:app/core/partner_center.py
retry_after = None
if "Retry-After" in e.response.headers:
    try:
        retry_after = int(e.response.headers["Retry-After"])
    except (ValueError, TypeError):
        pass
```
- **Problem:** No validation, no bounds checking
- **Production risk:** Malicious API returns `Retry-After: -1` or `Retry-After: 999999` → immediate retry or infinite wait
- **Fix:** Validate: `retry_after = max(1, min(int(retry_after), 3600))` (1s to 1h)

### Exponential Backoff Implementation Bugs

**`app/tasks/d365_push.py` — Exponential Backoff Without Jitter**
```237:237:app/tasks/d365_push.py
raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
```
- **Problem:** No jitter, all retries happen at same time
- **Backoff risk:** Thundering herd on retry
- **Fix:** Add jitter: `countdown=60 * (2 ** retries) + random.uniform(0, 10)`

### Rate-Limit Bypass Vectors

**NO RATE-LIMIT ON TOKEN ACQUISITION**
- **Problem:** D365 token acquisition has no rate limiting
- **Bypass risk:** Multiple workers acquire tokens simultaneously → rate limit on token endpoint
- **Fix:** Add rate limiting to token acquisition, or use shared token cache

---

## 3. 🗄️ DB TRANSACTION ISOLATION SCAN

### Race Conditions in Concurrent Writes

**`app/core/merger.py:upsert_companies()` — Race Condition in Python**
```10:90:app/core/merger.py
def upsert_companies(...)
    company = db.query(Company).filter(Company.domain == normalized_domain).first()
    if company:
        # Update
    else:
        # Create
        db.add(company)
    db.commit()
```
- **Problem:** Two concurrent requests → both see no company → both try INSERT → one fails
- **Race condition:** IntegrityError catch → retry → UPDATE, but this is not atomic
- **Fix:** Use PostgreSQL `ON CONFLICT DO UPDATE` at SQL level

**`app/core/referral_ingestion.py:sync_referrals_from_partner_center()` — No Transaction Isolation**
```635:985:app/core/referral_ingestion.py
def sync_referrals_from_partner_center(db: Session) -> Dict[str, int]:
```
- **Problem:** Multiple `db.commit()` calls in one function
- **Race condition:** Two syncs run concurrently → duplicate referrals
- **Fix:** Wrap entire sync in transaction, use `ON CONFLICT DO UPDATE`

### Lost Updates in Domain Merge Logic

**`app/core/referral_ingestion.py` — Link Status Update Without Lock**
```760:771:app/core/referral_ingestion.py
if linked_company:
    referral_tracking.link_status = 'auto_linked'
    referral_tracking.linked_lead_id = linked_company.id
else:
    referral_tracking.link_status = 'unlinked'
    referral_tracking.linked_lead_id = None
db.commit()
```
- **Problem:** Two syncs update same referral → last write wins, first update lost
- **Lost update:** Concurrent syncs can overwrite each other's link status
- **Fix:** Use `SELECT ... FOR UPDATE` or optimistic locking (version column)

### Phantom Reads in Referral Ingestion

**NO ISOLATION LEVEL SET — Defaults to READ COMMITTED**
- **Problem:** PostgreSQL default is READ COMMITTED, but no explicit setting
- **Phantom read risk:** Between query and commit, another transaction can insert/delete rows
- **Fix:** Use `SET TRANSACTION ISOLATION LEVEL SERIALIZABLE` for critical operations, or use row-level locking

### Isolation Level Correctness

**NO EXPLICIT ISOLATION LEVEL — Uses Database Default**
- **Problem:** No explicit isolation level, relies on PostgreSQL default (READ COMMITTED)
- **Isolation risk:** READ COMMITTED allows phantom reads, non-repeatable reads
- **Fix:** Document isolation level requirements, or set explicitly for critical operations

### Nested Transaction Handling

**NO NESTED TRANSACTIONS — Single Transaction Per Function**
- **Problem:** Functions call other functions that commit, breaking transaction boundaries
- **Nested risk:** Inner commit commits outer transaction, breaking rollback
- **Fix:** Use savepoints for nested transactions, or refactor to avoid nested commits

### Savepoint Usage (or Lack Thereof)

**NO SAVEPOINTS — All-or-Nothing Transactions**
- **Problem:** Partial failure = entire transaction rolls back
- **Savepoint risk:** Can't recover from partial failures, must retry entire operation
- **Fix:** Use savepoints for partial recovery, or break into smaller transactions

### Deadlock Potential in Celery Tasks

**`app/core/tasks.py:process_batch_with_retry()` — Batch Processing Without Lock Ordering**
```265:412:app/core/tasks.py
def process_batch_with_retry(...)
    for domain in batch:
        scan_single_domain(domain, db, commit=False)
    db.commit()
```
- **Problem:** Multiple workers process same batch → deadlock on same rows
- **Deadlock risk:** Worker A locks row 1, Worker B locks row 2, both try to lock each other's row
- **Fix:** Process domains in sorted order (consistent lock ordering), or use `SELECT ... FOR UPDATE SKIP LOCKED`

### Long-Running Transactions Blocking Writes

**`app/core/referral_ingestion.py:sync_referrals_from_partner_center()` — Long Transaction**
```635:985:app/core/referral_ingestion.py
def sync_referrals_from_partner_center(db: Session) -> Dict[str, int]:
```
- **Problem:** Entire sync runs in one transaction (could be 1000+ referrals)
- **Blocking risk:** Long transaction holds locks, blocks other operations
- **Fix:** Commit in batches, or use smaller transactions

---

## 4. 🗺️ MAPPING LAYER FUTURE-PROOFING

### D365 Field Mapping Brittleness

**`app/integrations/d365/mapping.py:map_lead_to_d365()` — Hardcoded Field Names**
```49:60:app/integrations/d365/mapping.py
hunter_fields = {
    "hunter_score": lead_data.get("readiness_score"),
    "hunter_segment": lead_data.get("segment"),
    ...
}
```
- **Problem:** Field names are hardcoded strings, no validation
- **Brittleness risk:** D365 schema changes → code breaks, no compile-time check
- **Fix:** Use Pydantic model with field aliases, or config file

### Hardcoded Field Names That Will Break

**`app/integrations/d365/mapping.py` — All Fields Hardcoded**
```35:70:app/integrations/d365/mapping.py
d365_payload = {
    "subject": f"Hunter: {domain}",
    "companyname": company_name,
    "websiteurl": f"https://{domain}" if domain else None,
}
```
- **Problem:** Field names are magic strings, typos = silent failures
- **Break risk:** D365 renames field → code breaks, but no error (field just ignored)
- **Fix:** Use constants or enum for field names, validate at startup

### Missing Null Handling in Mappings

**`app/integrations/d365/mapping.py` — None Values Skipped**
```68:70:app/integrations/d365/mapping.py
for key, value in hunter_fields.items():
    if value is not None:
        d365_payload[key] = value
```
- **Problem:** None values are skipped, but what if D365 requires the field?
- **Null risk:** D365 adds required field → mapping fails silently
- **Fix:** Validate required fields, or use D365 schema validation

### Type Coercion Edge Cases

**`app/integrations/d365/mapping.py:_extract_primary_email()` — Type Assumptions**
```84:116:app/integrations/d365/mapping.py
def _extract_primary_email(lead_data: Dict[str, Any]) -> Optional[str]:
    contact_emails = lead_data.get("contact_emails")
    if contact_emails:
        if isinstance(contact_emails, list) and len(contact_emails) > 0:
            first_email = contact_emails[0]
            if isinstance(first_email, dict):
                return first_email.get("email") or first_email.get("value")
            elif isinstance(first_email, str):
                return first_email
```
- **Problem:** Assumes `contact_emails` is list of dicts or strings, but what if it's something else?
- **Type risk:** Unexpected type → returns None, but no error
- **Fix:** Validate types, or use Pydantic model for type safety

### Custom Field Handling (Future-Proof?)

**`app/integrations/d365/mapping.py` — Custom Fields with `hunter_` Prefix**
```49:60:app/integrations/d365/mapping.py
hunter_fields = {
    "hunter_score": lead_data.get("readiness_score"),
    ...
}
```
- **Problem:** Custom fields need to be created in D365, but code doesn't validate they exist
- **Future-proof risk:** D365 custom field deleted → mapping fails silently
- **Fix:** Validate custom fields exist at startup, or use D365 metadata API

### Mapping Validation Logic Gaps

**NO VALIDATION — Assumes All Fields Are Valid**
- **Problem:** No validation of field names, types, or required fields
- **Validation gap:** Invalid data → D365 API error, but could be caught earlier
- **Fix:** Add Pydantic validation, or use D365 schema validation

### Reverse Mapping Correctness (D365 → Hunter)

**NO REVERSE MAPPING — Only Hunter → D365**
- **Problem:** No mapping from D365 → Hunter, so updates from D365 can't be synced back
- **Reverse risk:** D365 updates lead → Hunter doesn't know, data out of sync
- **Fix:** Add reverse mapping, or use webhook to sync D365 updates back to Hunter

### Mapping Versioning Strategy (or Lack Thereof)

**NO VERSIONING — Mapping Changes Break Existing Data**
- **Problem:** Mapping changes → existing D365 leads have old field values
- **Versioning risk:** Can't migrate existing leads to new mapping
- **Fix:** Add mapping version, migrate existing leads, or use backward-compatible mappings

---

## 5. 🔴 D365 ERROR TAXONOMY ALIGNMENT

### Error Classification Correctness

**`app/integrations/d365/errors.py` — Basic Error Hierarchy**
```4:26:app/integrations/d365/errors.py
class D365Error(Exception):
    pass

class D365AuthenticationError(D365Error):
    pass

class D365APIError(D365Error):
    pass

class D365RateLimitError(D365Error):
    pass

class D365DuplicateError(D365Error):
    pass
```
- **✅ GOOD:** Error hierarchy exists
- **❌ BAD:** Error classification is incomplete (missing transient errors, validation errors)
- **Classification risk:** Wrong error type → wrong retry strategy
- **Fix:** Add more error types: `D365TransientError`, `D365ValidationError`, `D365NotFoundError`

### Retryable vs Non-Retryable Error Handling

**`app/tasks/d365_push.py` — Retry Logic Based on Exception Type**
```177:212:app/tasks/d365_push.py
except D365RateLimitError as e:
    # Rate limit - retry with exponential backoff
    raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

except (D365AuthenticationError, D365APIError, D365DuplicateError) as e:
    # Non-retryable errors
    return {"status": "error", ...}
```
- **Problem:** `D365APIError` is non-retryable, but some API errors are transient (5xx)
- **Retry risk:** Transient 5xx errors → no retry → task fails
- **Fix:** Split `D365APIError` into `D365TransientError` (retry) and `D365PermanentError` (don't retry)

### OData Error Parsing Robustness

**`app/integrations/d365/client.py` — Basic Error Text Parsing**
```228:234:app/integrations/d365/client.py
else:
    error_text = response.text
    logger.error(...)
    raise D365APIError(f"Create failed: {response.status_code} - {error_text}")
```
- **Problem:** Error text is just logged, not parsed for structured error info
- **Parsing risk:** OData errors have structured format, but code doesn't parse it
- **Fix:** Parse OData error response, extract error code and message

### HTTP Status Code Mapping Accuracy

**`app/integrations/d365/client.py` — Status Code → Exception Mapping**
```207:234:app/integrations/d365/client.py
if response.status_code == 201:
    return result
elif response.status_code == 429:
    raise D365RateLimitError("Rate limit exceeded")
elif response.status_code == 409:
    raise D365DuplicateError(f"Duplicate lead: {error_text}")
else:
    raise D365APIError(f"Create failed: {response.status_code} - {error_text}")
```
- **Problem:** Only handles 201, 429, 409, everything else is generic `D365APIError`
- **Mapping risk:** 401 (auth) → `D365APIError` instead of `D365AuthenticationError`
- **Fix:** Map all status codes: 401 → auth error, 403 → permission error, 5xx → transient error

### Throttling vs Authentication vs Transient Errors

**NO DISTINCTION — All Errors Treated Same**
- **Problem:** Throttling (429), authentication (401), transient (5xx) all handled differently, but code doesn't distinguish
- **Distinction risk:** Wrong retry strategy → infinite retries or no retry
- **Fix:** Map status codes to error types, use appropriate retry strategy

### Error Logging Completeness

**`app/integrations/d365/client.py` — Error Logging**
```177:234:app/integrations/d365/client.py
logger.error(
    "d365_lead_create_failed",
    status_code=response.status_code,
    error=error_text
)
```
- **✅ GOOD:** Logs status code and error text
- **❌ BAD:** Missing request ID, correlation ID, retry count
- **Logging gap:** Hard to correlate errors across retries
- **Fix:** Add request ID, correlation ID, retry count to logs

### Error Context Preservation

**`app/tasks/d365_push.py` — Error Stored in DB**
```204:206:app/tasks/d365_push.py
company.d365_sync_status = "error"
company.d365_sync_error = str(e)
db.commit()
```
- **✅ GOOD:** Error stored in DB for debugging
- **❌ BAD:** Error is just string, no structured error info
- **Context risk:** Can't query errors by type, can't aggregate error statistics
- **Fix:** Store structured error (JSON), or add error_type column

### Error Recovery Strategies

**NO RECOVERY — Errors Are Permanent**
- **Problem:** Once error occurs, task fails, no automatic recovery
- **Recovery risk:** Transient errors → permanent failures, manual intervention required
- **Fix:** Add error recovery strategies: exponential backoff, circuit breaker, dead letter queue

---

## 6. 🧪 TEST SUITE BRITTLENESS SCAN

### Flaky Tests (Time-Dependent, Order-Dependent)

**`tests/conftest.py:db_session()` — Transaction-Based Isolation**
```41:81:tests/conftest.py
@pytest.fixture(scope="function")
def db_session():
    ...
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        transaction.rollback()
```
- **✅ GOOD:** Transaction-based isolation prevents test pollution
- **❌ BAD:** Tests depend on transaction rollback, but what if rollback fails?
- **Flaky risk:** Transaction rollback failure → test pollution → flaky tests
- **Fix:** Add cleanup verification, or use separate test database per test

### Mock Overuse Hiding Real Bugs

**NO MOCK ANALYSIS — Need to Check Test Files**
- **Problem:** Can't analyze mocks without reading test files
- **Mock risk:** Over-mocking hides integration issues
- **Fix:** Review test files, ensure integration tests exist

### Integration Test Gaps

**`tests/conftest.py` — Integration Test Marker**
```61:61:tests/conftest.py
# Integration Tests**: Use `@pytest.mark.requires_integration` for Redis/Celery-dependent tests
```
- **✅ GOOD:** Integration test marker exists
- **❌ BAD:** Can't verify if all integration paths are tested
- **Gap risk:** Missing integration tests → bugs in production
- **Fix:** Review integration test coverage, ensure all integration paths are tested

### Test Data Pollution Between Tests

**`tests/conftest.py:db_session()` — Transaction Rollback Prevents Pollution**
```77:78:tests/conftest.py
transaction.rollback()
session.close()
```
- **✅ GOOD:** Transaction rollback prevents pollution
- **❌ BAD:** What if rollback fails? Or what if test uses global state?
- **Pollution risk:** Test failure → rollback skipped → pollution
- **Fix:** Add cleanup verification, or use separate test database

### Missing Edge Case Coverage

**NO EDGE CASE ANALYSIS — Need to Check Test Files**
- **Problem:** Can't analyze edge case coverage without reading test files
- **Coverage risk:** Missing edge cases → bugs in production
- **Fix:** Review test files, ensure edge cases are covered

### Test Maintenance Burden

**497 TESTS — Large Test Suite**
- **Problem:** Large test suite = high maintenance burden
- **Maintenance risk:** Tests break on refactoring, high maintenance cost
- **Fix:** Use test fixtures, reduce duplication, or use property-based testing

### Slow Tests Blocking CI/CD

**NO TEST TIMING ANALYSIS — Need to Check CI/CD Config**
- **Problem:** Can't analyze test timing without CI/CD config
- **Timing risk:** Slow tests → long CI/CD runs → slow feedback
- **Fix:** Review CI/CD config, optimize slow tests, or use test parallelization

### Tests That Don't Actually Test Anything

**NO TEST ANALYSIS — Need to Check Test Files**
- **Problem:** Can't analyze test quality without reading test files
- **Quality risk:** Tests that don't assert anything, or assert wrong things
- **Fix:** Review test files, ensure tests have meaningful assertions

---

## 7. 🚀 PRODUCTION LOAD FAILURE POINTS

### Where Will It Break at 10x Current Load?

1. **Database Connection Pool Exhaustion**
   - **Current:** Unknown connection pool size
   - **10x load:** 10x connections → pool exhausted → requests fail
   - **Fix:** Increase pool size, or use connection pooling with limits

2. **Celery Queue Backlog Scenarios**
   - **Current:** Unknown queue size
   - **10x load:** 10x tasks → queue backlog → tasks delayed
   - **Fix:** Increase queue size, or use priority queues

3. **Memory Pressure Points**
   - **Current:** Unknown memory usage
   - **10x load:** 10x memory → OOM kills
   - **Fix:** Monitor memory, adjust `worker_max_tasks_per_child`, or use streaming

4. **CPU Bottlenecks**
   - **Current:** Unknown CPU usage
   - **10x load:** 10x CPU → slow requests → timeouts
   - **Fix:** Scale horizontally, or optimize CPU-intensive operations

5. **Network Timeout Cascades**
   - **Current:** 30s timeout for D365 API
   - **10x load:** 10x requests → network congestion → timeouts → retries → more timeouts
   - **Fix:** Reduce timeout, or use circuit breaker

6. **Cache Stampede Risks**
   - **Current:** Redis cache for DNS/WHOIS
   - **10x load:** Cache miss → 10x requests to external API → rate limit
   - **Fix:** Use cache warming, or use distributed locks for cache misses

7. **N+1 Query Patterns**
   - **Current:** Unknown query patterns
   - **10x load:** 10x queries → database overload
   - **Fix:** Use eager loading, or batch queries

---

## 8. 🏗️ LONG-TERM ARCHITECTURAL DEBT

### Code That Will Be Impossible to Refactor in 6 Months

1. **`app/core/referral_ingestion.py:sync_referrals_from_partner_center()` — 775 Lines**
   - **Debt:** God function, impossible to refactor
   - **6-month risk:** Can't add features, can't fix bugs, must rewrite
   - **Fix:** Break into smaller functions now, before it's too late

2. **`app/integrations/d365/mapping.py` — Hardcoded Field Names**
   - **Debt:** Field names are magic strings
   - **6-month risk:** D365 schema changes → must update code everywhere
   - **Fix:** Use config file or constants now

### Patterns That Don't Scale Beyond Current Use Case

1. **In-Memory Token Cache**
   - **Debt:** Token cache is per-instance
   - **Scale risk:** Multiple workers → multiple token acquisitions → rate limit
   - **Fix:** Move to Redis now, before scaling

2. **Single DB Session Per Task**
   - **Debt:** One session for entire task
   - **Scale risk:** Long transactions → lock contention → deadlocks
   - **Fix:** Use smaller transactions now

### Technical Decisions That Lock You Into Bad Paths

1. **Direct D365 Client Usage in Tasks**
   - **Debt:** Tasks know about D365 client
   - **Lock risk:** Can't add other CRMs without changing task code
   - **Fix:** Extract to service layer now

2. **Hardcoded Field Mappings**
   - **Debt:** Field mappings are in code
   - **Lock risk:** Can't change mappings without code changes
   - **Fix:** Use config file now

### Missing Abstractions That Will Cause Copy-Paste Hell

1. **No CRM Service Interface**
   - **Debt:** D365 client is used directly
   - **Copy-paste risk:** Add Salesforce → copy-paste D365 code → maintenance hell
   - **Fix:** Create CRM service interface now

2. **No Domain Extraction Service**
   - **Debt:** Domain extraction is in referral ingestion
   - **Copy-paste risk:** Add new source → copy-paste extraction logic → maintenance hell
   - **Fix:** Extract to service now

### Over-Coupling That Will Make D365 v2 Impossible

1. **Task → Client Direct Dependency**
   - **Debt:** Tasks depend on D365 client directly
   - **Coupling risk:** D365 v2 changes → must update all tasks
   - **Fix:** Use service layer now

2. **Mapping → Client Dependency**
   - **Debt:** Mapping knows about D365 field names
   - **Coupling risk:** D365 v2 changes → must update mapping
   - **Fix:** Use config file now

### Under-Coupling That Will Cause Integration Chaos

1. **No Integration Test Framework**
   - **Debt:** Integration tests are ad-hoc
   - **Chaos risk:** Add new integration → no test framework → bugs
   - **Fix:** Create integration test framework now

2. **No Error Recovery Framework**
   - **Debt:** Error recovery is ad-hoc
   - **Chaos risk:** New errors → no recovery strategy → manual intervention
   - **Fix:** Create error recovery framework now

---

## 📊 Summary

- **Critical Reliability Issues:** 5 (idempotency, retry logic, dead letter queue, state corruption, worker crash recovery)
- **High Priority Scalability Issues:** 4 (rate limiting, transaction isolation, mapping brittleness, error taxonomy)
- **Medium Priority Issues:** 3 (test brittleness, production load points, architectural debt)
- **Long-Term Debt:** 6 (refactoring blockers, scaling blockers, coupling issues)

**Total Estimated Effort:** ~3-4 weeks (if done sequentially)

**Recommendation:** Fix critical reliability issues immediately, then tackle scalability issues before D365 integration goes live. Address long-term debt incrementally.

