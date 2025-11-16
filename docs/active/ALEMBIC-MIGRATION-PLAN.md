# Alembic Migration Plan - Production v1.0

**Tarih**: 2025-01-28  
**Versiyon**: v1.0.0  
**Status**: ✅ **Production Ready**  
**Kullanım**: Production deployment sırasında database migration yönetimi

---

## 📋 Overview

Hunter v1.0 uses **Alembic** for database migration management. This document outlines the migration strategy for production deployment.

### Migration System Status

- ✅ **Alembic Setup**: Complete
- ✅ **Base Revision**: `08f51db8dce0` (represents current production schema)
- ✅ **Migration History**: Collapsed history strategy (base revision includes all historical migrations g16-g20)
- ✅ **Legacy Migrations**: Archived in `app/db/migrations/legacy/` (reference only)

---

## 🎯 Pre-Deployment Migration Check

### 1. Check Current Migration Version

```bash
# Using Docker Compose
docker-compose exec api alembic current

# Or directly (if Alembic is installed locally)
alembic current
```

**Expected Output**:
```
08f51db8dce0 (head)
```

### 2. Check Migration History

```bash
# View migration history
docker-compose exec api alembic history

# View specific revision
docker-compose exec api alembic history 08f51db8dce0
```

### 3. Check for Schema Drift

```bash
# Autogenerate to detect schema changes
docker-compose exec api alembic revision --autogenerate -m "check_drift" --sql

# Review the generated SQL (should be empty if no drift)
```

**If drift detected**: Review and create proper migration before deployment.

---

## 🚀 Production Deployment Migration Steps

### Step 1: Pre-Migration Backup

**CRITICAL**: Always backup database before migration.

```bash
# Create backup
pg_dump -h <production-db-host> -U <user> -d <database> > backup_pre_migration_$(date +%Y%m%d_%H%M%S).sql

# Or using Docker
docker exec -e PGPASSWORD=<password> <postgres-container> \
    pg_dump -U <user> -d <database> > backup_pre_migration_$(date +%Y%m%d_%H%M%S).sql
```

**Backup Location**: Store in `backups/` directory with timestamp.

### Step 2: Check Current Version

```bash
# Check current migration version in production
docker-compose exec api alembic current
```

**Expected**: Should match base revision `08f51db8dce0` or be at head.

### Step 3: Run Migration

```bash
# Upgrade to head (latest migration)
docker-compose exec api alembic upgrade head

# Verify migration
docker-compose exec api alembic current
```

**Expected Output**:
```
08f51db8dce0 (head)
```

### Step 4: Verify Migration Success

```bash
# Check migration status
docker-compose exec api alembic current

# Test database connectivity
docker-compose exec api python -c "from app.db.session import SessionLocal; db = SessionLocal(); db.execute('SELECT 1'); print('✅ Database connection OK')"
```

---

## 🔄 Migration Scenarios

### Scenario 1: Fresh Production Database

**Situation**: New production database, no existing schema.

**Steps**:
1. Create database
2. Run `alembic upgrade head` (will create all tables)
3. Verify schema matches expected state

### Scenario 2: Existing Production Database

**Situation**: Production database exists, needs migration to v1.0.

**Steps**:
1. Backup database
2. Check current migration version
3. Run `alembic upgrade head`
4. Verify migration success

### Scenario 3: Schema Drift Detected

**Situation**: Production schema differs from expected state.

**Steps**:
1. **STOP**: Do not proceed with deployment
2. Investigate drift:
   ```bash
   alembic revision --autogenerate -m "detect_drift" --sql > drift_analysis.sql
   ```
3. Review `drift_analysis.sql` to understand differences
4. Create proper migration to align schema
5. Test migration in staging environment
6. Proceed with deployment after drift resolved

---

## 📊 Migration Verification Checklist

### Pre-Migration
- [ ] Database backup created
- [ ] Current migration version checked
- [ ] Schema drift check completed (no drift detected)
- [ ] Migration plan reviewed

