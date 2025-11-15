# P1 Distributed Rate Limiting Hazırlığı

**Tarih**: 2025-01-28  
**Durum**: Hazırlık Tamamlandı  
**Amaç**: Redis-based distributed rate limiting için zemin hazırlamak (read-only analiz)

---

## 📋 Mevcut Rate Limiter Analizi

### ✅ Mevcut Rate Limiter Yapısı

#### 1. RateLimiter Class (Token Bucket Algorithm)
- **Lokasyon**: `app/core/rate_limiter.py`
- **Algoritma**: Token bucket (thread-safe)
- **Özellikler**:
  - `rate`: Maximum requests per second
  - `burst`: Maximum burst size (default: rate)
  - `acquire()`: Try to acquire tokens (non-blocking)
  - `wait()`: Wait until tokens available (blocking)

**Kod Örneği:**
```python
class RateLimiter:
    def __init__(self, rate: float, burst: Optional[float] = None):
        self.rate = rate
        self.burst = burst or rate
        self.tokens = self.burst
        self.last_update = time.time()
        self.lock = Lock()
```

---

### ✅ Mevcut Rate Limiter Kullanımları

#### 2. DNS Rate Limiter
- **Fonksiyon**: `get_dns_rate_limiter()` → `RateLimiter(rate=10.0, burst=10.0)`
- **Limit**: 10 requests/second
- **Kullanım**: `wait_for_dns_rate_limit()` - Blocking wait
- **Kullanım Yerleri**:
  - `app/core/tasks.py` - `scan_single_domain()` fonksiyonunda (satır 54)

**Kod Örneği:**
```python
# app/core/rate_limiter.py
_dns_rate_limiter: Optional[RateLimiter] = None

def get_dns_rate_limiter() -> RateLimiter:
    global _dns_rate_limiter
    with _rate_limiter_lock:
        if _dns_rate_limiter is None:
            _dns_rate_limiter = RateLimiter(rate=10.0, burst=10.0)
        return _dns_rate_limiter

def wait_for_dns_rate_limit():
    limiter = get_dns_rate_limiter()
    wait_time = limiter.wait()
    if wait_time > 0:
        time.sleep(wait_time)
```

#### 3. WHOIS Rate Limiter
- **Fonksiyon**: `get_whois_rate_limiter()` → `RateLimiter(rate=5.0, burst=5.0)`
- **Limit**: 5 requests/second
- **Kullanım**: `wait_for_whois_rate_limit()` - Blocking wait
- **Kullanım Yerleri**:
  - `app/core/tasks.py` - `scan_single_domain()` fonksiyonunda (satır 60)

**Kod Örneği:**
```python
# app/core/rate_limiter.py
_whois_rate_limiter: Optional[RateLimiter] = None

def get_whois_rate_limiter() -> RateLimiter:
    global _whois_rate_limiter
    with _rate_limiter_lock:
        if _whois_rate_limiter is None:
            _whois_rate_limiter = RateLimiter(rate=5.0, burst=5.0)
        return _whois_rate_limiter

def wait_for_whois_rate_limit():
    limiter = get_whois_rate_limiter()
    wait_time = limiter.wait()
    if wait_time > 0:
        time.sleep(wait_time)
```

#### 4. API Key Rate Limiter
- **Fonksiyon**: `get_api_key_limiter(api_key_id, rate_limit_per_minute)`
- **Limit**: Per-key, per-minute (configurable, default: 60 req/min)
- **Kullanım**: `app/core/api_key_auth.py` - `verify_api_key()` fonksiyonunda
- **Storage**: In-memory dict (`_api_key_limiters: Dict[str, RateLimiter]`)

**Kod Örneği:**
```python
# app/core/api_key_auth.py
_api_key_limiters: Dict[str, RateLimiter] = {}
_rate_limiter_lock = Lock()

def get_api_key_limiter(api_key_id: int, rate_limit_per_minute: int) -> RateLimiter:
    limiter_key = f"api_key_{api_key_id}"
    with _rate_limiter_lock:
        if limiter_key not in _api_key_limiters:
            rate_per_second = rate_limit_per_minute / 60.0
            _api_key_limiters[limiter_key] = RateLimiter(
                rate=rate_per_second,
                burst=rate_limit_per_minute,
            )
        return _api_key_limiters[limiter_key]
```

