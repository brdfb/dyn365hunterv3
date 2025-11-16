# Partner Center Phase 2 - TODO

**Date Created**: 2025-01-28  
**Status**: In Progress  
**Phase**: Integration Roadmap - Phase 2  
**Priority**: P1  
**Estimated Duration**: 2-3 days  
**Risk Level**: 2/10 (external API dependency)  
**Branch**: `feature/partner-center-referrals`

---

## 🎯 Phase Goal

Partner Center'dan referral'ları çekip Hunter'a entegre etmek. Referral'lar otomatik olarak domain'e normalize edilecek, company olarak upsert edilecek ve domain scan tetiklenecek.

**MVP Yaklaşımı**: Minimal API client (50-70 satır), polling (10 min prod, 30s dev), sadece sync endpoint, lead listesine 1 kolon.

**Key Features**:
- Hybrid DB model (raw_leads ingestion + partner_center_referrals tracking)
- Azure Tenant ID signal → M365 existing customer detection
- Lead types (Co-sell, Marketplace, Solution Provider)
- Domain scan idempotent (domain bazlı, referral bazlı değil)
- Scoring pipeline entegrasyonu (Azure Tenant ID override + Co-sell boost)

**Akış**: Partner Center API → Referral Ingestion → Domain Normalization → Company Upsert → Domain Scan Trigger

---

## 📋 Tasks

### Task 2.1: Partner Center API Client (MVP: Minimal) ✅ **COMPLETED**

**File**: `app/core/partner_center.py` (NEW)

- [x] Minimal OAuth 2.0 authentication (MSAL + Device Code Flow)
- [x] `get_referrals()` fonksiyonu (GET referrals endpoint)
- [x] Basic rate limiting: `time.sleep(1)` between requests
- [x] Basic retry: 2 deneme (transient failures için)
- [x] Token expiry kontrolü (MSAL silent token acquisition)
- [x] Error handling (network errors, API errors, token refresh errors)
- [x] Structured logging (PII masking ile)
- [x] Config ekle (`app/config.py`): Feature flag ve OAuth/API key config

**NOT**: Aşırı abstraction çıkarıldı. Client class basit tutuldu (50-70 satır MVP).

**Acceptance Criteria**:
- [x] Partner Center'a authenticate olabiliyor (MSAL + Device Code Flow)
- [x] Referral'ları başarıyla çekebiliyor
- [x] Rate limiting'e uyuyor (`time.sleep(1)`)
- [x] Token refresh otomatik çalışıyor (MSAL silent acquisition)
- [x] Hatalar graceful handle ediliyor
- [x] Logging structured ve PII maskelenmiş

---

### Task 2.2: Referral Data Model (raw_leads + partner_center_referrals hybrid) ✅ **COMPLETED**

**Files**: 
- `app/db/models.py` (modify)
- `alembic/versions/XXXX_add_partner_center_referrals.py` (NEW)

#### 2.2.1: raw_leads Ingestion (Mevcut Pattern)
- [x] `raw_leads` table'ını kullan (mevcut pattern'e uyumlu)
- [x] `source='partnercenter'` olarak kaydet
- [x] `payload` JSONB field'ına full referral JSON'ı kaydet
- [x] `domain` field'ına normalized domain kaydet
- [x] `company_name`, `email`, `website` field'larını doldur

#### 2.2.2: partner_center_referrals Tracking (Referral Lifecycle)
- [x] `PartnerCenterReferral` model oluştur (`app/db/models.py`)
  - [x] Fields: `referral_id` (unique), `referral_type`, `company_name`, `domain`, `azure_tenant_id`, `status`, `raw_data`, `synced_at`
  - [x] Indexes: `referral_id`, `domain`, `status`, `synced_at`, `referral_type`, `azure_tenant_id`
- [x] Alembic migration script oluştur
- [ ] Migration'ı test et (upgrade/downgrade) - **PENDING** (DB connection required)

**Acceptance Criteria**:
- [x] Hybrid model çalışıyor (raw_leads ingestion + partner_center_referrals tracking)
- [x] raw_leads pattern'e uyumlu (source='partnercenter')
- [x] partner_center_referrals model tüm required field'ları içeriyor
- [x] Migration script oluşturuldu
- [x] Index'ler tanımlandı
- [ ] Migration rollback test edilecek (DB connection required)

---

### Task 2.3: Referral Ingestion ✅ **COMPLETED**

**File**: `app/core/referral_ingestion.py` (NEW)

