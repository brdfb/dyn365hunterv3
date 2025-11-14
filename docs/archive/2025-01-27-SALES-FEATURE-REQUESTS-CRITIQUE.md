# SALES-FEATURE-REQUESTS.md - Kritik Değerlendirme

**Tarih**: 2025-01-27  
**Değerlendiren**: Technical Review  
**Kapsam**: Özellik önerilerinin MVP scope, teknik gerçekçilik ve öncelik analizi

---

## 🔴 KRİTİK SORUNLAR

### 1. **MVP Scope İhlali - Bulk Scan ve CSV Export**

**Sorun:**
- `SALES-FEATURE-REQUESTS.md`'de **Bulk Scan** ve **CSV Export** yüksek öncelik verilmiş
- Ancak `.cursorrules` ve `CRITIQUE.md`'de açıkça **OUT OF SCOPE (Post-MVP)** olarak belirtilmiş:
  - ❌ Bulk scan endpoint (`/scan/bulk`)
  - ❌ CSV export endpoint (`POST /export`)

**Etki:**
- MVP scope discipline ihlali
- Yanlış beklenti yaratma
- Post-MVP özellikler MVP olarak sunulmuş

**Çözüm:**
- Bu özellikler **Post-MVP** olarak işaretlenmeli
- Öncelik matrisinde "Post-MVP" kategorisi eklenmeli
- MVP scope'unda olmayan özellikler açıkça belirtilmeli

---

### 2. **Bulk Scan - Teknik Riskler İhmal Edilmiş**

