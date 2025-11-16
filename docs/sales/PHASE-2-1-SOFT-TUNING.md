# Phase 2.1 - Sales Engine Soft Tuning

**Date**: 2025-01-28  
**Status**: Optional (Future Enhancement)  
**Purpose**: Fine-tuning opportunity potential scores based on sales feedback

---

## Overview

Real-world smoke test results showed that opportunity scores are slightly higher than expected but within acceptable range (±15 points). This document outlines the soft tuning mechanism for future adjustments.

---

## Tuning Factor Configuration

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
   - Migration: Expected 60-80, actual?
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

---

## Decision Log

**2025-01-28**: Tuning factor mechanism added but set to default (1.0). No immediate adjustment needed based on smoke test results. Will monitor sales feedback and adjust if needed.

