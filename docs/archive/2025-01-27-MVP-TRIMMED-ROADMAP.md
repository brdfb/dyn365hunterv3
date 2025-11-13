# Dyn365Hunter MVP - Trimmed Roadmap (10 İş Günü)

## Scope Reduction Summary

**Çıkarılanlar:**
- Phase 6: UI (Optional)
- `/ingest/webhook` endpoint
- `/scan/bulk` endpoint (sequential riskli)
- `POST /export` CSV endpoint
- `scripts/demo_run.sh`
- `app/core/exporter.py`

**Kalan MVP Core:**
- Docker setup (Compose, healthcheck)
- FastAPI skeleton + `/healthz`
- PostgreSQL + SQLAlchemy models
- Domain normalization
- `/ingest/csv` ve `/ingest/domain`
- DNS analyzer (MX/SPF/DKIM/DMARC)
- WHOIS analyzer (optional, graceful fail)
- Provider mapping
- Rule-based scorer
- `/scan/domain` (single domain)
- `GET /leads` (filtered)
- `GET /leads/{domain}` (single lead)
- Basic tests (3 test file)
- README.md

## Gün Bazlı Plan

### G1: Foundation & Docker Setup
**Hedef:** Docker Compose ile PostgreSQL + FastAPI çalışıyor, `/healthz` yanıt veriyor.

**İşler:**
- `Dockerfile` oluştur (Python 3.10-slim, uvicorn)
- `docker-compose.yml` (postgres + api, healthcheck, volumes)
- `.dockerignore`
- `setup_dev.sh` (Docker check, .env copy, compose up, schema migration, healthcheck)
- `.env.example` (DATABASE_URL, POSTGRES_*, API_*, LOG_LEVEL)
- `requirements.txt` (fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic-settings)
- `app/__init__.py`
- `app/main.py` (FastAPI app, `/healthz` endpoint)
- `app/config.py` (Pydantic Settings, DATABASE_URL)
- `app/db/__init__.py`
- `app/db/session.py` (SQLAlchemy engine, session factory)

**Test/Acceptance:**
- `bash setup_dev.sh` → success, no errors
- `curl http://localhost:8000/healthz` → `{"status": "ok", "database": "connected"}`

**Done Criteria:**
- ✅ Docker Compose up, PostgreSQL healthy
- ✅ FastAPI `/healthz` 200 OK
- ✅ DB connection test passed

---

### G2: Database Schema & Models
**Hedef:** PostgreSQL schema oluşturuldu, SQLAlchemy models tanımlandı.

**İşler:**
- `app/db/schema.sql` (CREATE TABLE: raw_leads, companies, domain_signals, lead_scores, VIEW: leads_ready)
- `app/db/models.py` (SQLAlchemy models: RawLead, Company, DomainSignal, LeadScore)
- Schema migration script (Python veya Alembic init)
- `setup_dev.sh` güncelle (schema.sql migration otomatik)

**Test/Acceptance:**
- `docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "\dt"` → 4 table görünüyor
- `docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "\dv"` → `leads_ready` VIEW görünüyor
- Python: `from app.db.models import Company; Company.__table__.columns` → domain UNIQUE constraint var

**Done Criteria:**
- ✅ 4 table + 1 VIEW oluşturuldu
- ✅ Models SQLAlchemy'de tanımlı
- ✅ Migration otomatik çalışıyor

---

### G3: Domain Normalization & Data Files
**Hedef:** Domain normalization çalışıyor, `providers.json` ve `rules.json` hazır.

**İşler:**
- `app/core/__init__.py`
- `app/core/normalizer.py` (`normalize_domain()`, `extract_domain_from_email()`, `extract_domain_from_website()`)
- `app/data/providers.json` (10+ provider: M365, Google, Yandex, Hosting, Local, Unknown + örnek MX roots)
- `app/data/rules.json` (base_score, provider_points, signal_points, segment_rules)
- `app/core/provider_map.py` (`load_providers()`, `classify_provider()`)
- `app/core/scorer.py` (`load_rules()`, `calculate_score()`, `determine_segment()`, `score_domain()`)

