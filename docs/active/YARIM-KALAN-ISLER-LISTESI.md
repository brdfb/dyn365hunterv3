# 📋 Yarım Kalan İşler - Tam Liste

**Tarih**: 2025-01-30  
**Durum**: Güncel Durum Özeti  
**Son Güncelleme**: 2025-01-30 (D365 Push PoC completion sonrası)

---

## 🎯 KRİTİK (P0) - Acil Aksiyon Gerekenler

### 1. HAMLE 1: Partner Center Sync Aktifleştirme ✅ **COMPLETED** (2025-01-30)

**Durum**: ✅ Kod bazında DONE, ürün bazında yeterince iyi seviyesinde  
**Süre**: Tamamlandı (2025-01-30)  
**Öncelik**: P0 (Kritik - Kaynak entegrasyonu)  
**Karar**: UI JS & error handling manuel smoke test ile kapanacak (mimari değişiklik gerektirmiyor)

**Tamamlananlar:**
- [x] Feature flag aktifleştirildi: `HUNTER_PARTNER_CENTER_ENABLED=true` ✅
- [x] OAuth credentials kontrolü tamamlandı (CLIENT_ID, TENANT_ID mevcut) ✅
- [x] Token cache dosyası kontrolü tamamlandı (`.token_cache` mevcut) ✅
- [x] Manual sync test tamamlandı (739 referral, 17 M365 company) ✅
- [x] UI feedback kontrolü tamamlandı (HTML yapısı doğrulandı, browser test yapıldı) ✅
- [x] Error handling doğrulama tamamlandı (Kod incelemesi tamamlandı) ✅

**Tamamlananlar:**
- [x] OAuth credentials kontrolü ✅
- [x] Feature flag aktifleştirildi ✅
- [x] Initial authentication ✅
- [x] Manual sync test ✅
- [x] UI HTML yapısı doğrulandı ✅
- [x] Error handling kod incelemesi tamamlandı ✅

**Kalan İşler (Opsiyonel - Mimari Değişiklik Gerektirmiyor):**
- [ ] Background sync (Celery Beat) - Beat service yok (opsiyonel, D365 sonrası)
- [ ] UI JavaScript functionality manuel smoke test (10-20 dk, XS-S)
- [ ] Error handling manuel smoke test (10-20 dk, XS-S)

**Dosyalar:**
- `app/config.py` - Feature flag kontrolü
- `app/core/partner_center.py` - OAuth client
- `app/core/referral_ingestion.py` - Sync logic
- `app/core/tasks.py` - Celery task
- `.env` - Feature flag ve credentials

**Referans**: `docs/active/CRITICAL-3-HAMLE-PRODUCT-READY.md` - Hamle 1

---

### 2. HAMLE 2: D365 Phase 2.9 E2E Wiring & Tenant Setup ✅ **DEV TESTS COMPLETED** (2025-01-30)

