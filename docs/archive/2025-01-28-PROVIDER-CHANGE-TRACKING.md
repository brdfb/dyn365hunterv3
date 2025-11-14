# Provider Change Tracking

**Date:** 2025-01-28  
**Status:** ✅ Implemented  
**Feature:** Automatic detection and logging of provider changes

## Overview

The system automatically tracks when a domain switches email providers (e.g., Google → M365, Local → Google). This enables sales teams to identify migration opportunities and track customer behavior over time.

## How It Works

### Automatic Detection

When a domain is scanned (via `/scan/domain` or CSV ingestion with `auto_scan=true`):

1. **Current provider** is retrieved from the `companies` table
2. **New provider** is detected from MX records
3. **Comparison** is made between old and new provider
4. **If different**, a change record is created in `provider_change_history` table

### Database Schema

```sql
CREATE TABLE provider_change_history (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL REFERENCES companies(domain) ON DELETE CASCADE,
    previous_provider VARCHAR(50),
    new_provider VARCHAR(50) NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    scan_id INTEGER
);
```

### Example Scenario

**Week 1:**
- Domain: `example.com`
- Provider: `Google`
- Scan performed → No change logged (first scan)

**Week 2:**
- Domain: `example.com`
- Provider: `M365` (customer migrated)
- Scan performed → Change logged:
  ```json
  {
    "domain": "example.com",
    "previous_provider": "Google",
    "new_provider": "M365",
    "changed_at": "2025-01-28T10:30:00Z"
  }
  ```

## Querying Provider Changes

### SQL Query

```sql
-- Get all provider changes for a specific domain
SELECT domain, previous_provider, new_provider, changed_at
FROM provider_change_history
WHERE domain = 'example.com'
ORDER BY changed_at DESC;

-- Get recent provider changes (last 30 days)
SELECT domain, previous_provider, new_provider, changed_at
FROM provider_change_history
WHERE changed_at >= NOW() - INTERVAL '30 days'
ORDER BY changed_at DESC;

-- Get domains that switched to M365
SELECT domain, previous_provider, new_provider, changed_at
FROM provider_change_history
WHERE new_provider = 'M365'
ORDER BY changed_at DESC;
```

### API Endpoint (Future)

A dedicated API endpoint for querying provider changes is planned:

```bash
# Get provider changes for a domain
GET /provider-changes?domain=example.com

# Get recent provider changes
GET /provider-changes?since=2025-01-01
```

## Use Cases

### 1. Migration Opportunity Detection

When a customer switches from Google to M365, this indicates:
- Active migration in progress
- Potential upsell opportunity
- Customer is evaluating cloud solutions

### 2. Customer Behavior Tracking

Track how customers change providers over time:
- Local → Cloud migration trends
- Provider switching patterns
- Migration frequency

### 3. Sales Follow-up

Identify customers who recently migrated:
- Follow up within 1-2 weeks of migration
- Offer additional services
- Understand migration reasons

## Implementation Details

### Code Locations

- **Model**: `app/db/models.py` - `ProviderChangeHistory` class
- **Scan Endpoint**: `app/api/scan.py` - Provider change detection and logging
- **CSV Ingestion**: `app/api/ingest.py` - Provider change detection during bulk scan

### Key Logic

```python
# Track provider changes
previous_provider = company.provider
provider_changed = False

# Update company provider if we have new information
if provider and provider != "Unknown":
    if previous_provider != provider:
        provider_changed = True
    company.provider = provider

# Log provider change if detected
if provider_changed and previous_provider:
    change_history = ProviderChangeHistory(
        domain=domain,
        previous_provider=previous_provider,
        new_provider=provider
    )
    db.add(change_history)
```

## Notes

- **First Scan**: No change is logged (no previous provider to compare)
- **Unknown Provider**: Changes from/to "Unknown" are not logged (not meaningful)
- **Same Provider**: No change is logged if provider remains the same
- **Cascade Delete**: If a company is deleted, all its change history is automatically deleted

## Future Enhancements

1. **API Endpoint**: Dedicated endpoint for querying provider changes
2. **Notifications**: Email/webhook notifications for significant provider changes
3. **Analytics**: Dashboard showing provider change trends
4. **Export**: CSV export of provider changes for analysis

