# Dyn365Hunter Mini UI

**Internal production kullanım için stabilize edilmiş UI (v1.1-stable).**

---

## 🎯 Amaç

- **Ana kullanıcı**: Sales team + internal engineering team
- "CSV yükle → tara → lead tablosunu gör → export et" akışını tarayıcıdan göstermek
- **Not**: Bu UI başlangıçta demo amaçlıydı; G19 + Gün 3 sonrası **internal production kullanım için stabilize edilmiştir**. Uzun vadede React/Next.js sürümü planlanmıştır.

---

## 🚀 Nasıl Ayağa Kaldırılır?

### 1. Backend'i Başlat

```bash
# Docker Compose ile
docker-compose up -d

# Veya local development
uvicorn app.main:app --reload
```

### 2. Mini UI'ye Eriş

Tarayıcıda aç:
```
http://localhost:8000/mini-ui/
```

**Not**: FastAPI otomatik olarak `mini-ui/` klasörünü `/mini-ui` path'inde serve eder.

---

## 📋 Özellikler

### 1. CSV/Excel Upload
- CSV veya Excel dosyası yükleme
- Otomatik kolon tespiti (OSB dosyaları için)
- Yükleme sonrası otomatik lead listesi refresh

**Endpoint**: `POST /ingest/csv`

### 2. Tek Domain Scan
- Domain tarama
- Şirket adı (opsiyonel)
- Sonuç gösterimi (skor, segment, provider)

**Endpoint**: `POST /scan/domain`

