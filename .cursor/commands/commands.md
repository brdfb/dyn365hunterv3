# Dyn365Hunter MVP - Project Commands

## Setup Dev Environment

Setup development environment with Docker Compose, database migration, and health check.

**Usage:** `/setup-dev` or mention "setup dev environment"

**What it does:**
- Checks Docker/Docker Compose availability
- Copies `.env.example` to `.env` if not exists
- Runs `docker-compose up -d`
- Waits for PostgreSQL healthcheck (max 30s)
- Runs schema migration automatically
- Verifies `/healthz` endpoint
- Prints access URLs

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

**Command:**
```bash
pytest tests/ -v --cov=app/core --cov=app/api
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

**Commands:**
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