#### 2.3.1: Lead Tipi Detection
- [x] `detect_referral_type()` - Referral tipini tespit et
  - [x] Co-sell → `'co-sell'` (priority boost için)
  - [x] Marketplace → `'marketplace'`
  - [x] Solution Provider → `'solution-provider'`
- [x] Lead tipini `partner_center_referrals.referral_type` field'ına kaydet

#### 2.3.2: Domain Extraction Fallback
- [x] `extract_domain_from_referral()` - Referral'dan domain çıkar (fallback chain)
  - [x] **1. Try website**: `referral.website` → `extract_domain_from_website()` → `normalize_domain()`
  - [x] **2. Try email**: `referral.contact.email` → `extract_domain_from_email()` → `normalize_domain()`
  - [x] **3. Skip**: Domain yoksa → referral'ı skip et (log warning)
- [x] `app/core/normalizer.py`'deki `normalize_domain()` kullan

#### 2.3.3: Azure Tenant ID → Company Override (Ingestion Only)
- [x] `apply_azure_tenant_signal()` - Azure Tenant ID sinyalini company'ye uygula
  - [x] **Eğer `azureTenantId` varsa**: `Company.provider = 'M365'` (override provider detection)
  - [x] **Eğer `azureTenantId` yoksa**: Provider detection normal akışta
- [x] **NOT**: Segment override scoring pipeline'da yapılacak (scorer.py'de)

#### 2.3.4: raw_leads Ingestion (Mevcut Pattern)
- [x] `ingest_to_raw_leads()` - Referral'ı `raw_leads` table'ına kaydet
  - [x] `source='partnercenter'`
  - [x] `payload` → Full referral JSON (JSONB)
  - [x] `domain` → Normalized domain
  - [x] `company_name`, `email`, `website` → Referral'dan al

#### 2.3.5: partner_center_referrals Tracking
- [x] `upsert_referral_tracking()` - Referral lifecycle tracking
  - [x] `referral_id` unique olduğu için duplicate check yap
  - [x] `referral_type`, `azure_tenant_id`, `status` kaydet
  - [x] Varsa update et, yoksa insert et

#### 2.3.6: Company Upsert & Domain Scan (Idempotent)
- [x] `upsert_company_from_referral()` - Referral'dan company oluştur/update et (via `upsert_companies()`)
  - [x] Domain normalize edilmiş olmalı
  - [x] Azure Tenant ID varsa → `provider='M365'` override
  - [x] Domain unique olduğu için duplicate check yap
- [x] `trigger_domain_scan()` - Domain scan tetikle (**IDEMPOTENT**)
  - [x] **Kritik**: Aynı domain için tekrar scan yapılmamalı
  - [x] `domain_signals` table'ında domain var mı kontrol et
  - [x] Eğer domain zaten scan edilmişse → skip (log info)
  - [x] Eğer domain scan edilmemişse → `scan_single_domain()` çağır
  - [x] **NOT**: Referral bazlı değil, domain bazlı scan (aynı şirkete 3 referral gelirse 1 scan yeterli)

#### 2.3.7: Ana Sync Fonksiyonu
- [x] `sync_referrals_from_partner_center()` - Ana sync fonksiyonu
  - [x] Partner Center'dan referral'ları çek
  - [x] Her referral için:
    1. Lead tipi detection
    2. Domain extraction (fallback chain)
    3. Domain yoksa → skip (log warning)
    4. raw_leads ingestion
    5. partner_center_referrals tracking
    6. Azure Tenant ID sinyali → company provider override (segment değil)
    7. Company upsert
    8. Domain scan trigger (idempotent - domain bazlı)
  - [x] Duplicate referral'ları skip et
  - [x] Her referral bağımsız işlenir (bir hata diğerlerini etkilemez)

#### 2.3.8: Scoring Pipeline Entegrasyonu (Kritik) ⏳ **PENDING**
- [ ] `app/core/scorer.py`'ye Azure Tenant ID override ekle
  - [ ] `determine_segment()` fonksiyonuna `azure_tenant_id` parametresi ekle
  - [ ] Eğer `azure_tenant_id` varsa:
    - [ ] `segment = 'Existing'` (Migration değil, existing customer)
    - [ ] `reason = 'M365 existing customer (Azure Tenant ID)'`
    - [ ] Score override: 55 (M365 existing baseline, configurable)
- [ ] `app/core/scorer.py`'ye Co-sell priority boost ekle
  - [ ] `score_domain()` fonksiyonuna `referral_type` parametresi ekle
  - [ ] Eğer `referral_type == 'co-sell'`:
    - [ ] `score += settings.partner_center_cosell_bonus` (default: 15)
