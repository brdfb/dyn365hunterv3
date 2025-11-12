# Dyn365Hunter MVP - Go/No-Go Checklist

## Go Criteria (Tümü Yeşil Olmalı)

### Infrastructure & Setup
- [ ] **INFRA-1**: Docker Compose up → PostgreSQL healthy, FastAPI healthy
  - Check: `docker-compose ps` → postgres "healthy", api "healthy"
  - Fail: Container crash, healthcheck fail

- [ ] **INFRA-2**: `/healthz` endpoint responds 200 OK
  - Check: `curl http://localhost:8000/healthz` → `{"status": "ok", "database": "connected"}`
  - Fail: 500 error, timeout, DB connection fail

- [ ] **INFRA-3**: Database schema migration successful
  - Check: `docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "\dt"` → 4 tables (raw_leads, companies, domain_signals, lead_scores)
  - Check: `docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "\dv"` → 1 VIEW (leads_ready)
  - Fail: Missing tables, migration error

### Core Functionality

- [ ] **CORE-1**: Domain ingestion works (`POST /ingest/domain`)
  - Check: `curl -X POST http://localhost:8000/ingest/domain -H "Content-Type: application/json" -d '{"domain": "example.com", "company_name": "Example"}'` → 201 Created
  - Check: `docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "SELECT COUNT(*) FROM raw_leads;"` → ≥1 row
  - Fail: 400/500 error, DB insert fail

- [ ] **CORE-2**: Domain normalization works
  - Check: `POST /ingest/domain {"domain": "WWW.EXAMPLE.COM"}` → DB'de `"example.com"` (lowercase, www stripped)
  - Check: `POST /ingest/domain {"domain": "user@example.com"}` → DB'de `"example.com"` (email extracted)
  - Fail: Normalization fail, duplicate domain handling fail

- [ ] **CORE-3**: Single domain scan works (`POST /scan/domain`) ≤10s
  - Check: `curl -X POST http://localhost:8000/scan/domain -H "Content-Type: application/json" -d '{"domain": "example.com"}'` → 200 OK, response time ≤10s (cold: ≤15s)
  - Check: Response contains: `{"domain": "example.com", "score": <number>, "segment": <string>, "reason": <string>}`
  - Check: `domain_signals` tablosunda kayıt (MX/SPF/DKIM/DMARC değerleri)
  - Check: `lead_scores` tablosunda kayıt (score + segment + reason)
  - Fail: Timeout >10s, 500 error, missing data in DB

- [ ] **CORE-4**: DNS analysis works (MX/SPF/DKIM/DMARC)
  - Check: `POST /scan/domain {"domain": "google.com"}` → MX root: `"aspmx.l.google.com"`, SPF/DKIM/DMARC detected
  - Check: `POST /scan/domain {"domain": "microsoft.com"}` → MX root contains `"outlook"` or `"protection.outlook"`, SPF/DKIM/DMARC detected
  - Fail: DNS lookup fail, timeout, incorrect MX root extraction

- [ ] **CORE-5**: WHOIS analysis works (optional, graceful fail)
  - Check: `POST /scan/domain {"domain": "example.com"}` → WHOIS data (registrar/expires_at) veya None (graceful fail)
  - Check: WHOIS fail durumunda scoring devam ediyor (score dönüyor)
  - Fail: WHOIS fail → sistem crash, scoring fail

- [ ] **CORE-6**: Provider mapping works
  - Check: `POST /scan/domain {"domain": "microsoft.com"}` → provider: `"M365"` (MX root → provider classification)
  - Check: `POST /scan/domain {"domain": "google.com"}` → provider: `"Google"`
  - Check: `POST /scan/domain {"domain": "example.com"}` → provider: `"Local"` (mail.example.com) veya `"Unknown"`
  - Fail: Provider mapping fail, incorrect classification

- [ ] **CORE-7**: Scoring works (rule-based)
  - Check: `POST /scan/domain {"domain": "microsoft.com"}` → score ≥50 (M365 provider points)
  - Check: `POST /scan/domain {"domain": "google.com"}` → score ≥30 (Google provider points)
  - Check: SPF/DKIM/DMARC detected → signal points added
  - Fail: Scoring fail, incorrect score calculation

- [ ] **CORE-8**: Segment logic works
  - Check: `POST /scan/domain {"domain": "microsoft.com"}` → segment: `"Existing"` (provider == M365)
  - Check: `POST /scan/domain {"domain": "google.com"}` → segment: `"Migration"` (provider in [Google, Yandex, Hosting, Local])
  - Check: `POST /scan/domain {"domain": "invalid-domain-xyz-123.com"}` → segment: `"Skip"` (mx_missing)
  - Fail: Segment logic fail, incorrect segment assignment

### Leads API

- [ ] **LEADS-1**: Leads query works (`GET /leads`) <1s
  - Check: `curl "http://localhost:8000/leads"` → 200 OK, response time <1s, JSON array
  - Fail: 500 error, timeout >1s

- [ ] **LEADS-2**: Leads filtering works (`GET /leads?segment=Migration&min_score=70`)
  - Check: `GET /leads?segment=Migration` → filtered results (segment == Migration)
  - Check: `GET /leads?min_score=70` → filtered results (score ≥70)
  - Check: `GET /leads?provider=M365` → filtered results (provider == M365)
  - Check: `GET /leads?segment=Migration&min_score=70` → combined filter works
  - Fail: Filtering fail, incorrect results

- [ ] **LEADS-3**: Single lead query works (`GET /lead/{domain}`)
  - Check: `GET /lead/example.com` → 200 OK, single lead details (signals + score + reason)
  - Check: `GET /lead/invalid-domain` → 404 Not Found
  - Fail: 500 error, missing data

