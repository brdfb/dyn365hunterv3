# IP Enrichment Implementation

**Status**: ✅ Implemented  
**Feature Flag**: `HUNTER_ENRICHMENT_ENABLED` (default: `false`)  
**Phase**: Production-ready (no-break upgrade)

## Overview

IP enrichment adds geolocation, ASN, ISP, and proxy detection data to domain scans. The feature is designed as a **no-break upgrade** - it can be deployed to production with the feature flag disabled, and enabled later without any code changes.

## Architecture

### Key Principles

1. **No-break upgrade**: Feature flag disabled by default, all enrichment code is opt-in
2. **Fire-and-forget**: Enrichment runs in separate DB session, doesn't affect scan transaction
3. **Graceful degradation**: Missing DB files don't crash the app, enrichment is skipped
4. **Thread-safe**: Lazy-loaded DB readers with thread-safe initialization
5. **Cached**: 24-hour TTL for IP enrichment results (IPs rarely change)

### Components

- **`app/core/analyzer_enrichment.py`**: Core enrichment logic (MaxMind, IP2Location, IP2Proxy)
- **`app/core/enrichment_service.py`**: Service layer with DB session management
- **`app/core/analyzer_dns.py`**: IP resolution from MX records and root domain
- **`app/db/models.py`**: `IpEnrichment` SQLAlchemy model
- **`app/api/debug.py`**: Debug endpoints for troubleshooting

## Configuration

### Environment Variables

All enrichment settings use the `HUNTER_` prefix:

```bash
# Feature flag (required to enable)
HUNTER_ENRICHMENT_ENABLED=true

# Database paths (at least one required if enabled)
HUNTER_ENRICHMENT_DB_PATH_MAXMIND_ASN=/app/data/maxmind/GeoLite2-ASN.mmdb
HUNTER_ENRICHMENT_DB_PATH_MAXMIND_CITY=/app/data/maxmind/GeoLite2-City.mmdb
HUNTER_ENRICHMENT_DB_PATH_IP2LOCATION=/app/data/ip2location/IP2LOCATION-LITE-DB11.BIN
HUNTER_ENRICHMENT_DB_PATH_IP2PROXY=/app/data/ip2proxy/IP2PROXY-LITE-PX11.BIN
```

### Database Setup

1. **MaxMind GeoLite2** (free, requires account):
   - Sign up at https://www.maxmind.com/en/geolite2/signup
   - Download `GeoLite2-ASN.mmdb` and `GeoLite2-City.mmdb`
   - Place in `app/data/maxmind/` (or configure path)

2. **IP2Location LITE** (free, email required):
   - Download from https://lite.ip2location.com/
   - Place `IP2LOCATION-LITE-DB11.BIN` in `app/data/ip2location/`

3. **IP2Proxy LITE** (free, email required):
   - Download from https://lite.ip2proxy.com/
   - Place `IP2PROXY-LITE-PX11.BIN` in `app/data/ip2proxy/`

## Database Schema

### Migration

```bash
# Run migration
python -m alembic upgrade head
```

### Table: `ip_enrichment`

- **Unique constraint**: `(domain, ip_address)` - enables UPSERT
- **Foreign key**: `companies.domain` (CASCADE delete)
- **Indexes**: `domain`, `ip_address`, composite `(domain, ip_address)`

## Usage

### Automatic Enrichment

Enrichment runs automatically after successful domain scans:

1. Domain is scanned via `/scan/domain` or bulk scan
2. IP addresses are resolved from MX records and root domain
3. First IP is enriched (if enrichment enabled)
4. Result is saved to `ip_enrichment` table

### Debug Endpoints

**Get enrichment for IP**:
```bash
GET /debug/ip-enrichment/{ip}?use_cache=true
```

**Check configuration**:
```bash
GET /debug/ip-enrichment/config
```

## Testing Checklist

### 1. Flag OFF Test (Critical)

```bash
# .env
HUNTER_ENRICHMENT_ENABLED=false
```

**Expected**:
- ✅ App starts without errors
- ✅ No enrichment logs
- ✅ All existing tests pass
- ✅ `/scan/domain` works exactly as before

### 2. Flag ON, DB Missing Test

```bash
# .env
HUNTER_ENRICHMENT_ENABLED=true
HUNTER_ENRICHMENT_DB_PATH_MAXMIND_ASN=/does/not/exist.mmdb
```

**Expected**:
- ✅ App starts (with warning log)
- ✅ `/scan/domain` works (enrichment skipped)
- ✅ No crashes or errors

### 3. Flag ON, DB Available Test

```bash
# .env
HUNTER_ENRICHMENT_ENABLED=true
HUNTER_ENRICHMENT_DB_PATH_MAXMIND_ASN=/app/data/maxmind/GeoLite2-ASN.mmdb
```

**Expected**:
- ✅ App starts (with info log)
- ✅ `/scan/domain` creates enrichment record
- ✅ UPSERT works (rescan doesn't create duplicates)
- ✅ Debug endpoint shows enrichment data

## Performance

- **Cache**: 24-hour TTL (IPs rarely change)
- **Lazy loading**: DB files loaded on first use
- **Thread-safe**: Safe for multi-worker deployments
- **Non-blocking**: Enrichment doesn't delay scan response

## Troubleshooting

### Enrichment Not Working

1. Check feature flag: `HUNTER_ENRICHMENT_ENABLED=true`
2. Check DB paths: Files must exist and be readable
3. Check logs: Look for `ip_enrichment_*` log messages
4. Use debug endpoint: `/debug/ip-enrichment/config`

### Common Issues

**"No database files available"**:
- Set at least one `HUNTER_ENRICHMENT_DB_PATH_*` variable
- Ensure file exists and is readable

**"Module not found"**:
- Install required packages: `pip install geoip2 ip2location IP2Proxy`

**"Enrichment skipped"**:
- Check if IP was resolved (MX records exist)
- Check if enrichment DBs are loaded (see debug endpoint)

## Deployment Strategy

### Phase 1: Deploy with Flag OFF (No Risk)

1. Deploy code + migration
2. Run `alembic upgrade head`
3. Verify all tests pass
4. **Flag remains `false`** → Hunter works exactly as before

### Phase 2: Enable in Stage

1. Set `HUNTER_ENRICHMENT_ENABLED=true` in stage
2. Place DB files in configured paths
3. Test enrichment works
4. Monitor logs for issues

### Phase 3: Enable in Production

1. Set `HUNTER_ENRICHMENT_ENABLED=true` in production
2. Place DB files in configured paths
3. Monitor for 24 hours
4. Verify enrichment data is being collected

## Future Enhancements

- Background task queue (Celery/RQ) for heavy enrichment
- Retention policy for old enrichment records
- Multiple IP enrichment per domain (MX + web IPs)
- Enrichment data in `/leads` endpoint response

