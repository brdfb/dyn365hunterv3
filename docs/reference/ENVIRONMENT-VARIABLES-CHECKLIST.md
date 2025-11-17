# Environment Variables Checklist - Production v1.0

**Tarih**: 2025-01-28  
**Versiyon**: v1.0.0  
**Status**: ✅ **Production Ready**  
**Kullanım**: Production deployment öncesi environment variables kontrolü

---

## 📋 Checklist

### ✅ **REQUIRED (Zorunlu)**

#### Database
- [ ] `DATABASE_URL` - PostgreSQL connection string
  - Format: `postgresql://user:password@host:port/database`
  - Example: `postgresql://dyn365hunter:secure_password@db.example.com:5432/dyn365hunter`
  - **Production**: Use secure credentials, SSL enabled
  - **Validation**: Connection test required before deployment

#### Redis
- [ ] `REDIS_URL` - Redis connection string
  - Format: `redis://host:port/db` or `redis://:password@host:port/db`
  - Example: `redis://redis.example.com:6379/0`
  - **Production**: Use secure credentials if password-protected
  - **Validation**: Connection test required before deployment

#### API Configuration
- [ ] `API_HOST` - API server host (default: `0.0.0.0`)
  - **Production**: Usually `0.0.0.0` (bind to all interfaces)
  
- [ ] `API_PORT` - API server port (default: `8000`)
  - **Production**: Usually `8000` or configured port

- [ ] `LOG_LEVEL` - Logging level (default: `INFO`)
  - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
  - **Production**: `INFO` or `WARNING` (not `DEBUG`)

- [ ] `ENVIRONMENT` - Environment name (default: `development`)
  - **Production**: Must be `production`
  - Used for feature flags and environment-specific behavior

---

### ⚠️ **OPTIONAL (Önerilen)**

#### Error Tracking
- [ ] `HUNTER_SENTRY_DSN` - Sentry DSN for error tracking
  - Format: `https://<key>@<org>.ingest.sentry.io/<project>`
  - **Production**: Strongly recommended
  - **Validation**: Test error reporting after deployment

#### Database Connection Pooling
- [ ] `HUNTER_DB_POOL_SIZE` - Connection pool size (default: `20`)
  - **Production**: Adjust based on load (20-50 recommended)
  
- [ ] `HUNTER_DB_MAX_OVERFLOW` - Max overflow connections (default: `10`)
  - **Production**: Adjust based on load (10-20 recommended)

---

### 🔒 **FEATURE FLAGS (Post-MVP - Şimdilik OFF)**

#### IP Enrichment
- [x] `HUNTER_ENRICHMENT_ENABLED` - IP enrichment feature flag (default: `false`)
  - **Production v1.0**: ✅ `true` (Activated 2025-01-28)
  - If enabled, also configure database paths below

#### Partner Center Integration
- [ ] `HUNTER_PARTNER_CENTER_ENABLED` - Partner Center feature flag (default: `false`)
  - **Production v1.0**: `false` (Post-MVP feature - Decision: Feature Flag OFF)
  - **Decision Date**: 2025-01-28
  - If enabled in future, configure OAuth credentials below

---

### 📦 **IP ENRICHMENT DATABASES (Optional - Only if HUNTER_ENRICHMENT_ENABLED=true)**

#### MaxMind Databases
- [ ] `MAXMIND_CITY_DB` - Path to GeoLite2-City.mmdb
  - Example: `app/data/maxmind/GeoLite2-City.mmdb`
  - **Production**: Ensure file exists and is readable

- [ ] `MAXMIND_COUNTRY_DB` - Path to GeoLite2-Country.mmdb (optional)
  - Example: `app/data/maxmind/GeoLite2-Country.mmdb`
  - **Production**: Optional fallback for country-only lookups

- [ ] `MAXMIND_ASN_DB` - Path to GeoLite2-ASN.mmdb (optional)
  - Example: `app/data/maxmind/GeoLite2-ASN.mmdb`
  - **Production**: Optional, only if ASN data needed

