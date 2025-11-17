# Manuel UI Kontrol Checklist (2025-01-29)

**Tarih:** 2025-01-29  
**Amaç:** Production öncesi Mini UI manuel kontrolü

---

## 🎯 Test Domain'leri

1. **gibibyte.com.tr** (Existing / RENEWAL / P4)
   - Expected: P4 badge (orange), "Renewal Pressure" tooltip
   
2. **dmkimya.com.tr** (Migration / COMPETITIVE / P2)
   - Expected: P2 badge (red), "Competitive Takeover" tooltip

---

## ✅ Lead Listesi Kontrolü

### P-Badge Kontrolü

**gibibyte.com.tr:**
- [ ] P4 badge görünüyor mu? (turuncu/sarı renk)
- [ ] Badge'de "P4" yazıyor mu?
- [ ] Tooltip'te "Renewal Pressure" yazıyor mu?

**dmkimya.com.tr:**
- [ ] P2 badge görünüyor mu? (kırmızı renk)
- [ ] Badge'de "P2" yazıyor mu?
- [ ] Tooltip'te "Competitive Takeover" yazıyor mu?

**Beklenen Badge Renkleri:**
- P1: Yeşil (#27ae60)
- P2: Kırmızı (#e74c3c)
- P3: Mavi (#3498db)
- P4: Turuncu (#f39c12)
- P5: Sarı (#f1c40f)
- P6: Gri (#95a5a6)

---

## ✅ Score Modal Kontrolü

### 1. Modal Açılışı

**Her iki domain için:**
- [ ] Lead listesinde skor'a tıklayınca modal açılıyor mu?
- [ ] Domain adı doğru görünüyor mu?

### 2. Provider-Specific Açıklama

**gibibyte.com.tr (M365):**
- [ ] Açıklama: "Bu skor, M365 kullanımı, DNS ve IP verilerine göre hesaplandı." yazıyor mu?
- [ ] "Google Workspace" yazmıyor mu?

**dmkimya.com.tr (Google):**
- [ ] Açıklama: "Bu skor, Google Workspace kullanımı, DNS ve IP verilerine göre hesaplandı." yazıyor mu?
- [ ] "M365 kullanımı" yazmıyor mu?

### 3. CSP P-Model (Phase 3) Bloğu

**Her iki domain için:**
- [ ] "CSP P-Model (Phase 3)" başlığı görünüyor mu?
- [ ] Technical Heat değeri görünüyor mu?
  - gibibyte.com.tr → "Hot"
  - dmkimya.com.tr → "Warm"
- [ ] Commercial Segment değeri görünüyor mu?
  - gibibyte.com.tr → "RENEWAL"
  - dmkimya.com.tr → "COMPETITIVE"
- [ ] Commercial Heat değeri görünüyor mu?
  - gibibyte.com.tr → "MEDIUM"
  - dmkimya.com.tr → "HIGH"
- [ ] Priority Category badge görünüyor mu?
  - gibibyte.com.tr → P4 badge (turuncu)
  - dmkimya.com.tr → P2 badge (kırmızı)
- [ ] Priority Label görünüyor mu?
  - gibibyte.com.tr → "Renewal Pressure"
  - dmkimya.com.tr → "Competitive Takeover"

### 4. DMARC Coverage Kontrolü

**Her iki domain için (DMARC yok):**
- [ ] DMARC Coverage görünmüyor mu? (veya "N/A" / "-" gösteriyor mu?)
- [ ] "100%" yazmıyor mu? (BUG: Eğer 100% görüyorsanız, cache temizlenmeli)

---

## ✅ Sales Summary Modal Kontrolü

### 1. Segment Uyumu

**gibibyte.com.tr:**
- [ ] Segment: "Existing" görünüyor mu?
- [ ] P-Model Commercial Segment: "RENEWAL" ile uyumlu mu?

**dmkimya.com.tr:**
- [ ] Segment: "Migration" görünüyor mu?
- [ ] P-Model Commercial Segment: "COMPETITIVE" ile uyumlu mu?

### 2. Risk Metni Kontrolü

**Her iki domain için (SPF + DKIM var, DMARC yok):**
- [ ] Risk Özeti: "DMARC yok. SPF ve DKIM mevcut, ancak DMARC eksik olduğu için spoofing riski hâlâ yüksek." yazıyor mu?
- [ ] "SPF ve DKIM eksik" yazmıyor mu? (BUG: Eğer "eksik" yazıyorsa, backend'de bug var)

### 3. Teknik Durum Kontrolü

**Her iki domain için:**
- [ ] SPF kaydı mevcut ✅
- [ ] DKIM kaydı mevcut ✅
- [ ] DMARC politikası yok ❌
- [ ] Risk Özeti ile Teknik Durum tutarlı mı?

### 4. Opportunity Potential

**gibibyte.com.tr:**
- [ ] Opportunity Potential: ~73 civarı mı? (70-80 arası makul)

**dmkimya.com.tr:**
- [ ] Opportunity Potential: ~89 civarı mı? (80-95 arası makul)

---

## 🐛 Bug Kontrolü

### Eğer Bug Görürseniz:

**1. DMARC Coverage 100% görünüyorsa:**
```bash
# Cache temizle
python scripts/invalidate_scoring_cache.py dmkimya.com.tr
python scripts/invalidate_scoring_cache.py gibibyte.com.tr

# Rescan yap
curl -X POST "http://localhost:8000/api/v1/scan/dmkimya.com.tr/rescan"
curl -X POST "http://localhost:8000/api/v1/scan/gibibyte.com.tr/rescan"
```

**2. Risk metni "SPF ve DKIM eksik" diyorsa:**
- Backend'de `app/core/sales_engine.py` kontrol et
- API response'u kontrol et: `curl http://localhost:8000/api/v1/leads/{domain}/sales-summary`

**3. P-badge görünmüyorsa:**
- Browser console'da hata var mı kontrol et
- API response'da `priority_category` var mı kontrol et: `curl http://localhost:8000/api/v1/leads/{domain}`

---

## ✅ Kontrol Sonucu

**Tüm kontroller geçtiyse:**
- ✅ Lead listesi: P-badge ve tooltip çalışıyor
- ✅ Score modal: P-Model bloğu dolu, provider-specific açıklama doğru
- ✅ Sales Summary: Risk metni doğru, segment uyumlu, opportunity potential mantıklı

**Status:** ✅ **Production Ready**

---

## 📝 Notlar

- Tüm kontrolleri yaptıktan sonra sonuçları buraya not edin
- Bug görürseniz yukarıdaki "Bug Kontrolü" bölümünü takip edin
- Production deployment'a geçmeden önce tüm kontrollerin geçtiğinden emin olun

