# Partner Center Phase 2 - UAT / Dry Run Checklist

**Date**: 2025-01-30  
**Environment**: Docker (Development)  
**Feature Flag**: `HUNTER_PARTNER_CENTER_ENABLED=true` (temporary for UAT)

---

## 🎯 UAT Goals

1. ✅ Verify API endpoint works (`POST /api/referrals/sync`)
2. ✅ Verify Celery task executes correctly
3. ✅ Verify Celery Beat schedule is active
4. ✅ Verify UI shows referral column with badges
5. ✅ Verify referral data appears in leads API
6. ✅ Verify error handling works (feature flag OFF)

---

## 📋 Pre-UAT Setup

### 1. Environment Configuration

```bash
# Check current feature flag status
docker-compose exec api env | grep PARTNER_CENTER

# Enable feature flag for UAT (temporary)
# Edit .env file or set environment variable
HUNTER_PARTNER_CENTER_ENABLED=true
HUNTER_PARTNER_CENTER_CLIENT_ID=<your-client-id>
HUNTER_PARTNER_CENTER_TENANT_ID=<your-tenant-id>
# Note: CLIENT_SECRET not needed for Device Code Flow

# Restart API container to apply changes
docker-compose restart api
```

### 2. Verify Services

```bash
# Check all services are running
docker-compose ps

# Check API health
curl http://localhost:8000/healthz

# Check Celery worker
docker-compose logs worker | tail -20

# Check Celery Beat (if running separately)
# Note: Celery Beat runs in worker container by default
```

---

## 🧪 UAT Test Scenarios

### Test 1: Feature Flag Disabled (Default State)

**Goal**: Verify feature flag protection works

```bash
# Set feature flag to false
export HUNTER_PARTNER_CENTER_ENABLED=false
docker-compose restart api

# Test sync endpoint (should return 400)
curl -X POST http://localhost:8000/api/referrals/sync \
  -H "Content-Type: application/json"

# Expected: 400 Bad Request with error message
```

**✅ Pass Criteria**: Returns 400 with clear error message

---

### Test 2: Manual Sync Endpoint (Feature Flag Enabled)

**Goal**: Verify manual sync endpoint works

```bash
# Enable feature flag
export HUNTER_PARTNER_CENTER_ENABLED=true
docker-compose restart api

# Test sync endpoint
curl -X POST http://localhost:8000/api/referrals/sync \
  -H "Content-Type: application/json"

# Expected: 200 OK with task_id
# Response: {"task_id": "...", "status": "queued"}
```

**✅ Pass Criteria**: Returns 200 with task_id

---

### Test 3: Celery Task Execution

**Goal**: Verify Celery task processes correctly

```bash
# Check worker logs after sync
docker-compose logs worker | tail -50

# Check for task execution logs
# Expected: Structured logs with sync statistics
```

**✅ Pass Criteria**: 
- Task appears in worker logs
- Structured logging present
- No errors in task execution

---

### Test 4: Celery Beat Schedule

**Goal**: Verify background sync schedule is active

```bash
# Check Celery Beat schedule
docker-compose exec worker celery -A app.core.celery_app inspect scheduled

# Or check worker logs for beat schedule
docker-compose logs worker | grep "beat"

# Expected: sync-partner-center-referrals task in schedule
```

**✅ Pass Criteria**: 
- Schedule shows sync-partner-center-referrals task
- Schedule interval: 30s (dev) or 600s (prod)

---

### Test 5: Leads API with Referral Type

**Goal**: Verify referral_type field appears in leads API

```bash
# Test GET /leads endpoint
curl "http://localhost:8000/leads?page=1&page_size=10" | jq '.leads[0] | {domain, referral_type}'

# Test GET /leads/{domain} endpoint
curl "http://localhost:8000/leads/example.com" | jq '{domain, referral_type}'

# Expected: referral_type field present (null or "co-sell"/"marketplace"/"solution-provider")
```

**✅ Pass Criteria**: 
- referral_type field present in response
- null when no referral
- correct type when referral exists

---

### Test 6: UI Referral Column

**Goal**: Verify referral column appears in Mini UI

1. Open Mini UI: http://localhost:8000/mini-ui/
2. Check leads table for "Referral" column
3. Verify badge colors:
   - Co-sell: Blue badge
   - Marketplace: Green badge
   - Solution Provider: Orange badge
   - No referral: "-"

**✅ Pass Criteria**: 
- Referral column visible
- Badge colors correct
- Empty state shows "-"

---

### Test 7: Database Verification

**Goal**: Verify referral data in database

```bash
# Check partner_center_referrals table
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c \
  "SELECT referral_id, referral_type, domain, status, synced_at FROM partner_center_referrals LIMIT 10;"

# Check leads_ready view includes referral_type
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c \
  "SELECT domain, referral_type FROM leads_ready LIMIT 10;"
```

**✅ Pass Criteria**: 
- Referral data present in table
- leads_ready view includes referral_type column

---

## 🔍 Verification Commands

### Quick Health Check

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

### Check Feature Flag Status

```bash
# In API container
docker-compose exec api env | grep PARTNER_CENTER

# Or via API (if endpoint exists)
curl http://localhost:8000/healthz | jq '.partner_center_enabled'
```

### Monitor Sync Activity

```bash
# Watch worker logs
docker-compose logs -f worker

# Watch API logs
docker-compose logs -f api

# Check Celery task status
docker-compose exec worker celery -A app.core.celery_app inspect active
```

---

## 📊 UAT Results Template

```
Test 1: Feature Flag Disabled
- Status: [ ] PASS [ ] FAIL
- Notes: 

Test 2: Manual Sync Endpoint
- Status: [ ] PASS [ ] FAIL
- Notes: 

Test 3: Celery Task Execution
- Status: [ ] PASS [ ] FAIL
- Notes: 

Test 4: Celery Beat Schedule
- Status: [ ] PASS [ ] FAIL
- Notes: 

Test 5: Leads API with Referral Type
- Status: [ ] PASS [ ] FAIL
- Notes: 

Test 6: UI Referral Column
- Status: [ ] PASS [ ] FAIL
- Notes: 

Test 7: Database Verification
- Status: [ ] PASS [ ] FAIL
- Notes: 

Overall UAT Status: [ ] PASS [ ] FAIL
```

---

## 🚨 Rollback Plan

If UAT fails:

1. **Disable Feature Flag**
   ```bash
   export HUNTER_PARTNER_CENTER_ENABLED=false
   docker-compose restart api
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

---

## ✅ Post-UAT

After successful UAT:

1. **Disable Feature Flag** (return to MVP-safe state)
   ```bash
   export HUNTER_PARTNER_CENTER_ENABLED=false
   docker-compose restart api
   ```

2. **Document UAT Results**
   - Update this checklist with results
   - Note any issues found
   - Document any configuration changes needed

3. **Prepare for Merge**
   - All tests passing ✅
   - UAT successful ✅
   - Ready for main merge ✅

---

**Last Updated**: 2025-01-30  
**Status**: Ready for UAT

