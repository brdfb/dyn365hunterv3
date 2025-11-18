# Production UAT Guide - CSP P-Model + Sales Summary v1.1

**Date**: 2025-01-29  
**Status**: ✅ **DONE & PROD-READY** - Ready for Production UAT

---

## 🚀 Quick Start

### 1. Setup Production Environment

```bash
# Run setup script
bash scripts/production_uat_setup.sh
```

This script will:
- ✅ Check Docker and services
- ✅ Verify database and Redis connections
- ✅ Check API health
- ✅ Verify database migrations (CSP P-Model migration)
- ✅ Verify feature flags (core features - no flags needed)
- ✅ Create screenshot directory

---

### 2. Run UAT Tests

```bash
# Run automated UAT tests for golden domains
bash scripts/production_uat_test.sh
```

This script will test:
- ✅ `gibibyte.com.tr` (P4 - Existing M365)
- ✅ `dmkimya.com.tr` (P2 - Google Workspace Migration)
- ⏳ P1 Local/Hosting Migration (find domain)
- ⏳ P3 Weak Partner M365 (find domain)

---

### 3. Check Logs

```bash
# Verify logging for P-Model and Sales Summary
bash scripts/production_uat_log_check.sh
```

This script will check:
- ✅ `score_domain` events with P-Model fields
- ✅ `sales_summary_viewed` events with structured fields
- ✅ PII leakage check (domain-only logging)
- ✅ Log level verification (INFO)

---

## 📋 Manual UAT Checklist

### Domain 1: gibibyte.com.tr (P4 - Existing M365)

**Expected P-Model Fields**:
- `priority_category`: P4
- `commercial_segment`: RENEWAL
- `technical_heat`: Warm
- `commercial_heat`: MEDIUM
- `priority_label`: "Yenileme Baskısı - Mevcut M365 Müşterisi"

**Steps**:
1. Ingest: `curl -X POST http://localhost:8000/api/v1/ingest/domain -H "Content-Type: application/json" -d '{"domain": "gibibyte.com.tr"}'`
2. Scan: `curl -X POST http://localhost:8000/api/v1/scan/domain -H "Content-Type: application/json" -d '{"domain": "gibibyte.com.tr"}'`
3. Verify Lead: `curl http://localhost:8000/api/v1/leads/gibibyte.com.tr | jq '.priority_category, .commercial_segment, .technical_heat'`
4. Verify Score Breakdown: `curl http://localhost:8000/api/v1/leads/gibibyte.com.tr/score-breakdown | jq '.priority_category, .commercial_segment'`
5. Verify Sales Summary: `curl http://localhost:8000/api/v1/leads/gibibyte.com.tr/sales-summary | jq '.segment_explanation, .provider_reasoning, .security_reasoning'`
6. **UI Screenshots**:
   - Open: `http://localhost:8000/mini-ui/`
   - Find `gibibyte.com.tr` in lead list
   - Verify P4 badge (orange) is visible
   - Click score → Verify CSP P-Model panel in score breakdown modal
   - Click "📞 Sales" button → Verify all Sales Summary sections

---

### Domain 2: dmkimya.com.tr (P2 - Google Workspace Migration)

**Expected P-Model Fields**:
- `priority_category`: P2
- `commercial_segment`: COMPETITIVE
- `technical_heat`: Hot
- `commercial_heat`: HIGH
- `priority_label`: "Rekabetçi Devralma - Google Workspace'ten M365'ye Geçiş"

**Steps**:
1. Ingest: `curl -X POST http://localhost:8000/api/v1/ingest/domain -H "Content-Type: application/json" -d '{"domain": "dmkimya.com.tr"}'`
2. Scan: `curl -X POST http://localhost:8000/api/v1/scan/domain -H "Content-Type: application/json" -d '{"domain": "dmkimya.com.tr"}'`
3. Verify Lead: `curl http://localhost:8000/api/v1/leads/dmkimya.com.tr | jq '.priority_category, .commercial_segment, .technical_heat'`
4. **Critical Check**: Verify DMARC coverage is `null` (not 100%) if no DMARC record exists
5. **Critical Check**: Verify Sales Summary risk text correctly states "SPF ve DKIM mevcut" (not "eksik")
6. **UI Screenshots**:
   - Verify P2 badge (red) in lead list
   - Verify provider-specific description in score breakdown modal ("Google Workspace kullanımı...")
   - Verify Sales Summary risk text is correct

---

### Domain 3: P1 Local/Hosting Migration

**Expected P-Model Fields**:
- `priority_category`: P1
- `commercial_segment`: GREENFIELD
- `technical_heat`: Hot
- `commercial_heat`: HIGH
- `priority_label`: "Yüksek Potansiyel Greenfield - Yeni Müşteri Fırsatı"