**Test/Acceptance:**
- `normalize_domain("WWW.EXAMPLE.COM")` → `"example.com"`
- `normalize_domain("xn--example.com")` → punycode decode
- `extract_domain_from_email("user@example.com")` → `"example.com"`
- `classify_provider("outlook-com.olc.protection.outlook.com")` → `"M365"`
- `classify_provider("mail.example.com")` → `"Local"`
- `load_providers()` → 10+ provider yükleniyor
- `load_rules()` → rules yükleniyor

**Done Criteria:**
- ✅ Normalizer 3 fonksiyon çalışıyor
- ✅ `providers.json` ve `rules.json` valid JSON, içerik dolu
- ✅ Provider mapping ve scorer skeleton hazır

---

### G4: Ingest Endpoints (CSV + Domain)
**Hedef:** Domain ve CSV ingestion çalışıyor, `raw_leads` tablosuna yazıyor.

**İşler:**
- `app/api/__init__.py`
- `app/api/ingest.py` (`POST /ingest/domain`, `POST /ingest/csv`)
- `app/core/merger.py` (`upsert_companies()` - domain unique key)
- `app/main.py` güncelle (ingest router register)
- `requirements.txt` güncelle (pandas, python-multipart)

**Test/Acceptance:**
- `POST /ingest/domain {"domain": "example.com", "company_name": "Example"}` → 201, `raw_leads` tablosunda kayıt
- `POST /ingest/csv` (multipart, 5 satır CSV) → 201, 5 kayıt `raw_leads` tablosunda
- Duplicate domain → idempotent upsert (company güncelleniyor)

**Done Criteria:**
- ✅ `/ingest/domain` çalışıyor
- ✅ `/ingest/csv` çalışıyor (pandas parse)
- ✅ Normalization uygulanıyor
- ✅ `companies` tablosuna upsert çalışıyor

---

### G5: DNS Analyzer
**Hedef:** DNS analizi çalışıyor (MX/SPF/DKIM/DMARC), `domain_signals` tablosuna yazıyor.

**İşler:**
- `app/core/analyzer_dns.py` (`get_mx_records()`, `check_spf()`, `check_dkim()`, `check_dmarc()`, `analyze_dns()`)
- `requirements.txt` güncelle (dnspython)
- Timeout handling (10s), error handling

**Test/Acceptance:**
- `analyze_dns("example.com")` → MX, SPF, DKIM, DMARC değerleri dönüyor
- `analyze_dns("invalid-domain-xyz-123.com")` → timeout veya error, graceful fail
- `analyze_dns("google.com")` → MX root: `"aspmx.l.google.com"`, SPF/DKIM/DMARC var

**Done Criteria:**
- ✅ DNS analyzer 4 fonksiyon çalışıyor
- ✅ Timeout 10s, error handling var
- ✅ MX root extraction çalışıyor

---

### G6: WHOIS Analyzer
**Hedef:** WHOIS lookup çalışıyor (optional, graceful fail), `domain_signals` tablosuna yazıyor.

**İşler:**
- `app/core/analyzer_whois.py` (`get_whois_info()`)
- `requirements.txt` güncelle (python-whois)
- Timeout handling (5s), error handling (graceful fail)

**Test/Acceptance:**
- `get_whois_info("example.com")` → registrar, expires_at, nameservers dönüyor
- `get_whois_info("invalid-domain-xyz-123.com")` → None veya error, graceful fail
- WHOIS fail durumunda scoring devam ediyor (WHOIS puanı 0)

**Done Criteria:**
- ✅ WHOIS analyzer çalışıyor
- ✅ Timeout 5s, graceful fail var
- ✅ WHOIS fail durumunda sistem çökmez

---

### G7: Scan Endpoint & Scoring Integration
**Hedef:** `/scan/domain` endpoint çalışıyor, DNS + WHOIS analizi yapıp scoring uyguluyor.

**İşler:**
- `app/api/scan.py` (`POST /scan/domain`)
- `app/main.py` güncelle (scan router register)
- Scoring integration (`score_domain()` çağrısı)
- `domain_signals` ve `lead_scores` tablosuna yazma