### Demo Scenario (Kahvelik Akış)

- [ ] **DEMO-1**: 3 domain ingest → scan → leads query → ≥1 Migration lead ≥70 score
  - Steps:
    1. `POST /ingest/domain {"domain": "example.com", "company_name": "Example Inc"}` → 201
    2. `POST /ingest/domain {"domain": "google.com", "company_name": "Google"}` → 201
    3. `POST /ingest/domain {"domain": "microsoft.com", "company_name": "Microsoft"}` → 201
    4. `POST /scan/domain {"domain": "example.com"}` → 200, score dönüyor
    5. `POST /scan/domain {"domain": "google.com"}` → 200, score dönüyor
    6. `POST /scan/domain {"domain": "microsoft.com"}` → 200, score dönüyor
    7. `GET /leads?segment=Migration&min_score=70` → ≥1 lead dönüyor
  - Total time: ≤2 minutes (setup hariç)
  - Fail: Any step fails, no Migration lead ≥70 score

### Data Files

- [ ] **DATA-1**: `providers.json` valid and loaded
  - Check: `load_providers()` → 10+ provider loaded, valid JSON
  - Check: Provider mapping çalışıyor (MX root → provider)
  - Fail: Invalid JSON, missing providers, mapping fail

- [ ] **DATA-2**: `rules.json` valid and loaded
  - Check: `load_rules()` → rules loaded, valid JSON
  - Check: Scoring rules çalışıyor (base_score, provider_points, signal_points, segment_rules)
  - Fail: Invalid JSON, missing rules, scoring fail

### Error Handling

- [ ] **ERROR-1**: Invalid domain handling
  - Check: `POST /scan/domain {"domain": "invalid-domain-xyz-123"}` → 400 Bad Request, error message
  - Fail: 500 error, crash

- [ ] **ERROR-2**: DNS timeout handling
  - Check: `POST /scan/domain {"domain": "slow-dns-domain.com"}` → timeout ≤10s, graceful fail (scan_status: "dns_timeout")
  - Fail: Timeout >10s, crash

- [ ] **ERROR-3**: WHOIS fail handling
  - Check: `POST /scan/domain {"domain": "whois-fail-domain.com"}` → WHOIS fail, scoring devam ediyor
  - Fail: WHOIS fail → crash, scoring fail

- [ ] **ERROR-4**: PII masking in logs
  - Check: Log files → domain görünüyor, email/company_name görünmüyor
  - Fail: PII in logs

### Tests

- [ ] **TEST-1**: Test suite runs successfully
  - Check: `pytest tests/` → all tests pass (≥15 tests)
  - Check: Coverage ≥70% (normalizer, analyzer_dns, analyzer_whois, scorer, ingest)
  - Fail: Tests fail, coverage <70%

## No-Go Criteria (Herhangi Biri Fail Olursa DUR)

### Bloklayıcı Hatalar

- [ ] **BLOCK-1**: Docker Compose setup fail
  - Fail: `bash setup_dev.sh` → error, containers don't start
  - Action: **STOP**, fix Docker setup

- [ ] **BLOCK-2**: Database connection fail
  - Fail: `/healthz` → `{"database": "disconnected"}`
  - Action: **STOP**, fix DB connection

- [ ] **BLOCK-3**: Schema migration fail
  - Fail: Missing tables, migration error
  - Action: **STOP**, fix schema migration

- [ ] **BLOCK-4**: Core ingestion fail
  - Fail: `POST /ingest/domain` → 500 error, DB insert fail
  - Action: **STOP**, fix ingestion logic

- [ ] **BLOCK-5**: Core scan fail
  - Fail: `POST /scan/domain` → 500 error, timeout >15s, crash
  - Action: **STOP**, fix scan logic

- [ ] **BLOCK-6**: Scoring fail
  - Fail: Scoring logic çalışmıyor, incorrect scores, segment logic fail
  - Action: **STOP**, fix scoring logic

- [ ] **BLOCK-7**: Demo scenario fail
  - Fail: 3 domain → scan → leads query → no Migration lead ≥70 score
  - Action: **STOP**, verify scoring rules, provider mapping

- [ ] **BLOCK-8**: Data files invalid
  - Fail: `providers.json` or `rules.json` invalid JSON, missing data
  - Action: **STOP**, fix data files

- [ ] **BLOCK-9**: PII leak in logs
  - Fail: Email/company_name in logs
  - Action: **STOP**, fix logging

- [ ] **BLOCK-10**: Test suite fail
  - Fail: `pytest tests/` → tests fail, coverage <70%
  - Action: **STOP**, fix tests

## Go Decision Matrix

| Category | Must-Have | Should-Have | Nice-to-Have |
|----------|-----------|-------------|--------------|
| Infrastructure | INFRA-1, INFRA-2, INFRA-3 | - | - |
| Core Functionality | CORE-1, CORE-3, CORE-6, CORE-7, CORE-8 | CORE-2, CORE-4, CORE-5 | - |
| Leads API | LEADS-1, LEADS-2 | LEADS-3 | - |
| Demo Scenario | DEMO-1 | - | - |
| Data Files | DATA-1, DATA-2 | - | - |
| Error Handling | ERROR-1, ERROR-2 | ERROR-3, ERROR-4 | - |
| Tests | TEST-1 | - | - |

**Go Decision:** Tüm "Must-Have" maddeler yeşil olmalı.

**No-Go Decision:** Herhangi bir "Bloklayıcı" madde fail olursa dur.

