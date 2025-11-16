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

### Quick Start

**🚀 Hızlı Başlangıç**: Detaylı setup rehberi için → [`IP-ENRICHMENT-QUICK-START.md`](./IP-ENRICHMENT-QUICK-START.md)

**Özet**:
1. 3 DB dosyasını indir (MaxMind, IP2Location, IP2Proxy)
2. `app/data/` dizinine koy
3. `.env`'de `HUNTER_ENRICHMENT_ENABLED=true` yap
4. Docker'ı yeniden başlat

### Environment Variables

**New Format (Recommended)**:
```bash
# Feature flag (required to enable)
HUNTER_ENRICHMENT_ENABLED=true

# MaxMind GeoIP Databases
MAXMIND_CITY_DB=app/data/maxmind/GeoLite2-City.mmdb
MAXMIND_COUNTRY_DB=app/data/maxmind/GeoLite2-Country.mmdb
# MAXMIND_ASN_DB=app/data/maxmind/GeoLite2-ASN.mmdb  # Optional - only add if you use ASN database

# IP2Location & IP2Proxy
IP2LOCATION_DB=app/data/ip2location/IP2LOCATION-LITE-DB11.BIN
IP2PROXY_DB=app/data/ip2proxy/IP2PROXY-LITE-PX11.BIN
```

**Legacy Format (Still Supported)**:
```bash
# Legacy format (backward compatible)
HUNTER_ENRICHMENT_DB_PATH_MAXMIND_ASN=/app/data/maxmind/GeoLite2-ASN.mmdb
HUNTER_ENRICHMENT_DB_PATH_MAXMIND_CITY=/app/data/maxmind/GeoLite2-City.mmdb
HUNTER_ENRICHMENT_DB_PATH_IP2LOCATION=/app/data/ip2location/IP2LOCATION-LITE-DB11.BIN
HUNTER_ENRICHMENT_DB_PATH_IP2PROXY=/app/data/ip2proxy/IP2PROXY-LITE-PX11.BIN
```

### Database Setup

1. **MaxMind GeoLite2** (free, requires account):
   - Sign up at https://www.maxmind.com/en/geolite2/signup
   - Download `GeoLite2-City.mmdb` (required) and `GeoLite2-Country.mmdb` (optional fallback)
   - Optional: Download `GeoLite2-ASN.mmdb` for ASN data
   - Place in `app/data/maxmind/` (or configure path)

2. **IP2Location LITE** (free, email required):
   - Download from https://lite.ip2location.com/
   - Place `IP2LOCATION-LITE-DB11.BIN` in `app/data/ip2location/`

3. **IP2Proxy LITE** (free, email required):
   - Download from https://lite.ip2proxy.com/
   - Place `IP2PROXY-LITE-PX11.BIN` in `app/data/ip2proxy/`

**📖 Detaylı Setup**: [`IP-ENRICHMENT-QUICK-START.md`](./IP-ENRICHMENT-QUICK-START.md) - Adım adım rehber

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

## Security Notes

### Debug Endpoints

⚠️ **Important**: Debug endpoints (`/debug/ip-enrichment/*`) are for **internal/admin use only**.

**Production Recommendations**:
- Restrict access to internal network only, OR
- Add authentication (admin token) to debug endpoints, OR
- Disable debug endpoints in production environment

**Current Status**: Debug endpoints are publicly accessible. Consider adding authentication middleware or network restrictions before enabling in production.

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

## Deployment Strategy & Rollout Plan

### Phase 1: Dev Environment (Flag OFF)

**Status**: `HUNTER_ENRICHMENT_ENABLED=false` (default)

**Purpose**: 
- All existing test scenarios continue to work
- No behavioral changes, zero risk

**Verification**:
- Run test suite → all tests pass
- Verify no enrichment logs appear
- `/healthz` shows `enrichment_enabled: false`

### Phase 2: Stage Environment (Flag ON)

**Status**: `HUNTER_ENRICHMENT_ENABLED=true`

**Setup**:
1. Set `HUNTER_ENRICHMENT_ENABLED=true` in stage environment
2. Place DB files in configured paths (MaxMind, IP2Location, IP2Proxy)
3. Restart application

**Sanity Checks**:
```bash
# Check health endpoint
curl http://stage-api/healthz | jq '.enrichment_enabled'
# Expected: true

# Check debug endpoint
curl http://stage-api/debug/ip-enrichment/config | jq '.availability'
# Expected: {"at_least_one_db_available": true}

# Test enrichment
curl http://stage-api/debug/ip-enrichment/8.8.8.8 | jq '.enrichment'
# Expected: enrichment result with data

# Verify DB record
psql -c "SELECT COUNT(*) FROM ip_enrichment;"
# Expected: > 0 after test scans
```

