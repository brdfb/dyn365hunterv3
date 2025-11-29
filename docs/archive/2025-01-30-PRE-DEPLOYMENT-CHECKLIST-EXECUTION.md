# 📋 Pre-Deployment Checklist - Execution Log

**Tarih**: 2025-01-30  
**Versiyon**: v1.0.0  
**Durum**: 🔄 **IN PROGRESS**  
**Süre Tahmini**: 2-3 gün (6 saat toplam)

---

## 🎯 Genel Bakış

Bu checklist, production deployment öncesi **tüm kritik adımları** içerir. Her adım tamamlandığında işaretlenecek ve doğrulama komutları çalıştırılacak.

**Referans**: `docs/reference/PRODUCTION-CHECKLIST-RUNBOOK.md` (2 saatlik operasyonel runbook)

---

## 📅 DAY 1: Environment Setup (2 saat)

**Status**: 🔄 **IN PROGRESS** - Development ortamında kontroller yapıldı, Production için environment variables set edilmeli

### 1.1 Environment Variables Setup

#### ✅ Required Variables

- [ ] **`ENVIRONMENT=production`** (ZORUNLU) ⚠️ **PRODUCTION'DA SET EDİLMELİ**
  ```bash
  # Check
  echo "ENVIRONMENT: ${ENVIRONMENT:-NOT SET}"
  # Expected: production
  ```

- [ ] **`DATABASE_URL`** (ZORUNLU)
  ```bash
  # Check (first 20 chars only for security)
  echo "DATABASE_URL: ${DATABASE_URL:0:20}..."
  # Format: postgresql://user:password@host:port/database
  # Production: SSL enabled (postgresql://...?sslmode=require)
  ```

- [ ] **`REDIS_URL`** (ZORUNLU)
  ```bash
  # Check (first 20 chars only)
  echo "REDIS_URL: ${REDIS_URL:0:20}..."
  # Format: redis://host:port/db or redis://:password@host:port/db
  ```

- [ ] **`LOG_LEVEL=INFO`** (ZORUNLU - Production için)
  ```bash
  # Check
  echo "LOG_LEVEL: ${LOG_LEVEL:-NOT SET}"
  # Expected: INFO (not DEBUG)
  ```

- [ ] **`API_HOST=0.0.0.0`** (Default, genellikle değiştirilmez)
  ```bash
  # Check
  echo "API_HOST: ${API_HOST:-0.0.0.0}"
  ```

- [ ] **`API_PORT=8000`** (Default, genellikle değiştirilmez)
  ```bash
  # Check
  echo "API_PORT: ${API_PORT:-8000}"
  ```

#### ⚠️ Optional (Strongly Recommended)

- [ ] **`HUNTER_SENTRY_DSN`** (ÖNERİLEN - Error tracking için)
  ```bash
  # Check
  echo "HUNTER_SENTRY_DSN: ${HUNTER_SENTRY_DSN:+SET}"
  # Format: https://<key>@<org>.ingest.sentry.io/<project>
  ```

- [ ] **`HUNTER_DB_POOL_SIZE=20`** (Optional - default: 20)
  ```bash
  # Check
  echo "HUNTER_DB_POOL_SIZE: ${HUNTER_DB_POOL_SIZE:-20}"
  ```

- [ ] **`HUNTER_DB_MAX_OVERFLOW=10`** (Optional - default: 10)
  ```bash
  # Check
  echo "HUNTER_DB_MAX_OVERFLOW: ${HUNTER_DB_MAX_OVERFLOW:-10}"
  ```

#### 🔒 Feature Flags (Production v1.0 - Phase 1: Both OFF)

- [ ] **`HUNTER_PARTNER_CENTER_ENABLED=false`** (Phase 1: OFF)
  ```bash
  # Check
  echo "HUNTER_PARTNER_CENTER_ENABLED: ${HUNTER_PARTNER_CENTER_ENABLED:-false}"
  # Expected: false (Phase 1)
  ```

- [ ] **`HUNTER_D365_ENABLED=false`** (Phase 1: OFF)
  ```bash
  # Check
  echo "HUNTER_D365_ENABLED: ${HUNTER_D365_ENABLED:-false}"
  # Expected: false (Phase 1)
  ```

