# TODO: Post-MVP Sprint 1 - CSV Export + UI Mini

**Date Created**: 2025-01-28  
**Status**: In Progress  
**Phase**: G14 (Post-MVP Sprint 1)

---

## 🎯 Sprint Hedefi

Post-MVP'nin düşük riskli kısımlarını implement et: CSV Export ve UI Mini.

**Strateji**: Core'a dokunmayan, feedback gerektirmeyen özellikler.

---

## 📋 Tasks

### Sprint 0: Stabilizasyon (1-2 gün) ✅ COMPLETED

- [x] Log-level tuning (INFO → production uygun) - Config'de mevcut
- [x] Pydantic error mesajlarını düzeltme (daha açıklayıcı) - API endpoint'lerde iyileştirildi
- [x] WHOIS fallback hız ayarı (5s timeout kalibrasyonu) - Mevcut (WHOIS_TIMEOUT = 5)
- [x] DNS timeout kalibrasyonu (10s timeout) - Mevcut (DNS_TIMEOUT = 10)
- [x] `min_score` default davranışı kontrolü - Query parameter olarak çalışıyor
- [x] Providers/rules JSON final review - Mevcut ve çalışıyor
- [x] Kod kalitesi rötuşları (1-2 saat) - Error handling iyileştirildi

---

### Sprint 1: CSV Export (1 gün) ✅ COMPLETED

#### Backend Implementation

- [x] `app/api/leads.py` güncelle (export endpoint eklendi)
  - [x] `GET /leads/export` endpoint
  - [x] Filter parametreleri (segment, min_score, provider)
  - [x] CSV generation (pandas DataFrame → CSV)
  - [x] Excel generation (pandas DataFrame → xlsx)
  - [x] File download response (Content-Disposition header)
  - [x] Filename format (`leads_YYYY-MM-DD_HH-MM-SS.csv` / `.xlsx`)

- [x] `app/main.py` güncelle
  - [x] Export endpoint leads router'ında (route conflict düzeltildi)

- [x] `tests/test_export.py` oluştur
  - [x] Export with filters test
  - [x] Export empty result test
  - [x] Export large dataset test
  - [x] CSV format validation test
  - [x] Excel format validation test
  - [x] Filename format validation test
  - [x] Invalid format test
  - [x] Invalid min_score test

- [x] Documentation
  - [x] `README.md` - CSV Export endpoint documentation
  - [x] `CHANGELOG.md` - G14: CSV Export added

---

### Sprint 1: UI Mini (2-3 gün)

#### Frontend Implementation

- [ ] `app/static/` klasör yapısı oluştur
  - [ ] `app/static/index.html` - Ana sayfa
  - [ ] `app/static/css/style.css` - Stil dosyası
  - [ ] `app/static/js/app.js` - JavaScript logic

- [ ] File Upload Feature
  - [ ] File input (CSV, Excel)
  - [ ] Auto-detect columns checkbox
  - [ ] Upload button → `POST /ingest/csv`
  - [ ] Success/error feedback

- [ ] Domain Scan Feature
  - [ ] Domain input field
  - [ ] Company name (optional)
  - [ ] Scan button → `POST /scan/domain`
  - [ ] Progress indicator
  - [ ] Result display (score, segment, provider)

- [ ] Leads Table Feature
  - [ ] Segment filter dropdown
  - [ ] Min score slider/input
  - [ ] Provider filter dropdown
  - [ ] Table with sortable columns
  - [ ] Export CSV button → `GET /leads/export`
  - [ ] Pagination (optional, 50 per page)

- [ ] Dashboard Summary Feature
  - [ ] Total leads count
  - [ ] Segment distribution (pie chart or bars)
  - [ ] Average score
  - [ ] High priority count

- [ ] `app/main.py` güncelle
  - [ ] Static file serving (`app.mount("/static", ...)`)

- [ ] UI Testing
  - [ ] File upload test (CSV, Excel)
  - [ ] Domain scan test
  - [ ] Leads table filtering test
  - [ ] CSV export from UI test
  - [ ] Error handling test (invalid domain, network errors)
  - [ ] Browser compatibility test (Chrome, Firefox, Safari)
  - [ ] Responsive design test (mobile, tablet, desktop)

- [ ] Documentation
  - [ ] `docs/SALES-GUIDE.md` - UI Mini usage guide
  - [ ] `docs/SALES-SCENARIOS.md` - UI usage scenarios

---

## ✅ Acceptance Criteria

### CSV Export
- [ ] `GET /leads/export` endpoint çalışıyor
- [ ] Filter parametreleri (`segment`, `min_score`, `provider`) çalışıyor
- [ ] CSV format doğru (headers, encoding)
- [ ] Filename format doğru (`leads_YYYY-MM-DD_HH-MM-SS.csv`)
- [ ] Large dataset (1000+ leads) export edilebiliyor
- [ ] Tests passing (≥5 test cases)

### UI Mini
- [ ] File upload çalışıyor (CSV, Excel)
- [ ] Domain scan çalışıyor
- [ ] Leads table görüntüleniyor (filters, sorting)
- [ ] CSV export butonu çalışıyor
- [ ] Dashboard summary görüntüleniyor
- [ ] Responsive design (mobile-friendly)
- [ ] Error handling çalışıyor

---

## 📝 Notes

### Risk Mitigation

**CSV Export**:
- Large dataset memory issue → Streaming response, pagination option

**UI Mini**:
- Browser compatibility → Vanilla JS, no framework dependencies, polyfills if needed

### Success Metrics

**CSV Export**:
- Export success rate: ≥99%
- Export time for 1000 leads: ≤5 seconds
- User satisfaction: Positive feedback from sales team

**UI Mini**:
- Page load time: ≤2 seconds
- Feature usage: All features used within first week
- User satisfaction: Positive feedback from sales team

---

## 🔄 Next Steps (Feedback Sonrası)

- [ ] Sprint 2: Bulk Scan (1-2 hafta) - Async queue, progress tracking
- [ ] Sprint 3: Webhook Ingestion (1 hafta) - Authentication, rate limiting
- [ ] Sprint 4: Notes/Tags/Favorites (2 hafta) - Schema changes, CRUD endpoints

---

**Son Güncelleme**: 2025-01-28  
**Sprint 1 Başlangıç**: 2025-01-28  
**Sprint 1 Hedef Bitiş**: 2025-02-03 (1 hafta)

