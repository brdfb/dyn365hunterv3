# Phase 2.1 - Sales Engine Soft Tuning

**Date**: 2025-01-28  
**Status**: ✅ **Completed** (2025-01-28)  
**Purpose**: Fine-tuning opportunity potential scores based on sales feedback

---

## Overview

Real-world smoke test results showed that opportunity scores are slightly higher than expected but within acceptable range (±15 points). This document outlines the soft tuning mechanism for future adjustments.

**Update (2025-01-28)**: Segment threshold tuning completed based on sales team feedback.

---

## Segment Threshold Tuning (2025-01-28) ✅

### Changes Applied

#### 1. Migration Threshold: 70 → 60

**Before:**
- Migration segment required score >= 70
- Many good leads (Local provider + SPF = 20 points) couldn't reach Migration segment

**After:**
- Migration segment now requires score >= 60
- More leads qualify for Migration segment
- Local provider + SPF + DKIM = 30 points → Still needs more signals, but threshold is more achievable

**Impact:**
- More leads in Migration segment
- Better lead quality (still requires 60+ score)
- Local provider leads with good signals can now reach Migration

**Example (Note: Risk points not included in these examples):**
- Local provider (10) + SPF (10) + DKIM (10) + DMARC quarantine (15) = 45 points → Still Cold
- Local provider (10) + SPF (10) + DKIM (10) + DMARC reject (20) = 50 points → Still Cold
- Local provider (10) + SPF (10) + DKIM (10) + DMARC reject (20) + Additional signals = 60+ points → Migration ✅

**Important Note:** Actual score calculation includes risk points (negative):
- Missing SPF: -10 points
- Missing DKIM: -10 points
- DMARC policy = "none": -10 points
- These risk points can significantly reduce the final score.

#### 2. Local Provider Cold Threshold: 10 → 5

**Before:**
- Local provider leads with score 5-9 were in Skip segment
- Active businesses with self-hosted mail servers were being skipped

**After:**
- Local provider leads with score 5-59 are now in Cold segment
- Active businesses with self-hosted mail servers are now visible in Cold segment

**Impact:**
- More actionable leads (self-hosted mail servers are good migration candidates)
- Better lead visibility (active businesses no longer skipped)
- Sales team can now see and prioritize self-hosted mail server leads

**Example:**
- `dardagangida.com.tr`: Score 5, Local provider → Now in Cold segment (was Skip)
- Active business with self-hosted mail server → Migration potential visible

**Edge Cases:**
- Local provider + score 0-4 → Still Skip segment (too low score, general Skip rule applies)
- Local provider + score 60+ → Migration segment (Migration rule matches first, before Local Cold rule)
- Local provider + score 5-59 → Cold segment (Local-specific Cold rule)

#### 3. General Cold Segment: 40-69 → 40-59

**Before:**
- General Cold segment was 40-69
- Overlapped with Migration segment (60-69)

**After:**
- General Cold segment is now 40-59
- No overlap with Migration segment (60+)
- Clearer segment boundaries

**Impact:**
- Clearer segment boundaries
- No confusion between Cold and Migration
- Better lead prioritization

**Important: Segment Evaluation Order**
Segment rules are evaluated **in order (top to bottom)**, and the **first matching rule wins**. This means:
- Migration rule (60+, Local) is checked before Local Cold rule (5-59, Local)
- Local provider + score 60+ → Migration segment (not Cold)
- Local provider + score 5-59 → Cold segment (Local-specific rule)
- Local provider + score 0-4 → Skip segment (general Skip rule, max_score: 39)

---

## Opportunity Potential Formülü (Gerçek Hesaplama)

**Backend**: `app/core/sales_engine.py:320-397`

