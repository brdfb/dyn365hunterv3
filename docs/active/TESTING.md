# Testing Guide

## Running Tests

### Option 1: In Docker Container (Recommended)

Tests should be run inside Docker container to ensure database connectivity.

```bash
# Start containers (if not running)
docker-compose up -d

# Run all tests
docker-compose exec api pytest tests/ -v

# Run specific test file
docker-compose exec api pytest tests/test_priority.py -v

# Run with coverage
docker-compose exec api pytest tests/ -v --cov=app --cov-report=term
```

### Option 2: Using Test Script

```bash
# Run tests with automatic container check
bash scripts/run-tests-docker.sh
```

### Option 3: Local Testing (Without Database)

Some tests can run locally without database:

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/WSL
# or
.venv\Scripts\activate     # Windows

# Run unit tests (no database required)
pytest tests/test_priority.py -v
pytest tests/test_scorer_rules.py -v
pytest tests/test_scan_single.py -v
pytest tests/test_ingest_csv.py -v
```

**Note:** Integration tests (`test_api_endpoints.py`) require database and should be run in Docker container.

## Test Structure

### Unit Tests (No Database Required)
- `tests/test_priority.py` - Priority score calculation
- `tests/test_scorer_rules.py` - Scoring rules and segment logic
- `tests/test_scan_single.py` - DNS/WHOIS analyzer (with mocks)
- `tests/test_ingest_csv.py` - CSV parsing and normalization

### Integration Tests (Database Required)
- `tests/test_api_endpoints.py` - API endpoint tests
  - Requires PostgreSQL connection
  - Uses transaction rollback for test isolation
  - Tests: ingest, scan, leads, dashboard endpoints

## Test Database Configuration

Tests use environment variable `TEST_DATABASE_URL` or `DATABASE_URL`:

```bash
# In Docker container (automatic)
DATABASE_URL=postgresql://dyn365hunter:password123@postgres:5432/dyn365hunter

# Local testing (if PostgreSQL running locally)
TEST_DATABASE_URL=postgresql://dyn365hunter:password123@localhost:5432/dyn365hunter
```

## Troubleshooting

### Tests Skipped: "Test database not available"

**Cause:** Database connection not available.

**Solution:**
1. Run tests in Docker container:
   ```bash
   docker-compose exec api pytest tests/ -v
   ```

2. Or start local PostgreSQL and set `TEST_DATABASE_URL`.

### Import Errors (e.g., `httpx` not found)

**Cause:** Dependencies not installed in container.

**Solution:**
1. Rebuild container:
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. Or install missing dependency:
   ```bash
   docker-compose exec api pip install httpx==0.25.2
   ```

### Container Not Running

**Solution:**
```bash
# Start containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

## Expected Test Results

When running in Docker container with database:
- **Total tests:** ~90 tests
- **Passed:** All tests should pass
- **Skipped:** 0 (if database available)

When running locally without database:
- **Unit tests:** ~70 tests pass
- **Integration tests:** ~20 tests skipped (expected)

## CI/CD

Tests are automatically run in GitHub Actions CI pipeline:
- All dependencies installed
- PostgreSQL service available
- All tests should pass

See `.github/workflows/ci.yml` for CI configuration.

