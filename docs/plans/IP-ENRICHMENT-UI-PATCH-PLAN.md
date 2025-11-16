# IP Enrichment UI Integration - Patch Plan

**Date**: 2025-01-28  
**Status**: 📋 **Ready for Implementation**  
**Approach**: Minimal (Yaklaşım A)  
**Sprint**: G19 sonrası mini sprint

---

## 🎯 Overview

Minimal IP enrichment integration:
- **Backend**: Add IP enrichment to score-breakdown and sales-summary endpoints
- **UI**: Add minimal "Network & Location" section to Score Breakdown modal (country + proxy warning)
- **Sales Engine**: Add IP context to prompt (structured, not hard-coded)

---

## 📁 File-by-File Patch Plan

### 1. Backend: Response Models

#### File: `app/api/leads.py`

**Location**: After line 690 (after `dmarc_coverage` field)

**Add**:
```python
# IP Enrichment schema (minimal)
class IPEnrichmentSchema(BaseModel):
    """Minimal IP enrichment data for UI display."""
    country: Optional[str] = None  # ISO 3166-1 alpha-2 country code (e.g., "TR")
    is_proxy: Optional[bool] = None  # Proxy detection result
    proxy_type: Optional[str] = None  # Proxy type (VPN, TOR, PUB, etc.)
```

**Location**: In `ScoreBreakdownResponse` class (after line 690)

**Add**:
```python
    # IP Enrichment (optional)
    ip_enrichment: Optional[IPEnrichmentSchema] = None
```

**Location**: In `get_score_breakdown` function (after line 762, before return)

**Add**:
```python
    # Get IP enrichment (optional)
    from app.core.enrichment_service import latest_ip_enrichment
    from app.db.models import IpEnrichment
    
    ip_enrichment_record = latest_ip_enrichment(normalized_domain, db)
    ip_enrichment_data = None
    if ip_enrichment_record:
        ip_enrichment_data = IPEnrichmentSchema(
            country=ip_enrichment_record.country,
            is_proxy=ip_enrichment_record.is_proxy,
            proxy_type=ip_enrichment_record.proxy_type,
        )
    
    breakdown_dict["ip_enrichment"] = ip_enrichment_data
```

---

### 2. Backend: Sales Summary Endpoint

#### File: `app/api/sales_summary.py`

**Location**: After line 86 (after extracting `expires_at`)

**Add**:
```python
    # Get IP enrichment (optional)
    from app.core.enrichment_service import latest_ip_enrichment
    from app.db.models import IpEnrichment
    
    ip_enrichment_record = latest_ip_enrichment(normalized_domain, db)
    ip_context = None
    if ip_enrichment_record:
        ip_context = {
            "country": ip_enrichment_record.country,
            "is_proxy": ip_enrichment_record.is_proxy,
            "proxy_type": ip_enrichment_record.proxy_type,
        }
```

**Location**: In `generate_sales_summary` call (line 99, add new parameter)

**Modify**:
```python
    # Generate sales summary
    summary = generate_sales_summary(
        domain=normalized_domain,
        provider=provider,
        segment=segment,
        readiness_score=readiness_score,
        priority_score=priority_score,
        tenant_size=tenant_size,
        local_provider=local_provider,
        spf=spf,
        dkim=dkim,
        dmarc_policy=dmarc_policy,
        dmarc_coverage=dmarc_coverage,
        contact_quality_score=contact_quality_score,
        expires_at=expires_at,
        tuning_factor=tuning_factor,
        ip_context=ip_context,  # NEW: IP enrichment context
    )
```

---

### 3. Backend: Sales Engine

#### File: `app/core/sales_engine.py`

**Location**: In `generate_sales_summary` function signature (after line 442)

**Add parameter**:
```python
def generate_sales_summary(
    domain: str,
    provider: Optional[str],
    segment: Optional[str],
    readiness_score: Optional[int],
    priority_score: Optional[int],
    tenant_size: Optional[str],
    local_provider: Optional[str] = None,
    spf: Optional[bool] = None,
    dkim: Optional[bool] = None,
    dmarc_policy: Optional[str] = None,
    dmarc_coverage: Optional[int] = None,
    contact_quality_score: Optional[int] = None,
    expires_at: Optional[date] = None,
    tuning_factor: float = 1.0,
    ip_context: Optional[Dict[str, Any]] = None,  # NEW: IP enrichment context
) -> Dict[str, Any]:
```

**Location**: In function docstring (after line 460)

**Add**:
```python
        ip_context: Optional IP enrichment context dict with:
            - country: Optional[str] - ISO 3166-1 alpha-2 country code
            - is_proxy: Optional[bool] - Proxy detection result
            - proxy_type: Optional[str] - Proxy type (VPN, TOR, PUB, etc.)
```

**Location**: In function body (after line 465, before return statement)

**Add IP context to prompt building** (if using LLM, otherwise skip):
```python
    # Build IP context string for prompt (if available)
    ip_context_str = None
    if ip_context:
        parts = []
        if ip_context.get("country"):
            parts.append(f"Country: {ip_context['country']}")
        if ip_context.get("is_proxy"):
            proxy_type = ip_context.get("proxy_type", "unknown")
            parts.append(f"Proxy detected: {proxy_type}")
        if parts:
            ip_context_str = ", ".join(parts)
    
    # Note: IP context is available for future LLM integration
    # For now, it's passed but not actively used in text generation
    # This prepares the infrastructure for future enhancements
```

**Note**: Since `generate_sales_summary` currently uses rule-based logic (not LLM), IP context is added to the function signature but not actively used yet. This prepares the infrastructure for future LLM integration.

---

### 4. Frontend: TypeScript Types

#### File: `mini-ui/types/sales.ts` (or create new `mini-ui/types/score.ts`)

