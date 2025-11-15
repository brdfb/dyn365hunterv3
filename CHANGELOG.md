# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Priority Score Improvements** - Enhanced priority scoring system
  - Extended priority range from 1-6 to 1-7 for better granularity
  - Migration segment now always gets priority (even with low scores: Priority 3-4)
  - Improved priority distribution:
    - Migration + Score 50-69 → Priority 3 (was Priority 6)
    - Migration + Score 0-49 → Priority 4 (was Priority 6)
    - Existing + Score 30-49 → Priority 5 (was Priority 6)
    - Existing + Score 0-29 → Priority 6 (was Priority 6)
    - Cold + Score 20-39 → Priority 6 (was Priority 6)
    - Cold + Score 0-19 → Priority 7 (new)
    - Skip → Priority 7 (was Priority 6)
  - Enhanced UI visualization:
    - Each priority level now has unique visual indicator (🔥⭐🟡🟠⚪⚫🔴)
    - Tooltip support for priority badges with detailed information
  - Updated constants and thresholds in `app/core/constants.py`
  - Updated priority calculation logic in `app/core/priority.py`
  - Updated UI components in `mini-ui/js/ui-leads.js`
  - Updated API default values (Priority 6 → 7)
  - Updated test suite in `tests/test_priority.py`
  - Updated documentation (SEGMENT-GUIDE.md, SALES-GUIDE.md, SALES-SCENARIOS.md, README.md)

- **G19: Microsoft SSO Authentication + UI Upgrade** - Authentication and enhanced UI features
  - Microsoft SSO Authentication:
    - `GET /auth/login` - Initiate Azure AD OAuth 2.0 login
    - `GET /auth/callback` - OAuth callback handler
    - `GET /auth/me` - Get current user information
    - `POST /auth/refresh` - Refresh access token
    - `POST /auth/logout` - Logout and revoke tokens
    - JWT token management (access + refresh tokens)
    - User management (users table with Azure AD integration)
    - Security hardening:
      - OAuth state/nonce storage (Redis)
      - Token revocation table
      - Refresh token encryption (Fernet)
    - Favorites migration: Session-based → user-based (on first login)
    - Setup guide: `docs/archive/2025-11-15-G19-AZURE-AD-SETUP.md` (archived after completion)
  - UI Upgrade (Lead Table):
    - Sorting: Sort by domain, readiness_score, priority_score, segment, provider, scanned_at
    - Pagination: Page-based pagination with configurable page size (default: 50, max: 200)
    - Full-text search: Search in domain, canonical_name, and provider fields
    - Frontend: Clickable table headers, pagination UI, search input with debounce
  - Dashboard KPI:
    - `GET /dashboard/kpis` - New lightweight endpoint for KPI cards
    - Returns: total_leads, migration_leads, high_priority
    - Frontend: 4 KPI cards (Total, Migration, High Priority, Max Score)
  - Score Breakdown:
    - `GET /leads/{domain}/score-breakdown` - Detailed score analysis
    - Returns: base_score, provider points, signal points, risk points, total_score
    - Frontend: Modal UI with clickable score cells
  - Tests: Comprehensive test suite
    - `tests/test_ui_upgrade.py` - UI upgrade tests (sorting, pagination, search) - 20+ test cases
    - `tests/test_integration_g19.py` - Integration tests (auth e2e, UI upgrade e2e, protected routes) - 15+ test cases
    - `tests/test_auth.py` - Auth tests (OAuth flow, token generation, user management) - 22 test cases
  - Post-MVP Sprint 6 feature (authentication + UI enhancement)
- Production readiness documentation:
  - `PRODUCTION-READINESS-CRITIQUE-V2.md` - P0/P1/P2 hardening checklist with code examples
  - `PRODUCTION-ENGINEERING-GUIDE-V1.md` - SRE runbook with health checks, monitoring, deployment strategies

### Documentation
- Added comprehensive production readiness critique (v2) with health checks & probes
- Added production engineering guide (v1) with SRE practices and incident response runbook
- Added Azure AD setup guide (G19) with step-by-step instructions
- Archived completed phase documentation to `docs/archive/`

## [1.0.0] - 2025-11-14

