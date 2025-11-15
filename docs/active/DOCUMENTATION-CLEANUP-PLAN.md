# Dokümantasyon Temizleme Planı

**Tarih**: 2025-01-28  
**Durum**: Active  
**Sorun**: `docs/active/` klasöründe 9 dosya birikmiş, dokümantasyon yönetimi kurallarına göre temizlenmeli

---

## 📊 Mevcut Durum Analizi

### `docs/active/` Klasöründe 9 Dosya:

| Dosya | Tip | Durum | Aksiyon |
|-------|-----|-------|---------|
| `DEVELOPMENT-ENVIRONMENT.md` | Reference Guide | ✅ Aktif | **KAL** |
| `DOCKER-TROUBLESHOOTING.md` | Reference Guide | ✅ Aktif | **KAL** |
| `DOMAIN-DATA-EXPANSION-CRITIQUE.md` | Critique | ✅ Aktif (yeni) | **KAL** |
| `G19-PRIORITY-CRITIQUE.md` | Critique | ❌ G19 tamamlandı | **ARCHIVE** |
| `KALAN-ISLER-PRIORITY.md` | TODO/Backlog | ⚠️ Kısmen aktif | **GÜNCELLE** |
| `PRODUCTION-ENGINEERING-GUIDE-V1.md` | Reference Guide | ✅ Aktif | **KAL** |
| `PRODUCTION-READINESS-CRITIQUE-V2.md` | Critique | ❌ G19 öncesi, G19 tamamlandı | **ARCHIVE** |
| `SATIS-EKIBI-TEST-RAPORU.md` | Test Raporu | ❌ G19 sonrası, tamamlandı | **ARCHIVE** |
| `WSL-GUIDE.md` | Reference Guide | ✅ Aktif | **KAL** |

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

### Archive Edilecekler (3 dosya):

1. **`G19-PRIORITY-CRITIQUE.md`**
   - **Neden**: G19 tamamlandı, critique artık aktif değil
   - **Yeni Ad**: `2025-01-28-G19-PRIORITY-CRITIQUE.md`
   - **Hedef**: `docs/archive/`

2. **`PRODUCTION-READINESS-CRITIQUE-V2.md`**
   - **Neden**: G19 öncesi critique, G19 tamamlandı, P0 maddeler tamamlandı
   - **Yeni Ad**: `2025-01-28-PRODUCTION-READINESS-CRITIQUE-V2.md`
   - **Hedef**: `docs/archive/`
   - **Not**: Production Engineering Guide v1 aktif kalmalı (reference guide)

3. **`SATIS-EKIBI-TEST-RAPORU.md`**
   - **Neden**: G19 sonrası test raporu, sorunlar çözüldü (P0/P1)
   - **Yeni Ad**: `2025-01-28-SATIS-EKIBI-TEST-RAPORU.md`
   - **Hedef**: `docs/archive/`

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

### `docs/active/` Klasöründe Kalacaklar (6 dosya):

1. ✅ `DEVELOPMENT-ENVIRONMENT.md` - Reference guide
2. ✅ `DOCKER-TROUBLESHOOTING.md` - Reference guide
3. ✅ `DOMAIN-DATA-EXPANSION-CRITIQUE.md` - Aktif tartışma
4. ✅ `KALAN-ISLER-PRIORITY.md` - Backlog takibi (güncellenecek)
5. ✅ `PRODUCTION-ENGINEERING-GUIDE-V1.md` - Reference guide
6. ✅ `WSL-GUIDE.md` - Reference guide

**Toplam**: 6 dosya (kurallara uygun: "Maximum 5-7 active files")

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
**Durum**: Archive işlemi yapılacak

