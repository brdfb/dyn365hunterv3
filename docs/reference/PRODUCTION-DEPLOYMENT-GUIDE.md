# Production Deployment Guide - Hunter v1.0

**Tarih**: 2025-01-28  
**Versiyon**: v1.0.0  
**Status**: ✅ **Production Ready**  
**Kullanım**: Production deployment için adım adım rehber

---

## 🎯 Overview

This guide walks you through deploying Hunter v1.0 to production. It covers:

- Pre-deployment checks
- Deployment script usage
- Environment verification
- Backup & restore procedures
- Migration flow
- Smoke tests
- Rollback procedures

---

## 📋 Pre-Deployment Checklist

### 1. Environment Variables

**Verify all required environment variables are set:**

```bash
# Check required variables
echo "DATABASE_URL: ${DATABASE_URL:+SET}"
echo "REDIS_URL: ${REDIS_URL:+SET}"
echo "ENVIRONMENT: ${ENVIRONMENT:-NOT SET}"
echo "LOG_LEVEL: ${LOG_LEVEL:-NOT SET}"
echo "HUNTER_SENTRY_DSN: ${HUNTER_SENTRY_DSN:+SET}"
```

**See**: `docs/active/ENVIRONMENT-VARIABLES-CHECKLIST.md` for complete checklist.

### 2. Database Backup

**CRITICAL**: Always backup before deployment.

```bash
# Create backup
pg_dump -h <db-host> -U <user> -d <database> \
  > backups/backup_pre_v1.0_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
ls -lh backups/backup_pre_v1.0_*.sql
```

**See**: `docs/archive/2025-01-28-ALEMBIC-MIGRATION-PLAN.md` for detailed backup procedures (archived - reference only).

### 3. Current Migration Status

```bash
# Check current migration version
docker-compose exec api alembic current

# Expected: 08f51db8dce0 (head)
```

---

## 🚀 Deployment Script Usage

### Basic Deployment

```bash
# Run deployment script
bash scripts/deploy_production.sh

# This will:
# 1. Check prerequisites
# 2. Create database backup
# 3. Run Alembic migration
# 4. Build and deploy application
# 5. Wait for services
# 6. Run smoke tests
```

### Dry Run (Recommended First)

```bash
# Test deployment without making changes
bash scripts/deploy_production.sh --dry-run

# Shows what would be done without executing
```

### Skip Options

```bash
# Skip backup (not recommended)
bash scripts/deploy_production.sh --skip-backup

# Skip smoke tests (not recommended)
bash scripts/deploy_production.sh --skip-tests
```

### Deployment Log

```bash
# Deployment logs are saved to:
./logs/deploy_YYYYMMDD_HHMMSS.log

# View logs
tail -f logs/deploy_*.log
```

---

## 🔍 Environment Verification

### 1. Health Checks

```bash
# Liveness
curl -i http://localhost:8000/healthz/live
# Expected: 200 OK

# Readiness
curl -i http://localhost:8000/healthz/ready
# Expected: 200 OK (DB + Redis OK)

# Startup
curl -i http://localhost:8000/healthz/startup
# Expected: 200 OK
```

### 2. Database Connection

```bash
# Test database connection
docker-compose exec api python -c "
from app.db.session import SessionLocal
db = SessionLocal()
db.execute('SELECT 1')
print('✅ Database connection OK')
"
```

### 3. Redis Connection

```bash
# Test Redis connection
docker-compose exec redis redis-cli ping
# Expected: PONG

# Or from application
docker-compose exec api python -c "
from app.core.redis_client import get_redis_client
r = get_redis_client()
print('✅ Redis connection OK' if r.ping() else '❌ Redis connection FAILED')
"
```

### 4. Sentry Configuration

```bash
# Verify Sentry DSN is set
docker-compose exec api env | grep HUNTER_SENTRY_DSN

# Test error reporting (check Sentry dashboard)
docker-compose exec api python - << 'EOF'
from app.core.logging import logger
logger.error("Sentry test error", extra={"context": "deployment-test"})
EOF
```

---

## 💾 Backup & Restore Procedures

### Backup

**Automated (via deployment script)**:
```bash
# Backup is created automatically before migration
# Location: backups/backup_pre_v1.0_YYYYMMDD_HHMMSS.sql
```

**Manual Backup**:
```bash
# Direct PostgreSQL
pg_dump -h <db-host> -U <user> -d <database> \
  > backups/backup_manual_$(date +%Y%m%d_%H%M%S).sql

# Docker
docker-compose exec -T postgres pg_dump -U dyn365hunter -d dyn365hunter \
  > backups/backup_manual_$(date +%Y%m%d_%H%M%S).sql
```

### Restore

**If rollback needed**:
```bash
# Stop application
docker-compose down

# Restore database
psql -h <db-host> -U <user> -d <database> \
  < backups/backup_pre_v1.0_YYYYMMDD_HHMMSS.sql

# Or using Docker
docker-compose exec -T postgres psql -U dyn365hunter -d dyn365hunter \
  < backups/backup_pre_v1.0_YYYYMMDD_HHMMSS.sql

# Restart application
docker-compose up -d
```

**See**: `docs/active/ROLLBACK-PLAN.md` for detailed restore procedures.

---

## 🔄 Migration Flow

### ⚠️ Important: Database Reset Policy

**DO NOT use `schema.sql` or legacy SQL migrations for database reset.**