**Durum**: Backend %94 + UI completed, Push PoC completed, E2E runbook ready  
**Süre**: 1-2 gün (ops fazı)  
**Öncelik**: P0 (Kritik - Satış pipeline'ı)  
**Karar**: HAMLE 2'ye geçildi (2025-01-30) - Pipeline'ın gerçek değeri D365'e indiğin anda açılıyor

**Tamamlananlar:**
- [x] Azure AD App Registration oluştur ✅
- [x] D365 Application User oluştur ve security role ata ✅
- [x] Hunter config güncelle (`.env` - D365 credentials) ✅
- [x] Feature flag aktifleştir: `HUNTER_D365_ENABLED=true` (DEV) ✅
- [x] Manual E2E testler (3 core senaryo): ✅
  - [x] Happy path test ✅
  - [x] Idempotency test ✅
  - [x] Edge case test ✅ (all bugs fixed)
- [x] UI Badge & Link test ✅
- [x] Error handling testler ✅ (Authentication error tested, Rate limit & API error code verified)
- [x] Go/No-Go gate: ✅ GO (production'a geçiş için hazır)

**Durum:** ✅ Dev testleri %100 tamamlandı, production deployment hazırlığı

**Dosyalar:**
- `docs/active/D365-PHASE-2.9-E2E-RUNBOOK.md` - Step-by-step runbook
- `.env` - D365 credentials
- `app/config.py` - Feature flag kontrolü

**Referans**: `docs/active/D365-PHASE-2.9-E2E-RUNBOOK.md`

---

## 🔄 IN PROGRESS - Devam Eden İşler

### 3. Integration Roadmap - Phase 3: Dynamics 365 Integration ✅ **DEV TESTS COMPLETED**

**Durum**: Backend %94 + UI completed, Push PoC completed, E2E dev testleri completed  
**Süre**: Production deployment hazırlığı  
**Öncelik**: P2

**Tamamlananlar:**
- [x] Phase 2.9 (E2E Wiring) - Tenant setup ve manuel testler ✅
- [x] E2E Tests: Happy path ✅, Idempotency ✅, Edge case ✅
- [x] UI Badge & Link: Badge görünüyor ✅, D365 link çalışıyor ✅
- [x] Error Handling: Authentication error tested ✅, Rate limit & API error code verified ✅
- [x] Go/No-Go Decision: ✅ GO (production'a geçiş için hazır)

**Kalan İşler:**
- [ ] Production deployment (HAMLE 2 dev testleri tamamlandı)
- [ ] Success criteria validation (production'da):
  - [ ] Dynamics sync success rate > 90%
  - [ ] Pipeline accuracy > 95%
  - [ ] Error recovery automatic

**Referans**: `docs/todos/INTEGRATION-ROADMAP.md` - Phase 3

---

### 4. G21: Architecture Refactor - Phase 4-6 🔄 **PAUSED**

**Durum**: Phase 0-3 completed, Phase 4 paused (Integration Roadmap Phase 3 overlaps)  
**Süre**: Post-MVP  
**Öncelik**: P0 (Critical) ama paused

**Kalan İşler:**
- [ ] Phase 4: Dynamics Migration (PAUSED - Integration Roadmap Phase 3 ile birleştirilecek)
- [ ] Phase 5: Monitoring & Stabilization (deprecated endpoint usage monitoring)
- [ ] Phase 6: Cleanup (remove deprecated endpoints, archive tables)

**Referans**: `docs/todos/G21-architecture-refactor.md`

---

## 📋 POST-MVP / FUTURE ENHANCEMENTS

### 5. Partner Center - Scoring Pipeline Integration ⏳ **FUTURE ENHANCEMENT**

**Durum**: Backend hazır, entegrasyon eksik  
**Süre**: 1-2 gün  
**Öncelik**: Post-MVP

**Yapılacaklar:**
- [ ] Azure Tenant ID override (scoring pipeline'da)
- [ ] Co-sell boost (scoring pipeline'da)
- [ ] Referral type bazlı scoring adjustment

**Referans**: `docs/todos/INTEGRATION-ROADMAP.md` - Phase 2, Task 2.3

---

### 6. D365 - Option Set Value Mapping (Post-MVP Enhancement) ⏳ **PARTIALLY DONE**

**Durum**: Mapping fonksiyonları eklendi, D365'teki gerçek value'lar doğrulanmalı  
**Süre**: 1-2 saat  
**Öncelik**: Post-MVP

**Yapılacaklar:**
- [ ] D365 Option Set metadata'sını kontrol et (Power Apps → Customizations → Option Sets)
- [ ] Mapping value'larını D365'teki gerçek value'larla karşılaştır
- [ ] Gerekirse mapping fonksiyonlarını güncelle
- [ ] Dynamic Option Set value lookup (opsiyonel - runtime'da D365'ten çek)

**Not**: Şu anki mapping varsayılan değerler kullanıyor (0, 1, 2, 3). D365'te farklı value'lar olabilir.

**Referans**: `docs/reference/D365-OPTION-SET-MAPPING.md`

---

### 7. D365 - Post-MVP Fields (6 Alan) ⏳ **POST-MVP**

**Durum**: D365'te henüz oluşturulmamış  
**Süre**: 1-2 gün  
**Öncelik**: Post-MVP

**Eksik Alanlar:**
- [ ] `hnt_prioritycategory` (priority_category)
- [ ] `hnt_prioritylabel` (priority_label)
- [ ] `hnt_technicalheat` (technical_heat)
- [ ] `hnt_commercialsegment` (commercial_segment)
- [ ] `hnt_commercialheat` (commercial_heat)
- [ ] `hnt_ispartnercenterreferral` (calculated from `hnt_referralid`)

**Yapılacaklar:**
- [ ] D365'te custom field'ları oluştur
- [ ] Form'a ekle (Hunter Intelligence section)
- [ ] View'lara ekle
- [ ] `mapping.py`'ye ekle
- [ ] Test et

**Referans**: `docs/archive/2025-01-30-D365-PUSH-POC-TASK-LIST.md` - Post-MVP section

---

### 8. Partner Center - Future Enhancements ⏳ **POST-MVP** (Kısmen Tamamlandı)

**Durum**: Backend hazır, UI enhancement'lar eksik  
**Süre**: 1-2 gün  
**Öncelik**: Post-MVP

**Yapılacaklar:**
- [ ] `GET /api/v1/partner-center/referrals` - List referrals with filters (endpoint yok)
- [x] `GET /api/v1/partner-center/referrals/{referral_id}` - Get single referral (✅ Completed - `get_referral_detail` endpoint var)
- [ ] Referrals section to Mini UI
- [ ] Referral status badges
- [x] Referral detail modal (✅ Completed - 2025-01-30)

**Referans**: `docs/todos/INTEGRATION-ROADMAP.md` - Phase 2, Future Enhancements

---

### 9. D365 - Future Enhancements ⏳ **POST-MVP**

**Durum**: Backend hazır, enhancement'lar eksik  
**Süre**: 1-2 gün  
**Öncelik**: Post-MVP

**Yapılacaklar:**
- [ ] Bulk push endpoint (`POST /api/v1/d365/push-bulk`)
- [ ] Push status dashboard
- [ ] Retry failed pushes
- [ ] Push history/audit log

**Referans**: `docs/todos/INTEGRATION-ROADMAP.md` - Phase 3, Future Enhancements

---

## 🔧 P2 BACKLOG - Code Quality & Performance

### 10. N+1 Query Prevention ⏳ **BACKLOG**

**Durum**: Potansiyel sorun - Doğru risk bölgeleri analiz edilmeli  
**Süre**: 1 gün  
**Öncelik**: P2

**Yapılacaklar:**
- [ ] `leads_ready` VIEW SQL'ini audit et (N+1 var mı?)
- [ ] JOIN + ORDER BY + LIMIT pattern'ini optimize et
- [ ] Provider filtering'de unnecessary join'leri kaldır
- [ ] Pagination COUNT(*) stratejisini optimize et (window function?)
- [ ] Eager loading ekle (joinedload, selectinload) - gerekli yerlerde
- [ ] Test: Query count kontrol et (N+1 yok mu? - SQLAlchemy query logging)

**Referans**: `docs/active/KALAN-ISLER-PRIORITY.md` - P2, N+1 Query Prevention

---

### 11. Sync-First Refactor ⏳ **BACKLOG**

**Durum**: Şu an async-first yaklaşım  
**Süre**: 2 gün  
**Öncelik**: P2

**Yapılacaklar:**
- [ ] Async fonksiyonları sync'e çevir (gereksiz async'ler)
- [ ] Code maintainability iyileştir

**Referans**: `docs/active/KALAN-ISLER-PRIORITY.md` - P2, Sync-First Refactor

---

### 12. Repository/Service Layer ⏳ **BACKLOG**

**Durum**: Şu an direct DB access  
**Süre**: 3 gün  
**Öncelik**: P2

**Yapılacaklar:**
- [ ] Repository pattern ekle
- [ ] Service layer ekle
- [ ] Code organization iyileştir

**Referans**: `docs/active/KALAN-ISLER-PRIORITY.md` - P2, Repository/Service Layer

---

## 🎨 UI POLISH - Estetik İyileştirmeler

### 13. HAMLE 3: UI Polish ⏳ **PENDING**

**Durum**: UI çalışıyor ama estetik fakir  
**Süre**: 3-5 gün  
**Öncelik**: P1 (Yüksek - Kullanıcı deneyimi)

**Yapılacaklar:**
- [ ] Table view estetik iyileştirmeleri
- [ ] Modal'lar estetik iyileştirmeleri
- [ ] Button'lar estetik iyileştirmeleri
- [ ] Color scheme iyileştirmeleri
- [ ] Typography iyileştirmeleri
- [ ] Spacing/layout iyileştirmeleri

**Referans**: `docs/active/CRITICAL-3-HAMLE-PRODUCT-READY.md` - Hamle 3

---

## 📊 ÖZET TABLO

| # | İş | Durum | Öncelik | Süre | Blocker? |
|---|-----|-------|---------|------|----------|
| 1 | Partner Center Sync Aktifleştirme | ✅ Completed (2025-01-30) | P0 | Tamamlandı | ❌ Hayır |
| 2 | D365 Phase 2.9 E2E Wiring | 🔄 In Progress (2025-01-30) | P0 | 1-2 gün | ❌ Hayır (tenant setup) |
| 3 | Integration Roadmap Phase 3 | 🔄 In Progress | P2 | Phase 2.9 sonrası | ❌ Hayır |
| 4 | G21 Phase 4-6 | 🔄 Paused | P0 (paused) | Post-MVP | ❌ Hayır |
| 5 | Partner Center Scoring Integration | ⏳ Future | Post-MVP | 1-2 gün | ❌ Hayır |
| 6 | D365 Option Set Value Verification | ⏳ Future | Post-MVP | 1-2 saat | ❌ Hayır |
| 7 | D365 Post-MVP Fields (6 alan) | ⏳ Future | Post-MVP | 1-2 gün | ❌ Hayır |
| 8 | Partner Center Future Enhancements | ⏳ Future | Post-MVP | 1-2 gün | ❌ Hayır |
| 9 | D365 Future Enhancements | ⏳ Future | Post-MVP | 1-2 gün | ❌ Hayır |
| 10 | N+1 Query Prevention | ⏳ Backlog | P2 | 1 gün | ❌ Hayır |
| 11 | Sync-First Refactor | ⏳ Backlog | P2 | 2 gün | ❌ Hayır |
| 12 | Repository/Service Layer | ⏳ Backlog | P2 | 3 gün | ❌ Hayır |
| 13 | UI Polish | ⏳ Pending | P1 | 3-5 gün | ❌ Hayır |

---

## 🎯 ÖNCELİK SIRASI (Önerilen)

### Acil (Bu Hafta)
1. **HAMLE 1**: Partner Center Sync Aktifleştirme ✅ **COMPLETED** (2025-01-30)
2. **HAMLE 2**: D365 Phase 2.9 E2E Wiring ✅ **DEV TESTS COMPLETED** (2025-01-30) - Go/No-Go: ✅ GO

### Orta Vadeli (Bu Ay)
3. **HAMLE 3**: UI Polish (3-5 gün)

### Post-MVP / Backlog
4. Partner Center Scoring Integration
5. D365 Option Set Value Verification
6. D365 Post-MVP Fields
7. N+1 Query Prevention
8. Sync-First Refactor
9. Repository/Service Layer

---

## 📝 NOTLAR

- **D365 Push PoC**: ✅ Completed (2025-01-30) - End-to-end flow working
- **Partner Center Backend**: ✅ Completed (2025-01-30) - Feature flag OFF
- **G21 Phase 0-3**: ✅ Completed (2025-01-28)
- **Integration Roadmap Phase 1-2**: ✅ Completed (2025-01-30)

---

## ✅ KONTROL SONUÇLARI (2025-01-30)

### Yapılan İşler (Kısmen veya Tamamen)
- ✅ **Partner Center Referral Detail Endpoint**: `GET /api/v1/partner-center/referrals/{referral_id}` endpoint'i var ve çalışıyor
- ✅ **Partner Center Referral Detail Modal**: UI'da modal tamamlandı (2025-01-30)
- ✅ **D365 Option Set Mapping Functions**: Mapping fonksiyonları eklendi (doğrulama bekliyor)

### Yapılmayan İşler (Kontrol Edildi)
- ❌ **Partner Center Sync**: Feature flag `False` - Aktifleştirilmemiş
- ❌ **D365 Phase 2.9 E2E**: Feature flag `False` - Tenant setup yapılmamış
- ❌ **Partner Center Scoring Integration**: Config var ama `scorer.py`'de kullanılmıyor
- ❌ **D365 Post-MVP Fields**: Mapping'de comment olarak var, kodlanmamış
- ❌ **D365 Bulk Push**: Endpoint yok
- ❌ **Partner Center Referrals List**: `GET /api/v1/partner-center/referrals` endpoint'i yok
- ❌ **N+1 Query Prevention**: Eager loading yok, VIEW optimize edilmemiş
- ❌ **Sync-First Refactor**: Async fonksiyonlar var
- ❌ **Repository/Service Layer**: Direct DB access var

**Son Güncelleme**: 2025-01-30  
**Kontrol Tarihi**: 2025-01-30