**Test/Acceptance:**
- `POST /scan/domain {"domain": "example.com"}` → 200, `domain_signals` ve `lead_scores` tablosunda kayıt
- Response: `{"domain": "example.com", "score": 75, "segment": "Migration", "reason": "..."}`
- Scan süresi ≤10s (cold: ≤15s)
- Invalid domain → 400 error

**Done Criteria:**
- ✅ `/scan/domain` çalışıyor
- ✅ DNS + WHOIS analizi yapılıyor
- ✅ Scoring uygulanıyor, `lead_scores` tablosuna yazılıyor
- ✅ Response time ≤10s

---

### G8: Leads API
**Hedef:** `/leads` ve `/leads/{domain}` endpoint'leri çalışıyor, filtreleme yapıyor.

**İşler:**
- `app/api/leads.py` (`GET /leads`, `GET /leads/{domain}`)
- `app/main.py` güncelle (leads router register)
- Query params: `segment`, `min_score`, `provider`
- `leads_ready` VIEW kullanımı

**Test/Acceptance:**
- `GET /leads?segment=Migration&min_score=70` → filtered results
- `GET /leads/example.com` → single lead details (signals + score + reason)
- Empty result → `[]` (200 OK)
- Invalid domain → 404

**Done Criteria:**
- ✅ `/leads` filtreleme çalışıyor
- ✅ `/leads/{domain}` single lead dönüyor
- ✅ Response time <1s

---

### G9: Tests & Edge Cases
**Hedef:** 3 test dosyası hazır, edge case'ler test ediliyor.

**İşler:**
- `tests/__init__.py`
- `tests/test_scan_single.py` (DNS/WHOIS mock, analyzer test, edge cases: timeout, invalid domain)
- `tests/test_scorer_rules.py` (scoring rules test, segment logic test, edge cases: override, missing MX)
- `tests/test_ingest_csv.py` (CSV parsing test, normalization test, edge cases: malformed CSV, empty file)
- `requirements.txt` güncelle (pytest, pytest-mock)

**Test/Acceptance:**
- `pytest tests/` → tüm testler geçiyor (≥15 test)
- Coverage: normalizer, analyzer_dns, analyzer_whois, scorer, ingest (≥70%)

**Done Criteria:**
- ✅ 3 test dosyası hazır
- ✅ Edge case'ler test ediliyor
- ✅ Test coverage ≥70%

---

### G10: Documentation & Demo
**Hedef:** README.md hazır, demo senaryosu çalışıyor.

**İşler:**
- `README.md` (setup instructions, .env template, WSL2 + Docker setup, demo commands, acceptance criteria)
- Demo senaryosu: 3 domain ingest → scan → leads query
- Final acceptance test: `/healthz`, `/ingest/domain`, `/scan/domain`, `/leads` → tümü çalışıyor

**Test/Acceptance:**
- README.md'yi takip eden yeni kullanıcı setup yapabiliyor
- Demo senaryosu: 3 domain → ≥1 Migration lead ≥70 skor
- `curl` komutları README'deki gibi çalışıyor

**Done Criteria:**
- ✅ README.md tam ve doğru
- ✅ Demo senaryosu çalışıyor
- ✅ Exit criteria sağlanıyor

---

## Exit Criteria (Kahvelik Akış Demo Senaryosu)

**Senaryo:** Satışçı 3 domain'i analiz edip Migration segment'inde ≥70 skorlu lead'leri görüyor.

**Adımlar:**
1. `bash setup_dev.sh` → success
2. `curl -X POST http://localhost:8000/ingest/domain -H "Content-Type: application/json" -d '{"domain": "example.com", "company_name": "Example Inc"}'` → 201
3. `curl -X POST http://localhost:8000/scan/domain -H "Content-Type: application/json" -d '{"domain": "example.com"}'` → 200, score dönüyor
4. (2-3 domain daha ingest + scan)
5. `curl "http://localhost:8000/leads?segment=Migration&min_score=70"` → ≥1 lead dönüyor

**Süre:** ≤2 dakika (setup hariç)

**Başarı Kriteri:**
- ✅ Tüm endpoint'ler çalışıyor
- ✅ Scoring doğru çalışıyor (Migration segment, ≥70 skor)
- ✅ Response time kabul edilebilir (scan ≤10s, leads <1s)

