# Fresh Test Manual Guide - DB Reset & Bug Verification

**Tarih:** 2025-01-29  
**Amaç:** Database reset sonrası tüm bug fix'lerin doğru çalıştığını manuel olarak test etmek

---

## 🔄 Adım 1: Database Reset

### Seçenek A: Docker ile (Önerilen)

```bash
# 1. Docker container'ları durdur
docker-compose down

# 2. Database volume'u sil (tüm data silinir)
docker-compose down -v

# 3. Container'ları başlat
docker-compose up -d

# 4. Migration'ları çalıştır
docker-compose exec api alembic upgrade head
```

### Seçenek B: Manuel PostgreSQL

```bash
# 1. PostgreSQL'e bağlan
psql -U dyn365hunter -d dyn365hunter

# 2. Tüm tabloları sil
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO dyn365hunter;
GRANT ALL ON SCHEMA public TO public;

# 3. Çık
\q

# 4. Migration'ları çalıştır
python -m app.db.run_migration upgrade head
```

### Seçenek C: Python Script (Database bağlantısı varsa)

```bash
python scripts/reset_db_and_test.py
```

---

## 🧪 Adım 2: Test Domain'leri Ekle ve Tara

### Test Domain 1: dmkimya.com.tr (Google, P2)

```bash
# 1. Domain ekle
curl -X POST "http://localhost:8000/api/v1/ingest/domain" \
  -H "Content-Type: application/json" \
  -d '{"domain": "dmkimya.com.tr", "company_name": "DM Kimya Test"}'

# 2. Domain'i tara
curl -X POST "http://localhost:8000/api/v1/scan/domain" \
  -H "Content-Type: application/json" \
  -d '{"domain": "dmkimya.com.tr"}'

# 3. Sonuçları kontrol et
curl "http://localhost:8000/api/v1/leads/dmkimya.com.tr" | python -m json.tool
```

**Beklenen Sonuçlar:**
- ✅ `dmarc_coverage: null` (100 değil!)
- ✅ `dmarc_policy: null`
- ✅ `priority_category: "P2"`
- ✅ `priority_label: "Competitive Takeover"`
- ✅ `technical_heat: "Warm"`
- ✅ `commercial_segment: "COMPETITIVE"`
- ✅ `commercial_heat: "HIGH"`

---

## ✅ Adım 3: Bug Fix Verification

### Bug 1: DMARC Coverage Tutarlılığı

**Test:**
```bash
# Lead response
curl "http://localhost:8000/api/v1/leads/dmkimya.com.tr" | python -c "import sys, json; d=json.load(sys.stdin); print('Lead DMARC Coverage:', d.get('dmarc_coverage'))"

# Score breakdown
curl "http://localhost:8000/api/v1/leads/dmkimya.com.tr/score-breakdown" | python -c "import sys, json; d=json.load(sys.stdin); print('Breakdown DMARC Coverage:', d.get('dmarc_coverage'))"
```

**Beklenen:**
- ✅ Her ikisi de `null` olmalı (100 değil!)
- ✅ Tutarlı olmalı

### Bug 2: Risk Summary Metni

**Test:**
```bash
curl "http://localhost:8000/api/v1/leads/dmkimya.com.tr/sales-summary" | python -c "import sys, json; d=json.load(sys.stdin); sec=d.get('security_reasoning', {}); print('Risk Summary:', sec.get('summary', 'NOT_FOUND'))"
```

**Beklenen:**
- ✅ "DMARC yok. SPF ve DKIM mevcut, ancak DMARC eksik olduğu için spoofing riski hâlâ yüksek."
- ❌ "DMARC yok, SPF ve DKIM eksik" OLMAMALI

### Bug 3: Score Modal Açıklama

**Test:**
- Mini UI'da score breakdown modal'ını aç
- Açıklama cümlesini kontrol et

**Beklenen:**
- ✅ "Bu skor, Google Workspace kullanımı, DNS ve IP verilerine göre hesaplandı."
- ❌ "M365 kullanımı, Google Workspace" OLMAMALI