---

## ⚠️ Mevcut Sorunlar

### 1. Multi-Worker Rate Limit Tutarsızlığı
- **Sorun**: Her worker kendi in-memory rate limiter'ını tutuyor
- **Etki**: 2 worker varsa, toplam limit 2x olur (10 req/s → 20 req/s)
- **Örnek**: Worker 1: 10 req/s, Worker 2: 10 req/s → Toplam: 20 req/s (yanlış!)

### 2. API Key Rate Limiter Multi-Worker Sorunu
- **Sorun**: Her worker kendi `_api_key_limiters` dict'ini tutuyor
- **Etki**: Aynı API key farklı worker'larda farklı limit'lere sahip olabilir
- **Örnek**: API key limit: 60 req/min → Worker 1: 60 req/min, Worker 2: 60 req/min → Toplam: 120 req/min (yanlış!)

### 3. Redis Kullanılmıyor
- **Durum**: Redis service var ama rate limiting için kullanılmıyor
- **Etki**: Distributed rate limiting yok

---

## 🔧 Redis Setup Kontrolü

### ✅ Redis Service Var
- **Lokasyon**: `docker-compose.yml` (satır 21-34)
- **Image**: `redis:7-alpine`
- **Port**: 6379
- **Healthcheck**: `redis-cli ping`
- **Volume**: `redis_data:/data`