**Sorun:**
- `SALES-FEATURE-REQUESTS.md`'de Bulk Scan için sadece fayda belirtilmiş
- `CRITIQUE.md`'de belirtilen kritik riskler yok:
  - Timeout stratejisi yok (100 domain → 20 dakika, kullanıcı timeout alabilir)
  - Rate-limit stratejisi yok (DNS/WHOIS rate-limit'e takılabilir)
  - Partial failure handling yok (50. domain'de hata → ne olacak?)
  - Progress tracking nasıl olacak? (WebSocket? Polling?)

**Etki:**
- Teknik gerçekçilik eksik
- Riskler göz ardı edilmiş
- Implementasyon zorluğu yanlış değerlendirilmiş (3-5 gün → 1-2 hafta)

**Çözüm:**
- Bulk Scan için risk analizi eklenmeli
- Async queue gereksinimi belirtilmeli
- MVP'de sequential bulk yerine async queue önerilmeli

---

### 3. **CSV Export - Endpoint Tasarımı Eksik**

**Sorun:**
- `GET /leads/export?format=csv` önerilmiş
- Ancak:
  - Filtreleme parametreleri nasıl geçilecek? (segment, min_score, provider)
  - Response format? (CSV string? File download?)
  - Content-Type header? (`text/csv` vs `application/json`)
  - Büyük dataset'ler için pagination? (1000+ lead)

**Etki:**
- Endpoint tasarımı yarım kalmış
- Implementasyon detayları belirsiz
- Edge case'ler düşünülmemiş

**Çözüm:**
- Endpoint tasarımı detaylandırılmalı
- Filtreleme parametreleri belirtilmeli
- Response format ve header'lar tanımlanmalı

---

### 4. **Priority Score - Mantık Belirsiz**

**Sorun:**
- Priority Score için mantık verilmiş ama:
  - "Migration + Score 80+ → Priority: 1" - Bu zaten segment'te var
  - "Existing + Score 70+ → Priority: 3" - Bu segment'te yok, neden?
  - Segment + Score kombinasyonu zaten mevcut, priority_score ne ekliyor?

**Etki:**
- Gereksiz complexity
- Mevcut segment mantığı ile çakışma riski
- Değer önerisi belirsiz

**Çözüm:**
- Priority Score'un segment'ten farkı açıklanmalı
- Veya segment mantığı yeterli ise priority_score gereksiz olabilir
- Gerçek ihtiyaç analizi yapılmalı

---

### 5. **Email Templates - API Sorumluluğu Değil**

**Sorun:**
- Email template'leri API'de tutulması önerilmiş
- Ancak:
  - Bu frontend/CRM'in sorumluluğu
  - API'nin görevi değil
  - Content management gerektirir (CRUD operations)

**Etki:**
- Yanlış sorumluluk ataması
- API scope'unun dışına çıkma
- Gereksiz complexity

**Çözüm:**
- Email template'leri frontend/CRM'de tutulmalı
- Veya ayrı bir content service olmalı
- API sadece data sağlamalı, template yönetimi değil

---

## 🟡 ÖNEMLİ SORUNLAR

### 6. **Notes/Tags - Database Schema Değişikliği Gerektirir**

**Sorun:**
- Notes/Tags için database schema değişikliği gerekiyor
- Yeni tablo veya column ekleme
- Migration gerektirir

**Etki:**
- MVP scope'unda değil (schema değişikliği)
- Implementasyon zorluğu yanlış değerlendirilmiş (orta → yüksek)

**Çözüm:**
- Database schema değişikliği gerektiği belirtilmeli
- Migration planı eklenmeli
- Post-MVP olarak işaretlenmeli

---

### 7. **Favorites - Database Schema Değişikliği Gerektirir**

**Sorun:**
- Favorites için user/lead ilişkisi gerekiyor
- Authentication gerektirir (kimin favorisi?)
- Database schema değişikliği

**Etki:**
- MVP scope'unda değil (auth + schema değişikliği)
- Implementasyon zorluğu yanlış değerlendirilmiş (kolay → orta-yüksek)

**Çözüm:**
- Authentication gereksinimi belirtilmeli
- Database schema değişikliği belirtilmeli
- Post-MVP olarak işaretlenmeli

---

### 8. **Reminders - Scheduler Gerektirir**

**Sorun:**
- Reminders için scheduler/background job gerekiyor
- `.cursorrules`'da scheduler **OUT OF SCOPE** olarak belirtilmiş
- Cron job veya task queue gerektirir

**Etki:**
- MVP scope'unda değil (scheduler OUT OF SCOPE)
- Implementasyon zorluğu yanlış değerlendirilmiş (orta → yüksek)

**Çözüm:**
- Scheduler gereksinimi belirtilmeli
- Post-MVP olarak işaretlenmeli
- Veya external scheduler (cron) kullanılabilir (API dışında)

---

### 9. **Dashboard - Basit Endpoint Olabilir**

**Sorun:**
- Dashboard için basit bir endpoint yeterli
- Database aggregation query'leri
- MVP scope'unda olabilir (basit endpoint)

**Etki:**
- Öncelik düşük verilmiş ama MVP scope'unda olabilir
- Quick win olabilir (1 gün)

**Çözüm:**
- Dashboard MVP scope'unda olabilir
- Öncelik yükseltilmeli (düşük → orta)
- Quick win olarak eklenebilir

---

## 📊 ÖNCELİK MATRİSİ DÜZELTMELERİ

### Mevcut Matris Sorunları:
1. **Bulk Scan** - MVP scope'unda değil ama yüksek öncelik
2. **CSV Export** - MVP scope'unda değil ama yüksek öncelik
3. **Priority Score** - Mantık belirsiz
4. **Email Templates** - API sorumluluğu değil
5. **Notes/Tags** - Schema değişikliği gerektirir
6. **Favorites** - Auth + Schema değişikliği gerektirir
7. **Reminders** - Scheduler gerektirir
8. **Dashboard** - MVP scope'unda olabilir ama düşük öncelik

### Düzeltilmiş Matris:

| Özellik | MVP Scope | Öncelik | Zorluk | Etki | Not |
|---------|-----------|---------|--------|------|-----|
| **Priority Score** | ✅ MVP | 🟡 Orta | 🟢 Kolay | ⭐⭐ Orta | Mantık netleştirilmeli |
| **Dashboard** | ✅ MVP | 🟡 Orta | 🟢 Kolay | ⭐⭐ Orta | Quick win olabilir |
| **CSV Export** | ❌ Post-MVP | 🔴 Yüksek | 🟢 Kolay | ⭐⭐⭐ Yüksek | Endpoint tasarımı eksik |
| **Bulk Scan** | ❌ Post-MVP | 🔴 Yüksek | 🔴 Yüksek | ⭐⭐⭐ Yüksek | Async queue gerektirir |
| **Email Templates** | ❌ Post-MVP | 🟢 Düşük | 🟡 Orta | ⭐ Düşük | API sorumluluğu değil |
| **Notes/Tags** | ❌ Post-MVP | 🟢 Düşük | 🔴 Yüksek | ⭐ Düşük | Schema değişikliği |
| **Favorites** | ❌ Post-MVP | 🟢 Düşük | 🔴 Yüksek | ⭐ Düşük | Auth + Schema |
| **Reminders** | ❌ Post-MVP | 🟢 Düşük | 🔴 Yüksek | ⭐ Düşük | Scheduler gerektirir |

---

## 💡 ÖNERİLER

### 1. **MVP Scope'unda Olanlar (Hemen Yapılabilir)**

#### Priority Score (Mantık Netleştirildikten Sonra)
- Sadece response'a field ekleme
- Mevcut segment mantığına ekleme
- **Ama:** Mantık netleştirilmeli - segment'ten farkı ne?

#### Dashboard (Quick Win)
- Basit aggregation endpoint
- Segment dağılımı, toplam lead sayısı
- **Zorluk:** Kolay (1 gün)
- **Fayda:** Hızlı özet görünüm

---

### 2. **Post-MVP Ama Yüksek Öncelik**

#### CSV Export
- Endpoint tasarımı detaylandırılmalı
- Filtreleme parametreleri belirtilmeli
- Response format tanımlanmalı

#### Bulk Scan
- Async queue gereksinimi belirtilmeli
- Timeout/rate-limit stratejisi eklenmeli
- Progress tracking mekanizması belirtilmeli
- **Not:** Sequential bulk yerine async queue önerilmeli

---

### 3. **Post-MVP ve Düşük Öncelik**

#### Email Templates
- API sorumluluğu değil
- Frontend/CRM'de tutulmalı
- Veya ayrı content service

#### Notes/Tags, Favorites, Reminders
- Database schema değişikliği gerektirir
- Auth gerektirir (favorites, reminders)
- Scheduler gerektirir (reminders)
- Post-MVP olarak planlanmalı

---

## 🎯 DÜZELTME ÖNERİLERİ

### 1. **Dosya Yapısı**
```
SALES-FEATURE-REQUESTS.md
├── MVP Scope'unda Olanlar
│   ├── Priority Score (mantık netleştirildikten sonra)
│   └── Dashboard (quick win)
├── Post-MVP - Yüksek Öncelik
│   ├── CSV Export (endpoint tasarımı detaylandırılmalı)
│   └── Bulk Scan (async queue gereksinimi belirtilmeli)
└── Post-MVP - Düşük Öncelik
    ├── Email Templates (API sorumluluğu değil)
    ├── Notes/Tags (schema değişikliği)
    ├── Favorites (auth + schema)
    └── Reminders (scheduler)
```

### 2. **Risk Analizi Ekleme**
- Her özellik için risk analizi
- Teknik zorluklar
- MVP scope uyumluluğu

### 3. **Endpoint Tasarımı Detaylandırma**
- Request/Response formatları
- Filtreleme parametreleri
- Error handling
- Edge case'ler

### 4. **Mantık Netleştirme**
- Priority Score'un segment'ten farkı
- Gerçek ihtiyaç analizi
- Değer önerisi

---

## 📝 SONUÇ

### Kritik Sorunlar:
1. ❌ MVP scope ihlali (Bulk Scan, CSV Export)
2. ❌ Teknik riskler ihmal edilmiş (Bulk Scan)
3. ❌ Endpoint tasarımı eksik (CSV Export)
4. ❌ Mantık belirsiz (Priority Score)
5. ❌ Yanlış sorumluluk ataması (Email Templates)

### Öneriler:
1. ✅ MVP scope'unda olanlar ayrılmalı
2. ✅ Post-MVP özellikler açıkça belirtilmeli
3. ✅ Risk analizi eklenmeli
4. ✅ Endpoint tasarımı detaylandırılmalı
5. ✅ Mantık netleştirilmeli

### Hızlı Düzeltmeler:
1. **Priority Score** - Mantık netleştirildikten sonra MVP scope'unda olabilir
2. **Dashboard** - Quick win, MVP scope'unda olabilir
3. **CSV Export** - Post-MVP ama endpoint tasarımı detaylandırılmalı
4. **Bulk Scan** - Post-MVP, async queue gereksinimi belirtilmeli

---

**Not:** Bu critique, SALES-FEATURE-REQUESTS.md'nin teknik gerçekçilik ve MVP scope uyumluluğunu iyileştirmek için hazırlanmıştır.

