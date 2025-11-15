# Legacy SQL Migrations

**Status**: Archived - For Reference Only  
**Date**: 2025-01-28  
**Reason**: Migrated to Alembic migration system

## Overview

These SQL migration files represent the historical schema changes made before Alembic was introduced. They are kept here for:

- **Reference**: Understanding the evolution of the database schema
- **Forensic purposes**: Debugging schema-related issues
- **Documentation**: Historical record of changes

## ⚠️ Important

**DO NOT RUN THESE MIGRATIONS** - They have already been applied to the database.

The current schema state is represented by Alembic base revision: `08f51db8dce0_base_revision`

## Migration Files

| File | Phase | Date | Description |
|------|-------|------|-------------|
| `g16_webhook_enrichment.sql` | G16 | 2025-11-14 | Webhook + Lead Enrichment |
| `g17_notes_tags_favorites.sql` | G17 | 2025-11-14 | Notes, Tags, Favorites (CRM-lite) |
| `g18_rescan_alerts_scoring.sql` | G18 | 2025-11-14 | ReScan + Alerts + Enhanced Scoring |
| `g19_favorites_migration.sql` | G19 | 2025-01-28 | Favorites Migration (Session → User) |
| `g19_users_auth.sql` | G19 | 2025-01-28 | Users & Authentication (Microsoft SSO) |
| `g20_domain_intelligence.sql` | G20 | 2025-01-28 | Domain Intelligence Layer |

## Migration to Alembic

All changes from these migrations are now represented in:
- **Base Revision**: `alembic/versions/08f51db8dce0_base_revision.py`
- **Alembic Status**: `alembic stamp 08f51db8dce0` (applied to dev/prod)

## Future Changes

All future schema changes should be made using Alembic:

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

---

**See Also**:
- `docs/active/P1-ALEMBIC-PREPARATION.md` - Alembic migration preparation
- `alembic/versions/08f51db8dce0_base_revision.py` - Base revision representing current schema

