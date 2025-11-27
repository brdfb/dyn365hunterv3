# Çözüm 2 - Multiple Referrals Aggregate Plan

**Tarih**: 2025-01-30  
**Durum**: ✅ **TAMAMLANDI (MVP)**  
**Öncelik**: Orta (Çözüm 1 tamamlandıktan sonra)

---

## 🎯 Amaç

Aynı domain için birden fazla referral olduğunda, kullanıcıya aggregate bilgi göstermek:
- Toplam referral sayısı
- Tüm referral type'ları (array)
- Tüm referral ID'leri (opsiyonel)
- Link status breakdown (kaç tanesi linked, kaç tanesi unlinked)

**Mevcut Durum (Çözüm 1):**
- `referral_type`: Sadece bir referral type (MAX() ile seçiliyor)
- `link_status`: Aggregate (none/linked/unlinked/mixed)
- `referral_id`: Sadece primary referral ID (en yeni)

**Hedef Durum (Çözüm 2):**
- `referral_count`: Toplam referral sayısı
- `referral_types`: Array of referral types (["co-sell", "marketplace"])
- `referral_ids`: Array of referral IDs (opsiyonel, veya sadece primary)
- `link_status`: Aynı kalacak (aggregate)
- `link_status_breakdown`: Opsiyonel - {"linked": 2, "unlinked": 1}

---

## 📊 Senaryo Örnekleri

### Senaryo 1: Tek Referral
**Domain**: `example.com`
- 1 referral: `co-sell`, `linked`

**Response (Çözüm 1):**
```json
{
  "referral_type": "co-sell",
  "link_status": "linked",
  "referral_id": "ref-001"
}
```

**Response (Çözüm 2):**
```json
{
  "referral_count": 1,
  "referral_types": ["co-sell"],
  "referral_type": "co-sell",  // Backward compatibility
  "link_status": "linked",
  "referral_id": "ref-001",  // Primary (backward compatibility)
  "referral_ids": ["ref-001"]  // Optional
}
```

### Senaryo 2: Multiple Referrals (Farklı Types)
**Domain**: `example.com`
- Referral 1: `co-sell`, `linked`, `ref-001`
- Referral 2: `marketplace`, `unlinked`, `ref-002`

**Response (Çözüm 1):**
```json
{
  "referral_type": "marketplace",  // MAX() picks one (belirsiz)
  "link_status": "mixed",
  "referral_id": "ref-002"  // En yeni
}
```

**Response (Çözüm 2):**
```json
{
  "referral_count": 2,
  "referral_types": ["co-sell", "marketplace"],
  "referral_type": "co-sell",  // Primary (en yeni veya priority-based)
  "link_status": "mixed",
  "referral_id": "ref-002",  // Primary (backward compatibility)
  "referral_ids": ["ref-002", "ref-001"]  // Sorted by priority
}
```

### Senaryo 3: Multiple Referrals (Aynı Type)
**Domain**: `example.com`
- Referral 1: `co-sell`, `linked`, `ref-001`
- Referral 2: `co-sell`, `linked`, `ref-002`

**Response (Çözüm 2):**
```json
{
  "referral_count": 2,
  "referral_types": ["co-sell"],
  "referral_type": "co-sell",
  "link_status": "linked",
  "referral_id": "ref-002",  // En yeni
  "referral_ids": ["ref-002", "ref-001"]
}
```

---

## 🔧 Teknik Tasarım

### Backend Changes

#### 1. Response Model Güncellemesi

**File**: `app/api/leads.py`

```python
class LeadResponse(BaseModel):
    # ... existing fields ...
    
    # Solution 1 fields (backward compatible)
    referral_type: Optional[str] = None
    link_status: Optional[str] = None
    referral_id: Optional[str] = None
    
    # Solution 2 fields (new)
    referral_count: Optional[int] = None  # Total number of referrals
    referral_types: Optional[List[str]] = None  # Array of referral types (unique)
    referral_ids: Optional[List[str]] = None  # Array of referral IDs (sorted by priority)
    link_status_breakdown: Optional[Dict[str, int]] = None  # Optional: {"linked": 2, "unlinked": 1}
```

#### 2. SQL Query Güncellemesi

**File**: `app/api/leads.py` - `get_leads()`, `get_lead()`, `export_leads()`

**Mevcut Query:**
```sql
SELECT DISTINCT ON (lr.domain)
    ...
    MAX(pcr.referral_type) AS referral_type,
    CASE ... END AS aggregated_link_status,
    COALESCE((SELECT ... LIMIT 1), NULL) AS primary_referral_id
FROM leads_ready lr
LEFT JOIN partner_center_referrals pcr ON lr.domain = pcr.domain
GROUP BY ...
```

