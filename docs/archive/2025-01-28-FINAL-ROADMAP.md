# Final Roadmap - Post-MVP Sprint 2-6

**Tarih**: 2025-11-14  
**Durum**: Planlama Tamamlandı  
**Kapsam**: Post-MVP Sprint 2-6 (G15-G20)

---

## 📋 Genel Bakış

Bu roadmap, kritik değerlendirme sonrası temizlenmiş ve gerçekçi hale getirilmiş sprint planını içerir.

**Temel Prensipler:**
- ✅ Scope creep yok
- ✅ Bağımlılıklar doğru sırada
- ✅ Teknik zorluklar gerçekçi
- ✅ Mevcut sistemler kullanılıyor (gereksiz duplikasyon yok)

---

## 🎯 Sprint Özeti

| Sprint | Phase | Odak | Süre | Durum |
|--------|-------|------|------|-------|
| **Sprint 1** | G14 | MVP Kapanış | ✅ Tamamlandı | ✅ Completed |
| **Sprint 2** | G15 | Bulk Scan & Async | 1-2 hafta | 📋 Planlandı |
| **Sprint 3** | G16 | Webhook + Basit Enrichment | 1 hafta | 📋 Planlandı |
| **Sprint 4** | G17 | Notes/Tags/Favorites + PDF | 2 hafta | 📋 Planlandı |
| **Sprint 5** | G18 | ReScan + Alerts + Enhanced Scoring | 2 hafta | 📋 Planlandı |
| **Sprint 6** | G19 | Auth + UI + Advanced Features | 2-3 hafta | 📋 Planlandı |

---

## 📌 Sprint 1 (G14) – MVP Kapanış ✅

**Durum**: ✅ Tamamlandı

**Kalan İş:**
- [ ] Large dataset export testi (ertelendi, gerçek kullanımda test edilecek)

**Not:** Sprint 1 tamamlandı, MVP kapanış sprint'i olarak işaretlendi.

---

## 📌 Sprint 2 (G15) – Bulk Scan & Async Queue

**Odak**: Core altyapı - Bulk scan için async queue sistemi

**Süre**: 1-2 hafta

### Yapılacaklar

#### Async Queue Infrastructure
- [ ] Queue system seçimi (Celery / RQ / FastAPI BackgroundTasks)
- [ ] Worker configuration
  - Max concurrent tasks per worker
  - Task timeout (15s per domain)
  - Max retries (2 for transient failures)
- [ ] Redis setup (queue + progress tracking)

#### Rate Limiting
- [ ] DNS query rate limiting (10 req/s per worker)
- [ ] WHOIS query rate limiting (5 req/s per worker)
- [ ] Exponential backoff on rate-limit errors

#### Progress Tracking
- [ ] Redis store for job status
- [ ] Polling-based progress endpoint (`GET /scan/bulk/{job_id}`)
- [ ] Status updates (every 5 seconds)
- [ ] Job status model (pending, running, completed, failed)

#### Error Handling
- [ ] Partial failure handling (continue processing remaining domains)
- [ ] Transient error retry (up to 2 times)
- [ ] Permanent error logging
- [ ] Failed domains list in response

#### Timeout Strategy
- [ ] Per-domain timeout (15s: DNS 10s + WHOIS 5s)
- [ ] Job timeout (30 minutes for 100 domains)
- [ ] Client timeout handling (polling-based, no HTTP timeout)

#### API Endpoints
- [ ] `POST /scan/bulk` - Bulk scan endpoint
- [ ] `GET /scan/bulk/{job_id}` - Progress tracking endpoint
- [ ] `GET /scan/bulk/{job_id}/results` - Results endpoint

### Çıkarılanlar (Kritik Değerlendirme Sonrası)

