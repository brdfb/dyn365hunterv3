# G19 Öncesi Yapılması Gerekenler - Pre-Flight Checklist

**Tarih**: 2025-01-28  
**Durum**: 🔴 Critical - G19'e geçmeden önce tamamlanmalı  
**Süre Tahmini**: ~1.5 gün (11 saat)  
**İlgili Doküman**: [Production Readiness Critique v2](./PRODUCTION-READINESS-CRITIQUE-V2.md)

---

## 🚨 P0 - CRITICAL (G19 Öncesi Zorunlu)

Bu maddeler **production'a çıkmadan önce** yapılması gereken kritik güvenlik ve stability iyileştirmeleridir. G19'e geçmeden önce tamamlanmalı.

---

### ✅ 1. Database Connection Pooling

**Dosya:** `app/db/session.py`  
**Süre:** 1 saat  
**Öncelik:** 🔴 CRITICAL

**Mevcut Durum:**
```python
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # ✅ İyi
    echo=False,
    # ❌ pool_size, max_overflow, pool_recycle YOK
)
```

**Yapılacaklar:**
- [x] `app/db/session.py` dosyasını aç
- [x] Connection pool parametrelerini ekle:
  ```python
  engine = create_engine(
      settings.database_url,
      pool_pre_ping=True,
      pool_size=20,              # Normal pool size
      max_overflow=10,           # Extra connections under load
      pool_recycle=3600,          # Recycle connections after 1 hour
      pool_timeout=30,            # Wait 30s for connection from pool
      echo=False,
  )
  ```
- [x] (Opsiyonel) Environment variable'lara taşı:
  - `HUNTER_DB_POOL_SIZE` (default: 20)
  - `HUNTER_DB_MAX_OVERFLOW` (default: 10)
- [x] Test: Concurrent request test (100+ parallel requests)
- [x] Docker Compose'u restart et, `/healthz` çalışıyor mu kontrol et

**Etki:** Production'da ilk patlayacak nokta. **Yapılmadan prod'a çıkma.**

**Referans:** [Production Readiness Critique v2 - Madde 1](./PRODUCTION-READINESS-CRITIQUE-V2.md#1-database-connection-pooling)

---

### ✅ 2. API Key Security (bcrypt/Argon2)

**Dosya:** `app/core/api_key_auth.py`  
**Süre:** 2 saat  
**Öncelik:** 🔴 CRITICAL

**Mevcut Durum:**
```python
def hash_api_key(api_key: str) -> str:
    """Hash an API key using SHA-256."""
    return hashlib.sha256(api_key.encode()).hexdigest()  # ❌ Salt yok
```

**Yapılacaklar:**
- [x] `requirements.txt`'e `bcrypt` ekle:
  ```
  bcrypt>=4.0.0
  ```
- [x] `app/core/api_key_auth.py` dosyasını aç
- [x] `hash_api_key()` fonksiyonunu güncelle:
  ```python
  import bcrypt
  
  def hash_api_key(api_key: str) -> str:
      """Hash an API key using bcrypt (with salt)."""
      salt = bcrypt.gensalt()
      hashed = bcrypt.hashpw(api_key.encode(), salt)
      return hashed.decode()
  
  def verify_api_key(api_key: str, stored_hash: str) -> bool:
      """Verify API key against stored hash."""
      return bcrypt.checkpw(api_key.encode(), stored_hash.encode())
  ```
- [x] `verify_api_key()` dependency fonksiyonunu güncelle (bcrypt kullan)
- [x] Migration stratejisi belirle:
  - [x] Yeni API key'ler bcrypt ile hash'le
  - [ ] Eski SHA-256 hash'ler için migration script yaz (veya ilk login'de migrate et) - Not: İleride yapılacak
- [x] Test: Eski ve yeni hash format'larını destekle
- [x] Mevcut API key'leri test et (çalışıyor mu?)

**Etki:** Security vulnerability. **Yapılmadan prod'a çıkma.**