**Yeni Query (Çözüm 2):**
```sql
SELECT DISTINCT ON (lr.domain)
    ...
    -- Solution 1 (backward compatible)
    MAX(pcr.referral_type) AS referral_type,
    CASE ... END AS aggregated_link_status,
    COALESCE((SELECT ... LIMIT 1), NULL) AS primary_referral_id,
    
    -- Solution 2 (new aggregate fields)
    COUNT(pcr.id) AS referral_count,
    ARRAY_AGG(DISTINCT pcr.referral_type) FILTER (WHERE pcr.referral_type IS NOT NULL) AS referral_types,
    ARRAY_AGG(pcr.referral_id ORDER BY pcr.synced_at DESC, pcr.created_at DESC) 
        FILTER (WHERE pcr.referral_id IS NOT NULL) AS referral_ids,
    -- Optional: Link status breakdown
    jsonb_object_agg(
        COALESCE(CASE WHEN pcr.link_status = 'auto_linked' THEN 'linked' ELSE pcr.link_status END, 'unlinked'),
        COUNT(*)
    ) FILTER (WHERE pcr.id IS NOT NULL) AS link_status_breakdown
FROM leads_ready lr
LEFT JOIN partner_center_referrals pcr ON lr.domain = pcr.domain
GROUP BY ...
```

**Notlar:**
- `ARRAY_AGG(DISTINCT ...)` → Unique referral types
- `ARRAY_AGG(... ORDER BY ...)` → Sorted referral IDs (priority order)
- `jsonb_object_agg()` → Link status breakdown (opsiyonel)

#### 3. Response Mapping

**File**: `app/api/leads.py`

```python
LeadResponse(
    # ... existing fields ...
    referral_type=getattr(row, "referral_type", None),
    link_status=getattr(row, "aggregated_link_status", None) or "none",
    referral_id=getattr(row, "primary_referral_id", None),
    # Solution 2 fields
    referral_count=getattr(row, "referral_count", 0) or 0,
    referral_types=getattr(row, "referral_types", None) or [],
    referral_ids=getattr(row, "referral_ids", None) or [],
    link_status_breakdown=getattr(row, "link_status_breakdown", None),
)
```

---

### UI Changes

#### 1. Leads Table

**File**: `mini-ui/js/ui-leads.js`

**Mevcut Rendering:**
```javascript
${getReferralBadge(lead.referral_type)}
${lead.link_status ? ` ${getLinkStatusBadge(lead.link_status)}` : ''}
```

**Yeni Rendering (Çözüm 2):**
```javascript
${getReferralBadge(lead.referral_type)}
${lead.referral_count > 1 ? `<span class="referral-count-badge" title="${lead.referral_count} referral">(${lead.referral_count})</span>` : ''}
${lead.link_status ? ` ${getLinkStatusBadge(lead.link_status)}` : ''}
${lead.referral_types && lead.referral_types.length > 1 ? `<span class="referral-types-badge" title="Types: ${lead.referral_types.join(', ')}">${lead.referral_types.map(t => getReferralBadge(t)).join(' ')}</span>` : ''}
```

**Alternatif (Daha Temiz):**
- Referral kolonunda: Primary badge + count badge
- Hover tooltip: Tüm referral types ve IDs
- Breakdown modal: Detaylı liste

#### 2. Breakdown Modal

**File**: `mini-ui/js/ui-leads.js` - `showScoreBreakdown()`

**Yeni Section:**
```javascript
if (breakdown.referral_count > 0) {
    html += `<div class="score-breakdown__section">
        <div class="score-breakdown__section-title">Partner Center Referrals (${breakdown.referral_count})</div>`;
    
    if (breakdown.referral_types && breakdown.referral_types.length > 0) {
        html += `<div class="score-breakdown__item">
            <span class="score-breakdown__label">Referral Types</span>
            <span class="score-breakdown__value">${breakdown.referral_types.map(t => getReferralBadge(t)).join(' ')}</span>
        </div>`;
    }
    
    if (breakdown.link_status_breakdown) {
        html += `<div class="score-breakdown__item">
            <span class="score-breakdown__label">Link Status Breakdown</span>
            <span class="score-breakdown__value">
                ${Object.entries(breakdown.link_status_breakdown).map(([status, count]) => 
                    `${getLinkStatusBadge(status)} × ${count}`
                ).join(', ')}
            </span>
        </div>`;
    }
    
    if (breakdown.referral_ids && breakdown.referral_ids.length > 0) {
        html += `<div class="score-breakdown__item">
            <span class="score-breakdown__label">Referral IDs</span>
            <span class="score-breakdown__value" style="font-family: monospace; font-size: 0.85rem;">
                ${breakdown.referral_ids.map(id => escapeHtml(id)).join(', ')}
            </span>
        </div>`;
    }
    
    html += `</div>`;
}
```

---

## 📋 Implementation Checklist

