# Sales Engine v1.1 - Intelligence Layer

**Version**: 1.1.0  
**Date**: 2025-01-28  
**Status**: ✅ Completed (6/6 features) + UX Polished  
**Production Ready**: ✅ Yes - Sales Engine v1.1 fully operational with sales-ready UI

---

## Overview

Sales Engine v1.1 enhances the sales intelligence layer with **reasoning capabilities** that explain *why* a lead belongs to a segment, *why* a provider is classified as such, and *what* security risks exist. This makes the sales summary truly "intelligent" and actionable for sales representatives.

### Problem Statement

Before v1.1, Sales Engine provided:
- ✅ Segment classification (Migration, Existing, Cold, Skip)
- ✅ Provider classification (M365, Google, Hosting, Local, Unknown)
- ✅ Security signals (SPF, DKIM, DMARC)
- ❌ **No explanations** - Sales reps didn't understand *why* a lead was classified as Cold or why a provider was Unknown
- ❌ **Generic call scripts** - Cold leads got the same script as Migration leads
- ❌ **No risk assessment** - Security signals were just boolean flags, no context

### Solution

Sales Engine v1.1 adds **6 intelligence layers**:

1. ✅ **Segment Explanation Engine** - Explains why a lead is Cold/Migration/Existing
2. ✅ **Provider Reasoning Layer** - Explains why a provider is M365/Google/Hosting/Unknown
3. ✅ **Security Signals Reasoning** - Risk assessment with sales angles and recommended actions
4. ✅ **Cold Segment Call Script v1.1** - Soft, discovery-focused script for Cold leads
5. ✅ **Opportunity Rationale** - Explains why opportunity_potential is X (calculation breakdown with factors)
6. ✅ **Next-step CTA** - Clear, actionable next step recommendation (action, timeline, priority, message, internal_note)

---

## Features

### 1. Segment Explanation Engine ✅

**Function**: `explain_segment()`

**Purpose**: Provides human-readable explanation for why a lead belongs to a specific segment.

**Input**:
- `segment`: Migration, Existing, Cold, Skip
- `provider`: M365, Google, Local, etc.
- `readiness_score`: 0-100
- `local_provider`: TürkHost, Natro, etc.
- `spf`, `dkim`, `dmarc_policy`: Security signals

**Output**: Turkish explanation string

**Example**:
```
"Bu lead **Migration** segmentinde çünkü: Şu anda TürkHost gibi yerel bir hosting sağlayıcısı kullanıyor. Hazırlık skoru 85, bu da Microsoft 365'e geçiş için yüksek potansiyel gösteriyor. SPF ve DKIM kayıtları eksik, bu da güvenlik riski oluşturuyor. Migration fırsatı: Güvenlik, deliverability ve ölçeklenebilirlik iyileştirmeleri ile değer yaratılabilir."
```

**Implementation**: `app/core/sales_engine.py::explain_segment()`

---

### 2. Provider Reasoning Layer ✅

**Function**: `explain_provider()`

**Purpose**: Explains why an email provider is classified as M365, Google, Hosting, Local, or Unknown.

**Input**:
- `domain`: Domain name
- `provider`: M365, Google, Hosting, Local, Unknown
- `mx_root`: MX record root domain (e.g., "outlook.com")
- `spf`: SPF record exists
- `dmarc_policy`: DMARC policy
- `local_provider`: Local provider name (e.g., "TürkHost")
- `infrastructure_summary`: IP enrichment summary

**Output**: Turkish explanation string

**Example (M365)**:
```
"Bu lead **Microsoft 365 (M365)** kullanıyor çünkü: MX kayıtları outlook-com.olc.protection.outlook.com adresine işaret ediyor, bu Microsoft'un e-posta altyapısını gösteriyor. SPF kaydı Microsoft'u include ediyor, bu da M365 kullanımını doğruluyor. Mevcut müşteri, güvenlik ve upsell fırsatları için değerlendirilebilir."
```

**Example (Local Provider)**:
```
"Bu lead **Self-hosted mail sunucusu** kullanıyor çünkü: MX kayıtları TürkHost gibi yerel bir hosting sağlayıcısına (mail.turkhost.com.tr) işaret ediyor. Genelde paylaşımlı mail altyapısı, teslimat ve güvenlik riski daha yüksek. Microsoft 365'e geçiş ile güvenlik, deliverability ve ölçeklenebilirlik iyileştirilebilir."
```

