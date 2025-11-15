# Satış Ekibi Test Raporu - Bulgular ve Öneriler

**Tarih**: 2025-01-28  
**Test Edilen**: Mini UI, API Endpoints, Dokümantasyon  
**Test Verisi**: `mkposb_firma_listesi_13.11.2025.xlsx` (46 domain başarıyla işlendi)

---

## 🚨 KRİTİK SORUNLAR (P0 - Hemen Düzeltilmeli)

### 1. API Response'da Türkçe Karakter Encoding Sorunu

**Sorun:**
API response'larda Türkçe karakterler Unicode escape sequence olarak geliyor:

```json
{
  "canonical_name": "DM YAPI VE MADEN K\u00c4\u00b0MYASALLARI...",
  "reason": "Cloud kullan\u00c4\u00b1c\u00c4\u00b1lar\u00c4\u00b1, ge\u00c3\u00a7i\u00c5\u0178e haz\u00c4\u00b1r..."
}
```

**Etki:**
- Satış ekibi şirket adlarını okuyamıyor
- Excel export'ta Türkçe karakterler bozuk görünüyor
- Mini UI'de şirket adları anlamsız görünüyor

**Beklenen:**
```json
{
  "canonical_name": "DM YAPI VE MADEN KİMYASALLARI...",
  "reason": "Cloud kullanıcıları, geçişe hazır..."
}
```

**Lokasyon:**
- `app/api/leads.py` - Response encoding
- `app/core/scorer.py` - Reason message encoding
- Tüm API endpoint'leri

**Çözüm:**
- FastAPI response encoding'i kontrol et
- JSON response'lar UTF-8 olarak encode edilmeli
- `Content-Type: application/json; charset=utf-8` header'ı ekle

**Öncelik**: 🔴 **P0 - Hemen düzeltilmeli**

---

### 2. Mini UI'de Metin Bozuklukları (Word Break Sorunu)

**Sorun:**
Browser snapshot'ta görünen metin bozuklukları:
- "Do ya Seç" → "Dosya Seç" olmalı
- "Otomatik kolon te piti" → "Otomatik kolon tespiti" olmalı
- "Lead Li te i" → "Lead Listesi" olmalı
- "Exi ting" → "Existing" olmalı
- "Ho ting" → "Hosting" olmalı

**Etki:**
- Kullanıcı arayüzü profesyonel görünmüyor
- Metinler okunamıyor
- Satış ekibi kullanmakta zorlanıyor

**Lokasyon:**
- `mini-ui/styles.css` - Word-break CSS kuralları eksik
- Browser rendering sorunu

**Çözüm:**
```css
/* mini-ui/styles.css */
body, .form__label, .filters__label, .filters__select {
    word-break: keep-all;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Veya daha geniş container'lar için */
.filters__select, .form__label {
    min-width: fit-content;
}
```

**Öncelik**: 🔴 **P0 - Hemen düzeltilmeli**

---

## ⚠️ YÜKSEK ÖNCELİKLİ SORUNLAR (P1 - Bu Sprint)

### 3. Excel Upload Sonrası Progress Tracking Eksik

**Sorun:**
Excel dosyası yüklendiğinde progress tracking gösterilmiyor:
- Kullanıcı işlemin ne kadar sürdüğünü bilmiyor
- 46 domain için ~10-15 dakika sürebilir
- Kullanıcı sayfayı yenileyebilir veya işlemi iptal edebilir

**Etki:**
- Kullanıcı deneyimi kötü
- Büyük dosyalar için kullanılamaz
- Satış ekibi sabırsızlanıyor

**Beklenen:**
- Progress bar gösterilmeli
- "İşleniyor: 15/46 domain..." mesajı
- Job ID ile progress tracking

**Lokasyon:**
- `mini-ui/app.js` - CSV upload handler
- Progress tracking implementasyonu eksik

**Çözüm:**
```javascript
// CSV upload sonrası job_id al
// Polling ile progress takibi
// Progress bar göster
```

**Öncelik**: 🟡 **P1 - Bu sprint**

---

### 4. Error Messages Türkçe/İngilizce Karışık

**Sorun:**
API error mesajları karışık:
- Bazıları Türkçe: "geçersiz domain formatı"
- Bazıları İngilizce: "Invalid domain format"
- Tutarsızlık var

**Etki:**
- Kullanıcı deneyimi kötü
- Hata mesajları anlaşılmıyor
- Satış ekibi kafası karışıyor

**Beklenen:**
- Tüm error mesajları Türkçe olmalı (veya tutarlı bir dil)
- Mini UI'de Türkçe gösterilmeli

**Lokasyon:**
- `app/core/normalizer.py` - Error messages
- `app/api/ingest.py` - Error messages
- Tüm API endpoint'leri

**Çözüm:**
- Error message'ları standardize et
- Türkçe/İngilizce seçeneği ekle (opsiyonel)

**Öncelik**: 🟡 **P1 - Bu sprint**

---

### 5. Dashboard KPI'da "Max Score" Eksik

**Sorun:**
Dashboard KPI endpoint'inde `max_score` field'ı yok:
```json
{
  "total_leads": 57,
  "migration_leads": 3,
  "high_priority": 3
  // max_score eksik!
}
```

**Etki:**
- Mini UI'de "En Yüksek Skor" KPI kartı boş kalıyor
- Satış ekibi en yüksek skorlu lead'i göremiyor

**Beklenen:**
```json
{
  "total_leads": 57,
  "migration_leads": 3,
  "high_priority": 3,
  "max_score": 85
}
```

**Lokasyon:**
- `app/api/dashboard.py` - KPI endpoint
- `mini-ui/app.js` - KPI display

**Çözüm:**
- `GET /dashboard/kpis` endpoint'ine `max_score` ekle
- Mini UI'de göster

