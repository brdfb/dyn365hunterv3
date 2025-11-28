# D365 Option Set Value Mapping

**Created:** 2025-01-30  
**Status:** Active Reference  
**Location:** `app/integrations/d365/mapping.py`

---

## Overview

D365 Choice (Option Set) fields require **integer values** instead of string literals. This document describes the mapping functions used to convert Hunter string values to D365 Option Set integer values.

---

## Mapping Functions

### 1. Segment Mapping (`_map_segment_to_option_set_value`)

**Hunter Values → D365 Integer Values:**
- `Migration` → `0`
- `Existing` → `1`
- `Cold` → `2`
- `Skip` → `3`

**Field:** `hnt_segment`  
**Source:** `lead_data.get("segment")`

---

### 2. Tenant Size Mapping (`_map_tenant_size_to_option_set_value`)

**Hunter Values → D365 Integer Values:**
- `small` → `0`
- `medium` → `1`
- `large` → `2`

**Field:** `hnt_huntertenantsize`  
**Source:** `lead_data.get("tenant_size")`  
**Note:** Values are normalized to lowercase before mapping.

---

### 3. Source Mapping (`_map_source_to_option_set_value`)

**Hunter Values → D365 Integer Values:**
- `Manual` → `0`
- `Partner Center` → `1`
- `Import` → `2`

**Field:** `hnt_source`  
**Source:** Calculated as `"Partner Center" if referral_id else "Manual"`

---

### 4. Processing Status Mapping (`_map_processing_status_to_option_set_value`)

**Hunter Values → D365 Integer Values:**
- `Idle` → `0`
- `Working` → `1`
- `Completed` → `2`
- `Error` → `3`

**Field:** `hnt_processingstatus`  
**Source:** `lead_data.get("d365_sync_status")` → mapped via `_map_processing_status()` → integer value

---

## Important Notes

### ⚠️ D365 Option Set Values May Vary

The integer values used in this mapping are **assumed defaults** based on typical D365 Option Set behavior (values start at 0 and increment by 1).

**If D365 Option Set values differ**, you must:

1. **Check D365 Option Set Metadata:**
   - Power Apps → Customizations → Option Sets
   - Or via API: `GET /api/data/v9.2/EntityDefinitions(LogicalName='lead')/Attributes`

2. **Update Mapping Functions:**
   - Edit mapping functions in `app/integrations/d365/mapping.py`
   - Update the integer values in the mapping dictionaries

### Example: Different Option Set Values

If D365 uses different values (e.g., `Existing = 100000000`), update the mapping:

```python
def _map_segment_to_option_set_value(segment: Optional[str]) -> Optional[int]:
    mapping = {
        "Migration": 100000000,  # Actual D365 value
        "Existing": 100000001,   # Actual D365 value
        "Cold": 100000002,        # Actual D365 value
        "Skip": 100000003,        # Actual D365 value
    }
    return mapping.get(segment)
```

---

## Usage in Mapping

The mapping functions are called in `map_lead_to_d365()`:

```python
hunter_fields = {
    "hnt_segment": _map_segment_to_option_set_value(lead_data.get("segment")),
    "hnt_huntertenantsize": _map_tenant_size_to_option_set_value(lead_data.get("tenant_size")),
    "hnt_source": _map_source_to_option_set_value(source_value),
    "hnt_processingstatus": _map_processing_status_to_option_set_value(processing_status_str),
}
```

**Only non-None values are included in the payload** (to avoid sending `null` for Option Set fields).

---

## Testing

To verify Option Set mapping:

```python
from app.integrations.d365.mapping import map_lead_to_d365

lead_data = {
    "segment": "Existing",
    "tenant_size": "medium",
    # ... other fields
}

payload = map_lead_to_d365(lead_data)
print(payload.get("hnt_segment"))  # Should be 1 (integer)
print(payload.get("hnt_huntertenantsize"))  # Should be 1 (integer)
```

---

## Related Documentation

- **D365 Lead Data Dictionary**: `docs/reference/LEAD-DATA-DICTIONARY.md`
- **D365 Mapping Implementation**: `app/integrations/d365/mapping.py`
- **D365 Push PoC**: `docs/archive/2025-01-30-D365-PUSH-POC-TASK-LIST.md`

---

## Future Enhancements

- **Dynamic Option Set Value Lookup**: Query D365 metadata API to get actual Option Set values at runtime
- **Caching**: Cache Option Set metadata to avoid repeated API calls
- **Validation**: Validate integer values against D365 Option Set metadata before push

