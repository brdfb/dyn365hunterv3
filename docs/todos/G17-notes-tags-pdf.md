# TODO: Sprint 4 (G17) - Notes/Tags/Favorites + Basit PDF

**Date Created**: 2025-11-14  
**Status**: 📋 Planned  
**Phase**: G17 (Post-MVP Sprint 4)  
**Süre**: 2 hafta

---

## 🎯 Sprint Hedefi

CRM-lite - Notes, tags, favorites + satış sunumu (basit PDF).

**Strateji**: CRM-lite sprint, AI ve Microsoft Auth çıkarıldı (kritik değerlendirme sonrası).

---

## 📋 Tasks

### Notes System

- [ ] Schema: `notes` tablosu
  - [ ] `id` (primary key)
  - [ ] `domain` (foreign key to companies.domain)
  - [ ] `note` (text)
  - [ ] `created_at` (timestamp)
  - [ ] `updated_at` (timestamp)
  - [ ] Migration script

- [ ] CRUD endpoints
  - [ ] `POST /leads/{domain}/notes` - Create note
  - [ ] `GET /leads/{domain}/notes` - List notes
  - [ ] `PUT /leads/{domain}/notes/{note_id}` - Update note
  - [ ] `DELETE /leads/{domain}/notes/{note_id}` - Delete note

### Tags System

- [ ] Schema: `tags` tablosu (many-to-many)
  - [ ] `id` (primary key)
  - [ ] `domain` (foreign key to companies.domain)
  - [ ] `tag` (string, unique per domain)
  - [ ] `created_at` (timestamp)
  - [ ] Migration script

- [ ] CRUD endpoints
  - [ ] `POST /leads/{domain}/tags` - Add tag
  - [ ] `GET /leads/{domain}/tags` - List tags
  - [ ] `DELETE /leads/{domain}/tags/{tag_id}` - Remove tag

- [ ] Auto-tagging logic
  - [ ] "security-risk" (no SPF + no DKIM)
  - [ ] "migration-ready" (Migration segment + score >= 70)
  - [ ] "expire-soon" (expires_at < 30 days)
  - [ ] "weak-spf" (SPF exists but weak)
  - [ ] "google-workspace" (provider = Google)
  - [ ] "local-mx" (provider = Local)
  - [ ] Auto-tagging trigger (scan sonrası)

### Favorites System

- [ ] Schema: `favorites` tablosu
  - [ ] `id` (primary key)
  - [ ] `domain` (foreign key to companies.domain)
  - [ ] `user_id` (string, session-based, auth yok)
  - [ ] `created_at` (timestamp)
  - [ ] Migration script

- [ ] CRUD endpoints
  - [ ] `POST /leads/{domain}/favorite` - Add favorite
  - [ ] `GET /leads?favorite=true` - List favorites
  - [ ] `DELETE /leads/{domain}/favorite` - Remove favorite

### PDF Account Summary (Basit, AI Yok)

- [ ] PDF generation library
  - [ ] ReportLab veya WeasyPrint seçimi
  - [ ] Dependency ekleme

- [ ] PDF template
  - [ ] Provider bilgisi
  - [ ] SPF/DKIM/DMARC status
  - [ ] Expiry date
  - [ ] Signals (MX, nameservers)
  - [ ] Migration Score, Priority Score
  - [ ] Risks (no SPF, no DKIM, DMARC none)
  - [ ] **AI Recommendation YOK** (Sprint 6+)

- [ ] Endpoint: `GET /leads/{domain}/summary.pdf`
  - [ ] PDF generation
  - [ ] File download response

### API Endpoints

- [ ] Notes endpoints (4 endpoint)
- [ ] Tags endpoints (3 endpoint)
- [ ] Favorites endpoints (3 endpoint)
- [ ] PDF endpoint (1 endpoint)

### Testing

- [ ] Unit tests
  - [ ] Notes CRUD tests
  - [ ] Tags CRUD tests
  - [ ] Favorites CRUD tests
  - [ ] Auto-tagging logic tests
  - [ ] PDF generation tests

- [ ] Integration tests
  - [ ] Notes end-to-end test
  - [ ] Tags end-to-end test
  - [ ] Favorites end-to-end test
  - [ ] PDF generation end-to-end test

### Documentation

- [ ] API documentation
  - [ ] Notes endpoints docs
  - [ ] Tags endpoints docs
  - [ ] Favorites endpoints docs
  - [ ] PDF endpoint docs

- [ ] README.md güncellemesi
  - [ ] Notes/Tags/Favorites kullanımı
  - [ ] PDF summary kullanımı

- [ ] CHANGELOG.md güncellemesi
  - [ ] G17: Notes/Tags/Favorites + PDF Summary added

---

## ✅ Acceptance Criteria

- [ ] Notes CRUD çalışıyor (4 endpoint)
- [ ] Tags CRUD çalışıyor (3 endpoint)
- [ ] Auto-tagging çalışıyor (6 tag type)
- [ ] Favorites çalışıyor (session-based, 3 endpoint)
- [ ] PDF summary oluşturuluyor (AI olmadan)
- [ ] Tests passing (≥12 test cases)

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
**Sprint Başlangıç**: TBD  
**Sprint Bitiş**: TBD

