# Active Docs Cleanup Plan (2025-01-29)

**Durum:** ⚠️ **21 dosya var, maksimum 5-7 olmalı!**

---

## 📊 Mevcut Durum

**Toplam:** 21 dosya  
**Hedef:** 5-7 dosya  
**Fazla:** 14-16 dosya

---

## 🗂️ Kategorizasyon

### ✅ Archive Edilecekler (7 dosya) - Tamamlanmış İşler

1. **BROWSER-UI-CHECK-RESULTS-2025-01-29.md**
   - Durum: ✅ TÜM KONTROLLER GEÇTİ
   - Action: Archive → `docs/archive/2025-01-29-BROWSER-UI-CHECK-RESULTS.md`

2. **FINAL-PRODUCTION-CHECK-2025-01-29.md**
   - Durum: ✅ PRODUCTION READY
   - Action: Archive → `docs/archive/2025-01-29-FINAL-PRODUCTION-CHECK.md`

3. **MANUAL-UI-CHECKLIST-2025-01-29.md**
   - Durum: ✅ Production Ready
   - Action: Archive → `docs/archive/2025-01-29-MANUAL-UI-CHECKLIST.md`

4. **PRODUCTION-READINESS-SUMMARY-2025-01-29.md**
   - Durum: ✅ Production Ready
   - Action: Archive → `docs/archive/2025-01-29-PRODUCTION-READINESS-SUMMARY.md`

5. **PRODUCTION-PREFLIGHT-CHECK-2025-01-29.md**
   - Durum: ✅ ALL CHECKS PASSED
   - Action: Archive → `docs/archive/2025-01-29-PRODUCTION-PREFLIGHT-CHECK.md`

6. **DOCUMENTATION-UPDATE-2025-01-29.md**
   - Durum: ✅ Güncellendi
   - Action: Archive → `docs/archive/2025-01-29-DOCUMENTATION-UPDATE.md`

7. **CSP-COMMERCIAL-SEGMENT-DESIGN.md**
   - Durum: CSP P-Model tamamlandı (2025-01-29)
   - Action: Archive → `docs/archive/2025-01-29-CSP-COMMERCIAL-SEGMENT-DESIGN.md`

---

### 📚 Reference'a Taşınacaklar (7 dosya) - Reference Guides

8. **ENVIRONMENT-VARIABLES-CHECKLIST.md**
   - Type: Reference guide
   - Action: Move → `docs/reference/ENVIRONMENT-VARIABLES-CHECKLIST.md`

9. **PRODUCTION-CHECKLIST-RUNBOOK.md**
   - Type: Reference guide
   - Action: Move → `docs/reference/PRODUCTION-CHECKLIST-RUNBOOK.md`

10. **PRODUCTION-DEPLOYMENT-GUIDE.md**
    - Type: Reference guide
    - Action: Move → `docs/reference/PRODUCTION-DEPLOYMENT-GUIDE.md`

11. **PRODUCTION-ENGINEERING-GUIDE-V1.md**
    - Type: Reference guide
    - Action: Move → `docs/reference/PRODUCTION-ENGINEERING-GUIDE-V1.md`

12. **ROLLBACK-PLAN.md**
    - Type: Reference guide
    - Action: Move → `docs/reference/ROLLBACK-PLAN.md`

13. **SMOKE-TESTS-RUNBOOK.md**
    - Type: Reference guide
    - Action: Move → `docs/reference/SMOKE-TESTS-RUNBOOK.md`

14. **PRODUCTION-DEPLOYMENT-CHECKLIST.md**
    - Type: Reference guide
    - Action: Move → `docs/reference/PRODUCTION-DEPLOYMENT-CHECKLIST.md`

---

### ✅ Aktif Kalacaklar (7 dosya) - Current Work

15. **G21-ROADMAP-CURRENT.md**
    - Durum: G21 devam ediyor
    - Reason: Aktif phase roadmap

16. **NO-BREAK-REFACTOR-PLAN.md**
    - Durum: G21 devam ediyor
    - Reason: Aktif refactor planı

17. **HUNTER-STATE-v1.0.md**
    - Durum: Aktif state doc
    - Reason: Current state tracking

18. **POST-MVP-STRATEGY.md**
    - Durum: Aktif strategy
    - Reason: Post-MVP planning

19. **PRODUCTION-MONITORING-WATCH.md**
    - Durum: Aktif monitoring
    - Reason: Production monitoring

20. **KALAN-ISLER-PRIORITY.md**
    - Durum: Aktif priority doc
    - Reason: Priority tracking

21. **SALES-ENGINE-V1.1.md**
    - Durum: Aktif feature doc
    - Reason: Sales engine aktif kullanımda

---

## 📋 Action Plan

### Step 1: Archive Completed Work (7 files)
```bash
# Archive completed checks and CSP P-Model design
mv docs/active/BROWSER-UI-CHECK-RESULTS-2025-01-29.md docs/archive/2025-01-29-BROWSER-UI-CHECK-RESULTS.md
mv docs/active/FINAL-PRODUCTION-CHECK-2025-01-29.md docs/archive/2025-01-29-FINAL-PRODUCTION-CHECK.md
mv docs/active/MANUAL-UI-CHECKLIST-2025-01-29.md docs/archive/2025-01-29-MANUAL-UI-CHECKLIST.md
mv docs/active/PRODUCTION-READINESS-SUMMARY-2025-01-29.md docs/archive/2025-01-29-PRODUCTION-READINESS-SUMMARY.md
mv docs/active/PRODUCTION-PREFLIGHT-CHECK-2025-01-29.md docs/archive/2025-01-29-PRODUCTION-PREFLIGHT-CHECK.md
mv docs/active/DOCUMENTATION-UPDATE-2025-01-29.md docs/archive/2025-01-29-DOCUMENTATION-UPDATE.md
mv docs/active/CSP-COMMERCIAL-SEGMENT-DESIGN.md docs/archive/2025-01-29-CSP-COMMERCIAL-SEGMENT-DESIGN.md
```

### Step 2: Move Reference Guides (7 files)
```bash
# Move reference guides to docs/reference/
mv docs/active/ENVIRONMENT-VARIABLES-CHECKLIST.md docs/reference/
mv docs/active/PRODUCTION-CHECKLIST-RUNBOOK.md docs/reference/
mv docs/active/PRODUCTION-DEPLOYMENT-GUIDE.md docs/reference/
mv docs/active/PRODUCTION-ENGINEERING-GUIDE-V1.md docs/reference/
mv docs/active/ROLLBACK-PLAN.md docs/reference/
mv docs/active/SMOKE-TESTS-RUNBOOK.md docs/reference/
mv docs/active/PRODUCTION-DEPLOYMENT-CHECKLIST.md docs/reference/
```

### Step 3: Verify Active Count
**Hedef:** 7 dosya (maksimum 5-7 aralığında)

**Kalan Aktif Dosyalar:**
1. G21-ROADMAP-CURRENT.md
2. NO-BREAK-REFACTOR-PLAN.md
3. HUNTER-STATE-v1.0.md
4. POST-MVP-STRATEGY.md
5. PRODUCTION-MONITORING-WATCH.md
6. KALAN-ISLER-PRIORITY.md
7. SALES-ENGINE-V1.1.md

---

## ✅ Sonuç

**Önce:** 21 dosya  
**Sonra:** 7 dosya  
**Archive:** 7 dosya  
**Reference:** 7 dosya

**Status:** ✅ **Hedef aralığında (5-7 dosya)**

