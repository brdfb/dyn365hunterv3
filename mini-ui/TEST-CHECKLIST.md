# Mini UI Test Checklist

**Tarih**: 2025-01-29  
**Durum**: Test Edilecek (Phase 3: CSP P-Model Integration eklendi)

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
- [x] `/leads/export` - GET (CSV/Excel export) - Gün 3
- [x] `/leads/{domain}/summary.pdf` - GET (PDF export) - Gün 3
- [x] `/leads/{domain}/score-breakdown` - GET (Score breakdown) - G19
- [x] `/dashboard` - GET (Dashboard stats)
- [x] `/dashboard/kpis` - GET (Dashboard KPIs) - G19

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
- [ ] Backend çalışıyor mu? (`curl http://localhost:8000/healthz` veya `curl http://localhost:8000/healthz/ready`)
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
- [ ] Tablo kolonları doğru mu? (Öncelik, Domain, Şirket, Provider, Tenant Size, Local Provider, Segment, Skor)
- [ ] Column widths optimize edilmiş mi? (domain, provider, score, segment, priority)
- [ ] Row hover effect çalışıyor mu? (smooth transition)
- [ ] Segment badge'leri doğru renkte mi? (Migration: green, Existing: blue, Cold: yellow, Skip: red)
- [ ] Skor renklendirmesi doğru mu? (≥70: green, ≥50: yellow, <50: red)
- [ ] Öncelik badge'leri görüntüleniyor mu? (P1-P6 renkli badge'ler veya fallback emoji badge'ler)
- [ ] P-Model priority_category badge'leri doğru renkte mi? (P1: green, P2: red, P3: blue, P4: orange, P5: yellow, P6: gray)
- [ ] Priority tooltip'leri görüntüleniyor mu? (priority_label veya fallback tooltip)
- [ ] Empty state gösteriliyor mu? (lead yoksa + CTA button)
- [ ] Loading state spinner görüntüleniyor mu? (lead'ler yüklenirken)

### Test 6: Filters
- [ ] Segment filtresi çalışıyor mu?
- [ ] Min score filtresi çalışıyor mu?
- [ ] Provider filtresi çalışıyor mu?
- [ ] Filtrele butonu çalışıyor mu?
- [ ] Filtre sonuçları doğru mu?

### Test 6.1: Search (G19)
- [ ] Search input görüntüleniyor mu?
- [ ] Search input'a yazı yazılabiliyor mu?
- [ ] Debounce çalışıyor mu? (500ms sonra arama yapılıyor mu?)
- [ ] Search sonuçları doğru mu?
- [ ] Search temizlenince tüm lead'ler görüntüleniyor mu?

### Test 6.2: Sorting (G19)
- [ ] Table header'lar tıklanabilir mi? (Öncelik, Domain, Provider, Segment, Skor)
- [ ] Header'a tıklayınca sıralama değişiyor mu?
- [ ] Aynı header'a tekrar tıklayınca sıralama yönü değişiyor mu? (asc ↔ desc)
- [ ] Sort icon'ları görüntüleniyor mu? (▲/▼)
- [ ] Aktif sıralama icon ile gösteriliyor mu?

### Test 6.3: Pagination (G19)
- [ ] Pagination UI görüntüleniyor mu? (50+ lead varsa)
- [ ] Sayfa numaraları görüntüleniyor mu?
- [ ] Önceki/Sonraki butonları çalışıyor mu?
- [ ] Sayfa bilgisi gösteriliyor mu? (örn: "1-50 / 150")
- [ ] Sayfa numarasına tıklayınca sayfa değişiyor mu?
- [ ] İlk sayfada "Önceki" butonu disabled mı?
- [ ] Son sayfada "Sonraki" butonu disabled mı?
- [ ] Tek sayfa veya sonuç yoksa pagination gizleniyor mu?

### Test 7: Export CSV/Excel/PDF (Gün 3)
- [ ] Export CSV butonu çalışıyor mu?
- [ ] Export Excel butonu çalışıyor mu?
- [ ] CSV dosyası indiriliyor mu?
- [ ] Excel dosyası indiriliyor mu?
- [ ] Dosya adı doğru mu? (`leads_YYYY-MM-DD_HH-MM-SS.csv` veya `.xlsx`)
- [ ] Filtreler export'a uygulanıyor mu?
- [ ] Toast notification gösteriliyor mu? (export başarı/hata)
- [ ] PDF export butonu score breakdown modal'da görüntüleniyor mu?
- [ ] PDF export çalışıyor mu? (new tab'de açılıyor mu?)

### Test 7.1: Score Breakdown Modal (G19 + Gün 3 + Phase 3)
- [ ] Skor'a tıklayınca modal açılıyor mu?
- [ ] Modal close button (X) çalışıyor mu?
- [ ] ESC key ile modal kapanıyor mu?
- [ ] Backdrop'a tıklayınca modal kapanıyor mu? (sadece overlay'e tıklayınca)
- [ ] Modal scroll çalışıyor mu? (uzun içerik için)
- [ ] Score breakdown tooltip'leri görüntüleniyor mu? (signal/risk hover'da)
- [ ] PDF export butonu modal'da görüntüleniyor mu?
- [ ] Domain taranmamışsa hata mesajı gösteriliyor mu?
- [ ] **Provider-specific açıklama cümlesi** doğru mu? (M365 → "M365 kullanımı...", Google → "Google Workspace kullanımı...", Local/Hosting → "mevcut email sağlayıcınız...", Unknown → "DNS ve IP verilerine göre...")
- [ ] **DMARC Coverage** null/undefined durumunda gösterilmiyor mu? (DMARC yoksa gösterilmemeli)
- [ ] **CSP P-Model Panel** görüntüleniyor mu? (technical_heat, commercial_segment, commercial_heat, priority_category, priority_label)
- [ ] **Priority Category badge** score breakdown panel'de doğru renkte mi? (P1-P6)
- [ ] **Eski lead'lerde** P-Model alanları yoksa gracefully handle ediliyor mu? (panel gösterilmiyor veya "-" gösteriliyor)

