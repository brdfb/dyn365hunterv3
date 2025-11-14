# TODO: Sprint 4 (G17) - Notes/Tags/Favorites + Basit PDF

**Date Created**: 2025-11-14  
**Status**: ✅ Completed  
**Phase**: G17 (Post-MVP Sprint 4)  
**Süre**: 2 hafta

---

## 🎯 Sprint Hedefi

CRM-lite - Notes, tags, favorites + satış sunumu (basit PDF).

**Strateji**: CRM-lite sprint, AI ve Microsoft Auth çıkarıldı (kritik değerlendirme sonrası).

---

## 📋 Tasks

### Notes System

- [x] Schema: `notes` tablosu
  - [x] `id` (primary key)
  - [x] `domain` (foreign key to companies.domain)
  - [x] `note` (text)
  - [x] `created_at` (timestamp)
  - [x] `updated_at` (timestamp)
  - [x] Migration script

- [x] CRUD endpoints
  - [x] `POST /leads/{domain}/notes` - Create note
  - [x] `GET /leads/{domain}/notes` - List notes
  - [x] `PUT /leads/{domain}/notes/{note_id}` - Update note
  - [x] `DELETE /leads/{domain}/notes/{note_id}` - Delete note

### Tags System

- [x] Schema: `tags` tablosu (many-to-many)
  - [x] `id` (primary key)
  - [x] `domain` (foreign key to companies.domain)
  - [x] `tag` (string, unique per domain)
  - [x] `created_at` (timestamp)
  - [x] Migration script

- [x] CRUD endpoints
  - [x] `POST /leads/{domain}/tags` - Add tag
  - [x] `GET /leads/{domain}/tags` - List tags
  - [x] `DELETE /leads/{domain}/tags/{tag_id}` - Remove tag

- [x] Auto-tagging logic
  - [x] "security-risk" (no SPF + no DKIM)
  - [x] "migration-ready" (Migration segment + score >= 70)
  - [x] "expire-soon" (expires_at < 30 days)
  - [x] "weak-spf" (SPF exists but weak)
  - [x] "google-workspace" (provider = Google)
  - [x] "local-mx" (provider = Local)
  - [x] Auto-tagging trigger (scan sonrası)

### Favorites System

- [x] Schema: `favorites` tablosu
  - [x] `id` (primary key)
  - [x] `domain` (foreign key to companies.domain)
  - [x] `user_id` (string, session-based, auth yok)
  - [x] `created_at` (timestamp)
  - [x] Migration script

- [x] CRUD endpoints
  - [x] `POST /leads/{domain}/favorite` - Add favorite
  - [x] `GET /leads?favorite=true` - List favorites
  - [x] `DELETE /leads/{domain}/favorite` - Remove favorite

### PDF Account Summary (Basit, AI Yok)

- [x] PDF generation library
  - [x] ReportLab veya WeasyPrint seçimi
  - [x] Dependency ekleme

- [x] PDF template
  - [x] Provider bilgisi
  - [x] SPF/DKIM/DMARC status
  - [x] Expiry date
  - [x] Signals (MX, nameservers)
  - [x] Migration Score, Priority Score
  - [x] Risks (no SPF, no DKIM, DMARC none)
  - [x] **AI Recommendation YOK** (Sprint 6+)

- [x] Endpoint: `GET /leads/{domain}/summary.pdf`
  - [x] PDF generation
  - [x] File download response

### API Endpoints

- [x] Notes endpoints (4 endpoint)
- [x] Tags endpoints (3 endpoint)
- [x] Favorites endpoints (3 endpoint)
- [x] PDF endpoint (1 endpoint)

### Testing

- [x] Unit tests
  - [x] Notes CRUD tests
  - [x] Tags CRUD tests
  - [x] Favorites CRUD tests
  - [x] Auto-tagging logic tests
  - [x] PDF generation tests

- [x] Integration tests
  - [x] Notes end-to-end test
  - [x] Tags end-to-end test
  - [x] Favorites end-to-end test
  - [x] PDF generation end-to-end test

### Documentation

- [x] API documentation
  - [x] Notes endpoints docs
  - [x] Tags endpoints docs
  - [x] Favorites endpoints docs
  - [x] PDF endpoint docs

- [x] README.md güncellemesi
  - [x] Notes/Tags/Favorites kullanımı
  - [x] PDF summary kullanımı

- [x] CHANGELOG.md güncellemesi
  - [x] G17: Notes/Tags/Favorites + PDF Summary added

---

## ✅ Acceptance Criteria

- [x] Notes CRUD çalışıyor (4 endpoint)
- [x] Tags CRUD çalışıyor (3 endpoint)
- [x] Auto-tagging çalışıyor (6 tag type)
- [x] Favorites çalışıyor (session-based, 3 endpoint)
- [x] PDF summary oluşturuluyor (AI olmadan)
- [x] Tests passing (≥12 test cases)

---

## 📝 Notes

### Çıkarılanlar (Kritik Değerlendirme Sonrası)

- ❌ AI Recommendation (Sprint 6+'ya taşındı)
- ❌ Microsoft Auth (Sprint 6'ya taşındı, session-based favorites yeterli)

### Bağımlılıklar

- ✅ Sprint 3 tamamlandı (webhook + enrichment)

### Risk Mitigation

- **PDF generation**: ReportLab önerilir (Python-native, WeasyPrint HTML gerektirir)
- **Auto-tagging**: Basit logic yeterli (ML/AI gerekli değil)
- **Favorites**: Session-based yeterli (auth Sprint 6'da)

---

**Son Güncelleme**: 2025-11-14  
**Sprint Başlangıç**: 2025-11-14  
**Sprint Bitiş**: 2025-11-14  
**Tamamlanma Tarihi**: 2025-11-14