- [ ] **`HUNTER_ENRICHMENT_ENABLED=false`** (v1.0: OFF)
  ```bash
  # Check
  echo "HUNTER_ENRICHMENT_ENABLED: ${HUNTER_ENRICHMENT_ENABLED:-false}"
  # Expected: false (v1.0)
  ```

**Status**: ⏳ **TODO**  
**Note**: Production ortamında environment variables set edilmeli (template: `docs/active/PRE-DEPLOYMENT-STATUS.md`)

---

### 1.2 Database Connection Test

- [x] **Database connection test** ✅ **DEVELOPMENT'DA TAMAMLANDI**
  ```bash
  # Test database connection
  docker-compose exec api python -c "
  from app.db.session import SessionLocal
  try:
      db = SessionLocal()
      db.execute('SELECT 1')
      print('✅ Database connection OK')
  except Exception as e:
      print(f'❌ Database connection FAILED: {e}')
  "
  # Expected: ✅ Database connection OK
  # ✅ Development'da: PostgreSQL Ready, Database connection OK
  ```

- [x] **PostgreSQL readiness check** ✅ **DEVELOPMENT'DA TAMAMLANDI**
  ```bash
  # Check PostgreSQL is ready
  docker-compose exec postgres pg_isready -U dyn365hunter
  # Expected: postgres:5432 - accepting connections
  # ✅ Development'da: PostgreSQL Ready
  ```

**Status**: ✅ **DEVELOPMENT'DA TAMAMLANDI** - ⚠️ **PRODUCTION'DA TEKRAR TEST EDİLMELİ**

---

### 1.3 Redis Connection Test

- [x] **Redis PING test** ✅ **DEVELOPMENT'DA TAMAMLANDI**
  ```bash
  # Direct Redis connection
  docker-compose exec redis redis-cli ping
  # Expected: PONG
  # ✅ Development'da: Redis PING = PONG
  ```

- [x] **Redis connection from application** ✅ **DEVELOPMENT'DA TAMAMLANDI**
  ```bash
  # Test from application
  docker-compose exec api python -c "
  from app.core.redis_client import get_redis_client
  try:
      r = get_redis_client()
      result = r.ping()
      print('✅ Redis connection OK' if result else '❌ Redis connection FAILED')
  except Exception as e:
      print(f'❌ Redis connection FAILED: {e}')
  "
  # Expected: ✅ Redis connection OK
  # ✅ Development'da: Redis Connection (from app) = OK
  ```

**Status**: ✅ **DEVELOPMENT'DA TAMAMLANDI** - ⚠️ **PRODUCTION'DA TEKRAR TEST EDİLMELİ**

---

### 1.4 Sentry DSN Verification

- [ ] **Sentry DSN check**
  ```bash
  # Check Sentry DSN is set (without exposing value)
  docker-compose exec api env | grep HUNTER_SENTRY_DSN
  # Expected: HUNTER_SENTRY_DSN=https://...
  ```

- [ ] **Sentry test error generation**
  ```bash
  # Generate test error
  docker-compose exec api python - << 'EOF'
  from app.core.logging import logger
  try:
      1 / 0
  except ZeroDivisionError:
      logger.error("Sentry test error", 
                   extra={"context": "sentry-test", 
                         "environment": "production"})
      raise
  EOF
  # Then check Sentry dashboard (should appear within 1-2 minutes)
  ```

- [ ] **Sentry dashboard verification**
  - [ ] Go to Sentry dashboard
  - [ ] Check "Issues" tab
  - [ ] Look for test error (should appear within 1-2 minutes)
  - [ ] Verify environment tag is `production`
  - [ ] Verify stack trace is visible

**Status**: ⏳ **TODO**

---

## 📅 DAY 2: Migration & Backup (2 saat)

### 2.1 Database Backup

- [x] **Backup directory mevcut** ✅ **DEVELOPMENT'DA TAMAMLANDI**
  ```bash
  # Backup directory exists
  ls -la backups/
  # ✅ Development'da: backups/ directory exists with previous backups
  ```

