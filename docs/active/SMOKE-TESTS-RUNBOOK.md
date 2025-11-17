# Smoke Tests Runbook - Hunter v1.0

**Tarih**: 2025-01-28  
**Versiyon**: v1.0.0  
**Status**: 🔄 **IN PROGRESS** - Production hazırlık aktif  
**Süre**: 2 saat (operasyonel runbook)

---

## 🎯 Amaç

Production deployment sonrası kritik fonksiyonların çalıştığını doğrulamak:

- Core endpoints çalışıyor mu?
- Sales Engine çalışıyor mu?
- Bulk operations çalışıyor mu?
- Rate limiting ve cache çalışıyor mu?
- Error handling doğru mu?

---

## 7.1 Core Endpoints Test (30 dk)

### Health Endpoints

```bash
# Liveness
curl -i http://localhost:8000/healthz/live
# Expected: 200 OK

# Readiness
curl -i http://localhost:8000/healthz/ready
# Expected: 200 OK

# Startup
curl -i http://localhost:8000/healthz/startup
# Expected: 200 OK

# Metrics
curl -s http://localhost:8000/healthz/metrics | jq '.'
# Expected: JSON with metrics data
```

### Leads Endpoint

```bash
# Get leads list
curl -i "http://localhost:8000/api/v1/leads?limit=10"

# Expected: 200 OK
# Response: JSON array of leads

# With filters
curl -i "http://localhost:8000/api/v1/leads?provider=M365&limit=5"

# Expected: 200 OK
# Response: Filtered leads
```

### Scan Endpoint

```bash
# Single domain scan
curl -i -X POST "http://localhost:8000/api/v1/scan" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your-api-key>" \
  -d '{"domain": "example.com"}'

# Expected: 200 OK or 202 Accepted (if async)
# Response: Scan result or job ID
```

### Checklist

- [ ] `/healthz/live` returns 200
- [ ] `/healthz/ready` returns 200
- [ ] `/healthz/startup` returns 200
- [ ] `/healthz/metrics` returns valid JSON
- [ ] `/api/v1/leads` returns 200 with leads array
- [ ] `/api/v1/leads` with filters works
- [ ] `/api/v1/scan` accepts domain and returns result

---

## 7.2 Sales Engine Endpoint Test (30 dk)

### Sales Summary Endpoint

```bash
# Test with real domain (if exists in DB)
curl -i "http://localhost:8000/api/v1/leads/example.com/sales-summary"

# Expected: 200 OK
# Response: Sales summary JSON

# Test with non-existent domain
curl -i "http://localhost:8000/api/v1/leads/nonexistent-domain-12345.invalid/sales-summary"

# Expected: 404 Not Found
```

### Sales Summary Response Verification

**Expected Response Structure**:
```json
{
  "domain": "example.com",
  "one_liner": "...",
  "call_script": ["...", "..."],
  "discovery_questions": ["...", "..."],
  "offer_tier": "Basic|Pro|Enterprise",
  "opportunity_potential": 0-100,
  "urgency": "low|medium|high",
  "metadata": {
    "segment": "...",
    "priority": 0-100,
    "provider": "..."
  }
}
```

### Test with Different Segments

```bash
# Test Migration segment domain
curl -s "http://localhost:8000/api/v1/leads/<migration-domain>/sales-summary" | jq '.'

# Test Existing segment domain
curl -s "http://localhost:8000/api/v1/leads/<existing-domain>/sales-summary" | jq '.'

# Verify:
# - Migration: call_script mentions migration benefits
# - Existing: call_script mentions upsell/expansion
```

### Checklist

- [ ] Sales summary endpoint returns 200 for existing domain
- [ ] Sales summary endpoint returns 404 for non-existent domain
- [ ] Response contains all required fields (one_liner, call_script, etc.)
- [ ] Migration segment domains get migration-focused scripts
- [ ] Existing segment domains get upsell-focused scripts
- [ ] Offer tier recommendation is logical (Basic/Pro/Enterprise)

---

## 7.3 Bulk Scan Test (30 dk)

### Test Domain Set (10 domains)

**Create test file** (`tests/smoke_test_domains.txt`):
```
example.com
google.com
microsoft.com
github.com
stackoverflow.com
reddit.com
amazon.com
netflix.com
twitter.com
linkedin.com
```

### Bulk Scan Command

```bash
# Bulk scan with test domains
curl -i -X POST "http://localhost:8000/api/v1/scan/bulk" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your-api-key>" \
  -d @- << EOF
{
  "domains": [
    "example.com",
    "google.com",
    "microsoft.com",
    "github.com",
    "stackoverflow.com",
    "reddit.com",
    "amazon.com",
    "netflix.com",
    "twitter.com",
    "linkedin.com"
  ]
}
EOF

# Expected: 202 Accepted or 200 OK
# Response: Job ID or results
```