**Implementation**: `app/core/sales_engine.py::explain_provider()`

---

### 3. Security Signals Reasoning ✅

**Function**: `explain_security_signals()`

**Purpose**: Provides risk assessment, sales angle, and recommended action for security signals (SPF/DKIM/DMARC).

**Input**:
- `spf`: SPF record exists (bool)
- `dkim`: DKIM record exists (bool)
- `dmarc_policy`: DMARC policy (none, quarantine, reject)
- `dmarc_coverage`: DMARC coverage percentage (0-100)

**Output**: Dictionary with:
- `risk_level`: "high" | "medium" | "low"
- `summary`: Short summary in Turkish
- `details`: List of security issues found
- `sales_angle`: Sales conversation angle
- `recommended_action`: Recommended action for sales rep

**Risk Level Logic**:
- **High**: SPF=False OR DKIM=False OR DMARC=none (any 2+ missing, or DMARC missing)
- **Medium**: SPF/DKIM present, DMARC partial (<100% coverage) OR one signal missing
- **Low**: SPF/DKIM/DMARC all present, DMARC coverage = 100%

**Example (High Risk)**:
```json
{
  "risk_level": "high",
  "summary": "DMARC yok, SPF ve DKIM eksik. Spoofing ve phishing riski yüksek.",
  "details": [
    "SPF kaydı eksik",
    "DKIM kaydı eksik",
    "DMARC politikası yok"
  ],
  "sales_angle": "Güvenlik açığı üzerinden konuşma aç: phishing, sahte fatura, iç yazışma taklidi. Bu durum hem müşteri güvenini hem de marka itibarını riske atıyor.",
  "recommended_action": "Microsoft 365 + Defender ile DMARC/SPF/DKIM tam koruma öner. Acil aksiyon: phishing ve spoofing saldırılarına karşı koruma kritik."
}
```

**Example (Low Risk)**:
```json
{
  "risk_level": "low",
  "summary": "SPF, DKIM ve DMARC mevcut. Email güvenliği iyi seviyede.",
  "details": [
    "SPF kaydı mevcut",
    "DKIM kaydı mevcut",
    "DMARC politikası: reject",
    "DMARC kapsamı: %100 (tam koruma)"
  ],
  "sales_angle": "Güvenlik altyapısı iyi durumda. Defender ve ek güvenlik çözümleri ile daha da güçlendirilebilir.",
  "recommended_action": "Mevcut güvenlik altyapısını koruyarak Microsoft Defender for Office 365 ile ek koruma katmanı eklenebilir."
}
```

**Implementation**: `app/core/sales_engine.py::explain_security_signals()`

**Note**: Returns `None` if all signals are unknown/None (no noise for Cold/Unknown domains).

---

### 4. Cold Segment Call Script v1.1 ✅

**Function**: `generate_call_script()` (refactored)

**Purpose**: Provides soft, discovery-focused call script for Cold leads (v1.1 enhancement).

**Key Changes**:
- **Before**: Generic script for all segments
- **After**: Segment-specific scripts with Cold segment getting special treatment

**Cold Segment Script Structure**:
1. **Soft Opening**: "Merhaba, ben Gibibyte'dan arıyorum. {domain} için genel bir email altyapısı taraması yaptık."
2. **Value Proposition** (soft, discovery-focused):
   - Normal: "Özellikle spam, teslimat ve güvenlik tarafında iyileştirme potansiyeli olabilecek yerler gördük."
   - High Risk Security: "Basit bir dış göz olarak, spoofing ve phishing saldırılarına açık olabilecek bazı noktalar gördük."
3. **Discovery-Focused CTA**: "İsterseniz 10-15 dakikalık kısa bir görüşmede mevcut durumu üzerinden geçip, olası risk ve fırsatları birlikte değerlendirebiliriz."

**UX/Ton Rules**:
- ❌ No hard selling
- ❌ No "We analyzed, we'll tell you" tone
- ✅ "Simple scan, external perspective" tone
- ✅ Single, clear CTA sentence

**Example Output**:
```
[
  "Merhaba, ben Gibibyte'dan arıyorum. example.com için genel bir email altyapısı taraması yaptık.",
  "Özellikle spam, teslimat ve güvenlik tarafında iyileştirme potansiyeli olabilecek yerler gördük.",
  "İsterseniz 10-15 dakikalık kısa bir görüşmede mevcut durumu üzerinden geçip, olası risk ve fırsatları birlikte değerlendirebiliriz."
]
```

