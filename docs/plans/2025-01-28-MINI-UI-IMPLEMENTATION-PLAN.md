# Mini UI Implementation Plan

**Tarih**: 2025-01-28  
**Durum**: In Progress  
**Kapsam**: Mini UI (HTML + Vanilla JS) Implementation

---

## 📋 Spec Özeti

### Amaç
- Hızlı demo ve iç kullanım (sales + developer)
- "CSV yükle → tara → lead tablosunu gör → export et" akışı
- Uzun vadeli "gerçek frontend" değil; **köprü**

### Teknoloji
- HTML + CSS + **Vanilla JS** (framework yok)
- Kod disiplinli ve modüler (framework'e taşınabilir)

---

## 🎯 Sert Kurallar (Guardrails)

### 1. Kod Miktarı
- **JS toplam kod miktarı ≤ 400 satır** (yorumlar hariç)

### 2. Özellik Sınırı
- **En fazla 4 ana özellik:**
  1. CSV upload → `/ingest/csv`
  2. Tekil domain scan → `/scan/domain`
  3. Leads table + basit filtre → `/leads`
  4. Export butonu → `/leads/export`

- **5. özellik ihtiyacı doğarsa → "Framework zamanı" sinyali**
  - Kod içinde TODO ile not bırak

### 3. İş Mantığı
- **Tüm iş mantığı backend'de kalacak**
- Frontend sadece:
  - API çağrısı yapar
  - Sonucu gösterir
  - Basit form/filtre UI'si sunar

### 4. Entegrasyon
- **Entegrasyon yüzeyi = API**
- Hiçbir entegrasyon davranışı (D365 sync, webhook, vs.) UI'ye gömülmeyecek

---

## 📁 Dosya Yapısı

```
mini-ui/
  index.html
  styles.css
  js/
    app.js          # Giriş noktası, bootstrap, event binding
    api.js          # Tüm fetch çağrıları
    ui-leads.js     # Tablo + filtre render fonksiyonları
    ui-forms.js     # CSV upload + domain scan form davranışı
```

**Not**: Gereksiz micro-modülerlik yapma; 3-4 JS dosyası yeterli.

---

## 🔧 JS Modül Mantığı

### `api.js`
```javascript
// Tüm API çağrıları
async function fetchLeads(filters)
async function scanDomain(domain)
async function uploadCsv(file, autoDetect)
async function exportLeads(filters)
async function fetchDashboard()
```

### `ui-leads.js`
```javascript
// Tablo ve filtre render
function renderLeadsTable(leads)
function renderStats(summary)  // Toplam lead sayısı, Migration count vs.
function bindLeadFilters(state)
```

### `ui-forms.js`
```javascript
// Form davranışları
function bindCsvUploadForm(state)
function bindScanDomainForm(state)
```

### `app.js`
```javascript
// Global state objesi (tek bir yer)
window.state = {
  leads: [],
  filters: { segment: null, minScore: null, provider: null },
  dashboard: null,
  loading: false
}

// init() fonksiyonu → DOM hazır olduğunda çağrılır
function init() {
  // Default filtreler ile /leads çağır
  // Tabloyu doldur
  // Event'leri bağla
}
```

**Kural**: Global değişkenleri `window.state` ile 1 obje ile sınırla; başka global saçma değişkenler yaratma.

---

## 🎨 UI Davranışı (Kullanıcı Akışı)

### Layout (Tek Sayfa)

**Üst Kısım:**
- Basit header: "Dyn365Hunter Mini UI"
- Küçük KPI alanı:
  - Toplam lead sayısı
  - Migration lead sayısı
  - En yüksek skor

**Sol Blok:**
- **Form 1 – CSV Upload**
  - File input (sadece .csv, .xlsx)
  - Auto-detect columns checkbox
  - "Yükle ve işle" butonu
  - İşlem bitince: Toast / küçük mesaj
  - İsteğe bağlı otomatik `/leads` refresh

- **Form 2 – Tek Domain Scan**
  - Input: domain
  - Input: company name (optional)
  - "Tara" butonu
  - Sonuç: Küçük panel (domain, score, segment, provider)
  - İsteğe bağlı otomatik `/leads` refresh

**Sağ Blok:**
- **Leads Tablosu + Filtreler**
  - Filtreler:
    - Segment (select: All, Migration, Existing, Cold, Skip)
    - Min score (input number)
    - Provider (select: All, M365, Google, Hosting, Local, Unknown)
    - "Filtrele" butonu
  - Tablo:
    - Kolonlar: Domain, Company (varsa), Provider, Segment, Score
  - Export butonu:
    - Eğer `/leads/export` endpoint'i varsa: API'den dönen CSV'yi indirt
    - Yoksa: Mevcut JSON'dan basit CSV stringify et → Blob → download

**Loading ve Error:**
- Basit text göster
- Ağır animation, component kütüphanesi, vs. istemiyoruz

---

## 🔌 Entegrasyon / API-First Prensipleri

### 1. Tüm İş Kuralları Backend'de
- UI tarafında: Sadece request/response işle
- Response'u tablo, badge, stat olarak göster

### 2. İş Mantığı UI'de Olmamalı
- Örnek: "Skoru 80 üstü olanları auto-highlight etme kuralı"
- Bunu JS'te hardcode etme
- Max görsel highlight yapabilir, ama filtre/segmentation kararı backend'den gelmeli

### 3. API Endpoint'lerini Kolay Değiştirilebilir Yap
```javascript
const API_BASE_URL = 'http://localhost:8000'  // Tek noktadan yönet
```

**Fayda:**
- Yarın başka UI (React/Next) geldiğinde aynı API'yi kullanacak
- Yarın D365 entegrasyonu geldiğinde UI'ye dokunmadan ilerleyebileceğiz

---

## 🚀 Geleceğe Hazırlık: Framework'e Geçiş

### 1. Render Fonksiyonları Componentleşme Mantığı
- "Leads tablosu tek fonksiyon, stat alanı tek fonksiyon, filtre bar tek fonksiyon"

### 2. API Çağrılarını Tek Dosyada Tut
- `fetch logic` tekrar dağılmasın

### 3. CSS BEM Pattern
```css
.leads-table
.leads-table__row
.leads-table__cell--highlight
```

**Fayda:**
- JSX component'lere taşırken mental model birebir aynı olacak
- En kötü ihtimalle bu kodu "yakıp yeniden yazsan bile" UX flow + API tasarımından kazanmış olacağız

---

## 📝 Implementation Adımları

### Adım 1: Dosya Yapısı ✅
- [x] `mini-ui/` klasör yapısı oluştur
- [x] `index.html`, `styles.css`, `js/` klasörü

### Adım 2: HTML İskeleti
- [ ] `index.html` - Layout, header, KPI, form alanları, leads table

### Adım 3: CSS
- [ ] `styles.css` - BEM pattern, responsive, color coding

### Adım 4: JS - API Layer
- [ ] `api.js` - Tüm fetch fonksiyonları

### Adım 5: JS - UI Layer
- [ ] `ui-leads.js` - Tablo render, filtre binding, stats render
- [ ] `ui-forms.js` - CSV upload form, domain scan form binding

### Adım 6: JS - App Layer
- [ ] `app.js` - Global state, init, orchestration
- [ ] **400 satır kontrolü** (yorumlar hariç)

### Adım 7: FastAPI Integration
- [ ] `app/main.py` - Static file serving (`app.mount("/mini-ui", ...)`)

### Adım 8: Documentation
- [ ] `README-mini-ui.md` - Kullanım kılavuzu, limitler, endpoint'ler

---

## ✅ Acceptance Criteria

### Functional
- [ ] CSV upload çalışıyor (CSV, Excel)
- [ ] Domain scan çalışıyor
- [ ] Leads table görüntüleniyor (filters, sorting)
- [ ] Export butonu çalışıyor
- [ ] Dashboard summary görüntüleniyor
- [ ] Responsive design (mobile-friendly)
- [ ] Error handling çalışıyor

### Technical
- [ ] JS toplam kod miktarı ≤ 400 satır (yorumlar hariç)
- [ ] 4 ana özellik (upload, scan, table, export)
- [ ] API-first yaklaşım (iş mantığı backend'de)
- [ ] BEM CSS pattern
- [ ] Modüler JS yapısı (api.js, ui-leads.js, ui-forms.js, app.js)
- [ ] Global state tek obje (`window.state`)

### Documentation
- [ ] `README-mini-ui.md` - Kullanım kılavuzu
- [ ] Endpoint'ler dokümante edilmiş
- [ ] Limitler belirtilmiş (4 feature, 400 satır)

---

## 🚨 Risk Mitigation

### 1. Kod Miktarı Aşımı
- **Risk**: 400 satır sınırı aşılabilir
- **Mitigation**: 
  - Her modülde satır sayısını takip et
  - Gereksiz abstraction yapma
  - Yorumları minimal tut

### 2. Özellik Creep
- **Risk**: 5. özellik ekleme isteği
- **Mitigation**: 
  - TODO ile "Framework zamanı" sinyali bırak
  - Scope'u sıkı tut

### 3. Browser Compatibility
- **Risk**: Eski tarayıcılar desteklenmeyebilir
- **Mitigation**: 
  - Vanilla JS (ES6+)
  - Modern tarayıcılar için (Chrome, Firefox, Safari)
  - Polyfills gerekirse ekle

---

## 📊 Success Metrics

- [ ] Page load time: ≤2 seconds
- [ ] Feature usage: All features used within first week
- [ ] User satisfaction: Positive feedback from sales team
- [ ] JS kod miktarı: ≤400 satır (yorumlar hariç)
- [ ] Özellik sayısı: 4 (upload, scan, table, export)

---

**Son Güncelleme**: 2025-01-28  
**Durum**: In Progress  
**Başlangıç**: 2025-01-28

