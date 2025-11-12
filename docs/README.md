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

### Active Documentation
- `CRITIQUE.md` - Plan critique and recommendations
- `GO-NO-GO-CHECKLIST.md` - Acceptance criteria
- `MVP-TRIMMED-ROADMAP.md` - 10-day implementation roadmap

### Archived Documentation
- `2025-11-12-G1-foundation.md` - G1: Foundation & Docker Setup (Completed)
- `2025-11-12-G2-database-schema.md` - G2: Database Schema & Models (Completed)
- `2025-11-12-G3-domain-normalization.md` - G3: Domain Normalization & Data Files (Completed)
- `2025-11-12-PATCH-SUGGESTIONS.diff` - Plan patch suggestions (archived)
- `2025-11-12-ACTIONS.json` - Implementation action items (all completed, archived)
- `2025-11-12-test-google-domain.sh` - Temporary test script (archived)
- `2025-11-12-demo-script.sh` - Demo script (archived)

**Note:** Phases G4-G10 are completed (see CHANGELOG.md for details). Phase documentation for G4-G10 was not created as separate TODO files, but all work is documented in CHANGELOG.md.

### Important Prompts & Decisions
- `2025-11-12-initial-setup.md` - Initial project setup
- `2025-11-12-alembic-decision.md` - [DECISION] Alembic migration approach
- `2025-11-12-phase-completion-workflow.md` - Phase completion workflow enhancement

### TODOs
- (No active TODOs - All phases G1-G10 completed)

