# Logging Golden Samples - Structured Logging Examples

Bu dokümantasyon, core modüllerde kullanılan structured logging formatının golden sample'larını içerir.

## Format Standardı

Tüm log satırları şu pattern'i takip eder:

```python
logger.<level>(
    "event_name",  # İlk parametre: event name (string)
    key1=value1,   # Sonrası: snake_case key=value çiftleri
    key2=value2,
    ...
)
```

## Ortak Key'ler

- `operation`: İşlem tipi (get/set/delete/acquire/wait)
- `reason`: Hata/olay nedeni (redis_unavailable, connection_failed, etc.)
- `redis_key`: Redis key prefix (PII içermez: "dns", "whois", "api_key_123")
- `domain`: Domain bilgisi (mask'lenmiş veya hash'lenmiş)
- `error`: Hata mesajı (string)
- `rate`: Rate limit değeri (float)
- `retry_count`: Retry sayısı (int)

## Golden Samples

### 1. Successful Cache Hit

**Event**: `cache_hit` (opsiyonel, şu an loglanmıyor ama eklenebilir)

```json
{
  "event": "cache_hit",
  "operation": "get",
  "key_prefix": "dns",
  "timestamp": "2025-01-28T10:30:45.123Z",
  "logger": "app.core.cache",
  "level": "debug"
}
```

**Not**: Şu an cache hit'ler loglanmıyor (sadece metrics'te takip ediliyor). Gerekirse eklenebilir.

### 2. Cache Miss + Backend Fetch

**Event**: Normal akış, loglanmıyor (sadece metrics'te takip ediliyor)

Cache miss normal bir durum, log gürültüsü yaratmamak için loglanmıyor.

### 3. Cache Operation Failure (Debug Level)

**Event**: `cache_get_failed`, `cache_set_failed`, `cache_delete_failed`

```json
{
  "event": "cache_get_failed",
  "operation": "get",
  "key": "cache:dns:<a1b2c3d4>",
  "error": "Connection timeout",
  "timestamp": "2025-01-28T10:30:45.123Z",
  "logger": "app.core.cache",
  "level": "debug"
}
```

**Özellikler**:
- `key` mask'lenmiş (domain PII içermez)
- `debug` seviyesi (sık olabilir, normal akış)
- `operation` key'i mevcut

### 4. Rate Limit Applied (Normal Flow)

**Event**: Rate limit normal akış, loglanmıyor (sadece metrics'te takip ediliyor)

Rate limit hit normal bir durum, log gürültüsü yaratmamak için loglanmıyor.

### 5. Rate Limiter Fallback (Warning)

**Event**: `rate_limiter_fallback`

```json
{
  "event": "rate_limiter_fallback",
  "redis_key": "dns",
  "rate": 10.0,
  "reason": "redis_unavailable",
  "timestamp": "2025-01-28T10:30:45.123Z",
  "logger": "app.core.distributed_rate_limiter",
  "level": "warning"
}
```

**Özellikler**:
- `warning` seviyesi (gerçek problem)
- `reason` key'i mevcut
- `redis_key` PII içermez

### 6. Redis Rate Limit Operation Failed (Warning)

**Event**: `redis_rate_limit_operation_failed`

```json
{
  "event": "redis_rate_limit_operation_failed",
  "redis_key": "api_key_123",
  "operation": "acquire",
  "error": "Connection refused",
  "reason": "redis_operation_failed",
  "timestamp": "2025-01-28T10:30:45.123Z",
  "logger": "app.core.distributed_rate_limiter",
  "level": "warning",
  "exc_info": true
}
```

**Özellikler**:
- `warning` seviyesi
- `operation` ve `reason` key'leri mevcut
- `exc_info: true` (stack trace dahil)

### 7. Circuit Breaker Opened (Warning)

**Event**: `circuit_breaker_opened`

```json
{
  "event": "circuit_breaker_opened",
  "failure_count": 5,
  "recovery_timeout": 60.0,
  "timestamp": "2025-01-28T10:30:45.123Z",
  "logger": "app.core.distributed_rate_limiter",
  "level": "warning"
}
```

**Özellikler**:
- `warning` seviyesi (sistem hala çalışıyor ama problem var)
- Circuit breaker state bilgisi

### 8. Circuit Breaker Recovery Attempt (Info)

**Event**: `circuit_breaker_attempting_recovery`

```json
{
  "event": "circuit_breaker_attempting_recovery",
  "timestamp": "2025-01-28T10:30:45.123Z",
  "logger": "app.core.distributed_rate_limiter",
  "level": "info"
}
```

**Özellikler**:
- `info` seviyesi (önemli ama problem değil)

### 9. Redis Client Initialized (Info)

**Event**: `redis_client_initialized`

```json
{
  "event": "redis_client_initialized",
  "timestamp": "2025-01-28T10:30:45.123Z",
  "logger": "app.core.redis_client",
  "level": "info"
}
```

**Özellikler**:
- `info` seviyesi (normal akış, önemli event)

### 10. Redis Client Initialization Failed (Error)

**Event**: `redis_client_initialization_failed`

```json
{
  "event": "redis_client_initialization_failed",
  "error": "Connection refused: connect() failed",
  "reason": "connection_failed",
  "timestamp": "2025-01-28T10:30:45.123Z",
  "logger": "app.core.redis_client",
  "level": "error"
}
```

**Özellikler**:
- `error` seviyesi (critical infrastructure failure)
- `reason` key'i mevcut

## Log Seviyesi Rehberi

### Debug
- Normal akış, sık olabilir
- Cache operation failures (get/set/delete)
- Detaylı debugging bilgisi

### Info
- Önemli ama problem olmayan olaylar
- Redis client initialized
- Circuit breaker recovery attempts
- Normal operation milestones

### Warning
- Bir şeyler sıkıntılı ama sistem hala çalışıyor
- Rate limiter fallback (Redis unavailable)
- Redis rate limit operation failed
- Circuit breaker opened

### Error
- Bu feature şu an çalışmıyor
- Redis client initialization failed (critical infrastructure)
- Critical system failures

## PII Masking

Tüm log satırlarında PII mask'lenir:

- **Domain**: `cache:dns:example.com` → `cache:dns:<a1b2c3d4>` (8-char hash)
- **Email**: `mask_pii(email)` → `<a1b2c3d4>` (8-char hash)
- **Company Name**: `mask_pii(company_name)` → `<a1b2c3d4>` (8-char hash)

**Redis Key'ler**: PII içermez (sadece ID'ler: `api_key_123`, `dns`, `whois`)

## Query Örnekleri

### Tüm rate limiter fallback'leri bul
```json
{"event": "rate_limiter_fallback"}
```

### Redis initialization failure'ları bul
```json
{"event": "redis_client_initialization_failed"}
```

### Belirli bir operation için cache failure'ları bul
```json
{"event": "cache_get_failed", "operation": "get"}
```

### Circuit breaker açılmalarını bul
```json
{"event": "circuit_breaker_opened"}
```

## Best Practices

1. **Event Name**: Her zaman ilk parametre, kebab-case (örn: `cache_get_failed`)
2. **Context Keys**: snake_case (örn: `redis_key`, `operation`, `reason`)
3. **PII Masking**: Domain/email/company_name her zaman mask'lenir
4. **Log Levels**: Debug (normal), Info (important), Warning (problem but working), Error (broken)
5. **Consistency**: Aynı event type için aynı key'ler kullanılır

