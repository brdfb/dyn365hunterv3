# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- DNS resolver: Added public DNS servers (8.8.8.8, 1.1.1.1, etc.) for reliable DNS resolution in containers
- Lead endpoint: Fixed `/lead/{domain}` endpoint - changed from VIEW query to direct JOIN for better reliability
- CHANGELOG: Added missing G3 phase documentation

### Changed
- DNS analyzer: All DNS queries now use public DNS servers for consistent resolution
- Lead endpoint: Improved error handling and query reliability

### Removed
- Removed temporary test script (`test_google_domain.sh`) - archived
- Removed demo script (`scripts/demo.sh`) - archived
- Removed completed action items (`docs/active/ACTIONS.json`) - archived

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
    - `GET /lead/{domain}` - Single lead details
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

