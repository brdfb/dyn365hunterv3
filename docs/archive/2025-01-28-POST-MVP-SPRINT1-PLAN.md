# Post-MVP Sprint 1 Plan - Düşük Riskli Modüller

**Tarih**: 2025-01-28  
**Durum**: In Progress  
**Kapsam**: CSV Export + UI Mini (Düşük Riskli Post-MVP Modülleri)

---

## 🎯 Stratejik Karar

**Karar**: Post-MVP'nin düşük riskli kısımlarını hemen yapıyoruz, yüksek riskli kısımlarını feedback sonrası yapıyoruz.

**Gerekçe**:
- CSV Export ve UI Mini core'a dokunmuyor
- Feedback gerektirmiyor (satış ekibi zaten istiyor)
- Momentum korunuyor, double-work riski yok

---

## 📊 Karar Matrisi

| Modül | Etki | Risk | Core'a Dokunur? | Feedback Şart? | Ne Zaman? |
|-------|------|------|-----------------|----------------|-----------|
| **CSV Export** | ⭐⭐⭐ Çok Yüksek | 🟢 Çok Düşük | ❌ | ❌ | **Hemen** |
| **UI Mini** | ⭐⭐ Orta | 🟢 Düşük | ❌ | ❌ | **Hemen** |
| **Dashboard/Leads Table** | ⭐⭐ Orta | 🟢 Düşük | ❌ | ❌ | **Hemen** |
| **Bulk Scan (async)** | ⭐⭐⭐ Çok Yüksek | 🔴 Çok Yüksek | ✅ | ✅ | **Sonra** |
| **Webhook ingestion** | ⭐⭐ Orta | 🟡 Orta | ✅ | ✅ | **Sonra** |
| **Notes/Tags** | ⭐⭐ Orta | 🟡 Orta | ✅ (schema) | ✅ | **Sonra** |
| **Favorites/Reminders** | ⭐⭐ Orta | 🟡 Orta | ✅ | ✅ | **Sonra** |

---

## 🚀 Sprint 0: Stabilizasyon (Bugün-Yarın)

### Hedef
MVP'yi production-ready hale getir, küçük rötuşlar yap.

### İşler
- [ ] Log-level tuning (INFO → production uygun)
- [ ] Pydantic error mesajlarını düzeltme (daha açıklayıcı)
- [ ] WHOIS fallback hız ayarı (5s timeout kalibrasyonu)
- [ ] DNS timeout kalibrasyonu (10s timeout)
- [ ] `min_score` default davranışı kontrolü
- [ ] Providers/rules JSON final review
- [ ] Kod kalitesi rötuşları (1-2 saat)

### Süre
**1-2 gün** (paralel yapılabilir)

### Çıktı
- MVP stabil ve production-ready
- Post-MVP geliştirmeye hazır

---

## 🎯 Sprint 1: CSV Export + UI Mini (Bu Hafta)

### Hedef
Satış ekibinin en çok istediği iki özelliği ekle: CSV Export ve basit UI.

---

### 1. CSV Export (1 gün)

#### Backend Implementation

**Endpoint**: `GET /leads/export`

**Query Parameters**:
- `segment` (optional): Filter by segment (Migration, Existing, Cold, Skip)
- `min_score` (optional): Minimum readiness score (0-100)
- `provider` (optional): Filter by provider (M365, Google, etc.)
- `format` (optional): Export format (`csv` default, future: `xlsx`)

**Response**:
- Content-Type: `text/csv; charset=utf-8`
- Content-Disposition: `attachment; filename=leads_YYYY-MM-DD_HH-MM-SS.csv`
- CSV headers: domain, company_name, provider, segment, readiness_score, priority_score, spf, dkim, dmarc_policy, mx_root, scanned_at

