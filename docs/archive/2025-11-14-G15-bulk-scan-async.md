# TODO: Sprint 2 (G15) - Bulk Scan & Async Queue

**Date Created**: 2025-11-14  
**Status**: 📋 Planned  
**Phase**: G15 (Post-MVP Sprint 2)  
**Süre**: 1-2 hafta

---

## 🎯 Sprint Hedefi

Core altyapı - Bulk scan için async queue sistemi kurulacak.

**Strateji**: Sadece altyapı, ek fantezi yok. Priority Score Engine ve ReScan çıkarıldı (kritik değerlendirme sonrası).

---

## 📋 Tasks

### Async Queue Infrastructure

- [ ] Queue system seçimi
  - [ ] Celery / RQ / FastAPI BackgroundTasks karşılaştırması
  - [ ] Seçim yapılacak (öneri: Celery - production-ready)
  - [ ] Redis setup (queue + progress tracking)

- [ ] Worker configuration
  - [ ] Max concurrent tasks per worker (5 önerilir)
  - [ ] Task timeout (15s per domain: DNS 10s + WHOIS 5s)
  - [ ] Max retries (2 for transient failures)
  - [ ] Worker startup script

### Rate Limiting

- [ ] DNS query rate limiting
  - [ ] 10 requests/second per worker
  - [ ] Rate limit detection
  - [ ] Exponential backoff on rate-limit errors

- [ ] WHOIS query rate limiting
  - [ ] 5 requests/second per worker
  - [ ] Rate limit detection
  - [ ] Exponential backoff on rate-limit errors

### Progress Tracking

- [ ] Redis store for job status
  - [ ] Job status model (pending, running, completed, failed)
  - [ ] Progress percentage calculation
  - [ ] Status updates (every 5 seconds)

- [ ] Polling-based progress endpoint
  - [ ] `GET /scan/bulk/{job_id}` endpoint
  - [ ] Response model (status, progress, processed, total, errors)
  - [ ] Results endpoint: `GET /scan/bulk/{job_id}/results`

### Error Handling

- [ ] Partial failure handling
  - [ ] Continue processing remaining domains on error
  - [ ] Failed domains list in response
  - [ ] Error categorization (transient vs permanent)

- [ ] Transient error retry
  - [ ] Retry up to 2 times
  - [ ] Exponential backoff

- [ ] Permanent error logging
  - [ ] Error logging to database
  - [ ] Error details in response

### Timeout Strategy

- [ ] Per-domain timeout
  - [ ] 15s total (DNS: 10s, WHOIS: 5s)
  - [ ] Timeout handling in scan logic

- [ ] Job timeout
  - [ ] 30 minutes for 100 domains
  - [ ] Job cancellation on timeout

- [ ] Client timeout handling
  - [ ] Polling-based (no HTTP timeout)
  - [ ] Client-side timeout handling

### API Endpoints

- [ ] `POST /scan/bulk` endpoint
  - [ ] Request model (domain_list: List[str])
  - [ ] Job creation
  - [ ] Job ID return

- [ ] `GET /scan/bulk/{job_id}` endpoint
  - [ ] Progress tracking
  - [ ] Status, progress, processed, total, errors

- [ ] `GET /scan/bulk/{job_id}/results` endpoint
  - [ ] Results return (completed jobs only)
  - [ ] Results format (List[LeadResponse])

### Testing

- [ ] Unit tests
  - [ ] Queue system tests
  - [ ] Rate limiting tests
  - [ ] Progress tracking tests
  - [ ] Error handling tests

- [ ] Integration tests
  - [ ] Bulk scan end-to-end test
  - [ ] Progress tracking test
  - [ ] Partial failure test

- [ ] Performance tests
  - [ ] 100 domain bulk scan < 5 dakika
  - [ ] Rate limiting test
  - [ ] Memory usage test

### Documentation

- [ ] API documentation
  - [ ] `POST /scan/bulk` endpoint docs
  - [ ] `GET /scan/bulk/{job_id}` endpoint docs
  - [ ] `GET /scan/bulk/{job_id}/results` endpoint docs

- [ ] README.md güncellemesi
  - [ ] Bulk scan kullanımı
  - [ ] Progress tracking kullanımı

- [ ] CHANGELOG.md güncellemesi
  - [ ] G15: Bulk Scan + Async Queue added

---

## ✅ Acceptance Criteria

- [ ] `POST /scan/bulk` endpoint çalışıyor
- [ ] Background jobs çalışıyor (Celery/RQ)
- [ ] Progress tracking çalışıyor (`GET /scan/bulk/{job_id}`)
- [ ] Rate limiting çalışıyor (DNS: 10 req/s, WHOIS: 5 req/s)
- [ ] Error handling çalışıyor (partial failure, retry)
- [ ] 100 domain bulk scan < 5 dakika
- [ ] Tests passing (≥10 test cases)

---

## 📝 Notes

### Çıkarılanlar (Kritik Değerlendirme Sonrası)

- ❌ Priority Score Engine (zaten var, `app/core/priority.py`)
- ❌ ReScan Infrastructure (erken, Sprint 5'e taşındı)

### Bağımlılıklar

- ✅ Sprint 1 tamamlandı (MVP kapanış)
- ✅ Mevcut scan endpoint (`POST /scan/domain`) çalışıyor

### Risk Mitigation

- **Queue system seçimi**: Celery önerilir (production-ready, Redis support)
- **Rate limiting**: Exponential backoff kritik (DNS/WHOIS rate-limit'e takılabilir)
- **Progress tracking**: Redis kullan (DB yerine, performans için)

---

**Son Güncelleme**: 2025-11-14  
**Sprint Başlangıç**: 2025-11-14  
**Sprint Bitiş**: 2025-11-14 ✅  
**Durum**: ✅ Sprint tamamlandı
- Implementation tamamlandı ✅
- Tests yazıldı (19+ test cases) ✅
- Documentation güncellendi (README, CHANGELOG) ✅

