# Pre-Commit Checklist

## ✅ Code Quality
- [x] All tests passing (90 tests)
- [x] No lint errors
- [x] Code formatted (black)
- [x] Type hints present

## ✅ Documentation
- [x] CHANGELOG.md updated (v0.5.0)
- [x] README.md updated (Dashboard, Priority Score)
- [x] API documentation updated
- [x] Test documentation added
- [x] Docker troubleshooting guide added

## ✅ Features Completed
- [x] Dashboard endpoint (`GET /dashboard`) - v0.4.0
- [x] Priority Score feature - v0.4.0
- [x] Hard-Fail Rules (MX missing → Skip) - v0.5.0
- [x] Risk Scoring (negative points) - v0.5.0
- [x] Provider Points updated (Hosting: 20, Local: 10) - v0.5.0
- [x] All tests passing
- [x] Version updated to 0.5.0

## ✅ CI/CD
- [x] GitHub Actions workflows configured
- [x] Test pipeline working
- [x] Lint pipeline working
- [x] Docker build pipeline working

## ✅ Git Status
- [ ] All changes committed
- [ ] Commit message follows convention
- [ ] Ready for push

## Commit Message Suggestion (v0.5.0)

```
feat: Enhanced scoring with hard-fail rules and risk scoring (v0.5.0)

Features:
- Hard-Fail Rules: Domains with missing MX records → Skip segment automatically
- Risk Scoring: Negative points for missing security signals (SPF, DKIM, DMARC)
- Provider Points: Updated Hosting (10→20) and Local (0→10) values

Changes:
- Added check_hard_fail() function in app/core/scorer.py
- Added risk_points section in app/data/rules.json
- Updated calculate_score() to apply risk points
- Updated score_domain() to check hard-fail conditions first
- Updated POST /scan/domain to pass mx_records for hard-fail checking
- Updated app/main.py version to 0.5.0

Documentation:
- Updated docs/SEGMENT-GUIDE.md with risk scoring and hard-fail rules
- Updated docs/plans/2025-01-27-phase0-hotfix-scoring.md
- Updated CHANGELOG.md (v0.5.0)

Tests:
- Added comprehensive tests for hard-fail rules (TestHardFailRules)
- Added comprehensive tests for risk scoring (TestRiskScoring)
- Added tests for updated provider points (TestProviderPointsUpdate)
- All 103+ tests passing

Closes: Phase 0 - Enhanced Scoring & Hard-Fail Rules
```

