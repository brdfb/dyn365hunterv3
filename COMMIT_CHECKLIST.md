# Pre-Commit Checklist

## ✅ Code Quality
- [x] All tests passing (214 tests)
- [x] No lint errors
- [x] Code formatted (black)
- [x] Type hints present

## ✅ Documentation
- [x] CHANGELOG.md updated (G20 features added)
- [x] README.md updated (G20 features added)
- [x] API documentation updated (G20 fields in responses)
- [x] Sales documentation updated (SALES-GUIDE.md, SEGMENT-GUIDE.md, SALES-SCENARIOS.md)
- [x] Test documentation added
- [x] Docker troubleshooting guide added
- [x] G20 implementation summary added

## ✅ Features Completed
- [x] Dashboard endpoint (`GET /dashboard`) - v0.4.0
- [x] Priority Score feature - v0.4.0
- [x] Priority Score improvements - Enhanced priority scoring (1-7, Migration always prioritized, improved UI visualization)
- [x] Hard-Fail Rules (MX missing → Skip) - v0.5.0
- [x] Risk Scoring (negative points) - v0.5.0
- [x] Provider Points updated (Hosting: 20, Local: 10) - v0.5.0
- [x] G14: CSV Export + Mini UI - v1.0.0
- [x] G15: Bulk Scan & Async Queue - v1.0.0
- [x] G16: Webhook + Lead Enrichment - v1.0.0
- [x] G17: Notes/Tags/Favorites + PDF Summary - v1.0.0
- [x] G18: ReScan + Alerts + Enhanced Scoring - v1.0.0
- [x] **G20: Domain Intelligence Layer** - Local Provider, Tenant Size, DMARC Coverage ✨ YENİ
  - [x] Local Provider Detail (P0) - TürkHost, Natro, vb. tespiti
  - [x] Tenant Size Estimation (P1) - M365/Google için small/medium/large
  - [x] DMARC Coverage (P1) - pct parametresi parsing
  - [x] Database migration completed
  - [x] API responses updated
  - [x] **Mini UI integration** - Tablo kolonları ve score breakdown modal güncellendi
  - [x] Documentation updated (SALES-GUIDE, SEGMENT-GUIDE, SALES-SCENARIOS)
  - [x] All tests passing
  - [x] All commits pushed to origin/main
- [x] All tests passing
- [x] Version updated to 1.0.0

## ✅ CI/CD
- [x] GitHub Actions workflows configured
- [x] Test pipeline working
- [x] Lint pipeline working
- [x] Docker build pipeline working

## ✅ Git Status
- [x] All changes committed
- [x] Commit message follows convention
- [x] Ready for push
- [x] Pushed to origin/main

## ✅ Context & Documentation Rules
- [x] Hunter Roadmap Mode rules added to `.cursor/rules/.cursorrules`
- [x] Context management rules documented (priority file reading order)
- [x] Dev vs Prod separation rules documented
- [x] D365 & Partner Center state rules documented
- [x] Documentation management priority order documented
- [x] Work style (Hunter Modu) rules documented
- [x] New chat/task summary process documented

## Commit Message Suggestion (v1.0.0)

```
feat: Post-MVP Sprint 2-5 completion - Major feature release (v1.0.0)

Features:
- G14: CSV Export + Mini UI - Lead export and simple web interface
- G15: Bulk Scan & Async Queue - Async bulk domain scanning with Celery + Redis
- G16: Webhook + Lead Enrichment - API key authentication and lead enrichment
- G17: Notes/Tags/Favorites + PDF Summary - CRM-lite features and PDF generation
- G18: ReScan + Alerts + Enhanced Scoring - Automation, change detection, and alerts

Major Changes:
- Added Celery + Redis for async task processing
- Added API key authentication system
- Added CRM-lite features (notes, tags, favorites)
- Added PDF summary generation
- Added ReScan infrastructure with change detection
- Added alerts system with notifications
- Enhanced scoring with additional risk detection

Documentation:
- Updated CHANGELOG.md (v1.0.0)
- Updated README.md with G15-G18 features
- Updated API documentation
- All feature documentation complete

Tests:
- Comprehensive test suite for all new features
- All 214 tests passing
- Test coverage maintained

Closes: Post-MVP Sprint 2-5 (G14-G18)
```