**Add** (or create file if doesn't exist):
```typescript
/**
 * IP Enrichment data (minimal subset for UI)
 */
export interface IpEnrichment {
    country?: string | null;   // ISO 3166-1 alpha-2 country code (e.g., "TR")
    is_proxy?: boolean | null;  // Proxy detection result
    proxy_type?: string | null; // Proxy type (VPN, TOR, PUB, etc.)
}

/**
 * Score Breakdown response (extends existing)
 */
export interface ScoreBreakdown {
    base_score: number;
    provider: {
        name: string;
        points: number;
    };
    signal_points: Record<string, number>;
    risk_points: Record<string, number>;
    total_score: number;
    tenant_size?: string | null;
    local_provider?: string | null;
    dmarc_coverage?: number | null;
    ip_enrichment?: IpEnrichment | null;  // NEW: IP enrichment data
}
```

---

### 5. Frontend: UI Rendering

#### File: `mini-ui/js/ui-leads.js`

**Location**: In `showScoreBreakdown` function (after line 420, after Domain Intelligence section closes)

**Add**:
```javascript
    // IP Enrichment: Network & Location (minimal)
    if (breakdown.ip_enrichment) {
        const ip = breakdown.ip_enrichment;
        const hasData = ip.country || ip.is_proxy;
        
        if (hasData) {
            html += `<div class="score-breakdown__section">
                <div class="score-breakdown__section-title">Network &amp; Location</div>`;
            
            // Country
            if (ip.country) {
                html += `<div class="score-breakdown__item">
                    <span class="score-breakdown__label">Ülke</span>
                    <span class="score-breakdown__value">${escapeHtml(ip.country)}</span>
                </div>`;
            }
            
            // Proxy warning
            if (ip.is_proxy) {
                const proxyType = ip.proxy_type ? ` (${escapeHtml(ip.proxy_type)})` : '';
                html += `<div class="score-breakdown__item">
                    <span class="score-breakdown__label">Proxy Uyarısı</span>
                    <span class="score-breakdown__value score-breakdown__value--warning">
                        ⚠️ Proxy tespit edildi${proxyType}
                    </span>
                </div>`;
            }
            
            html += `</div>`;
        }
    }
```

**Note**: Section only renders if `ip_enrichment` exists AND has at least one field (country or is_proxy). This prevents empty sections.

---

### 6. CSS Styling (Optional Enhancement)

#### File: `mini-ui/styles.css`

**Location**: After existing `.score-breakdown__value--positive` styles

**Add** (if not exists):
```css
/* IP Enrichment: Warning style for proxy detection */
.score-breakdown__value--warning {
    color: #d97706; /* amber-600 */
    font-weight: 500;
}
```

---

## ✅ Testing Checklist

### Backend Tests

- [ ] **Score Breakdown with IP enrichment**
  - Test domain with IP enrichment → `ip_enrichment` field populated
  - Test domain without IP enrichment → `ip_enrichment` is `null`
  - Test domain with partial IP data (only country) → `is_proxy` is `null`

- [ ] **Sales Summary with IP context**
  - Test domain with IP enrichment → `ip_context` passed to `generate_sales_summary`
  - Test domain without IP enrichment → `ip_context` is `None`
  - Verify function signature accepts `ip_context` parameter

### Frontend Tests

- [ ] **Score Breakdown Modal**
  - Test domain with IP enrichment (country + proxy) → Section visible with both fields
  - Test domain with IP enrichment (only country) → Section visible with country only
  - Test domain without IP enrichment → Section not rendered (no empty box)
  - Test domain with `ip_enrichment: null` → Section not rendered

- [ ] **Visual Check**
  - Proxy warning displays with amber color
  - Country code displays correctly
  - Section appears after "Domain Intelligence" section
  - Layout doesn't break on mobile

### Integration Tests

- [ ] **End-to-end flow**
  1. Scan domain with IP enrichment enabled
  2. Open Score Breakdown modal
  3. Verify "Network & Location" section appears
  4. Verify country and proxy warning (if applicable)

- [ ] **Edge Cases**
  - Multiple IPs → Latest enrichment record used
  - IP enrichment async still running → No "loading" state (acceptable for Phase 1)
  - Enrichment disabled → Section not rendered

---

## 📝 Implementation Notes

### Design Decisions

1. **Minimal Schema**: Only 3 fields (country, is_proxy, proxy_type) to keep scope small
2. **Optional Everywhere**: All IP enrichment fields are optional to handle missing data gracefully
3. **Conditional Rendering**: UI section only renders if data exists (no empty boxes)
4. **Future-Proof**: Sales engine accepts `ip_context` but doesn't use it yet (prepares for LLM integration)

### Performance Considerations

- **Extra DB Query**: `latest_ip_enrichment()` adds one query per modal open
  - **Acceptable for Phase 1**: G19 traffic profile is low
  - **Future optimization**: Add to `leads_ready` view or Redis cache

### Backward Compatibility

- All changes are **additive** (new optional fields)
- Existing endpoints continue to work without IP enrichment
- UI gracefully handles missing IP enrichment data

---

## 🚀 Deployment Checklist

1. [ ] Backend changes deployed
2. [ ] Frontend changes deployed
3. [ ] Test with domain that has IP enrichment
4. [ ] Test with domain without IP enrichment
5. [ ] Verify no console errors
6. [ ] Verify modal layout doesn't break

---

## 📚 Related Files

- `app/core/enrichment_service.py` - `latest_ip_enrichment()` function (already exists)
- `app/db/models.py` - `IpEnrichment` model (already exists)
- `docs/archive/2025-01-28-IP-ENRICHMENT-IMPLEMENTATION.md` - Full IP enrichment docs

---

**Status**: Ready for implementation after G19 sales flow completion.

