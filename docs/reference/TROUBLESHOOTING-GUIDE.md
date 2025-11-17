# Troubleshooting Guide - Hunter v1.0

**Tarih**: 2025-01-28  
**Versiyon**: v1.0.0  
**Status**: ✅ **Production Ready**  
**Kullanım**: Production sorun giderme rehberi

---

## 🎯 Overview

This guide covers common production issues and their solutions. Each section includes:

- Symptom description
- Diagnosis steps
- Resolution procedures
- Prevention measures

---

## 🏥 Health Check Failures

### `/healthz/live` Returns 503

**Symptom**: Liveness probe failing, container restarting.

**Diagnosis**:
```bash
# Check container status
docker-compose ps api

# Check logs
docker-compose logs api | tail -50

# Check if process is running
docker-compose exec api ps aux | grep uvicorn
```

**Resolution**:
```bash
# Restart container
docker-compose restart api

# If persists, check for deadlock/infinite loop in code
docker-compose logs api | grep -i "deadlock\|loop\|hang"
```

**Prevention**: Monitor application logs, set up alerts for repeated restarts.

---

### `/healthz/ready` Returns 503

**Symptom**: Readiness probe failing, traffic not routed to pod.

**Diagnosis**:
```bash
# Check database connection
docker-compose exec api python -c "
from app.db.session import SessionLocal
try:
    db = SessionLocal()
    db.execute('SELECT 1')
    print('✅ DB OK')
except Exception as e:
    print(f'❌ DB FAILED: {e}')
"

# Check Redis connection
docker-compose exec redis redis-cli ping
```

**Resolution**:

**If Database Issue**:
```bash
# Check PostgreSQL
docker-compose ps postgres
docker-compose logs postgres | tail -50

# Restart PostgreSQL if needed
docker-compose restart postgres

# Wait for PostgreSQL to be ready
docker-compose exec postgres pg_isready -U dyn365hunter
```

**If Redis Issue**:
```bash
# Check Redis
docker-compose ps redis
docker-compose logs redis | tail -50

# Restart Redis if needed
docker-compose restart redis

# Test Redis
docker-compose exec redis redis-cli ping
```

**Prevention**: Monitor database and Redis health, set up connection pool alerts.

---

### `/healthz/startup` Returns 503

**Symptom**: Startup probe failing, Kubernetes not sending traffic.

**Diagnosis**:
```bash
# Check if application is still starting
docker-compose logs api | grep -i "startup\|initializing\|ready"

# Check startup time (should be < 60s)
docker-compose logs api | head -100
```

**Resolution**:
```bash
# If startup is slow, check:
# 1. Database connection time
# 2. Redis connection time
# 3. Heavy initialization code

# Increase startup probe timeout if needed (Kubernetes)
# startupProbe:
#   initialDelaySeconds: 30
#   periodSeconds: 10
#   timeoutSeconds: 5
#   failureThreshold: 12  # 2 minutes total
```

**Prevention**: Optimize startup code, monitor startup time.

---

## 🔴 Redis Failures

### Redis Connection Refused

**Symptom**: Redis errors in logs, cache/rate limiting not working.

**Diagnosis**:
```bash
# Check Redis container
docker-compose ps redis

# Check Redis logs
docker-compose logs redis | tail -50

# Test Redis connection
docker-compose exec redis redis-cli ping
```

**Resolution**:
```bash
# Restart Redis
docker-compose restart redis

# Verify Redis is ready
docker-compose exec redis redis-cli ping
# Expected: PONG

# Check Redis memory
docker-compose exec redis redis-cli INFO memory
```

**Prevention**: Monitor Redis memory usage, set up alerts for connection failures.

---

### Redis Memory Full

**Symptom**: Redis errors, cache evictions, slow performance.

**Diagnosis**:
```bash
# Check Redis memory
docker-compose exec redis redis-cli INFO memory

# Check used memory vs max memory
docker-compose exec redis redis-cli CONFIG GET maxmemory
```

**Resolution**:
```bash
# Option 1: Increase Redis memory (docker-compose.yml)
# redis:
#   command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru

# Option 2: Clear old cache keys
docker-compose exec redis redis-cli FLUSHDB

# Option 3: Restart Redis (clears all data)
docker-compose restart redis
```

