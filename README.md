# Dyn365Hunter MVP

Lead intelligence engine for domain-based analysis and rule-based scoring.

[![CI/CD Pipeline](https://github.com/brdfb/dyn365hunterv3/actions/workflows/ci.yml/badge.svg)](https://github.com/brdfb/dyn365hunterv3/actions/workflows/ci.yml)
[![Code Quality](https://github.com/brdfb/dyn365hunterv3/actions/workflows/lint.yml/badge.svg)](https://github.com/brdfb/dyn365hunterv3/actions/workflows/lint.yml)

## Overview

Dyn365Hunter MVP is a FastAPI-based application that analyzes domains for lead intelligence. It performs DNS/WHOIS analysis and applies rule-based scoring to identify potential migration opportunities.

**Target**: ≤2 minute "kahvelik" analysis flow for sales team.

## Recent Updates (Last 6 Months)

**v1.1.0** (2025-01-28):
- **G21 Phase 2: Sales Engine** - Sales intelligence layer with call scripts, discovery questions, and offer tier recommendations
- **G21 Phase 3: Read-Only Mode** - CRM-lite features write endpoints disabled for Dynamics 365 migration
- **Stabilization Sprint** - 3-day enterprise-ready stabilization (UI, monitoring, core stability)
- **Core Logging Standardization** - Structured logging with PII masking across all modules

**v1.0.0** (2025-11-14):
- **G18: ReScan + Alerts** - Automation and change detection
- **G17: Notes, Tags, Favorites + PDF** - CRM-lite features and PDF summaries
- **G16: Webhook + Lead Enrichment** - Webhook ingestion with API key authentication
- **G15: Bulk Scan & Async Queue** - Async bulk domain scanning with progress tracking
- **G14: CSV Export + Mini UI** - Lead data export and simple web interface

> 📋 **Full changelog**: See [CHANGELOG.md](CHANGELOG.md) for complete release history

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
- ✅ **DMARC Coverage** (G20) - DMARC policy coverage percentage (pct parameter) ✨ YENİ
- ✅ WHOIS lookup (graceful fail with 5s timeout)
- ✅ Generic email generation for domains
- ✅ Email validation (syntax, MX, optional SMTP)
- ✅ Priority score calculation for lead prioritization
- ✅ **Tenant Size Estimation** (G20) - MX pattern-based tenant size for M365/Google (small/medium/large) ✨ YENİ
- ✅ **Local Provider Detection** (G20) - Specific local hosting provider identification (TürkHost, Natro, etc.) ✨ YENİ

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
- ✅ **UI Patch v1.1** - Skor detay modal ve UX iyileştirmeleri
  - DKIM çift gösterimi düzeltildi (tek satır: "DKIM Eksik: -15")
  - DMARC_NONE kategorisi düzeltildi (Pozitif Sinyaller'den çıkarıldı)
  - Sıralama tutarlılığı (SPF → DKIM → DMARC → Riskler)
  - Provider renkli badge'ler (M365, Google, Yandex, Local, vb.)
  - Sort ikonları iyileştirmeleri (tooltip + daha belirgin)
- ✅ **Stabilization Sprint - Gün 3: UI Stabilizasyon** (2025-01-28) - Enterprise-Ready / UI-Stable / Integration-Ready
  - Table view cleanup - Column width optimization, row hover effects, empty state with CTA, loading spinner, pagination improvements
  - Score breakdown modal - Enhanced close button, ESC key support, backdrop click, scroll optimization, tooltips for signals/risks
  - Header/Footer simplification - Compact header, footer with version info and links
  - Export/PDF basic - CSV/Excel export buttons, toast notifications, PDF export in modal
  - Tooltip + hover behavior - Generic tooltip system, smooth transitions, hover effects
  - UI %90+ stabil - Entegrasyona hazır
- ✅ **G21 Phase 2: Sales Engine** (2025-01-28) - Sales intelligence layer for lead qualification ✨ YENİ
  - Sales intelligence summary endpoint (`GET /api/v1/leads/{domain}/sales-summary`)
  - Segment-specific call scripts and discovery questions (Turkish)
  - Offer tier recommendations (Business Basic/Standard/Enterprise)
  - Opportunity potential scoring (0-100) with tuning factor support
  - Urgency level calculation (low/medium/high)
  - Frozen API contract (UI-ready, breaking change policy defined)
  - TypeScript and JSDoc type definitions for frontend integration
  - Logging and telemetry (`sales_summary_viewed` event)
- ✅ **G21 Phase 3: Read-Only Mode** (2025-01-28) - CRM-lite features write endpoints disabled ✨ YENİ
  - Write endpoints disabled (410 Gone) - Notes/Tags/Favorites write operations now return 410 Gone
  - Read endpoints remain available - Migration support for Dynamics 365 migration
  - Deprecated endpoint monitoring - Usage tracking via `GET /healthz/metrics` endpoint
  - Zero downtime migration support - Read-only mode enables safe migration to Dynamics 365

## Tech Stack

- **Backend**: FastAPI (Python 3.10)
- **Database**: PostgreSQL 15
- **Migration**: Alembic (P1) - Database migration management system
- **Queue**: Celery + Redis
- **Rate Limiting**: Redis-based distributed rate limiting (P1-2) - Multi-worker support with fallback
- **Caching**: Redis-based distributed caching (P1-3) - DNS, WHOIS, Provider, Scoring, Scan cache
- **Bulk Operations**: Batch processing optimization (P1-4) - Rate-limit aware batch processing with deadlock prevention
- **Logging**: Structured logging with PII masking (2025-01-28) - JSON format in production, contextual logging, domain/email masking
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
   - Run database schema migration (via Alembic)
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

**API Versioning (P1-5):**
- **V1 Endpoints**: All API endpoints are available under `/api/v1/` prefix (e.g., `/api/v1/leads`, `/api/v1/scan/domain`)
- **Legacy Endpoints**: Legacy endpoints (e.g., `/leads`, `/scan/domain`) continue to work for backward compatibility
- **Infrastructure Endpoints**: Health check (`/healthz`) and authentication (`/auth/*`) endpoints are not versioned
- **Migration**: Clients can gradually migrate to v1 endpoints while legacy endpoints remain active

### Quick Reference

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| **Health** | `/healthz` | GET | Health check and database status |
| **Health** | `/healthz/metrics` | GET | Metrics (cache, rate limit, bulk operations, errors) |
| **Ingest** | `/ingest/domain` | POST | Ingest single domain |
| **Ingest** | `/ingest/csv` | POST | Ingest domains from CSV/Excel file |
| **Ingest** | `/ingest/webhook` | POST | Webhook ingestion (API key required) |
| **Scan** | `/scan/domain` | POST | Analyze single domain (DNS + WHOIS + scoring) |
| **Scan** | `/scan/bulk` | POST | Create bulk scan job (async) |
| **Scan** | `/scan/bulk/{job_id}` | GET | Get bulk scan progress |
| **Scan** | `/scan/{domain}/rescan` | POST | Re-scan domain with change detection |
| **Leads** | `/leads` | GET | Query leads (filters, sorting, pagination, search) |
| **Leads** | `/leads/{domain}` | GET | Get single lead details |
| **Leads** | `/leads/{domain}/sales-summary` | GET | Get sales intelligence summary (G21 Phase 2) |
| **Leads** | `/leads/{domain}/score-breakdown` | GET | Get detailed score breakdown |
| **Leads** | `/leads/{domain}/enrich` | POST | Manually enrich lead with contact emails |
| **Leads** | `/leads/export` | GET | Export leads to CSV/Excel |
| **Leads** | `/leads/{domain}/summary.pdf` | GET | Generate PDF account summary |
| **Dashboard** | `/dashboard` | GET | Get aggregated dashboard statistics |
| **Dashboard** | `/dashboard/kpis` | GET | Get dashboard KPIs (lightweight) |
| **Auth** | `/auth/login` | GET | Initiate Microsoft SSO login |
| **Auth** | `/auth/me` | GET | Get current user information |
| **Admin** | `/admin/api-keys` | POST | Create API key |
| **Email** | `/email/generate` | POST | Generate generic email addresses |
| **Email** | `/email/generate-and-validate` | POST | Generate and validate emails |
| **Alerts** | `/alerts` | GET | List alerts with filters |
| **Alerts** | `/alerts/config` | POST | Configure alert preferences |

> 📖 **Detailed documentation**: See sections below for complete endpoint documentation with request/response examples

**Interactive API Documentation:**
- Swagger UI: `http://localhost:8000/docs` (interactive API explorer)
- ReDoc: `http://localhost:8000/redoc` (alternative documentation format)
- OpenAPI JSON: `http://localhost:8000/openapi.json` (machine-readable schema)
- Support: `http://localhost:8000/support` (support information endpoint)

### Health Check
- `GET /healthz` - Health check and database connection status
- `GET /healthz/live` - Liveness probe (Kubernetes/Docker)
- `GET /healthz/ready` - Readiness probe (checks database and Redis connections)
- `GET /healthz/startup` - Startup probe (checks if application has finished starting)
- `GET /healthz/metrics` - Metrics endpoint (Stabilization Sprint - Gün 2)
  - Returns: Cache metrics (hits, misses, hit rate), rate limit metrics (hits, acquired, circuit breaker state), bulk operations metrics (batch success/failure, processing time, deadlock count), error metrics (total errors, errors by component, error trends)
  - Example response: `{"cache": {...}, "rate_limit": {...}, "bulk_operations": {...}, "errors": {...}}`

### Ingest
- `POST /api/v1/ingest/domain` or `POST /ingest/domain` - Ingest single domain
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
  - Returns: `{"domain": "example.com", "score": 75, "segment": "Migration", "reason": "...", "provider": "M365", "tenant_size": "medium", "local_provider": null, "mx_root": "outlook.com", "spf": true, "dkim": true, "dmarc_policy": "reject", "dmarc_coverage": 100, "scan_status": "success"}`
  - Performs DNS analysis (MX, SPF, DKIM, DMARC) and WHOIS lookup
  - **G20**: Extracts DMARC coverage (pct), estimates tenant size (M365/Google), detects local provider ✨ YENİ
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
  - Returns: Complete lead information including signals, scores, priority_score, enrichment data (contact_emails, contact_quality_score, linkedin_pattern), **G20 fields (tenant_size, local_provider, dmarc_coverage)**, and metadata
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

### Sales Intelligence (G21 Phase 2) ✨ YENİ
- `GET /api/v1/leads/{domain}/sales-summary` - Get complete sales intelligence summary for a lead
  - Returns: Sales intelligence summary with:
    - `one_liner` - One-sentence sales summary (Turkish)
    - `call_script` - Call script bullets for sales outreach (Turkish)
    - `discovery_questions` - Discovery questions for sales qualification (Turkish)
    - `offer_tier` - Offer tier recommendation (Business Basic/Standard/Enterprise) with pricing details
    - `opportunity_potential` - Opportunity potential score (0-100)
    - `urgency` - Urgency level (low/medium/high)
    - `metadata` - Additional context (segment, provider, tenant_size, readiness_score, priority_score, etc.)
  - Example response:
    ```json
    {
      "domain": "example.com",
      "one_liner": "example.com - Migration fırsatı, yüksek hazırlık skoru (85), Enterprise teklif hazırlanabilir.",
      "call_script": ["Merhaba, example.com için email altyapınızı inceledik...", "..."],
      "discovery_questions": ["Şu anki email altyapınızdan memnun musunuz?", "..."],
      "offer_tier": {
        "tier": "Enterprise",
        "license": "Enterprise",
        "price_per_user_per_month": 20,
        "migration_fee": 10000,
        "defender_price_per_user_per_month": 10,
        "consulting_fee": 50000,
        "recommendation": "Enterprise çözümü önerilir..."
      },
      "opportunity_potential": 89,
      "urgency": "high",
      "metadata": {...}
    }
    ```
  - **API Contract**: Frozen contract (UI-ready) - See `docs/api/SALES-SUMMARY-V1-CONTRACT.md`
  - **Type Definitions**: TypeScript (`mini-ui/types/sales.ts`) and JSDoc (`mini-ui/types/sales.js`)
  - **Legacy Endpoint**: `GET /leads/{domain}/sales-summary` (backward compatible)

### Notes (G17: CRM-lite) ❌ **DISABLED** (G21 Phase 3)
- ❌ **Write endpoints disabled** (2025-01-28) - Returns 410 Gone (Read-Only Mode)
  - `POST /leads/{domain}/notes` - ❌ **Disabled (410 Gone)** - Create a note for a domain
    - Returns: 410 Gone with error message
    - **Reason**: Notes are now managed in Dynamics 365
    - **Alternative**: Use Dynamics 365 Timeline/Notes API
  - `PUT /leads/{domain}/notes/{note_id}` - ❌ **Disabled (410 Gone)** - Update a note
    - Returns: 410 Gone with error message
    - **Alternative**: Use Dynamics 365 Timeline/Notes API
  - `DELETE /leads/{domain}/notes/{note_id}` - ❌ **Disabled (410 Gone)** - Delete a note
    - Returns: 410 Gone with error message
    - **Alternative**: Use Dynamics 365 Timeline/Notes API
- ✅ **Read endpoint remains available** (migration support):
  - `GET /leads/{domain}/notes` - List all notes for a domain
    - Returns: Array of notes (ordered by created_at desc)
    - **Status**: Available for migration support until Phase 6

### Tags (G17: CRM-lite) ❌ **DISABLED** (G21 Phase 3)
- ❌ **Manual tag write endpoints disabled** (2025-01-28) - Returns 410 Gone (Read-Only Mode)
  - `POST /leads/{domain}/tags` - ❌ **Disabled (410 Gone)** (manual tags only) - Add a tag to a domain
    - Returns: 410 Gone with error message
    - **Reason**: Manual tags are now managed in Dynamics 365. Auto-tags (system-generated) remain available.
    - **Alternative**: Use Dynamics 365 Tags API for manual tag management
  - `DELETE /leads/{domain}/tags/{tag_id}` - ❌ **Disabled (410 Gone)** (manual tags only) - Remove a tag from a domain
    - Returns: 410 Gone with error message
    - **Alternative**: Use Dynamics 365 Tags API for manual tag management
- ✅ **Read endpoint remains available** (auto-tags needed):
  - `GET /leads/{domain}/tags` - List all tags for a domain
    - Returns: Array of tags (includes auto-tags and manual tags)
    - **Status**: Available for auto-tags (system-generated tags remain functional)
- **Auto-tagging**: Automatically applies tags after domain scan (✅ **Remains active**):
  - `security-risk`: No SPF + no DKIM
  - `migration-ready`: Migration segment + score >= 70
  - `expire-soon`: Domain expires in < 30 days
  - `weak-spf`: SPF exists but DMARC policy is 'none'
  - `google-workspace`: Provider is Google
  - `local-mx`: Provider is Local

### Favorites (G17: CRM-lite) ❌ **DISABLED** (G21 Phase 3)
- ❌ **Write endpoints disabled** (2025-01-28) - Returns 410 Gone (Read-Only Mode)
  - `POST /leads/{domain}/favorite` - ❌ **Disabled (410 Gone)** - Add a domain to favorites
    - Returns: 410 Gone with error message
    - **Reason**: Favorites are now managed in Dynamics 365
    - **Alternative**: Use Dynamics 365 Favorite field for favorite management
  - `DELETE /leads/{domain}/favorite` - ❌ **Disabled (410 Gone)** - Remove a domain from favorites
    - Returns: 410 Gone with error message
    - **Alternative**: Use Dynamics 365 Favorite field for favorite management
- ✅ **Read endpoint remains available** (migration support):
  - `GET /leads?favorite=true` - List favorite domains
    - Returns: Array of leads that are favorited by the current user
    - **Status**: Available for migration support until Phase 6

### PDF Summary (G17)
- `GET /leads/{domain}/summary.pdf` - Generate PDF account summary
  - Returns: PDF file download
  - Includes: Provider info, SPF/DKIM/DMARC status, expiry date, signals, scores, risks
  - File name: `{domain}_summary.pdf`
  - **Turkish Character Support**: Full UTF-8 support for Turkish characters (ı, ş, ğ, ü, ö, ç)

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

## Database Migrations

The project uses **Alembic** for database migration management (P1).

### Migration Commands

```bash
# Upgrade to latest migration
python -m app.db.run_migration upgrade

# Upgrade to specific revision
python -m app.db.run_migration upgrade <revision>

# Downgrade one step
python -m app.db.run_migration downgrade

# Show current revision
python -m app.db.run_migration current

# Show migration history
python -m app.db.run_migration history

# Check for schema drift
python -m app.db.run_migration check
```

### Creating New Migrations

```bash
# Create a new migration (autogenerate from models)
alembic revision --autogenerate -m "add_new_feature"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Migration Strategy

- **Base Revision**: `08f51db8dce0` represents the current production schema (includes all historical migrations g16-g20)
- **Legacy Migrations**: Historical SQL migration files are in `app/db/migrations/legacy/` for reference
- **Future Changes**: All schema changes will be managed through Alembic revisions

**Documentation**: See `docs/active/P1-ALEMBIC-STATUS.md` for detailed migration status and usage.

---

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
- [Logging Guide](docs/active/LOGGING-GOLDEN-SAMPLES.md) - Structured logging format and golden samples
- [Logging Smoke Test](docs/active/LOGGING-SMOKE-TEST.md) - Logging verification and testing guide
- [Mini UI README](mini-ui/README-mini-ui.md) - Mini UI usage guide and documentation

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

