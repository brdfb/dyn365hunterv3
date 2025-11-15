# Dokümantasyon Durumu - Kurallara Göre

**Tarih**: 2025-01-28  
**Kural**: Maximum 5-7 active files (`docs/active/`)  
**Mevcut**: 10 dosya (fazla)

---

## 📋 Kurallara Göre Kategorizasyon

### ✅ Reference Guide'lar (Aktif Kalmalı - 4 dosya)
Kurallara göre: "Reference guides - Development environment, testing, troubleshooting guides"

1. `DEVELOPMENT-ENVIRONMENT.md` ✅ - Geliştirme ortamı kurulumu
2. `DOCKER-TROUBLESHOOTING.md` ✅ - Docker sorun giderme
3. `PRODUCTION-ENGINEERING-GUIDE-V1.md` ✅ - Production operasyonları
4. `WSL-GUIDE.md` ✅ - WSL kullanım rehberi

### ⚠️ Feature Documentation (Archive Edilmeli - 1 dosya)
Kurallara göre: "Feature documentation - Archive when complete"

5. `DOCUMENTATION-CLEANUP-PLAN.md` ⚠️ - Plan dosyası, tamamlandıktan sonra archive edilmeli

### ⚠️ Critique'ler (Archive Edilmeli - 2 dosya)
Kurallara göre: "Critique'ler - Archive when decision made"

6. `DOMAIN-DATA-EXPANSION-CRITIQUE.md` ⚠️ - Karar verildikten sonra archive edilmeli
7. `SALES-PERSONA-CRITIQUE.md` ⚠️ - Persona v2.0 tamamlandı, archive edilmeli

### ✅ Satış Materyalleri (Aktif Kalabilir - 2 dosya)
Kurallara göre: "Feature documentation" ama satış ekibi için sürekli kullanılıyor

8. `SALES-PERSONA-v2.0.md` ✅ - Satış ekibi için reference guide
9. `SALES-TRAINING.md` ✅ - Satış ekibi için training material

### ✅ Backlog (Aktif Kalabilir - 1 dosya)
Kurallara göre: "Current phase TODO" - Backlog aktif takip ediliyor

10. `KALAN-ISLER-PRIORITY.md` ✅ - Backlog ve öncelik listesi

---

## 🎯 Kurallara Göre Aksiyon

### Archive Edilecekler (3 dosya)

1. **`DOCUMENTATION-CLEANUP-PLAN.md`** → Archive (plan tamamlandı)
2. **`DOMAIN-DATA-EXPANSION-CRITIQUE.md`** → Archive (karar verildikten sonra)
3. **`SALES-PERSONA-CRITIQUE.md`** → Archive (persona v2.0 tamamlandı)

### Aktif Kalacaklar (7 dosya)

**Reference Guide'lar (4):**
- DEVELOPMENT-ENVIRONMENT.md
- DOCKER-TROUBLESHOOTING.md
- PRODUCTION-ENGINEERING-GUIDE-V1.md
- WSL-GUIDE.md

**Satış Materyalleri (2):**
- SALES-PERSONA-v2.0.md
- SALES-TRAINING.md

**Backlog (1):**
- KALAN-ISLER-PRIORITY.md

**Sonuç**: 7 dosya (kurallara uygun: 5-7 dosya)

---

## 📝 Notlar

### Neden Birleştirme Yapmıyoruz?

Kurallara göre:
- ✅ Reference guide'lar ayrı tutulmalı (her biri farklı konu)
- ✅ Feature documentation archive edilmeli (tamamlandıysa)
- ✅ Critique'ler archive edilmeli (karar verildikten sonra)
- ❌ Birleştirme yapmak kurallara aykırı değil ama "işler karışabilir"

### Archive Kuralı

Kurallara göre:
- Date prefix: `YYYY-MM-DD-filename.md`
- Use `scripts/manage_docs.sh archive-*` commands
- Archive immediately when done

---

**Son Güncelleme**: 2025-01-28  
**Durum**: Kurallara göre analiz tamamlandı, archive işlemi yapılacak