**Prevention**: Set appropriate maxmemory, use LRU eviction policy, monitor memory usage.

---

### Redis Fallback to In-Memory

**Symptom**: Application logs show "Redis unavailable, using in-memory fallback".

**Diagnosis**:
```bash
# Check logs
docker-compose logs api | grep -i "redis.*fallback\|redis.*unavailable"

# Check Redis connection
docker-compose exec redis redis-cli ping
```

**Resolution**:
```bash
# Fix Redis connection issue
docker-compose restart redis

# Verify fallback cleared
docker-compose logs api | grep -i "redis.*available"
```

**Prevention**: Monitor Redis health, set up alerts for fallback mode.

---

## 🗄️ Database Connection Failures

### Database Connection Timeout

**Symptom**: Database connection errors, slow queries, timeouts.

**Diagnosis**:
```bash
# Check database connection pool
docker-compose exec api python -c "
from app.db.session import engine
print(f'Pool size: {engine.pool.size()}')
print(f'Checked out: {engine.pool.checkedout()}')
"

# Check active connections
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
SELECT count(*) FROM pg_stat_activity WHERE datname = 'dyn365hunter';
"
```

**Resolution**:
```bash
# Option 1: Increase connection pool (app/config.py)
# db_pool_size: int = 30  # Increase from 20
# db_max_overflow: int = 15  # Increase from 10

# Option 2: Check for connection leaks
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
SELECT pid, now() - query_start AS duration, query 
FROM pg_stat_activity 
WHERE state = 'active' 
ORDER BY duration DESC;
"

# Option 3: Restart application (releases connections)
docker-compose restart api
```

**Prevention**: Monitor connection pool usage, set up alerts for high connection count.

---

### Database Migration Drift

**Symptom**: Alembic reports schema drift, migration fails.

**Diagnosis**:
```bash
# Check for schema drift
docker-compose exec api alembic revision --autogenerate -m "check_drift" --sql

# Compare current schema with models
docker-compose exec api alembic check
```

**Resolution**:
```bash
# Option 1: Create migration for drift
docker-compose exec api alembic revision --autogenerate -m "fix_drift"
# Review generated migration
# Apply migration
docker-compose exec api alembic upgrade head

# Option 2: If drift is expected, stamp current revision
docker-compose exec api alembic stamp head
```

**Prevention**: Always use Alembic for schema changes, test migrations in staging first.

---

### Database Reset Issues

**Symptom**: Missing columns (`tenant_size`, `local_provider`, `dmarc_coverage`), view errors (`leads_ready`), schema mismatches, API errors about undefined columns.

**Root Cause**: Using deprecated `schema.sql` or legacy SQL migrations instead of Alembic for database reset.

**Diagnosis**:
```bash
# Check if G20 columns exist
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
  SELECT column_name FROM information_schema.columns 
  WHERE table_name = 'companies' AND column_name = 'tenant_size';
  SELECT column_name FROM information_schema.columns 
  WHERE table_name = 'domain_signals' AND column_name IN ('local_provider', 'dmarc_coverage');
"

# Check leads_ready view
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "\d+ leads_ready"

# Check for view errors in API logs
docker-compose logs api | grep -i "undefinedcolumn\|does not exist"
```

**Resolution**:
```bash
# ⚠️ DO NOT use schema.sql or legacy migrations
# ✅ Use official reset script
./scripts/reset_db_with_alembic.sh

# Or manually:
# 1. Drop schema
docker-compose exec -T api python -c "
from app.db.session import engine
from sqlalchemy import text
with engine.connect() as conn:
    conn.execute(text('DROP SCHEMA IF EXISTS public CASCADE;'))
    conn.execute(text('CREATE SCHEMA public;'))
    conn.execute(text('GRANT ALL ON SCHEMA public TO dyn365hunter;'))
    conn.execute(text('GRANT ALL ON SCHEMA public TO public;'))
    conn.commit()
print('✅ Schema dropped')
"

# 2. Run Alembic migrations (official way)
docker-compose exec api alembic upgrade head

# 3. Verify schema
docker-compose exec api python -c "
from app.db.session import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT column_name FROM information_schema.columns WHERE table_name = \\'companies\\' AND column_name = \\'tenant_size\\';'))
    print('✅ tenant_size exists' if result.fetchone() else '❌ tenant_size missing')
    result = conn.execute(text('SELECT column_name FROM information_schema.columns WHERE table_name = \\'domain_signals\\' AND column_name IN (\\'local_provider\\', \\'dmarc_coverage\\');'))
    cols = [row[0] for row in result]
    print(f'✅ domain_signals columns: {cols}')
"
```

