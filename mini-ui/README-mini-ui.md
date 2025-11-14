# Dyn365Hunter Mini UI

**Hızlı demo ve iç kullanım için basit, temiz bir Mini UI.**

---

## 🎯 Amaç

- Hızlı demo ve iç kullanım (sales + developer)
- "CSV yükle → tara → lead tablosunu gör → export et" akışını tarayıcıdan göstermek
- Uzun vadeli "gerçek frontend" değil; **köprü**

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
- Tablo görüntüleme (Domain, Şirket, Provider, Segment, Skor)

**Endpoint**: `GET /leads`

### 4. Export CSV
- Filtrelenmiş lead'leri CSV olarak export etme
- Otomatik dosya indirme

**Endpoint**: `GET /leads/export`

---

## 🔌 Kullanılan Endpoint'ler

### Backend API Endpoints

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/ingest/csv` | POST | CSV/Excel dosyası yükleme |
| `/scan/domain` | POST | Tek domain tarama |
| `/leads` | GET | Lead listesi (filtreli) |
| `/leads/export` | GET | Lead export (CSV) |
| `/dashboard` | GET | Dashboard istatistikleri |

### Query Parameters

**`/leads` ve `/leads/export`:**
- `segment`: Migration, Existing, Cold, Skip
- `min_score`: 0-100 arası minimum skor
- `provider`: M365, Google, Yandex, Zoho, Hosting, Local, Unknown

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
  README-mini-ui.md   # Bu dosya
```

---

## ⚠️ Limitler

### Kod Miktarı
- **JS toplam kod miktarı**: ~500 satır (yorumlar dahil), ~400 satır (yorumlar hariç)
- **4 ana özellik**: Upload, Scan, Table, Export

### Özellik Sınırı
- **5. özellik ihtiyacı doğarsa → "Framework zamanı" sinyali**
- Kod içinde TODO ile not bırakılmalı

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
   - Backend'de CORS middleware eklenmeli (production için)
   - Development'ta genellikle sorun olmaz

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

---

**Son Güncelleme**: 2025-01-28  
**Versiyon**: 1.0.0