### ✅ Redis URL Config Var
- **Lokasyon**: `app/config.py` (satır 18)
- **Config**: `redis_url: str = "redis://redis:6379/0"`
- **Environment Variable**: `REDIS_URL` (docker-compose.yml'de set edilmiş)

### ✅ Redis Kullanımı
- **Mevcut**: Celery broker olarak kullanılıyor (`app/core/celery_app.py`)
- **Eksik**: Rate limiting için kullanılmıyor

---

## 🔄 Migration Stratejisi (In-Memory → Redis)

### 1. DNS Rate Limiter Migration

**Mevcut:**
```python
# app/core/rate_limiter.py
_dns_rate_limiter: Optional[RateLimiter] = None

def get_dns_rate_limiter() -> RateLimiter:
    global _dns_rate_limiter
    with _rate_limiter_lock:
        if _dns_rate_limiter is None:
            _dns_rate_limiter = RateLimiter(rate=10.0, burst=10.0)
        return _dns_rate_limiter
```

**Yeni (Redis):**
```python
# app/core/rate_limiter.py
def get_dns_rate_limiter() -> DistributedRateLimiter:
    return DistributedRateLimiter(
        redis_client=redis_client,
        key="dns_rate_limit",
        rate=10.0,
        burst=10.0,
        fallback=InMemoryRateLimiter(rate=10.0, burst=10.0)
    )
```

**Migration Adımları:**
1. `DistributedRateLimiter` class oluştur (Redis-based token bucket)
2. `get_dns_rate_limiter()` fonksiyonunu Redis'e migrate et
3. Fallback mekanizması ekle (Redis down → in-memory)
4. Test: Multi-worker'da rate limit paylaşımı çalışıyor mu?

### 2. WHOIS Rate Limiter Migration

**Mevcut:**
```python
# app/core/rate_limiter.py
_whois_rate_limiter: Optional[RateLimiter] = None

def get_whois_rate_limiter() -> RateLimiter:
    global _whois_rate_limiter
    with _rate_limiter_lock:
        if _whois_rate_limiter is None:
            _whois_rate_limiter = RateLimiter(rate=5.0, burst=5.0)
        return _whois_rate_limiter
```

**Yeni (Redis):**
```python
# app/core/rate_limiter.py
def get_whois_rate_limiter() -> DistributedRateLimiter:
    return DistributedRateLimiter(
        redis_client=redis_client,
        key="whois_rate_limit",
        rate=5.0,
        burst=5.0,
        fallback=InMemoryRateLimiter(rate=5.0, burst=5.0)
    )
```

**Migration Adımları:**
1. `get_whois_rate_limiter()` fonksiyonunu Redis'e migrate et
2. Fallback mekanizması ekle
3. Test: Multi-worker'da rate limit paylaşımı çalışıyor mu?

### 3. API Key Rate Limiter Migration

**Mevcut:**
```python
# app/core/api_key_auth.py
_api_key_limiters: Dict[str, RateLimiter] = {}

def get_api_key_limiter(api_key_id: int, rate_limit_per_minute: int) -> RateLimiter:
    limiter_key = f"api_key_{api_key_id}"
    with _rate_limiter_lock:
        if limiter_key not in _api_key_limiters:
            rate_per_second = rate_limit_per_minute / 60.0
            _api_key_limiters[limiter_key] = RateLimiter(
                rate=rate_per_second,
                burst=rate_limit_per_minute,
            )
        return _api_key_limiters[limiter_key]
```

**Yeni (Redis):**
```python
# app/core/api_key_auth.py
def get_api_key_limiter(api_key_id: int, rate_limit_per_minute: int) -> DistributedRateLimiter:
    return DistributedRateLimiter(
        redis_client=redis_client,
        key=f"api_key_rate_limit:{api_key_id}",
        rate=rate_limit_per_minute / 60.0,
        burst=rate_limit_per_minute,
        fallback=InMemoryRateLimiter(
            rate=rate_limit_per_minute / 60.0,
            burst=rate_limit_per_minute
        )
    )
```

**Migration Adımları:**
1. `get_api_key_limiter()` fonksiyonunu Redis'e migrate et
2. In-memory `_api_key_limiters` dict'ini kaldır
3. Fallback mekanizması ekle
4. Test: Multi-worker'da API key rate limit paylaşımı çalışıyor mu?

---

## 🛡️ Fallback Stratejisi (Redis Down)

### Circuit Breaker Pattern

**Strateji**: Redis down durumunda in-memory rate limiter'a fallback

**Kod Örneği:**
```python
class DistributedRateLimiter:
    def __init__(self, redis_client, key, rate, burst, fallback):
        self.redis_client = redis_client
        self.key = key
        self.rate = rate
        self.burst = burst
        self.fallback = fallback
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30
        )
    
    def acquire(self, tokens: int = 1) -> bool:
        try:
            if self.circuit_breaker.is_open():
                # Circuit breaker açık → fallback kullan
                return self.fallback.acquire(tokens)
            
            # Redis'te rate limit kontrolü
            result = self._redis_acquire(tokens)
            self.circuit_breaker.record_success()
            return result
        except Exception as e:
            # Redis error → fallback kullan
            self.circuit_breaker.record_failure()
            logger.warning("redis_rate_limit_fallback", error=str(e))
            return self.fallback.acquire(tokens)
```

### Degrade Mode Logging

**Strateji**: Redis down durumunda WARN level log + Sentry tag

**Kod Örneği:**
```python
if self.circuit_breaker.is_open():
    logger.warning(
        "rate_limit_redis_down_fallback",
        limiter_key=self.key,
        fallback_to="in_memory",
        extra={"sentry_tags": {"rate_limit_degrade": True}}
    )
    return self.fallback.acquire(tokens)
```

---

## 📊 Redis Rate Limiting Tasarımı

### Token Bucket Algorithm (Redis)

**Redis Key Stratejisi:**
- DNS: `rate_limit:dns` (shared counter)
- WHOIS: `rate_limit:whois` (shared counter)
- API Key: `rate_limit:api_key:{api_key_id}` (per-key counter)

**Redis Operations:**
```python
# Token bucket implementation with Redis
def _redis_acquire(self, tokens: int = 1) -> bool:
    now = time.time()
    key = f"rate_limit:{self.key}"
    
    # Lua script for atomic operations
    lua_script = """
    local key = KEYS[1]
    local rate = tonumber(ARGV[1])
    local burst = tonumber(ARGV[2])
    local tokens = tonumber(ARGV[3])
    local now = tonumber(ARGV[4])
    
    local bucket = redis.call('HMGET', key, 'tokens', 'last_update')
    local current_tokens = tonumber(bucket[1]) or burst
    local last_update = tonumber(bucket[2]) or now
    
    -- Add tokens based on elapsed time
    local elapsed = now - last_update
    current_tokens = math.min(burst, current_tokens + elapsed * rate)
    
    -- Check if we have enough tokens
    if current_tokens >= tokens then
        current_tokens = current_tokens - tokens
        redis.call('HMSET', key, 'tokens', current_tokens, 'last_update', now)
        redis.call('EXPIRE', key, 3600)  -- TTL: 1 hour
        return 1
    else
        redis.call('HMSET', key, 'tokens', current_tokens, 'last_update', now)
        redis.call('EXPIRE', key, 3600)
        return 0
    end
    """
    
    result = self.redis_client.eval(
        lua_script,
        1,  # numkeys
        key,
        self.rate,
        self.burst,
        tokens,
        now
    )
    
    return result == 1
```

---

## 🧪 Test Senaryoları

### 1. Multi-Worker Rate Limiting Test

**Senaryo**: 2 worker, aynı API key, rate limit: 60 req/min

**Beklenen Sonuç:**
- Worker 1: 30 req/min
- Worker 2: 30 req/min
- Toplam: 60 req/min (distributed)

**Test Komutu:**
```bash
# Terminal 1: Worker 1
docker-compose exec worker celery -A app.core.celery_app worker --loglevel=info --concurrency=1

# Terminal 2: Worker 2
docker-compose exec -d worker celery -A app.core.celery_app worker --loglevel=info --concurrency=1

# Terminal 3: Test script
for i in {1..100}; do
  curl -X POST http://localhost:8000/ingest/webhook \
    -H "X-API-Key: test-key" \
    -H "Content-Type: application/json" \
    -d '{"domain": "example.com"}'
done
```

### 2. Redis Down Fallback Test

**Senaryo**: Redis down, rate limiting çalışmaya devam etmeli

**Beklenen Sonuç:**
- Circuit breaker devreye girmeli
- Fallback to in-memory çalışmalı
- WARN level log + Sentry tag

**Test Komutu:**
```bash
# Redis'i durdur
docker-compose stop redis

# Rate limiting isteği yap
curl -X POST http://localhost:8000/scan/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'

# Log kontrolü
docker-compose logs api | grep -i "redis.*down\|fallback\|circuit.*breaker"
```

---

## ✅ Hazırlık Checklist

- [x] Mevcut rate limiter analizi yapıldı (DNS, WHOIS, API key)
- [x] Kullanım yerleri tespit edildi (tasks.py, api_key_auth.py)
- [x] Redis setup kontrolü yapıldı (docker-compose.yml, config.py)
- [x] Migration stratejisi hazırlandı (in-memory → Redis)
- [x] Fallback stratejisi dokümante edildi (circuit breaker + degrade mode)
- [x] Redis rate limiting tasarımı hazırlandı (token bucket + Lua script)
- [x] Test senaryoları belirlendi (multi-worker, Redis down)

---

## 🚀 Sonraki Adımlar

1. **DistributedRateLimiter Class Oluştur**
   - Redis-based token bucket implementation
   - Lua script for atomic operations
   - Circuit breaker pattern

2. **DNS Rate Limiter Migration**
   - `get_dns_rate_limiter()` fonksiyonunu Redis'e migrate et
   - Fallback mekanizması ekle
   - Test: Multi-worker rate limiting

3. **WHOIS Rate Limiter Migration**
   - `get_whois_rate_limiter()` fonksiyonunu Redis'e migrate et
   - Fallback mekanizması ekle
   - Test: Multi-worker rate limiting

4. **API Key Rate Limiter Migration**
   - `get_api_key_limiter()` fonksiyonunu Redis'e migrate et
   - In-memory dict'i kaldır
   - Fallback mekanizması ekle
   - Test: Multi-worker API key rate limiting

5. **Circuit Breaker Implementation**
   - Circuit breaker class oluştur
   - Degrade mode logging ekle
   - Test: Redis down senaryosu

---

**Referans**: `docs/active/P1-IMPLEMENTATION-PLAYBOOK.md` - Distributed Rate Limiting bölümü