### Test 8: Error Handling
- [ ] Network hatası durumunda error mesajı gösteriliyor mu?
- [ ] Invalid domain durumunda error mesajı gösteriliyor mu?
- [ ] API hata durumunda error mesajı gösteriliyor mu?
- [ ] Toast notification hata mesajları gösteriliyor mu? (Gün 3)

### Test 9: UI Improvements (Gün 3)
- [ ] Header title kompakt mı? ("Dyn365Hunter")
- [ ] Footer görüntüleniyor mu? (version info, Docs/Support links)
- [ ] Footer responsive mi? (mobile'de dikey layout)
- [ ] Tooltip'ler çalışıyor mu? (score breakdown modal'da signal/risk tooltips)
- [ ] Hover effects çalışıyor mu? (button scale, badge opacity, row highlight)
- [ ] Toast notifications çalışıyor mu? (export başarı/hata)

### Test 10: Responsive Design
- [ ] Mobile görünümde layout doğru mu?
- [ ] Tablet görünümde layout doğru mu?
- [ ] Desktop görünümde layout doğru mu?
- [ ] Column widths responsive mi? (mobile'de scroll)

### Test 11: Browser Compatibility
- [ ] Chrome'da çalışıyor mu?
- [ ] Firefox'ta çalışıyor mu?
- [ ] Safari'de çalışıyor mu?
- [ ] Edge'de çalışıyor mu?
- [ ] Modern CSS features çalışıyor mu? (backdrop-filter, transform, transition)

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
- [ ] Leads table görüntüleniyor (filters, sorting, pagination, search)
- [ ] Search çalışıyor (debounce ile)
- [ ] Sorting çalışıyor (table headers clickable)
- [ ] Pagination çalışıyor (page numbers, prev/next, page info)
- [ ] Export butonları çalışıyor (CSV, Excel, PDF)
- [ ] Score breakdown modal çalışıyor (ESC key, backdrop click, tooltips)
- [ ] **P-Model badges** görüntüleniyor (P1-P6 renkli badge'ler, tooltip'ler)
- [ ] **CSP P-Model panel** score breakdown modal'da görüntüleniyor
- [ ] **Provider-specific description** score breakdown modal'da doğru
- [ ] **DMARC coverage** null/undefined durumunda gracefully handle ediliyor
- [ ] Toast notifications çalışıyor (export başarı/hata)
- [ ] Dashboard summary görüntüleniyor
- [ ] Responsive design (mobile-friendly)
- [ ] Error handling çalışıyor

### Technical
- [x] JS toplam kod miktarı ~1400-1500 satır (yorumlar hariç) - **G19 + Gün 3 + Phase 3 ile artış: ~900 satır**
- [x] 12+ ana özellik (upload, scan, table, export CSV/Excel/PDF, search, sorting, pagination, score breakdown modal, toast notifications, tooltips, P-Model badges, CSP P-Model panel)
- [x] API-first yaklaşım (iş mantığı backend'de)
- [x] BEM CSS pattern
- [x] Modüler JS yapısı (api.js, ui-leads.js, ui-forms.js, app.js)
- [x] Global state tek obje (`window.state`)
- [x] Generic tooltip system (CSS-based)
- [x] Toast notification system

### Documentation
- [x] `README-mini-ui.md` - Kullanım kılavuzu (G19 + Gün 3 + Phase 3 özellikleri eklendi)
- [x] Endpoint'ler dokümante edilmiş (G19 query params + Gün 3 PDF export eklendi)
- [x] Limitler belirtilmiş (12+ feature, ~1400-1500 satır)

---

**Son Güncelleme**: 2025-01-29 (G19: Search, Sorting, Pagination | Gün 3: UI Stabilizasyon test senaryoları eklendi | Phase 3: CSP P-Model Integration test senaryoları eklendi - P-badges, tooltips, score breakdown panel, provider-specific descriptions, DMARC coverage handling | İyileştirmeler: Production-safe logging, improved error handling)

