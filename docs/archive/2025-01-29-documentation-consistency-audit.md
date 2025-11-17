# Dokümantasyon Tutarlılık Denetimi - 2025-01-28

**Tarih**: 2025-01-28  
**Durum**: ✅ **GÜNCELLENDİ** (2025-01-28 - Tüm tutarsızlıklar giderildi)  
**Kapsam**: Partner Center Phase 2 dokümantasyonu

---

## ✅ Güncel ve Tutarlı Dosyalar

### 1. Yeni MVP Yaklaşımı (Revize Edilmiş)
- ✅ `docs/prompts/2025-01-28-partner-center-phase2-task-list.md` - **GÜNCEL** (MVP yaklaşımı)
- ✅ `docs/todos/PARTNER-CENTER-PHASE2.md` - **GÜNCEL** (MVP yaklaşımı)
- ✅ `docs/active/KALAN-ISLER-PRIORITY.md` - **GÜNCEL** (Phase 2 task breakdown eklendi)

**Özellikler**:
- MVP: Minimal API client (50-70 satır)
- MVP: Sadece `POST /api/referrals/sync` endpoint
- MVP: UI'da sadece lead listesine 1 kolon (referral type)
- MVP: Polling (10 min prod, 30s dev)
- Scoring pipeline entegrasyonu
- Domain scan idempotent

---

## ✅ Güncellenmiş Dosyalar

### 2. Eski Dokümantasyon (MVP Yaklaşımına Göre Güncellendi - 2025-01-28)
- ✅ `docs/todos/INTEGRATION-ROADMAP.md` - **GÜNCELLENDİ** (MVP yaklaşımı eklendi)
- ✅ `docs/plans/2025-01-28-INTEGRATION-ROADMAP-v1.0.md` - **GÜNCELLENDİ** (MVP yaklaşımı eklendi)
- ✅ `docs/plans/2025-01-28-INTEGRATION-TASKS.md` - **GÜNCELLENDİ** (MVP yaklaşımı eklendi)