- [ ] **Pre-deployment backup alınmalı** ⚠️ **PRODUCTION'DA YAPILMALI**
  ```bash
  # Create backup directory
  mkdir -p backups
  
  # Option A: Direct PostgreSQL (if accessible)
  pg_dump -h <db-host> -U <user> -d <database> \
    --no-owner --no-acl \
    > backups/backup_pre_v1.0_$(date +%Y%m%d_%H%M%S).sql
  
  # Option B: Docker Compose (recommended for local)
  docker-compose exec -T postgres pg_dump -U dyn365hunter -d dyn365hunter \
    > backups/backup_pre_v1.0_$(date +%Y%m%d_%H%M%S).sql
  
  # Option C: Custom format (for large databases)
  pg_dump -h <db-host> -U <user> -d <database> \
    -F c \
    -f backups/backup_pre_v1.0_$(date +%Y%m%d_%H%M%S).dump
  ```

- [ ] **Backup integrity check**
  ```bash
  # Check backup file exists and is not empty
  ls -lh backups/backup_pre_v1.0_*.sql
  
  # Check backup file size (should be > 0)
  stat -c%s backups/backup_pre_v1.0_*.sql  # Linux
  # stat -f%z backups/backup_pre_v1.0_*.sql  # macOS
  
  # Verify backup file is valid SQL
  head -20 backups/backup_pre_v1.0_*.sql | grep -q "PostgreSQL database dump" && echo "✅ Valid SQL dump" || echo "❌ Invalid dump"
  # Expected: ✅ Valid SQL dump
  ```

- [ ] **Backup location decision**
  - [ ] Local disk: `./backups/` directory
  - [ ] Cloud storage: S3/Azure Blob/GCS (optional but recommended)
  - [ ] **Recommended**: Local disk + Cloud storage (dual backup)

**Status**: ⏳ **TODO**

---

### 2.2 Restore Dry-Run Test (Staging Environment)

- [ ] **Create staging test database**
  ```bash
  # Create staging test database
  docker-compose exec postgres psql -U dyn365hunter -c "CREATE DATABASE staging_test;"
  ```

- [ ] **Restore backup to staging**
  ```bash
  # Restore backup to staging
  docker-compose exec -T postgres psql -U dyn365hunter -d staging_test \
    < backups/backup_pre_v1.0_YYYYMMDD_HHMMSS.sql
  # Expected: No errors
  ```

- [ ] **Verify restore**
  ```bash
  # Check tables exist
  docker-compose exec postgres psql -U dyn365hunter -d staging_test -c "\dt"
  # Expected: List of tables
  
  # Check data counts
  docker-compose exec postgres psql -U dyn365hunter -d staging_test -c "SELECT COUNT(*) FROM companies;"
  docker-compose exec postgres psql -U dyn365hunter -d staging_test -c "SELECT COUNT(*) FROM domain_signals;"
  # Expected: Count > 0 (if data exists)
  ```

- [ ] **Cleanup**
  ```bash
  # Drop staging test database
  docker-compose exec postgres psql -U dyn365hunter -c "DROP DATABASE staging_test;"
  ```

**Status**: ⏳ **TODO**

---

### 2.3 Migration Test

- [x] **Current migration version check** ✅ **DEVELOPMENT'DA TAMAMLANDI**
  ```bash
  # Check current migration version
  docker-compose exec api alembic current
  # Expected: Shows current revision (e.g., f786f93501ea)
  # ✅ Development'da: Current revision = 67a00e2b26ab (head)
  ```

- [ ] **Migration dry-run (staging)**
  ```bash
  # ⚠️ IMPORTANT: Test in staging first, not production!
  # Check what migrations would be applied
  docker-compose exec api alembic upgrade head --sql
  # This shows SQL without executing (dry-run)
  ```

- [x] **Schema verification (G20 columns)** ✅ **DEVELOPMENT'DA TAMAMLANDI**
  ```bash
  # Check critical G20 columns exist
  docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'companies' AND column_name = 'tenant_size';
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'domain_signals' AND column_name IN ('local_provider', 'dmarc_coverage');
  "
  # Expected: tenant_size, local_provider, dmarc_coverage columns exist
  # ✅ Development'da: tenant_size column exists, all tables present
  ```

