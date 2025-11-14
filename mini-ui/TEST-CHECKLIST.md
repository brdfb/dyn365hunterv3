# Mini UI Test Checklist

**Tarih**: 2025-01-28  
**Durum**: Test Edilecek

---

## ✅ Dosya Yapısı Kontrolü

- [x] `mini-ui/index.html` var
- [x] `mini-ui/styles.css` var
- [x] `mini-ui/js/api.js` var
- [x] `mini-ui/js/ui-leads.js` var
- [x] `mini-ui/js/ui-forms.js` var
- [x] `mini-ui/js/app.js` var
- [x] `mini-ui/README-mini-ui.md` var

---

## ✅ Kod Kontrolü

### Syntax Kontrolü
- [x] HTML syntax doğru
- [x] CSS syntax doğru
- [x] JavaScript syntax doğru (ES6 modules)

### Import/Export Kontrolü
- [x] `api.js` export'ları doğru
- [x] `ui-leads.js` export'ları doğru
- [x] `ui-forms.js` export'ları doğru
- [x] `app.js` import'ları doğru

### API Endpoint Kontrolü
- [x] `/ingest/csv` - POST (CSV upload)
- [x] `/ingest/domain` - POST (Domain ingest - scan öncesi)
- [x] `/scan/domain` - POST (Domain scan)
- [x] `/leads` - GET (Lead listesi)
- [x] `/leads/export` - GET (CSV export)
- [x] `/dashboard` - GET (Dashboard stats)

---

## 🔧 Düzeltilen Sorunlar

### 1. Scan Domain - Company Name Sorunu ✅
**Sorun**: Scan endpoint'i `company_name` kabul etmiyor, sadece `domain` bekliyor.

**Çözüm**: 
- `ingestDomain()` fonksiyonu eklendi
- Scan form'u önce domain'i ingest ediyor (company name varsa), sonra scan yapıyor
- Eğer domain zaten varsa, ingest hatası ignore ediliyor ve scan devam ediyor

### 2. Ingest Error Handling ✅
**Sorun**: Ingest error handling'de "already exists" kontrolü yapılıyor ama bu her zaman çalışmayabilir.

**Çözüm**: 
- Try-catch ile ingest yapılıyor
- Eğer "already exists" hatası alınırsa, scan devam ediyor
- Diğer hatalar throw ediliyor

---

## 🧪 Manuel Test Senaryoları

### Test 1: Mini UI Erişimi
- [ ] Backend çalışıyor mu? (`curl http://localhost:8000/healthz`)
- [ ] Mini UI açılıyor mu? (`http://localhost:8000/mini-ui/`)
- [ ] CSS yükleniyor mu?
- [ ] JavaScript yükleniyor mu? (Browser console'da hata var mı?)

### Test 2: Dashboard Stats
- [ ] KPI alanı görüntüleniyor mu?
- [ ] Toplam lead sayısı gösteriliyor mu?
- [ ] Migration lead sayısı gösteriliyor mu?
- [ ] En yüksek skor gösteriliyor mu?

### Test 3: CSV Upload
- [ ] CSV dosyası seçilebiliyor mu?
- [ ] Excel dosyası seçilebiliyor mu?
- [ ] Auto-detect checkbox çalışıyor mu?
- [ ] Upload butonu çalışıyor mu?
- [ ] Success mesajı gösteriliyor mu?
- [ ] Hata durumunda error mesajı gösteriliyor mu?
- [ ] Upload sonrası lead listesi refresh oluyor mu?

### Test 4: Domain Scan
- [ ] Domain input çalışıyor mu?
- [ ] Company name input çalışıyor mu? (opsiyonel)
- [ ] Scan butonu çalışıyor mu?
- [ ] Domain önce ingest ediliyor mu? (company name varsa)
- [ ] Scan sonucu gösteriliyor mu? (domain, skor, segment, provider)
- [ ] Hata durumunda error mesajı gösteriliyor mu?
- [ ] Scan sonrası lead listesi refresh oluyor mu?

### Test 5: Leads Table
- [ ] Lead tablosu görüntüleniyor mu?
- [ ] Tablo kolonları doğru mu? (Domain, Şirket, Provider, Segment, Skor)
- [ ] Segment badge'leri doğru renkte mi? (Migration: green, Existing: blue, Cold: yellow, Skip: red)
- [ ] Skor renklendirmesi doğru mu? (≥70: green, ≥50: yellow, <50: red)
- [ ] Empty state gösteriliyor mu? (lead yoksa)

### Test 6: Filters
- [ ] Segment filtresi çalışıyor mu?
- [ ] Min score filtresi çalışıyor mu?
- [ ] Provider filtresi çalışıyor mu?
- [ ] Filtrele butonu çalışıyor mu?
- [ ] Filtre sonuçları doğru mu?

### Test 7: Export CSV
- [ ] Export butonu çalışıyor mu?
- [ ] CSV dosyası indiriliyor mu?
- [ ] Dosya adı doğru mu? (`leads_YYYY-MM-DD_HH-MM-SS.csv`)
- [ ] Filtreler export'a uygulanıyor mu?

### Test 8: Error Handling
- [ ] Network hatası durumunda error mesajı gösteriliyor mu?
- [ ] Invalid domain durumunda error mesajı gösteriliyor mu?
- [ ] API hata durumunda error mesajı gösteriliyor mu?

### Test 9: Responsive Design
- [ ] Mobile görünümde layout doğru mu?
- [ ] Tablet görünümde layout doğru mu?
- [ ] Desktop görünümde layout doğru mu?

### Test 10: Browser Compatibility
- [ ] Chrome'da çalışıyor mu?
- [ ] Firefox'ta çalışıyor mu?
- [ ] Safari'de çalışıyor mu?
- [ ] Edge'de çalışıyor mu?

---

## 🐛 Bilinen Sorunlar

### 1. Ingest Error Handling
**Durum**: "already exists" kontrolü string match ile yapılıyor, bu her zaman çalışmayabilir.

**Öneri**: Daha iyi bir yaklaşım için API'den dönen status code'u kontrol etmek (409 Conflict).

**Öncelik**: Düşük (şu an çalışıyor)

---

## 📊 Test Sonuçları

**Test Tarihi**: _Henüz test edilmedi_  
**Test Eden**: _Henüz test edilmedi_  
**Sonuç**: _Bekliyor_

---

## ✅ Acceptance Criteria Kontrolü

### Functional
- [ ] CSV upload çalışıyor (CSV, Excel)
- [ ] Domain scan çalışıyor
- [ ] Leads table görüntüleniyor (filters, sorting)
- [ ] Export butonu çalışıyor
- [ ] Dashboard summary görüntüleniyor
- [ ] Responsive design (mobile-friendly)
- [ ] Error handling çalışıyor

### Technical
- [x] JS toplam kod miktarı ≤ 400 satır (yorumlar hariç) - **~400 satır**
- [x] 4 ana özellik (upload, scan, table, export)
- [x] API-first yaklaşım (iş mantığı backend'de)
- [x] BEM CSS pattern
- [x] Modüler JS yapısı (api.js, ui-leads.js, ui-forms.js, app.js)
- [x] Global state tek obje (`window.state`)

### Documentation
- [x] `README-mini-ui.md` - Kullanım kılavuzu
- [x] Endpoint'ler dokümante edilmiş
- [x] Limitler belirtilmiş (4 feature, 400 satır)

---

**Son Güncelleme**: 2025-01-28