### Added
- **G18: ReScan + Alerts + Enhanced Scoring** - Automation and change detection
  - ReScan infrastructure:
    - `POST /scan/{domain}/rescan` - Manual rescan with change detection
    - `POST /scan/bulk/rescan` - Bulk rescan for multiple domains
    - Change detection for signals (SPF, DKIM, DMARC, MX) and scores
    - History tables: `signal_change_history`, `score_change_history`
  - Alerts system:
    - `GET /alerts` - List alerts with filters
    - `POST /alerts/config` - Configure alert preferences
    - `GET /alerts/config` - List alert configurations
    - Alert types: MX changed, DMARC added, Domain expire soon, Score changed
    - Notification methods: Email (placeholder), Webhook (HTTP POST), Slack (optional)
    - Alert configuration: Immediate or daily digest frequency
  - Enhanced scoring (AI-free):
    - DKIM none penalty (additional risk point)
    - SPF multiple includes risk detection
    - Enhanced risk scoring for security signals
  - Scheduler:
    - Daily rescan task via Celery Beat
    - Automatic change detection and alert generation
    - Configurable schedule (daily, weekly, monthly)
  - Database migration: `app/db/migrations/g18_rescan_alerts_scoring.sql`
  - Implementation:
    - `app/core/change_detection.py` - Change detection logic
    - `app/core/rescan.py` - ReScan engine
    - `app/core/notifications.py` - Notification engine
    - `app/api/rescan.py` - ReScan endpoints
    - `app/api/alerts.py` - Alerts endpoints
    - `app/db/models.py` - History and alert models
    - `app/core/celery_app.py` - Celery Beat schedule
    - `app/core/tasks.py` - Daily rescan task
  - Tests: Comprehensive test suite
    - `tests/test_rescan_alerts.py` - ReScan, change detection, and alerts tests
  - Post-MVP Sprint 5 feature (automation + change alerts)
  - **Bug Fixes (2025-11-14)**:
    - Fixed bulk rescan change detection (now uses `rescan_domain` with change detection)
    - Fixed alert notification processing (added Celery Beat task for pending alerts)
    - Fixed daily rescan change detection (now properly detects changes)
    - Added immediate alert processing trigger after rescan
- **G17: Notes, Tags, Favorites + PDF Summary** - CRM-lite features and PDF account summaries
  - Notes system:
    - `POST /leads/{domain}/notes` - Create a note for a domain
    - `GET /leads/{domain}/notes` - List all notes for a domain
    - `PUT /leads/{domain}/notes/{note_id}` - Update a note
    - `DELETE /leads/{domain}/notes/{note_id}` - Delete a note
    - Database table: `notes` with domain foreign key
  - Tags system:
    - `POST /leads/{domain}/tags` - Add a tag to a domain
    - `GET /leads/{domain}/tags` - List all tags for a domain
    - `DELETE /leads/{domain}/tags/{tag_id}` - Remove a tag from a domain
    - Database table: `tags` with domain foreign key and unique constraint
    - Auto-tagging: Automatically applies tags after domain scan:
      - `security-risk`: No SPF + no DKIM
      - `migration-ready`: Migration segment + score >= 70
      - `expire-soon`: Domain expires in < 30 days
      - `weak-spf`: SPF exists but DMARC policy is 'none'
      - `google-workspace`: Provider is Google
      - `local-mx`: Provider is Local
  - Favorites system:
    - `POST /leads/{domain}/favorite` - Add a domain to favorites
    - `GET /leads?favorite=true` - List favorite domains (session-based)
    - `DELETE /leads/{domain}/favorite` - Remove a domain from favorites
    - Database table: `favorites` with domain and user_id (session-based)
  - PDF Summary:
    - `GET /leads/{domain}/summary.pdf` - Generate PDF account summary
    - Includes: Provider info, SPF/DKIM/DMARC status, expiry date, signals, scores, risks
    - Uses ReportLab for PDF generation
  - Database migration: `app/db/migrations/g17_notes_tags_favorites.sql`
  - Implementation:
    - `app/core/auto_tagging.py` - Auto-tagging logic
    - `app/api/notes.py` - Notes endpoints
    - `app/api/tags.py` - Tags endpoints
    - `app/api/favorites.py` - Favorites endpoints
    - `app/api/pdf.py` - PDF summary endpoint
    - `app/db/models.py` - Note, Tag, Favorite models
  - Tests: Comprehensive test suite
    - `tests/test_notes_tags_favorites.py` - Notes, tags, favorites, and auto-tagging tests
    - `tests/test_pdf.py` - PDF generation tests
  - Post-MVP Sprint 4 feature (CRM-lite + PDF summary)