**Implementation**:
```python
# app/api/export.py
@router.get("/leads/export")
async def export_leads(
    segment: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None),
    provider: Optional[str] = Query(None),
    format: str = Query("csv", regex="^(csv|xlsx)$"),
    db: Session = Depends(get_db)
):
    # Reuse existing GET /leads logic
    leads = await get_leads(segment, min_score, provider, db)
    
    # Convert to DataFrame
    df = pd.DataFrame([lead.dict() for lead in leads])
    
    # Generate CSV
    csv_content = df.to_csv(index=False)
    
    # Return as file download
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=leads_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        }
    )
```

**Dosyalar**:
- `app/api/export.py` - Export endpoint
- `app/main.py` - Router registration
- `tests/test_export.py` - Export tests

**Test Cases**:
- Export with filters (segment, min_score, provider)
- Export empty result
- Export large dataset (1000+ leads)
- CSV format validation
- Filename format validation

**Süre**: **1 gün**

**Risk**: 🟢 Çok Düşük (core'a dokunmuyor, mevcut `/leads` logic'i kullanıyor)

---

### 2. UI Mini (2-3 gün)

#### Frontend Implementation

**Teknoloji**: HTML + Vanilla JavaScript + CSS (No framework)

**Dosya Yapısı**:
```
mini-ui/
├── index.html          # Ana sayfa
├── styles.css          # CSS (BEM pattern)
├── js/
│   ├── app.js         # Orchestration, global state
│   ├── api.js         # API client (fetch calls)
│   ├── ui-leads.js    # Table & filter rendering
│   └── ui-forms.js    # Form binding
└── README-mini-ui.md  # Kullanım kılavuzu
```

**Özellikler**:

1. **File Upload** (CSV/Excel ingestion)
   - File input
   - Auto-detect columns checkbox
   - Upload button → `POST /ingest/csv`
   - Success/error feedback

2. **Domain Scan** (Single domain analysis)
   - Domain input field
   - Company name (optional)
   - Scan button → `POST /scan/domain`
   - Progress indicator
   - Result display (score, segment, provider)

3. **Leads Table** (Filtered lead list)
   - Segment filter dropdown
   - Min score slider/input
   - Provider filter dropdown
   - Table with sortable columns
   - Export CSV button → `GET /leads/export`
   - Pagination (optional, 50 per page)

4. **Dashboard Summary** (Quick stats)
   - Total leads count
   - Segment distribution (pie chart or bars)
   - Average score
   - High priority count

**UI Tasarım**:
- Minimal, modern, responsive
- FastAPI Swagger UI benzeri stil
- Color coding: Migration (green), Existing (blue), Cold (yellow), Skip (red)

**Dosyalar**:
- `mini-ui/index.html` - Ana sayfa
- `mini-ui/styles.css` - Stil dosyası (BEM pattern)
- `mini-ui/js/app.js` - Orchestration, global state
- `mini-ui/js/api.js` - API client (tüm fetch çağrıları)
- `mini-ui/js/ui-leads.js` - Table & filter rendering
- `mini-ui/js/ui-forms.js` - Form binding
- `app/main.py` - Static file serving (`app.mount("/mini-ui", StaticFiles(directory="mini-ui", html=True), name="mini-ui")`)

**Test Cases**:
- File upload (CSV, Excel)
- Domain scan
- Leads table filtering
- CSV export from UI
- Error handling (invalid domain, network errors)

**Süre**: **2-3 gün** ✅ **Tamamlandı (1 gün)**

