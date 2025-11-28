# D365 Lead Fields v1.0 - Kritik Analiz

**Tarih**: 2025-01-30  
**Durum**: ✅ Kritik tamamlandı, öneriler hazır

---

## 🎯 Özet

**18 alanlık D365 Lead custom field seti** için kritik analiz ve öneriler.

**Sonuç**: Plan %95 doğru, 3 kritik düzeltme + 2 öneri var.

---

## ✅ Güçlü Yönler

1. **Sıralama Doğru**: Önce kolonlar %100, sonra form design ✅
2. **18 Alan Mantıklı**: Core Intelligence (7) + Partner Center (6) + Sync/Ops (5) ✅
3. **Publisher Prefix**: `<prefix>_` kullanımı doğru ✅
4. **Post-MVP Ayrımı**: Advanced fields ayrı tutulmuş ✅

---

## 🔴 Kritik Sorunlar (3 Adet)

### 1. **Priority Score Eksik** ⚠️ **KRİTİK**

**Sorun**: 
- Backend'de `priority_score` (1-7) hesaplanıyor ve API'de döndürülüyor ✅
- Ama `mapping.py`'de D365'e gönderilmiyor ❌

**Mevcut Durum**:
```python
# app/integrations/d365/mapping.py (satır 49-60)
hunter_fields = {
    "hunter_score": lead_data.get("readiness_score"),  # ✅ Var
    "hunter_priority_category": lead_data.get("priority_category"),  # ✅ Var
    # ❌ "hunter_priority_score": lead_data.get("priority_score"),  # EKSİK!
}
```

**Çözüm**:
- `mapping.py`'ye `hunter_priority_score` ekle
- `d365_push.py`'de `priority_score` hesapla ve `lead_data`'ya ekle

**D365 Field**:
- **Display Name**: Hunter Priority Score
- **Schema Name**: `<prefix>_HunterPriorityScore`
- **Tip**: WN (Whole Number, 1-7)

---

### 2. **Is Partner Center Referral Bool Eksik** ⚠️ **KRİTİK**

**Sorun**:
- `referral_id` var ama `is_partner_center_referral` bool field yok
- D365 form'da "Bu lead Partner Center'dan mı?" sorusu için bool gerekli

**Mevcut Durum**:
```python
# app/integrations/d365/mapping.py (satır 62-65)
referral_id = lead_data.get("referral_id")
if referral_id:
    hunter_fields["hunter_referral_id"] = referral_id  # ✅ Var
# ❌ hunter_fields["hunter_is_partner_center_referral"] = bool(referral_id)  # EKSİK!
```

**Çözüm**:
- `mapping.py`'ye `hunter_is_partner_center_referral` ekle
- Logic: `bool(referral_id)` veya `partner_center_referrals` tablosundan kontrol

**D365 Field**:
- **Display Name**: Hunter Is Partner Center Referral
- **Schema Name**: `<prefix>_HunterIsPartnerCenterReferral`
- **Tip**: 2O (Two Options / Boolean)

---

### 3. **Sync Attempt Count Backend'de Yok** ⚠️ **KRİTİK**

**Sorun**:
- D365'te `hunter_sync_attempt_count` field'ı olacak
- Ama backend'de bu sayacı tutan bir mekanizma yok

**Mevcut Durum**:
- `companies.d365_sync_status` var ✅
- `companies.d365_sync_error` var ✅
- `companies.d365_sync_last_at` var ✅
- ❌ `companies.d365_sync_attempt_count` YOK

**Çözüm**:
- Migration: `companies` tablosuna `d365_sync_attempt_count` (Integer, default=0) ekle
- `d365_push.py`'de her push attempt'te `attempt_count += 1` yap
- Mapping'de D365'e gönder

**D365 Field**:
- **Display Name**: Hunter Sync Attempt Count
- **Schema Name**: `<prefix>_HunterSyncAttemptCount`
- **Tip**: WN (Whole Number, default=0)

---

## 🟡 Orta Öncelik Sorunlar (2 Adet)

### 4. **M365 Fit Score & Match Tags Henüz Yok** 🟡

**Durum**:
- Backend'de M365 Fit Score hesaplama yok
- Backend'de M365 Match Tags sistemi yok
- Partner Center'da `azure_tenant_id` var ama M365 fit hesaplama yok

**Öneri**:
- **Şimdilik**: D365'te field'ları aç, backend'de `None` gönder
- **Post-MVP**: M365 fit hesaplama algoritması ekle
- **Alternatif**: `provider == "M365"` ise `m365_fit_score = readiness_score` (basit mapping)

