# Partner Center Phase 2 - Background Sync UAT (Eksiksiz Kapanış)

**Date**: 2025-01-30  
**Environment**: Docker (Development)  
**Feature Flag**: `HUNTER_PARTNER_CENTER_ENABLED=true` (temporary for UAT)  
**Goal**: Verify Background Sync, Idempotency, Celery Beat Schedule

---

## 🎯 UAT Goals

1. ✅ Verify manual sync works (API endpoint)
2. ✅ Verify Celery task execution
3. ✅ Verify idempotent behavior (no duplicates on re-run)
4. ✅ Verify Celery Beat schedule triggers tasks
5. ✅ Verify logging and error handling
6. ✅ Verify database state after sync

---

## 📋 Pre-UAT Setup

### 1. Environment Configuration

```bash
# Enable feature flag for UAT
export HUNTER_PARTNER_CENTER_ENABLED=true
export HUNTER_PARTNER_CENTER_CLIENT_ID=<your-client-id>
export HUNTER_PARTNER_CENTER_TENANT_ID=<your-tenant-id>
# Note: CLIENT_SECRET not needed for Device Code Flow

# Restart API and Worker containers
docker-compose restart api worker
```

### 2. Verify Services

```bash
# Check all services
docker-compose ps

# Check API health
curl http://localhost:8000/healthz

# Check worker logs
docker-compose logs worker | tail -20
```

---

## 🧪 UAT Test Scenarios

### Test 1: Manual Sync via API Endpoint

**Goal**: Verify manual sync endpoint works

```bash
# Test sync endpoint
curl -X POST http://localhost:8000/api/referrals/sync \
  -H "Content-Type: application/json"

# Expected: 200 OK with task_id
# Response: {"task_id": "...", "status": "queued"}

# Check worker logs
docker-compose logs worker | tail -50 | grep -i "sync\|referral"
```

**✅ Pass Criteria**: 
- Returns 200 with task_id
- Task appears in worker logs
- No errors in execution

---

### Test 2: Direct Celery Task Execution (Dry Run Simulation)

**Goal**: Verify task can be executed directly

```bash
# Execute task directly (simulate dry-run by checking logs)
docker-compose exec worker celery -A app.core.celery_app call app.core.tasks.sync_partner_center_referrals_task

# Or via Python shell
docker-compose exec api python -c "
from app.core.tasks import sync_partner_center_referrals_task
result = sync_partner_center_referrals_task.apply()
print(result.get())
"
```

**✅ Pass Criteria**: 
- Task executes without errors
- Structured logs present
- Sync statistics logged

---

### Test 3: Idempotency Test (CRITICAL)

**Goal**: Verify no duplicates on re-run

**Step 1: First Run**
```bash
# Trigger sync
curl -X POST http://localhost:8000/api/referrals/sync \
  -H "Content-Type: application/json"

# Wait for completion (check logs)
docker-compose logs -f worker

# Check database state
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
SELECT COUNT(*) as total_referrals, 
       COUNT(DISTINCT referral_id) as unique_referrals,
       COUNT(DISTINCT domain) as unique_domains
FROM partner_center_referrals;
"
```

**Step 2: Second Run (Idempotency Check)**
```bash
# Trigger sync again (should skip duplicates)
curl -X POST http://localhost:8000/api/referrals/sync \
  -H "Content-Type: application/json"

# Wait for completion
docker-compose logs -f worker

# Check database state (should be same or only new referrals)
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
SELECT COUNT(*) as total_referrals, 
       COUNT(DISTINCT referral_id) as unique_referrals,
       COUNT(DISTINCT domain) as unique_domains
FROM partner_center_referrals;
"
```

**✅ Pass Criteria**: 
- First run: N new referrals created
- Second run: 0 new referrals (or only genuinely new ones)
- No duplicate referral_id entries
- Logs show "skipped" or "already exists" messages

---

### Test 4: Celery Beat Schedule Verification

**Goal**: Verify background sync schedule is active

**Step 1: Check Schedule Configuration**
```bash
# Check Celery Beat schedule
docker-compose exec worker celery -A app.core.celery_app inspect scheduled

# Or check worker logs for beat schedule
docker-compose logs worker | grep -i "beat\|schedule"
```

**Step 2: Monitor Beat Execution (Wait 1-2 cycles)**
```bash
# Development: 30 seconds interval
# Production: 600 seconds (10 minutes) interval

# Monitor logs for scheduled task execution
docker-compose logs -f worker | grep -i "sync.*partner.*center\|referral"

# Wait for at least 1-2 cycles (30s dev, 600s prod)
# Expected: Task triggered automatically
```

**✅ Pass Criteria**: 
- Schedule shows `sync-partner-center-referrals` task
- Schedule interval: 30s (dev) or 600s (prod)
- Task triggered automatically after interval
- Logs show scheduled execution

---

### Test 5: Logging and Error Handling

**Goal**: Verify structured logging and error handling

```bash
# Check logs for structured data
docker-compose logs worker | grep -i "sync.*partner.*center" | tail -20

# Expected log structure:
# - source: "partner_center_sync"
# - duration: execution time
# - env: environment
# - feature_flag_state: enabled/disabled
# - sync statistics: new, updated, skipped counts
```

