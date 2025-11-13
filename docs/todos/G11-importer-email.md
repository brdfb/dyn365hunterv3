# G11-G13: Importer + Email Module Implementation

**Status:** Pending  
**Priority:** P0 (Importer), P1 (Email Generator), P2 (Email Validator)  
**Created:** 2025-01-27

## Overview

Add two new modules to Dyn365Hunter MVP:
1. **Importer Module** (G11) - Excel/CSV column auto-detection
2. **Email Generator** (G12) - Generic email generation
3. **Email Validator** (G13) - Light email validation

## Priority Breakdown

### P0: Importer Module (G11) - MUST HAVE
- **Why:** Critical for OSB Excel file ingestion
- **Impact:** High - enables sales team to import OSB lists directly
- **Dependencies:** None (uses existing normalizer)
- **Risk:** Low (backward compatible)

### P1: Email Generator (G12) - SHOULD HAVE
- **Why:** Quick win, simple implementation
- **Impact:** Medium - useful for sales outreach
- **Dependencies:** None
- **Risk:** Very Low

### P2: Email Validator (G13) - NICE TO HAVE
- **Why:** SMTP validation has reliability/performance concerns
- **Impact:** Medium - but can be added incrementally
- **Dependencies:** Email Generator (G12)
- **Risk:** Medium (SMTP spam/blacklist concerns)

## Implementation Order

1. **G11: Importer** (P0) - Start here
2. **G12: Email Generator** (P1) - After G11
3. **G13: Email Validator** (P2) - After G12

## Acceptance Criteria

### G11: Importer Module
- [ ] Excel support (.xlsx, .xls) added to `/ingest/csv`
- [ ] `auto_detect_columns` query parameter (default: False)
- [ ] Column guessing functions in `app/core/importer.py`
- [ ] Backward compatibility maintained (existing CSV ingestion works)
- [ ] Tests for column detection
- [ ] Documentation updated

### G12: Email Generator
- [ ] `generate_generic_emails()` function
- [ ] Generic email list (Türkçe + International)
- [ ] API endpoint `/email/generate-and-validate` (generation only, validation later)
- [ ] Tests for email generation
- [ ] Documentation updated

### G13: Email Validator
- [ ] Syntax validation (regex)
- [ ] MX record validation (DNS)
- [ ] Optional SMTP validation (flag-based)
- [ ] Confidence score (high/medium/low)
- [ ] Tests with mocks
- [ ] Documentation updated

## Notes

- All modules follow MVP scope (no UI, no bulk operations)
- Importer reuses existing `normalizer` module (no duplication)
- Email validator uses light validation by default (SMTP optional)
- All changes are backward compatible

## Related Documentation

- Implementation Plan: `docs/plans/2025-01-27-IMPORTER-EMAIL-IMPLEMENTATION-PLAN.md`
- Critique: `docs/plans/2025-01-27-IMPORTER-EMAIL-MODULE-CRITIQUE.md`