- **G16: Webhook + Lead Enrichment** - Webhook ingestion with API key authentication and lead enrichment
  - `POST /ingest/webhook` endpoint for webhook data ingestion
    - API key authentication via `X-API-Key` header
    - Rate limiting per API key (configurable, default: 60 requests/minute)
    - Automatic domain normalization and company upsert
    - Lead enrichment with contact emails, quality score, and LinkedIn pattern detection
    - Retry logic with exponential backoff for failed requests (max 3 retries)
    - Error logging and webhook failure tracking
  - `POST /admin/api-keys` endpoint for API key generation
    - Generate secure API keys (SHA-256 hashed)
    - Configurable rate limits per key
    - Key activation/deactivation support
  - `GET /admin/api-keys` endpoint for listing API keys
  - `PATCH /admin/api-keys/{key_id}/activate` and `/deactivate` endpoints
  - `POST /leads/{domain}/enrich` endpoint for manual lead enrichment
  - Database schema updates:
    - `api_keys` table for API key management
    - `webhook_retries` table for retry tracking
    - `companies.contact_emails` (JSONB array) for contact email storage
    - `companies.contact_quality_score` (integer, 0-100) for quality scoring
    - `companies.linkedin_pattern` (string) for LinkedIn email pattern detection
  - Lead enrichment features:
    - Contact quality score calculation (based on email count and domain matching)
    - LinkedIn email pattern detection (firstname.lastname, f.lastname, firstname)
    - Email deduplication and normalization
  - Implementation:
    - `app/core/api_key_auth.py` - API key authentication and rate limiting
    - `app/core/enrichment.py` - Lead enrichment logic
    - `app/core/webhook_retry.py` - Retry logic with exponential backoff
    - `app/api/admin.py` - Admin endpoints for API key management
    - `app/api/ingest.py` - Webhook endpoint
    - `app/api/leads.py` - Enrichment endpoint and updated GET /leads/{domain}
    - `app/db/migrations/g16_webhook_enrichment.sql` - Database migration script
  - Tests: Comprehensive test suite (20+ test cases)
    - `tests/test_webhook.py` - Webhook endpoint tests (10 tests)
    - `tests/test_enrichment.py` - Enrichment logic tests (10 tests)
    - `tests/test_api_key_auth.py` - API key authentication tests
  - Post-MVP Sprint 3 feature (webhook infrastructure + basic enrichment)
- **G15: Bulk Scan & Async Queue** - Async bulk domain scanning with progress tracking
  - `POST /scan/bulk` endpoint for creating bulk scan jobs (up to 1000 domains)
  - `GET /scan/bulk/{job_id}` endpoint for checking job status and progress
  - `GET /scan/bulk/{job_id}/results` endpoint for retrieving scan results
  - Celery + Redis integration for async task processing
  - Rate limiting: DNS (10 req/s), WHOIS (5 req/s) per worker
  - Progress tracking with Redis (job status, progress percentage, error tracking)
  - Error handling: Partial failure support, retry logic, exponential backoff
  - Worker configuration: 5 concurrent tasks, 15s per-domain timeout, 2 max retries
  - Docker Compose: Redis service and Celery worker service added
  - Implementation:
    - `app/core/celery_app.py` - Celery application configuration
    - `app/core/rate_limiter.py` - Rate limiting utilities (token bucket algorithm)
    - `app/core/progress_tracker.py` - Redis-based progress tracking
    - `app/core/tasks.py` - Celery tasks for bulk scanning
    - `app/api/scan.py` - Bulk scan API endpoints
  - Tests: Comprehensive test suite (19+ test cases)
    - `tests/test_rate_limiter.py` - Rate limiting tests (9 tests)
    - `tests/test_progress_tracker.py` - Progress tracking tests (10 tests)
    - `tests/test_error_handling.py` - Error handling tests
    - `tests/test_bulk_scan.py` - Integration tests for bulk scan API
  - Worker startup script: `scripts/start_celery_worker.sh`
  - Post-MVP Sprint 2 feature (core infrastructure)