**✅ Pass Criteria**: 
- Structured logs present
- Duration logged
- Sync statistics logged
- Error handling graceful (no crashes)

---

### Test 6: Database State Verification

**Goal**: Verify referral data in database

```bash
# Check partner_center_referrals table
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
SELECT 
    referral_id,
    referral_type,
    domain,
    status,
    synced_at,
    created_at,
    updated_at
FROM partner_center_referrals
ORDER BY synced_at DESC
LIMIT 10;
"

# Check for duplicates
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
SELECT referral_id, COUNT(*) as count
FROM partner_center_referrals
GROUP BY referral_id
HAVING COUNT(*) > 1;
"

# Check leads_ready view includes referral_type
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
SELECT domain, referral_type
FROM leads_ready
WHERE referral_type IS NOT NULL
LIMIT 10;
"
```

**✅ Pass Criteria**: 
- Referral data present in table
- No duplicate referral_id entries
- leads_ready view includes referral_type
- Domain normalization correct

---

### Test 7: Feature Flag Protection

**Goal**: Verify feature flag blocks execution when disabled

```bash
# Disable feature flag
export HUNTER_PARTNER_CENTER_ENABLED=false
docker-compose restart api worker

# Test sync endpoint (should return 400)
curl -X POST http://localhost:8000/api/referrals/sync \
  -H "Content-Type: application/json"

# Expected: 400 Bad Request with error message

# Check worker logs (task should skip execution)
docker-compose logs worker | tail -20
```

**✅ Pass Criteria**: 
- API returns 400 when flag disabled
- Task skips execution when flag disabled
- Logs show feature flag check

---

## 🔍 Verification Commands

### Quick Status Check

```bash
# All services healthy
docker-compose ps

# API responding
curl http://localhost:8000/healthz

# Worker running
docker-compose logs worker | tail -5

# Database accessible
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "SELECT 1;"
```

### Monitor Sync Activity

```bash
# Watch worker logs
docker-compose logs -f worker

# Watch API logs
docker-compose logs -f api

# Check Celery task status
docker-compose exec worker celery -A app.core.celery_app inspect active

# Check scheduled tasks
docker-compose exec worker celery -A app.core.celery_app inspect scheduled
```

### Database Queries

```bash
# Count referrals
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
SELECT 
    COUNT(*) as total,
    COUNT(DISTINCT referral_id) as unique_ids,
    COUNT(DISTINCT domain) as unique_domains,
    referral_type,
    status
FROM partner_center_referrals
GROUP BY referral_type, status;
"

# Check latest sync
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
SELECT MAX(synced_at) as last_sync
FROM partner_center_referrals;
"
```

---

## 📊 UAT Results Template

```
Test 1: Manual Sync via API Endpoint
- Status: [ ] PASS [ ] FAIL
- Task ID: 
- Notes: 

Test 2: Direct Celery Task Execution
- Status: [ ] PASS [ ] FAIL
- Notes: 

Test 3: Idempotency Test
- First Run: [ ] PASS [ ] FAIL
  - New Referrals: 
  - Notes: 
- Second Run: [ ] PASS [ ] FAIL
  - New Referrals: 
  - Duplicates: [ ] YES [ ] NO
  - Notes: 

Test 4: Celery Beat Schedule
- Schedule Configuration: [ ] PASS [ ] FAIL
- Automatic Execution: [ ] PASS [ ] FAIL
- Interval: [ ] 30s (dev) [ ] 600s (prod)
- Notes: 

Test 5: Logging and Error Handling
- Structured Logs: [ ] PASS [ ] FAIL
- Error Handling: [ ] PASS [ ] FAIL
- Notes: 

Test 6: Database State Verification
- Referral Data: [ ] PASS [ ] FAIL
- No Duplicates: [ ] PASS [ ] FAIL
- leads_ready View: [ ] PASS [ ] FAIL
- Notes: 

Test 7: Feature Flag Protection
- API Block: [ ] PASS [ ] FAIL
- Task Skip: [ ] PASS [ ] FAIL
- Notes: 

Overall UAT Status: [ ] PASS [ ] FAIL
```

---

## 🚨 Rollback Plan

If UAT fails:

1. **Disable Feature Flag**
   ```bash
   export HUNTER_PARTNER_CENTER_ENABLED=false
   docker-compose restart api worker
   ```

2. **Check Logs**
   ```bash
   docker-compose logs api | tail -50
   docker-compose logs worker | tail -50
   ```

3. **Verify System Health**
   ```bash
   curl http://localhost:8000/healthz
   ```

4. **Clean Database (if needed)**
   ```bash
   # WARNING: Only if necessary
   docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
   DELETE FROM partner_center_referrals;
   "
   ```

---

## ✅ Post-UAT

After successful UAT:

1. **Disable Feature Flag** (return to MVP-safe state)
   ```bash
   export HUNTER_PARTNER_CENTER_ENABLED=false
   docker-compose restart api worker
   ```

2. **Document UAT Results**
   - Update this checklist with results
   - Note any issues found
   - Document any configuration changes needed

3. **Prepare for Merge + Tag**
   - All tests passing ✅
   - UAT successful ✅
   - Background sync verified ✅
   - Idempotency verified ✅
   - Ready for main merge + tag ✅

---

**Last Updated**: 2025-01-30  
**Status**: Ready for Background Sync UAT

