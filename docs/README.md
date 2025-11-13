# Documentation Structure

## 📁 Folder Organization

```
docs/
├── active/          # Active documentation (current phase)
├── archive/         # Archived documentation (completed phases)
├── prompts/         # Important prompts, conversations, and architectural decisions
├── todos/           # TODO lists and task tracking
└── plans/           # Project plans and roadmaps
```

## 📋 Documentation Lifecycle

1. **Active** → Current phase documentation
2. **Archive** → Completed phase documentation
3. **Prompts** → Important prompts, conversations, and architectural decisions saved for reference
4. **Todos** → Task tracking and completion status

## 🔄 Archive Rules

- Move to `archive/` when phase is complete
- Keep only active documentation in `active/`
- Archive with date prefix: `YYYY-MM-DD-filename.md`

## 📝 Current Status

### Active Documentation (Reference Guides)
- `DEVELOPMENT-ENVIRONMENT.md` - Development environment setup guide
- `WSL-GUIDE.md` - WSL2 setup and configuration guide
- `TESTING.md` - Testing guide and troubleshooting
- `DOCKER-TROUBLESHOOTING.md` - Docker troubleshooting guide

**Note:** Active documentation now contains only reference guides (setup, troubleshooting, testing). Phase-specific and planning documentation has been moved to `plans/` and `archive/`.

### Archived Documentation
- `2025-01-27-MVP-TRIMMED-ROADMAP.md` - 10-day implementation roadmap (Completed)
- `2025-11-12-G1-foundation.md` - G1: Foundation & Docker Setup (Completed)
- `2025-11-12-G2-database-schema.md` - G2: Database Schema & Models (Completed)
- `2025-11-12-G3-domain-normalization.md` - G3: Domain Normalization & Data Files (Completed)
- `2025-01-27-G11-importer-email.md` - G11-G13: Importer + Email Module Implementation (Completed)
  - G11: Importer Module - Excel/CSV column auto-detection
  - G12: Email Generator - Generic email generation
  - G13: Email Validator - Light email validation (syntax, MX, optional SMTP)
- `2025-11-12-PATCH-SUGGESTIONS.diff` - Plan patch suggestions (archived)
- `2025-11-12-ACTIONS.json` - Implementation action items (all completed, archived)
- `2025-11-12-test-google-domain.sh` - Temporary test script (archived)
- `2025-11-12-demo-script.sh` - Demo script (archived)

**Note:** 
- All MVP phases (G1-G10) are completed (see CHANGELOG.md for details)
- MVP scope features (Dashboard, Priority Score) completed in v0.4.0
- Phase documentation for G4-G10 was not created as separate TODO files, but all work is documented in CHANGELOG.md
- G11-G13 (Importer + Email modules) completed in 2025-01-27

### Important Prompts & Decisions
- `2025-11-12-initial-setup.md` - Initial project setup
- `2025-11-12-alembic-decision.md` - [DECISION] Alembic migration approach
- `2025-11-12-phase-completion-workflow.md` - Phase completion workflow enhancement

### Project Plans
- `2025-01-27-phase0-hotfix-scoring.md` - Phase 0: Enhanced Scoring & Hard-Fail Rules (Completed)
- `2025-01-27-SALES-FEATURE-REQUESTS.md` - Sales team feature requests (MVP scope completed, Post-MVP planning)
- `2025-01-27-SALES-FEATURE-REQUESTS-CRITIQUE.md` - Technical review of feature requests
- `2025-01-27-IMPORTER-EMAIL-IMPLEMENTATION-PLAN.md` - Importer + Email Module Implementation Plan (v2, Prioritized)
- `2025-01-27-IMPORTER-EMAIL-MODULE-CRITIQUE.md` - Design critique and alternative approaches

### TODOs
- No active TODOs - All phases completed