**Steps**:
1. Find a domain with Local/Hosting provider and Migration segment
2. Ingest and scan the domain
3. Verify P-Model fields match expectations
4. **UI Screenshots**:
   - Verify P1 badge (green) in lead list
   - Verify CSP P-Model panel

---

### Domain 4: P3 Weak Partner M365

**Expected P-Model Fields**:
- `priority_category`: P3
- `commercial_segment`: WEAK_PARTNER
- `technical_heat`: Warm
- `commercial_heat`: MEDIUM
- `priority_label`: "Zayıf Partner M365 - Mevcut Müşteri, Zayıf İlişki"

**Steps**:
1. Find a domain with M365 provider, Existing segment, low score (<70)
2. Ingest and scan the domain
3. Verify P-Model fields match expectations
4. **UI Screenshots**:
   - Verify P3 badge (blue) in lead list
   - Verify CSP P-Model panel

---

## 📸 Screenshot Requirements

**Save screenshots to**: `docs/archive/2025-01-29-PRODUCTION-UAT-SCREENSHOTS/`

**Required Screenshots**:
1. **Lead List** - P-badges visible for all 4 domains
2. **Score Breakdown Modal** - CSP P-Model panel visible
3. **Sales Summary Modal** - All sections visible (segment explanation, provider reasoning, security reasoning, opportunity rationale, next step)
4. **Provider-Specific Description** - Score breakdown modal header (M365, Google, Local/Hosting)

---

## 📊 Log Verification

### Expected Log Events

**score_domain event** (INFO level):
```json
{
  "event": "score_domain",
  "domain": "example.com",
  "priority_category": "P2",
  "commercial_segment": "COMPETITIVE",
  "technical_heat": "Hot",
  "commercial_heat": "HIGH",
  "priority_label": "Rekabetçi Devralma...",
  "level": "INFO",
  "timestamp": "2025-01-29T..."
}
```

**sales_summary_viewed event** (INFO level):
```json
{
  "event": "sales_summary_viewed",
  "domain": "example.com",
  "segment": "Migration",
  "offer_tier": "Enterprise",
  "opportunity_potential": 89,
  "urgency": "high",
  "level": "INFO",
  "timestamp": "2025-01-29T..."
}
```

### Verify Logs

```bash
# Check score_domain events
docker-compose logs api | grep -i "score_domain" | tail -10

# Check sales_summary_viewed events
docker-compose logs api | grep -i "sales_summary_viewed" | tail -10

# Check for PII leakage (should be empty)
docker-compose logs api | grep -iE "email|company_name|@.*\."

# Check structured logging format
docker-compose logs api | jq '.' | head -20
```

---

## ✅ Completion Criteria

**Production UAT Complete When**:
- ✅ All 4 golden domains tested
- ✅ All P-Model fields verified (priority_category, commercial_segment, technical_heat, commercial_heat, priority_label)
- ✅ All Sales Summary v1.1 fields verified (segment_explanation, provider_reasoning, security_reasoning, opportunity_rationale, next_step)
- ✅ All screenshots taken and saved
- ✅ Logs verified (score_domain, sales_summary_viewed events)
- ✅ No PII leakage in logs
- ✅ No errors or warnings in production logs

---

## 🐛 Troubleshooting

### Issue: P-Model fields are null

**Check**:
1. Database migration applied: `docker-compose exec api python -m app.db.run_migration current`
2. Should show: `f786f93501ea` (CSP P-Model migration)
3. If not, run: `docker-compose exec api python -m app.db.run_migration upgrade head`

### Issue: DMARC coverage shows 100% when no DMARC record exists

**Check**:
1. Verify `app/core/analyzer_dns.py` fix is applied
2. Clear cache: `docker-compose exec api python scripts/invalidate_scoring_cache.py --domain example.com`
3. Rescan domain: `curl -X POST http://localhost:8000/api/v1/scan/domain -d '{"domain": "example.com"}'`

### Issue: Sales Summary risk text is incorrect

**Check**:
1. Verify `app/core/sales_engine.py` fix is applied
2. Check Sales Summary response: `curl http://localhost:8000/api/v1/leads/example.com/sales-summary | jq '.security_reasoning.risk_summary'`

---

## 📖 Related Documentation

- **Production Readiness Checklist**: `docs/archive/2025-01-29-PRODUCTION-READINESS-CHECKLIST-2025-01-29.md`
- **CSP P-Model Implementation**: `docs/archive/2025-01-29-CSP-P-MODEL-IMPLEMENTATION-PLAN.md`
- **Sales Engine v1.1**: `docs/active/SALES-ENGINE-V1.1.md`

---

**Status**: ⏳ **Ready for Production UAT**  
**Next Step**: Run `bash scripts/production_uat_setup.sh` to prepare environment

