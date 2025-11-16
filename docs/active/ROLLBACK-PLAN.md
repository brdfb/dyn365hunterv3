# Rollback Plan - Production v1.0

**Tarih**: 2025-01-28  
**Versiyon**: v1.0.0  
**Status**: ✅ **Production Ready**  
**Kullanım**: Production deployment sonrası sorun durumunda rollback prosedürleri

---

## 🎯 Rollback Strategy

Hunter v1.0 deployment uses a **multi-layer rollback strategy**:

1. **Application Rollback** - Revert to previous Docker image
2. **Database Migration Rollback** - Revert Alembic migrations
3. **Database Restore** - Restore from backup (last resort)

---

## 🚨 When to Rollback

### Immediate Rollback Triggers

- ❌ Health checks failing after deployment
- ❌ Critical errors in application logs
- ❌ Database migration failures
- ❌ API endpoints returning 500 errors
- ❌ Smoke tests failing
- ❌ High error rate in Sentry (>5% of requests)

### Decision Matrix

| Issue Type | Severity | Rollback Method | Time to Rollback |
|------------|----------|-----------------|------------------|
| Health checks fail | Critical | Application Rollback | < 5 minutes |
| Database migration fails | Critical | Database Restore | < 15 minutes |
| API errors (>10%) | High | Application Rollback | < 10 minutes |
| Performance degradation | Medium | Monitor first, rollback if persists | < 30 minutes |
| Minor bugs | Low | Hotfix instead of rollback | N/A |

---

## 🔄 Rollback Procedures

### Method 1: Application Rollback (Docker/Kubernetes)

**Use Case**: Application code issues, health checks failing, API errors.

**Time**: < 5 minutes

#### Docker Compose

```bash
# 1. Stop current deployment
docker-compose down

# 2. Checkout previous version (if using git)
git checkout <previous-version-tag>
# Or use previous Docker image
docker pull <registry>/hunter:<previous-version>

# 3. Deploy previous version
docker-compose up -d

# 4. Verify rollback
curl http://localhost:8000/healthz/live
curl http://localhost:8000/healthz/ready
```

#### Kubernetes

```bash
# 1. Rollback deployment
kubectl rollout undo deployment/dyn365hunter-api

# 2. Check rollback status
kubectl rollout status deployment/dyn365hunter-api

# 3. Verify rollback
kubectl get pods -l app=dyn365hunter-api
curl https://production-url/healthz/live
```

---

### Method 2: Database Migration Rollback (Alembic)

**Use Case**: Database migration issues, schema problems.

**Time**: < 10 minutes

**Prerequisites**:
- Database backup exists
- Alembic migration history intact

#### Rollback Steps

```bash
# 1. Check current migration version
docker-compose exec api alembic current

# 2. Rollback one migration
docker-compose exec api alembic downgrade -1

# 3. Verify rollback
docker-compose exec api alembic current

# 4. Test application
curl http://localhost:8000/healthz/ready
```

#### Rollback to Specific Revision

```bash
# Rollback to specific revision
docker-compose exec api alembic downgrade <revision_id>

# Example: Rollback to base
docker-compose exec api alembic downgrade base
```

**⚠️ Warning**: Database migration rollback may cause data loss if migration included data transformations. Always check migration file before rollback.

---

### Method 3: Database Restore (Last Resort)

**Use Case**: Database corruption, migration rollback not possible, critical data issues.

**Time**: < 15 minutes (depends on database size)

**Prerequisites**:
- Database backup exists (created before deployment)
- Application stopped

#### Restore Steps

```bash
# 1. Stop application
docker-compose down

# 2. Drop current database (if needed)
docker-compose exec postgres psql -U dyn365hunter -c "DROP DATABASE IF EXISTS dyn365hunter;"
docker-compose exec postgres psql -U dyn365hunter -c "CREATE DATABASE dyn365hunter;"

# 3. Restore from backup
docker-compose exec -T postgres psql -U dyn365hunter -d dyn365hunter < backups/backup_pre_v1.0_YYYYMMDD_HHMMSS.sql

# Or using pg_restore (if backup is in custom format)
docker-compose exec -T postgres pg_restore -U dyn365hunter -d dyn365hunter < backups/backup_pre_v1.0_YYYYMMDD_HHMMSS.dump

# 4. Verify database
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "\dt"

# 5. Restart application
docker-compose up -d

# 6. Verify application
curl http://localhost:8000/healthz/ready
```

#### Restore from Remote Backup

```bash
# If backup is on remote server
scp user@backup-server:/path/to/backup.sql ./backups/
docker-compose exec -T postgres psql -U dyn365hunter -d dyn365hunter < backups/backup.sql
```

---

## 📋 Rollback Checklist

### Pre-Rollback