- **Provider Change Tracking** - Automatic detection and logging of provider changes
  - `ProviderChangeHistory` model in `app/db/models.py` to track provider changes over time
  - Automatic detection when domain is scanned (via `/scan/domain` or CSV ingestion with `auto_scan=true`)
  - Provider changes logged to `provider_change_history` table (domain, previous_provider, new_provider, changed_at)
  - Implementation: Provider change detection in `app/api/scan.py` and `app/api/ingest.py`
  - Use cases: Migration opportunity detection, customer behavior tracking, sales follow-up
  - Documentation: `docs/active/PROVIDER-CHANGE-TRACKING.md`

- **Duplicate Prevention** - Automatic cleanup of duplicate LeadScore and DomainSignal records
  - Delete existing records before creating new ones (prevents duplicates on re-scan)
  - Implementation: Explicit delete queries in `app/api/scan.py` and `app/api/ingest.py`
  - Ensures only one current record per domain for both `lead_scores` and `domain_signals` tables
  - Benefits: Data quality, accurate lead counts, always reflects most recent scan
  - Documentation: `docs/active/DUPLICATE-PREVENTION.md`

- **Domain Validation** - Enhanced validation to filter invalid domains
  - `is_valid_domain()` function in `app/core/normalizer.py` to validate domain format
  - Filters invalid values: nan, n/a, web sitesi, website, http, https, etc.
  - URL extraction: Automatically extracts domain from URLs (http://example.com/ → example.com)
  - Validation integrated into CSV ingestion and scan endpoints
  - Invalid domains are skipped with descriptive error messages
  - Documentation: `docs/active/DOMAIN-VALIDATION.md`

- **Progress Tracking** - Real-time progress updates for CSV ingestion and scanning operations
  - In-memory job tracking system (`app/api/jobs.py`) for job status and progress
  - `GET /jobs/{job_id}` endpoint (`app/api/progress.py`) to query job progress
  - Progress updates during CSV ingestion and auto-scan operations
  - Frontend polling mechanism in Mini UI for real-time progress bar
  - Progress metrics: processed, total, successful, failed, remaining, progress_percent, message
  - Status: queued, processing, completed, failed

- **Auto-Scan Feature** - Automatic domain scanning after CSV ingestion
  - `auto_scan=true` query parameter for `/ingest/csv` endpoint (default: true)
  - Automatically scans all ingested domains (DNS + WHOIS + scoring)
  - Results automatically added to lead list
  - Integrated with progress tracking for long-running operations
  - Frontend: Mini UI automatically enables auto-scan

- **G14: CSV Export** - Lead data export to CSV and Excel formats
  - `GET /leads/export` endpoint for exporting leads to CSV or Excel format
  - Filter parameters: `segment`, `min_score`, `provider` (same as GET /leads)
  - Format parameter: `csv` (default) or `xlsx`
  - Timestamped filename: `leads_YYYY-MM-DD_HH-MM-SS.csv` or `.xlsx`
  - Export includes all lead fields: domain, company_name, provider, segment, scores, signals, etc.
  - Implementation: Export endpoint added to `app/api/leads.py` router
  - Tests: `tests/test_export.py` - Comprehensive export tests (9 test cases)
  - Post-MVP feature (low-risk, core-independent)

- **G14: Mini UI** - Simple web interface for demo and internal use
  - HTML + Vanilla JavaScript + CSS (no framework)
  - `mini-ui/` directory structure with modular JS (api.js, ui-leads.js, ui-forms.js, app.js)
  - Features:
    - CSV/Excel file upload with auto-detect columns option
    - Single domain scan with auto-ingest (if company name provided)
    - Leads table with filters (segment, min score, provider)
    - CSV export button
    - Dashboard statistics (KPI: total leads, migration count, max score)
  - Static file serving via FastAPI (`app.mount("/mini-ui", ...)`)
  - Responsive design (mobile-friendly)
  - BEM CSS pattern for maintainability
  - API-first approach (all business logic in backend)
  - Documentation: `mini-ui/README-mini-ui.md`, `mini-ui/TEST-CHECKLIST.md`
  - Post-MVP feature (low-risk, core-independent, demo-ready)

- **G11: Importer Module** - Excel/CSV column auto-detection and ingestion enhancement
  - Excel file support (.xlsx, .xls) for `/ingest/csv` endpoint
  - `auto_detect_columns` query parameter for automatic column detection
  - `app/core/importer.py` - Column guessing utilities (`guess_company_column`, `guess_domain_column`)
  - Heuristic-based column detection for OSB Excel files
  - Backward compatible: existing CSV ingestion continues to work
  - Tests: `tests/test_importer_autodetect.py` - Column detection tests
  - Tests: Updated `tests/test_ingest_csv.py` with Excel support tests

- **G12: Email Generator** - Generic email address generation
  - `POST /email/generate` endpoint for generating generic email addresses
  - `app/core/email_generator.py` - Email generation utilities (`generate_generic_emails`)
  - Generic email list includes Türkçe (iletisim, satis, muhasebe, ik) and International (info, sales, admin, support, hr) local parts
  - Domain normalization integrated (www prefix removal, lowercase, etc.)
  - Tests: `tests/test_email_generator.py` - Email generation tests

- **G13: Email Validator** - Email validation with syntax, MX, and optional SMTP checks
  - `POST /email/generate-and-validate` endpoint for generating and validating emails
  - `app/core/email_validator.py` - Email validation utilities
    - Syntax validation (RFC 5322 simplified regex)
    - MX record validation (DNS lookup using existing `get_mx_records`)
    - Optional SMTP validation (RCPT TO check, flag-based, default: disabled)
  - Validation result includes status ("valid", "invalid", "unknown"), confidence level ("high", "medium", "low"), and detailed checks
  - Light validation by default (syntax + MX, no SMTP) for fast response times
  - SMTP validation optional and controlled via `use_smtp` parameter
  - Tests: `tests/test_email_validator.py` - Comprehensive validation tests with mocks (19 test cases)

### Post-MVP (High Priority)
- ✅ CSV Export - **Completed** (G14) - CSV and Excel export with filters
- ✅ Mini UI - **Completed** (G14) - Simple web interface for demo and internal use
- ✅ Bulk Scan - **Completed** (G15) - Async bulk domain scanning with progress tracking
- ✅ Webhook + Enrichment - **Completed** (G16) - Webhook ingestion with API key authentication
- ✅ Notes/Tags/Favorites + PDF - **Completed** (G17) - CRM-lite features and PDF summaries
- ✅ ReScan + Alerts - **Completed** (G18) - Automation and change detection

### Post-MVP (Low Priority)
- Email Templates, Reminders - Requirements specified

## [0.5.0] - 2025-01-27

### Added
- **Hard-Fail Rules**: Domains with missing MX records are automatically assigned Skip segment
  - `check_hard_fail()` function in `app/core/scorer.py`
  - Hard-fail check happens before scoring calculation
  - Returns Skip segment with score 0 and clear reason message

- **Risk Scoring**: Negative points for missing security signals
  - `risk_points` section in `app/data/rules.json`
  - Risk penalties: no SPF (-10), no DKIM (-10), DMARC none (-10), hosting MX weak (-10)
  - Risk scoring applied in `calculate_score()` function

### Changed
- **Provider Points**: Updated provider point values
  - Hosting: 10 → **20** (better reflects hosting provider value)
  - Local: 0 → **10** (self-hosted domains have some value)

- **Scoring Logic**: Enhanced scoring calculation
  - `calculate_score()` now applies risk points (negative)
  - Score is floored at 0 and capped at 100
  - `score_domain()` checks hard-fail conditions first

- **API**: Updated `POST /scan/domain` endpoint
  - Now passes `mx_records` to `score_domain()` for hard-fail checking

### Testing
- Added comprehensive tests for hard-fail rules (`TestHardFailRules`)
- Added comprehensive tests for risk scoring (`TestRiskScoring`)
- Added tests for updated provider points (`TestProviderPointsUpdate`)
- All 33 tests passing

### Documentation
- Updated `docs/SEGMENT-GUIDE.md` with risk scoring and hard-fail rules
- Updated `docs/plans/2025-01-27-phase0-hotfix-scoring.md` with implementation plan

## [0.4.0] - 2025-01-27

### Added
- Dashboard endpoint (`GET /dashboard`)
  - `app/api/dashboard.py` - Dashboard statistics endpoint
  - Segment distribution (Migration, Existing, Cold, Skip counts)
  - Average readiness score calculation
  - High priority leads count (Migration + score >= 70)
  - Empty database handling
  - Uses `leads_ready` VIEW for efficient aggregation

- Priority Score feature
  - `app/core/priority.py` - Priority score calculation module
  - `calculate_priority_score()` - Priority scoring logic based on segment and score
  - Priority levels: 1 (highest) to 6 (lowest)
  - Integration with `GET /leads` and `GET /leads/{domain}` endpoints
  - `LeadResponse` model updated with `priority_score` field

### Changed
- **API**: Updated `app/main.py` to register dashboard router
- **API**: Updated `app/api/leads.py` to include priority score in responses
- **Models**: Added `priority_score: Optional[int]` to `LeadResponse` model

## [0.3.0] - 2025-01-27

### Changed
- **Documentation**: Organized and archived completed MVP documentation
  - Archived: MVP-TRIMMED-ROADMAP.md, GO-NO-GO-CHECKLIST.md, PROJECT-EVALUATION.md, SALES-TEAM-EVALUATION.md, CRITIQUE.md
  - Active: SALES-FEATURE-REQUESTS.md, SALES-FEATURE-REQUESTS-CRITIQUE.md (MVP scope features)
  - Active: DEVELOPMENT-ENVIRONMENT.md, WSL-GUIDE.md (setup guides)

## [0.2.0] - 2025-11-12

### Added
- G4: Ingest Endpoints (CSV + Domain)
  - `app/core/merger.py` - Company upsert utilities (upsert_companies with domain unique key)
  - `app/api/ingest.py` - Ingest endpoints:
    - `POST /ingest/domain` - Single domain ingestion
    - `POST /ingest/csv` - CSV file ingestion with pandas
  - Domain extraction from email and website URLs
  - Idempotent company upsert (domain unique constraint)
  - Added `pandas==2.1.3` and `python-multipart==0.0.6` dependencies

- G5: DNS Analyzer
  - `app/core/analyzer_dns.py` - DNS analysis utilities:
    - `get_mx_records()` - MX record retrieval (sorted by priority)
    - `check_spf()` - SPF record validation
    - `check_dkim()` - DKIM record validation
    - `check_dmarc()` - DMARC policy extraction
    - `analyze_dns()` - Complete DNS analysis
  - MX root domain extraction
  - 10s timeout handling for DNS queries
  - Graceful error handling for DNS failures

- G6: WHOIS Analyzer
  - `app/core/analyzer_whois.py` - WHOIS lookup utilities:
    - `get_whois_info()` - WHOIS information retrieval
    - Registrar, expiration date, and nameservers extraction
  - 5s timeout handling
  - Graceful fail (WHOIS failures don't break scoring)

- G7: Scan Endpoint & Scoring Integration
  - `app/api/scan.py` - Domain scanning endpoint:
    - `POST /scan/domain` - Complete domain analysis (DNS + WHOIS + scoring)
  - Integration with DNS and WHOIS analyzers
  - Provider classification integration
  - Scoring and segment determination
  - Results saved to `domain_signals` and `lead_scores` tables

- G8: Leads API
  - `app/api/leads.py` - Lead query endpoints:
    - `GET /leads` - Filtered lead list (segment, min_score, provider filters)
    - `GET /leads/{domain}` - Single lead details
  - Uses `leads_ready` VIEW for efficient querying
  - Response time <1s for filtered queries

- G9: Tests & Edge Cases
  - `tests/test_scan_single.py` - DNS/WHOIS analyzer tests with mocks
  - `tests/test_scorer_rules.py` - Scoring rules and segment logic tests
  - `tests/test_ingest_csv.py` - CSV parsing and normalization tests
  - `tests/test_api_endpoints.py` - API endpoint integration tests (ingest, scan, leads)
  - Edge case coverage: timeouts, invalid domains, malformed CSV, missing MX records
  - Test coverage: 71% (75 tests passed, target ≥70% achieved)

- G10: Documentation & Demo
  - Complete README.md with setup instructions, API documentation, and example usage
  - WSL2 + Docker setup guide
  - Virtual environment setup instructions
  - Complete API endpoint documentation with examples
  - Demo scenario: 3 domain ingest → scan → leads query workflow
  - Development environment guide (`docs/active/DEVELOPMENT-ENVIRONMENT.md`)
  - WSL guide (`docs/active/WSL-GUIDE.md`)

- CI/CD Pipeline
  - `.github/workflows/ci.yml` - Complete CI pipeline:
    - Test execution with PostgreSQL service
    - Code coverage reporting
    - Docker image build
    - Docker Compose integration tests
  - `.github/workflows/lint.yml` - Code quality checks:
    - Black formatting check
    - Flake8 linting
    - MyPy type checking

### Changed
- **Dependencies**: Updated `requirements.txt` to include `idna`, `pandas`, `python-multipart`, `httpx` for ingestion and testing
- **API**: Updated `app/main.py` to register all API routers (ingest, scan, leads)
- **Documentation**: 
  - Updated README.md with complete API documentation and example usage
  - Updated documentation paths to reflect `docs/active/` structure
- **Development Tools**:
  - Enhanced `.gitignore` and `.cursorignore` with comprehensive Python, testing, and IDE exclusions
  - Added virtual environment setup script (`setup_venv.sh`) with Windows/Linux/Mac compatibility
  - Updated `setup_dev.sh` to support optional venv setup with `--with-venv` flag
  - Updated `docker-compose.yml` to mount `tests/` directory for container-based testing
- **Testing**: Improved test isolation: API endpoint tests use transaction rollback instead of table drops

### Fixed
- WHOIS analyzer exception handling (graceful fail for all exceptions)
- DNS analyzer timeout handling (proper status reporting)
- Virtual environment setup script Windows compatibility (python3 vs python command detection)
- Pip upgrade in venv script for cross-platform compatibility

### Removed
- Removed duplicate `scripts/wsl-setup-venv.sh` (functionality merged into `setup_venv.sh`)
- Consolidated WSL documentation: merged 3 separate files into single `docs/active/WSL-GUIDE.md`
- Simplified `setup_venv.sh`: removed redundant Python detection logic and WSL-specific warnings

### Deprecated
- N/A

### Security
- N/A

## [0.1.0] - 2025-11-12

### Added
- G1: Foundation & Docker Setup
  - Docker Compose setup with PostgreSQL 15 and FastAPI
  - FastAPI application skeleton with `/healthz` endpoint
  - Database connection and session management
  - Development setup script (`setup_dev.sh`)
  - Environment configuration (`.env.example`)

- G2: Database Schema & Models
  - PostgreSQL schema (`app/db/schema.sql`) with 4 tables and 1 view:
    - `raw_leads` - Raw ingested data
    - `companies` - Normalized company information (domain unique)
    - `domain_signals` - DNS and WHOIS analysis results
    - `lead_scores` - Calculated readiness scores and segments
    - `leads_ready` - View for querying ready leads
  - SQLAlchemy models (`app/db/models.py`): RawLead, Company, DomainSignal, LeadScore
  - Automatic schema migration script (`app/db/migrate.py`)

- G3: Domain Normalization & Data Files
  - `app/core/normalizer.py` - Domain normalization utilities:
    - `normalize_domain()` - Punycode decode, www stripping, lowercase
    - `extract_domain_from_email()` - Domain extraction from email addresses
    - `extract_domain_from_website()` - Domain extraction from website URLs
  - `app/core/provider_map.py` - Provider classification:
    - `load_providers()` - Load provider definitions from JSON
    - `classify_provider()` - Classify provider from MX root domain
  - `app/core/scorer.py` - Rule-based scoring engine:
    - `load_rules()` - Load scoring rules from JSON
    - `calculate_score()` - Calculate readiness score
    - `determine_segment()` - Determine lead segment (Migration, Existing, Cold, Skip)
    - `score_domain()` - Complete scoring workflow
  - `app/data/providers.json` - Provider definitions (10+ providers: M365, Google, Yandex, Zoho, Amazon, SendGrid, Mailgun, Hosting, Local, Unknown)
  - `app/data/rules.json` - Scoring rules (base_score, provider_points, signal_points, segment_rules)

### Changed
- N/A

### Fixed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Security
- N/A

