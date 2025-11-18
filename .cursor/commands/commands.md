# Dyn365Hunter - Project Commands

**Version:** 1.0.0  
**Last Updated:** 2025-01-30

## Setup Dev Environment

Setup development environment with Docker Compose, database migration, and health check.

**Usage:** `/setup-dev` or mention "setup dev environment"

**What it does:**
- Checks Docker/Docker Compose availability
- Copies `.env.example` to `.env` if not exists
- Runs `docker-compose up -d` (PostgreSQL, Redis, API, Worker)
- Waits for PostgreSQL and Redis healthcheck (max 30s)
- Runs schema migration automatically
- Verifies `/healthz` endpoint
- Prints access URLs (API, Mini UI)

**Command:**
```bash
bash setup_dev.sh
```

---

## Run Tests

Run the test suite with pytest.

**Usage:** `/run-tests` or mention "run tests"

**What it does:**
- Runs all tests in `tests/` directory
- Shows test coverage
- Validates core modules (normalizer, analyzer, scorer, ingest)

**Command (Docker - Recommended):**
```bash
bash scripts/run-tests-docker.sh
# Or directly:
docker-compose exec api pytest tests/ -v --tb=short
```

**Command (Local - requires venv):**
```bash
# Activate venv first
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Run tests
pytest tests/ -v --cov=app --cov-report=term
```

---

## Demo Scenario

Execute the MVP demo scenario: 3 domain ingest → scan → leads query.

**Usage:** `/demo` or mention "demo scenario"

**What it does:**
1. Ingests 3 domains: `example.com`, `google.com`, `microsoft.com`
2. Scans each domain (DNS + WHOIS + scoring)
3. Queries leads with filter: `segment=Migration&min_score=70`
4. Verifies ≥1 Migration lead with score ≥70

**Command (Script - Recommended):**
```bash
bash scripts/sales-demo.sh
```

**Commands (Manual):**
```bash
# Ingest domains
curl -X POST http://localhost:8000/ingest/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "company_name": "Example Inc"}'

curl -X POST http://localhost:8000/ingest/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "google.com", "company_name": "Google"}'

curl -X POST http://localhost:8000/ingest/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "microsoft.com", "company_name": "Microsoft"}'

# Scan domains
curl -X POST http://localhost:8000/scan/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'

curl -X POST http://localhost:8000/scan/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "google.com"}'

curl -X POST http://localhost:8000/scan/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "microsoft.com"}'

# Query leads
curl "http://localhost:8000/leads?segment=Migration&min_score=70"
```

---

## Check Health

Check API health and database connection.

**Usage:** `/health` or mention "check health"

**What it does:**
- Tests `/healthz` endpoint
- Verifies database connection
- Returns status: `{"status": "ok", "database": "connected"}`

**Command:**
```bash
curl http://localhost:8000/healthz
```

---

## Reset Database

Reset the database (WARNING: deletes all data).

**Usage:** `/reset-db` or mention "reset database"

**What it does:**
- Stops containers
- Removes volumes (deletes data)
- Restarts containers
- Runs schema migration

**Command:**
```bash
docker-compose down -v && docker-compose up -d && sleep 5 && docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -f /app/db/schema.sql
```

---

## View Logs

View FastAPI application logs.

**Usage:** `/logs` or mention "view logs"

**What it does:**
- Shows real-time logs from FastAPI container
- Filters for errors/warnings

**Command:**
```bash
docker-compose logs -f api
```

---

## Start Celery Worker

Start Celery worker for async task processing (bulk scan, rescan, etc.).

**Usage:** `/start-worker` or mention "start celery worker"

**What it does:**
- Starts Celery worker for async tasks
- Required for bulk scan and rescan operations
- Processes tasks from Redis queue

**Command:**
```bash
bash scripts/start_celery_worker.sh
# Or directly:
docker-compose exec worker celery -A app.core.celery_app worker --loglevel=info
```

**Note:** Worker is automatically started by `docker-compose up -d` if configured in `docker-compose.yml`.

---

## Bulk Scan

Create a bulk scan job for multiple domains (async).

**Usage:** `/bulk-scan` or mention "bulk scan"

**What it does:**
- Creates async job for scanning multiple domains
- Returns job_id for progress tracking
- Max 1000 domains per job

**Command:**
```bash
# Create bulk scan job
curl -X POST http://localhost:8000/scan/bulk \
  -H "Content-Type: application/json" \
  -d '{"domain_list": ["example.com", "google.com", "microsoft.com"]}'

# Check progress (use job_id from response)
curl "http://localhost:8000/scan/bulk/{job_id}"

# Get results (when completed)
curl "http://localhost:8000/scan/bulk/{job_id}/results"
```

---

## Export Leads

Export leads to CSV or Excel format.

**Usage:** `/export-leads` or mention "export leads"

**What it does:**
- Exports leads with optional filters (segment, min_score, provider)
- Supports CSV and Excel formats
- Timestamped filename

**Command:**
```bash
# CSV export (default)
curl "http://localhost:8000/leads/export?format=csv&segment=Migration&min_score=70" -o leads.csv

# Excel export
curl "http://localhost:8000/leads/export?format=xlsx&segment=Migration&min_score=70" -o leads.xlsx
```

---

## Mini UI

Access the web interface for demo and internal use.

**Usage:** `/mini-ui` or mention "open mini ui"

**What it does:**
- Opens web interface in browser
- CSV/Excel upload
- Single domain scan
- Leads table with filters
- CSV export

**Command:**
Open in browser: `http://localhost:8000/mini-ui/`

---

## ReScan Domain

Re-scan a domain and detect changes (G18).

**Usage:** `/rescan` or mention "rescan domain"

**What it does:**
- Re-scans domain (DNS + WHOIS)
- Detects changes (MX, DMARC, score)
- Creates alerts for detected changes

**Command:**
```bash
# Single domain rescan
curl -X POST http://localhost:8000/scan/example.com/rescan

# Bulk rescan
curl -X POST "http://localhost:8000/scan/bulk/rescan?domain_list=example.com,google.com"
```

---

## Partner Center Sync

Manually trigger Partner Center referral synchronization (Task 2.4 - 2025-01-30).

**Usage:** `/sync-referrals` or mention "sync partner center referrals"

**What it does:**
- Triggers manual sync of referrals from Partner Center
- Enqueues Celery task for background processing
- Returns task_id for monitoring
- Requires feature flag `partner_center_enabled=True` (disabled by default, MVP-safe)

**Command:**
```bash
# Manual sync (requires feature flag enabled)
curl -X POST http://localhost:8000/api/referrals/sync \
  -H "Content-Type: application/json"

# Response: {"task_id": "abc123", "status": "queued"}
```

**Note:** 
- Background sync runs automatically via Celery Beat (10 min prod, 30s dev)
- Manual sync is optional (Task 2.5 Aşama 3 - not implemented yet)
- Feature flag: `HUNTER_PARTNER_CENTER_ENABLED=false` (default: disabled)