- [ ] Identify issue and confirm rollback is needed
- [ ] Notify team (if applicable)
- [ ] Locate backup file (if database restore needed)
- [ ] Check current application version
- [ ] Check current migration version (if database rollback)

### During Rollback

- [ ] Stop application (if needed)
- [ ] Execute rollback procedure
- [ ] Monitor rollback progress
- [ ] Verify rollback success

### Post-Rollback

- [ ] Verify health checks passing
- [ ] Run smoke tests
- [ ] Check application logs for errors
- [ ] Verify database state (if database rollback)
- [ ] Monitor error rate (Sentry)
- [ ] Document rollback reason and procedure used

---

## 🔍 Verification Steps

### After Application Rollback

```bash
# 1. Health checks
curl http://localhost:8000/healthz/live
curl http://localhost:8000/healthz/ready
curl http://localhost:8000/healthz/startup

# 2. Core endpoints
curl http://localhost:8000/api/v1/leads
curl http://localhost:8000/api/v1/scan?domain=example.com

# 3. Check logs
docker-compose logs api | tail -50

# 4. Check Sentry (if configured)
# Verify error rate returned to normal
```

### After Database Rollback

```bash
# 1. Verify migration version
docker-compose exec api alembic current

# 2. Verify database schema
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "\dt"

# 3. Test database queries
docker-compose exec api python -c "from app.db.session import SessionLocal; db = SessionLocal(); result = db.execute('SELECT COUNT(*) FROM companies'); print(f'Companies: {result.scalar()}')"

# 4. Verify application
curl http://localhost:8000/healthz/ready
```

### After Database Restore

```bash
# 1. Verify database restored
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "\dt"

# 2. Check data integrity
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "SELECT COUNT(*) FROM companies;"
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "SELECT COUNT(*) FROM domain_signals;"

# 3. Verify application
curl http://localhost:8000/healthz/ready
curl http://localhost:8000/api/v1/leads
```

---

## 🛡️ Prevention Measures

### Pre-Deployment

- ✅ Test deployment in staging environment
- ✅ Run smoke tests before production deployment
- ✅ Create database backup before migration
- ✅ Verify rollback procedure works in staging

### During Deployment

- ✅ Monitor deployment progress
- ✅ Watch health checks during deployment
- ✅ Monitor error logs in real-time
- ✅ Have rollback command ready

### Post-Deployment

- ✅ Run smoke tests immediately after deployment
- ✅ Monitor error rate for first 30 minutes
- ✅ Check Sentry for new errors
- ✅ Verify all critical endpoints working

---

## 📊 Rollback Decision Tree

```
Deployment Issue Detected
    │
    ├─ Health checks failing?
    │   └─ YES → Application Rollback (Method 1)
    │
    ├─ Database migration failed?
    │   └─ YES → Database Migration Rollback (Method 2)
    │       └─ Rollback fails?
    │           └─ YES → Database Restore (Method 3)
    │
    ├─ API errors > 10%?
    │   └─ YES → Application Rollback (Method 1)
    │
    └─ Minor issues?
        └─ Monitor and hotfix instead of rollback
```

---

## 📝 Rollback Documentation

### After Rollback

Document the following:

1. **Issue Description**: What went wrong?
2. **Rollback Method**: Which method was used?
3. **Rollback Time**: How long did it take?
4. **Root Cause**: Why did the issue occur?
5. **Prevention**: How to prevent in future?
6. **Post-Rollback Actions**: What needs to be fixed?

**Template**:
```markdown
## Rollback Report - YYYY-MM-DD HH:MM

**Issue**: [Description]
**Severity**: [Critical/High/Medium]
**Rollback Method**: [Application/Database Migration/Database Restore]
**Rollback Time**: [X minutes]
**Root Cause**: [Analysis]
**Prevention**: [Actions to take]
**Status**: [Resolved/Pending]
```

---

## 🔗 Related Documents

- `docs/active/PRODUCTION-DEPLOYMENT-CHECKLIST.md` - Deployment checklist
- `docs/active/ALEMBIC-MIGRATION-PLAN.md` - Migration procedures
- `scripts/deploy_production.sh` - Deployment script (includes backup)
- `docs/active/PRODUCTION-ENGINEERING-GUIDE-V1.md` - SRE runbook

---

## ✅ Production v1.0 Rollback Readiness

**Status**: ✅ **Ready**

- Application rollback tested: ✅
- Database migration rollback tested: ✅
- Database restore procedure documented: ✅
- Backup strategy in place: ✅

**Backup Location**: `backups/backup_pre_v1.0_YYYYMMDD_HHMMSS.sql`

**Rollback Time Estimates**:
- Application Rollback: < 5 minutes
- Database Migration Rollback: < 10 minutes
- Database Restore: < 15 minutes

---

**Last Updated**: 2025-01-28  
**Status**: ✅ **Production Ready**

