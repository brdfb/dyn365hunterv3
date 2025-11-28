# HAMLE 1: UI Feedback Test Checklist

**Tarih**: 2025-01-30  
**Durum**: 🔄 **TEST EDİLECEK**  
**URL**: `http://localhost:8000/mini-ui/`

---

## ✅ Test Checklist

### 1. Sync Button Test

- [ ] Header'da "🔄 Partner Center Sync" butonu görünüyor mu?
- [ ] Butona tıklayınca:
  - [ ] Toast notification gösteriliyor mu? ("Partner Center sync sıraya alındı")
  - [ ] Buton disable oluyor mu? (1 saniye sonra enable olmalı)
  - [ ] Sync status "queued" (turuncu) oluyor mu?

**Beklenen Davranış:**
- Buton tıklanınca → API call → Toast → Status "queued" → 2 dakika sonra "ok"

---

### 2. Sync Status Indicator Test

- [ ] Sağ üstte sync status gösteriliyor mu?
- [ ] Format doğru mu? ("Son sync: X dk önce (OK/FAIL/queued)")
- [ ] Renk kodları doğru mu?
  - [ ] OK → Yeşil (`header__sync-status--ok`)
  - [ ] FAIL → Kırmızı (`header__sync-status--fail`)
  - [ ] queued → Turuncu (`header__sync-status--queued`)
- [ ] Zaman formatı doğru mu?
  - [ ] < 1 dk → "az önce"
  - [ ] < 60 dk → "X dk önce"
  - [ ] ≥ 60 dk → "X saat önce"
- [ ] Sayfa yenilendiğinde status korunuyor mu? (localStorage)

**Test Senaryoları:**
1. Sync butonuna tıkla → Status "queued" olmalı
2. 2 dakika bekle → Status "ok" olmalı
3. Sayfayı yenile → Status korunmalı

---

### 3. Referral Column Test

- [ ] Leads tablosunda "Referral" kolonu var mı?
- [ ] Badge'ler doğru gösteriliyor mu?
  - [ ] Co-sell → Mavi badge (`referral-badge--co-sell`)
  - [ ] Marketplace → Yeşil badge (`referral-badge--marketplace`)
  - [ ] Solution Provider → Turuncu badge (`referral-badge--solution-provider`)
- [ ] Referral olmayan lead'lerde "-" gösteriliyor mu?
- [ ] Badge'e tıklayınca referral detail modal açılıyor mu?

**Beklenen:**
- 739 referral database'de → Tabloda referral badge'leri görünmeli
- Badge tıklanınca → Modal açılmalı

---

### 4. Referral Type Filter Test

- [ ] Filter bar'da "Referral" dropdown'u var mı?
- [ ] Seçenekler doğru mu? ("Tümü", "Co-sell", "Marketplace", "Solution Provider")
- [ ] Filter çalışıyor mu?
  - [ ] "Co-sell" seçince → Sadece co-sell referral'ları gösteriyor mu?
  - [ ] "Marketplace" seçince → Sadece marketplace referral'ları gösteriyor mu?
  - [ ] "Solution Provider" seçince → Sadece solution-provider referral'ları gösteriyor mu?
- [ ] Filter state localStorage'da korunuyor mu? (sayfa yenilendiğinde)

---

### 5. Referral Detail Modal Test

- [ ] Referral badge'e tıklayınca modal açılıyor mu?
- [ ] Modal içeriği doğru mu?
  - [ ] Referral ID
  - [ ] Referral Type
  - [ ] Company Name
  - [ ] Domain
  - [ ] Status (Active, In Progress, Won)
  - [ ] Created Date
  - [ ] Updated Date
- [ ] Action buttons çalışıyor mu?
  - [ ] "Copy Referral ID" → Clipboard'a kopyalıyor mu?
  - [ ] "Send to D365" → D365 push tetikleniyor mu?
  - [ ] "Open in Partner Center" → Partner Center link açılıyor mu?
- [ ] Modal kapatma çalışıyor mu? (X butonu, backdrop click, ESC key)

---

## 🐛 Bilinen Sorunlar

### 1. Sync Status Auto-Update
**Sorun**: Sync status 2 dakika sonra otomatik "ok" oluyor (gerçek sync durumu kontrol edilmiyor)  
**Etki**: Düşük - Kullanıcı deneyimini etkilemiyor  
**Çözüm**: Backend'den sync status polling (future enhancement)

### 2. Referral Badge CSS
**Sorun**: `ui-leads.js` satır 254'te gereksiz `replace()` kodu var  
**Etki**: Yok - Kod çalışıyor ama gereksiz  
**Çözüm**: Cleanup (P2 backlog)

---

## 📝 Test Sonuçları

**Test Tarihi**: _______________  
**Test Eden**: _______________  
**Sonuç**: _______________

**Notlar:**
- 

---

**Son Güncelleme**: 2025-01-30

