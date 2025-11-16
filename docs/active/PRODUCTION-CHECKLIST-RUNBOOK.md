# Production Checklist Runbook - Hunter v1.0

**Tarih**: 2025-01-28  
**Versiyon**: v1.0.0  
**Status**: 🔄 **IN PROGRESS** - Production hazırlık aktif  
**Süre**: 2 saat (operasyonel runbook)

---

## 🎯 Amaç

Production'a çıkmadan önce:

- Health endpoints gerçekten çalışıyor mu?
- Monitoring / Sentry gerçekten veri alıyor mu?
- DB backup stratejin kâğıt üstünde değil, fiilen hazır mı?
- Redis + API versioning gerçekten doğrulandı mı?

---

## 6.1 Health Checks (30 dk)

**Staging veya prod candidate ortamında:**

### Test Commands

```bash
# Liveness
curl -i http://<host>:<port>/healthz/live

# Readiness
curl -i http://<host>:<port>/healthz/ready

# Startup
curl -i http://<host>:<port>/healthz/startup
```

### Beklenen Response

**HTTP Status**: `200 OK`

**JSON Response**:
```json
{
  "status": "ok",
  "environment": "production",
  "db": {
    "status": "ok"
  },
  "redis": {
    "status": "ok"
  }
}
```

### Detailed Verification

#### Liveness Probe (`/healthz/live`)

```bash
# Test
curl -i http://localhost:8000/healthz/live

# Expected: Always returns 200 (even if DB/Redis down)
# Purpose: Kubernetes knows container is alive
```

#### Readiness Probe (`/healthz/ready`)

```bash
# Test
curl -i http://localhost:8000/healthz/ready

# Expected: 200 if ready, 503 if not ready
# Checks: Database connection, Redis connection
```

#### Startup Probe (`/healthz/startup`)

```bash
# Test
curl -i http://localhost:8000/healthz/startup

# Expected: 200 if ready, 503 if still starting
# Purpose: Kubernetes waits before sending traffic
```

### Checklist

- [ ] `/healthz/live` 200 döndü
- [ ] `/healthz/ready` 200 döndü (DB + Redis OK)
- [ ] `/healthz/startup` 200 döndü
- [ ] Response JSON'da `environment: "production"` görünüyor
- [ ] Response JSON'da `db.status: "ok"` görünüyor
- [ ] Response JSON'da `redis.status: "ok"` görünüyor (eğer healthz'te gösteriyorsan)

### Failure Scenarios

**If `/healthz/ready` returns 503**:
```bash
# Check database connection
docker-compose exec api python -c "from app.db.session import SessionLocal; db = SessionLocal(); db.execute('SELECT 1')"

# Check Redis connection
docker-compose exec redis redis-cli ping
```

---

## 6.2 Monitoring & Sentry (30 dk)

### 1) Sentry DSN Verification

```bash
# Check if Sentry DSN is set (without exposing the value)
echo "HUNTER_SENTRY_DSN: ${HUNTER_SENTRY_DSN:+SET} ${HUNTER_SENTRY_DSN:+(hidden)}"

# Or in Docker
docker-compose exec api env | grep HUNTER_SENTRY_DSN
```

**Expected**: `HUNTER_SENTRY_DSN=SET (hidden)` or actual DSN value

### 2) Test Error Generation

**Option A: Using Python directly**

```bash
docker-compose exec api python - << 'EOF'
from app.core.logging import logger
import structlog

logger = structlog.get_logger(__name__)

try:
    1 / 0
except ZeroDivisionError:
    logger.error("Sentry test error", 
                 extra={"context": "sentry-test", 
                       "environment": "production"})
    raise
EOF
```

**Option B: Using API endpoint (if test endpoint exists)**

```bash
# If you have a test error endpoint
curl -X POST http://localhost:8000/debug/test-error \
  -H "X-API-Key: <your-api-key>"
```

**Option C: Trigger real error (scan non-existent domain)**