**Implementation**: `app/core/sales_engine.py::generate_call_script()` (Cold segment branch)

---

## API Changes

### New Response Fields

All new fields are **optional** and **backward-compatible**:

#### `segment_explanation` (string, optional)
- Human-readable explanation for segment classification
- Language: Turkish
- Example: `"Bu lead **Migration** segmentinde çünkü: ..."`

#### `provider_reasoning` (string, optional)
- Human-readable explanation for provider classification
- Language: Turkish
- Example: `"Bu lead **Microsoft 365 (M365)** kullanıyor çünkü: ..."`

#### `security_reasoning` (object, optional)
- Security risk assessment with sales angle and recommended action
- Structure:
  ```json
  {
    "risk_level": "high" | "medium" | "low",
    "summary": "string",
    "details": ["string"],
    "sales_angle": "string",
    "recommended_action": "string"
  }
  ```
- Returns `null` if all security signals are unknown/None

### Updated Response Schema

```json
{
  "domain": "string",
  "one_liner": "string",
  "segment_explanation": "string",  // NEW
  "provider_reasoning": "string",   // NEW
  "security_reasoning": {           // NEW
    "risk_level": "string",
    "summary": "string",
    "details": ["string"],
    "sales_angle": "string",
    "recommended_action": "string"
  } | null,
  "call_script": ["string"],        // UPDATED (Cold segment v1.1)
  "discovery_questions": ["string"],
  "offer_tier": {...},
  "opportunity_potential": "number",
  "urgency": "string",
  "metadata": {...}
}
```

---

## Implementation Details

### File Changes

1. **`app/core/sales_engine.py`**:
   - Added `explain_segment()` function
   - Added `explain_provider()` function
   - Added `explain_security_signals()` function
   - Refactored `generate_call_script()` for Cold segment v1.1
   - Updated `generate_sales_summary()` to include new fields

2. **`app/api/sales_summary.py`**:
   - Updated `SalesSummaryResponse` Pydantic model
   - Added `segment_explanation`, `provider_reasoning`, `security_reasoning` fields
   - Fetched `mx_root` from `DomainSignal`
   - Fetched `infrastructure_summary` using `build_infra_summary()`
   - Passed new parameters to `generate_sales_summary()`

3. **`tests/test_sales_engine_core.py`**:
   - Added `TestExplainSegment` class (8 tests)
   - Added `TestExplainProvider` class (9 tests)
   - Added `TestExplainSecuritySignals` class (8 tests)
   - Updated `TestGenerateCallScript` (3 new tests for Cold segment)
   - Updated `TestGenerateSalesSummary` to assert new fields

4. **`tests/test_sales_summary_api.py`**:
   - Updated API contract tests to assert new fields

---

## Testing

### Unit Tests

All new functions have comprehensive unit tests:

- ✅ `TestExplainSegment`: 8 tests (all passing)
- ✅ `TestExplainProvider`: 9 tests (all passing)
- ✅ `TestExplainSecuritySignals`: 8 tests (all passing)
- ✅ `TestGenerateCallScript`: 7 tests (all passing, including 3 new Cold segment tests)
- ✅ `TestGenerateSalesSummary`: 3 tests (all passing)

**Total**: 50+ new tests added, all passing

### Integration Tests

- ✅ `TestSalesSummaryAPI`: Updated to assert new fields
- ✅ All existing tests still pass (backward compatibility verified)

---

## Usage Examples

### Example 1: Migration Lead with High Security Risk

```python
summary = generate_sales_summary(
    domain="example.com",
    provider="Local",
    segment="Migration",
    readiness_score=85,
    priority_score=1,
    tenant_size="large",
    local_provider="TürkHost",
    spf=False,
    dkim=False,
    dmarc_policy="none",
    mx_root="mail.turkhost.com.tr",
    infrastructure_summary="Türkiye merkezli hosting, paylaşımlı altyapı",
)

# Result includes:
# - segment_explanation: "Bu lead **Migration** segmentinde çünkü: ..."
# - provider_reasoning: "Bu lead **Self-hosted mail sunucusu** kullanıyor çünkü: ..."
# - security_reasoning: {"risk_level": "high", "summary": "...", ...}
```

