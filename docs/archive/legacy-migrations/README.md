# Legacy SQL Migrations - Historical Reference Only

**Status**: ⚠️ **DEPRECATED - DO NOT USE**

These SQL migration files are kept for historical reference only. They have been ported to Alembic migrations and should **NOT** be used for database setup or reset.

## Migration Files

- `g16_webhook_enrichment.sql` - Webhook infrastructure (G16)
- `g17_notes_tags_favorites.sql` - CRM-lite features (G17)
- `g18_rescan_alerts_scoring.sql` - Rescan, alerts, scoring (G18)
- `g19_favorites_migration.sql` - Favorites migration (G19)
- `g19_users_auth.sql` - User authentication (G19)
- `g20_domain_intelligence.sql` - Domain intelligence (G20)

## Why These Are Deprecated

1. **Alembic is the official migration system** (v1.0+)
2. These SQL files are **not transaction-safe** and can fail mid-execution
3. They are **out of sync** with current Alembic migrations
4. Using them can cause **schema mismatches** (e.g., missing G20 columns)

## Official Way to Reset Database

```bash
# Use the official reset script
./scripts/reset_db_with_alembic.sh

# Or manually:
# 1. Drop schema: DROP SCHEMA public CASCADE; CREATE SCHEMA public;
# 2. Run Alembic: alembic upgrade head
```

## When to Reference These Files

- **Historical context**: Understanding what changes were made in each phase
- **Debugging**: If you need to see the original SQL for a specific feature
- **Documentation**: Reference for migration history

## ⚠️ DO NOT

- ❌ Run these files directly (`psql -f ...`)
- ❌ Use them for database setup
- ❌ Combine them with `schema.sql` for reset
- ❌ Reference them in production runbooks

## ✅ DO

- ✅ Use Alembic migrations for all database changes
- ✅ Use `./scripts/reset_db_with_alembic.sh` for database reset
- ✅ Reference Alembic migration files in `alembic/versions/` for current schema

---

**Last Updated**: 2025-01-29  
**Reason**: Migration to pure Alembic approach for v1.0+

