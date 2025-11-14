# Satış Ekibi İçin Özellik Önerileri

**Tarih**: 2025-01-27  
**Perspektif**: Satış Ekibi İhtiyaçları  
**Amaç**: İşleri kolaylaştıracak ek özellikler

---

## 🎯 MVP Scope'unda Olanlar (✅ TAMAMLANDI)

### 1. **Öncelik Skoru (Priority Score)** ⭐⭐ ✅ TAMAMLANDI

**Durum:** ✅ Tamamlandı (v0.4.0)

**Implementasyon:**
- ✅ `app/core/priority.py` - Priority score calculation module
- ✅ `calculate_priority_score()` - Priority scoring logic
- ✅ `GET /leads` ve `GET /leads/{domain}` endpoint'lerinde priority_score döndürülüyor
- ✅ Priority levels: 1 (highest) to 6 (lowest)
- ✅ Response model'e `priority_score: Optional[int]` eklendi

**Çözüm:**
```
Response'a priority_score ekle:
- Migration + Score 80+ → Priority: 1 (En yüksek)
- Migration + Score 70-79 → Priority: 2
- Existing + Score 70+ → Priority: 3
- Existing + Score 50-69 → Priority: 4
- Cold + Score 40+ → Priority: 5
- Diğerleri → Priority: 6
```

**Fayda:**
- ✅ Daha kolay önceliklendirme
- ✅ Sıralama daha anlaşılır
- ✅ Zaman yönetimi kolaylaşır

**Öncelik**: ✅ Tamamlandı - MVP scope'unda

---

### 2. **Dashboard/Özet Görünüm** ⭐⭐ ✅ TAMAMLANDI

**Durum:** ✅ Tamamlandı (v0.4.0)

**Implementasyon:**
- ✅ `app/api/dashboard.py` - Dashboard statistics endpoint
- ✅ `GET /dashboard` endpoint implement edildi
- ✅ Segment dağılımı, ortalama skor, yüksek öncelikli lead sayısı
- ✅ `leads_ready` VIEW kullanılıyor
- ✅ Boş veritabanı durumu handle ediliyor

**Çözüm:**
```
GET /dashboard
→ {
  "total_leads": 150,
  "migration": 25,
  "existing": 50,
  "cold": 60,
  "skip": 15,
  "avg_score": 55,
  "high_priority": 10
}
```

**Fayda:**
- ✅ Hızlı özet görünüm
- ✅ Segment dağılımı
- ✅ İstatistikler

**Öncelik**: ✅ Tamamlandı - MVP scope'unda (Quick Win: 1 gün)

---

## 🔴 Post-MVP - Yüksek Öncelik (Satış Ekibi İstiyor Ama MVP Scope'unda Değil)

### 3. **CSV Export - Lead Listesini Excel'e Aktarma** ⭐⭐⭐

**Sorun:**
- Lead listesini Excel'de çalışmak için manuel kopyala-yapıştır yapmak gerekiyor
- Filtrelenmiş sonuçları export edemiyoruz
- CRM'e aktarmak için format dönüşümü gerekiyor

**Çözüm:**
```
GET /leads/export?segment=Migration&min_score=70&provider=M365&format=csv
→ CSV file download (Content-Type: text/csv; charset=utf-8)
```

**Endpoint Tasarımı (Detaylandırıldı):**

**Request:**
- **Method**: `GET`
- **Path**: `/leads/export`
- **Query Parameters**:
  - `segment` (optional): Filter by segment (Migration, Existing, Cold, Skip)
  - `min_score` (optional): Minimum readiness score (0-100)
  - `provider` (optional): Filter by provider (M365, Google, etc.)
  - `format` (required): Export format (`csv` - only format supported initially)
  - `limit` (optional): Maximum number of records (default: 10000, max: 50000)
  - `offset` (optional): Pagination offset (default: 0)
- **Response**:
  - **Content-Type**: `text/csv; charset=utf-8`
  - **Content-Disposition**: `attachment; filename="leads_export_YYYY-MM-DD_HH-MM-SS.csv"`
  - **Body**: CSV content with headers
- **CSV Columns**:
  - `domain`, `canonical_name`, `provider`, `country`, `readiness_score`, `segment`, `priority_score`, `mx_root`, `spf`, `dkim`, `dmarc_policy`, `registrar`, `expires_at`, `scan_status`, `scanned_at`
- **Error Handling**:
  - `400 Bad Request`: Invalid parameters (e.g., limit > 50000)
  - `500 Internal Server Error`: Export generation failure
- **Pagination**:
  - For datasets > 10000 records, use `limit` and `offset` parameters
  - Client should make multiple requests if needed
  - Response includes `X-Total-Count` header for total record count