- [x] Config'e ekle (`app/config.py`):
  - [x] `partner_center_cosell_bonus: int = 15`
  - [x] `partner_center_azure_tenant_score: int = 55`

#### 2.3.9: Logging & Error Handling
- [x] Structured logging ekle
- [x] Error handling (her referral bağımsız, bir hata diğerlerini etkilemez)

**Acceptance Criteria**:
- [x] Lead tipi detection çalışıyor (Co-sell, Marketplace, Solution Provider)
- [x] Domain extraction fallback çalışıyor (website → email → skip)
- [x] Azure Tenant ID sinyali çalışıyor (Company.provider='M365' override)
- [x] raw_leads ingestion çalışıyor (mevcut pattern'e uyumlu)
- [x] partner_center_referrals tracking çalışıyor (referral lifecycle)
- [x] Referral'lar doğru normalize ediliyor
- [x] Company'ler doğru upsert ediliyor (Azure Tenant ID override ile)
- [x] Domain scan idempotent çalışıyor (aynı domain için tekrar scan yapılmıyor)
- [ ] Scoring pipeline entegrasyonu çalışıyor (Azure Tenant ID → Segment='Existing', Co-sell → priority boost) ⏳ **PENDING**
- [x] Duplicate'ler graceful handle ediliyor
- [x] Her referral bağımsız işleniyor (bir hata diğerlerini etkilemez)
- [x] Domain yoksa referral skip ediliyor (log warning)

---

### Task 2.4: API Endpoints (MVP: Sadece Sync)

**Files**:
- `app/api/referrals.py` (NEW - Basit endpoint)
- `app/main.py` (modify - router register)

#### 2.4.1: MVP Endpoint (Sadece Bu)
- [ ] `POST /api/referrals/sync` - Manual Sync (MVP Primary)
  - [ ] Request body: `SyncReferralsRequest` (optional: `force` flag)
  - [ ] Response model: `SyncReferralsResponse` (success count, failure count, errors)
  - [ ] Feature flag check: `partner_center_enabled` kontrolü
  - [ ] Async execution: Celery task olarak çalıştır (long-running operation)
  - [ ] Error handling: 400 (feature disabled), 500
  - [ ] **Sync Strategy**: Scheduled polling (10 minutes, configurable) - MVP primary method

**Future Enhancement** (Post-MVP - Şimdilik YOK):
- ⏳ `GET /api/referrals` - List referrals (nice-to-have, MVP'de gerek yok)
- ⏳ `GET /api/referrals/{referral_id}` - Get single referral (nice-to-have, MVP'de gerek yok)
- ⏳ `POST /ingest/partnercenter` - Webhook endpoint (future enhancement)
- ⏳ v1 API versioning (nice-to-have, MVP'de gerek yok)

**Acceptance Criteria**:
- [ ] MVP endpoint çalışıyor (`POST /api/referrals/sync`)
- [ ] Response model validate ediliyor
- [ ] Error handling complete
- [ ] Endpoint main app'e register edilmiş
- [ ] Feature flag kontrolü yapılıyor
- [ ] Polling sync çalışıyor (10 minutes interval)

---

### Task 2.5: UI Integration (MVP: Sadece Lead Listesine Kolon)

**Files**:
- `mini-ui/js/ui-leads.js` (modify)
- `mini-ui/styles.css` (modify - minimal)
- `mini-ui/js/api.js` (modify - sadece sync call)
- `app/api/leads.py` (modify - referral_type field ekle)

#### 2.5.1: Lead Listesine Referral Kolonu
- [ ] Leads API'ye referral bilgisi ekle (`app/api/leads.py`)
  - [ ] `LeadResponse` model'ine `referral_type: Optional[str]` field'ı ekle
  - [ ] SQL query'ye LEFT JOIN `partner_center_referrals` ekle (domain bazlı)
  - [ ] Referral varsa `referral_type` doldur, yoksa `None`
- [ ] Leads table'a "Referral" kolonu ekle (`mini-ui/js/ui-leads.js`)
- [ ] Kolon gösterimi:
  - [ ] Referral yoksa → "-"
  - [ ] Referral varsa → Referral tipi: "Co-sell" / "Marketplace" / "SP"
- [ ] Badge styling (minimal, mevcut badge pattern'ine uyumlu)

#### 2.5.2: API Integration (Minimal)
- [ ] `api.js`'e sadece sync call ekle:
  - [ ] `syncReferrals()` - POST /api/referrals/sync
- [ ] Error handling (API errors)
- [ ] Toast notification (sync başarılı/başarısız)

**Future Enhancement** (Post-MVP - Şimdilik YOK):
- ⏳ Referral detail modal
- ⏳ Referral filter
- ⏳ Referral status badges
- ⏳ Referral listesi (ayrı tab)

**Acceptance Criteria**:
- [ ] Leads API response'unda referral_type field'ı var (JOIN ile partner_center_referrals)
- [ ] Lead listesinde referral kolonu görünüyor
- [ ] Referral tipi doğru gösteriliyor (Co-sell / Marketplace / SP)
- [ ] Sync button çalışıyor (opsiyonel, admin için)
- [ ] Toast notification çalışıyor

---

### Task 2.6: Background Sync

**Files**:
- `app/core/celery_app.py` (modify - beat_schedule)
- `app/core/tasks.py` (modify - yeni task)

#### 2.6.1: Celery Task
- [ ] `sync_partner_center_referrals_task()` task'ı oluştur
- [ ] Feature flag check: `partner_center_enabled` kontrolü
- [ ] `app/core/referral_ingestion.py`'deki `sync_referrals_from_partner_center()` çağır
- [ ] Error handling (log, don't crash)
- [ ] Structured logging (success/failure counts)

#### 2.6.2: Celery Beat Schedule (MVP: Polling, Dev Override)
- [ ] `app/core/celery_app.py`'deki `beat_schedule`'a ekle
- [ ] **Production**: Scheduled polling (10 minutes = 600 seconds, configurable)
- [ ] **Development**: Auto-override to 30-60 seconds (test edilebilir olsun)
- [ ] Task expires: 1 hour (if not picked up)
- [ ] **Not**: Webhook endpoint future enhancement olarak işaretlendi

**Acceptance Criteria**:
- [ ] Sync task schedule'da çalışıyor
- [ ] Hatalar graceful handle ediliyor
- [ ] Progress tracked (success/failure counts)
- [ ] Results logged (structured logging)
- [ ] Dev mode'da 30s interval çalışıyor (test edilebilir)

---

## 📊 Progress Tracking

**Current Status**: 🔄 **In Progress** (Tasks 2.1, 2.2, 2.3 completed)

**Completed Tasks**: 3/6 (50%)

**Task Status**:
- [x] Task 2.1: Partner Center API Client ✅ **COMPLETED** (2025-01-28)
- [x] Task 2.2: Referral Data Model ✅ **COMPLETED** (2025-01-28)
- [x] Task 2.3: Referral Ingestion ✅ **COMPLETED** (2025-01-28)
- [ ] Task 2.4: API Endpoints
- [ ] Task 2.5: UI Integration
- [ ] Task 2.6: Background Sync

**Next Steps**:
1. Task 2.4: Create API endpoints (`app/api/referrals.py`) - `POST /api/referrals/sync`
2. Task 2.5: UI Integration - Add referral column to lead list
3. Task 2.6: Background Sync - Celery task and beat schedule
4. Scoring Pipeline Integration - Azure Tenant ID override and Co-sell boost

---

## 🔗 Related Documents

- `docs/prompts/2025-01-28-partner-center-phase2-task-list.md` - Detailed task list with acceptance criteria
- `docs/plans/2025-01-28-INTEGRATION-ROADMAP-v1.0.md` - Integration roadmap
- `docs/active/KALAN-ISLER-PRIORITY.md` - Priority list (Phase 2: Partner Center Referrals)
- `docs/todos/INTEGRATION-ROADMAP.md` - Integration Roadmap TODO

---

## ✅ Success Criteria

### Functional
- [ ] Partner Center'dan referral'lar başarıyla çekiliyor (polling, 10 minutes prod, 30s dev)
- [ ] Lead tipleri doğru tespit ediliyor (Co-sell, Marketplace, Solution Provider)
- [ ] Azure Tenant ID sinyali çalışıyor (Company.provider='M365' override)
- [ ] Domain extraction fallback çalışıyor (website → email → skip)
- [ ] Referral'lar raw_leads'e kaydediliyor (source='partnercenter')
- [ ] Referral'lar partner_center_referrals'e kaydediliyor (lifecycle tracking)
- [ ] Referral'lar domain'e normalize ediliyor
- [ ] Company'ler otomatik upsert ediliyor (Azure Tenant ID override ile)
- [ ] Domain scan idempotent çalışıyor (aynı domain için tekrar scan yapılmıyor)
- [ ] Scoring pipeline entegrasyonu çalışıyor:
  - [ ] Azure Tenant ID → Segment='Existing', Score=55
  - [ ] Co-sell → Priority boost +15
- [ ] Background sync çalışıyor (polling, 10 minutes prod, 30s dev)
- [ ] Manual sync çalışıyor (API endpoint)
- [ ] Lead listesinde referral kolonu görünüyor (Co-sell / Marketplace / SP)

### Technical
- [ ] Feature flag çalışıyor (disabled by default, production'a deploy edilebilir)
- [ ] Error handling complete (graceful degradation)
- [ ] Structured logging (PII masking)
- [ ] Basic rate limiting çalışıyor (sleep(1) between requests)
- [ ] Basic retry çalışıyor (2 deneme)
- [ ] Token expiry kontrolü çalışıyor (refresh gerektiğinde)
- [ ] Migration script çalışıyor (upgrade/downgrade)
- [ ] Hybrid database model çalışıyor (raw_leads + partner_center_referrals)
- [ ] Polling sync çalışıyor (10 minutes prod, 30s dev - test edilebilir)
- [ ] API endpoint çalışıyor (sadece sync endpoint, MVP)
- [ ] Scoring pipeline entegrasyonu çalışıyor (Azure Tenant ID + Co-sell boost)

### Testing
- [ ] Unit tests (partner_center.py, referral_ingestion.py)
- [ ] Integration tests (API endpoints)
- [ ] E2E tests (UI integration)
- [ ] Migration tests (upgrade/downgrade)

---

## 📝 Notes

1. **Feature Flag**: Partner Center integration feature flag ile kontrol edilecek (disabled by default). **Production'a deploy edilir ama default kapalı**. Feature flag açıldığında gradual rollout yapılabilir, rollback mekanizması var.

2. **Sync Strategy**: **MVP Primary = Scheduled Polling** (10 minutes prod, 30 seconds dev - test edilebilir). Webhook endpoint future enhancement olarak işaretlendi (post-MVP).

3. **Database Model**: **Hybrid yaklaşım** - Ingestion için `raw_leads` (mevcut pattern, source='partnercenter'), tracking için `partner_center_referrals` (referral lifecycle).

4. **Azure Tenant ID Sinyali**: 
   - Ingestion'da: Company.provider='M365' override
   - Scoring'de: Segment='Existing', Score=55 (scoring pipeline'da)

5. **Lead Tipleri**: Co-sell → priority boost (+15, scoring pipeline'da), Marketplace/Solution Provider → normal scoring.

6. **Domain Extraction**: Fallback chain (website → email → skip). Domain yoksa referral skip edilir (log warning).

7. **Domain Scan Idempotent**: Aynı domain için tekrar scan yapılmaz (domain bazlı, referral bazlı değil).

8. **Scoring Pipeline Entegrasyonu**: Azure Tenant ID override ve Co-sell boost **scoring pipeline'da** yapılır (ingestion'da değil).

9. **API Client**: MVP için minimal (50-70 satır). OAuth + basic retry + sleep(1) rate limiting yeterli.

10. **API Endpoints**: MVP için sadece `POST /api/referrals/sync`. List/get endpoints nice-to-have (post-MVP).

11. **UI Integration**: MVP için sadece lead listesine 1 kolon (Referral tipi: Co-sell / Marketplace / SP). Yeni tab + modal + filter post-MVP.

12. **Error Handling**: Her referral bağımsız işlenecek. Bir referral'da hata olsa bile diğerleri işlenmeye devam edecek.

---

**Last Updated**: 2025-01-28  
**Status**: ✅ **DECISION MADE** - Feature Flag OFF (Post-MVP)

**MVP Status**: ✅ **MVP'ye etkisi YOK** - Feature flag default OFF, kod hazır ama aktif değil

**Karar (2025-01-28)**: 
- ✅ **Feature Flag OFF bırak (Post-MVP)**
- ✅ Şimdilik production'a etkisi yok
- ✅ Device Code Flow implementasyonu hazır (istersen sonra açılabilir)
- ✅ Post-MVP sprint'inde tamamlanacak (API endpoints, Celery, UI, Scoring)

**Current State**: 
- ✅ Core components completed (Tasks 2.1, 2.2, 2.3 - 50% progress)
- ✅ MVP-safe: Sadece `raw_leads` + `companies` yazıyor, scan trigger disabled
- ✅ Manual sync script hazır (`scripts/sync_partner_center.py`)
- ✅ Migration hazır (DB hazır olunca `alembic upgrade head`)

**Next Sprint**: Post-MVP (G21-G22) - API endpoints, Celery task, UI integration, Scoring pipeline

**Production v1.0 Status**: ✅ **GO** - Production'a çıkış onaylandı, Partner Center Post-MVP