**Prevention**: 
- ❌ **DO NOT**: Use `schema.sql` or legacy SQL migrations for database reset (outdated, missing G20 columns)
- ❌ **DO NOT**: Combine `schema.sql` with legacy migrations (transaction-unsafe, causes schema mismatches)
- ✅ **DO**: Always use Alembic migrations (`alembic upgrade head`)
- ✅ **DO**: Use `./scripts/reset_db_with_alembic.sh` for database reset
- ✅ **DO**: Verify critical columns after reset (tenant_size, local_provider, dmarc_coverage)

**See**: 
- `docs/reference/PRODUCTION-DEPLOYMENT-GUIDE.md` - Migration Flow section
- `docs/archive/legacy-migrations/README.md` - Why legacy migrations are deprecated

---

### Database Lock/Deadlock

**Symptom**: Queries hanging, deadlock errors in logs.

**Diagnosis**:
```bash
# Check for locks
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
SELECT * FROM pg_locks WHERE NOT granted;
"

# Check for deadlocks
docker-compose logs api | grep -i "deadlock\|lock.*timeout"
```

**Resolution**:
```bash
# Option 1: Kill blocking queries
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE pid IN (
  SELECT blocked_locks.pid 
  FROM pg_locks blocked_locks 
  JOIN pg_locks blocking_locks ON blocked_locks.locktype = blocking_locks.locktype
  WHERE NOT blocked_locks.granted
);
"

# Option 2: Increase transaction timeout (app/db/session.py)
# sessionmaker(bind=engine, expire_on_commit=False, autocommit=False)
# Add: timeout=30
```

**Prevention**: Use proper transaction isolation, avoid long-running transactions.

---

## 📊 Sentry Event Not Appearing

### Sentry DSN Not Set

**Symptom**: Errors not appearing in Sentry dashboard.

**Diagnosis**:
```bash
# Check Sentry DSN
docker-compose exec api env | grep HUNTER_SENTRY_DSN

# Check Sentry initialization in logs
docker-compose logs api | grep -i sentry
```

**Resolution**:
```bash
# Set Sentry DSN in environment
export HUNTER_SENTRY_DSN="https://<key>@<org>.ingest.sentry.io/<project>"

# Or in docker-compose.yml
# environment:
#   HUNTER_SENTRY_DSN: "https://..."

# Restart application
docker-compose restart api
```

**Prevention**: Verify Sentry DSN in environment variables checklist.

---

### Sentry Events Delayed

**Symptom**: Events appear in Sentry but with delay.

**Diagnosis**:
```bash
# Check Sentry SDK configuration
docker-compose logs api | grep -i "sentry.*init"

# Test error generation
docker-compose exec api python - << 'EOF'
from app.core.logging import logger
logger.error("Sentry test", extra={"test": True})
EOF
```

**Resolution**:
```bash
# Sentry uses async transport by default
# Events may be batched and sent periodically
# This is normal behavior

# For immediate sending (not recommended for production):
# Configure Sentry with sync transport (increases latency)
```

**Prevention**: Understand Sentry's async behavior, events may take 1-2 minutes to appear.

---

## ⏱️ Scan Timeouts

### DNS Query Timeout

**Symptom**: Domain scans failing with DNS timeout errors.

**Diagnosis**:
```bash
# Check DNS timeout configuration
grep -r "DNS.*timeout\|dns.*timeout" app/

# Check logs for timeout errors
docker-compose logs api | grep -i "dns.*timeout\|timeout.*dns"
```

**Resolution**:
```bash
# DNS timeout is set to 10s (app/core/analyzer_dns.py)
# If domains consistently timeout:
# 1. Check network connectivity
# 2. Check DNS server availability
# 3. Consider increasing timeout (not recommended)

# For specific problematic domains, skip DNS check
# (requires code change)
```