- [ ] **⚠️ CRITICAL: Database Reset Policy**
  - [ ] **DO NOT** use `schema.sql` (outdated, missing G20 columns)
  - [ ] **DO NOT** use legacy SQL migrations (transaction-unsafe)
  - [ ] **DO** use Alembic migrations only (official way)
  - [ ] **DO** use `./scripts/reset_db_with_alembic.sh` for database reset

**Status**: ⏳ **TODO**

---

### 2.4 Rollback Plan Test

- [ ] **Application rollback test (<5dk)**
  ```bash
  # Test application rollback (Docker Compose)
  docker-compose down
  # (In real scenario: checkout previous version or use previous Docker image)
  docker-compose up -d
  # Verify rollback
  curl http://localhost:8000/healthz/live
  curl http://localhost:8000/healthz/ready
  ```

- [ ] **Migration rollback test (<10dk)**
  ```bash
  # Test migration rollback
  docker-compose exec api alembic downgrade -1
  # Verify rollback
  docker-compose exec api alembic current
  ```

- [ ] **Database restore test (<15dk)**
  ```bash
  # Test database restore (use staging test database)
  # (Already tested in section 2.2)
  ```

**Status**: ⏳ **TODO**

---

## 📅 DAY 3: Deployment & Verification (2 saat)

### 3.1 Health Checks

- [x] **Liveness probe (`/healthz/live`)** ✅ **DEVELOPMENT'DA TAMAMLANDI**
  ```bash
  curl -i http://localhost:8000/healthz/live
  # Expected: 200 OK
  # Response: {"status": "ok"}
  # ✅ Development'da: Health Check (Liveness) = OK
  ```

- [x] **Readiness probe (`/healthz/ready`)** ✅ **DEVELOPMENT'DA TAMAMLANDI**
  ```bash
  curl -i http://localhost:8000/healthz/ready
  # Expected: 200 OK
  # Response: {"status": "ok", "db": {"status": "ok"}, "redis": {"status": "ok"}}
  # ✅ Development'da: Health Check (Readiness) = OK, DB + Redis OK
  ```

- [x] **Startup probe (`/healthz/startup`)** ✅ **DEVELOPMENT'DA TAMAMLANDI**
  ```bash
  curl -i http://localhost:8000/healthz/startup
  # Expected: 200 OK
  # Response: {"status": "ok"}
  # ✅ Development'da: Health Check (Startup) = OK
  ```

- [x] **Metrics endpoint (`/healthz/metrics`)** ✅ **DEVELOPMENT'DA TAMAMLANDI**
  ```bash
  curl -s http://localhost:8000/healthz/metrics | jq '.'
  # Expected: Valid JSON with metrics data
  # ✅ Development'da: Health Check (Metrics) = OK
  ```

**Status**: ✅ **DEVELOPMENT'DA TAMAMLANDI** - ⚠️ **PRODUCTION'DA TEKRAR TEST EDİLMELİ**

---

### 3.2 Deployment Script Dry-Run

- [ ] **Deployment script dry-run**
  ```bash
  # Test deployment without making changes
  ENVIRONMENT=production bash scripts/deploy_production.sh --dry-run
  # Expected: Shows what would be done without executing
  ```

- [ ] **Safety guards verification**
  - [ ] Production guard: Requires `FORCE_PRODUCTION=yes` when `ENVIRONMENT=production`
  - [ ] Localhost protection: Blocks production deployments if `DATABASE_URL` points to localhost
  - [ ] Backup integrity: Validates backup file integrity before proceeding

**Status**: ⏳ **TODO**

---

### 3.3 Smoke Tests

- [ ] **Core endpoints test**
  ```bash
  # Leads endpoint
  curl -i "http://localhost:8000/api/v1/leads?limit=10"
  # Expected: 200 OK
  
  # Scan endpoint
  curl -i -X POST "http://localhost:8000/api/v1/scan" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: <your-api-key>" \
    -d '{"domain": "example.com"}'
  # Expected: 200 OK or 202 Accepted
  ```

