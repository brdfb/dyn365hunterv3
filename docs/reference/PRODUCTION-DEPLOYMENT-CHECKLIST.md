# Production Deployment Checklist - Hunter v1.0

**Tarih**: 2025-01-28  
**Versiyon**: v1.0.0  
**Status**: 🔄 **IN PROGRESS** - Production hazırlık aktif  
**Karar**: ✅ **GO** - Production v1.0'a çıkış onaylandı

---

## 📋 Pre-Deployment Checklist

### ✅ Teknik Hazırlık (Tamamlandı)

- [x] P0 Hardening tamamlandı (G19)
- [x] P1 Performance tamamlandı (2025-01-28)
- [x] Stabilization Sprint tamamlandı (3 gün)
- [x] Test Fixes tamamlandı (86 test passing, 0 failures)
- [x] Sales Engine tamamlandı (G21 Phase 2)
- [x] Read-Only Mode tamamlandı (G21 Phase 3)

### 🔄 Deployment Hazırlık (In Progress)

#### Environment Variables
- [ ] Database connection string (`DATABASE_URL`)
- [ ] Redis connection string (`REDIS_URL`)
- [ ] API key secrets (production keys)
- [ ] Sentry DSN (`SENTRY_DSN`)
- [ ] Log level (`LOG_LEVEL=INFO`)
- [ ] Environment (`ENVIRONMENT=production`)
- [ ] Partner Center feature flag (`PARTNER_CENTER_ENABLED=false` - Post-MVP)

#### Database Migration
- [ ] Alembic migration system verified (`alembic current`)
- [ ] Production database backup alındı
- [ ] Migration planı hazır (`alembic upgrade head`)
- [ ] Rollback planı hazır (`alembic downgrade -1`)

#### Health Checks
- [ ] Liveness probe configured (`/healthz/live`)
- [ ] Readiness probe configured (`/healthz/ready`)
- [ ] Startup probe configured (`/healthz/startup`)
- [ ] Health checks test edildi (local)

#### Monitoring & Logging
- [ ] Sentry error tracking configured
- [ ] Structured logging configured
- [ ] Log aggregation configured (ELK or similar)
- [ ] Metrics endpoint verified (`/healthz/metrics`)

#### Infrastructure
- [ ] Redis health check verified
- [ ] Database connection pooling verified
- [ ] API versioning verified (v1 + legacy endpoints)
- [ ] Rate limiting configured (distributed rate limiter)

---

## 🚀 Deployment Steps

### Step 1: Pre-Deployment Verification
```bash
# 1. Health checks
curl http://localhost:8000/healthz/live
curl http://localhost:8000/healthz/ready
curl http://localhost:8000/healthz/startup

# 2. Database migration status
docker-compose exec api alembic current

# 3. Test suite
docker-compose exec api pytest tests/ -v --tb=short
```

### Step 2: Database Backup
```bash
# Production database backup
pg_dump -h <production-db-host> -U <user> -d <database> > backup_pre_v1.0_$(date +%Y%m%d_%H%M%S).sql
```

### Step 3: Database Migration
```bash
# ⚠️ IMPORTANT: Use Alembic only - DO NOT use schema.sql or legacy migrations
# Run Alembic migration
docker-compose exec api alembic upgrade head

# Verify migration
docker-compose exec api alembic current
# Expected: f786f93501ea (head - CSP P-Model)

# Verify critical G20 columns exist
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
  SELECT column_name FROM information_schema.columns 
  WHERE table_name = 'companies' AND column_name = 'tenant_size';
  SELECT column_name FROM information_schema.columns 
  WHERE table_name = 'domain_signals' AND column_name IN ('local_provider', 'dmarc_coverage');
"
```

**Database Reset Policy**:
- ❌ **DO NOT**: Use `schema.sql` or legacy SQL migrations (outdated, missing G20 columns)
- ✅ **DO**: Use `./scripts/reset_db_with_alembic.sh` for database reset
- ✅ **DO**: Always use Alembic migrations for schema changes

### Step 4: Deployment
```bash
# Build and deploy (example for Docker/Kubernetes)
docker-compose build --no-cache api
docker-compose up -d

# Or for Kubernetes
kubectl apply -f k8s/deployment.yaml
kubectl rollout status deployment/dyn365hunter-api
```

### Step 5: Post-Deployment Verification
```bash
# 1. Health checks
curl https://production-url/healthz/live
curl https://production-url/healthz/ready

# 2. Core endpoints
curl https://production-url/api/v1/leads
curl https://production-url/api/v1/scan?domain=example.com

# 3. Sales Engine endpoint
curl https://production-url/api/v1/leads/example.com/sales-summary

# 4. Metrics
curl https://production-url/healthz/metrics
```

---

## 🧪 Smoke Tests

### Core Functionality
- [ ] Health checks passing (`/healthz/live`, `/healthz/ready`, `/healthz/startup`)
- [ ] Leads endpoint working (`GET /api/v1/leads`)
- [ ] Scan endpoint working (`POST /api/v1/scan`)
- [ ] Sales Engine endpoint working (`GET /api/v1/leads/{domain}/sales-summary`)

### Bulk Operations
- [ ] Bulk scan test (10 domain)
- [ ] Rate limiting working (distributed rate limiter)
- [ ] Cache working (Redis cache layer)

### Error Handling
- [ ] 404 errors handled gracefully
- [ ] 500 errors logged to Sentry
- [ ] API key authentication working

---

## 📊 Post-Deployment Monitoring

### First 1 Hour
- [ ] Error rate < 1%
- [ ] Latency P95 < 500ms
- [ ] Health checks passing
- [ ] No critical errors in Sentry

### First 24 Hours
- [ ] Error rate stable
- [ ] Latency stable
- [ ] Cache hit rate > 50%
- [ ] Rate limiting working correctly
- [ ] Database connection pool healthy

---

## 🔄 Rollback Plan

### If Issues Detected

1. **Immediate Rollback**:
   ```bash
   # Kubernetes
   kubectl rollout undo deployment/dyn365hunter-api
   
   # Docker Compose
   docker-compose down
   docker-compose up -d --scale api=0
   ```

2. **Database Rollback** (if needed):
   ```bash
   # Alembic rollback
   docker-compose exec api alembic downgrade -1
   
   # Or restore from backup
   psql -h <production-db-host> -U <user> -d <database> < backup_pre_v1.0_*.sql
   ```

3. **Investigation**:
   - Check Sentry for errors
   - Check logs for issues
   - Check health check status
   - Check database migration status

---

## 📝 Documentation Updates

- [ ] README.md güncelle (production status)
- [ ] CHANGELOG.md güncelle (v1.0.0 release)
- [ ] Production Engineering Guide güncelle
- [ ] Troubleshooting Guide güncelle

---

## ✅ Success Criteria

### Technical
- [x] All P0 items completed
- [x] All P1 items completed
- [x] Stabilization Sprint completed
- [x] Test suite passing (86 tests)

### Operational
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Error tracking active
- [ ] Logging configured
- [ ] Backup strategy in place

### Functional
- [ ] Core endpoints working
- [ ] Sales Engine working
- [ ] Bulk operations working
- [ ] Rate limiting working
- [ ] Cache working

---

**Last Updated**: 2025-01-28  
**Status**: 🔄 **IN PROGRESS** - Production deployment hazırlık aktif