**Monitoring**:
- Check logs for `ip_enrichment_saved` / `ip_enrichment_failed` messages
- Verify no errors in Sentry (if configured)

### Phase 3: Production (First 1-2 Days)

**Status**: `HUNTER_ENRICHMENT_ENABLED=true`

**Monitoring Checklist**:

1. **Sentry Error Tracking**:
   - Filter by `hunter_enrichment_error=true` tag
   - Monitor error rate (should be < 1%)
   - Check for `ip_enrichment_save_failed` / `ip_enrichment_failed` events
   - **Action if errors spike**: Set flag to `false` immediately (no code change needed)

2. **Database Health**:
   ```sql
   -- Check table growth
   SELECT COUNT(*) FROM ip_enrichment;
   SELECT COUNT(*) FROM ip_enrichment WHERE created_at > NOW() - INTERVAL '1 hour';
   ```
   - Verify row count is increasing (enrichment is working)
   - Check for reasonable growth rate (not exponential)
   - **Action if no growth**: Check logs, verify DB files are accessible

3. **Health Check**:
   ```bash
   curl http://prod-api/healthz | jq '.enrichment_enabled'
   # Expected: true
   ```

### Phase 4: Production (After 1-2 Days)

**If no issues**:
- ✅ Feature is stable, keep enabled
- ✅ Monitor weekly for first month
- ✅ Review retention policy after 6 months

**If issues found**:
- Set `HUNTER_ENRICHMENT_ENABLED=false` (instant disable, no code change)
- Investigate issues, fix, re-enable in stage first
- Re-rollout after fixes verified

## API Exposure (Level 1 - Minimal)

**Status**: ✅ **IMPLEMENTED** (2025-01-28)

### Infrastructure Summary Field

The `infrastructure_summary` field is now available in `/leads` and `/lead/{domain}` API responses.

**Format**: Human-readable single-line summary
- Example: `"Hosted on DataCenter, ISP: Hetzner, Country: DE"`
- Example: `"Hosted on Commercial, ISP: Amazon, Country: US"`

**Components**:
1. **Usage Type** (most important signal):
   - `DCH` → "DataCenter" (hosting/reseller detection)
   - `COM` → "Commercial" (business hosting)
   - `RES` → "Residential" (home/consumer)
   - `MOB` → "Mobile" (mobile carrier)
2. **ISP**: Internet Service Provider name
3. **Country**: ISO 3166-1 alpha-2 country code

**API Response Example**:
```json
{
  "domain": "example.com",
  "score": 72,
  "segment": "Migration",
  "provider": "Local",
  "infrastructure_summary": "Hosted on DataCenter, ISP: Hetzner, Country: DE"
}
```

**Implementation**:
- `app/core/enrichment_service.py`:
  - `latest_ip_enrichment()` - Get most recent enrichment record
  - `build_infra_summary()` - Build human-readable summary
- `app/api/leads.py`:
  - `LeadResponse.infrastructure_summary` - Optional field
  - Automatically populated in `get_leads()` and `get_lead()` endpoints

**Backward Compatibility**:
- Field is optional (`None` if no enrichment data available)
- No breaking changes to existing API consumers
- Graceful degradation: if enrichment is disabled or no data exists, field is `null`

**Performance Note**:
- Current implementation queries enrichment data per lead (N+1 pattern)
- For large lead lists, consider batch query optimization in future
- Single lead endpoint (`/lead/{domain}`) performance is acceptable

## Future Enhancements

### Level 2 - Detailed Infrastructure Block (Planned)
- Detailed infrastructure panel in lead detail view
- Full IP, ASN, proxy detection details
- UI component for infrastructure insights

### Level 3 - Advanced Analytics (Future)
- "TR dışı firmalar listesi" (non-TR companies list)
- "Hosting & Reseller tespit oranı" (hosting detection rate)
- "Proxy şüphesi olanlar" (proxy suspicion list)
- Heatmap (country distribution)

### Other Enhancements
- Background task queue (Celery/RQ) for heavy enrichment
- **Retention policy for old enrichment records** (TASK: Review after 6 months)
  - Monitor `ip_enrichment` table growth
  - Consider cleanup policy: `DELETE FROM ip_enrichment WHERE created_at < NOW() - INTERVAL '365 days'`
  - Add to maintenance cron job if table size becomes a concern
- Multiple IP enrichment per domain (MX + web IPs)
- Metrics integration (Prometheus/Sentry):
  - `ip_enrichment_success_count`
  - `ip_enrichment_error_count`
  - `ip_enrichment_cache_hit_rate`