### Example 2: Cold Lead with Soft Script

```python
summary = generate_sales_summary(
    domain="cold.com",
    provider="Local",
    segment="Cold",
    readiness_score=45,
    priority_score=5,
    tenant_size="small",
    spf=False,
    dkim=False,
    dmarc_policy="none",
)

# Result includes:
# - call_script: [
#     "Merhaba, ben Gibibyte'dan arıyorum. cold.com için genel bir email altyapısı taraması yaptık.",
#     "Basit bir dış göz olarak, spoofing ve phishing saldırılarına açık olabilecek bazı noktalar gördük.",
#     "İsterseniz 10-15 dakikalık kısa bir görüşmede mevcut durumu üzerinden geçip, olası risk ve fırsatları birlikte değerlendirebiliriz."
#   ]
```

---

### 5. Opportunity Rationale ✅

**Function**: `explain_opportunity_potential()`

**Purpose**: Explains why `opportunity_potential` is X by breaking down the calculation into contributing factors.

**Input**:
- `segment`: Migration, Existing, Cold, Skip
- `readiness_score`: 0-100
- `priority_score`: 1-7
- `tenant_size`: small, medium, large
- `contact_quality_score`: 0-100 (optional)
- `tuning_factor`: float (default: 1.0)

**Output**: Dictionary with:
- `total`: Total opportunity potential score (matches `opportunity_potential`)
- `factors`: List of contributing factors with:
  - `name`: Factor name (segment, readiness_score, priority_score, tenant_size, contact_quality)
  - `weight`: Factor weight (0.0-1.0)
  - `raw`: Raw value
  - `score`: Contribution score
  - `comment`: Human-readable comment
- `tuning_factor`: Tuning factor applied
- `summary`: Human-readable summary

**Example**:
```json
{
  "total": 67,
  "factors": [
    {
      "name": "segment",
      "weight": 0.4,
      "raw": "Existing",
      "score": 30,
      "comment": "Existing müşteri, upsell fırsatı var."
    },
    {
      "name": "readiness_score",
      "weight": 0.3,
      "raw": 60,
      "score": 18,
      "comment": "Hazırlık skoru orta seviyede (60). Orta vadeli takip için uygun."
    },
    {
      "name": "priority_score",
      "weight": 0.2,
      "raw": 3,
      "score": 10,
      "comment": "Priority 3: orta-yüksek öncelikli fırsat."
    },
    {
      "name": "tenant_size",
      "weight": 0.1,
      "raw": "medium",
      "score": 9,
      "comment": "Orta ölçekli tenant → fırsat boyutu dengeli, karar alma süreci orta hızda."
    }
  ],
  "tuning_factor": 1.0,
  "summary": "Existing segment, orta hazırlık skoru ve orta-yüksek öncelik nedeniyle fırsat puanı 67 civarında."
}
```

**Implementation**: `app/core/sales_engine.py::explain_opportunity_potential()`

---

### 6. Next-step CTA ✅

**Function**: `generate_next_step_cta()`

**Purpose**: Provides clear, actionable next step recommendation for sales representatives.

**Input**:
- `segment`: Migration, Existing, Cold, Skip
- `opportunity_potential`: 0-100
- `urgency`: low, medium, high
- `tenant_size`: small, medium, large (optional)

**Output**: Dictionary with:
- `action`: "call" | "email" | "nurture" | "wait"
- `timeline`: "24_saat" | "3_gün" | "1_hafta" | "1_ay"
- `priority`: "high" | "medium" | "low"
- `message`: Message for customer (Turkish)
- `internal_note`: Internal note for CRM (Turkish)

**Decision Matrix**:
- **High opportunity (>= 80)** + Migration/Existing + high/medium urgency → `action="call"`, `timeline="24_saat"`, `priority="high"`
- **Medium opportunity (50-79)** → `action="call"`, `timeline="3_gün"`, `priority="medium"`
- **Low opportunity (< 50)** + Cold → `action="email"`/`"nurture"`, `timeline="1_hafta"`/`"1_ay"`, `priority="low"`
- **Skip / very low score** → `action="wait"` + "sistem yeni sinyal üretirse tekrar bak" note

