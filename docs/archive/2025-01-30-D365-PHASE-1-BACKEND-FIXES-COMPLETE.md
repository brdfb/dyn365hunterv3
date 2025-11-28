# D365 Phase 1 - Backend Düzeltmeleri ✅ TAMAMLANDI

**Tarih**: 2025-01-30  
**Durum**: ✅ **Tüm düzeltmeler tamamlandı**

---

## 🎯 Özet

**Phase 1 - Backend Düzeltme Paketi** başarıyla tamamlandı:
- ✅ **P0 Kritik 3 düzeltme** (Priority Score, Is Partner Center Referral, Sync Attempt Count)
- ✅ **P1 Bonus 2 düzeltme** (Partner Center enriched fields, Sync/Ops mapping)

---

## ✅ Tamamlanan Düzeltmeler

### P0-1: Priority Score Mapping ✅

**Dosyalar**:
- `app/integrations/d365/mapping.py` - `hunter_priority_score` eklendi
- `app/tasks/d365_push.py` - `priority_score` hesaplama ve `lead_data`'ya ekleme

**Değişiklikler**:
```python
# mapping.py
hunter_fields["hunter_priority_score"] = lead_data.get("priority_score")

# d365_push.py
from app.core.priority import calculate_priority_score
priority_score = calculate_priority_score(row.segment, row.readiness_score)
lead_data["priority_score"] = priority_score
```

---

### P0-2: Is Partner Center Referral (Bool) ✅

**Dosyalar**:
- `app/integrations/d365/mapping.py` - `hunter_is_partner_center_referral` eklendi

**Değişiklikler**:
```python
# mapping.py
referral_id = lead_data.get("referral_id")
if referral_id:
    hunter_fields["hunter_referral_id"] = referral_id

hunter_fields["hunter_is_partner_center_referral"] = bool(referral_id)
```

---

### P0-3: Sync Attempt Count ✅

**Dosyalar**:
- `alembic/versions/67a00e2b26ab_add_d365_sync_attempt_count.py` - Migration oluşturuldu
- `app/db/models.py` - `d365_sync_attempt_count` field eklendi
- `app/tasks/d365_push.py` - Counter artırma logic eklendi
- `app/integrations/d365/mapping.py` - Mapping eklendi

**Değişiklikler**:
```python
# Migration
op.add_column('companies', sa.Column('d365_sync_attempt_count', sa.Integer(), nullable=True, server_default='0'))
op.create_index('idx_companies_d365_sync_attempt_count', 'companies', ['d365_sync_attempt_count'])

# models.py
d365_sync_attempt_count = Column(Integer, nullable=True, server_default="0", index=True)

# d365_push.py
company.d365_sync_attempt_count = (company.d365_sync_attempt_count or 0) + 1

# mapping.py
hunter_fields["hunter_sync_attempt_count"] = lead_data.get("d365_sync_attempt_count")
```

---

### P1-4: Partner Center Enriched Fields ✅

**Dosyalar**:
- `app/tasks/d365_push.py` - Query'ye `azure_tenant_id` ve `referral_type` eklendi
- `app/integrations/d365/mapping.py` - Mapping eklendi

**Değişiklikler**:
```python
# d365_push.py query
pcr.azure_tenant_id,
pcr.referral_type

# lead_data
"azure_tenant_id": row.azure_tenant_id if hasattr(row, "azure_tenant_id") else None,
"referral_type": row.referral_type if hasattr(row, "referral_type") else None,

# mapping.py
hunter_fields["hunter_tenant_id"] = lead_data.get("azure_tenant_id")
hunter_fields["hunter_referral_type"] = lead_data.get("referral_type")
hunter_fields["hunter_source"] = "Partner Center" if referral_id else "Manual"
```

---

### P1-5: Sync/Ops Mapping ✅

**Dosyalar**:
- `app/integrations/d365/mapping.py` - Helper fonksiyon ve mapping eklendi
- `app/tasks/d365_push.py` - Query'ye sync fields eklendi

