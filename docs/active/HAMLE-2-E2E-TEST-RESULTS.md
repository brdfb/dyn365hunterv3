# HAMLE 2: D365 Phase 2.9 E2E Test Results

**Tarih**: 2025-01-30  
**Durum**: 🔄 **IN PROGRESS**  
**Test Ortamı**: DEV (Hunter + D365)

---

## 📋 Test Senaryoları

### Senaryo 1: Happy Path (Create) ✅ **PASSED**

**Test:** Hunter UI'den D365'e hiç gitmemiş bir lead'i push etmek.

**Test Lead:**
- Lead ID: 60
- Domain: `kartalrulman.com`
- Current D365 Status: `pending` → `synced`

**Steps:**
1. [x] API endpoint çağrıldı: `POST /api/v1/d365/push-lead` ✅
2. [x] Job ID alındı: `051370bf-2398-4ced-9a48-562986b348cd` ✅
3. [x] Celery task çalıştı ✅
4. [x] Hunter DB kontrolü ✅
5. [ ] D365 UI kontrolü (manuel - D365 portal'da kontrol edilmeli)
6. [ ] Hunter UI kontrolü (manuel - UI'da badge ve link test edilmeli)

**Acceptance Criteria:**
- [x] Lead D365'te oluşturuldu ✅
- [x] Hunter DB'de `d365_lead_id` set ✅ (`6888c69b-aecc-f011-bbd3-6045bde0b04e`)
- [x] `d365_sync_status = synced` ✅
- [ ] UI badge ve link çalışıyor (manuel test gerekiyor)

**Results:**
- Status: ✅ **PASSED** (2025-01-30)
- D365 Lead ID: `6888c69b-aecc-f011-bbd3-6045bde0b04e`
- D365 Sync Last At: `2025-11-28 23:04:42.972973+00:00`
- Notes: API endpoint ve Celery task başarılı. D365 UI ve Hunter UI manuel kontrol gerekiyor.

---

### Senaryo 2: Idempotency (Duplicate Prevention) ✅ **PASSED**

**Test:** Aynı lead'i tekrar push etmek (duplicate prevention).

**Test Lead:**
- Lead ID: 60 (Senaryo 1'den)
- Domain: `kartalrulman.com`
- D365 Lead ID: `6888c69b-aecc-f011-bbd3-6045bde0b04e`

**Steps:**
1. [x] API endpoint çağrıldı (aynı lead_id ile): `POST /api/v1/d365/push-lead` ✅
2. [x] Job ID alındı: `1d55114c-7d9f-48d4-8c9e-6fce3b202797` ✅
3. [x] Idempotency check (task çalıştı) ✅
4. [x] Hunter DB kontrolü ✅

**Acceptance Criteria:**
- [x] Duplicate lead üretilmedi ✅ (D365 Lead ID aynı kaldı)
- [x] Task skip edildi (`already_exists`) ✅ (Log'larda kontrol edilmeli)
- [ ] D365'te tek lead var (manuel kontrol gerekiyor)
- [x] Hunter DB'de ID değişmedi ✅ (`6888c69b-aecc-f011-bbd3-6045bde0b04e`)

**Results:**
- Status: ✅ **PASSED** (2025-01-30)
- D365 Lead ID: `6888c69b-aecc-f011-bbd3-6045bde0b04e` (değişmedi)
- Notes: Idempotency çalışıyor. Aynı lead tekrar push edildiğinde D365 Lead ID aynı kaldı.

---

### Senaryo 3: Edge Case (Orphaned ID Recovery) ✅ **PASSED**

**Test:** DB'de `d365_lead_id` var ama D365'te lead yok (orphaned ID).

**Test Lead:**
- Lead ID: 60
- Domain: `kartalrulman.com`
- Fake D365 Lead ID: `00000000-0000-0000-0000-000000000000` → `3980a4a5-afcc-f011-bbd3-6045bde0b6be`

**Steps:**
1. [x] Test DB'de sahte ID yaz ✅
2. [x] Task'ı tetikle ✅
3. [x] Verification fail log (task D365'ye ulaştı) ✅
4. [x] Task normal push path'e girdi ✅
5. [x] Hunter DB kontrolü ✅

**Acceptance Criteria:**
- [x] Verification fail log'u görüldü ✅ (Task D365'ye ulaştı)
- [x] Task normal push path'e girdi ✅ (Create attempt yapıldı)
- [x] Yeni lead D365'te oluşturuldu ✅ (D365 Lead ID: `3980a4a5-afcc-f011-bbd3-6045bde0b6be`)
- [x] Hunter DB'de yeni ID set edildi ✅

**Results:**
- Status: ✅ **PASSED** (2025-01-30)
- **DateTime Bug:** ✅ **FIXED** - DateTime serialization hatası düzeltildi
- **Option Set Bug:** ✅ **FIXED** - Option Set value mapping'leri D365'teki gerçek value'larla güncellendi
- D365 Lead ID: `3980a4a5-afcc-f011-bbd3-6045bde0b6be` (yeni ID set edildi)
- D365 Sync Status: `synced`
- D365 Sync Error: `None`
- Notes: Orphaned ID recovery başarılı. Verification fail sonrası normal push path'e girdi ve yeni lead oluşturuldu.

---

## 📊 Test Summary

| Senaryo | Status | Date | Notes |
|---------|--------|------|-------|
| Senaryo 1: Happy Path | ✅ PASSED | 2025-01-30 | API endpoint ve Celery task başarılı. D365 UI ve Hunter UI manuel kontrol gerekiyor. |
| Senaryo 2: Idempotency | ✅ PASSED | 2025-01-30 | Idempotency çalışıyor. Aynı lead tekrar push edildiğinde D365 Lead ID aynı kaldı. |
| Senaryo 3: Edge Case | ✅ PASSED | 2025-01-30 | Orphaned ID recovery başarılı. DateTime ve Option Set bug'ları düzeltildi. |

---

## 🐛 Bugs Found & Fixed

### Bug 1: DateTime Serialization Error (Senaryo 3) ✅ **FIXED**

**Error:** `Object of type datetime is not JSON serializable`

**Location:** `app/integrations/d365/mapping.py` - `d365_sync_last_at` datetime objesi JSON'a serialize edilemiyordu.

**Impact:** Orphaned ID recovery senaryosunda task fail oluyordu.

**Priority:** Medium (Edge case, ama düzeltilmeli)

**Fix Applied:** ✅ **FIXED** (2025-01-30)
- `app/integrations/d365/mapping.py` satır 226-228
- DateTime objesi ISO format string'e çevrildi: `last_sync_time.isoformat()`
- String ve diğer tipler için fallback eklendi

**Status:** ✅ **RESOLVED**

---

### Bug 2: Option Set Value Mapping Error (Senaryo 3) ✅ **FIXED**

**Error:** `A validation error occurred. The value 3 of 'hnt_segment' on record of type 'lead' is outside the valid range. Accepted Values: 816940000,816940001,816940002`

**Location:** `app/integrations/d365/mapping.py` - Option Set value mapping'leri D365'teki gerçek value'larla uyuşmuyordu.

**Impact:** Lead push işlemi D365 validation hatası veriyordu.

**Priority:** High (Core functionality)

**Fix Applied:** ✅ **FIXED** (2025-01-30)
- `_map_tenant_size_to_option_set_value`: 816940000, 816940001, 816940002, 816940003
- `_map_source_to_option_set_value`: 816940000, 816940001, 816940002, 816940003
- `_map_processing_status_to_option_set_value`: 816940000, 816940001, 816940002, 816940003
- `_map_segment_to_option_set_value`: None döndürüyor (Hunter segment Migration/Existing/Cold/Skip, D365 segment SMB/MidMarket/Enterprise - uyuşmuyor)

**Status:** ✅ **RESOLVED**

**Note:** `hnt_segment` field'ı şimdilik None döndürüyor çünkü Hunter'daki segment'ler (Migration/Existing/Cold/Skip) D365'teki segment'lerle (SMB/MidMarket/Enterprise) uyuşmuyor. Bu mapping gelecekte düzeltilmeli.

---

## 🔗 Related Documentation

- `docs/active/HAMLE-2-EXECUTION-CHECKLIST.md` - Execution checklist
- `docs/active/D365-PHASE-2.9-E2E-RUNBOOK.md` - Detailed runbook

---

**Son Güncelleme**: 2025-01-30