**Risk**: 🟢 Düşük (read-only UI, core'a dokunmuyor)

**Not**: Implementation tamamlandı. Dosya yapısı `mini-ui/` olarak oluşturuldu (planlanan `app/static/` yerine). Modüler JS yapısı kullanıldı (4 dosya: app.js, api.js, ui-leads.js, ui-forms.js). Scan form'u otomatik ingest yapıyor (company name varsa).

---

### Sprint 1 Toplam Süre
**3-4 gün** (1 hafta)

---

## 📋 Sonraki Sprintler (Feedback Sonrası)

### Sprint 2: Bulk Scan (1-2 hafta)
- Async queue (Redis/Celery)
- Progress tracking
- Rate-limit strategy
- Timeout handling
- **Risk**: 🔴 Çok Yüksek (core'a dokunuyor, feedback gerekli)

### Sprint 3: Webhook Ingestion (1 hafta)
- Webhook endpoint
- Authentication
- Rate limiting
- **Risk**: 🟡 Orta (ingestion logic'e dokunuyor)

### Sprint 4: Notes/Tags/Favorites (2 hafta)
- Database schema changes
- CRUD endpoints
- Auth integration
- **Risk**: 🟡 Orta (schema değişikliği)

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

## 🧪 Testing Strategy

### CSV Export
- Unit tests: Export logic
- Integration tests: Endpoint + filters
- Edge cases: Empty result, large dataset, invalid filters

### UI Mini
- Manual testing: All features
- Browser testing: Chrome, Firefox, Safari
- Responsive testing: Mobile, tablet, desktop
- Error scenario testing: Network errors, invalid inputs

---

## 📝 Documentation Updates

### API Documentation
- [ ] `README.md` - CSV Export endpoint documentation
- [ ] `docs/SALES-GUIDE.md` - UI Mini usage guide
- [ ] `docs/SALES-SCENARIOS.md` - UI usage scenarios

### Code Documentation
- [ ] `app/api/export.py` - Docstrings
- [ ] `app/static/js/app.js` - Code comments

---

## 🚨 Risk Mitigation

### CSV Export
- **Risk**: Large dataset memory issue
- **Mitigation**: Streaming response, pagination option

### UI Mini
- **Risk**: Browser compatibility
- **Mitigation**: Vanilla JS, no framework dependencies, polyfills if needed

---

## 📊 Success Metrics

### CSV Export
- Export success rate: ≥99%
- Export time for 1000 leads: ≤5 seconds
- User satisfaction: Positive feedback from sales team

### UI Mini
- Page load time: ≤2 seconds
- Feature usage: All features used within first week
- User satisfaction: Positive feedback from sales team

---

## 🔄 Feedback Loop

### Sprint 1 Sonrası
1. **MVP kullanımı devam eder** (paralel)
2. **Feedback toplanır** (1-2 hafta)
3. **Sprint 2 planlanır** (Bulk Scan, Webhook)

### Feedback Toplama
- CSV Export kullanım istatistikleri
- UI Mini kullanım istatistikleri
- Satış ekibi geri bildirimi
- Core değişiklik ihtiyaçları (varsa)

---

## 📅 Timeline

```
Sprint 0: Stabilizasyon (1-2 gün)
├── Day 1: Log tuning, error messages
└── Day 2: Timeout calibration, final review

Sprint 1: CSV Export + UI Mini (3-4 gün)
├── Day 1: CSV Export backend
├── Day 2-3: UI Mini implementation
└── Day 4: Testing, documentation, deployment

Feedback Collection (1-2 hafta)
└── MVP kullanımı + Sprint 1 özellikleri

Sprint 2: Bulk Scan (1-2 hafta) - Feedback sonrası
Sprint 3: Webhook (1 hafta) - Feedback sonrası
Sprint 4: Notes/Tags (2 hafta) - Feedback sonrası
```

---

## 🎯 Sprint 1 Definition of Done

- [ ] CSV Export endpoint implemented and tested
- [ ] UI Mini implemented and tested
- [ ] Documentation updated
- [ ] All tests passing
- [ ] Code review completed
- [ ] Deployed to development environment
- [ ] Sales team demo completed
- [ ] Feedback collected

---

**Son Güncelleme**: 2025-01-28  
**Durum**: In Progress  
**Sprint 1 Başlangıç**: 2025-01-28  
**Sprint 1 Hedef Bitiş**: 2025-02-03 (1 hafta)

