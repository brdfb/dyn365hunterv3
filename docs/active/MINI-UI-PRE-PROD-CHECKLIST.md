# Mini UI Pre-Production Checklist

**Date**: 2025-01-30  
**Status**: ⚠️ **PRE-PRODUCTION REVIEW**  
**Purpose**: Mini UI'yi prod'a gitmeden önce test etmek

---

## 🚀 Erişim

**URL**: `http://localhost:8000/mini-ui/`

**Backend Status**: ✅ Running
- API: `http://localhost:8000` (healthy)
- Database: Connected
- Redis: Connected
- Partner Center: Enabled

---

## ✅ Test Edilecek Özellikler

### 1. Partner Center Integration (YENİ)

#### 1.1 Sync Button
- [ ] Header'da "🔄 Partner Center Sync" butonu görünüyor mu?
- [ ] Butona tıklayınca toast notification gösteriliyor mu? ("Partner Center sync sıraya alındı")
- [ ] Buton disable/enable durumu çalışıyor mu?

#### 1.2 Sync Status Indicator
- [ ] Sağ üstte sync status gösteriliyor mu?
- [ ] Format: "Son sync: X dk önce (OK/FAIL/Sırada)"
- [ ] Renk kodları doğru mu?
  - [ ] OK → Yeşil
  - [ ] FAIL → Kırmızı
  - [ ] Sırada → Turuncu
- [ ] Zaman formatı doğru mu?
  - [ ] < 1 dk → "az önce"
  - [ ] < 60 dk → "X dk önce"
  - [ ] ≥ 60 dk → "X saat önce"
- [ ] Sayfa yenilendiğinde status korunuyor mu? (localStorage)

#### 1.3 Referral Column
- [ ] Leads tablosunda "Referral" kolonu var mı?
- [ ] Badge'ler doğru gösteriliyor mu?
  - [ ] Co-sell → Mavi badge
  - [ ] Marketplace → Yeşil badge
  - [ ] Solution Provider → Turuncu badge
- [ ] Referral olmayan lead'lerde "-" gösteriliyor mu?

#### 1.4 Referral Type Filter
- [ ] Filter bar'da "Referral" dropdown'u var mı?
- [ ] Seçenekler: "Tümü", "Co-sell", "Marketplace", "Solution Provider"
- [ ] Filter çalışıyor mu? (sadece seçilen referral type'ı gösteriyor mu?)
- [ ] Filter state localStorage'da korunuyor mu?

### 2. Core Features

#### 2.1 CSV/Excel Upload
- [ ] CSV dosyası yüklenebiliyor mu?
- [ ] Excel dosyası yüklenebiliyor mu?
- [ ] Upload sonrası lead listesi refresh oluyor mu?
- [ ] Toast notification gösteriliyor mu?

#### 2.2 Domain Scan
- [ ] Tek domain scan çalışıyor mu?
- [ ] Scan sonrası lead listesi refresh oluyor mu?
- [ ] Sonuç gösterimi doğru mu? (skor, segment, provider)

#### 2.3 Leads Table
- [ ] Lead listesi gösteriliyor mu?
- [ ] Kolonlar doğru mu? (Priority, Domain, Şirket, Provider, Tenant Size, Local Provider, Referral, Skor, Segment)
- [ ] Sorting çalışıyor mu? (kolon başlıklarına tıklayınca)
- [ ] Pagination çalışıyor mu?
- [ ] Search çalışıyor mu? (full-text search)

#### 2.4 Filters
- [ ] Segment filter çalışıyor mu?
- [ ] Min Skor filter çalışıyor mu?
- [ ] Provider filter çalışıyor mu?
- [ ] Referral Type filter çalışıyor mu?
- [ ] Clear filters butonu çalışıyor mu?
- [ ] Filter state localStorage'da korunuyor mu?

#### 2.5 Score Breakdown Modal
- [ ] Domain'e tıklayınca modal açılıyor mu?
- [ ] Score breakdown detayları gösteriliyor mu?
- [ ] CSP P-Model paneli var mı?
- [ ] Provider-specific açıklamalar doğru mu?
- [ ] Modal kapatılabiliyor mu? (X, ESC, backdrop click)

#### 2.6 Export
- [ ] CSV export çalışıyor mu?
- [ ] Excel export çalışıyor mu?
- [ ] Export sonrası toast notification gösteriliyor mu?
- [ ] Export filter'ları uyguluyor mu?

#### 2.7 Dashboard KPIs
- [ ] KPI kartları gösteriliyor mu?
- [ ] Değerler doğru mu? (Toplam Lead, Migration, Yüksek Öncelik, En Yüksek Skor)
- [ ] KPI'lar otomatik refresh oluyor mu?

### 3. UX/UI Polish

#### 3.1 Loading States
- [ ] Table loading spinner gösteriliyor mu?
- [ ] Button disable states çalışıyor mu?
- [ ] Modal loading states çalışıyor mu?

#### 3.2 Toast Notifications
- [ ] Toast'lar gösteriliyor mu?
- [ ] Toast'lar otomatik dismiss oluyor mu?
- [ ] Toast pozisyonları doğru mu? (stacking)

#### 3.3 Tooltips
- [ ] Priority badge tooltip'leri çalışıyor mu?
- [ ] Provider badge tooltip'leri çalışıyor mu?
- [ ] Tenant Size tooltip'leri çalışıyor mu?

#### 3.4 Responsive Design
- [ ] Mobile görünümde layout bozulmuyor mu?
- [ ] Tablet görünümde layout bozulmuyor mu?
- [ ] Header responsive mi? (sync button + status)

### 4. Error Handling

#### 4.1 API Errors
- [ ] API hatalarında toast notification gösteriliyor mu?
- [ ] Error mesajları Türkçe ve anlaşılır mı?
- [ ] Network hatalarında uygun mesaj gösteriliyor mu?

#### 4.2 Edge Cases
- [ ] Boş lead listesi durumunda empty state gösteriliyor mu?
- [ ] Filter sonucu boşsa uygun mesaj var mı?
- [ ] Invalid domain scan'de hata mesajı gösteriliyor mu?

---

## 🐛 Bilinen Sorunlar

- [ ] Yok (şu an için)

---

## 📝 Test Sonuçları

**Test Tarihi**: _______________

**Test Eden**: _______________

**Genel Durum**: 
- [ ] ✅ Tüm testler geçti
- [ ] ⚠️ Bazı testler başarısız (detaylar aşağıda)
- [ ] ❌ Kritik sorunlar var

**Notlar**:
- 

---

## 🎯 Production'a Gitmeden Önce

- [ ] Tüm testler geçti
- [ ] Bilinen sorunlar dokümante edildi
- [ ] Error handling test edildi
- [ ] Responsive design test edildi
- [ ] Partner Center integration test edildi
- [ ] Performance test edildi (büyük lead listeleri)

---

**Son Güncelleme**: 2025-01-30

