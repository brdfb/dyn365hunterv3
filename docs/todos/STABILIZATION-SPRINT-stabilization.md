# TODO: STABILIZATION-SPRINT - stabilization

**Date Created**: 2025-01-28
**Status**: In Progress
**Phase**: STABILIZATION-SPRINT
**Hedef**: Enterprise-Ready / UI-Stable / Integration-Ready
**Süre**: 3 Gün (18 saat)
**Versiyon**: v1.1 → v1.1-stable

## Gün 1: Core Stabilizasyon (6-7 saat) ✅ TAMAMLANDI

### 1.1 Alembic Stabilizasyon (2 saat) ✅
- [x] Schema drift kontrolü (`alembic check` komutu ekle)
- [x] Dry-run test: `alembic revision --autogenerate --dry-run`
- [x] Schema drift detection script oluştur
- [x] Rollback testleri (test migration oluştur, upgrade/downgrade test)
- [x] `run_migration.py` Alembic'e migrate
- [x] Test dosyası: `tests/test_alembic.py` (10 passed, 1 skipped)

### 1.2 Distributed Rate Limiting Testleri (2 saat) ✅
- [x] Multi-worker rate limiting test (2 worker process, aynı API key)
- [x] Rate limit paylaşımı doğrula (10 req/s DNS, 5 req/s WHOIS)
- [x] Limit aşımı senaryosu test et
- [x] Redis down fallback test (in-memory limiter fallback)
- [x] Test dosyası: `tests/test_distributed_rate_limiter.py` (11 passed)

### 1.3 Bulk Operations Test Düzeltmeleri (2 saat) ✅
- [x] Test isolation sorunlarını çöz (`test_bulk_operations_p1.py` içindeki 3 error)
- [x] Database fixture'ları düzelt (transaction rollback)
- [x] Redis fixture'ları düzelt (test isolation)
- [x] Deadlock recovery testleri (deadlock simulation, retry logic)
- [x] Test düzeltmesi: `sample_domains` fixture unique domain'ler kullanıyor (11 passed, 2 skipped)

### 1.4 API Backward Compatibility Testleri (1 saat) ✅
- [x] Legacy endpoint'ler çalışıyor mu? (`/scan/domain` vs `/api/v1/scan/domain`)
- [x] Dual-path routing test (v1 + legacy aynı anda)
- [x] Zero downtime deployment test
- [x] Response format consistency test
- [x] Test dosyası: `tests/test_api_versioning.py` (response format consistency, zero downtime tests eklendi)
- [x] DB fixture eklendi: Test isolation için `db_session` ve `client` fixture'ları
- [x] Router prefix düzeltmesi: `app/main.py`'de double prefix sorunu çözüldü
- [x] Test sonucu: **15/15 passed** ✅

### 1.5 Redis Health Check (30 dakika) ✅
- [x] `/healthz/ready` endpoint'ine Redis ping ekle
- [x] Redis ping test (connection pool check)
- [x] Redis down durumunda health check fail et
- [x] `app/api/health.py` güncellendi: `get_redis_client()` kullanıyor (connection pool)

## Gün 2: Monitoring ve Safety (6-7 saat)

### 2.1 Cache Hit Metrics (2 saat)
- [ ] Redis cache hit rate monitoring
- [ ] Metrics endpoint ekle (`/metrics/cache` veya `/healthz/metrics`)
- [ ] Cache hit rate hesapla: `hits / (hits + misses) * 100`
- [ ] TTL expiration tracking

### 2.2 Rate Limit Metrics (1 saat)
- [ ] Rate limit hit counter (limit aşımı sayısı)
- [ ] Rate limit per-key metrics (API key bazlı)
- [ ] Circuit breaker state tracking
- [ ] Metrics endpoint'e rate limit stats ekle

### 2.3 Bulk Operations Metrics (1 saat)
- [ ] Batch success/failure rate
- [ ] Average batch processing time
- [ ] Deadlock occurrence count
- [ ] Partial commit recovery count

### 2.4 Error Trend Logging (1 saat)
- [ ] Sentry error categorization (error tags ekle)
- [ ] Error grouping stratejisi (Alembic, Redis, DB, DNS, WHOIS)
- [ ] Error trend tracking (daily/weekly error count)
- [ ] Critical error alerting (Sentry alert rules)

### 2.5 Deadlock Simulation Testleri (1 saat)
- [ ] Concurrent transaction test (2+ transaction aynı anda)
- [ ] Deadlock detection test (PostgreSQL deadlock error)
- [ ] Retry logic test (deadlock sonrası retry)
- [ ] Transaction timeout test (30s timeout)

### 2.6 Cache Invalidation Simulation (1 saat)
- [ ] Rescan sonrası cache invalidation test
- [ ] TTL expiration test (cache otomatik expire)
- [ ] Cache key collision test
- [ ] Cache consistency test (Redis down → fallback → recovery)

## Gün 3: UI Stabilizasyon (5-6 saat)

### 3.1 Table View Cleanup (2 saat)
- [ ] Column width optimization (domain, provider, score)
- [ ] Row hover effect (highlight on hover)
- [ ] Empty state message (lead yoksa mesaj göster)
- [ ] Loading state (spinner veya skeleton)
- [ ] Table pagination UI iyileştirme

### 3.2 Score Breakdown Modal İyileştirme (1 saat)
- [ ] Modal close button (X) daha belirgin
- [ ] Modal backdrop click to close
- [ ] Keyboard navigation (ESC to close)
- [ ] Modal scroll optimization
- [ ] Score breakdown tooltip'leri

### 3.3 Header/Footer Sadeleştirme (1 saat)
- [ ] Header title daha kompakt
- [ ] Header logo/icon ekle (opsiyonel)
- [ ] Footer ekleme (opsiyonel)

### 3.4 Export/PDF Basic (1 saat)
- [ ] CSV export UI iyileştirme (export button daha belirgin)
- [ ] Export format seçimi (CSV/Excel)
- [ ] Export progress indicator
- [ ] PDF export basic (lead detail'da)

### 3.5 Tooltip + Hover Behavior (30 dakika)
- [ ] Generic tooltip component (CSS + JS)
- [ ] Tooltip positioning (top, bottom, left, right)
- [ ] Tooltip delay (hover 500ms sonra göster)
- [ ] Hover behavior iyileştirme (table row, button, badge)

### 3.6 Favori/Tag UI Mini Düzenleme (30 dakika)
- [ ] Favorite button (star icon) daha belirgin
- [ ] Favorite filter daha kolay erişilebilir
- [ ] Tag badge'leri daha kompakt
- [ ] Tag color coding (auto-tag'ler için renk)

## Success Criteria

- [ ] Tüm testler geçiyor mu? (`pytest tests/ -v`)
- [ ] Alembic rollback çalışıyor mu?
- [ ] Multi-worker rate limiting test başarılı mı?
- [ ] UI 2 dakikada kullanılabilir mi? (dogfooding test)
- [ ] Metrics endpoint çalışıyor mu? (`/healthz/metrics`)
- [ ] Sentry error tracking aktif mi?

## Notes

**Referans Dokümanlar**:
- `docs/active/STABILIZATION-SPRINT-PLAN-v1.0.md` - Detaylı plan
- `docs/active/UI-STABILIZATION-CHECKLIST-v1.0.md` - UI checklist

**Hedef**: Hunter v1.1 → **v1.1-stable** (Enterprise-Ready / UI-Stable / Integration-Ready)
