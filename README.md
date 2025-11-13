# Dyn365Hunter MVP

Lead intelligence engine for domain-based analysis and rule-based scoring.

[![CI/CD Pipeline](https://github.com/brdfb/dyn365hunterv3/actions/workflows/ci.yml/badge.svg)](https://github.com/brdfb/dyn365hunterv3/actions/workflows/ci.yml)
[![Code Quality](https://github.com/brdfb/dyn365hunterv3/actions/workflows/lint.yml/badge.svg)](https://github.com/brdfb/dyn365hunterv3/actions/workflows/lint.yml)

## Overview

Dyn365Hunter MVP is a FastAPI-based application that analyzes domains for lead intelligence. It performs DNS/WHOIS analysis and applies rule-based scoring to identify potential migration opportunities.

**Target**: ≤2 minute "kahvelik" analysis flow for sales team.

## Features

- ✅ Docker Compose setup with PostgreSQL and FastAPI
- ✅ Database schema with 4 tables and 1 view
- ✅ Domain normalization (punycode, www stripping, email/URL extraction)
- ✅ Provider mapping (M365, Google, Yandex, Zoho, Amazon, SendGrid, Mailgun, Hosting, Local, Unknown)
- ✅ Rule-based scoring engine with segment classification
- ✅ Domain ingestion (CSV + single domain endpoints)
- ✅ DNS analysis (MX/SPF/DKIM/DMARC with 10s timeout)
- ✅ WHOIS lookup (graceful fail with 5s timeout)
- ✅ Lead segmentation API with filtering
- ✅ Dashboard endpoint with aggregated statistics
- ✅ Priority score calculation for lead prioritization

## Tech Stack

- **Backend**: FastAPI (Python 3.10)
- **Database**: PostgreSQL 15
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
   - Start Docker Compose services
   - Wait for PostgreSQL to be ready
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

## API Endpoints

### Health Check
- `GET /healthz` - Health check and database connection status

### Ingest
- `POST /ingest/domain` - Ingest single domain
  - Request body: `{"domain": "example.com", "company_name": "Example Inc", "email": "user@example.com", "website": "https://example.com"}`
  - Returns: `{"domain": "example.com", "company_id": 1, "message": "Domain ingested successfully"}`
- `POST /ingest/csv` - Ingest domains from CSV file
  - Multipart form data with CSV file
  - Required column: `domain`
  - Optional columns: `company_name`, `email`, `website`
  - Returns: `{"ingested": 5, "total_rows": 5, "errors": null}`

### Scan
- `POST /scan/domain` - Analyze single domain (DNS + WHOIS + scoring)
  - Request body: `{"domain": "example.com"}`
  - Returns: `{"domain": "example.com", "score": 75, "segment": "Migration", "reason": "...", "provider": "M365", "mx_root": "outlook.com", "spf": true, "dkim": true, "dmarc_policy": "reject", "scan_status": "success"}`
  - Performs DNS analysis (MX, SPF, DKIM, DMARC) and WHOIS lookup
  - Calculates readiness score and determines segment

### Leads
- `GET /leads` - Query leads with filters
  - Query parameters:
    - `segment` (optional): Filter by segment (Migration, Existing, Cold, Skip)
    - `min_score` (optional): Minimum readiness score (0-100)
    - `provider` (optional): Filter by provider (M365, Google, etc.)
  - Returns: Array of lead objects with `priority_score` field (1-6, where 1 is highest priority)
- `GET /leads/{domain}` - Get single lead details
  - Returns: Complete lead information including signals, scores, priority_score, and metadata

### Dashboard
- `GET /dashboard` - Get aggregated dashboard statistics
  - Returns: `{"total_leads": 150, "migration": 25, "existing": 50, "cold": 60, "skip": 15, "avg_score": 55.5, "high_priority": 10}`
  - Provides segment distribution, average score, and high priority lead count

## Development

### Project Structure

```
dyn365hunterv3/
├── app/                    # FastAPI application
│   ├── api/               # API endpoints
│   ├── core/              # Core logic (normalizer, analyzer, scorer)
│   ├── db/                # Database models and session
│   └── data/              # Configuration files (providers.json, rules.json)
├── tests/                 # Test files
├── docs/                  # Documentation
├── Dockerfile             # FastAPI container
├── docker-compose.yml     # Services configuration
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

# 3. Query leads
curl "http://localhost:8000/leads?segment=Migration&min_score=70"

# 4. Get single lead
curl "http://localhost:8000/leads/example.com"

# 5. Get dashboard statistics
curl "http://localhost:8000/dashboard"
```

## Documentation

### For Sales Team
- [Sales Guide](docs/SALES-GUIDE.md) - Quick start guide for sales team (5 minutes)
- [Segment Guide](docs/SEGMENT-GUIDE.md) - Segment and score explanations
- [Sales Scenarios](docs/SALES-SCENARIOS.md) - Real-world usage scenarios
- [Sales Demo Script](scripts/sales-demo.sh) - Quick demo script

### For Developers
- [Sales Feature Requests](docs/active/SALES-FEATURE-REQUESTS.md) - MVP scope features (Dashboard, Priority Score) and Post-MVP roadmap
- [Sales Feature Requests Critique](docs/active/SALES-FEATURE-REQUESTS-CRITIQUE.md) - Technical analysis and recommendations
- [Development Environment](docs/active/DEVELOPMENT-ENVIRONMENT.md) - Setup guide
- [WSL Guide](docs/active/WSL-GUIDE.md) - WSL2 setup and troubleshooting
- [Testing Guide](docs/active/TESTING.md) - How to run tests
- [Docker Troubleshooting](docs/active/DOCKER-TROUBLESHOOTING.md) - Common Docker issues and solutions

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

