# Golden Dataset v1.0 Blueprint

**Date**: 2025-01-28  
**Status**: 📋 **Blueprint** (Implementation pending)  
**Purpose**: Ground truth dataset for scoring engine validation

---

## 🎯 Executive Summary

**Current State**: Silver regression set exists (`test_regression_dataset.py`)  
**Target State**: True golden dataset with real-world data + human validation  
**Timeline**: 2-4 weeks (passive data collection + human validation)

---

## 📋 Requirements

### 1. Real-World Data (200-500 domains)

**Source**: Production domains scanned by Hunter  
**Format**: JSON snapshots with complete DNS lookup results

**Required Fields**:
```json
{
  "domain": "firma.com",
  "timestamp": "2025-01-29T11:30:45Z",
  "mx_records": [
    {
      "host": "mail.protection.outlook.com",
      "priority": 10,
      "resolved_ips": ["40.107.0.0", "40.107.1.0"]
    }
  ],
  "spf": {
    "record": "v=spf1 include:spf.protection.outlook.com -all",
    "valid": true,
    "mechanisms": ["include", "all"]
  },
  "dkim": {
    "valid": true,
    "selector": "selector1",
    "public_key": "base64..."
  },
  "dmarc": {
    "record": "v=DMARC1; p=reject; pct=100",
    "policy": "reject",
    "pct": 100
  },
  "provider": {
    "detected": "M365",
    "confidence": "high",
    "mx_pattern_match": true
  },
  "tenant_size": {
    "estimated": "medium",
    "mx_count": 2,
    "pattern": "standard"
  },
  "ip_enrichment": {
    "country": "TR",
    "city": "Istanbul",
    "isp": "Turk Telekom",
    "is_proxy": false,
    "is_hosting": false,
    "is_datacenter": false
  },
  "scoring": {
    "readiness_score": 72,
    "segment": "Migration",
    "priority_score": 1,
    "breakdown": {
      "base_score": 0,
      "provider_points": 50,
      "signal_points": 22,
      "risk_points": 0
    }
  }
}
```

### 2. Human Validation (100% reviewed)

**Reviewers**:
- Sales team member (1 person)
- Technical reviewer (developer)
- Optional: Additional domain expert

**Validation Format**:
| Domain | Score | Segment | Priority | Correct? | Notes |
|--------|-------|---------|----------|----------|-------|
| firma.com | 72 | Migration | 1 | ✅ Yes | Perfect match |
| example.com | 45 | Cold | 5 | ❌ No | Should be Existing (M365) |
| test.com | 0 | Skip | 7 | ✅ Yes | No MX, correct |

**Validation Criteria**:
- Score matches business logic
- Segment matches provider + score combination
- Priority matches segment + score combination
- Edge cases documented with explanations

### 3. Versioned Storage

**Structure**:
```
tests/golden_dataset/
├── v1.0/
│   ├── golden_v1.0.json          # Validated dataset
│   ├── validation_log.md         # Human validation notes
│   └── metadata.json              # Version info, date, reviewers
├── v1.1/
│   ├── golden_v1.1.json          # Updated after rule changes
│   ├── validation_log.md
│   └── metadata.json
└── raw_samples/                   # Unvalidated production samples
    ├── 2025-01-29/
    │   ├── sample_001.json
    │   ├── sample_002.json
    │   └── ...
    └── 2025-01-30/
        └── ...
```

**Versioning Rules**:
- `v1.0`: Initial validated dataset (200-500 domains)
- `v1.1`: Updated after rule changes (if rules change, dataset stays same, rules must match)
- `v1.2`: New edge cases added (production discoveries)

### 4. Rule Independence

**Key Principle**:
> **Dataset = Ground Truth**  
> **Rules = Must Match Dataset**

**Workflow**:
1. Dataset is validated by humans (ground truth)
2. Rules are tested against dataset
3. If rule change breaks dataset → **Rule is wrong, not dataset**
4. Rules must be updated to match dataset

**Example**:
```python
# Golden dataset says: M365 + SPF only = Score 45
# Rule says: M365 + SPF only = Score 50
# Result: Rule is wrong, must be fixed to match dataset
```

---

## 🔄 Data Collection Pipeline

### Phase 1: Passive Collection (Week 1-2)

**Implementation**:
- Add logging hook to scoring pipeline
- Save JSON snapshots to `golden_raw_samples/YYYY-MM-DD/`
- Collect 500-1000 raw samples (will filter to 200-500)

**Code Location**: `app/core/scorer.py` (add snapshot export)

**Format**: See JSON schema above

**Storage**: `tests/golden_dataset/raw_samples/`

### Phase 2: Sample Selection (Week 2)

**Criteria**:
- Diverse provider distribution (M365, Google, Yandex, Hosting, Local, etc.)
- Diverse score ranges (0-100)
- Diverse segments (Migration, Existing, Cold, Skip)
- Edge cases (DMARC none, DKIM broken, multi-MX, etc.)
- Turkish local providers (Turhost, IHS, Aerotek, etc.)

**Selection**: Manual review of raw samples, pick 200-500 best examples

### Phase 3: Human Validation (Week 3)

**Process**:
1. Export selected samples to validation spreadsheet
2. Sales team + technical reviewer validate each domain
3. Document disagreements (if any)
4. Finalize validated dataset