### Progress Tracking

```bash
# Get bulk scan progress (if async)
curl -s "http://localhost:8000/api/v1/progress/<job-id>" | jq '.'

# Expected: Progress status with completed/total counts
```

### Verification

```bash
# Wait for bulk scan to complete (check progress endpoint)
# Then verify domains are in database

# Check leads list includes scanned domains
curl -s "http://localhost:8000/api/v1/leads?limit=20" | jq '.[] | .domain' | grep -E "(example|google|microsoft)"

# Expected: At least some of the test domains appear
```

### Checklist

- [ ] Bulk scan accepts 10 domains
- [ ] Bulk scan returns job ID or results
- [ ] Progress tracking works (if async)
- [ ] At least 5/10 domains successfully scanned
- [ ] Scanned domains appear in leads list
- [ ] No critical errors in logs during bulk scan

---

## 7.4 Rate Limiting & Cache Test (30 dk)

### Rate Limiting Test

```bash
# Test DNS rate limiting (10 req/s)
for i in {1..15}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    "http://localhost:8000/api/v1/scan?domain=test${i}.com" &
done
wait

# Expected: First 10 requests succeed, next 5 may be rate limited (429)

# Test WHOIS rate limiting (5 req/s)
for i in {1..10}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    "http://localhost:8000/api/v1/scan?domain=test${i}.com" &
done
wait

# Expected: First 5 requests succeed, next 5 may be rate limited (429)
```

### Cache Test

```bash
# First request (cache miss)
time curl -s "http://localhost:8000/api/v1/scan?domain=cache-test.com" > /dev/null
# Note: Time taken

# Second request (cache hit - should be faster)
time curl -s "http://localhost:8000/api/v1/scan?domain=cache-test.com" > /dev/null
# Expected: Significantly faster (< 50% of first request time)

# Verify cache hit in metrics
curl -s "http://localhost:8000/healthz/metrics" | jq '.cache.hit_rate'
# Expected: hit_rate > 0 after second request
```

### Redis Cache Verification

```bash
# Check Redis keys
docker-compose exec redis redis-cli KEYS "dns:*"
docker-compose exec redis redis-cli KEYS "whois:*"
docker-compose exec redis redis-cli KEYS "scoring:*"

# Expected: Cache keys exist for scanned domains
```

### Checklist

- [ ] Rate limiting works (429 returned when limit exceeded)
- [ ] DNS rate limit: 10 req/s enforced
- [ ] WHOIS rate limit: 5 req/s enforced
- [ ] Cache hit improves response time (second request faster)
- [ ] Cache keys exist in Redis
- [ ] Cache hit rate > 0 in metrics

---

## 7.5 Error Handling Test (30 dk)

### 404 Errors

```bash
# Non-existent domain
curl -i "http://localhost:8000/api/v1/leads/nonexistent-domain-12345.invalid"

# Expected: 404 Not Found
# Response: JSON error message

# Non-existent endpoint
curl -i "http://localhost:8000/api/v1/nonexistent-endpoint"

# Expected: 404 Not Found
```

### 400 Errors

```bash
# Invalid domain format
curl -i -X POST "http://localhost:8000/api/v1/scan" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your-api-key>" \
  -d '{"domain": "invalid..domain"}'

# Expected: 400 Bad Request
# Response: Validation error message

# Missing required field
curl -i -X POST "http://localhost:8000/api/v1/scan" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your-api-key>" \
  -d '{}'

# Expected: 400 Bad Request
```

### 401 Errors

```bash
# Missing API key
curl -i "http://localhost:8000/api/v1/leads"

# Expected: 401 Unauthorized (if API key required)

# Invalid API key
curl -i -H "X-API-Key: invalid-key-12345" \
  "http://localhost:8000/api/v1/leads"

# Expected: 401 Unauthorized
```

### 500 Errors (Should be logged to Sentry)

```bash
# Trigger internal error (if test endpoint exists)
curl -i -X POST "http://localhost:8000/debug/test-error" \
  -H "X-API-Key: <your-api-key>"

# Expected: 500 Internal Server Error
# Verify: Error appears in Sentry dashboard
```

### Error Response Format

**Expected Error Response**:
```json
{
  "detail": "Error message",
  "status_code": 404,
  "error_type": "NotFoundError"
}
```

### Checklist

- [ ] 404 errors return proper JSON error response
- [ ] 400 errors return validation error messages
- [ ] 401 errors return when API key missing/invalid
- [ ] 500 errors logged to Sentry (if test error triggered)
- [ ] Error responses follow consistent format
- [ ] Error messages are user-friendly (not exposing internals)