### Post-Migration
- [ ] Migration completed successfully (`alembic current` shows head)
- [ ] Database connection test passed
- [ ] Core tables exist (companies, domain_signals, raw_leads, etc.)
- [ ] Application health checks passing
- [ ] Smoke tests passing

---

## 🔙 Rollback Procedures

### Rollback to Previous Migration

```bash
# Rollback one migration
docker-compose exec api alembic downgrade -1

# Rollback to specific revision
docker-compose exec api alembic downgrade <revision_id>

# Rollback to base (if needed)
docker-compose exec api alembic downgrade base
```

### Rollback with Database Restore

If migration fails and rollback is not possible:

1. **Stop application**
2. **Restore database from backup**:
   ```bash
   psql -h <production-db-host> -U <user> -d <database> < backup_pre_migration_*.sql
   ```
3. **Verify database state**
4. **Restart application**

**See**: `docs/active/ROLLBACK-PLAN.md` for detailed rollback procedures.

---

## 🛡️ Safety Measures

### 1. Always Backup Before Migration

```bash
# Automated backup (included in deploy_production.sh)
backup_database() {
    local backup_file="backups/backup_pre_${VERSION}_${TIMESTAMP}.sql"
    pg_dump ... > "$backup_file"
}
```

### 2. Test Migration in Staging First

- Run migration in staging environment
- Verify application works correctly
- Only then proceed to production

### 3. Monitor Migration Progress

```bash
# Watch migration logs
docker-compose logs -f api | grep -i alembic

# Check database during migration
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "\dt"
```

### 4. Have Rollback Plan Ready

- Know how to rollback before starting migration
- Have database backup accessible
- Test rollback procedure in staging

---

## 📝 Creating New Migrations (Future)

### For Post-MVP Features

When creating new migrations after v1.0:

```bash
# 1. Create new migration
docker-compose exec api alembic revision --autogenerate -m "add_new_feature"

# 2. Review generated migration file
# Location: alembic/versions/XXXX_add_new_feature.py

# 3. Test migration
docker-compose exec api alembic upgrade head

# 4. Test rollback
docker-compose exec api alembic downgrade -1

# 5. Commit migration file to version control
```

### Migration Best Practices

1. **Always review autogenerated migrations** - Alembic may miss some changes
2. **Test both upgrade and downgrade** - Ensure rollback works
3. **Use descriptive migration names** - Clear purpose in name
4. **Keep migrations small** - One logical change per migration
5. **Document breaking changes** - Note any data migration requirements

---

## 🔍 Troubleshooting

### Migration Fails with "Target database is not up to date"

**Cause**: Database schema is ahead of migration history.

**Solution**:
```bash
# Check current state
alembic current

# If database is ahead, stamp it to current revision
alembic stamp head
```

### Migration Fails with "Can't locate revision identified by 'XXXX'"

**Cause**: Migration file missing or migration history corrupted.

**Solution**:
1. Check migration files exist: `ls alembic/versions/`
2. Verify migration history: `alembic history`
3. If needed, restore from backup and re-run migration

### Schema Drift After Migration

**Cause**: Manual database changes or migration didn't apply correctly.

**Solution**:
1. Detect drift: `alembic revision --autogenerate --sql`
2. Create migration to fix drift
3. Test in staging
4. Apply to production

---

## 📚 Related Documents

- `docs/active/PRODUCTION-DEPLOYMENT-CHECKLIST.md` - Full deployment checklist
- `docs/active/ROLLBACK-PLAN.md` - Rollback procedures
- `alembic.ini` - Alembic configuration
- `alembic/env.py` - Alembic environment setup
- `alembic/versions/` - Migration files directory

---

## ✅ Production v1.0 Migration Status

**Current State**: ✅ **Ready for Production**

- Base revision: `08f51db8dce0`
- Migration history: Clean (collapsed history strategy)
- No pending migrations for v1.0
- Rollback tested: ✅

**Deployment Command**:
```bash
docker-compose exec api alembic upgrade head
```

**Expected Result**: Database schema matches v1.0 requirements.

---

**Last Updated**: 2025-01-28  
**Status**: ✅ **Production Ready**