```bash
# This should trigger a 404 or similar error
curl -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your-api-key>" \
  -d '{"domain": "nonexistent-test-domain-12345.invalid"}'
```

### 3) Verify in Sentry Dashboard

1. Go to Sentry dashboard
2. Check "Issues" tab
3. Look for test error (should appear within 1-2 minutes)
4. Verify:
   - Event appears in dashboard
   - Environment tag is `production` (or `staging`)
   - Stack trace is visible
   - Context data is present

### Checklist

- [ ] `HUNTER_SENTRY_DSN` prod ortamında set
- [ ] Test error Sentry'de göründü (dashboard'da)
- [ ] Environment tag'i doğru (`production` veya `staging`)
- [ ] Error details (stack trace, context) görünüyor
- [ ] Error appears within 2 minutes of generation

### Troubleshooting

**If Sentry events don't appear**:
```bash
# Check Sentry initialization in logs
docker-compose logs api | grep -i sentry

# Check if Sentry SDK is installed
docker-compose exec api pip list | grep sentry

# Verify DSN format (should start with https://)
echo $HUNTER_SENTRY_DSN | grep -q "^https://" && echo "DSN format OK" || echo "DSN format invalid"
```

---

## 6.3 Database Backup Strategy (30 dk)

### 1) Backup Command (Choose based on your environment)

#### Option A: Postgres Native (Direct Connection)

```bash
# Production backup
pg_dump -h <db-host> -U <user> -d <database> \
  --no-owner --no-acl \
  > backups/backup_pre_v1.0_$(date +%Y%m%d_%H%M%S).sql

# With compression
pg_dump -h <db-host> -U <user> -d <database> \
  --no-owner --no-acl \
  | gzip > backups/backup_pre_v1.0_$(date +%Y%m%d_%H%M%S).sql.gz
```

#### Option B: Docker Container

```bash
# Using docker exec
docker exec -e PGPASSWORD=<password> <postgres-container> \
  pg_dump -U <user> -d <database> \
  > backups/backup_pre_v1.0_$(date +%Y%m%d_%H%M%S).sql

# Or using docker-compose
docker-compose exec -T postgres pg_dump -U dyn365hunter -d dyn365hunter \
  > backups/backup_pre_v1.0_$(date +%Y%m%d_%H%M%S).sql
```

#### Option C: Custom Format (Recommended for large databases)

```bash
# Custom format allows selective restore
pg_dump -h <db-host> -U <user> -d <database> \
  -F c \
  -f backups/backup_pre_v1.0_$(date +%Y%m%d_%H%M%S).dump
```

### 2) Backup Location Decision

**Choose one or multiple:**

- [ ] **Local disk**: `./backups/` directory
  - Pros: Fast access, simple
  - Cons: Limited space, not redundant
  
- [ ] **Separate backup VM/server**
  - Pros: Isolated, can automate
  - Cons: Requires network access
  
- [ ] **Cloud storage** (S3, Azure Blob, GCS)
  - Pros: Redundant, scalable, versioned
  - Cons: Requires cloud credentials, network access

**Recommended**: Local disk + Cloud storage (dual backup)

### 3) Restore Dry-Run (Staging Environment)

**CRITICAL**: Test restore procedure before production deployment.

```bash
# 1. Create staging test database
docker-compose exec postgres psql -U dyn365hunter -c "CREATE DATABASE staging_test;"

# 2. Restore backup to staging
docker-compose exec -T postgres psql -U dyn365hunter -d staging_test \
  < backups/backup_pre_v1.0_YYYYMMDD_HHMMSS.sql

# 3. Verify restore
docker-compose exec postgres psql -U dyn365hunter -d staging_test -c "\dt"
docker-compose exec postgres psql -U dyn365hunter -d staging_test -c "SELECT COUNT(*) FROM companies;"
docker-compose exec postgres psql -U dyn365hunter -d staging_test -c "SELECT COUNT(*) FROM domain_signals;"

# 4. Cleanup
docker-compose exec postgres psql -U dyn365hunter -c "DROP DATABASE staging_test;"
```