---

## 📋 Test Checklist

### ✅ DMARC Coverage
- [ ] Lead response: `dmarc_coverage: null`
- [ ] Score breakdown: `dmarc_coverage: null`
- [ ] İkisi tutarlı

### ✅ P-Model Fields
- [ ] `priority_category: "P2"`
- [ ] `priority_label: "Competitive Takeover"`
- [ ] `technical_heat: "Warm"`
- [ ] `commercial_segment: "COMPETITIVE"`
- [ ] `commercial_heat: "HIGH"`

### ✅ Risk Summary
- [ ] "SPF ve DKIM mevcut" diyor (eksik değil)
- [ ] DMARC eksikliği doğru açıklanıyor

### ✅ Score Modal
- [ ] Provider'a göre dinamik açıklama
- [ ] Google için "Google Workspace" yazıyor

### ✅ UI Badge'leri
- [ ] P2 badge görünüyor (kırmızı)
- [ ] Tooltip'te "Competitive Takeover" yazıyor

---

## 🔍 Detaylı Kontrol

### Score Breakdown Modal Kontrolü

1. Mini UI'da domain'e tıkla
2. Score'a tıkla (score breakdown modal açılır)
3. Kontrol et:
   - ✅ DMARC Coverage: Görünmemeli veya "N/A" (100% değil!)
   - ✅ CSP P-Model bölümü var
   - ✅ Priority Category: P2 badge
   - ✅ Açıklama cümlesi: "Google Workspace" yazıyor

### Sales Summary Kontrolü

1. Mini UI'da "📞 Sales" butonuna tıkla
2. Kontrol et:
   - ✅ Risk Özeti: "SPF ve DKIM mevcut" diyor
   - ✅ Teknik Durum: SPF ✅, DKIM ✅, DMARC ❌
   - ✅ Tutarlı

---

## 🐛 Eğer Bug Görürsen

### DMARC Coverage hala 100 ise:

1. **Cache temizle:**
   ```bash
   python scripts/invalidate_scoring_cache.py dmkimya.com.tr
   ```

2. **Rescan yap:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/scan/dmkimya.com.tr/rescan"
   ```

3. **Tekrar kontrol et**

### Risk Summary hala yanlış ise:

1. **API response'u kontrol et:**
   ```bash
   curl "http://localhost:8000/api/v1/leads/dmkimya.com.tr/sales-summary" | python -m json.tool
   ```

2. **SPF ve DKIM değerlerini kontrol et:**
   - `spf: true` olmalı
   - `dkim: true` olmalı

3. **Eğer doğruysa ama metin yanlışsa:** Backend'de `app/core/sales_engine.py` kontrol et

---

## 📊 Beklenen Sonuçlar (dmkimya.com.tr)

```json
{
  "domain": "dmkimya.com.tr",
  "provider": "Google",
  "segment": "Migration",
  "readiness_score": 70,
  "spf": true,
  "dkim": true,
  "dmarc_policy": null,
  "dmarc_coverage": null,  // ✅ null olmalı (100 değil!)
  "priority_category": "P2",
  "priority_label": "Competitive Takeover",
  "technical_heat": "Warm",
  "commercial_segment": "COMPETITIVE",
  "commercial_heat": "HIGH"
}
```

**Sales Summary Risk:**
```
"DMARC yok. SPF ve DKIM mevcut, ancak DMARC eksik olduğu için spoofing riski hâlâ yüksek."
```

**Score Modal Açıklama:**
```
"Bu skor, Google Workspace kullanımı, DNS ve IP verilerine göre hesaplandı."
```

---

## ✅ Başarı Kriterleri

Tüm testler geçtiyse:
- ✅ DMARC coverage tutarlı (null)
- ✅ Risk summary doğru metin
- ✅ Score modal provider'a göre dinamik
- ✅ P-Model alanları doğru
- ✅ UI badge'leri çalışıyor

**Sonuç:** Tüm bug'lar düzeltilmiş, sistem tutarlı çalışıyor! 🎉