### Backend
- [ ] Update `LeadResponse` model with Solution 2 fields
- [ ] Update SQL query in `get_leads()` to include aggregate fields
- [ ] Update SQL query in `get_lead()` to include aggregate fields
- [ ] Update SQL query in `export_leads()` to include aggregate fields
- [ ] Update `get_score_breakdown()` to include aggregate fields
- [ ] Handle NULL/empty arrays gracefully (default to empty array)
- [ ] Test with 0, 1, 2+ referrals scenarios

### UI
- [ ] Update Leads table rendering to show referral count badge
- [ ] Update Breakdown modal to show aggregate information
- [ ] Add CSS for new badges (referral-count-badge, referral-types-badge)
- [ ] Add tooltips for multiple referrals
- [ ] Test with multiple referrals scenarios

### Tests
- [ ] Unit tests for aggregate query logic
- [ ] Integration tests for multiple referrals scenarios
- [ ] UI tests for badge rendering

### Documentation
- [ ] Update CHANGELOG.md
- [ ] Update README.md API documentation
- [ ] Update SOLUTION-1-UI-CONSISTENCY-CHECK.md (mark Solution 2 as next step)

---

## ⚠️ Backward Compatibility

**Kritik**: Çözüm 1 alanları korunmalı:
- `referral_type`: Primary referral type (en yeni veya priority-based)
- `link_status`: Aggregate status (none/linked/unlinked/mixed)
- `referral_id`: Primary referral ID (en yeni)

**Neden?**
- Mevcut UI kodları bu alanları kullanıyor
- Export işlemleri bu alanları kullanıyor
- API contract'ı bozmamak için

**Çözüm 2 alanları ek olarak gelir:**
- `referral_count`: Yeni alan
- `referral_types`: Yeni alan (array)
- `referral_ids`: Yeni alan (array, opsiyonel)
- `link_status_breakdown`: Yeni alan (opsiyonel)

---

## 🎯 UI/UX Önerileri

### Leads Table

**Option 1: Minimal (Önerilen)**
- Primary badge + count badge: `[Co-sell] (2)`
- Hover tooltip: "2 referrals: Co-sell, Marketplace"

**Option 2: Expanded**
- Primary badge + all type badges: `[Co-sell] [Marketplace]`
- Count badge: `(2)`

**Option 3: Compact**
- Primary badge only (mevcut)
- Count badge: `(2)` (küçük, gri)
- Breakdown modal'da detay

### Breakdown Modal

**Section Title**: "Partner Center Referrals (2)"
- Referral Types: `[Co-sell] [Marketplace]`
- Link Status: `🔗 Linked (1), 🔓 Unlinked (1)`
- Referral IDs: `ref-002, ref-001` (sorted by priority)

---

## 📊 Efor Tahmini

- **Backend**: M (Medium - ~4-6 saat)
  - SQL query güncellemesi: 2 saat
  - Response model güncellemesi: 1 saat
  - Test yazma: 2-3 saat

- **UI**: S (Small - ~2-3 saat)
  - Badge rendering: 1 saat
  - Breakdown modal: 1 saat
  - CSS: 30 dakika

- **Test**: S (Small - ~2 saat)
  - Unit tests: 1 saat
  - Integration tests: 1 saat

**Toplam**: M (Medium - ~1 gün)

---

## 🔄 Migration Strategy

1. **Phase 1**: Backend only (add fields, keep backward compatible)
2. **Phase 2**: UI updates (gradual, optional features)
3. **Phase 3**: Export updates (add new columns)

**Risk**: Düşük (backward compatible, additive changes)

---

## ✅ Acceptance Criteria

- [ ] `referral_count` doğru hesaplanıyor (0, 1, 2+)
- [ ] `referral_types` array unique ve doğru sıralı
- [ ] `referral_ids` array priority order'da (en yeni önce)
- [ ] Backward compatibility korunuyor (referral_type, link_status, referral_id)
- [ ] UI'da count badge görünüyor (2+ referrals için)
- [ ] Breakdown modal'da aggregate bilgi görünüyor
- [ ] Export'ta yeni kolonlar var (opsiyonel)
- [ ] Tüm testler geçiyor

---

## 🔗 İlgili Dosyalar

- `app/api/leads.py` - Leads API endpoints
- `app/schemas/leads.py` - LeadResponse model (if exists, otherwise in leads.py)
- `mini-ui/js/ui-leads.js` - Leads table rendering
- `mini-ui/styles.css` - Badge styles
- `tests/test_leads_link_status.py` - Test suite (extend for Solution 2)

---

## 📝 Notlar

- **DISTINCT ON**: Korunacak (domain bazında duplicate prevention için gerekli)
- **Aggregate Logic**: PostgreSQL array functions kullanılacak
- **Performance**: Array aggregation minimal overhead (test edilmeli)
- **Export**: Yeni kolonlar opsiyonel (backward compatibility için)

---

**Son Güncelleme**: 2025-01-30  
**Durum**: 📋 Planlama aşaması - Implementation başlamadı