### 4) Backup Automation (Optional but Recommended)

**Cron job example**:
```bash
# Add to crontab (daily backup at 2 AM)
0 2 * * * /path/to/backup_script.sh
```

**Backup script** (`scripts/backup_database.sh`):
```bash
#!/bin/bash
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql"

# Create backup
pg_dump -h <db-host> -U <user> -d <database> > "$BACKUP_FILE"

# Compress
gzip "$BACKUP_FILE"

# Upload to cloud (optional)
# aws s3 cp "${BACKUP_FILE}.gz" s3://your-bucket/backups/

# Keep only last 7 days
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +7 -delete
```

### Checklist

- [ ] Production için backup komutu dokümante (yukarıdaki seçeneklerden biri)
- [ ] Backup lokasyonu belli (`backups/` + dış lokasyon if applicable)
- [ ] Staging ortamında en az 1 restore testi yapıldı
- [ ] Restore testi başarılı (tables exist, data counts match)
- [ ] ROLLBACK-PLAN'daki süre hedefi (<= 15 dk) gerçekçi
- [ ] Backup automation script hazır (optional but recommended)

### Backup Verification

```bash
# Check backup file exists and is not empty
ls -lh backups/backup_pre_v1.0_*.sql

# Check backup file size (should be > 0)
stat -f%z backups/backup_pre_v1.0_*.sql  # macOS
stat -c%s backups/backup_pre_v1.0_*.sql   # Linux

# Verify backup file is valid SQL
head -20 backups/backup_pre_v1.0_*.sql | grep -q "PostgreSQL database dump" && echo "Valid SQL dump" || echo "Invalid dump"
```

---

## 6.4 Redis Health + API Versioning (30 dk)

### 🔹 Redis Health (15 dk)

#### Basic Connection Test

```bash
# Redis ping (direct connection)
redis-cli -h <redis-host> -p <port> ping

# Expected: PONG

# Or using Docker
docker-compose exec redis redis-cli ping

# Expected: PONG
```

#### Health Endpoint Verification

```bash
# Check Redis status in health endpoint
curl -s http://localhost:8000/healthz/ready | jq '.redis'

# Expected:
# {
#   "status": "ok"
# }
```

#### Redis Functionality Test

```bash
# Test Redis operations
docker-compose exec redis redis-cli SET test_key "test_value"
docker-compose exec redis redis-cli GET test_key
docker-compose exec redis redis-cli DEL test_key

# Expected: test_value, then (integer) 1
```

#### Redis Connection Pool Test

```bash
# Test from application
docker-compose exec api python - << 'EOF'
from app.core.redis_client import get_redis_client
import redis

client = get_redis_client()
result = client.ping()
print(f"Redis ping: {result}")
assert result == True, "Redis connection failed"
print("✅ Redis connection OK")
EOF
```

### Checklist

- [ ] Redis PING = PONG (direct connection)
- [ ] Redis PING = PONG (from application)
- [ ] Health endpoint'te Redis `status: "ok"`
- [ ] Redis SET/GET/DEL operations work
- [ ] Redis connection pool working (from application test)

### 🔹 API Versioning (15 dk)

#### v1 Endpoints Test

```bash
# Leads endpoint (v1)
curl -i http://localhost:8000/api/v1/leads

# Expected: 200 OK or 401 Unauthorized (if API key required)

# Scan endpoint (v1)
curl -i "http://localhost:8000/api/v1/scan?domain=example.com"

# Expected: 200 OK or 400 Bad Request (if domain invalid)

# Sales Engine endpoint (v1)
curl -i "http://localhost:8000/api/v1/leads/example.com/sales-summary"

# Expected: 200 OK or 404 Not Found (if domain doesn't exist)
```

#### Legacy Endpoints Test

**Decision**: Legacy endpoints status