**Fayda:**
- ✅ Excel'de filtreleme/sıralama yapabiliriz
- ✅ CRM'e kolayca aktarabiliriz
- ✅ Raporlama için kullanabiliriz
- ✅ Takım içi paylaşım kolaylaşır

**Öncelik**: 🔴 Yüksek - Post-MVP (MVP scope'unda değil)

---

### 4. **Toplu Analiz (Bulk Scan)** ⭐⭐⭐

**Sorun:**
- CSV'den 100 domain ekledik ama her birini tek tek analiz etmek zorundayız
- 100 domain için 20-25 dakika sürüyor
- Manuel işlem çok zaman alıyor

**Çözüm (Async Queue ile):**
```
POST /scan/bulk
{
  "domains": ["domain1.com", "domain2.com", ...],
  "max_concurrent": 5
}
→ 202 Accepted
{
  "job_id": "uuid-here",
  "status": "queued",
  "total_domains": 100,
  "message": "Bulk scan job queued. Use GET /scan/bulk/{job_id} to check status."
}

GET /scan/bulk/{job_id}
→ 200 OK
{
  "job_id": "uuid-here",
  "status": "processing" | "completed" | "failed",
  "total_domains": 100,
  "completed": 45,
  "failed": 2,
  "pending": 53,
  "progress": 45.0,
  "results": [...],  // Only if status="completed"
  "errors": [...]     // Only if any failures
}
```

**Endpoint Tasarımı (Detaylandırıldı):**

**Request (POST /scan/bulk):**
- **Method**: `POST`
- **Path**: `/scan/bulk`
- **Body**:
  ```json
  {
    "domains": ["domain1.com", "domain2.com", ...],  // Required, max 1000 domains
    "max_concurrent": 5  // Optional, default: 5, max: 10
  }
  ```
- **Response**: `202 Accepted`
  ```json
  {
    "job_id": "uuid-here",
    "status": "queued",
    "total_domains": 100,
    "message": "Bulk scan job queued"
  }
  ```

**Status Check (GET /scan/bulk/{job_id}):**
- **Method**: `GET`
- **Path**: `/scan/bulk/{job_id}`
- **Response**: `200 OK`
  ```json
  {
    "job_id": "uuid-here",
    "status": "queued" | "processing" | "completed" | "failed",
    "total_domains": 100,
    "completed": 45,
    "failed": 2,
    "pending": 53,
    "progress": 45.0,
    "started_at": "2025-01-27T10:00:00Z",
    "completed_at": null,
    "results": [...],  // Only if status="completed"
    "errors": [...]    // Only if any failures
  }
  ```

**Async Queue Mimarisi:**
- **Queue System**: Redis + Celery
- **Worker Configuration**:
  - Max concurrent tasks per worker: 5 (configurable)
  - Task timeout: 15s per domain (DNS: 10s, WHOIS: 5s)
  - Max retries: 2 (for transient failures)
- **Rate Limiting**:
  - DNS queries: 10 requests/second per worker
  - WHOIS queries: 5 requests/second per worker
  - Exponential backoff on rate-limit errors
- **Progress Tracking**:
  - Redis store for job status
  - Polling-based (client polls GET /scan/bulk/{job_id})
  - Status updates every 5 seconds
- **Error Handling**:
  - Partial failures: Continue processing remaining domains
  - Transient errors: Retry up to 2 times
  - Permanent errors: Log and continue
  - Failed domains listed in `errors` array
- **Timeout Strategy**:
  - Per-domain timeout: 15s (DNS: 10s, WHOIS: 5s)
  - Job timeout: 30 minutes (for 100 domains)
  - Client timeout: Use polling, no HTTP timeout

**Fayda:**
- ✅ 100 domain'i tek seferde analiz edebiliriz
- ✅ Zaman tasarrufu (20 dakika → 5 dakika with async)
- ✅ Progress tracking (polling-based)
- ✅ Hata durumunda devam eder (partial failure handling)
- ✅ Rate-limit koruması (exponential backoff)

**Öncelik**: 🔴 Yüksek - Post-MVP (MVP scope'unda değil, async queue gerektirir)

---

## 🟡 Post-MVP - Orta/Düşük Öncelik

### 5. **Email Template'leri** ⭐⭐

**Sorun:**
- Her segment için farklı email yazmak gerekiyor
- Standart template'ler yok
- Zaman kaybı

**Çözüm:**
```
GET /templates?segment=Migration
→ Hazır email template'leri döner

Örnek:
- Migration segment için: "Migration teklifi" template'i
- Existing segment için: "Upsell teklifi" template'i
- Cold segment için: "Bilgilendirme" template'i
```

**Fayda:**
- ✅ Hızlı email hazırlama
- ✅ Tutarlı mesajlaşma
- ✅ Zaman tasarrufu

**Not:** Bu frontend/CRM'in sorumluluğu, API'nin görevi değil. Content management gerektirir.

**Öncelik**: 🟢 Düşük - Post-MVP (API sorumluluğu değil)

---

## 🟢 Post-MVP - Düşük Öncelik (Database Schema Değişikliği Gerektirir)

### 6. **Lead'lere Not/Etiket Ekleme** ⭐

**Sorun:**
- Lead'lerle ilgili notları başka yerde tutmak zorundayız
- "Bu lead'i aradım, görüşme yapıldı" gibi bilgileri kaydedemiyoruz
- Takım içi bilgi paylaşımı zor

**Çözüm:**
```
POST /leads/{domain}/notes
{
  "note": "Arama yapıldı, görüşme planlandı",
  "tags": ["contacted", "meeting-scheduled"]
}

GET /leads/{domain}
→ notes ve tags bilgisi döner
```

**Fayda:**
- ✅ Lead geçmişi takibi
- ✅ Takım içi bilgi paylaşımı
- ✅ Daha iyi organizasyon

**Not:** Database schema değişikliği gerektirir (yeni tablo veya column). Migration planı gerekli.

**Öncelik**: 🟢 Düşük - Post-MVP (Schema değişikliği)

---

### 7. **Favoriler/İşaretleme** ⭐

**Sorun:**
- Önemli lead'leri işaretleyemiyoruz
- Her seferinde filtreleme yapmak gerekiyor
- "Takip etmem gerekenler" listesi yok

**Çözüm:**
```
POST /leads/{domain}/favorite
GET /leads?favorite=true
```

**Fayda:**
- ✅ Önemli lead'leri hızlıca bulma
- ✅ Kişisel takip listesi
- ✅ Daha iyi organizasyon

**Not:** Authentication gerektirir (kimin favorisi?). Database schema değişikliği gerekli.

**Öncelik**: 🟢 Düşük - Post-MVP (Auth + Schema değişikliği)

---

### 8. **Takip Hatırlatıcıları** ⭐

**Sorun:**
- "Bu lead'i 1 ay sonra tekrar kontrol et" diyoruz ama unutuyoruz
- Segment'e göre takip zamanı belirleyemiyoruz
- Manuel takip zor

**Çözüm:**
```
POST /leads/{domain}/reminder
{
  "reminder_date": "2025-02-27",
  "note": "Cold segment, 1 ay sonra tekrar kontrol"
}

GET /leads/reminders?date=2025-02-27
→ O gün takip edilmesi gereken lead'ler
```

**Fayda:**
- ✅ Otomatik hatırlatma
- ✅ Düzenli takip
- ✅ Hiçbir lead kaçmaz

**Not:** Scheduler/background job gerektirir. `.cursorrules`'da scheduler **OUT OF SCOPE** olarak belirtilmiş. Cron job veya task queue gerektirir.

**Öncelik**: 🟢 Düşük - Post-MVP (Scheduler gerektirir)

---

## 📊 Öncelik Matrisi (Düzeltilmiş)

| Özellik | MVP Scope | Öncelik | Zorluk | Etki | Önerilen Sıra |
|---------|-----------|---------|--------|------|----------------|
| **Priority Score** | ✅ MVP | 🟡 Orta | 🟢 Kolay | ⭐⭐ Orta | 1 |
| **Dashboard** | ✅ MVP | 🟡 Orta | 🟢 Kolay | ⭐⭐ Orta | 2 |
| **CSV Export** | ❌ Post-MVP | 🔴 Yüksek | 🟢 Kolay | ⭐⭐⭐ Yüksek | 3 |
| **Bulk Scan** | ❌ Post-MVP | 🔴 Yüksek | 🔴 Yüksek | ⭐⭐⭐ Yüksek | 4 |
| **Email Templates** | ❌ Post-MVP | 🟢 Düşük | 🟡 Orta | ⭐ Düşük | 5 |
| **Notes/Tags** | ❌ Post-MVP | 🟢 Düşük | 🔴 Yüksek | ⭐ Düşük | 6 |
| **Favorites** | ❌ Post-MVP | 🟢 Düşük | 🔴 Yüksek | ⭐ Düşük | 7 |
| **Reminders** | ❌ Post-MVP | 🟢 Düşük | 🔴 Yüksek | ⭐ Düşük | 8 |

---

## 💡 Hızlı Kazanımlar (Quick Wins - MVP Scope'unda) ✅ TAMAMLANDI

### 1. Dashboard (1 gün) ✅ TAMAMLANDI
- ✅ Basit aggregation endpoint
- ✅ Segment dağılımı, toplam lead sayısı
- ✅ Hemen kullanılabilir
- ✅ MVP scope'unda

### 2. Priority Score (Yarım gün) ✅ TAMAMLANDI
- ✅ Response'a field ekleme
- ✅ Mevcut skorlama mantığına ekleme
- ✅ Mantık netleştirildi ve implement edildi
- ✅ MVP scope'unda

---

## 🔴 Post-MVP - Yüksek Öncelik (Satış Ekibi İstiyor)

### 3. CSV Export (1-2 gün)
- En kolay implementasyon
- En yüksek fayda
- **Ama:** Endpoint tasarımı detaylandırılmalı
- Post-MVP

### 4. Bulk Scan (1-2 hafta - Async Queue ile)
- Zaman tasarrufu çok yüksek
- Satış ekibinin en çok istediği özellik
- **Ama:** Async queue gerektirir (Redis/Celery)
- **Ama:** Timeout/rate-limit stratejisi gerekli
- Post-MVP

---

## 🎯 Önerilen Yaklaşım

### Faz 1: MVP Scope'unda Hızlı Kazanımlar (1 hafta) ✅ TAMAMLANDI
1. ✅ Dashboard (1 gün) - Quick win - **TAMAMLANDI (v0.4.0)**
2. ✅ Priority Score (yarım gün) - Mantık netleştirildikten sonra - **TAMAMLANDI (v0.4.0)**

### Faz 2: Post-MVP - Yüksek Öncelik (2-3 hafta)
3. ✅ CSV Export (1-2 gün) - Endpoint tasarımı detaylandırılmalı
4. ✅ Bulk Scan (1-2 hafta) - Async queue ile

### Faz 3: Post-MVP - İyileştirmeler (Sonra)
5. ✅ Email Templates (API sorumluluğu değil)
6. ✅ Notes/Tags (Schema değişikliği)
7. ✅ Favorites (Auth + Schema)
8. ✅ Reminders (Scheduler)

---

## ❓ Satış Ekibine Sorulacak Sorular

1. **CSV Export** - "Lead listesini Excel'e aktarmak ister misiniz?"
   - Beklenen cevap: ✅ Evet, kesinlikle

2. **Bulk Scan** - "100 domain'i tek seferde analiz etmek ister misiniz?"
   - Beklenen cevap: ✅ Evet, çok zaman kazandırır

3. **Priority Score** - "Daha kolay önceliklendirme için priority score ister misiniz?"
   - Beklenen cevap: ✅ Evet, iyi olur

4. **Email Templates** - "Hazır email template'leri ister misiniz?"
   - Beklenen cevap: 🟡 Belki, sonra

5. **Notes/Tags** - "Lead'lere not eklemek ister misiniz?"
   - Beklenen cevap: 🟡 Belki, sonra

---

## 📝 Sonuç

### MVP Scope'unda Olanlar (✅ TAMAMLANDI):
1. **Dashboard** (⭐⭐) ✅ **TAMAMLANDI (v0.4.0)** - Quick win, 1 gün
2. **Priority Score** (⭐⭐) ✅ **TAMAMLANDI (v0.4.0)** - Mantık netleştirildikten sonra, yarım gün

### Post-MVP - Yüksek Öncelik (Satış Ekibi İstiyor):
1. **CSV Export** (⭐⭐⭐) - 1-2 gün, endpoint tasarımı detaylandırılmalı
2. **Bulk Scan** (⭐⭐⭐) - 1-2 hafta, async queue gerektirir

### Post-MVP - Düşük Öncelik:
- Email Templates (API sorumluluğu değil)
- Notes/Tags (Schema değişikliği)
- Favorites (Auth + Schema)
- Reminders (Scheduler)

**Hızlı Başlangıç (MVP Scope'unda):**
- Dashboard + Priority Score = 1.5 gün
- Hemen kullanılabilir
- Orta fayda

**Post-MVP (Satış Ekibi İstiyor):**
- CSV Export = 1-2 gün (endpoint tasarımı detaylandırılmalı)
- Bulk Scan = 1-2 hafta (async queue gerektirir)
- Zaman tasarrufu çok yüksek

---

**Not:** 
- MVP scope'unda olanlar: Dashboard, Priority Score (mantık netleştirildikten sonra)
- Post-MVP özellikler: CSV Export, Bulk Scan, Email Templates, Notes/Tags, Favorites, Reminders
- Detaylı critique için: `SALES-FEATURE-REQUESTS-CRITIQUE.md`