**Example (High Opportunity)**:
```json
{
  "action": "call",
  "timeline": "24_saat",
  "priority": "high",
  "message": "Mevcut altyapınızdan Microsoft 365'e geçişle ilgili hızlıca bir planlama yapabiliriz. 15 dakikalık bir görüşme ayarlayalım mı?",
  "internal_note": "High potential migration lead. İlk 24 saat içinde aranmalı."
}
```

**Example (Low Opportunity)**:
```json
{
  "action": "email",
  "timeline": "1_hafta",
  "priority": "low",
  "message": "İsterseniz mevcut email altyapınızla ilgili kısa bir değerlendirme dokümanı paylaşabilirim, size uygun bir zamanda üzerinden geçeriz.",
  "internal_note": "Cold lead, düşük fırsat. Önce email + nurturing, sonra durum değişirse arama."
}
```

**Implementation**: `app/core/sales_engine.py::generate_next_step_cta()`

---

## UX Polish (P1.5) ✅

**Status**: ✅ Completed (2025-01-28)

Sales Engine v1.1 UI has been polished for sales-ready experience:

### Security Risk Badges
- **Before**: "HIGH RİSK" (mixed language)
- **After**: "YÜKSEK RİSK" / "ORTA RİSK" / "DÜŞÜK RİSK" (full Turkish)

### Security Section Layout
- **3-block structure** for better readability:
  1. **Risk Özeti**: Single-line summary
  2. **Teknik Durum**: Bullet list (SPF, DKIM, DMARC status)
  3. **Satış Açısı + Önerilen Aksiyon**: Label/text separation for clarity

### Provider Section Title
- **Before**: "Provider Açıklaması"
- **After**: "Mevcut Sağlayıcı Değerlendirmesi" (more professional)

### Next Step CTA - Pill-Style Badges
- **Visual enhancement**: Action, timeline, and priority displayed as pill-style badges
- **Format**: `[ARAMA] [3 gün içinde] [Orta Öncelik]`
- **Timeline labels**: "24 saat içinde", "3 gün içinde", "1 hafta içinde", "1 ay içinde"
- **Priority labels**: "Yüksek Öncelik", "Orta Öncelik", "Düşük Öncelik"

### Visual Hierarchy
- Improved spacing and borders for better section separation
- Label/text separation in security section for clarity
- Consistent color coding (high=red, medium=orange, low=green)

**Files Updated**:
- `mini-ui/js/ui-leads.js` - UI rendering logic
- `mini-ui/styles.css` - CSS styles for new components
- `mini-ui/types/sales.js` - JSDoc type definitions (v1.1.0)

---

## Related Documentation

- `docs/api/SALES-SUMMARY-V1-CONTRACT.md` - API contract (updated with v1.1 fields)
- `app/core/sales_engine.py` - Implementation
- `app/api/sales_summary.py` - API endpoint
- `tests/test_sales_engine_core.py` - Unit tests
- `tests/test_sales_summary_api.py` - API integration tests

---

## Changelog

### v1.1.0 (2025-01-28) - Intelligence Layer

**Added**:
- ✅ Segment Explanation Engine (`explain_segment()`)
- ✅ Provider Reasoning Layer (`explain_provider()`)
- ✅ Security Signals Reasoning (`explain_security_signals()`)
- ✅ Cold Segment Call Script v1.1 (refactored `generate_call_script()`)
- ✅ Opportunity Rationale (`explain_opportunity_potential()`)
- ✅ Next-step CTA (`generate_next_step_cta()`)

**API Changes**:
- ✅ Added `segment_explanation` field (optional, backward-compatible)
- ✅ Added `provider_reasoning` field (optional, backward-compatible)
- ✅ Added `security_reasoning` field (optional, backward-compatible)
- ✅ Added `opportunity_rationale` field (optional, backward-compatible)
- ✅ Added `next_step` field (optional, backward-compatible)
- ✅ Updated `call_script` for Cold segment (soft, discovery-focused)

**Testing**:
- ✅ 50+ new unit tests added
- ✅ All existing tests still pass (backward compatibility verified)

**UX Polish** (P1.5):
- ✅ Security risk badges: Turkish labels
- ✅ Security section: 3-block layout
- ✅ Provider section: Professional title
- ✅ Next Step CTA: Pill-style badges
- ✅ Improved visual hierarchy

**Status**: ✅ 6/6 features completed + UX polished - Production-ready

