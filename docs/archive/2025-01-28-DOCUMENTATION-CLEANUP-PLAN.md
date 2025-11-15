# Dokümantasyon Temizleme Planı

**Tarih**: 2025-01-28  
**Durum**: ✅ **Kısmen Tamamlandı** - Bazı işler yapıldı, güncelleme gerekli  
**Sorun**: `docs/active/` klasöründe dosya birikimi, dokümantasyon yönetimi kurallarına göre temizlenmeli

---

## 📊 Mevcut Durum Analizi

### `docs/active/` Klasöründe Mevcut Dosyalar (Güncellenmiş):

| Dosya | Tip | Durum | Aksiyon |
|-------|-----|-------|---------|
| `DEVELOPMENT-ENVIRONMENT.md` | Reference Guide | ✅ Aktif | **KAL** |
| `DOCKER-TROUBLESHOOTING.md` | Reference Guide | ✅ Aktif | **KAL** |
| `DOCUMENTATION-CLEANUP-PLAN.md` | Plan | ✅ Aktif (güncellenmiş) | **KAL** |
| `DOMAIN-DATA-EXPANSION-CRITIQUE.md` | Critique | ✅ Aktif (yeni) | **KAL** |
| `G20-IMPLEMENTATION-SUMMARY.md` | Implementation Summary | ❌ G20 tamamlandı | **✅ ARCHIVE EDİLDİ** |
| `KALAN-ISLER-PRIORITY.md` | TODO/Backlog | ⚠️ Kısmen aktif | **GÜNCELLE** |
| `PRODUCTION-ENGINEERING-GUIDE-V1.md` | Reference Guide | ✅ Aktif | **KAL** |
| `SALES-PERSONA-CRITIQUE.md` | Critique | ✅ Aktif | **KAL** |
| `SALES-PERSONA-v2.0.md` | Persona | ✅ Aktif | **KAL** |
| `SALES-TRAINING.md` | Training Material | ✅ Aktif | **KAL** |
| `WSL-GUIDE.md` | Reference Guide | ✅ Aktif | **KAL** |

**Not**: G19 ile ilgili critique'ler zaten archive edilmiş (2025-01-28-*).

---

## 🎯 Sorun: Neden Birikti?

### 1. **Faz Tamamlandıktan Sonra Archive Edilmedi**
- G19 tamamlandı (2025-01-28)
- G19 ile ilgili critique'ler hala `active/` klasöründe
- Test raporları archive edilmedi

### 2. **Dokümantasyon Yönetimi Kuralları Uygulanmadı**
- Kurallar: "Phase complete → Archive TODO and phase documentation"
- Uygulanmadı: G19 critique'leri hala `active/` klasöründe

### 3. **Reference Guide vs Critique Ayrımı Yapılmadı**
- Reference guide'lar: Aktif kalmalı (DEVELOPMENT-ENVIRONMENT, DOCKER-TROUBLESHOOTING, vb.)
- Critique'ler: Faz tamamlandıktan sonra archive edilmeli

---

## ✅ Çözüm: Archive Planı

### ✅ Archive Edilenler (Zaten Yapıldı):

1. **`G19-PRIORITY-CRITIQUE.md`** ✅
   - **Durum**: Archive edildi → `docs/archive/2025-01-28-G19-PRIORITY-CRITIQUE.md`

2. **`PRODUCTION-READINESS-CRITIQUE-V2.md`** ✅
   - **Durum**: Archive edildi → `docs/archive/2025-01-28-PRODUCTION-READINESS-CRITIQUE-V2.md`

3. **`SATIS-EKIBI-TEST-RAPORU.md`** ✅
   - **Durum**: Archive edildi → `docs/archive/2025-01-28-SATIS-EKIBI-TEST-RAPORU.md`

4. **`G20-IMPLEMENTATION-SUMMARY.md`** ✅
   - **Durum**: Archive edildi → `docs/archive/2025-01-28-G20-IMPLEMENTATION-SUMMARY.md`

5. **Plan Dosyaları** ✅
   - `UI-PATCH-PLAN-v1.1.md` → `docs/archive/2025-01-28-UI-PATCH-PLAN-v1.1.md`
   - `G19-auth-ui-advanced-plan.md` → `docs/archive/2025-01-28-G19-auth-ui-advanced-plan.md`

6. **Eski Prompt Dosyaları** ✅
   - `2025-11-12-alembic-decision.md` → `docs/archive/2025-11-12-alembic-decision.md`
   - `2025-11-12-initial-setup.md` → `docs/archive/2025-11-12-initial-setup.md`
   - `2025-11-12-phase-completion-workflow.md` → `docs/archive/2025-11-12-phase-completion-workflow.md`

