# Dyn365Hunter MVP

Lead intelligence engine for domain-based analysis and rule-based scoring.

[![CI/CD Pipeline](https://github.com/brdfb/dyn365hunterv3/actions/workflows/ci.yml/badge.svg)](https://github.com/brdfb/dyn365hunterv3/actions/workflows/ci.yml)
[![Code Quality](https://github.com/brdfb/dyn365hunterv3/actions/workflows/lint.yml/badge.svg)](https://github.com/brdfb/dyn365hunterv3/actions/workflows/lint.yml)

## Overview

Dyn365Hunter MVP is a FastAPI-based application that analyzes domains for lead intelligence. It performs DNS/WHOIS analysis and applies rule-based scoring to identify potential migration opportunities.

**Target**: ≤2 minute "kahvelik" analysis flow for sales team.

## Features

### Core Functionality
- ✅ Docker Compose setup with PostgreSQL and FastAPI
- ✅ Database schema with 5 tables (companies, domain_signals, lead_scores, raw_leads, provider_change_history)
- ✅ Domain normalization (punycode, www stripping, email/URL extraction)
- ✅ Provider mapping (M365, Google, Yandex, Zoho, Amazon, SendGrid, Mailgun, Hosting, Local, Unknown)
- ✅ Rule-based scoring engine with segment classification
- ✅ Domain ingestion (CSV + Excel + single domain endpoints)
- ✅ Excel/CSV column auto-detection for OSB files

### Analysis & Scoring
- ✅ DNS analysis (MX/SPF/DKIM/DMARC with 10s timeout)
- ✅ WHOIS lookup (graceful fail with 5s timeout)
- ✅ Generic email generation for domains
- ✅ Email validation (syntax, MX, optional SMTP)
- ✅ Priority score calculation for lead prioritization

### Data Quality & Tracking
- ✅ **Provider change tracking** - Automatic detection and history logging when domains switch providers
- ✅ **Duplicate prevention** - Automatic cleanup of duplicate LeadScore and DomainSignal records
- ✅ **Domain validation** - Enhanced validation to filter invalid domains (nan, web sitesi, etc.)

### API & UI
- ✅ Lead segmentation API with filtering
- ✅ Dashboard endpoint with aggregated statistics
- ✅ CSV/Excel export endpoint (`GET /leads/export`) - Export leads with filters
- ✅ Mini UI (HTML + Vanilla JS) - Simple web interface for demo and internal use
- ✅ **Progress tracking** - Real-time progress updates for CSV ingestion and scanning operations
- ✅ **Bulk Scan** - Async bulk domain scanning with progress tracking (G15)
- ✅ **G19: Microsoft SSO Authentication** - Azure AD integration with OAuth 2.0 flow
- ✅ **G19: UI Upgrade** - Sorting, pagination, and full-text search for leads table
- ✅ **G19: Dashboard KPI** - New `/dashboard/kpis` endpoint with high priority leads count
- ✅ **G19: Score Breakdown** - Detailed score analysis with modal UI

## Tech Stack

- **Backend**: FastAPI (Python 3.10)
- **Database**: PostgreSQL 15
- **Queue**: Celery + Redis
- **DNS Analysis**: dnspython
- **WHOIS**: python-whois
- **Deployment**: Docker Compose

## Quick Start

### Prerequisites

**Recommended:**
- Docker Desktop (with WSL2 integration)
- WSL2 (Ubuntu 22.04 or later)
- Git

**Alternative (not recommended):**
- Docker Desktop (Windows)
- Git Bash or PowerShell
- Python 3.10+ (for local testing)

> 💡 **Recommendation:** Use WSL2 for best performance and production-like environment. See [Development Environment Guide](docs/active/DEVELOPMENT-ENVIRONMENT.md) for details.

### Setup

1. **Clone the repository:**
   
   **In WSL (Recommended):**
   ```bash
   cd ~/projects
   git clone https://github.com/brdfb/dyn365hunterv3.git
   cd dyn365hunterv3
   ```
   
   **In Windows (Git Bash):**
   ```bash
   git clone https://github.com/brdfb/dyn365hunterv3.git
   cd dyn365hunterv3
   ```
   
   **If project is already in Windows (`C:\CursorPro\DomainHunterv3`):**
   ```bash
   # In WSL, use Windows path:
   cd /mnt/c/CursorPro/DomainHunterv3
   # Or copy to Linux file system for better performance:
   cp -r /mnt/c/CursorPro/DomainHunterv3 ~/projects/dyn365hunterv3
   cd ~/projects/dyn365hunterv3
   ```

2. **Setup Python virtual environment (optional, recommended for local development):**
   
   **For Windows (Git Bash, CMD, PowerShell):**
   ```bash
   bash setup_venv.sh
   source .venv/Scripts/activate  # Git Bash
   # or
   .venv\Scripts\activate.bat     # CMD
   # or
   .venv\Scripts\Activate.ps1     # PowerShell
   ```
   
   **For WSL/Linux:**
   ```bash
   bash setup_venv.sh
   source .venv/bin/activate
   ```
   
   **Note:** If `python3-venv` is not installed, run: `sudo apt update && sudo apt install python3-venv`
   
   **Troubleshooting:** See [WSL Guide](docs/active/WSL-GUIDE.md) for common issues and solutions.

3. **Run setup script:**
   ```bash
   bash setup_dev.sh
   # Or with venv: bash setup_dev.sh --with-venv
   ```

   This will:
   - Check Docker availability
   - Create `.env` from `.env.example`
   - Start Docker Compose services (PostgreSQL, Redis, API, Worker)
   - Wait for PostgreSQL and Redis to be ready
   - Run database schema migration
   - Verify `/healthz` endpoint

4. **Verify installation:**
   ```bash
   curl http://localhost:8000/healthz
   ```

   Expected response:
   ```json
   {
     "status": "ok",
     "database": "connected",
     "environment": "development"
   }
   ```

## Mini UI

A simple web interface for demo and internal use:

**Access**: `http://localhost:8000/mini-ui/`

**Features**:
- CSV/Excel file upload
- Single domain scan (with auto-ingest)
- Leads table with filters (segment, min score, provider)
- CSV export
- Dashboard statistics (KPI)

**Documentation**: See [mini-ui/README-mini-ui.md](mini-ui/README-mini-ui.md)

---

## API Endpoints

**Interactive API Documentation:**
- Swagger UI: `http://localhost:8000/docs` (interactive API explorer)
- ReDoc: `http://localhost:8000/redoc` (alternative documentation format)
- OpenAPI JSON: `http://localhost:8000/openapi.json` (machine-readable schema)

### Health Check
- `GET /healthz` - Health check and database connection status

### Ingest
- `POST /ingest/domain` - Ingest single domain
  - Request body: `{"domain": "example.com", "company_name": "Example Inc", "email": "user@example.com", "website": "https://example.com"}`
  - Returns: `{"domain": "example.com", "company_id": 1, "message": "Domain ingested successfully"}`
- `POST /ingest/csv` - Ingest domains from CSV or Excel file
  - Multipart form data with CSV (.csv) or Excel (.xlsx, .xls) file
  - Query parameter: `auto_detect_columns` (optional, default: false) - Auto-detect company/domain columns for OSB Excel files
  - Required column: `domain` (when `auto_detect_columns=false`)
  - Optional columns: `company_name`, `email`, `website`
  - When `auto_detect_columns=true`: Automatically detects company and domain columns using heuristics
  - Returns: `{"ingested": 5, "total_rows": 5, "errors": null}`

### Scan
- `POST /scan/domain` - Analyze single domain (DNS + WHOIS + scoring)
  - Request body: `{"domain": "example.com"}`
  - Returns: `{"domain": "example.com", "score": 75, "segment": "Migration", "reason": "...", "provider": "M365", "mx_root": "outlook.com", "spf": true, "dkim": true, "dmarc_policy": "reject", "scan_status": "success"}`
  - Performs DNS analysis (MX, SPF, DKIM, DMARC) and WHOIS lookup
  - Calculates readiness score and determines segment
- `POST /scan/bulk` - Create bulk scan job for multiple domains (async)
  - Request body: `{"domain_list": ["example.com", "google.com", "microsoft.com"]}`
  - Returns: `{"job_id": "uuid", "message": "Bulk scan job created successfully", "total": 3}`
  - Creates async job that scans all domains in background
  - Max 1000 domains per job
  - Rate limiting: DNS (10 req/s), WHOIS (5 req/s)
  - Use `GET /scan/bulk/{job_id}` to check progress
- `GET /scan/bulk/{job_id}` - Get bulk scan job status and progress
  - Returns: `{"job_id": "uuid", "status": "running", "progress": 50, "total": 3, "processed": 1, "succeeded": 1, "failed": 0, "errors": []}`
  - Status: `pending`, `running`, `completed`, `failed`
  - Progress: 0-100 percentage
  - Polling-based (no HTTP timeout)
- `GET /scan/bulk/{job_id}/results` - Get bulk scan results (completed jobs only)
  - Returns: `{"job_id": "uuid", "total": 3, "succeeded": 2, "failed": 1, "results": [...]}`
  - Returns scan results for all successfully processed domains
  - Only available for completed jobs

### Leads
- `GET /leads` - Query leads with filters, sorting, pagination, and search (G19)
  - Query parameters:
    - `segment` (optional): Filter by segment (Migration, Existing, Cold, Skip)
    - `min_score` (optional): Minimum readiness score (0-100)
    - `provider` (optional): Filter by provider (M365, Google, etc.)
    - `favorite` (optional): Filter by favorites (true = only favorites, false = all leads)
    - `sort_by` (optional): Sort by field (domain, readiness_score, priority_score, segment, provider, scanned_at)
    - `sort_order` (optional): Sort order (asc or desc, default: asc)
    - `page` (optional): Page number (1-based, default: 1)
    - `page_size` (optional): Number of items per page (default: 50, max: 200)
    - `search` (optional): Full-text search in domain, canonical_name, and provider
  - Returns: Paginated response with `leads`, `total`, `page`, `page_size`, `total_pages`
  - Each lead includes `priority_score` field (1-7, where 1 is highest priority)
- `GET /leads/{domain}/score-breakdown` - Get detailed score breakdown for a domain (G19)
  - Returns: Score breakdown with base_score, provider points, signal points, risk points, and total_score
- `GET /leads/{domain}` - Get single lead details
  - Returns: Complete lead information including signals, scores, priority_score, enrichment data (contact_emails, contact_quality_score, linkedin_pattern), and metadata
- `POST /leads/{domain}/enrich` - Manually enrich a lead with contact emails
  - Request body: `{"contact_emails": ["john@example.com", "jane@example.com"]}`
  - Returns: Enrichment results (contact_emails, contact_quality_score, linkedin_pattern)
  - Calculates quality score and detects LinkedIn email patterns
- `GET /leads/export` - Export leads to CSV or Excel format
  - Query parameters:
    - `segment` (optional): Filter by segment (Migration, Existing, Cold, Skip)
    - `min_score` (optional): Minimum readiness score (0-100)
    - `provider` (optional): Filter by provider (M365, Google, etc.)
    - `format` (optional): Export format (`csv` or `xlsx`, default: `csv`)
  - Returns: CSV or Excel file download with lead data
  - File name format: `leads_YYYY-MM-DD_HH-MM-SS.csv` or `leads_YYYY-MM-DD_HH-MM-SS.xlsx`

### Notes (G17: CRM-lite)
- `POST /leads/{domain}/notes` - Create a note for a domain
  - Request body: `{"note": "This is a note"}`
  - Returns: Created note with id, domain, note, created_at, updated_at
- `GET /leads/{domain}/notes` - List all notes for a domain
  - Returns: Array of notes (ordered by created_at desc)
- `PUT /leads/{domain}/notes/{note_id}` - Update a note
  - Request body: `{"note": "Updated note"}`
  - Returns: Updated note
- `DELETE /leads/{domain}/notes/{note_id}` - Delete a note
  - Returns: 204 No Content

### Tags (G17: CRM-lite)
- `POST /leads/{domain}/tags` - Add a tag to a domain
  - Request body: `{"tag": "important"}`
  - Returns: Created tag with id, domain, tag, created_at
- `GET /leads/{domain}/tags` - List all tags for a domain
  - Returns: Array of tags
- `DELETE /leads/{domain}/tags/{tag_id}` - Remove a tag from a domain
  - Returns: 204 No Content
- **Auto-tagging**: Automatically applies tags after domain scan:
  - `security-risk`: No SPF + no DKIM
  - `migration-ready`: Migration segment + score >= 70
  - `expire-soon`: Domain expires in < 30 days
  - `weak-spf`: SPF exists but DMARC policy is 'none'
  - `google-workspace`: Provider is Google
  - `local-mx`: Provider is Local

### Favorites (G17: CRM-lite)
- `POST /leads/{domain}/favorite` - Add a domain to favorites
  - Returns: Created favorite with id, domain, user_id, created_at
  - Session-based (no authentication required yet)
- `GET /leads?favorite=true` - List favorite domains
  - Returns: Array of leads that are favorited by the current user
- `DELETE /leads/{domain}/favorite` - Remove a domain from favorites
  - Returns: 204 No Content

### PDF Summary (G17)
- `GET /leads/{domain}/summary.pdf` - Generate PDF account summary
  - Returns: PDF file download
  - Includes: Provider info, SPF/DKIM/DMARC status, expiry date, signals, scores, risks
  - File name: `{domain}_summary.pdf`

### ReScan (G18: Automation)
- `POST /scan/{domain}/rescan` - Re-scan a single domain and detect changes
  - Returns: Scan result with detected changes (signals, scores, alerts)
  - Detects: MX changes, DMARC changes, expiry warnings, score changes
  - Creates alerts for detected changes
- `POST /scan/bulk/rescan?domain_list=domain1.com,domain2.com` - Bulk rescan multiple domains
  - Returns: Job ID for async processing
  - Maximum 1000 domains per request
  - Uses same progress tracking as bulk scan

### Alerts (G18: Change Notifications)
- `GET /alerts` - List alerts with optional filters
  - Query parameters:
    - `domain` (optional): Filter by domain
    - `alert_type` (optional): Filter by alert type (mx_changed, dmarc_added, expire_soon, score_changed)
    - `status` (optional): Filter by status (pending, sent, failed)
    - `limit` (optional): Maximum number of alerts (default: 100)
  - Returns: List of alerts
- `POST /alerts/config` - Create or update alert configuration
  - Request body: `{"alert_type": "mx_changed", "notification_method": "webhook", "enabled": true, "frequency": "immediate", "webhook_url": "https://example.com/webhook"}`
  - Returns: Alert configuration
- `GET /alerts/config` - List alert configurations for current user
  - Returns: List of alert configurations
- **Notification methods**: Email (placeholder), Webhook (HTTP POST), Slack (optional)
- **Alert types**: MX changed, DMARC added, Domain expire soon, Score changed
- **Daily rescan**: Automatically runs daily via Celery Beat scheduler

### Dashboard
- `GET /dashboard` - Get aggregated dashboard statistics (legacy endpoint)
  - Returns: `{"total_leads": 150, "migration": 25, "existing": 50, "cold": 60, "skip": 15, "avg_score": 55.5, "max_score": 90, "high_priority": 10}`
  - Provides segment distribution, average score, max score, and high priority lead count
- `GET /dashboard/kpis` - Get dashboard KPIs (G19)
  - Returns: `{"total_leads": 150, "migration_leads": 25, "high_priority": 10}`
  - Lightweight endpoint for KPI cards (total leads, migration leads, high priority leads)

### Webhook Ingestion (G16)
- `POST /ingest/webhook` - Ingest data from webhook with API key authentication
  - **Authentication**: Requires `X-API-Key` header
  - Request body: `{"domain": "example.com", "company_name": "Example Inc", "contact_emails": ["john@example.com"]}`
  - Returns: `{"status": "success", "domain": "example.com", "ingested": true, "enriched": true, "message": "..."}`
  - Features:
    - API key authentication and rate limiting (per key)
    - Automatic domain normalization
    - Lead enrichment (contact emails, quality score, LinkedIn pattern detection)
    - Retry logic with exponential backoff for failed requests
    - Error logging and tracking

### Authentication (G19: Microsoft SSO)
- `GET /auth/login` - Initiate Microsoft SSO login
  - Redirects to Azure AD login page
  - Returns: Redirect to Azure AD OAuth 2.0 authorization endpoint
- `GET /auth/callback` - OAuth callback endpoint
  - Handles Azure AD OAuth callback with authorization code
  - Returns: Redirect to frontend with access_token and refresh_token
- `GET /auth/me` - Get current user information
  - **Authentication**: Requires `Authorization: Bearer {access_token}` header
  - Returns: User information (id, email, display_name)
- `POST /auth/refresh` - Refresh access token
  - Request body: `{"refresh_token": "..."}`
  - Returns: New access_token and refresh_token
- `POST /auth/logout` - Logout current user
  - **Authentication**: Requires `Authorization: Bearer {access_token}` header
  - Revokes refresh token and clears session
  - Returns: 200 OK
- **Setup**: See [Azure AD Setup Guide](docs/archive/2025-11-15-G19-AZURE-AD-SETUP.md) for configuration instructions

### Admin (API Key Management)
- `POST /admin/api-keys` - Create a new API key
  - Request body: `{"name": "My API Key", "rate_limit_per_minute": 60, "created_by": "admin"}`
  - Returns: API key (shown only once - store securely!)
- `GET /admin/api-keys` - List all API keys (without showing actual keys)
- `PATCH /admin/api-keys/{key_id}/activate` - Activate an API key
- `PATCH /admin/api-keys/{key_id}/deactivate` - Deactivate an API key

### Email Tools
- `POST /email/generate` - Generate generic email addresses for a domain
  - Request body: `{"domain": "example.com"}`
  - Returns: `{"domain": "example.com", "emails": ["admin@example.com", "hr@example.com", "info@example.com", ...]}`
  - Generates common generic email addresses (info, sales, admin, iletisim, satis, etc.) for the given domain
  - Domain is normalized before generation (www prefix removed, lowercase, etc.)
- `POST /email/generate-and-validate` - Generate and validate generic email addresses for a domain
  - Request body: `{"domain": "example.com", "use_smtp": false}`
  - Returns: `{"domain": "example.com", "emails": [{"email": "info@example.com", "status": "valid", "confidence": "medium", "checks": {"syntax": true, "mx": true, "smtp": "skipped"}, "reason": "Valid syntax and MX records (SMTP not checked)"}, ...]}`
  - Generates generic emails and validates each one using:
    - Syntax validation (regex)
    - MX record validation (DNS)
    - Optional SMTP validation (if `use_smtp=true`, default: false)
  - Returns validation status ("valid", "invalid", "unknown"), confidence level ("high", "medium", "low"), and detailed checks

## Development

### Project Structure

```
dyn365hunterv3/
├── app/                    # FastAPI application
│   ├── api/               # API endpoints
│   ├── core/              # Core logic (normalizer, analyzer, scorer, celery, tasks)
│   ├── db/                # Database models and session
│   └── data/              # Configuration files (providers.json, rules.json)
├── tests/                 # Test files
├── docs/                  # Documentation
├── scripts/               # Utility scripts
│   └── start_celery_worker.sh  # Celery worker startup script
├── Dockerfile             # FastAPI container
├── docker-compose.yml     # Services configuration (PostgreSQL, Redis, API, Worker)
└── setup_dev.sh          # Development setup script
```

### Running Tests

**Note:** For local testing (outside Docker), activate virtual environment first:
```bash
# Activate venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term

# Run specific test file
pytest tests/test_scan_single.py -v
```

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type check
mypy app/
```

## CI/CD

The project includes GitHub Actions workflows:

- **CI Pipeline** (`ci.yml`): Runs tests, linting, Docker build, and Docker Compose tests
- **Code Quality** (`lint.yml`): Format and type checking

Workflows run on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

## Environment Variables

See `.env.example` for all available environment variables:

```bash
# Database
DATABASE_URL=postgresql://dyn365hunter:password123@postgres:5432/dyn365hunter
POSTGRES_USER=dyn365hunter
POSTGRES_PASSWORD=password123
POSTGRES_DB=dyn365hunter

# Redis (for Celery queue and progress tracking)
REDIS_URL=redis://redis:6379/0

# FastAPI
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Development
ENVIRONMENT=development
```

## Example Usage

### Complete Flow

```bash
# 1. Ingest a domain
curl -X POST http://localhost:8000/ingest/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "company_name": "Example Inc"}'

# 2. Scan the domain
curl -X POST http://localhost:8000/scan/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'

# 2b. Bulk scan multiple domains (async)
curl -X POST http://localhost:8000/scan/bulk \
  -H "Content-Type: application/json" \
  -d '{"domain_list": ["example.com", "google.com", "microsoft.com"]}'

# 2c. Check bulk scan progress
curl "http://localhost:8000/scan/bulk/{job_id}"

# 2d. Get bulk scan results (when completed)
curl "http://localhost:8000/scan/bulk/{job_id}/results"

# 3. Query leads
curl "http://localhost:8000/leads?segment=Migration&min_score=70"

# 4. Get single lead
curl "http://localhost:8000/leads/example.com"

# 5. Get dashboard statistics
curl "http://localhost:8000/dashboard"

# 6. Create API key for webhook
curl -X POST http://localhost:8000/admin/api-keys \
  -H "Content-Type: application/json" \
  -d '{"name": "My Webhook Key", "rate_limit_per_minute": 60}'

# 7. Ingest data via webhook
curl -X POST http://localhost:8000/ingest/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{"domain": "example.com", "company_name": "Example Inc", "contact_emails": ["john@example.com"]}'

# 8. Manually enrich a lead
curl -X POST http://localhost:8000/leads/example.com/enrich \
  -H "Content-Type: application/json" \
  -d '{"contact_emails": ["john@example.com", "jane@example.com"]}'
```

## Documentation

### For Sales Team
- [Sales Guide](docs/SALES-GUIDE.md) - Quick start guide for sales team (5 minutes)
- [Segment Guide](docs/SEGMENT-GUIDE.md) - Segment and score explanations
- [Sales Scenarios](docs/SALES-SCENARIOS.md) - Real-world usage scenarios
- [Sales Demo Script](scripts/sales-demo.sh) - Quick demo script

### For Developers

#### Feature Documentation
- [Provider Change Tracking](docs/active/PROVIDER-CHANGE-TRACKING.md) - Automatic detection and logging of provider changes
- [Duplicate Prevention](docs/active/DUPLICATE-PREVENTION.md) - Automatic cleanup of duplicate records
- [Domain Validation](docs/active/DOMAIN-VALIDATION.md) - Enhanced domain validation and filtering

#### Development Guides
- [Development Environment](docs/active/DEVELOPMENT-ENVIRONMENT.md) - Setup guide
- [WSL Guide](docs/active/WSL-GUIDE.md) - WSL2 setup and troubleshooting
- [Testing Guide](docs/active/TESTING.md) - How to run tests
- [Docker Troubleshooting](docs/active/DOCKER-TROUBLESHOOTING.md) - Common Docker issues and solutions
- [Mini UI README](mini-ui/README-mini-ui.md) - Mini UI usage guide and documentation

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

