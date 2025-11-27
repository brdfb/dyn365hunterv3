# Dev vs Prod Environment Differences

**Tarih:** 2025-01-30  
**Versiyon:** v1.0.0  
**Status:** ✅ **Güncel**

---

## 🎯 Özet

**Kod seviyesinde:** ✅ **EŞİT** - Aynı kod, aynı branch  
**Konfigürasyon seviyesinde:** ⚠️ **FARKLI** - Environment variable'lar ve feature flag'ler farklı

---

## 📋 Feature Flags (Her İkisi de Default: `false`)

### Partner Center Integration
- **Dev:** `HUNTER_PARTNER_CENTER_ENABLED=false` (default)
- **Prod:** `HUNTER_PARTNER_CENTER_ENABLED=false` (default)
- **Durum:** ✅ **EŞİT** - Her ikisi de kapalı (MVP-safe)
- **Not:** Production'da aktifleştirmek için `HUNTER_PARTNER_CENTER_ENABLED=true` set edilmeli

### Dynamics 365 Integration
- **Dev:** `HUNTER_D365_ENABLED=false` (default)
- **Prod:** `HUNTER_D365_ENABLED=false` (default)
- **Durum:** ✅ **EŞİT** - Her ikisi de kapalı (MVP-safe)
- **Not:** Production'da aktifleştirmek için `HUNTER_D365_ENABLED=true` set edilmeli

### IP Enrichment
- **Dev:** `HUNTER_ENRICHMENT_ENABLED=false` (default)
- **Prod:** `HUNTER_ENRICHMENT_ENABLED=false` (default)
- **Durum:** ✅ **EŞİT** - Her ikisi de kapalı (default)
- **Not:** Her iki ortamda da DB dosyaları yoksa kapalı kalır

---

## ⚙️ Environment-Based Differences

### 1. Celery Sync Interval (Partner Center)

**Kod:** `app/core/celery_app.py` (lines 45-49)

```python
"schedule": (
    30.0 if settings.environment == "development" 
    else float(settings.partner_center_sync_interval)
),
```

- **Dev:** `30 saniye` (auto-override, test için)
- **Prod:** `600 saniye` (10 dakika, `HUNTER_PARTNER_CENTER_SYNC_INTERVAL` env var)
- **Durum:** ⚠️ **FARKLI** - Dev'de daha sık sync (test için)

---

### 2. Log Level

**Kod:** `app/core/logging.py` (line 34)

```python
log_level = "DEBUG" if settings.environment == "development" else "INFO"
```

- **Dev:** `DEBUG` (detaylı loglar)
- **Prod:** `INFO` (sadece önemli loglar)
- **Durum:** ⚠️ **FARKLI** - Dev'de daha detaylı logging

---

### 3. Log Format

**Kod:** `app/core/logging.py` (lines 20-23)

```python
if settings.environment == "production":
    _processors.append(structlog.processors.JSONRenderer())  # JSON output for production
else:
    _processors.append(structlog.dev.ConsoleRenderer())  # Pretty format for dev
```

- **Dev:** Pretty console format (okunabilir)
- **Prod:** JSON format (log aggregation için)
- **Durum:** ⚠️ **FARKLI** - Dev'de human-readable, Prod'da machine-readable

---

### 4. Sentry Error Tracking

**Kod:** `app/core/error_tracking.py` (lines 12-22)

```python
if settings.environment in {"production", "staging"}:
    if hasattr(settings, "sentry_dsn") and settings.sentry_dsn:
        sentry_sdk.init(...)
```

- **Dev:** Sentry **disabled** (sentry_dsn kontrol edilmez)
- **Prod:** Sentry **enabled** (if `HUNTER_SENTRY_DSN` provided)
- **Durum:** ⚠️ **FARKLI** - Prod'da error tracking aktif

---

### 5. Environment Variable

**Kod:** `app/config.py` (line 27)

```python
environment: str = "development"  # Default
```

- **Dev:** `ENVIRONMENT=development` (default)
- **Prod:** `ENVIRONMENT=production` (zorunlu)
- **Durum:** ⚠️ **FARKLI** - Environment name farklı

---

## 🔍 Kod Seviyesi Karşılaştırması

### ✅ Aynı Olanlar

1. **Core Engine:** ✅ Tamamen aynı
   - DNS analyzer
   - WHOIS analyzer
   - Scoring engine
   - Sales engine
   - Provider mapping
   - Normalization

2. **API Endpoints:** ✅ Tamamen aynı
   - Tüm endpoint'ler aynı
   - Feature flag kontrolü aynı
   - Response format aynı

3. **Database Schema:** ✅ Tamamen aynı
   - Aynı migration'lar
   - Aynı tablolar
   - Aynı view'ler

4. **Celery Tasks:** ✅ Tamamen aynı
   - Task logic aynı
   - Sadece schedule interval farklı (Partner Center sync)

5. **Error Handling:** ✅ Tamamen aynı
   - Aynı exception handling
   - Sadece Sentry tracking farklı (prod'da aktif)

---

## 📊 Özet Tablo

| Özellik | Dev | Prod | Durum |
|---------|-----|------|-------|
| **Kod** | ✅ Aynı | ✅ Aynı | ✅ **EŞİT** |
| **Feature Flags** | `false` (default) | `false` (default) | ✅ **EŞİT** |
| **Partner Center Sync** | 30s | 600s | ⚠️ **FARKLI** |
| **Log Level** | `DEBUG` | `INFO` | ⚠️ **FARKLI** |
| **Log Format** | Pretty | JSON | ⚠️ **FARKLI** |
| **Sentry** | Disabled | Enabled (if DSN) | ⚠️ **FARKLI** |
| **Environment** | `development` | `production` | ⚠️ **FARKLI** |

---

## 🎯 Sonuç

### Kod Seviyesi: ✅ **EŞİT**

- Aynı kod base
- Aynı branch
- Aynı feature flag default'ları
- Aynı API endpoints
- Aynı database schema

### Konfigürasyon Seviyesi: ⚠️ **FARKLI** (Beklenen)

- **Celery sync interval:** Dev'de daha sık (test için)
- **Log level:** Dev'de DEBUG, Prod'da INFO
- **Log format:** Dev'de pretty, Prod'da JSON
- **Sentry:** Prod'da aktif (if DSN provided)
- **Environment name:** Farklı (development vs production)

### Feature Flags: ✅ **EŞİT** (Default: `false`)

- Partner Center: `false` (her ikisi de)
- D365: `false` (her ikisi de)
- IP Enrichment: `false` (her ikisi de)

---

## 📝 Notlar

1. **Feature Flag'ler:** Her iki ortamda da default `false` - MVP-safe yaklaşım
2. **Environment-based differences:** Beklenen ve normal (dev test için, prod production için optimize)
3. **Kod parity:** ✅ Kod seviyesinde tam eşitlik var
4. **Production deployment:** Feature flag'leri aktifleştirmek için environment variable'lar set edilmeli

---

## 🔗 İlgili Dokümanlar

- `docs/reference/ENVIRONMENT-VARIABLES-CHECKLIST.md` - Environment variable'lar
- `docs/reference/PRODUCTION-DEPLOYMENT-GUIDE.md` - Production deployment
- `docs/active/CRITICAL-3-HAMLE-PRODUCT-READY.md` - Feature flag aktifleştirme planları

---

**Son Güncelleme:** 2025-01-30