- ❌ **DO NOT**: `psql -f app/db/schema.sql` (outdated, missing G20 columns)
- ❌ **DO NOT**: Run legacy SQL migrations manually (transaction-unsafe)
- ✅ **DO**: Use Alembic migrations only (official way for v1.0+)

**Official reset method:**
```bash
# Use the official reset script
./scripts/reset_db_with_alembic.sh

# Or manually:
# 1. Drop schema: DROP SCHEMA public CASCADE; CREATE SCHEMA public;
# 2. Run Alembic: alembic upgrade head
```

### Step 1: Check Current Version

```bash
docker-compose exec api alembic current
```

### Step 2: Run Migration

```bash
# Upgrade to head
docker-compose exec api alembic upgrade head

# Verify migration
docker-compose exec api alembic current
# Expected: f786f93501ea (head - CSP P-Model)
```

### Step 3: Verify Schema

```bash
# Check tables exist
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "\dt"

# Check critical G20 columns exist
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
  SELECT column_name FROM information_schema.columns 
  WHERE table_name = 'companies' AND column_name = 'tenant_size';
  SELECT column_name FROM information_schema.columns 
  WHERE table_name = 'domain_signals' AND column_name IN ('local_provider', 'dmarc_coverage');
"

# Check data counts
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "SELECT COUNT(*) FROM companies;"
```

**See**: `docs/archive/2025-01-28-ALEMBIC-MIGRATION-PLAN.md` for detailed migration procedures (archived - reference only).

---

## 🧪 Smoke Tests

### Automated (via deployment script)

```bash
# Smoke tests run automatically after deployment
# Checks:
# - Health endpoints
# - Core endpoints
# - Sales Engine endpoint
```

### Manual Smoke Tests

```bash
# Run smoke tests manually
bash scripts/smoke_tests.sh

# Or use runbook
# See: docs/active/SMOKE-TESTS-RUNBOOK.md
```

### Smoke Test Checklist

- [ ] Health checks passing
- [ ] Leads endpoint working
- [ ] Scan endpoint working
- [ ] Sales Engine endpoint working
- [ ] No 500 errors in logs

**See**: `docs/active/SMOKE-TESTS-RUNBOOK.md` for complete smoke test procedures.

---

## 🔙 Rollback Decision

### When to Rollback

**Immediate rollback triggers**:
- ❌ Health checks failing
- ❌ Critical errors in logs
- ❌ Database migration failures
- ❌ Smoke tests failing
- ❌ High error rate (>5%)

### Rollback Methods

**1. Application Rollback** (< 5 minutes):
```bash
# Docker Compose
docker-compose down
git checkout <previous-version-tag>
docker-compose up -d

# Kubernetes
kubectl rollout undo deployment/dyn365hunter-api
```

**2. Database Migration Rollback** (< 10 minutes):
```bash
docker-compose exec api alembic downgrade -1
```

**3. Database Restore** (< 15 minutes):
```bash
# Restore from backup
psql -h <db-host> -U <user> -d <database> \
  < backups/backup_pre_v1.0_YYYYMMDD_HHMMSS.sql
```

**See**: `docs/active/ROLLBACK-PLAN.md` for detailed rollback procedures.

---

## 📊 Post-Deployment Monitoring

### First 1 Hour

**Monitor**:
- Error rate (< 1%)
- Latency (P95 < 500ms)
- Health checks (all passing)
- Sentry errors (no critical errors)

**Commands**:
```bash
# Check health
curl http://localhost:8000/healthz/ready

# Check metrics
curl http://localhost:8000/healthz/metrics | jq '.'

# Check logs
docker-compose logs -f api | grep -i error
```

### First 24 Hours

**Monitor**:
- Error rate stability
- Latency stability
- Cache hit rate (> 50%)
- Rate limiting working
- Database connection pool healthy

---

## 🔗 Related Documents

- `docs/active/PRODUCTION-DEPLOYMENT-CHECKLIST.md` - Full deployment checklist
- `docs/active/PRODUCTION-CHECKLIST-RUNBOOK.md` - Production checklist runbook
- `docs/active/SMOKE-TESTS-RUNBOOK.md` - Smoke tests runbook
- `docs/archive/2025-01-28-ALEMBIC-MIGRATION-PLAN.md` - Migration procedures (archived - reference only)
- `docs/active/ROLLBACK-PLAN.md` - Rollback procedures
- `docs/active/ENVIRONMENT-VARIABLES-CHECKLIST.md` - Environment variables
- `docs/active/TROUBLESHOOTING-GUIDE.md` - Troubleshooting guide

---

## ✅ Quick Reference

### Deployment Command

```bash
# Full deployment
bash scripts/deploy_production.sh

# Dry run first
bash scripts/deploy_production.sh --dry-run
```

### Verification Commands

```bash
# Health checks
curl http://localhost:8000/healthz/live
curl http://localhost:8000/healthz/ready

# Migration status
docker-compose exec api alembic current

# Smoke tests (standalone script)
bash scripts/smoke_tests.sh

# Or with custom API URL and key
API_URL="https://your-prod-url" API_KEY="your-key" bash scripts/smoke_tests.sh
```

### Rollback Command

```bash
# Quick rollback
docker-compose down
# Restore from backup or checkout previous version
docker-compose up -d
```

---

**Last Updated**: 2025-01-28  
**Status**: ✅ **Production Ready**

