# 🔥 Cursor ROAST Prompt — Hunter/D365 Edition (v1.1 PRO)

**Purpose:** Advanced, production-focused codebase audit with deep dives into reliability, scalability, and long-term maintainability.

**Usage:** Copy-paste this entire prompt into Cursor after v1.0 for deeper analysis.

---

## 🔥 "Hunter Codebase Roast & Hidden-Debt Audit — PRO Edition"

**Mode:** aggressive, production-SRE-level, future-proofing focus

**Goal:** identify reliability risks, scalability bottlenecks, transaction safety issues, and long-term architectural debt

**Context:** Hunter v1.0 core, Partner Center integration, Dynamics 365 adapter %94 completed, preparing for production scale

**Scope:** `app/`, `integrations/`, `tasks/`, `api/`, `core/`, migrations, tests, Celery workers, DB transactions, rate limiting

### 💣 Deliver these 8 outputs:

1. **Celery Reliability Audit:**
   - Task idempotency violations
   - Retry logic correctness
   - Dead letter queue handling
   - Task state corruption risks
   - Worker crash recovery
   - Long-running task timeouts
   - Memory leaks in workers
   - Task dependency chains that can deadlock

2. **Rate-Limit Real Behavior Analysis:**
   - Actual rate-limit enforcement (not just config)
   - Token bucket vs fixed window correctness
   - Burst handling under load
   - Partner Center API rate-limit alignment
   - D365 API rate-limit handling
   - Retry-after header parsing
   - Exponential backoff implementation bugs
   - Rate-limit bypass vectors

3. **DB Transaction Isolation Scan:**
   - Race conditions in concurrent writes
   - Lost updates in domain merge logic
   - Phantom reads in referral ingestion
   - Isolation level correctness (READ COMMITTED vs SERIALIZABLE)
   - Nested transaction handling
   - Savepoint usage (or lack thereof)
   - Deadlock potential in Celery tasks
   - Long-running transactions blocking writes

4. **Mapping Layer Future-Proofing:**
   - D365 field mapping brittleness
   - Hardcoded field names that will break
   - Missing null handling in mappings
   - Type coercion edge cases
   - Custom field handling (future-proof?)
   - Mapping validation logic gaps
   - Reverse mapping correctness (D365 → Hunter)
   - Mapping versioning strategy (or lack thereof)

5. **D365 Error Taxonomy Alignment:**
   - Error classification correctness
   - Retryable vs non-retryable error handling
   - OData error parsing robustness
   - HTTP status code mapping accuracy
   - Throttling vs authentication vs transient errors
   - Error logging completeness
   - Error context preservation
   - Error recovery strategies

6. **Test Suite Brittleness Scan:**
   - Flaky tests (time-dependent, order-dependent)
   - Mock overuse hiding real bugs
   - Integration test gaps
   - Test data pollution between tests
   - Missing edge case coverage
   - Test maintenance burden
   - Slow tests blocking CI/CD
   - Tests that don't actually test anything

7. **Production Load Failure Points:**
   - Where will it break at 10x current load?
   - Database connection pool exhaustion
   - Celery queue backlog scenarios
   - Memory pressure points
   - CPU bottlenecks
   - Network timeout cascades
   - Cache stampede risks
   - N+1 query patterns

8. **Long-Term Architectural Debt:**
   - Code that will be impossible to refactor in 6 months
   - Patterns that don't scale beyond current use case
   - Technical decisions that lock you into bad paths
   - Missing abstractions that will cause copy-paste hell
   - Over-coupling that will make D365 v2 impossible
   - Under-coupling that will cause integration chaos

### 🔧 Rules:

- No generic advice
- No "best practices" fluff
- No compliments
- Direct, harsh, specific
- Cite exact files + functions + line numbers
- Expose weak points with production scenarios
- Suggest only *surgical* improvements with ROI
- Include failure scenarios and recovery paths

### 🧠 Tone:

Production SRE who's seen 3am outages + senior architect who's refactored legacy codebases + cynical code reviewer who's been burned before.

### 🎯 Focus Areas:

1. **Reliability:** What will break in production and why?
2. **Scalability:** Where are the bottlenecks at 10x load?
3. **Maintainability:** What will be impossible to change in 6 months?
4. **Correctness:** What logic is subtly wrong?
5. **Observability:** What failures will be invisible?

---

## 📝 Notes

- **Created:** 2025-01-30
- **Version:** 1.1 PRO
- **Status:** Active
- **Prerequisite:** Run v1.0 first for general audit, then v1.1 PRO for deep dives
- **Use Case:** Before major production deployments, before D365 v2, before scaling to 10x load

