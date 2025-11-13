# Duplicate Prevention

**Date:** 2025-01-28  
**Status:** ✅ Implemented  
**Feature:** Automatic prevention and cleanup of duplicate LeadScore and DomainSignal records

## Problem

Previously, when a domain was scanned multiple times, duplicate records could be created in:
- `lead_scores` table (multiple scores for the same domain)
- `domain_signals` table (multiple signal records for the same domain)

This caused:
- Incorrect lead counts in the UI
- Confusion about which score is current
- Data quality issues

## Solution

### Automatic Cleanup on Scan

Before creating new records, the system now:
1. **Deletes** all existing `LeadScore` records for the domain
2. **Deletes** all existing `DomainSignal` records for the domain
3. **Creates** new records with the latest scan results

This ensures:
- Only one `LeadScore` record per domain
- Only one `DomainSignal` record per domain
- Always reflects the most recent scan

### Implementation

#### Scan Endpoint (`/scan/domain`)

```python
# Delete any existing domain_signals for this domain (prevent duplicates)
db.query(DomainSignal).filter(DomainSignal.domain == domain).delete()

# Create new domain_signal
domain_signal = DomainSignal(...)
db.add(domain_signal)

# Delete any existing lead_scores for this domain (prevent duplicates)
db.query(LeadScore).filter(LeadScore.domain == domain).delete()

# Create new lead_score
lead_score = LeadScore(...)
db.add(lead_score)
```

#### CSV Ingestion (`/ingest/csv`)

Same logic is applied during bulk CSV ingestion when `auto_scan=true`.

## Database Constraints

### Current State

- `companies.domain`: **UNIQUE** constraint (prevents duplicate companies)
- `lead_scores.domain`: **NO UNIQUE** constraint (allows multiple, but cleaned up on scan)
- `domain_signals.domain`: **NO UNIQUE** constraint (allows multiple, but cleaned up on scan)

### Why No Unique Constraints?

Unique constraints on `lead_scores` and `domain_signals` would prevent:
- Historical tracking (if needed in future)
- Race condition handling during concurrent scans
- Flexible cleanup strategies

Instead, we use **application-level cleanup** which is more flexible.

## Cleanup Script

For existing duplicate records, a cleanup script was created:

```python
# Find all duplicate domains
duplicates = db.query(LeadScore.domain, func.count(LeadScore.id))
    .group_by(LeadScore.domain)
    .having(func.count(LeadScore.id) > 1)
    .all()

# Keep the most recent record, delete others
for domain, count in duplicates:
    all_records = db.query(LeadScore)
        .filter(LeadScore.domain == domain)
        .order_by(LeadScore.updated_at.desc())
        .all()
    
    # Keep first (most recent), delete rest
    for record in all_records[1:]:
        db.delete(record)
```

## Testing

### Manual Test

1. Scan a domain: `POST /scan/domain` with `{"domain": "example.com"}`
2. Check records: `SELECT COUNT(*) FROM lead_scores WHERE domain = 'example.com'` → Should be 1
3. Scan again: `POST /scan/domain` with same domain
4. Check records again: Should still be 1 (not 2)

### Edge Cases

- **Concurrent Scans**: If two scans happen simultaneously, both will delete and create. The last one to commit wins (acceptable behavior).
- **Failed Scan**: If scan fails after delete but before create, domain will have no records (will be recreated on next scan).

## Benefits

1. **Data Quality**: No duplicate records
2. **Accurate Counts**: Lead counts in UI are correct
3. **Current Data**: Always shows most recent scan results
4. **Simplified Queries**: No need to filter duplicates in queries

## Future Enhancements

1. **Unique Constraints**: Add database-level unique constraints if historical tracking is not needed
2. **Soft Delete**: Instead of hard delete, mark records as "superseded" for audit trail
3. **Change Tracking**: Track score/segment changes over time (similar to provider changes)