**Tam Formül**:
```python
score = 0

# Segment weight (40 points)
if segment == "Migration": score += 40
elif segment == "Existing": score += 30
elif segment == "Cold": score += 15
else: score += 5  # Skip

# Readiness score weight (30 points)
score += int(readiness_score * 0.3)  # Max 30

# Priority score weight (20 points) - inverse (lower priority_score = higher opportunity)
if priority_score == 1: score += 20
elif priority_score == 2: score += 18
elif priority_score == 3: score += 15
elif priority_score == 4: score += 12
elif priority_score == 5: score += 8
elif priority_score == 6: score += 5
else: score += 2  # 7

# Tenant size weight (10 points)
if tenant_size == "large": score += 10
elif tenant_size == "medium": score += 7
elif tenant_size == "small": score += 5
else: score += 3  # Unknown

# Contact quality bonus (optional, up to 5 points)
score += int(contact_quality_score * 0.05)  # Max 5

# Apply tuning factor
score = int(score * tuning_factor)  # Default: 1.0

# Cap at 100
return min(score, 100)
```

**Örnek Hesaplama**:
- Migration (40) + Readiness 85 (25.5) + Priority 1 (20) + Large (10) + Contact Quality 80 (4) = 99.5 → 99 (tuning_factor=1.0)
- Existing (30) + Readiness 60 (18) + Priority 4 (12) + Medium (7) = 67 (tuning_factor=1.0)

**Not**: Tuning factor **sadece backend'de kullanılıyor**, UI'da gösterilmiyor. Admin UI yok (gelecekte eklenecek).

---

## Tuning Factor Configuration

**⚠️ DURUM: Tasarım - Henüz production kodda yok**

Tuning Factor şu an teorik bir kavramdır. Backend'de environment variable desteği var (`HUNTER_SALES_ENGINE_OPPORTUNITY_FACTOR`) ancak:
- ❌ UI'da gösterilmiyor
- ❌ Admin UI yok (gelecekte eklenecek)
- ✅ Backend'de environment variable ile ayarlanabilir (default: 1.0)

**Gerçek kullanım:** Şu an production'da tuning factor değiştirilmiyor, default 1.0 kullanılıyor.

### Environment Variable

```env
HUNTER_SALES_ENGINE_OPPORTUNITY_FACTOR=0.9
```

**Default**: `1.0` (no adjustment)  
**Range**: `0.0` to `2.0`  
**Recommended**: `0.9` to `1.1` (10% adjustment max)

### Usage

The tuning factor is applied to the final opportunity potential score:

```python
# app/core/sales_engine.py
score = int(score * tuning_factor)  # Applied before capping at 100
```

**UI Durumu**: 
- ❌ **UI'da gösterilmiyor**: Tuning factor sadece backend'de kullanılıyor
- ❌ **Admin UI yok**: Tuning factor'ü değiştirmek için admin UI yok (gelecekte eklenecek)
- ✅ **Backend'de çalışıyor**: Environment variable ile ayarlanabilir

### Examples

- `1.0`: No change (default)
- `0.9`: 10% reduction (if scores consistently too high)
- `0.95`: 5% reduction (fine-tuning)
- `1.1`: 10% increase (if scores consistently too low)
- `1.05`: 5% increase (fine-tuning)

---

## When to Adjust

### Reduce Factor (0.9-0.95)

**Signs**:
- Sales team feedback: "Scores are consistently too high"
- Many leads with 80+ scores but low conversion
- Opportunity scores don't match actual sales outcomes

**Action**: Reduce factor by 0.05-0.1

### Increase Factor (1.05-1.1)

**Signs**:
- Sales team feedback: "Scores are too conservative"
- High-quality leads getting low scores
- Opportunity scores consistently below expectations

**Action**: Increase factor by 0.05-0.1

### Keep Default (1.0)

**Signs**:
- Sales team satisfied with current scores
- Scores align with actual sales outcomes
- No consistent feedback about score accuracy

**Action**: No change needed

---

## Monitoring

### Log Analysis

Sales summary views are logged with opportunity potential:

```json
{
  "event": "sales_summary_viewed",
  "domain": "example.com",
  "segment": "Migration",
  "offer_tier": "Enterprise",
  "opportunity_potential": 89,
  "urgency": "high",
  "user_id": 123,
  "timestamp": "2025-01-28T12:00:00Z"
}
```

### Metrics to Track

1. **Average opportunity potential by segment**:
   - Migration: Expected 60-100 (threshold 60+), actual?
   - Existing: Expected 50-70, actual?
   - Cold: Expected 20-40, actual?