**Prevention**: Monitor DNS query success rate, set up alerts for high timeout rate.

---

### WHOIS Query Timeout

**Symptom**: WHOIS queries timing out, incomplete domain data.

**Diagnosis**:
```bash
# Check WHOIS timeout configuration
grep -r "WHOIS.*timeout\|whois.*timeout" app/

# Check logs
docker-compose logs api | grep -i "whois.*timeout"
```

**Resolution**:
```bash
# WHOIS timeout is set to 10s (app/core/analyzer_whois.py)
# WHOIS servers can be slow or unresponsive
# This is expected behavior

# Option 1: Accept partial data (WHOIS is optional)
# Option 2: Increase timeout (not recommended, slows down scans)
# Option 3: Use cached WHOIS data (already implemented)
```

**Prevention**: WHOIS timeouts are expected, cache reduces impact.

---

### Bulk Scan Timeout

**Symptom**: Bulk scan jobs timing out, incomplete results.

**Diagnosis**:
```bash
# Check bulk scan progress
curl http://localhost:8000/api/v1/progress/<job-id>

# Check Celery worker logs
docker-compose logs worker | grep -i "timeout\|failed"
```

**Resolution**:
```bash
# Option 1: Increase Celery task timeout
# In app/core/celery_app.py:
# @celery_app.task(time_limit=600)  # 10 minutes

# Option 2: Split bulk scan into smaller batches
# Reduce batch size in bulk_scan_task

# Option 3: Check for stuck tasks
docker-compose exec worker celery -A app.core.celery_app.celery_app inspect active
```

**Prevention**: Monitor bulk scan completion rate, set appropriate timeouts.

---

## 🔑 API Key Issues

### API Key Authentication Failing

**Symptom**: 401 Unauthorized errors, API key not working.

**Diagnosis**:
```bash
# Check API key format
curl -i -H "X-API-Key: <your-key>" http://localhost:8000/api/v1/leads

# Check API key in database
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
SELECT id, name, created_at FROM api_keys LIMIT 5;
"
```

**Resolution**:
```bash
# Option 1: Verify API key is correct
# Check key in database matches request header

# Option 2: Check API key hashing
# API keys are hashed with bcrypt
# Verify hash matches in database

# Option 3: Create new API key
# Use admin endpoint or database directly
```

**Prevention**: Store API keys securely, verify key format before use.

---

### API Key Rate Limiting

**Symptom**: 429 Too Many Requests errors.

**Diagnosis**:
```bash
# Check rate limit configuration
grep -r "rate.*limit\|RATE_LIMIT" app/config.py

# Check rate limit in logs
docker-compose logs api | grep -i "rate.*limit\|429"
```

**Resolution**:
```bash
# Rate limits are per API key
# Default: 100 requests/minute per key

# Option 1: Wait for rate limit to reset (1 minute)
# Option 2: Use multiple API keys for higher throughput
# Option 3: Increase rate limit (requires code change)
```

**Prevention**: Monitor rate limit hits, adjust limits based on usage patterns.

---

## 🔗 Related Documents

- `docs/active/PRODUCTION-DEPLOYMENT-GUIDE.md` - Deployment guide
- `docs/active/PRODUCTION-ENGINEERING-GUIDE-V1.md` - SRE runbook
- `docs/reference/DOCKER-TROUBLESHOOTING.md` - Docker-specific issues
- `docs/active/ROLLBACK-PLAN.md` - Rollback procedures

---

## ✅ Quick Reference

### Common Commands

```bash
# Check health
curl http://localhost:8000/healthz/ready

# Check logs
docker-compose logs -f api | grep -i error

# Check database
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "\dt"

# Check Redis
docker-compose exec redis redis-cli ping

# Check migration
docker-compose exec api alembic current
```

### Emergency Procedures

```bash
# Restart all services
docker-compose restart

# Rollback deployment
docker-compose down
# Restore from backup or checkout previous version
docker-compose up -d

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHDB
```

---

**Last Updated**: 2025-01-28  
**Status**: ✅ **Production Ready**