**Eski Yaklaşım (Hatalı)**:
- ❌ `GET /referrals` - List referrals (MVP'de yok)
- ❌ `GET /referrals/{referral_id}` - Get single referral (MVP'de yok)
- ❌ `POST /referrals/sync` - Manual sync (path farklı: `/api/referrals/sync` olmalı)
- ❌ UI'da referrals section, badges, filter (MVP'de sadece 1 kolon)
- ❌ API client detayları eksik (MVP: minimal 50-70 satır)
- ❌ Scoring pipeline entegrasyonu yok
- ❌ Domain scan idempotent yok

---

## 📊 Tutarsızlık Detayları

### Task 2.1: Partner Center API Client

| Özellik | Eski Dokümantasyon | Yeni MVP | Durum |
|---------|-------------------|----------|-------|
| Client complexity | Enterprise-grade (belirtilmemiş) | Minimal (50-70 satır) | ⚠️ Farklı |
| Rate limiting | Handle rate limiting (belirsiz) | `sleep(1)` basic | ⚠️ Farklı |
| Retry logic | Belirtilmemiş | 2 deneme | ⚠️ Farklı |

### Task 2.2: Referral Data Model

| Özellik | Eski Dokümantasyon | Yeni MVP | Durum |
|---------|-------------------|----------|-------|
| Model fields | referral_id, company_name, domain, status | + referral_type, azure_tenant_id | ⚠️ Eksik |
| Hybrid model | Belirtilmemiş | raw_leads + partner_center_referrals | ⚠️ Eksik |

### Task 2.3: Referral Ingestion

| Özellik | Eski Dokümantasyon | Yeni MVP | Durum |
|---------|-------------------|----------|-------|
| Lead tipi detection | Belirtilmemiş | Co-sell, Marketplace, SP | ⚠️ Eksik |
| Azure Tenant ID | Belirtilmemiş | M365 signal, segment override | ⚠️ Eksik |
| Domain scan | Normal trigger | Idempotent (domain bazlı) | ⚠️ Farklı |
| Scoring pipeline | Belirtilmemiş | Azure Tenant ID + Co-sell boost | ⚠️ Eksik |

### Task 2.4: API Endpoints

| Endpoint | Eski Dokümantasyon | Yeni MVP | Durum |
|----------|-------------------|----------|-------|
| GET /referrals | ✅ Var | ❌ Yok (post-MVP) | ⚠️ Farklı |
| POST /referrals/sync | ✅ Var | ✅ Var (path: `/api/referrals/sync`) | ⚠️ Path farklı |
| GET /referrals/{id} | ✅ Var | ❌ Yok (post-MVP) | ⚠️ Farklı |
| v1 versioning | Belirtilmemiş | Nice-to-have (post-MVP) | ⚠️ Farklı |

### Task 2.5: UI Integration

| Özellik | Eski Dokümantasyon | Yeni MVP | Durum |
|---------|-------------------|----------|-------|
| Referrals section | ✅ Yeni tab/section | ❌ Yok | ⚠️ Farklı |
| Status badges | ✅ Var | ❌ Yok (post-MVP) | ⚠️ Farklı |
| Referral filter | ✅ Var | ❌ Yok (post-MVP) | ⚠️ Farklı |
| Lead listesine kolon | Belirtilmemiş | ✅ Sadece bu | ⚠️ Farklı |

### Task 2.6: Background Sync

| Özellik | Eski Dokümantasyon | Yeni MVP | Durum |
|---------|-------------------|----------|-------|
| Sync schedule | Daily/hourly (belirsiz) | 10 min prod, 30s dev | ⚠️ Farklı |
| Dev override | Belirtilmemiş | 30-60s (test edilebilir) | ⚠️ Eksik |

---

## 🔧 Gerekli Güncellemeler

### Öncelik 1: Kritik Tutarsızlıklar

1. **`docs/todos/INTEGRATION-ROADMAP.md`**
   - Task 2.4: API Endpoints → Sadece `POST /api/referrals/sync` (MVP)
   - Task 2.5: UI Integration → Sadece lead listesine 1 kolon
   - Task 2.1: API Client → Minimal (50-70 satır) notu ekle
   - Task 2.3: Referral Ingestion → Scoring pipeline, idempotent scan ekle

2. **`docs/plans/2025-01-28-INTEGRATION-ROADMAP-v1.0.md`**
   - Phase 2 bölümü → MVP yaklaşımı notu ekle
   - API endpoints → Sadece sync endpoint (MVP)
   - UI integration → Minimal yaklaşım notu ekle

3. **`docs/plans/2025-01-28-INTEGRATION-TASKS.md`**
   - Task 2.4: API Endpoints → MVP: sadece sync endpoint
   - Task 2.5: UI Integration → MVP: sadece lead listesine kolon
   - Task 2.1-2.3: MVP yaklaşımı detayları ekle

### Öncelik 2: Referans Güncellemeleri

4. **`docs/README.md`** (eğer Phase 2'den bahsediyorsa)
   - MVP yaklaşımı notu ekle

---

## 📝 Önerilen Aksiyon Planı

### Seçenek 1: Eski Dokümantasyonu Güncelle (Önerilen)
- Eski dosyaları MVP yaklaşımına göre güncelle
- "Future Enhancement" notları ekle (GET endpoints, UI features)
- Tutarlılık sağla

### Seçenek 2: Eski Dokümantasyonu Arşivle
- Eski dosyaları `docs/archive/` altına taşı
- Sadece yeni MVP dokümantasyonunu aktif tut
- Daha temiz ama geçmiş bağlam kaybolur

### Seçenek 3: Hybrid Yaklaşım
- Eski dosyalarda "MVP" ve "Future Enhancement" bölümleri ayır
- MVP kısmını güncelle
- Future kısmını olduğu gibi bırak

---

## ✅ Doğrulama Checklist

Güncellemelerden sonra kontrol edilecekler:

- [ ] Tüm dosyalarda MVP yaklaşımı tutarlı mı?
- [ ] API endpoint'leri tutarlı mı? (sadece POST /api/referrals/sync)
- [ ] UI integration tutarlı mı? (sadece lead listesine kolon)
- [ ] Task breakdown'lar senkron mu?
- [ ] Referanslar doğru mu?
- [ ] "Future Enhancement" notları var mı?

---

## 🎯 Sonuç

**Genel Tutarlılık**: ✅ **%100** (7/7 dosya güncel - 2025-01-28'de güncellendi)

**Kritik Tutarsızlıklar**:
1. API endpoints (GET endpoints MVP'de yok)
2. UI integration (referrals section MVP'de yok)
3. API client yaklaşımı (minimal vs enterprise)
4. Scoring pipeline entegrasyonu (eski dokümantasyonda yok)

**Öneri**: ✅ **TAMAMLANDI** - Eski dokümantasyon MVP yaklaşımına göre güncellendi (Seçenek 1 uygulandı).

**Yapılan Güncellemeler** (2025-01-28):
- ✅ `docs/todos/INTEGRATION-ROADMAP.md` - MVP yaklaşımı ve Future Enhancement notları eklendi
- ✅ `docs/plans/2025-01-28-INTEGRATION-ROADMAP-v1.0.md` - MVP yaklaşımı ve Future Enhancement notları eklendi
- ✅ `docs/plans/2025-01-28-INTEGRATION-TASKS.md` - Tüm task'lar MVP yaklaşımına göre güncellendi

---

**Son Güncelleme**: 2025-01-28  
**Durum**: ✅ **TAMAMLANDI** - Tüm tutarsızlıklar giderildi, dokümantasyon %100 tutarlı