2. **Score distribution**:
   - How many leads in each range (0-29, 30-49, 50-69, 70-100)?
   - Does distribution match sales expectations?

3. **Conversion correlation**:
   - Do higher opportunity scores correlate with better conversion?
   - Are there outliers (high score, low conversion or vice versa)?

---

## Implementation

### Current Status

✅ Tuning factor added to `app/config.py`  
✅ Tuning factor applied in `calculate_opportunity_potential()`  
✅ Default value: `1.0` (no adjustment)  
✅ **Segment threshold tuning completed (2025-01-28)**

### Future Enhancements

1. **Admin UI**: Allow sales managers to adjust factor via UI
2. **A/B Testing**: Test different factors on sample leads
3. **Auto-tuning**: Machine learning-based adjustment based on conversion data
4. **Segment-specific factors**: Different factors for Migration vs Existing vs Cold

---

## Related Documents

- `docs/active/SALES-ENGINE-REAL-WORLD-SMOKE-1.md` - Real-world test results
- `docs/api/SALES-SUMMARY-V1-CONTRACT.md` - API contract
- `app/core/sales_engine.py` - Implementation
- `app/data/rules.json` - Segment rules configuration

---

## Decision Log

**2025-01-28**: Tuning factor mechanism added but set to default (1.0). No immediate adjustment needed based on smoke test results. Will monitor sales feedback and adjust if needed.

**2025-01-28 (Update)**: Segment threshold tuning completed:
- Migration threshold: 70 → 60
- Local provider Cold threshold: 10 → 5
- General Cold segment: 40-69 → 40-59

**Rationale**: Sales team feedback indicated that many good leads (especially self-hosted mail server users) were being skipped or not prioritized. Lowering thresholds makes more leads actionable while maintaining quality standards.

**Priority Score Impact:**
- Migration + score 80+ → Priority 1 (unchanged)
- Migration + score 70-79 → Priority 2 (unchanged)
- Migration + score 60-69 → Priority 3 (threshold updated: 50 → 60, matches segment min_score = 60)
- Migration + score 50-59 → **Artık mümkün değil** (Migration segment min_score = 60, bu skorlar Cold segment'ine düşer)

**Detaylı matris için:** [SEGMENT-GUIDE.md](SEGMENT-GUIDE.md) - Kanonik Segment-Priority Matrisi bölümüne bakın.
- Local provider + score 5-39 → Cold segment → Priority 6-7 (depending on score)
- Local provider + score 40-59 → Cold segment → Priority 5-6 (depending on score)
- Local provider + score 60+ → Migration segment → Priority 3-4 (depending on score)

**Segment Evaluation Order:**
1. Existing (M365 provider) - checked first
2. Migration (60+, Google/Yandex/Zoho/Hosting/Local) - checked second
3. Cold (Local, 5-59) - checked third (Local-specific)
4. Cold (40-59, general) - checked fourth
5. Skip (max_score: 39) - checked last (catch-all)

**Quick Reference Table:**

**⚠️ Detaylı kanonik matris için:** [SEGMENT-GUIDE.md](SEGMENT-GUIDE.md) - Kanonik Segment-Priority Matrisi bölümüne bakın.

| Provider | Score Range | Segment | Priority | Notes |
|----------|-------------|---------|----------|-------|
| M365 | Any | Existing | 3-6 | Always Existing, never Migration |
| Local | 0-4 | Skip | 7 | Too low, general Skip rule |
| Local | 5-39 | Cold | 6-7 | Local-specific Cold rule |
| Local | 40-59 | Cold | 5-6 | Local-specific Cold rule |
| Local | 60+ | Migration | 3-4 | Migration rule matches first |
| Google/Yandex/Zoho/Hosting | 60+ | Migration | 1-4 | Migration segment (min_score = 60) |
| Google/Yandex/Zoho/Hosting | 40-59 | Cold | 5-6 | General Cold rule |
| Google/Yandex/Zoho/Hosting | 0-39 | Skip | 7 | General Skip rule |