#### IP2Location & IP2Proxy
- [ ] `IP2LOCATION_DB` - Path to IP2LOCATION-LITE-DB11.BIN
  - Example: `app/data/ip2location/IP2LOCATION-LITE-DB11.BIN`
  - **Production**: Ensure file exists and is readable

- [ ] `IP2PROXY_DB` - Path to IP2PROXY-LITE-PX11.BIN
  - Example: `app/data/ip2proxy/IP2PROXY-LITE-PX11.BIN`
  - **Production**: Ensure file exists and is readable

---

### 🔐 **PARTNER CENTER OAUTH (Optional - Only if HUNTER_PARTNER_CENTER_ENABLED=true)**

**Note**: Partner Center integration is Post-MVP. These variables are only needed if feature flag is enabled in future.

- [ ] `HUNTER_PARTNER_CENTER_CLIENT_ID` - Azure AD OAuth client ID
- [ ] `HUNTER_PARTNER_CENTER_TENANT_ID` - Azure AD tenant ID
- [ ] `HUNTER_PARTNER_CENTER_API_URL` - Partner Center API base URL (default: `https://api.partnercenter.microsoft.com`)
- [ ] `HUNTER_PARTNER_CENTER_SCOPE` - MSAL scope (default: `https://api.partner.microsoft.com/.default`)
- [ ] `HUNTER_PARTNER_CENTER_TOKEN_CACHE_PATH` - Token cache file path (optional, defaults to `.token_cache`)

---

## 🔍 Validation Steps

### 1. Pre-Deployment Validation

```bash
# Check required variables are set
echo "DATABASE_URL: ${DATABASE_URL:0:20}..."  # Show first 20 chars only
echo "REDIS_URL: ${REDIS_URL:0:20}..."
echo "ENVIRONMENT: $ENVIRONMENT"
echo "LOG_LEVEL: $LOG_LEVEL"

# Test database connection
# (Use your database client or pg_isready)
pg_isready -h <host> -p <port> -U <user>

# Test Redis connection
redis-cli -h <host> -p <port> ping
```

### 2. Post-Deployment Validation

```bash
# Check environment in health endpoint
curl http://localhost:8000/healthz | jq '.environment'

# Check Sentry is configured (if enabled)
# Trigger a test error and verify it appears in Sentry dashboard
```

---

## 📝 Production Environment Template

```bash
# Database
DATABASE_URL=postgresql://dyn365hunter:secure_password@db.example.com:5432/dyn365hunter

# Redis
REDIS_URL=redis://redis.example.com:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=production

# Error Tracking (Recommended)
HUNTER_SENTRY_DSN=https://<key>@<org>.ingest.sentry.io/<project>

# Database Connection Pooling (Optional - defaults are usually fine)
HUNTER_DB_POOL_SIZE=20
HUNTER_DB_MAX_OVERFLOW=10

# Feature Flags (Production v1.0 - Both OFF)
HUNTER_ENRICHMENT_ENABLED=false
HUNTER_PARTNER_CENTER_ENABLED=false
```

---

## ⚠️ Security Notes

1. **Never commit `.env` files to version control**
   - Use `.env.example` as template
   - Store production secrets in secure vault (e.g., AWS Secrets Manager, Azure Key Vault)

2. **Use strong passwords for production**
   - Database passwords: Minimum 16 characters, mixed case, numbers, symbols
   - Redis passwords: If password-protected, use strong password

3. **Enable SSL/TLS for database connections**
   - Production `DATABASE_URL` should use SSL: `postgresql://...?sslmode=require`

4. **Rotate secrets regularly**
   - Database passwords: Every 90 days
   - API keys: Every 180 days
   - Sentry DSN: As needed

---

## 📚 Related Documents

- `docs/active/PRODUCTION-DEPLOYMENT-CHECKLIST.md` - Full deployment checklist
- `docs/active/ROLLBACK-PLAN.md` - Rollback procedures
- `.env.example` - Environment variables template
- `app/config.py` - Application configuration source

---

**Last Updated**: 2025-01-28  
**Status**: ✅ **Production Ready**

