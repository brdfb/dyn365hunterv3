# Dyn365Hunter MVP

Lead intelligence engine for domain-based analysis and rule-based scoring.

[![CI/CD Pipeline](https://github.com/brdfb/dyn365hunterv3/actions/workflows/ci.yml/badge.svg)](https://github.com/brdfb/dyn365hunterv3/actions/workflows/ci.yml)
[![Code Quality](https://github.com/brdfb/dyn365hunterv3/actions/workflows/lint.yml/badge.svg)](https://github.com/brdfb/dyn365hunterv3/actions/workflows/lint.yml)

## Overview

Dyn365Hunter MVP is a FastAPI-based application that analyzes domains for lead intelligence. It performs DNS/WHOIS analysis and applies rule-based scoring to identify potential migration opportunities.

**Target**: ≤2 minute "kahvelik" analysis flow for sales team.

## Features

- ✅ Domain ingestion (CSV + single domain)
- ✅ DNS analysis (MX/SPF/DKIM/DMARC)
- ✅ WHOIS lookup (graceful fail)
- ✅ Provider mapping (M365, Google, Hosting, etc.)
- ✅ Rule-based scoring
- ✅ Lead segmentation (Existing, Migration, Cold, Skip)

## Tech Stack

- **Backend**: FastAPI (Python 3.10)
- **Database**: PostgreSQL 15
- **DNS Analysis**: dnspython
- **WHOIS**: python-whois
- **Deployment**: Docker Compose

## Quick Start

### Prerequisites

- Docker Desktop (with WSL2 integration)
- WSL2 (Ubuntu/Debian)
- Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/brdfb/dyn365hunterv3.git
   cd dyn365hunterv3
   ```

2. **Run setup script:**
   ```bash
   bash setup_dev.sh
   ```

   This will:
   - Check Docker availability
   - Create `.env` from `.env.example`
   - Start Docker Compose services
   - Wait for PostgreSQL to be ready
   - Run database schema migration
   - Verify `/healthz` endpoint

3. **Verify installation:**
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
- `POST /ingest/csv` - Ingest domains from CSV file

### Scan
- `POST /scan/domain` - Analyze single domain (DNS + WHOIS + scoring)

### Leads
- `GET /leads` - Query leads with filters (`segment`, `min_score`, `provider`)
- `GET /lead/{domain}` - Get single lead details

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

## Documentation

- [MVP Roadmap](docs/MVP-TRIMMED-ROADMAP.md) - 10-day implementation plan
- [Plan Critique](docs/CRITIQUE.md) - Plan analysis and recommendations
- [Go/No-Go Checklist](docs/GO-NO-GO-CHECKLIST.md) - Acceptance criteria
- [Actions](docs/ACTIONS.json) - Implementation action items

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