**Değişiklikler**:
```python
# mapping.py - Helper fonksiyon
def _map_processing_status(sync_status: Optional[str]) -> Optional[str]:
    mapping = {
        "pending": "Idle",
        "in_progress": "Working",
        "synced": "Completed",
        "error": "Error",
    }
    if not sync_status:
        return "Idle"
    return mapping.get(sync_status, "Idle")

# mapping.py - Mapping
hunter_fields["hunter_last_sync_time"] = lead_data.get("d365_sync_last_at")
hunter_fields["hunter_sync_error_message"] = lead_data.get("d365_sync_error")
hunter_fields["hunter_processing_status"] = _map_processing_status(lead_data.get("d365_sync_status"))

# d365_push.py query
c.d365_sync_last_at,
c.d365_sync_error,
c.d365_sync_attempt_count,
```

---

## 📋 Eklenen Field'lar (Mapping'de)

### Core Intelligence (7)
1. ✅ `hunter_score` - readiness_score
2. ✅ `hunter_priority_score` - priority_score (1-7) **YENİ**
3. ✅ `hunter_segment` - segment
4. ✅ `hunter_provider` - provider
5. ✅ `hunter_tenant_size` - tenant_size
6. ✅ `hunter_infrastructure` - infrastructure_summary
7. ✅ `hunter_is_partner_center_referral` - bool(referral_id) **YENİ**

### Partner Center Enriched (4)
8. ✅ `hunter_tenant_id` - azure_tenant_id **YENİ**
9. ✅ `hunter_referral_id` - referral_id
10. ✅ `hunter_referral_type` - referral_type **YENİ**
11. ✅ `hunter_source` - source logic **YENİ**

### Sync/Ops (4)
12. ✅ `hunter_last_sync_time` - d365_sync_last_at **YENİ**
13. ✅ `hunter_sync_error_message` - d365_sync_error **YENİ**
14. ✅ `hunter_sync_attempt_count` - d365_sync_attempt_count **YENİ**
15. ✅ `hunter_processing_status` - d365_sync_status (mapped) **YENİ**

---

## 🚀 Sonraki Adımlar

### Phase 2: D365 Lead Custom Fields (13 Alan)

**Şimdi açılacak alanlar**:
1. Core Intelligence (7): Readiness Score, Priority Score, Segment, Provider, Tenant Size, Infrastructure Summary, Is Partner Center Referral
2. Partner Center (4): Tenant ID, Referral ID, Referral Type, Source
3. Sync/Ops (4): Last Sync Time, Sync Error Message, Sync Attempt Count, Processing Status

**Post-MVP (5 alan)**:
- M365 Fit Score, M365 Match Tags, Is Re-Enriched (şimdilik skip)

### Phase 3: Lead Form Design v1.0

Backend + field'lar oturduktan sonra form tasarımı yapılacak.

---

## ✅ Test Checklist

**Migration**:
- [ ] `alembic upgrade head` çalıştır
- [ ] `companies.d365_sync_attempt_count` field'ının eklendiğini doğrula

**Backend**:
- [ ] `d365_push.py` test et (priority_score hesaplama)
- [ ] `mapping.py` test et (tüm yeni field'ların mapping'de olduğunu doğrula)
- [ ] Partner Center referral'ı olan bir lead push et, field'ların doğru geldiğini kontrol et

**D365**:
- [ ] 13 alanı D365'te aç
- [ ] Test push yap, field'ların doğru doldurulduğunu kontrol et

---

## 📝 Notlar

- **Infrastructure Summary**: `build_infra_summary()` fonksiyonu `d365_push.py`'de kullanılıyor, IP enrichment'dan otomatik alınıyor
- **Priority Score**: `calculate_priority_score()` fonksiyonu ile hesaplanıyor (1-7)
- **Source Logic**: Basit logic (`referral_id` varsa → "Partner Center", yoksa → "Manual")
- **Processing Status**: `d365_sync_status` → `hunter_processing_status` mapping helper fonksiyonu ile yapılıyor

---

**Durum**: ✅ **Phase 1 tamamlandı, Phase 2'ye geçilebilir**

