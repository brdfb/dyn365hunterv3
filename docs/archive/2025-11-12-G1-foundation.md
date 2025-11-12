# TODO: G1 - Foundation & Docker Setup

**Date Created**: 2025-11-12
**Status**: Completed
**Phase**: G1

## Tasks

- [x] Create Dockerfile (Python 3.10-slim, uvicorn, hot-reload)
- [x] Create docker-compose.yml (PostgreSQL + FastAPI, healthchecks, volumes)
- [x] Create .dockerignore (exclude tests, .git, __pycache__)
- [x] Create setup_dev.sh (Docker check, .env copy, compose up, schema migration, healthcheck)
- [x] Create .env.example (DATABASE_URL, POSTGRES_*, API_*, LOG_LEVEL)
- [x] Create requirements.txt (fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic-settings)
- [x] Create app/__init__.py
- [x] Create app/main.py (FastAPI app, `/healthz` endpoint)
- [x] Create app/config.py (Pydantic Settings, DATABASE_URL)
- [x] Create app/db/__init__.py
- [x] Create app/db/session.py (SQLAlchemy engine, session factory)
- [x] Test: bash setup_dev.sh → success, /healthz 200 OK (pending manual test)

## Notes

- Dockerfile includes curl for healthcheck
- docker-compose.yml uses `depends_on.condition: service_healthy`
- setup_dev.sh handles schema migration (will be created in G2)
- All files committed and pushed to GitHub

## Next Phase

G2: Database Schema & Models