### Güncellenecekler (1 dosya):

4. **`KALAN-ISLER-PRIORITY.md`**
   - **Neden**: P0 maddeler tamamlandı, P1/P2 backlog'da
   - **Aksiyon**: P0 bölümünü "✅ Tamamlandı" olarak işaretle, P1/P2'yi güncelle
   - **Durum**: Aktif kalabilir (backlog takibi için)

### Aktif Kalacaklar (5 dosya):

5. **`DEVELOPMENT-ENVIRONMENT.md`** - Reference guide ✅
6. **`DOCKER-TROUBLESHOOTING.md`** - Reference guide ✅
7. **`DOMAIN-DATA-EXPANSION-CRITIQUE.md`** - Aktif tartışma ✅
8. **`PRODUCTION-ENGINEERING-GUIDE-V1.md`** - Reference guide ✅
9. **`WSL-GUIDE.md`** - Reference guide ✅

---

## 📋 Archive İşlemi

### Adım 1: Archive Edilecek Dosyaları Taşı

```bash
# G19 critique'ini archive et
mv docs/active/G19-PRIORITY-CRITIQUE.md docs/archive/2025-01-28-G19-PRIORITY-CRITIQUE.md

# Production readiness critique'ini archive et
mv docs/active/PRODUCTION-READINESS-CRITIQUE-V2.md docs/archive/2025-01-28-PRODUCTION-READINESS-CRITIQUE-V2.md

# Test raporunu archive et
mv docs/active/SATIS-EKIBI-TEST-RAPORU.md docs/archive/2025-01-28-SATIS-EKIBI-TEST-RAPORU.md
```

### Adım 2: KALAN-ISLER-PRIORITY.md'yi Güncelle

- P0 bölümünü "✅ Tamamlandı (G19)" olarak işaretle
- P1/P2 backlog'u güncelle
- Production Go/No-Go checklist'i güncelle

---

## 🎯 Sonuç: Hedef Durum

### `docs/active/` Klasöründe Kalacaklar (11 dosya - Güncellenmiş):

1. ✅ `DEVELOPMENT-ENVIRONMENT.md` - Reference guide
2. ✅ `DOCKER-TROUBLESHOOTING.md` - Reference guide
3. ✅ `DOCUMENTATION-CLEANUP-PLAN.md` - Plan (güncellenmiş)
4. ✅ `DOMAIN-DATA-EXPANSION-CRITIQUE.md` - Aktif tartışma
5. ✅ `KALAN-ISLER-PRIORITY.md` - Backlog takibi
6. ✅ `PRODUCTION-ENGINEERING-GUIDE-V1.md` - Reference guide
7. ✅ `SALES-PERSONA-CRITIQUE.md` - Critique (aktif)
8. ✅ `SALES-PERSONA-v2.0.md` - Persona (aktif)
9. ✅ `SALES-TRAINING.md` - Training material (aktif)
10. ✅ `WSL-GUIDE.md` - Reference guide

**Toplam**: 10 dosya (kurallara göre "Maximum 5-7 active files" - biraz fazla ama reference guide'lar ve aktif materyaller)

---

## 📝 Gelecek İçin Notlar

### Archive Kuralı:
- ✅ **Faz tamamlandıktan sonra**: Critique'leri ve test raporlarını archive et
- ✅ **Reference guide'lar**: Aktif kalabilir (sürekli kullanılıyor)
- ✅ **Tarih prefix**: Archive ederken `YYYY-MM-DD-` prefix ekle

### Aktif Klasörü Temiz Tut:
- ✅ **Maximum 5-7 dosya** (kurallara göre)
- ✅ **Sadece aktif faz dokümanları**
- ✅ **Reference guide'lar** (development, troubleshooting, vb.)

---

**Son Güncelleme**: 2025-01-28  
**Durum**: ✅ **Kısmen Tamamlandı** - G19/G20 planları ve critique'ler archive edildi, prompt dosyaları archive edildi.

**Not**: Kurallara göre `docs/active/` maksimum 5-7 dosya olmalı. Şu anda 10 dosya var. Birleştirme yapmak yerine, kurallara göre:
- Reference guide'lar aktif kalabilir (DEVELOPMENT-ENVIRONMENT, DOCKER-TROUBLESHOOTING, PRODUCTION-ENGINEERING-GUIDE, WSL-GUIDE)
- Feature documentation archive edilmeli (tamamlandıysa)
- Critique'ler archive edilmeli (karar verildikten sonra)
- Planning docs archive edilmeli (tamamlandıktan sonra)

**Öneri**: Bu plan dosyası da tamamlandıktan sonra archive edilmeli.

