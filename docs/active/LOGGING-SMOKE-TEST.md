# Logging Smoke Test Guide

Bu dokümantasyon, structured logging'in doğru çalıştığını doğrulamak için smoke test rehberidir.

## Hızlı Test

### 1. Unit Test (Kod Seviyesi)

```bash
python scripts/test_logging_output.py
```

Bu test şunları doğrular:
- ✅ PII masking (email, domain, company name)
- ✅ Log format structure (event name, context keys)
- ✅ Log level appropriateness (debug/info/warning/error)
- ✅ Structured logging context consistency
- ✅ Redis key PII check

### 2. Integration Test (API Seviyesi)

```bash
# Start API
docker-compose up -d api redis postgres

# Run smoke test
bash scripts/smoke_test_logging.sh

# Check logs
docker-compose logs api --tail=100 | grep -E '(cache_|rate_limiter_|redis_client_)'
```

## Test Senaryoları

### Senaryo 1: Health Check (Redis Initialization)

```bash
curl http://localhost:8000/healthz
```

**Beklenen Log:**
```json
{
  "event": "redis_client_initialized",
  "level": "info",
  "logger": "app.core.redis_client",
  "timestamp": "2025-01-28T10:30:45.123Z"
}
```

### Senaryo 2: Metrics Endpoint (Cache Operations)

```bash
curl http://localhost:8000/healthz/metrics
```

**Beklenen Log:**
- Cache operations (if any failures → debug level)
- No PII in cache keys (masked)

### Senaryo 3: Scan Endpoint (DNS/WHOIS Cache + Rate Limiting)

```bash
# First ingest a domain
curl -X POST http://localhost:8000/ingest/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "company_name": "Example Corp"}'

# Then scan
curl -X POST http://localhost:8000/scan/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'
```

**Beklenen Log:**
- DNS cache operations (if failures → debug level)
- WHOIS cache operations (if failures → debug level)
- Rate limiting operations (if fallback → warning level)
- **No domain PII in logs** (cache keys masked)

## Log Verification Checklist

### ✅ PII Verification

- [ ] No email addresses in logs
- [ ] No company names in logs
- [ ] Cache keys are masked (e.g., `cache:dns:<hash>`)
- [ ] Redis keys don't contain PII (e.g., `api_key_123`, `dns`, `whois`)

### ✅ Log Level Verification

- [ ] `cache_*_failed` → `debug` level
- [ ] `rate_limiter_fallback` → `warning` level
- [ ] `redis_client_initialization_failed` → `error` level
- [ ] `redis_client_initialized` → `info` level

### ✅ Structured Logging Format

- [ ] Event name is first parameter (string)
- [ ] Context keys are snake_case (`operation`, `reason`, `redis_key`)
- [ ] JSON format in production (if `ENVIRONMENT=production`)
- [ ] Pretty format in development (if `ENVIRONMENT=development`)

## Log Query Examples

### Tüm cache failure'ları bul

```bash
docker-compose logs api | grep "cache_.*_failed"
```

### Rate limiter fallback'leri bul

```bash
docker-compose logs api | grep "rate_limiter_fallback"
```

### Redis initialization failure'ları bul

```bash
docker-compose logs api | grep "redis_client_initialization_failed"
```

### JSON format ile parse et (jq ile)

```bash
docker-compose logs api | jq 'select(.event == "cache_get_failed")'
```

## Troubleshooting

### Problem: Logs görünmüyor

**Çözüm:**
```bash
# Log level'i kontrol et
docker-compose exec api env | grep LOG_LEVEL

# Debug level'e geç (development için)
export LOG_LEVEL=DEBUG
docker-compose restart api
```

### Problem: JSON format görünmüyor

**Çözüm:**
```bash
# Environment'i kontrol et
docker-compose exec api env | grep ENVIRONMENT

# Production mode'a geç
export ENVIRONMENT=production
docker-compose restart api
```

### Problem: PII görünüyor

**Çözüm:**
1. `_mask_cache_key()` fonksiyonunun çalıştığını kontrol et
2. `mask_pii()` fonksiyonunun import edildiğini kontrol et
3. Cache key'lerin mask'lendiğini doğrula

## Golden Samples

Detaylı log örnekleri için: `docs/active/LOGGING-GOLDEN-SAMPLES.md`

## Test Scripts

- **Unit Test**: `scripts/test_logging_output.py` - Kod seviyesi testler
- **Integration Test**: `scripts/smoke_test_logging.sh` - API seviyesi testler

## CI/CD Integration

Smoke test'i CI/CD pipeline'a eklemek için:

```yaml
# .github/workflows/test.yml
- name: Run Logging Smoke Test
  run: |
    python scripts/test_logging_output.py
```

