# Domain Validation

**Date:** 2025-01-28  
**Status:** ✅ Implemented  
**Feature:** Enhanced domain validation to filter invalid domains

## Problem

CSV/Excel files often contain invalid domain values:
- `nan` (pandas NaN values)
- `web sitesi` (Turkish for "website")
- `http://example.com/` (URLs instead of domains)
- Empty strings
- Invalid domain formats

These invalid domains were:
- Being stored in the database
- Causing scan failures
- Creating "Skip" segment records with score 0
- Cluttering the lead list

## Solution

### Validation Function

New `is_valid_domain()` function in `app/core/normalizer.py`:

```python
def is_valid_domain(domain: str) -> bool:
    """
    Check if a domain string is a valid domain format.
    
    Validations:
    - Not empty or whitespace-only
    - Not common invalid values (nan, n/a, web sitesi, etc.)
    - Not a URL (contains :// or starts with http)
    - Contains at least one dot
    - Each part is 1-63 characters
    - Contains only alphanumeric, hyphens, and dots
    - TLD is at least 2 characters
    """
```

### Invalid Values Filtered

The following values are automatically rejected:
- `nan`, `n/a`, `na`, `none`, `null`
- `web sitesi`, `website`, `web`
- `http`, `https`
- URLs (containing `://`)

### URL Extraction

If a URL is provided, the system extracts the domain:
- `http://www.example.com/` → `example.com`
- `https://example.com/path` → `example.com`
- `http://example.com:8080` → `example.com`

### Normalization Flow

1. **Input**: Raw domain string from CSV/Excel
2. **URL Extraction**: If URL format, extract domain
3. **Normalization**: Lowercase, remove www, strip whitespace
4. **Validation**: Check if valid domain format
5. **Rejection**: If invalid, skip with error message

## Implementation

### CSV Ingestion

```python
# Normalize domain
normalized_domain = normalize_domain(domain)
if not normalized_domain:
    errors.append(f"Row {idx + 1}: Invalid domain format '{domain}'")
    continue

# Additional validation
if not is_valid_domain(normalized_domain):
    errors.append(f"Row {idx + 1}: Invalid domain after normalization")
    continue
```

### Scan Endpoint

```python
# Check hard-fail conditions FIRST
from app.core.normalizer import is_valid_domain
if not is_valid_domain(domain):
    return {
        "score": 0,
        "segment": "Skip",
        "reason": f"Invalid domain format: {domain}"
    }
```

## Error Messages

Invalid domains are logged with descriptive error messages:

- `Row 5: Invalid domain format 'nan' (geçersiz domain formatı)`
- `Row 10: Invalid domain after normalization 'web sitesi' (normalizasyon sonrası geçersiz)`

These errors are included in the CSV ingestion response:

```json
{
    "job_id": "...",
    "ingested": 100,
    "scanned": 95,
    "errors": [
        "Row 5: Invalid domain format 'nan'",
        "Row 10: Invalid domain format 'web sitesi'"
    ]
}
```

## Examples

### Valid Domains

- `example.com` ✅
- `www.example.com` ✅ (normalized to `example.com`)
- `subdomain.example.com` ✅
- `example.co.uk` ✅

### Invalid Domains (Filtered)

- `nan` ❌
- `web sitesi` ❌
- `http://example.com/` ❌ (extracted to `example.com` if valid)
- `example` ❌ (no TLD)
- `example.` ❌ (empty TLD)
- `example..com` ❌ (double dot)

## Benefits

1. **Data Quality**: Only valid domains are stored
2. **Reduced Errors**: Fewer scan failures
3. **Cleaner Lists**: Lead list doesn't contain invalid entries
4. **Better UX**: Clear error messages for invalid data

## Migration

### Existing Invalid Records

Existing invalid domain records (e.g., `nan`, `web sitesi`) remain in the database but:
- Are filtered out during new scans
- Can be manually cleaned up if needed

### Cleanup Script

To clean up existing invalid records:

```python
from app.core.normalizer import is_valid_domain

# Find invalid companies
invalid_companies = [
    c for c in db.query(Company).all() 
    if not is_valid_domain(c.domain)
]

# Delete invalid companies and related records
for company in invalid_companies:
    db.query(LeadScore).filter(LeadScore.domain == company.domain).delete()
    db.query(DomainSignal).filter(DomainSignal.domain == company.domain).delete()
    db.delete(company)
```

## Future Enhancements

1. **TLD Validation**: Check against valid TLD list
2. **Domain Age**: Validate domain registration date
3. **DNS Validation**: Pre-check if domain resolves before storing
4. **Bulk Cleanup**: Automated cleanup of existing invalid records