- ❌ Priority Score Engine (zaten var, `app/core/priority.py`)
- ❌ ReScan Infrastructure (erken, Sprint 5'e taşındı)

### Deliverables

- ✅ Bulk scan endpoint çalışıyor
- ✅ Background jobs çalışıyor
- ✅ Progress tracking çalışıyor
- ✅ Rate limiting çalışıyor
- ✅ Error handling çalışıyor

### Bağımlılıklar

- ✅ Sprint 1 tamamlandı (MVP kapanış)
- ✅ Mevcut scan endpoint (`POST /scan/domain`) çalışıyor

---

## 📌 Sprint 3 (G16) – Webhook + Basit Lead Enrichment

**Odak**: Veri akışı - Webhook ingestion + basit lead enrichment

**Süre**: 1 hafta

### Yapılacaklar

#### Webhook Infrastructure
- [ ] `POST /ingest/webhook` endpoint
- [ ] API Key authentication (basit)
- [ ] Payload validation (Pydantic models)
- [ ] Retry logic (exponential backoff)
- [ ] Rate limiting (per API key)
- [ ] Error handling & logging

#### Lead Enrichment (Basit)
- [ ] Schema değişikliği:
  - `companies.contact_emails` (JSONB array)
  - `companies.contact_quality_score` (integer, 0-100)
  - `companies.linkedin_pattern` (string, basit pattern)
- [ ] Enrichment logic:
  - `contact_emails[]` - Webhook'tan gelen (manuel)
  - `contact_quality_score` - Basit hesaplama (email count, domain match)
  - `linkedin_pattern` - Basit string ops (firstname.lastname, f.lastname)

#### API Endpoints
- [ ] `POST /ingest/webhook` - Webhook ingestion
- [ ] `GET /leads/{domain}` - Enrichment fields response'a eklenecek

### Çıkarılanlar (Kritik Değerlendirme Sonrası)

- ❌ Contact Finder Engine (çok karmaşık, Sprint 6+'ya taşındı)
- ❌ Auto-tagging (Sprint 4'e taşındı)
- ❌ SMTP-check (zaten var, contact finder için değil)

### Deliverables

- ✅ Webhook endpoint çalışıyor
- ✅ API Key auth çalışıyor
- ✅ Lead enrichment fields çalışıyor
- ✅ Veri akışı hazır

### Bağımlılıklar

- ✅ Sprint 2 tamamlandı (bulk scan altyapısı)

---

## 📌 Sprint 4 (G17) – Notes/Tags/Favorites + Basit PDF

**Odak**: CRM-lite - Notes, tags, favorites + satış sunumu

**Süre**: 2 hafta

### Yapılacaklar

#### Notes System
- [ ] Schema: `notes` tablosu
  - `id`, `domain`, `note`, `created_at`, `updated_at`
- [ ] CRUD endpoints:
  - `POST /leads/{domain}/notes`
  - `GET /leads/{domain}/notes`
  - `PUT /leads/{domain}/notes/{note_id}`
  - `DELETE /leads/{domain}/notes/{note_id}`

#### Tags System
- [ ] Schema: `tags` tablosu (many-to-many)
  - `id`, `domain`, `tag`, `created_at`
- [ ] CRUD endpoints:
  - `POST /leads/{domain}/tags`
  - `GET /leads/{domain}/tags`
  - `DELETE /leads/{domain}/tags/{tag_id}`
- [ ] Auto-tagging logic:
  - "security-risk" (no SPF + no DKIM)
  - "migration-ready" (Migration segment + score >= 70)
  - "expire-soon" (expires_at < 30 days)
  - "weak-spf" (SPF exists but weak)
  - "google-workspace" (provider = Google)
  - "local-mx" (provider = Local)

#### Favorites System
- [ ] Schema: `favorites` tablosu
  - `id`, `domain`, `user_id` (session-based, auth yok)
- [ ] CRUD endpoints:
  - `POST /leads/{domain}/favorite`
  - `GET /leads?favorite=true`
  - `DELETE /leads/{domain}/favorite`

#### PDF Account Summary (Basit, AI Yok)
- [ ] PDF generation library (ReportLab veya WeasyPrint)
- [ ] PDF template:
  - Provider, SPF/DKIM/DMARC status
  - Expiry date
  - Signals (MX, nameservers)
  - Migration Score, Priority Score
  - Risks (no SPF, no DKIM, DMARC none)
  - **AI Recommendation YOK** (Sprint 6+)
- [ ] Endpoint: `GET /leads/{domain}/summary.pdf`

### Çıkarılanlar (Kritik Değerlendirme Sonrası)

- ❌ AI Recommendation (Sprint 6+'ya taşındı)
- ❌ Microsoft Auth (Sprint 6'ya taşındı, session-based favorites yeterli)

### Deliverables

- ✅ Notes CRUD çalışıyor
- ✅ Tags CRUD çalışıyor
- ✅ Auto-tagging çalışıyor
- ✅ Favorites çalışıyor (session-based)
- ✅ Basit PDF summary çalışıyor (AI olmadan)

### Bağımlılıklar

- ✅ Sprint 3 tamamlandı (webhook + enrichment)

---

## 📌 Sprint 5 (G18) – ReScan + Alerts + Enhanced Scoring

**Odak**: Otomasyon - ReScan jobs + change alerts + enhanced scoring

**Süre**: 2 hafta

### Yapılacaklar

#### ReScan Infrastructure
- [ ] Schema değişikliği (history tables):
  - `signal_change_history` (domain, old_value, new_value, changed_at)
  - `score_change_history` (domain, old_score, new_score, changed_at)
  - `provider_change_history` (zaten var, genişletilecek)
- [ ] ReScan engine:
  - Manual trigger: `POST /scan/{domain}/rescan`
  - Bulk rescan: `POST /scan/bulk/rescan?domain_list=...`
  - Change detection logic

#### Change Detection
- [ ] MX change detection
- [ ] DMARC change detection (none → quarantine/reject)
- [ ] Domain expiry detection (expires_at < 30 days)
- [ ] Score change detection (priority score değişti)

#### Alerts System
- [ ] Notification engine:
  - Email notifications (SMTP)
  - Webhook notifications
  - Slack notifications (optional)
- [ ] Alert triggers:
  - MX changed → alert
  - DMARC added → alert
  - Domain expire soon → alert
  - Priority score changed → alert

#### Enhanced Scoring (AI Yok)
- [ ] Signal-based scoring improvements:
  - DKIM none penalty (mevcut scorer'a ekle)
  - SPF include count (multiple includes = risk)
  - DMARC none penalty (mevcut scorer'a ekle)
- [ ] **AI-enhanced scoring YOK** (Sprint 6+)

#### Scheduler
- [ ] Daily ReScan cron job (Celery beat veya APScheduler)
- [ ] Configurable schedule (daily, weekly, monthly)
- [ ] Background worker setup

### Çıkarılanlar (Kritik Değerlendirme Sonrası)

- ❌ AI-enhanced scoring (Sprint 6+'ya taşındı)
- ❌ Ready-to-Migrate Score v2 (AI-enhanced) → "Enhanced Scoring" (AI olmadan)

### Deliverables

- ✅ ReScan engine çalışıyor
- ✅ Change detection çalışıyor
- ✅ Alerts çalışıyor (email/webhook)
- ✅ Enhanced scoring çalışıyor (AI olmadan)
- ✅ Daily cron job çalışıyor

### Bağımlılıklar

- ✅ Sprint 2 tamamlandı (bulk scan + async queue)
- ✅ Sprint 4 tamamlandı (tags system)

---

## 📌 Sprint 6 (G19) – Auth + UI + Advanced Features

**Odak**: Advanced features - Auth, UI upgrade, AI features (optional)

**Süre**: 2-3 hafta

### Yapılacaklar

#### Microsoft SSO Authentication
- [ ] Microsoft Identity Platform entegrasyonu
- [ ] OAuth 2.0 flow
- [ ] Token validation
- [ ] User management (users tablosu)
- [ ] Session management
- [ ] Token refresh

#### UI / Dashboard Upgrade
- [ ] Lead table upgrade (filters, sorting, pagination)
- [ ] Priority order display
- [ ] PDF preview (in-browser)
- [ ] Score explanation (tooltip/modal)
- [ ] Search functionality
- [ ] Bulk upload UI (file drag-drop)
- [ ] Sales panel (dashboard upgrade)

#### AI Features (Optional)
- [ ] AI Recommendation engine:
  - Migration readiness recommendation
  - Risk assessment recommendation
  - Next steps recommendation
- [ ] AI model integration (OpenAI API veya local model)

#### Contact Finder (Optional)
- [ ] Web scraping (legal/ethical considerations)
- [ ] Pattern generation (firstname.lastname, f.lastname)
- [ ] SMTP-check integration
- [ ] Rate limiting (web scraping için)

### Çıkarılanlar (Kritik Değerlendirme Sonrası)

- ❌ Hiçbir şey çıkarılmadı (Sprint 6 advanced features sprint'i)

### Deliverables

- ✅ Microsoft SSO çalışıyor
- ✅ UI upgrade tamamlandı
- ✅ AI features çalışıyor (optional)
- ✅ Contact Finder çalışıyor (optional)

### Bağımlılıklar

- ✅ Sprint 4 tamamlandı (favorites için auth gerekli)
- ✅ Sprint 5 tamamlandı (alerts için UI gerekli)

---

## 📊 Öncelik Matrisi

| Sprint | Öncelik | Zorluk | Satış Değeri | Teknik Değer |
|--------|---------|--------|--------------|--------------|
| **Sprint 2** | 🔴 Yüksek | 🔴 Yüksek | ⭐⭐⭐ Yüksek | ⭐⭐⭐ Yüksek |
| **Sprint 3** | 🔴 Yüksek | 🟡 Orta | ⭐⭐⭐ Yüksek | ⭐⭐ Orta |
| **Sprint 4** | 🔴 Yüksek | 🟡 Orta | ⭐⭐⭐ Yüksek | ⭐⭐ Orta |
| **Sprint 5** | 🟡 Orta | 🔴 Yüksek | ⭐⭐ Orta | ⭐⭐⭐ Yüksek |
| **Sprint 6** | 🟢 Düşük | 🔴 Yüksek | ⭐⭐ Orta | ⭐⭐ Orta |

---

## 🎯 Başarı Kriterleri

### Sprint 2
- ✅ 100 domain bulk scan < 5 dakika
- ✅ Progress tracking çalışıyor
- ✅ Rate limiting çalışıyor

### Sprint 3
- ✅ Webhook endpoint çalışıyor
- ✅ API Key auth çalışıyor
- ✅ Lead enrichment fields response'da

### Sprint 4
- ✅ Notes/Tags/Favorites CRUD çalışıyor
- ✅ Auto-tagging çalışıyor
- ✅ PDF summary oluşturuluyor

### Sprint 5
- ✅ ReScan engine çalışıyor
- ✅ Change detection çalışıyor
- ✅ Alerts çalışıyor (email/webhook)

### Sprint 6
- ✅ Microsoft SSO çalışıyor
- ✅ UI upgrade tamamlandı
- ✅ AI features çalışıyor (optional)

---

## 📝 Notlar

### Scope Discipline
- ✅ AI features sadece Sprint 6'da (optional)
- ✅ Contact Finder sadece Sprint 6'da (optional)
- ✅ Mevcut sistemler kullanılıyor (Priority Score zaten var)

### Bağımlılık Yönetimi
- ✅ Bulk scan bitmeden ReScan yapılmıyor
- ✅ Tags CRUD bitmeden Auto-Tagging yapılmıyor
- ✅ Async queue bitmeden Scheduler yapılmıyor

### Teknik Borç vs Satış Değeri
- ✅ Satış değeri yüksek özelliklere odaklanıldı (Bulk Scan, Webhook, Notes/Tags)
- ✅ Teknik borç yaratacak özellikler ertelendi (Contact Finder, AI)

---

**Son Güncelleme**: 2025-11-14  
**Durum**: Final roadmap hazır, sprint planları oluşturulacak