**D365 Fields**:
- `hunter_m365_fit_score` → Şimdilik `None` veya `readiness_score` (M365 ise)
- `hunter_m365_match_tags` → Şimdilik `None` veya `[]`

---

### 5. **Source Field Logic Eksik** 🟡

**Sorun**:
- D365'te `hunter_source` (enum: Partner Center, Manual, Import, Other) olacak
- Backend'de lead'in nereden geldiğini tutan bir field yok

**Mevcut Durum**:
- `partner_center_referrals` tablosunda `referral_id` var
- Ama `companies` tablosunda "bu lead nereden geldi?" bilgisi yok

**Öneri**:
- **Basit Çözüm**: `referral_id` varsa → `source = "Partner Center"`
- **Genel Çözüm**: `companies.source` field'ı ekle (migration gerekir)
- **Şimdilik**: `referral_id` kontrolü ile `source` belirle

**D365 Field**:
- **Display Name**: Hunter Source
- **Schema Name**: `<prefix>_HunterSource`
- **Tip**: CH (Choice: Partner Center, Manual, Import, Other)

---

## ✅ Backend'de Mevcut Olanlar (11/18)

### Core Intelligence (7/7) ✅
1. ✅ `readiness_score` → `hunter_score`
2. ✅ `priority_score` → **EKSİK** (mapping'de yok, hesaplanıyor ama gönderilmiyor)
3. ✅ `segment` → `hunter_segment`
4. ✅ `provider` → `hunter_provider`
5. ✅ `tenant_size` → `hunter_tenant_size`
6. ✅ `infrastructure_summary` → `hunter_infrastructure`
7. ❌ `is_partner_center_referral` → **EKSİK** (bool, `referral_id` kontrolü ile hesaplanabilir)

### Partner Center Enriched (4/6) ✅
8. ❌ `tenant_id` → **EKSİK** (`partner_center_referrals.azure_tenant_id` var ama mapping'de yok)
9. ✅ `referral_id` → `hunter_referral_id`
10. ✅ `referral_type` → **EKSİK** (`partner_center_referrals.referral_type` var ama mapping'de yok)
11. ❌ `source` → **EKSİK** (logic gerekli)
12. ❌ `m365_fit_score` → **EKSİK** (henüz hesaplanmıyor)
13. ❌ `m365_match_tags` → **EKSİK** (henüz hesaplanmıyor)

### Sync/Ops (2/5) ✅
14. ✅ `d365_sync_last_at` → `hunter_last_sync_time` (mapping'de yok ama DB'de var)
15. ✅ `d365_sync_error` → `hunter_sync_error_message` (mapping'de yok ama DB'de var)
16. ❌ `d365_sync_attempt_count` → **EKSİK** (DB'de yok, migration gerekir)
17. ❌ `is_re_enriched` → **EKSİK** (DB'de yok, logic gerekir)
18. ❌ `processing_status` → **EKSİK** (DB'de yok, `d365_sync_status` ile eşleştirilebilir)

---

## 🔧 Düzeltme Planı

### Phase 1: Backend Mapping Düzeltmeleri (1-2 saat)

**1. Priority Score Ekle**:
```python
# app/integrations/d365/mapping.py
from app.core.priority import calculate_priority_score

# lead_data'ya priority_score ekle (d365_push.py'de)
priority_score = calculate_priority_score(
    lead_data.get("segment"),
    lead_data.get("readiness_score")
)

# mapping.py'de
hunter_fields = {
    # ... existing fields ...
    "hunter_priority_score": lead_data.get("priority_score"),  # ✅ EKLE
}
```

**2. Is Partner Center Referral Ekle**:
```python
# mapping.py'de
is_partner_center_referral = bool(lead_data.get("referral_id"))
hunter_fields["hunter_is_partner_center_referral"] = is_partner_center_referral
```

**3. Sync Fields Ekle**:
```python
# mapping.py'de
hunter_fields = {
    # ... existing fields ...
    "hunter_last_sync_time": lead_data.get("d365_sync_last_at"),  # ✅ EKLE
    "hunter_sync_error_message": lead_data.get("d365_sync_error"),  # ✅ EKLE
    "hunter_sync_attempt_count": lead_data.get("d365_sync_attempt_count"),  # ⚠️ Migration gerekir
    "hunter_is_re_enriched": lead_data.get("is_re_enriched"),  # ⚠️ Logic gerekir
    "hunter_processing_status": lead_data.get("d365_sync_status"),  # ✅ EKLE (mapping: pending→Idle, in_progress→Working, synced→Completed, error→Error)
}
```

**4. Partner Center Fields Ekle**:
```python
# d365_push.py'de lead_data query'sine ekle
query = """
SELECT 
    -- ... existing fields ...
    pcr.azure_tenant_id,  # ✅ EKLE
    pcr.referral_type,  # ✅ EKLE
FROM leads_ready lr
LEFT JOIN companies c ON lr.company_id = c.id
LEFT JOIN partner_center_referrals pcr ON lr.domain = pcr.domain
WHERE lr.company_id = :company_id
LIMIT 1
"""

# mapping.py'de
hunter_fields = {
    # ... existing fields ...
    "hunter_tenant_id": lead_data.get("azure_tenant_id"),  # ✅ EKLE
    "hunter_referral_type": lead_data.get("referral_type"),  # ✅ EKLE
    "hunter_source": "Partner Center" if lead_data.get("referral_id") else "Manual",  # ✅ EKLE (basit logic)
}
```

---

### Phase 2: Database Migration (30 dakika)

**Migration**: `d365_sync_attempt_count` ekle

```python
# alembic/versions/XXXX_add_d365_sync_attempt_count.py
def upgrade() -> None:
    op.add_column('companies', sa.Column('d365_sync_attempt_count', sa.Integer(), nullable=True, server_default='0'))
    op.create_index('idx_companies_d365_sync_attempt_count', 'companies', ['d365_sync_attempt_count'])
```

**Migration**: `is_re_enriched` ekle (opsiyonel, şimdilik skip edilebilir)

```python
# alembic/versions/XXXX_add_is_re_enriched.py
def upgrade() -> None:
    op.add_column('companies', sa.Column('is_re_enriched', sa.Boolean(), nullable=True, server_default='false'))
```

---

### Phase 3: d365_push.py Güncellemeleri (30 dakika)

**1. Priority Score Hesapla**:
```python
# d365_push.py'de lead_data'ya ekle
from app.core.priority import calculate_priority_score

priority_score = calculate_priority_score(row.segment, row.readiness_score)
lead_data["priority_score"] = priority_score
```

**2. Sync Attempt Count Artır**:
```python
# d365_push.py'de push başlamadan önce
company.d365_sync_attempt_count = (company.d365_sync_attempt_count or 0) + 1
db.commit()
```

**3. Processing Status Mapping**:
```python
# mapping.py'de
def _map_processing_status(sync_status: Optional[str]) -> Optional[str]:
    """Map D365 sync status to processing status."""
    if not sync_status:
        return "Idle"
    mapping = {
        "pending": "Idle",
        "in_progress": "Working",
        "synced": "Completed",
        "error": "Error",
    }
    return mapping.get(sync_status, "Idle")
```

---

## 📋 D365 Field Set - Final Liste (18 Alan)

### Core Hunter Intelligence (7)
1. ✅ `hunter_readiness_score` (WN) - readiness_score
2. ✅ `hunter_priority_score` (WN) - priority_score (1-7) **EKSİK - EKLE**
3. ✅ `hunter_segment` (CH) - segment
4. ✅ `hunter_provider` (SLT) - provider
5. ✅ `hunter_tenant_size` (CH/SLT) - tenant_size
6. ✅ `hunter_infrastructure_summary` (MLT) - infrastructure_summary
7. ✅ `hunter_is_partner_center_referral` (2O) - bool(referral_id) **EKSİK - EKLE**

### Partner Center Enriched (6)
8. ✅ `hunter_tenant_id` (SLT) - azure_tenant_id **EKSİK - EKLE**
9. ✅ `hunter_referral_id` (SLT) - referral_id
10. ✅ `hunter_referral_type` (CH) - referral_type **EKSİK - EKLE**
11. ✅ `hunter_source` (CH) - source logic **EKSİK - EKLE**
12. ⚠️ `hunter_m365_fit_score` (WN) - **POST-MVP** (şimdilik None veya readiness_score)
13. ⚠️ `hunter_m365_match_tags` (MLT) - **POST-MVP** (şimdilik None)

### D365 Sync / Ops (5)
14. ✅ `hunter_last_sync_time` (DT) - d365_sync_last_at **EKSİK - EKLE**
15. ✅ `hunter_sync_error_message` (MLT) - d365_sync_error **EKSİK - EKLE**
16. ✅ `hunter_sync_attempt_count` (WN) - d365_sync_attempt_count **EKSİK - MIGRATION GEREKİR**
17. ⚠️ `hunter_is_re_enriched` (2O) - **POST-MVP** (şimdilik skip)
18. ✅ `hunter_processing_status` (CH) - d365_sync_status (mapped) **EKSİK - EKLE**

---

## 🎯 Öneriler

### 1. **M365 Fit Score - Basit Mapping** (Öneri)

**Şimdilik**: M365 Fit Score hesaplama yok, ama basit bir mapping yapılabilir:

```python
# mapping.py'de
if lead_data.get("provider") == "M365":
    m365_fit_score = lead_data.get("readiness_score")
else:
    m365_fit_score = None

hunter_fields["hunter_m365_fit_score"] = m365_fit_score
```

**Post-MVP**: Gerçek M365 fit algoritması (tenant size, license count, etc.)

---

### 2. **Source Field - Basit Logic** (Öneri)

**Şimdilik**: Basit logic ile source belirle:

```python
# mapping.py'de
if lead_data.get("referral_id"):
    source = "Partner Center"
elif lead_data.get("domain"):  # Manual entry
    source = "Manual"
else:
    source = "Other"

hunter_fields["hunter_source"] = source
```

**Post-MVP**: `companies.source` field'ı ekle (migration gerekir)

---

### 3. **Is Re-Enriched - Post-MVP** (Öneri)

**Şimdilik**: Skip et, D365'te field'ı aç ama backend'de `None` gönder.

**Post-MVP**: Rescan/enrichment tracking sistemi ekle.

---

## ✅ Sonuç

**Kritik Düzeltmeler** (Yapılmalı):
1. ✅ Priority Score mapping'e ekle
2. ✅ Is Partner Center Referral bool ekle
3. ✅ Sync Attempt Count migration + mapping

**Orta Öncelik** (Yapılabilir):
4. ⚠️ M365 Fit Score basit mapping (Post-MVP için hazırlık)
5. ⚠️ Source field basit logic

**Post-MVP** (Şimdilik Skip):
6. ⚠️ M365 Match Tags (henüz algoritma yok)
7. ⚠️ Is Re-Enriched (tracking sistemi gerekli)

**Toplam**: 18 alanın **13'ü** şimdi yapılabilir, **5'i** Post-MVP.

---

## 📝 Cursor'a Verilecek Prompt

```
D365 Lead entity üzerinde aşağıdaki Hunter alanlarını oluşturuyorum:

**Core Hunter Intelligence (7):**
- Hunter Readiness Score (int, 0-100)
- Hunter Priority Score (int, 1-7) ⚠️ EKSİK - mapping.py'ye ekle
- Hunter Segment (enum: Migration/Existing/Cold/Skip)
- Hunter Provider (string)
- Hunter Tenant Size (enum: Small/Medium/Large/Enterprise)
- Hunter Infrastructure Summary (string, MLT)
- Hunter Is Partner Center Referral (bool) ⚠️ EKSİK - mapping.py'ye ekle

**Partner Center Enriched (6):**
- Hunter Tenant ID (string, GUID) ⚠️ EKSİK - d365_push.py query'sine ekle
- Hunter Referral ID (string)
- Hunter Referral Type (enum: Co-sell/Marketplace/Solution Provider/Manual) ⚠️ EKSİK - d365_push.py query'sine ekle
- Hunter Source (enum: Partner Center/Manual/Import/Other) ⚠️ EKSİK - basit logic ekle
- Hunter M365 Fit Score (int, 0-100) ⚠️ POST-MVP - şimdilik None veya readiness_score (M365 ise)
- Hunter M365 Match Tags (string, MLT) ⚠️ POST-MVP - şimdilik None

**D365 Sync/Ops (5):**
- Hunter Last Sync Time (datetime) ⚠️ EKSİK - mapping.py'ye ekle
- Hunter Sync Error Message (string, MLT) ⚠️ EKSİK - mapping.py'ye ekle
- Hunter Sync Attempt Count (int) ⚠️ EKSİK - migration gerekir + mapping.py'ye ekle
- Hunter Is Re-Enriched (bool) ⚠️ POST-MVP - şimdilik skip
- Hunter Processing Status (enum: Idle/Working/Completed/Error) ⚠️ EKSİK - d365_sync_status mapping ekle

**Görevler:**
1. `app/integrations/d365/mapping.py`'yi güncelle (priority_score, is_partner_center_referral, sync fields, partner center fields)
2. `app/tasks/d365_push.py`'yi güncelle (priority_score hesapla, lead_data query'sine azure_tenant_id ve referral_type ekle)
3. Migration oluştur: `d365_sync_attempt_count` field'ı `companies` tablosuna ekle
4. Processing status mapping fonksiyonu ekle (d365_sync_status → hunter_processing_status)
```

---

**Durum**: ✅ Kritik analiz tamamlandı, düzeltme planı hazır.

