# TODO: G2 - Database Schema & Models

**Date Created**: 2025-11-12
**Status**: In Progress
**Phase**: G2

## Tasks

- [x] Create `app/db/schema.sql` (CREATE TABLE: raw_leads, companies, domain_signals, lead_scores, VIEW: leads_ready)
- [x] Create `app/db/models.py` (SQLAlchemy models: RawLead, Company, DomainSignal, LeadScore)
- [x] Create schema migration script (Python script for automatic migration)
- [x] Update `setup_dev.sh` (schema.sql migration otomatik çalışsın)

## Test/Acceptance

- [ ] `docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "\dt"` → 4 table görünüyor
- [ ] `docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "\dv"` → `leads_ready` VIEW görünüyor
- [ ] Python: `from app.db.models import Company; Company.__table__.columns` → domain UNIQUE constraint var

## Notes

- Schema migration otomatik çalışmalı (Python script veya Alembic)
- Domain UNIQUE key in companies table
- All tables should have proper indexes

## Next Phase

G3: Domain Normalization & Data Files