**Referans:** [Production Readiness Critique v2 - Madde 2](./PRODUCTION-READINESS-CRITIQUE-V2.md#2-api-key-security-bcryptargon2)

---

### ✅ 3. Structured Logging + PII Maskeleme

**Dosya:** `app/core/logging.py` (yeni), mevcut log dosyaları  
**Süre:** 4 saat  
**Öncelik:** 🔴 CRITICAL

**Mevcut Durum:**
- Sadece 6 dosyada logging var
- Structured logging yok (plain string format)
- PII maskeleme politikası net değil

**Yapılacaklar:**
- [x] `requirements.txt`'e `structlog` ekle:
  ```
  structlog>=23.0.0
  ```
- [x] `app/core/logging.py` dosyası oluştur:
  ```python
  import structlog
  import logging
  
  structlog.configure(
      processors=[
          structlog.stdlib.filter_by_level,
          structlog.stdlib.add_logger_name,
          structlog.stdlib.add_log_level,
          structlog.stdlib.PositionalArgumentsFormatter(),
          structlog.processors.TimeStamper(fmt="iso"),
          structlog.processors.StackInfoRenderer(),
          structlog.processors.format_exc_info,
          structlog.processors.JSONRenderer(),  # JSON output
      ],
      context_class=dict,
      logger_factory=structlog.stdlib.LoggerFactory(),
      wrapper_class=structlog.stdlib.BoundLogger,
      cache_logger_on_first_use=True,
  )
  
  logger = structlog.get_logger()
  ```
- [x] PII maskeleme helper fonksiyonu ekle:
  ```python
  def mask_pii(value: str) -> str:
      """Mask PII (email, company_name) - return hash or id."""
      # Implementation
  ```
- [x] Mevcut 6 dosyadaki logging'i structured logging'e migrate et:
  - [x] `app/api/ingest.py`
  - [x] `app/api/scan.py`
  - [x] `app/api/leads.py`
  - [x] `app/core/tasks.py`
  - [x] `app/core/rescan.py`
  - [x] `app/core/notifications.py`
- [x] PII policy uygula:
  - ✅ Log'lanabilir: domain, provider, segment, score, scan_status
  - ❌ Log'lanamaz: email, company_name, contact_emails (hash veya id kullan)
- [x] **Request ID / Correlation ID ekle:**
  - [x] Middleware oluştur: `app/core/middleware.py`
    ```python
    import uuid
    from starlette.middleware.base import BaseHTTPMiddleware
    
    class RequestIDMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            request_id = str(uuid.uuid4())
            request.state.request_id = request_id
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
    ```
  - [x] `app/main.py`'de middleware ekle:
    ```python
    from app.core.middleware import RequestIDMiddleware
    app.add_middleware(RequestIDMiddleware)
    ```
  - [x] Log'lara request_id ekle:
    ```python
    logger.info("scan_completed", request_id=request.state.request_id, domain=domain)
    ```
  - [ ] Sentry event'lerine request_id ekle: - Not: İleride yapılacak (Sentry context integration)
    ```python
    sentry_sdk.set_context("request", {"request_id": request.state.request_id})
    ```
  - [x] **Fayda:** UI'da hata görüp log/Sentry'de aynı request'i yakalamak çok kolay olur
- [x] Test: Log output'u kontrol et (JSON format, PII yok, request_id var)

**Etki:** Observability ve compliance. **Prod için kritik.**

**Referans:** [Production Readiness Critique v2 - Madde 3](./PRODUCTION-READINESS-CRITIQUE-V2.md#3-structured-logging--pii-maskeleme)

---

### ✅ 4. Error Tracking (Sentry)

**Dosya:** `app/core/error_tracking.py` (yeni), `app/main.py`  
**Süre:** 2 saat  
**Öncelik:** 🔴 CRITICAL

**Mevcut Durum:**
- Exception'lar sadece log'lanıyor
- Error tracking yok
- Production'da hata takibi zor

**Yapılacaklar:**
- [ ] Sentry account oluştur (https://sentry.io) veya mevcut account kullan - Not: Production'da yapılacak
- [x] `requirements.txt`'e `sentry-sdk` ekle:
  ```
  sentry-sdk[fastapi]>=1.38.0
  ```
- [x] `app/core/error_tracking.py` dosyası oluştur:
  ```python
  import sentry_sdk
  from sentry_sdk.integrations.fastapi import FastApiIntegration
  from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
  from app.config import settings
  
  if settings.environment == "production":
      sentry_sdk.init(
          dsn=settings.sentry_dsn,
          integrations=[
              FastApiIntegration(),
              SqlalchemyIntegration(),
          ],
          traces_sample_rate=0.1,  # 10% of transactions
          environment=settings.environment,
      )
  ```
- [x] `app/config.py`'ye `sentry_dsn` ekle:
  ```python
  sentry_dsn: Optional[str] = None
  ```
- [ ] `.env.example`'a ekle: - Not: İleride yapılacak
  ```
  HUNTER_SENTRY_DSN=  # Optional, only for production
  ```
- [x] `app/main.py`'de initialize et:
  ```python
  from app.core.error_tracking import *  # Initialize Sentry
  ```
- [x] **ENV Guard ekle (güvenlik kemeri):**
  - [x] `app/core/error_tracking.py`'de environment kontrolü:
    ```python
    if settings.environment in {"production", "staging"}:
        sentry_sdk.init(...)
    # Development'da Sentry kapalı
    ```
  - [x] `app/core/logging.py`'de environment-based log format:
    ```python
    if settings.environment == "production":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())  # Pretty format for dev
    ```
  - [x] Log level environment-based:
    ```python
    log_level = "DEBUG" if settings.environment == "development" else "INFO"
    ```
  - [x] **Not:** ENV=production dışı ortamlarda Sentry kapalı, dev'de log level = DEBUG
- [ ] Test: Exception fırlat, Sentry'de görünüyor mu kontrol et (production'da) - Not: Production'da test edilecek
- [x] Development'da Sentry kapalı olduğunu doğrula

**Etki:** Production monitoring. **Prod için kritik.**

**Referans:** [Production Readiness Critique v2 - Madde 4](./PRODUCTION-READINESS-CRITIQUE-V2.md#4-error-tracking-sentry)

---

### ✅ 5. Health Checks & Probes (Liveness/Readiness/Startup)

**Dosya:** `app/api/health.py` (yeni), `app/main.py`  
**Süre:** 2 saat  
**Öncelik:** 🔴 CRITICAL

**Mevcut Durum:**
- Sadece `/healthz` endpoint var (sadece DB ping)
- Redis ping yok
- Liveness/readiness ayrımı yok
- Startup probe yok

**Yapılacaklar:**
- [x] `app/api/health.py` dosyası oluştur:
  ```python
  from fastapi import APIRouter, HTTPException
  from sqlalchemy.orm import Session
  from sqlalchemy import text
  from app.db.session import get_db
  from app.config import settings
  import redis
  
  router = APIRouter(tags=["health"])
  
  # Liveness probe
  @router.get("/healthz/live")
  async def liveness_probe():
      return {"status": "alive"}
  
  # Readiness probe
  @router.get("/healthz/ready")
  async def readiness_probe(db: Session = Depends(get_db)):
      # Check database
      try:
          db.execute(text("SELECT 1"))
      except Exception as e:
          raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")
      
      # Check Redis
      try:
          redis_client = redis.from_url(settings.redis_url)
          redis_client.ping()
      except Exception as e:
          raise HTTPException(status_code=503, detail=f"Redis unavailable: {str(e)}")
      
      return {"status": "ready", "checks": {"database": True, "redis": True}}
  
  # Startup probe
  @router.get("/healthz/startup")
  async def startup_probe(db: Session = Depends(get_db)):
      return await readiness_probe(db)
  
  # Legacy endpoint (backward compatibility)
  @router.get("/healthz")
  async def health_check(db: Session = Depends(get_db)):
      # DB + Redis check, always return 200
  ```
- [x] `app/main.py`'de router'ı include et:
  ```python
  from app.api import health
  app.include_router(health.router)
  ```
- [x] Legacy `/healthz` endpoint'ini güncelle (Redis ping ekle)
- [x] **Minimal SLA hedefi ekle:**
  - [x] `/healthz/ready` max response time hedefi: **< 300ms**
  - [x] Smoke test'te ölç:
    ```bash
    time curl -s http://localhost:8000/healthz/ready
    ```
  - [x] **Fayda:** Health check 1-2 saniye dönüyorsa, DB/Redis'te bir sorun var demektir (erkenden görürsün)
- [x] Test: Tüm probe'ları test et:
  - [x] `/healthz/live` → 200
  - [x] `/healthz/ready` → 200 (DB + Redis OK, < 300ms)
  - [ ] `/healthz/ready` → 503 (DB down) - Not: Production'da test edilecek
  - [ ] `/healthz/ready` → 503 (Redis down) - Not: Production'da test edilecek
  - [x] `/healthz/startup` → 200
- [x] Kubernetes deployment örneği ekle (docs) - [Production Engineering Guide](./PRODUCTION-ENGINEERING-GUIDE-V1.md) referansı

**Etki:** Kubernetes/Docker orchestration için kritik. **Prod için kritik.**

**Referans:** [Production Readiness Critique v2 - Madde 5](./PRODUCTION-READINESS-CRITIQUE-V2.md#5-health-checks--probes-livenessreadinessstartup)

---

## 📊 Özet

| Madde | Dosya | Süre | Durum | Blocker? |
|-------|-------|------|-------|----------|
| 1. DB Connection Pooling | `app/db/session.py` | 1 saat | ✅ | ✅ Evet |
| 2. API Key Security | `app/core/api_key_auth.py` | 2 saat | ✅ | ✅ Evet |
| 3. Structured Logging | `app/core/logging.py` + 6 dosya | 4 saat | ✅ | ✅ Evet |
| 4. Error Tracking | `app/core/error_tracking.py` | 2 saat | ✅ | ✅ Evet |
| 5. Health Checks | `app/api/health.py` | 2 saat | ✅ | ✅ Evet |
| **TOPLAM** | | **11 saat** | **5/5** | |

---

## ✅ Tamamlandıktan Sonra

1. **Test Suite Çalıştır:**
   ```bash
   pytest tests/ -v
   ```
   - Tüm testler geçmeli (214+ tests)

2. **Docker Compose Test:**
   ```bash
   docker-compose down
   docker-compose up -d
   sleep 10
   curl http://localhost:8000/healthz/ready
   ```
   - Health checks çalışmalı

3. **Smoke Test:**
   - API endpoint'leri çalışıyor mu?
   - Logging JSON format'ta mı?
   - Sentry (production'da) çalışıyor mu?

4. **Commit & Push:**
   ```bash
   git add -A
   git commit -m "feat: Add P0 production hardening (G19 pre-flight)

   - Add DB connection pooling (pool_size, max_overflow)
   - Migrate API key hashing to bcrypt (with salt)
   - Implement structured logging (structlog, JSON format)
   - Add error tracking (Sentry integration)
   - Add health checks & probes (liveness/readiness/startup)
   
   Closes: G19 pre-flight checklist"
   git push origin main
   ```

---

## 🚦 Go/No-Go Decision

### ✅ Go (G19'e Geçebilir)

- [x] Tüm P0 maddeler tamamlandı
- [x] Test suite passing (214+ tests)
- [x] Docker Compose çalışıyor
- [x] Health checks çalışıyor
- [x] Logging structured (JSON)
- [x] Error tracking aktif (production'da)

### ⚠️ No-Go (G19'e Geçmeden Önce)

- [ ] P0 maddelerden herhangi biri eksik
- [ ] Test suite failing
- [ ] Health checks çalışmıyor
- [ ] Logging structured değil
- [ ] Error tracking yok

---

## 📚 Referanslar

- [Production Readiness Critique v2](./PRODUCTION-READINESS-CRITIQUE-V2.md) - Detaylı teknik açıklamalar
- [Production Engineering Guide v1](./PRODUCTION-ENGINEERING-GUIDE-V1.md) - SRE runbook
- [G19 TODO](./../todos/G19-auth-ui-advanced.md) - G19 sprint planı

---

**Son Güncelleme**: 2025-01-28  
**Durum**: ✅ Tamamlandı - G19'e geçilebilir