- [ ] **Sales Engine endpoint test**
  ```bash
  # Sales summary endpoint
  curl -i "http://localhost:8000/api/v1/leads/example.com/sales-summary"
  # Expected: 200 OK or 404 Not Found (if domain doesn't exist)
  ```

- [ ] **Bulk operations test**
  ```bash
  # Bulk scan test (10 domains)
  # (Use your bulk scan endpoint)
  ```

- [ ] **Rate limiting test**
  ```bash
  # Test rate limiting (make multiple requests)
  for i in {1..10}; do
    curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/v1/leads
  done
  # Expected: Some requests should be rate limited (429)
  ```

- [ ] **Cache functionality test**
  ```bash
  # Test cache (same request twice, second should be faster)
  time curl -s http://localhost:8000/api/v1/leads > /dev/null
  time curl -s http://localhost:8000/api/v1/leads > /dev/null
  # Expected: Second request should be faster (cached)
  ```

**Status**: ⏳ **TODO**

---

### 3.4 Monitoring Setup

- [ ] **Sentry dashboard verification**
  - [ ] Sentry dashboard accessible
  - [ ] Test error visible (from Day 1)
  - [ ] Environment tag is `production`

- [ ] **Log aggregation setup**
  - [ ] Logs are in JSON format (production)
  - [ ] Log aggregation configured (ELK or similar)
  - [ ] PII masking active (domain/email masking)

- [ ] **Metrics endpoint verification**
  ```bash
  # Check metrics endpoint
  curl -s http://localhost:8000/healthz/metrics | jq '.'
  # Expected: Valid JSON with metrics (cache, rate limit, bulk operations, errors)
  ```

- [ ] **Alerting kriterleri belirlenmeli**
  - [ ] P0 alerts: Health checks fail, DB/Redis down, Worker crash, API 500 errors
  - [ ] P1 alerts: DNS/WHOIS timeout > 10%, Response time > 2s, Task failure > 5%
  - [ ] P2 alerts: Normal logging (optional dependency warnings OK)

**Status**: ⏳ **TODO**

---

### 3.5 API Versioning Verification

- [ ] **v1 endpoints test**
  ```bash
  # v1 endpoints
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/v1/leads
  curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:8000/api/v1/scan?domain=test.com"
  # Expected: 200 or expected 4xx
  ```

- [ ] **Legacy endpoints decision**
  - [ ] **Option A**: Legacy endpoints removed → 404 expected
  - [ ] **Option B**: Legacy endpoints supported → 200 expected
  - [ ] **Decision documented**: _________________________

**Status**: ⏳ **TODO**

---

## ✅ Completion Criteria

### Minimum Requirements (All Must Pass)

- [ ] ✅ All health endpoints return 200 OK
- [ ] ✅ Sentry test event visible in dashboard
- [ ] ✅ Backup command documented + restore tested
- [ ] ✅ Redis PING = PONG
- [ ] ✅ Database connection OK
- [ ] ✅ v1 endpoints working
- [ ] ✅ Legacy endpoints decision documented
- [ ] ✅ Migration dry-run successful
- [ ] ✅ Rollback plan tested
- [ ] ✅ Smoke tests passing

---

## 📝 Notes

- **Staging First**: Always test in staging before production
- **Document Decisions**: If legacy endpoints are removed, document it clearly
- **Backup Frequency**: Decide on backup frequency (daily recommended)
- **Sentry Alerts**: Set up Sentry alerts for critical errors

---

## 🔗 Related Documents

- `docs/reference/PRODUCTION-CHECKLIST-RUNBOOK.md` - Detailed runbook (2 hours)
- `docs/reference/PRODUCTION-DEPLOYMENT-GUIDE.md` - Deployment guide
- `docs/reference/ENVIRONMENT-VARIABLES-CHECKLIST.md` - Environment variables
- `docs/reference/SMOKE-TESTS-RUNBOOK.md` - Smoke tests runbook
- `docs/reference/ROLLBACK-PLAN.md` - Rollback procedures

---

**Last Updated**: 2025-01-30  
**Status**: 🔄 **IN PROGRESS**  
**Next Step**: Start with Day 1 - Environment Setup