**Öncelik**: 🟡 **P1 - Bu sprint**

---

## 📋 ORTA ÖNCELİKLİ SORUNLAR (P2 - Sonraki Sprint)

### 6. Dokümantasyonda Eksik Bilgiler

**Sorun:**
- `SALES-GUIDE.md`'de Excel upload sonrası progress tracking'den bahsedilmiyor
- Mini UI'deki görsel sorunlardan bahsedilmiyor
- Error handling detayları eksik

**Etki:**
- Satış ekibi dokümantasyona güvenemiyor
- Gerçek kullanım ile dokümantasyon uyumsuz

**Çözüm:**
- Dokümantasyonu güncelle
- Gerçek kullanım senaryolarını ekle
- Screenshot'lar ekle (opsiyonel)

**Öncelik**: 🟢 **P2 - Sonraki sprint**

---

### 7. Mini UI'de Sorting/Pagination UI Eksik

**Sorun:**
Dokümantasyonda sorting/pagination özelliklerinden bahsediliyor ama:
- Tablo başlıklarına tıklayarak sorting yapılamıyor (görünmüyor)
- Pagination UI'de sayfa numaraları görünmüyor (sadece Önceki/Sonraki var)

**Etki:**
- G19 özellikleri tam çalışmıyor
- Satış ekibi sorting/pagination kullanamıyor

**Beklenen:**
- Tablo başlıklarında sorting icon'ları
- Sayfa numaraları (1, 2, 3, ...)
- Aktif sayfa vurgulaması

**Lokasyon:**
- `mini-ui/ui-leads.js` - Sorting/Pagination UI
- `mini-ui/styles.css` - Styling

**Çözüm:**
- Sorting UI ekle (tablo başlıklarında icon'lar)
- Pagination UI geliştir (sayfa numaraları)

**Öncelik**: 🟢 **P2 - Sonraki sprint**

---

### 8. Score Breakdown Modal Eksik

**Sorun:**
Dokümantasyonda "Skorlara tıklayarak detaylı skor analizi modal'ı açılır" deniyor ama:
- Skorlara tıklanınca modal açılmıyor
- Score breakdown endpoint'i var ama UI'de kullanılmıyor

**Etki:**
- G19 özelliği tam çalışmıyor
- Satış ekibi skor detaylarını göremiyor

**Beklenen:**
- Skorlara tıklanınca modal açılmalı
- Score breakdown detayları gösterilmeli

**Lokasyon:**
- `mini-ui/ui-leads.js` - Score click handler
- `mini-ui/index.html` - Modal HTML (var ama çalışmıyor)

**Çözüm:**
- Score click handler ekle
- Modal'ı doldur (`GET /leads/{domain}/score-breakdown`)

**Öncelik**: 🟢 **P2 - Sonraki sprint**

---

## 💡 İYİLEŞTİRME ÖNERİLERİ

### 9. Excel Upload Sonrası Başarı Mesajı

**Öneri:**
Excel upload sonrası daha detaylı başarı mesajı:
```
✅ 46 domain başarıyla yüklendi ve taranıyor...
📊 İşlem tamamlandığında lead listesi otomatik güncellenecek.
```

**Etki:**
- Kullanıcı ne olduğunu anlıyor
- Beklenti yönetimi iyileşiyor

**Öncelik**: 🟢 **P2 - Nice to have**

---

### 10. Export CSV Sonrası Dosya Adı

**Öneri:**
Export CSV sonrası dosya adı daha anlamlı olsun:
- Şu an: `leads_2025-01-28_14-30-00.csv`
- Öneri: `migration-leads-70+-2025-01-28.csv` (filtrelere göre)

**Etki:**
- Dosya adından içerik anlaşılıyor
- Organizasyon kolaylaşıyor

**Öncelik**: 🟢 **P2 - Nice to have**

---

## 📊 ÖZET: Öncelik Matrisi

| Sorun | Öncelik | Süre | Etki |
|-------|---------|------|------|
| 1. API Encoding Sorunu | 🔴 P0 | 2 saat | Yüksek |
| 2. UI Word Break Sorunu | 🔴 P0 | 1 saat | Yüksek |
| 3. Progress Tracking Eksik | 🟡 P1 | 4 saat | Orta |
| 4. Error Messages Karışık | 🟡 P1 | 2 saat | Orta |
| 5. Max Score KPI Eksik | 🟡 P1 | 1 saat | Düşük |
| 6. Dokümantasyon Eksik | 🟢 P2 | 2 saat | Düşük |
| 7. Sorting/Pagination UI | 🟢 P2 | 4 saat | Orta |
| 8. Score Breakdown Modal | 🟢 P2 | 3 saat | Orta |

**Toplam P0 Süre**: ~3 saat (hemen)  
**Toplam P1 Süre**: ~7 saat (bu sprint)  
**Toplam P2 Süre**: ~9 saat (sonraki sprint)

---

## 🎯 Önerilen Aksiyon Planı

### Hemen (Bugün - P0)
1. ✅ API encoding sorununu düzelt (UTF-8 response)
2. ✅ UI word-break sorununu düzelt (CSS)

### Bu Sprint (P1)
3. ✅ Progress tracking ekle (Excel upload)
4. ✅ Error messages standardize et
5. ✅ Max score KPI ekle

### Sonraki Sprint (P2)
6. ✅ Sorting/Pagination UI geliştir
7. ✅ Score breakdown modal çalışır hale getir
8. ✅ Dokümantasyonu güncelle

---

**Son Güncelleme**: 2025-01-28  
**Test Edilen**: Mini UI v1.0.0, API v1.0.0  
**Test Verisi**: 46 domain (mkposb_firma_listesi_13.11.2025.xlsx)