### 3. Leads Table + Filtreler
- Segment filtresi (Migration, Existing, Cold, Skip)
- Min skor filtresi
- Provider filtresi (M365, Google, Yandex, vb.)
- **Search input** (Domain, şirket veya provider'da arama) - G19
- **Sorting** (Table header'lara tıklayarak sıralama) - G19
- **Pagination** (Sayfa numaraları, önceki/sonraki butonları, sayfa bilgisi) - G19
- Tablo görüntüleme (Öncelik, Domain, Şirket, Provider, Tenant Size, Local Provider, Segment, Skor)
- **Table view improvements** (Gün 3) - Column width optimization, row hover effects, empty state with CTA, loading spinner
- **P-Model Priority Badges** (Phase 3 - 2025-01-29) - P1-P6 renkli badge'ler, priority_label tooltip'leri
- **Score breakdown modal** (G19 + Gün 3) - Click skor'a tıklayarak detaylı skor analizi, tooltips for signals/risks, ESC key support, backdrop click to close
- **CSP P-Model Panel** (Phase 3 - 2025-01-29) - Score breakdown modal'da technical_heat, commercial_segment, commercial_heat, priority_category, priority_label
- **Provider-specific description** (v1.1 - 2025-01-29) - Score breakdown modal açıklama cümlesi provider'a göre dinamik

**Endpoint**: `GET /leads`

### 4. Export CSV/Excel/PDF
- Filtrelenmiş lead'leri CSV veya Excel olarak export etme - Gün 3
- **CSV/Excel export buttons** - Ayrı butonlar (CSV ve Excel) - Gün 3
- **Toast notifications** - Export başarı/hata mesajları - Gün 3
- **PDF export** - Score breakdown modal'dan PDF indirme - Gün 3
- Otomatik dosya indirme
- **Performance Note**: PDF export high CPU load yaratır; yoğun kullanımda queue önerilir

**Endpoint**: `GET /leads/export` (CSV/Excel), `GET /leads/{domain}/summary.pdf` (PDF)

---

## 🔌 Kullanılan Endpoint'ler

### Backend API Endpoints

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/ingest/csv` | POST | CSV/Excel dosyası yükleme |
| `/scan/domain` | POST | Tek domain tarama |
| `/leads` | GET | Lead listesi (filtreli) |
| `/leads/export` | GET | Lead export (CSV/Excel) - Gün 3 |
| `/leads/{domain}/summary.pdf` | GET | PDF export (Gün 3) |
| `/leads/{domain}/score-breakdown` | GET | Score breakdown detayları (G19) |
| `/dashboard` | GET | Dashboard istatistikleri (tüm dashboard datası) |
| `/dashboard/kpis` | GET | Dashboard KPIs (G19) - Internal use only |

### Query Parameters

**`/leads` ve `/leads/export`:**
- `segment`: Migration, Existing, Cold, Skip
- `min_score`: 0-100 arası minimum skor
- `provider`: M365, Google, Yandex, Zoho, Hosting, Local, Unknown
- `search`: Domain, şirket veya provider'da arama (G19)
- `sort_by`: Sıralama alanı (domain, readiness_score, priority_score, segment, provider, scanned_at) (G19)
- `sort_order`: Sıralama yönü (asc, desc) (G19)
- `page`: Sayfa numarası (1-based) (G19)
- `page_size`: Sayfa başına kayıt sayısı (default: 50, max: 200) (G19)

---

## 📁 Dosya Yapısı

```
mini-ui/
  index.html          # Ana sayfa
  styles.css          # CSS (BEM pattern)
  js/
    app.js            # Global state, init, orchestration
    api.js            # Tüm fetch çağrıları
    ui-leads.js       # Tablo + filtre render
    ui-forms.js       # CSV upload + domain scan form
    logger.js         # Production-safe logging utility
  README-mini-ui.md   # Bu dosya
  TEST-CHECKLIST.md   # Test senaryoları
```

**Not**: UI tamamen modülerdir; React'e taşımaya hazır component pattern kullanır.

---

## ⚠️ Limitler

### Kod Miktarı
- **JS toplam kod miktarı**: ~1856 satır (yorumlar dahil), ~1400-1500 satır (yorumlar hariç) - Gün 3 + Phase 3 (P-Model) + iyileştirmeler ile artış
- **12+ ana özellik**: Upload, Scan, Table, Export (CSV/Excel/PDF), Search, Sorting, Pagination, Score Breakdown Modal, Toast Notifications, Tooltips, P-Model Badges, CSP P-Model Panel

### Özellik Sınırı
- **Mini UI şu anda 12+ özellikte, framework sınırına yaklaşmıştır**
- **15+ özellik ihtiyacı doğarsa → "Framework zamanı" sinyali**
- Kod içinde TODO ile not bırakılmalı
- **Not**: G19 ile Search, Sorting, Pagination eklendi (3 yeni özellik)
- **Not**: Gün 3 ile Export/PDF, Toast Notifications, Tooltips, Modal improvements eklendi (4+ yeni özellik)
- **Not**: Phase 3 (2025-01-29) ile P-Model Badges ve CSP P-Model Panel eklendi (2 yeni özellik)

### İş Mantığı
- **Tüm iş mantığı backend'de kalır**
- Frontend sadece:
  - API çağrısı yapar
  - Sonucu gösterir
  - Basit form/filtre UI'si sunar

---

## 🎨 Teknoloji

- **HTML5**: Semantic markup
- **CSS3**: BEM pattern, responsive design
- **Vanilla JavaScript (ES6+)**: Module pattern, no framework
- **FastAPI StaticFiles**: Static file serving
- **Production-safe logging**: Logger utility with debug mode (set `window.DEBUG = true` for development)

---

## 🔧 Yapılandırma

### API Base URL

Varsayılan: `http://localhost:8000`

Değiştirmek için `mini-ui/js/api.js` dosyasında:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

---

## 🚨 Sorun Giderme

### Mini UI Açılmıyor

1. Backend çalışıyor mu kontrol et:
   ```bash
   # Legacy endpoint (backward compatible)
   curl http://localhost:8000/healthz
   
   # Veya yeni health check endpoint'leri (recommended)
   curl http://localhost:8000/healthz/ready  # DB + Redis check
   curl http://localhost:8000/healthz/live   # Liveness check
   ```

2. `mini-ui/` klasörü proje root'unda var mı kontrol et

3. FastAPI log'larına bak:
   ```bash
   docker-compose logs api
   ```

### API Çağrıları Çalışmıyor

1. CORS hatası alıyorsan:
   - **Production kullanımda CORS whitelist gerekir** (backend'de CORS middleware)
   - Development'ta (localhost) genellikle sorun olmaz
   - Sales team localhost dışından açarsa CORS bozar

2. Network hatası:
   - API_BASE_URL doğru mu kontrol et
   - Backend endpoint'leri çalışıyor mu kontrol et

### Export Çalışmıyor

1. `/leads/export` endpoint'i backend'de var mı kontrol et
2. Browser console'da hata var mı kontrol et

---

## 🔄 Framework'e Geçiş

Bu Mini UI bir gün React/Next.js veya benzeri framework'e taşınabilir.

### Hazırlık

1. **Render fonksiyonları componentleşme mantığı ile yazıldı**
   - Leads tablosu tek fonksiyon
   - Stat alanı tek fonksiyon
   - Filtre bar tek fonksiyon

2. **API çağrıları tek dosyada** (`api.js`)
   - Fetch logic tekrar dağılmadı

3. **CSS BEM pattern**
   - `.leads-table`, `.leads-table__row`, `.leads-table__cell--highlight`
   - JSX component'lere taşırken mental model birebir aynı olacak

### Geçiş Stratejisi

1. API layer'ı aynen kullan (fetch fonksiyonları)
2. UI component'leri React component'lerine çevir
3. State management için Redux/Context API kullan
4. CSS'i CSS Modules veya styled-components'e taşı

---

## 📝 Notlar

- **Backend'e dokunulmadı**: Mini UI sadece mevcut API'yi kullanır
- **Zero dependency**: Hiçbir external library kullanılmadı
- **Modüler yapı**: Framework'e geçişe hazır
- **API-first**: Tüm iş mantığı backend'de

---

## 🎯 MVP Exit Kriteri

**"Satışçı 3 domain'i tarayıp Migration segmentinde ≥70 skor lead görebiliyor."**

Bu Mini UI ile:
1. CSV yükle → Domain'leri ekle
2. Domain tara → Skor hesapla
3. Lead tablosunu gör → Migration segmentinde ≥70 skor lead'leri filtrele
4. Export et → CSV olarak indir

**Kritik**: UI üzerinde Migration ≥70 filtre akışı eksiksiz çalışır (segment filter + min_score filter kombinasyonu).

---

**Son Güncelleme**: 2025-01-29  
**Versiyon**: 1.1-stable (G19: Search, Sorting, Pagination | Gün 3: UI Stabilizasyon - Table cleanup, Modal improvements, Export/PDF, Tooltips, Toast notifications | Phase 3: CSP P-Model Integration - P-badges, tooltips, score breakdown panel, provider-specific descriptions | İyileştirmeler: Production-safe logging, improved error handling, DMARC coverage bug fix, risk summary text fix)