---

## 7.6 "Satışçı Gözüyle" Kabul Kriteri

### Sales Team Perspective

**"Hunter'ı kullanabilir miyim?" testi:**

```bash
# 1. Can I see leads?
curl -s "http://localhost:8000/api/v1/leads?limit=10" | jq '.[0] | {domain, priority, segment, provider}'

# Expected: See lead with domain, priority, segment, provider

# 2. Can I scan a new domain?
curl -s -X POST "http://localhost:8000/api/v1/scan" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your-api-key>" \
  -d '{"domain": "newcompany.com"}' | jq '{domain, priority, segment}'

# Expected: New domain scanned and scored

# 3. Can I get sales summary?
curl -s "http://localhost:8000/api/v1/leads/newcompany.com/sales-summary" | jq '{one_liner, offer_tier, urgency}'

# Expected: Sales intelligence summary

# 4. Can I filter leads?
curl -s "http://localhost:8000/api/v1/leads?provider=M365&priority_min=50" | jq 'length'

# Expected: Filtered leads list
```

### Acceptance Criteria

**From Sales Team Perspective**:

- [ ] **Lead Discovery**: Can see list of leads with priority/segment
- [ ] **Domain Scanning**: Can scan new domain and get results
- [ ] **Sales Intelligence**: Can get sales summary for call prep
- [ ] **Filtering**: Can filter leads by provider, priority, segment
- [ ] **Performance**: Response time < 2 seconds for lead list
- [ ] **Reliability**: No errors during normal usage

### Real-World Usage Test

**Simulate sales workflow**:

```bash
# 1. Sales person opens lead list
curl -s "http://localhost:8000/api/v1/leads?limit=20&sort=priority_desc" | jq '.[0:5] | .[] | {domain, priority, segment}'

# 2. Sales person finds interesting lead, gets sales summary
curl -s "http://localhost:8000/api/v1/leads/<interesting-domain>/sales-summary" | jq '{one_liner, call_script: .call_script[0:2], urgency}'

# 3. Sales person scans competitor domain
curl -s -X POST "http://localhost:8000/api/v1/scan" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your-api-key>" \
  -d '{"domain": "competitor.com"}' | jq '{domain, priority, segment}'

# Expected: All operations complete successfully in < 10 seconds total
```

---

## 7.7 Smoke Tests Completion Criteria

### ✅ Minimum Requirements

- [ ] All health endpoints return 200
- [ ] Core endpoints (leads, scan) work
- [ ] Sales Engine endpoint works
- [ ] Bulk scan processes at least 5/10 domains
- [ ] Rate limiting works (429 when exceeded)
- [ ] Cache improves response time
- [ ] Error handling returns proper status codes
- [ ] Sales workflow test passes

### ✅ Performance Requirements

- [ ] Lead list response time < 2 seconds
- [ ] Single domain scan < 30 seconds
- [ ] Sales summary response time < 1 second
- [ ] Bulk scan (10 domains) < 5 minutes

### ✅ Reliability Requirements

- [ ] No 500 errors during smoke tests
- [ ] Error rate < 1% during smoke tests
- [ ] All critical endpoints accessible
- [ ] No database connection errors

---

## 📝 Smoke Test Script

**Complete smoke test script** (`scripts/smoke_tests.sh`):

Script hazır ve production-ready. Kullanım:

```bash
# Standalone smoke tests
bash scripts/smoke_tests.sh

# Custom API URL ve key ile
API_URL="https://your-prod-url" \
API_KEY="your-api-key" \
bash scripts/smoke_tests.sh
```

**Script özellikleri:**
- Health endpoints test (liveness, readiness, startup, metrics)
- Core endpoints test (leads, filters)
- Sales Engine endpoint test
- Scan endpoint test (API key ile)
- Detaylı test summary (passed/failed/warnings)
- Exit code: 0 (success) veya 1 (failure)

**Script içeriği**: `scripts/smoke_tests.sh` dosyasına bak.

---

## 🔗 Related Documents

- `docs/active/PRODUCTION-DEPLOYMENT-CHECKLIST.md` - Full deployment checklist
- `docs/active/PRODUCTION-CHECKLIST-RUNBOOK.md` - Production checklist runbook
- `docs/active/PRODUCTION-DEPLOYMENT-GUIDE.md` - Production deployment guide
- `docs/archive/2025-01-28-DEPLOYMENT-READY-SUMMARY.md` - Deployment ready summary (archived)
- `scripts/deploy_production.sh` - Deployment script
- `scripts/smoke_tests.sh` - Standalone smoke tests script

---

**Last Updated**: 2025-01-28  
**Status**: ✅ **COMPLETED** - Smoke tests script hazır ve production-ready