- [ ] **Option A**: Legacy endpoints removed → 404 expected
- [ ] **Option B**: Legacy endpoints supported → 200 expected

**If Option B (Legacy supported)**:

```bash
# Legacy scan endpoint
curl -i "http://localhost:8000/scan?domain=example.com"

# Legacy leads endpoint
curl -i "http://localhost:8000/leads"

# Expected: 200 OK (backward compatibility)
```

**If Option A (Legacy removed)**:

```bash
# Legacy endpoints should return 404
curl -i "http://localhost:8000/scan?domain=example.com"

# Expected: 404 Not Found
```

#### API Versioning Verification

```bash
# Test both v1 and legacy (if supported)
# v1 endpoints
curl -s http://localhost:8000/api/v1/leads | jq '.'
curl -s "http://localhost:8000/api/v1/scan?domain=test.com" | jq '.'

# Legacy endpoints (if supported)
curl -s http://localhost:8000/leads | jq '.'
curl -s "http://localhost:8000/scan?domain=test.com" | jq '.'

# Verify response structure is consistent
```

### Checklist

- [ ] `/api/v1/leads` endpoint çalışıyor (200 veya beklenen 4xx)
- [ ] `/api/v1/scan` endpoint çalışıyor (200 veya beklenen 4xx)
- [ ] `/api/v1/leads/{domain}/sales-summary` endpoint çalışıyor
- [ ] Legacy endpoint'ler için karar net:
  - [ ] Ya kaldırıldı, 404 dönüyor (dokümante)
  - [ ] Ya destekleniyor, 200 dönüyor (dokümante)
- [ ] API versioning backward compatibility test edildi (if applicable)

---

## 6.5 "Production Checklist" Bitti Saymak için Minimum Koşullar

Bu adımı **tamamlandı** işaretleyebilmen için en az şunlar gerçek olmalı:

### ✅ Required Checks

- [ ] Üç health endpoint de (live/ready/startup) çalışır durumda
- [ ] Sentry test event'i dashboard'da görüldü (ve environment doğru)
- [ ] Production için backup komutu + lokasyon + restore dry-run dokümante
- [ ] Redis'e ping atıp PONG aldın
- [ ] `/api/v1/leads`, `/api/v1/scan` ve kritik legacy endpoint'lerin durumu net

### ✅ Verification Commands

```bash
# Quick verification script
echo "=== Health Checks ==="
curl -s http://localhost:8000/healthz/live | jq '.status'
curl -s http://localhost:8000/healthz/ready | jq '.status'
curl -s http://localhost:8000/healthz/startup | jq '.status'

echo "=== Redis ==="
docker-compose exec redis redis-cli ping

echo "=== API Versioning ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/leads
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/scan?domain=test.com

echo "=== Sentry ==="
echo "Check Sentry dashboard manually for test event"
```

### ✅ Completion Criteria

**All checks must pass**:
- Health endpoints: ✅ All 200 OK
- Sentry: ✅ Test event visible in dashboard
- Backup: ✅ Command documented + restore tested
- Redis: ✅ PING = PONG
- API Versioning: ✅ v1 endpoints working + legacy decision documented

---

## 📝 Notes

- **Staging First**: Always test in staging before production
- **Document Decisions**: If legacy endpoints are removed, document it clearly
- **Backup Frequency**: Decide on backup frequency (daily recommended)
- **Sentry Alerts**: Set up Sentry alerts for critical errors

---

## 🔗 Related Documents

- `docs/active/PRODUCTION-DEPLOYMENT-CHECKLIST.md` - Full deployment checklist
- `docs/active/ROLLBACK-PLAN.md` - Rollback procedures
- `docs/active/ALEMBIC-MIGRATION-PLAN.md` - Migration procedures
- `scripts/deploy_production.sh` - Deployment script

---

**Last Updated**: 2025-01-28  
**Status**: 🔄 **IN PROGRESS** - Production checklist runbook hazır

