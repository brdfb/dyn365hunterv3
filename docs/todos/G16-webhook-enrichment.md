# TODO: Sprint 3 (G16) - Webhook + Basit Lead Enrichment

**Date Created**: 2025-11-14  
**Status**: 📋 Planned  
**Phase**: G16 (Post-MVP Sprint 3)  
**Süre**: 1 hafta

---

## 🎯 Sprint Hedefi

Veri akışı - Webhook ingestion + basit lead enrichment.

**Strateji**: Sadece webhook + basit enrichment, Contact Finder ve Auto-tagging çıkarıldı (kritik değerlendirme sonrası).

---

## 📋 Tasks

### Webhook Infrastructure

- [ ] `POST /ingest/webhook` endpoint
  - [ ] Request model (Pydantic)
  - [ ] Payload validation
  - [ ] Domain extraction from payload
  - [ ] Company name extraction from payload

- [ ] API Key authentication
  - [ ] API Key model (database table)
  - [ ] API Key validation middleware
  - [ ] API Key generation endpoint (admin)
  - [ ] Rate limiting per API key

- [ ] Retry logic
  - [ ] Exponential backoff
  - [ ] Max retries (3)
  - [ ] Retry queue (failed webhooks)

- [ ] Error handling & logging
  - [ ] Error logging
  - [ ] Error response format
  - [ ] Webhook failure tracking

### Lead Enrichment (Basit)

- [ ] Schema değişikliği
  - [ ] `companies.contact_emails` (JSONB array)
  - [ ] `companies.contact_quality_score` (integer, 0-100)
  - [ ] `companies.linkedin_pattern` (string, basit pattern)
  - [ ] Migration script

- [ ] Enrichment logic
  - [ ] `contact_emails[]` - Webhook'tan gelen (manuel)
  - [ ] `contact_quality_score` - Basit hesaplama:
    - Email count (daha fazla email = daha yüksek score)
    - Domain match (email domain = company domain)
  - [ ] `linkedin_pattern` - Basit string ops:
    - `firstname.lastname@domain.com`
    - `f.lastname@domain.com`
    - `firstname@domain.com`

- [ ] Enrichment endpoint
  - [ ] `POST /leads/{domain}/enrich` (manuel enrichment)
  - [ ] Webhook'tan otomatik enrichment

### API Endpoints

- [ ] `POST /ingest/webhook` endpoint
  - [ ] Request: `{ "domain": "...", "company_name": "...", "contact_emails": [...] }`
  - [ ] Response: `{ "status": "success", "domain": "...", "ingested": true }`

- [ ] `GET /leads/{domain}` endpoint güncelleme
  - [ ] Enrichment fields response'a eklenecek:
    - `contact_emails: List[str]`
    - `contact_quality_score: int`
    - `linkedin_pattern: str`

- [ ] `POST /leads/{domain}/enrich` endpoint (opsiyonel)
  - [ ] Manuel enrichment trigger

### Testing

- [ ] Unit tests
  - [ ] Webhook endpoint tests
  - [ ] API Key auth tests
  - [ ] Enrichment logic tests
  - [ ] Retry logic tests

- [ ] Integration tests
  - [ ] Webhook ingestion end-to-end test
  - [ ] Enrichment end-to-end test
  - [ ] Rate limiting test

### Documentation

- [ ] API documentation
  - [ ] `POST /ingest/webhook` endpoint docs
  - [ ] API Key generation docs
  - [ ] Enrichment fields docs

- [ ] README.md güncellemesi
  - [ ] Webhook kullanımı
  - [ ] API Key setup

- [ ] CHANGELOG.md güncellemesi
  - [ ] G16: Webhook + Lead Enrichment added

---

## ✅ Acceptance Criteria

- [ ] `POST /ingest/webhook` endpoint çalışıyor
- [ ] API Key auth çalışıyor
- [ ] Retry logic çalışıyor (exponential backoff)
- [ ] Rate limiting çalışıyor (per API key)
- [ ] Lead enrichment fields response'da (`contact_emails`, `contact_quality_score`, `linkedin_pattern`)
- [ ] Tests passing (≥8 test cases)

---

## 📝 Notes

### Çıkarılanlar (Kritik Değerlendirme Sonrası)

- ❌ Contact Finder Engine (çok karmaşık, Sprint 6+'ya taşındı)
- ❌ Auto-tagging (Sprint 4'e taşındı)
- ❌ SMTP-check (zaten var, contact finder için değil)

### Bağımlılıklar

- ✅ Sprint 2 tamamlandı (bulk scan altyapısı)

### Risk Mitigation

- **API Key auth**: Basit API key yeterli (OAuth gerekli değil, Sprint 6'da Microsoft SSO olacak)
- **Enrichment**: Basit hesaplama yeterli (ML/AI gerekli değil)
- **Webhook payload**: Esnek payload format (farklı kaynaklar için)

---

**Son Güncelleme**: 2025-11-14  
**Sprint Başlangıç**: TBD  
**Sprint Bitiş**: TBD