**Output**: `golden_v1.0.json` with validation metadata

### Phase 4: Test Integration (Week 4)

**Implementation**:
- Create `tests/test_golden_dataset.py`
- Load `golden_v1.0.json`
- Test rules against golden dataset
- If test fails → rule is wrong, not dataset

**Test Structure**:
```python
def test_golden_dataset_v1_0():
    """Test that rules match golden dataset v1.0 (ground truth)."""
    golden = load_golden_dataset("v1.0")
    for sample in golden:
        result = score_domain(...)
        assert result["score"] == sample["scoring"]["readiness_score"]
        assert result["segment"] == sample["scoring"]["segment"]
        # If this fails, RULE is wrong, not dataset
```

---

## 📊 JSON Schema

### Golden Dataset Entry

```json
{
  "domain": "string (required)",
  "timestamp": "ISO 8601 (required)",
  "mx_records": [
    {
      "host": "string (required)",
      "priority": "integer (required)",
      "resolved_ips": ["string array (optional)"]
    }
  ],
  "spf": {
    "record": "string (optional)",
    "valid": "boolean (required)",
    "mechanisms": ["string array (optional)"]
  },
  "dkim": {
    "valid": "boolean (required)",
    "selector": "string (optional)",
    "public_key": "string (optional)"
  },
  "dmarc": {
    "record": "string (optional)",
    "policy": "string | null (required)",
    "pct": "integer | null (optional)"
  },
  "provider": {
    "detected": "string (required)",
    "confidence": "string (required)",
    "mx_pattern_match": "boolean (required)"
  },
  "tenant_size": {
    "estimated": "string | null (required)",
    "mx_count": "integer (optional)",
    "pattern": "string (optional)"
  },
  "ip_enrichment": {
    "country": "string | null (optional)",
    "city": "string | null (optional)",
    "isp": "string | null (optional)",
    "is_proxy": "boolean | null (optional)",
    "is_hosting": "boolean | null (optional)",
    "is_datacenter": "boolean | null (optional)"
  },
  "scoring": {
    "readiness_score": "integer (required)",
    "segment": "string (required)",
    "priority_score": "integer (required)",
    "breakdown": {
      "base_score": "integer (required)",
      "provider_points": "integer (required)",
      "signal_points": "integer (required)",
      "risk_points": "integer (required)"
    }
  },
  "validation": {
    "reviewed_by": "string (required)",
    "reviewed_at": "ISO 8601 (required)",
    "correct": "boolean (required)",
    "notes": "string (optional)"
  }
}
```

### Metadata File

```json
{
  "version": "1.0",
  "created_at": "2025-01-29T00:00:00Z",
  "domain_count": 250,
  "reviewers": [
    {
      "name": "Sales Team Member",
      "role": "sales",
      "reviewed_count": 250
    },
    {
      "name": "Technical Reviewer",
      "role": "developer",
      "reviewed_count": 250
    }
  ],
  "coverage": {
    "providers": {
      "M365": 50,
      "Google": 45,
      "Yandex": 20,
      "Hosting": 30,
      "Local": 25,
      "Unknown": 10,
      "Other": 70
    },
    "segments": {
      "Migration": 80,
      "Existing": 60,
      "Cold": 70,
      "Skip": 40
    },
    "score_ranges": {
      "0-20": 30,
      "21-40": 40,
      "41-60": 50,
      "61-80": 70,
      "81-100": 60
    }
  }
}
```

---

## 🚀 Implementation Steps

### Step 1: Data Collection Hook (1 day)

**File**: `app/core/scorer.py`

Add snapshot export function:
```python
def export_golden_sample(domain: str, result: dict, db: Session):
    """Export scoring result as golden sample JSON."""
    # Save to tests/golden_dataset/raw_samples/YYYY-MM-DD/
    pass
```

### Step 2: Sample Collection (1-2 weeks)

- Enable snapshot export in production
- Collect 500-1000 raw samples
- Store in `tests/golden_dataset/raw_samples/`

### Step 3: Sample Selection (2-3 days)

- Review raw samples
- Select 200-500 diverse examples
- Export to validation format

### Step 4: Human Validation (1 week)

- Sales team + technical reviewer validate
- Document disagreements
- Finalize `golden_v1.0.json`

### Step 5: Test Integration (1 day)

- Create `tests/test_golden_dataset.py`
- Load `golden_v1.0.json`
- Test rules against golden dataset
- If test fails → rule is wrong

---

## ✅ Success Criteria

1. ✅ 200-500 real domains with complete DNS data
2. ✅ 100% human-validated (sales team + technical reviewer)
3. ✅ Versioned storage (`v1.0`, `v1.1`, etc.)
4. ✅ Rule-independent (dataset = ground truth)
5. ✅ Test integration (rules must match dataset)
6. ✅ Comprehensive coverage (all providers, segments, score ranges)

---

## 📝 Notes

- **Current regression set**: Keep as-is, renamed to `test_regression_dataset.py`
- **Golden dataset**: Separate effort, 2-4 weeks
- **Rule changes**: After golden dataset exists, rule changes must pass golden tests
- **CRM integration**: Only after golden dataset validates scoring accuracy

---

**Status**: 📋 Blueprint ready, implementation pending

