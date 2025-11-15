# P1 Implementation Playbook

**Tarih**: 2025-01-28  
**Durum**: ✅ **P1 Tamamlandı (2025-01-28)** - Reference Guide (Test Komutları, Rollback Reçeteleri, Risky Scenarios)  
**Referans**: `docs/active/KALAN-ISLER-PRIORITY.md` - P1 maddeleri tamamlandı, P2 backlog

---

## 📋 İçindekiler

1. [Branch Stratejisi](#branch-stratejisi)
2. [Commit Pattern](#commit-pattern)
3. [Test Komutları](#test-komutları)
4. [Risky Scenario Simulasyonları](#risky-scenario-simulasyonları)
5. [Rollback Reçeteleri](#rollback-reçeteleri)
6. [Release Pipeline](#release-pipeline)

---

## 🌿 Branch Stratejisi

### Branch Naming Convention

**Format**: `p1/{madde-kısa-adı}`

**P1 Branch'leri (Sıralama Önemli):**

```bash
# 1. Alembic Migration (EN ÖNCE)
git checkout -b p1/alembic-migration

# 2. Distributed Rate Limiting
git checkout -b p1/distributed-rate-limiting

# 3. Caching Layer
git checkout -b p1/caching-layer

# 4. Bulk Operations
git checkout -b p1/bulk-operations

# 5. API Versioning (EN SON)
git checkout -b p1/api-versioning
```

### Branch Workflow

```bash
# 1. Main'den yeni branch oluştur
git checkout main
git pull origin main
git checkout -b p1/alembic-migration

# 2. Implementasyon yap
# ... kod değişiklikleri ...

# 3. Test et
bash scripts/run-tests-docker.sh

# 4. Commit et (commit pattern'e uygun)
git add .
git commit -m "feat: add Alembic migration system"

# 5. Push et
git push origin p1/alembic-migration

# 6. PR oluştur (GitHub)
# PR title: "P1: Alembic Migration System"
# PR description: Risk matrix'ten mitigation stratejilerini ekle
```

### Branch Merge Sırası

**⚠️ KRİTİK**: Branch'ler bağımlılık sırasına göre merge edilmeli:

1. `p1/alembic-migration` → `main` (ilk merge)
2. `p1/distributed-rate-limiting` → `main` (Alembic sonrası)
3. `p1/caching-layer` → `main` (DRL sonrası)
4. `p1/bulk-operations` → `main` (Caching sonrası)
5. `p1/api-versioning` → `main` (en son)

**Merge Checklist:**
- [ ] Tüm testler geçiyor mu? (`bash scripts/run-tests-docker.sh`)
- [ ] Lint hataları yok mu? (`docker-compose exec api flake8 app/`)
- [ ] Type check geçiyor mu? (`docker-compose exec api mypy app/`)
- [ ] Risk matrix'teki test senaryoları çalıştırıldı mı?
- [ ] Rollback reçetesi test edildi mi?
- [ ] Documentation güncellendi mi? (CHANGELOG.md, README.md)

---

## 📝 Commit Pattern

### Commit Message Format

**Conventional Commits** standardı kullanılır:

```
<type>: <subject>

<body>

<footer>
```

### Commit Types

- `feat`: Yeni feature (P1 maddeleri için)
- `fix`: Bug fix
- `refactor`: Code refactoring
- `test`: Test ekleme/güncelleme
- `docs`: Documentation güncelleme
- `chore`: Build/config değişiklikleri

### P1 Commit Örnekleri

#### 1. Alembic Migration

```bash
git commit -m "feat: add Alembic migration system

- Alembic setup and configuration
- Base revision from current production schema
- Migrated 7 manual SQL migrations to Alembic format
- Added schema drift detection (alembic --autogenerate dry-run)
- Migration history tracking and rollback capability

Risk Mitigation:
- Base revision snapshot verified
- Rollback tests passed (alembic downgrade -1)
- Schema drift check implemented

Closes: P1-1 (Alembic Migration)"
```

#### 2. Distributed Rate Limiting

```bash
git commit -m "feat: implement Redis-based distributed rate limiting

- Redis-based rate limiting for DNS/WHOIS/API keys
- Circuit breaker + fallback to in-memory limiter
- Degrade mode logging (WARN level, Sentry tag)
- Multi-worker rate limiting support

Risk Mitigation:
- Circuit breaker tested (Redis down scenario)
- Fallback to in-memory verified
- Multi-worker test passed (2 workers, same API key)

Closes: P1-2 (Distributed Rate Limiting)"
```

#### 3. Caching Layer

```bash
git commit -m "feat: add Redis-based distributed caching layer

- DNS cache (1 hour TTL)
- WHOIS cache (24 hour TTL, migrated from in-memory)
- Provider mapping cache (24 hour TTL)
- Scoring cache (1 hour TTL, signals hash)
- Domain-level full scan cache (1 hour TTL)

Cache Key Design:
- dns:{domain}
- whois:{domain}
- provider:{mx_root}
- scoring:{domain}:{provider}:{signals_hash}
- scan:{domain}

Signals Hash: sha256(json.dumps(signals, sort_keys=True).encode())[:16]
TTL Alignment: Scan cache TTL <= DNS/WHOIS TTL (max 1 hour)

Risk Mitigation:
- TTL alignment verified
- Cache hit rate metrics added
- Versioned cache keys for future invalidation

Closes: P1-3 (Caching Layer)"
```

#### 4. Bulk Operations

```bash
git commit -m "feat: optimize bulk operations with batch processing

- Batch insert optimization (bulk_insert_mappings)
- Database transaction optimization (100 domain/batch)
- Deadlock prevention strategy (transaction timeout, retry)
- Batch failure recovery (partial commit log)
- Bulk log context (bulk_id, batch_no, total_batches)
- Rate-limit aware batch size calculation

Risk Mitigation:
- Deadlock scenario tested (2 workers, same domains)
- Batch failure recovery verified (DB down, Redis down)
- Partial commit log tested (100 domain, 50 success, 50 fail)

Closes: P1-4 (Bulk Operations)"
```

#### 5. API Versioning

```bash
git commit -m "feat: implement API versioning with backward compatibility

- API versioning structure (/api/v1/, /api/v2/)
- All 14 routers moved to /api/v1/
- Dual-path routing (v1 + legacy /api/...)
- Zero downtime deployment strategy
- Version deprecation policy (v1 supported for 6 months)

Risk Mitigation:
- Backward compatibility tests passed
- Zero downtime deployment verified
- Legacy endpoint redirects working

Closes: P1-5 (API Versioning)"
```

### Commit Checklist (Her Commit Öncesi)

- [ ] Code formatted (`black app/`)
- [ ] Lint errors fixed (`flake8 app/`)
- [ ] Type hints present
- [ ] Tests passing (`bash scripts/run-tests-docker.sh`)
- [ ] Commit message follows pattern
- [ ] Related documentation updated (if needed)

---

## 🧪 Test Komutları

### Genel Test Komutları

#### Docker'da Test Çalıştırma (Önerilen)

```bash
# Tüm testler
bash scripts/run-tests-docker.sh

# Veya direkt:
docker-compose exec api pytest tests/ -v --tb=short

# Coverage ile:
docker-compose exec api pytest tests/ -v --cov=app --cov-report=term

# Belirli test dosyası:
docker-compose exec api pytest tests/test_alembic.py -v

# Belirli test fonksiyonu:
docker-compose exec api pytest tests/test_alembic.py::test_migration_rollback -v
```

#### Local Test (Venv Gerekli)

```bash
# Venv aktive et
source .venv/bin/activate  # Linux/Mac
# veya
.venv\Scripts\activate     # Windows

# Test çalıştır
pytest tests/ -v --cov=app --cov-report=term
```

### P1-Specific Test Komutları

#### 1. Alembic Migration Tests

```bash
# Alembic migration test
docker-compose exec api alembic upgrade head
docker-compose exec api alembic downgrade -1
docker-compose exec api alembic upgrade head

# Schema drift check
docker-compose exec api alembic --autogenerate --dry-run

# Migration history check
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "SELECT * FROM alembic_version;"
```

#### 2. Distributed Rate Limiting Tests

```bash
# Multi-worker rate limiting test
# Terminal 1: Worker 1
docker-compose exec worker celery -A app.core.celery_app worker --loglevel=info --concurrency=1

# Terminal 2: Worker 2
docker-compose exec -d worker celery -A app.core.celery_app worker --loglevel=info --concurrency=1

# Terminal 3: Test script
docker-compose exec api python -c "
from app.core.rate_limiter import get_dns_rate_limiter
limiter = get_dns_rate_limiter()
for i in range(20):
    print(f'Request {i}: {limiter.acquire()}')
"

# Redis down test (circuit breaker)
docker-compose stop redis
# Test fallback to in-memory
docker-compose exec api pytest tests/test_rate_limiter.py::test_redis_down_fallback -v
docker-compose start redis
```

#### 3. Caching Layer Tests

```bash
# Cache hit rate test
docker-compose exec api python -c "
from app.core.cache import get_cached_dns_result, cache_dns_result
# First call (cache miss)
result1 = get_cached_dns_result('example.com')
print(f'First call: {result1}')
# Cache it
cache_dns_result('example.com', {'mx_root': 'outlook.com'}, ttl=3600)
# Second call (cache hit)
result2 = get_cached_dns_result('example.com')
print(f'Second call: {result2}')
"

# Redis cache inspection
docker-compose exec redis redis-cli
> KEYS dns:*
> TTL dns:example.com
> GET dns:example.com

# Provider mapping cache test
docker-compose exec api pytest tests/test_cache.py::test_provider_cache_hit -v

# Scoring cache test (signals hash stability)
docker-compose exec api pytest tests/test_cache.py::test_scoring_cache_hash_stability -v
```

#### 4. Bulk Operations Tests

```bash
# Deadlock test (2 workers, same domains)
# Terminal 1: Worker 1
docker-compose exec worker celery -A app.core.celery_app worker --loglevel=info

# Terminal 2: Bulk scan job (100 domains)
curl -X POST http://localhost:8000/scan/bulk \
  -H "Content-Type: application/json" \
  -d '{"domain_list": ["example.com", "google.com", ...]}'

# Terminal 3: Monitor logs
docker-compose logs -f worker | grep -i deadlock

# Batch failure recovery test
# Simulate DB down
docker-compose stop postgres
# Start bulk scan
curl -X POST http://localhost:8000/scan/bulk ...
# Check partial commit log
docker-compose exec api python -c "
from app.core.tasks import get_bulk_log_context
print(get_bulk_log_context('job_id'))
"
docker-compose start postgres
```

#### 5. API Versioning Tests

```bash
# Backward compatibility test
# Old endpoint (should still work)
curl "http://localhost:8000/leads?segment=Migration"

# New endpoint (v1)
curl "http://localhost:8000/api/v1/leads?segment=Migration"

# Both should return same result
curl "http://localhost:8000/leads?segment=Migration" > old.json
curl "http://localhost:8000/api/v1/leads?segment=Migration" > new.json
diff old.json new.json

# Zero downtime deployment test
# Deploy new version while old version running
# Check both endpoints work
```

### Test Coverage Targets

- **P1 Maddeleri**: ≥80% coverage (HIGH risk için)
- **Genel**: ≥70% coverage (mevcut hedef)
- **Critical paths**: 100% coverage (migration, rollback, circuit breaker)

---

## ⚠️ Risky Scenario Simulasyonları

### 1. Alembic Migration - Risky Scenarios

#### Scenario 1.1: Migration Drift (Schema Mismatch)

**Simülasyon:**
```bash
# 1. Production DB'de manuel değişiklik yap (simüle et)
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
ALTER TABLE companies ADD COLUMN test_column VARCHAR(50);
"

# 2. Alembic autogenerate çalıştır
docker-compose exec api alembic --autogenerate -m "test_migration"

# 3. Diff kontrolü yap (schema drift tespit edilmeli)
docker-compose exec api alembic --autogenerate --dry-run

# 4. Manuel diff ile doğrula
docker-compose exec api alembic revision --autogenerate -m "manual_diff_check"
```

**Beklenen Sonuç:**
- Alembic drift tespit etmeli
- Manuel diff ile doğrulanmalı
- Migration oluşturulmadan önce onay alınmalı

#### Scenario 1.2: Downgrade Fail

**Simülasyon:**
```bash
# 1. Migration'ı uygula
docker-compose exec api alembic upgrade head

# 2. Downgrade dene
docker-compose exec api alembic downgrade -1

# 3. Downgrade başarısız olursa (data loss riski)
# Rollback reçetesi uygula (aşağıda)
```

**Beklenen Sonuç:**
- Downgrade başarılı olmalı
- Data loss olmamalı
- Rollback reçetesi hazır olmalı

#### Scenario 1.3: Production Schema Mismatch

**Simülasyon:**
```bash
# 1. Production-like DB'de test et
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
-- Production schema'yı simüle et
CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY);
"

# 2. Alembic base revision oluştur
docker-compose exec api alembic revision --autogenerate -m "base_revision"

# 3. Base revision'ı doğrula
docker-compose exec api alembic history
```

**Beklenen Sonuç:**
- Base revision production schema'yı yansıtmalı
- Manuel diff ile doğrulanmalı

---

### 2. Distributed Rate Limiting - Risky Scenarios

#### Scenario 2.1: Redis Unavailable

**Simülasyon:**
```bash
# 1. Redis'i durdur
docker-compose stop redis

# 2. Rate limiting isteği yap
curl -X POST http://localhost:8000/scan/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'

# 3. Circuit breaker devreye girmeli
docker-compose logs api | grep -i "circuit.*breaker"

# 4. Fallback to in-memory çalışmalı
docker-compose logs api | grep -i "fallback.*in-memory"

# 5. Degrade mode log kontrolü
docker-compose logs api | grep -i "WARN.*degrade"
```

**Beklenen Sonuç:**
- Circuit breaker devreye girmeli
- Fallback to in-memory çalışmalı
- WARN level log + Sentry tag

#### Scenario 2.2: Limiter Mismatch (Multi-Worker)

**Simülasyon:**
```bash
# 1. 2 worker başlat
docker-compose up -d worker
docker-compose scale worker=2

# 2. Aynı API key ile 100 request yap (rate limit: 60 req/min)
for i in {1..100}; do
  curl -X POST http://localhost:8000/ingest/webhook \
    -H "X-API-Key: test-key" \
    -H "Content-Type: application/json" \
    -d '{"domain": "example.com"}'
done

# 3. Rate limit kontrolü (her iki worker'da aynı limit)
docker-compose logs worker | grep -i "rate.*limit"
```

**Beklenen Sonuç:**
- Her iki worker aynı rate limit'i kullanmalı
- Toplam limit: 60 req/min (distributed)
- Redis'te shared counter olmalı

---

### 3. Caching Layer - Risky Scenarios

#### Scenario 3.1: Stale Cache (TTL Mismatch)

**Simülasyon:**
```bash
# 1. DNS cache'e kaydet (1 saat TTL)
docker-compose exec api python -c "
from app.core.cache import cache_dns_result
cache_dns_result('example.com', {'mx_root': 'old.outlook.com'}, ttl=3600)
"

# 2. Domain'i tekrar scan et (cache hit olmalı)
curl -X POST http://localhost:8000/scan/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'

# 3. Cache'teki değer kontrol et
docker-compose exec redis redis-cli GET "dns:example.com"

# 4. TTL kontrolü (1 saat = 3600 saniye)
docker-compose exec redis redis-cli TTL "dns:example.com"
```

**Beklenen Sonuç:**
- Cache hit olmalı
- TTL doğru olmalı (3600 saniye)
- Stale cache riski minimize edilmeli

#### Scenario 3.2: Signals Hash Instability

**Simülasyon:**
```bash
# 1. Aynı signals ile 2 kez hash oluştur
docker-compose exec api python -c "
import hashlib
import json

signals1 = {'spf': True, 'dkim': True, 'dmarc_policy': 'reject'}
signals2 = {'dkim': True, 'spf': True, 'dmarc_policy': 'reject'}  # Farklı sıra

hash1 = hashlib.sha256(json.dumps(signals1, sort_keys=True).encode()).hexdigest()[:16]
hash2 = hashlib.sha256(json.dumps(signals2, sort_keys=True).encode()).hexdigest()[:16]

print(f'Hash1: {hash1}')
print(f'Hash2: {hash2}')
print(f'Match: {hash1 == hash2}')  # True olmalı
"
```

**Beklenen Sonuç:**
- `sort_keys=True` ile hash stabil olmalı
- Aynı signals → aynı hash

#### Scenario 3.3: Cache Consistency Loss

**Simülasyon:**
```bash
# 1. Scan cache'e kaydet (1 saat TTL)
docker-compose exec api python -c "
from app.core.cache import cache_scan_result
cache_scan_result('example.com', {'score': 75}, ttl=3600)
"

# 2. DNS cache'i expire et (simüle et - TTL'i 0 yap)
docker-compose exec redis redis-cli EXPIRE "dns:example.com" 0

# 3. Scan cache hala var mı kontrol et
docker-compose exec redis redis-cli GET "scan:example.com"

# 4. TTL uyumu kontrolü (scan TTL <= DNS TTL)
docker-compose exec redis redis-cli TTL "scan:example.com"
docker-compose exec redis redis-cli TTL "dns:example.com"
```

**Beklenen Sonuç:**
- Scan cache TTL <= DNS TTL (konsistensi)
- Cache invalidation stratejisi çalışmalı

---

### 4. Bulk Operations - Risky Scenarios

#### Scenario 4.1: Deadlock (2 Workers, Same Domains)

**Simülasyon:**
```bash
# 1. 2 worker başlat
docker-compose up -d worker
docker-compose scale worker=2

# 2. Aynı domain'leri 2 farklı bulk scan job'ına ekle
curl -X POST http://localhost:8000/scan/bulk \
  -H "Content-Type: application/json" \
  -d '{"domain_list": ["example.com", "google.com"]}'

# Job ID 1 al
JOB_ID_1=$(curl -s -X POST http://localhost:8000/scan/bulk ... | jq -r '.job_id')

# Aynı domain'lerle 2. job oluştur
curl -X POST http://localhost:8000/scan/bulk \
  -H "Content-Type: application/json" \
  -d '{"domain_list": ["example.com", "google.com"]}'

# Job ID 2 al
JOB_ID_2=$(curl -s -X POST http://localhost:8000/scan/bulk ... | jq -r '.job_id')

# 3. Deadlock log'larını izle
docker-compose logs -f worker | grep -i "deadlock\|timeout\|lock"
```

**Beklenen Sonuç:**
- Deadlock olmamalı (transaction timeout + retry)
- Batch isolation çalışmalı
- Partial commit log oluşmalı

#### Scenario 4.2: Batch Corruption

**Simülasyon:**
```bash
# 1. 100 domain'lik bulk scan başlat
curl -X POST http://localhost:8000/scan/bulk \
  -H "Content-Type: application/json" \
  -d '{"domain_list": ["domain1.com", "domain2.com", ...]}'

# 2. Batch ortasında DB'yi durdur (simüle et)
docker-compose stop postgres

# 3. Batch failure recovery kontrolü
docker-compose logs worker | grep -i "batch.*failure\|partial.*commit"

# 4. Partial commit log kontrolü
docker-compose exec api python -c "
from app.core.tasks import get_partial_commit_log
log = get_partial_commit_log('job_id')
print(f'Committed: {log[\"committed\"]}')
print(f'Failed: {log[\"failed\"]}')
"

# 5. DB'yi başlat
docker-compose start postgres

# 6. Retry mekanizması çalışmalı
docker-compose logs worker | grep -i "retry\|recovery"
```

**Beklenen Sonuç:**
- Partial commit log oluşmalı
- Batch failure recovery çalışmalı
- Retry mekanizması devreye girmeli

#### Scenario 4.3: Transaction Timeout

**Simülasyon:**
```bash
# 1. Uzun süren batch işlemi (simüle et - DB lock)
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "
BEGIN;
LOCK TABLE domain_signals IN EXCLUSIVE MODE;
-- Bu lock'u 30 saniye tut (timeout test için)
SELECT pg_sleep(30);
COMMIT;
"

# 2. Aynı anda bulk scan başlat
curl -X POST http://localhost:8000/scan/bulk ...

# 3. Transaction timeout kontrolü
docker-compose logs worker | grep -i "timeout\|transaction"
```

**Beklenen Sonuç:**
- Transaction timeout çalışmalı
- Retry logic devreye girmeli
- Deadlock prevention çalışmalı

---

### 5. API Versioning - Risky Scenarios

#### Scenario 5.1: 404/Route Mismatch

**Simülasyon:**
```bash
# 1. Eski endpoint'i test et (hala çalışmalı)
curl "http://localhost:8000/leads?segment=Migration"

# 2. Yeni endpoint'i test et
curl "http://localhost:8000/api/v1/leads?segment=Migration"

# 3. Her iki endpoint de 200 OK dönmeli
# 4. Response'lar aynı olmalı
```

**Beklenen Sonuç:**
- Her iki endpoint çalışmalı
- Response'lar aynı olmalı
- 404 hatası olmamalı

#### Scenario 5.2: Backward Compatibility Break

**Simülasyon:**
```bash
# 1. Eski client (legacy endpoint kullanıyor)
curl "http://localhost:8000/leads?segment=Migration" > old_response.json

# 2. Yeni client (v1 endpoint kullanıyor)
curl "http://localhost:8000/api/v1/leads?segment=Migration" > new_response.json

# 3. Response format kontrolü
diff old_response.json new_response.json

# 4. Response schema kontrolü (Pydantic models)
docker-compose exec api python -c "
from app.api.leads import LeadsListResponse
# Her iki response da LeadsListResponse model'ine uymalı
"
```

**Beklenen Sonuç:**
- Response format aynı olmalı
- Pydantic validation geçmeli
- Backward compatibility korunmalı

#### Scenario 5.3: Zero Downtime Deployment Failure

**Simülasyon:**
```bash
# 1. Deployment sırasında test (rolling update simülasyonu)
# Old version çalışıyor
curl "http://localhost:8000/leads?segment=Migration"

# 2. New version deploy et (Docker restart)
docker-compose restart api

# 3. Deployment sırasında her iki endpoint çalışmalı
curl "http://localhost:8000/leads?segment=Migration"  # Old
curl "http://localhost:8000/api/v1/leads?segment=Migration"  # New

# 4. Zero downtime kontrolü
# Her iki endpoint de çalışmalı, hiç downtime olmamalı
```

**Beklenen Sonuç:**
- Zero downtime deployment
- Her iki endpoint çalışmalı
- Hiç 503/502 hatası olmamalı

---

## 🔄 Rollback Reçeteleri

### Genel Rollback Stratejisi

**Rollback Öncesi Checklist:**
- [ ] Rollback planı hazır mı?
- [ ] Rollback test edildi mi? (staging'de)
- [ ] Data backup alındı mı? (production için)
- [ ] Rollback süresi tahmin edildi mi?
- [ ] Rollback sonrası test planı hazır mı?

---

### 1. Alembic Migration - Rollback

#### Rollback Senaryosu: Migration Başarısız

**Reçete:**

```bash
# 1. Migration durumunu kontrol et
docker-compose exec api alembic current

# 2. Son migration'ı geri al
docker-compose exec api alembic downgrade -1

# 3. Base'e kadar geri al (gerekirse)
docker-compose exec api alembic downgrade base

# 4. Schema durumunu kontrol et
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "\d companies"

# 5. Data integrity kontrolü
docker-compose exec api pytest tests/test_migration_rollback.py -v

# 6. API health check
curl http://localhost:8000/healthz
```

**Rollback Sonrası:**
- [ ] Schema eski haline döndü mü?
- [ ] Data loss var mı? (SELECT COUNT(*) kontrolü)
- [ ] API çalışıyor mu? (`/healthz` check)
- [ ] Testler geçiyor mu?

**Rollback Süresi:** ~5-10 dakika (migration boyutuna göre)

---

### 2. Distributed Rate Limiting - Rollback

#### Rollback Senaryosu: Redis Down + Circuit Breaker Fail

**Reçete:**

```bash
# 1. Redis'i durdur (simüle et)
docker-compose stop redis

# 2. Fallback to in-memory kontrolü
docker-compose logs api | grep -i "fallback.*in-memory"

# 3. Eğer fallback çalışmıyorsa, code rollback
git checkout main  # veya önceki commit
git revert <commit-hash>

# 4. API'yi restart et
docker-compose restart api

# 5. Rate limiting test et
curl -X POST http://localhost:8000/scan/domain ...

# 6. In-memory rate limiting çalışıyor mu kontrol et
docker-compose logs api | grep -i "rate.*limit"
```

**Rollback Sonrası:**
- [ ] In-memory rate limiting çalışıyor mu?
- [ ] API çalışıyor mu?
- [ ] Rate limit doğru çalışıyor mu?

**Rollback Süresi:** ~2-5 dakika (code revert)

---

### 3. Caching Layer - Rollback

#### Rollback Senaryosu: Stale Cache + Consistency Loss

**Reçete:**

```bash
# 1. Cache'i temizle (tüm cache keys)
docker-compose exec redis redis-cli FLUSHDB

# 2. Cache'i devre dışı bırak (code rollback)
# app/core/cache.py'de cache check'i skip et
git checkout main  # veya önceki commit

# 3. API'yi restart et
docker-compose restart api

# 4. Cache olmadan test et
curl -X POST http://localhost:8000/scan/domain ...

# 5. Performance kontrolü (cache olmadan yavaş olmalı)
time curl -X POST http://localhost:8000/scan/domain ...
```

**Rollback Sonrası:**
- [ ] Cache temizlendi mi?
- [ ] API cache olmadan çalışıyor mu?
- [ ] Performance acceptable mı? (cache olmadan)

**Rollback Süresi:** ~2-5 dakika (cache flush + code revert)

---

### 4. Bulk Operations - Rollback

#### Rollback Senaryosu: Deadlock + Batch Corruption

**Reçete:**

```bash
# 1. Aktif bulk job'ları durdur
docker-compose stop worker

# 2. Partial commit log kontrolü
docker-compose exec api python -c "
from app.core.tasks import get_partial_commit_log
log = get_partial_commit_log('job_id')
print(f'Committed domains: {log[\"committed\"]}')
print(f'Failed domains: {log[\"failed\"]}')
"

# 3. Failed domain'leri manuel olarak işle (gerekirse)
# Committed domain'ler zaten DB'de

# 4. Code rollback (deadlock prevention kaldır)
git checkout main  # veya önceki commit

# 5. Worker'ı restart et
docker-compose restart worker

# 6. Failed domain'leri tekrar scan et (sequential, safe mode)
for domain in failed_domains; do
  curl -X POST http://localhost:8000/scan/domain ...
done
```

**Rollback Sonrası:**
- [ ] Partial commit log kontrol edildi mi?
- [ ] Failed domain'ler manuel işlendi mi?
- [ ] Data consistency korundu mu?

**Rollback Süresi:** ~10-30 dakika (batch size'a göre)

---

### 5. API Versioning - Rollback

#### Rollback Senaryosu: 404/Route Mismatch + BC Break

**Reçete:**

```bash
# 1. Legacy endpoint'leri kontrol et
curl "http://localhost:8000/leads?segment=Migration"

# 2. Eğer legacy endpoint çalışmıyorsa, code rollback
git checkout main  # veya önceki commit

# 3. API'yi restart et
docker-compose restart api

# 4. Her iki endpoint'i test et
curl "http://localhost:8000/leads?segment=Migration"  # Legacy
curl "http://localhost:8000/api/v1/leads?segment=Migration"  # v1 (eğer hala varsa)

# 5. Client compatibility test
# Eski client'lar çalışıyor mu?
```

**Rollback Sonrası:**
- [ ] Legacy endpoint çalışıyor mu?
- [ ] Client compatibility korundu mu?
- [ ] Zero downtime sağlandı mı?

**Rollback Süresi:** ~2-5 dakika (code revert)

---

## 🚀 Release Pipeline

### P1 Release Stratejisi

**Release Sırası (Bağımlılık Sırasına Göre):**

1. **Alembic Migration** → `main` (ilk release)
2. **Distributed Rate Limiting** → `main` (Alembic sonrası)
3. **Caching Layer** → `main` (DRL sonrası)
4. **Bulk Operations** → `main` (Caching sonrası)
5. **API Versioning** → `main` (en son)

### Release Pipeline Adımları

#### Pre-Release Checklist

**Her P1 Maddesi İçin:**

- [ ] Tüm testler geçiyor mu? (`bash scripts/run-tests-docker.sh`)
- [ ] Lint hataları yok mu? (`docker-compose exec api flake8 app/`)
- [ ] Type check geçiyor mu? (`docker-compose exec api mypy app/`)
- [ ] Risk matrix'teki test senaryoları çalıştırıldı mı?
- [ ] Rollback reçetesi test edildi mi? (staging'de)
- [ ] Documentation güncellendi mi? (CHANGELOG.md, README.md)
- [ ] Commit message pattern'e uygun mu?
- [ ] PR review tamamlandı mı?

#### Release Adımları

**1. Branch Merge**

```bash
# 1. Main'i güncelle
git checkout main
git pull origin main

# 2. Feature branch'i merge et
git merge p1/alembic-migration --no-ff

# 3. Conflict kontrolü
git status

# 4. Merge commit message
git commit -m "Merge p1/alembic-migration into main

P1-1: Alembic Migration System
- Migration history tracking
- Rollback capability
- Schema drift detection

Risk: HIGH
Mitigation: Base revision snapshot, dry-run, rollback test"
```

**2. Test Suite (Post-Merge)**

```bash
# 1. Tüm testler
bash scripts/run-tests-docker.sh

# 2. Integration testler
docker-compose exec api pytest tests/test_integration_p1.py -v

# 3. Risk matrix test senaryoları
bash scripts/test_p1_risky_scenarios.sh
```

**3. Documentation Update**

```bash
# 1. CHANGELOG.md güncelle
# [Unreleased] bölümüne ekle:
# - P1-1: Alembic Migration System

# 2. README.md güncelle (gerekirse)
# - Alembic migration komutları ekle

# 3. Commit et
git add CHANGELOG.md README.md
git commit -m "docs: update documentation for P1-1 Alembic Migration"
```

**4. Tag & Release**

```bash
# 1. Version tag oluştur (P1 maddeleri için minor version bump)
# v1.0.0 → v1.1.0 (P1 tamamlandığında)

# 2. Tag oluştur
git tag -a v1.1.0 -m "Release v1.1.0: P1 Performance Improvements

P1-1: Alembic Migration System
P1-2: Distributed Rate Limiting
P1-3: Caching Layer
P1-4: Bulk Operations Optimization
P1-5: API Versioning"

# 3. Tag'ı push et
git push origin v1.1.0
```

**5. Production Deployment**

```bash
# 1. Production environment'a deploy
# (Docker Compose, Kubernetes, vb.)

# 2. Health check
curl https://api.example.com/healthz

# 3. Migration çalıştır (Alembic için)
docker-compose exec api alembic upgrade head

# 4. Smoke test
bash scripts/smoke_test_p1.sh

# 5. Monitor logs
docker-compose logs -f api | grep -i "error\|warn"
```

### Release Pipeline Checklist

**Her Release Öncesi:**

- [ ] Pre-release checklist tamamlandı mı?
- [ ] Test suite geçti mi?
- [ ] Documentation güncellendi mi?
- [ ] Risk matrix test senaryoları çalıştırıldı mı?
- [ ] Rollback reçetesi test edildi mi?
- [ ] Tag oluşturuldu mu?
- [ ] Production deployment planı hazır mı?

**Her Release Sonrası:**

- [ ] Production health check geçti mi?
- [ ] Smoke test geçti mi?
- [ ] Log monitoring aktif mi?
- [ ] Rollback planı hazır mı? (ilk 24 saat için)

---

## 📊 P1 Release Timeline

### Hafta 1: Alembic + DRL

**Gün 1-3: Alembic Migration**
- Branch: `p1/alembic-migration`
- Test: Migration up/down, schema drift
- Release: `v1.1.0-alembic` (pre-release tag)

**Gün 4: Distributed Rate Limiting**
- Branch: `p1/distributed-rate-limiting`
- Test: Multi-worker, Redis down, circuit breaker
- Release: `v1.1.0-drl` (pre-release tag)

### Hafta 2: Caching + Bulk

**Gün 1-2: Caching Layer**
- Branch: `p1/caching-layer`
- Test: Cache hit rate, TTL alignment, signals hash
- Release: `v1.1.0-caching` (pre-release tag)

**Gün 3: Bulk Operations**
- Branch: `p1/bulk-operations`
- Test: Deadlock, batch failure, partial commit
- Release: `v1.1.0-bulk` (pre-release tag)

### Hafta 3: Versioning + Integration

**Gün 1: API Versioning**
- Branch: `p1/api-versioning`
- Test: Backward compatibility, zero downtime
- Release: `v1.1.0-versioning` (pre-release tag)

**Gün 2-3: Integration & Final Release**
- Integration testleri
- End-to-end testler
- Final release: `v1.1.0` (production tag)

---

## 🔧 Utility Scripts

### P1 Test Script

**`scripts/test_p1_risky_scenarios.sh`** (oluşturulacak):

```bash
#!/bin/bash
# P1 Risky Scenario Test Suite

set -e

echo "🧪 Running P1 Risky Scenario Tests..."

# 1. Alembic Migration Tests
echo "📦 Testing Alembic Migration..."
docker-compose exec api alembic upgrade head
docker-compose exec api alembic downgrade -1
docker-compose exec api alembic upgrade head
docker-compose exec api alembic --autogenerate --dry-run

# 2. Distributed Rate Limiting Tests
echo "🚦 Testing Distributed Rate Limiting..."
docker-compose stop redis
docker-compose exec api pytest tests/test_rate_limiter.py::test_redis_down_fallback -v
docker-compose start redis

# 3. Caching Layer Tests
echo "💾 Testing Caching Layer..."
docker-compose exec api pytest tests/test_cache.py -v

# 4. Bulk Operations Tests
echo "📦 Testing Bulk Operations..."
docker-compose exec api pytest tests/test_bulk_operations.py -v

# 5. API Versioning Tests
echo "🔀 Testing API Versioning..."
docker-compose exec api pytest tests/test_api_versioning.py -v

echo "✅ All P1 risky scenario tests passed!"
```

### P1 Smoke Test Script

**`scripts/smoke_test_p1.sh`** (oluşturulacak):

```bash
#!/bin/bash
# P1 Smoke Test Suite

set -e

echo "💨 Running P1 Smoke Tests..."

# 1. Health Check
echo "🏥 Health Check..."
curl -f http://localhost:8000/healthz || exit 1

# 2. Redis Health (DRL için)
echo "🔴 Redis Health..."
curl -f http://localhost:8000/healthz/ready || exit 1

# 3. API Endpoints (Versioning için)
echo "🔀 API Endpoints..."
curl -f "http://localhost:8000/leads?segment=Migration" || exit 1
curl -f "http://localhost:8000/api/v1/leads?segment=Migration" || exit 1

# 4. Cache Hit Rate (Caching için)
echo "💾 Cache Hit Rate..."
# Cache hit rate metric kontrolü

# 5. Bulk Scan (Bulk Operations için)
echo "📦 Bulk Scan..."
JOB_ID=$(curl -s -X POST http://localhost:8000/scan/bulk \
  -H "Content-Type: application/json" \
  -d '{"domain_list": ["example.com"]}' | jq -r '.job_id')
curl -f "http://localhost:8000/scan/bulk/$JOB_ID" || exit 1

echo "✅ All P1 smoke tests passed!"
```

---

## 📚 Referanslar

- **P1 Priority Document**: `docs/active/KALAN-ISLER-PRIORITY.md`
- **Commit Checklist**: `COMMIT_CHECKLIST.md`
- **Commands Reference**: `.cursor/commands/commands.md`
- **Development Environment**: `docs/active/DEVELOPMENT-ENVIRONMENT.md`
- **Cursor Rules**: `.cursor/rules/.cursorrules`

---

**Son Güncelleme**: 2025-01-28  
**Durum**: ✅ **P1 Tamamlandı (2025-01-28)** - Reference Guide  
**Not**: P1 maddeleri tamamlandı. Bu playbook artık reference guide olarak kullanılabilir (test komutları, rollback reçeteleri, risky scenario simulasyonları gelecekteki benzer işler için referans olarak değerli).

