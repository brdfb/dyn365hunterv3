# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
- CSV Export - Endpoint design needs detail
- Bulk Scan - Requires async queue (risks identified)

### Post-MVP (Low Priority)
- Email Templates, Notes/Tags, Favorites, Reminders - Requirements specified

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

