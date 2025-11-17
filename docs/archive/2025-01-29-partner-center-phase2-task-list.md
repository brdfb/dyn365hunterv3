# Partner Center Phase 2 - Detaylı Task List

**Tarih**: 2025-01-28  
**Durum**: 🔄 **NEXT** (Phase 1 tamamlandı)  
**Priority**: P1  
**Süre**: 2-3 gün  
**Branch**: `feature/partner-center-referrals`

---

## 🎯 Genel Bakış

Partner Center'dan referral'ları çekip Hunter'a entegre etmek. Referral'lar otomatik olarak domain'e normalize edilecek, company olarak upsert edilecek ve domain scan tetiklenecek.

**Akış**: Partner Center API → Referral Ingestion → Domain Normalization → Company Upsert → Domain Scan Trigger

---

## 📋 Task Listesi

### Task 2.1: Partner Center API Client (MVP: Minimal)

**Dosya**: `app/core/partner_center.py` (YENİ)

**MVP Yaklaşımı**: Hunter max 20-200 referral çekecek, full enterprise client gereksiz. **50-70 satır minimal client yeterli**.

**Görevler**:
- [ ] **MSAL (Microsoft Authentication Library) + Device Code Flow** ile OAuth 2.0 authentication
  - **ÖNEMLİ**: Partner Center Referrals API sadece delegated permissions destekliyor, application permissions yok
  - **ÖNEMLİ**: ROPC flow MFA ile uyumsuz, bu yüzden MSAL + Device Code Flow kullanılmalı
  - Setup script: Device code flow ile bir kere login (MFA dahil tüm adımlar)
  - Refresh token'ı güvenli sakla (encrypted DB veya key vault)
  - Background job: MSAL `acquire_token_silent()` ile sessiz token alma
- [ ] Token cache yönetimi (refresh token storage, token refresh logic)
- [ ] `get_referrals()` fonksiyonu (GET referrals endpoint)
- [ ] Basic rate limiting: `time.sleep(1)` between requests (1 satır)
- [ ] Basic retry: 2 deneme (transient failures için)
- [ ] Token expiry kontrolü (MSAL otomatik handle eder)
- [ ] Error handling (network errors, API errors, token refresh errors)
- [ ] Structured logging (PII masking ile)

**NOT**: Aşırı abstraction çıkarılmalı. Client class basit tutulmalı (150 satır yerine 50-70 satır).

**Config Eklenecekler** (`app/config.py`):
```python
# Partner Center (Feature flag: disabled by default)
partner_center_enabled: bool = False
partner_center_api_url: Optional[str] = None  # Partner Center API base URL
partner_center_client_id: Optional[str] = None  # OAuth client ID
partner_center_client_secret: Optional[str] = None  # OAuth client secret
partner_center_tenant_id: Optional[str] = None  # Azure AD tenant ID (OAuth için)
# MSAL + Device Code Flow için (delegated permissions - application permissions yok):
partner_center_authority: str = "https://login.microsoftonline.com/{tenant_id}"  # MSAL authority
partner_center_scope: str = "https://api.partner.microsoft.com/.default"  # MSAL scope
partner_center_token_cache_path: Optional[str] = None  # Token cache file path (optional, defaults to .token_cache)
```

**Environment Variables** (`.env.example`):
```bash
# Partner Center Integration (Feature flag: disabled by default)
# NOTE: Partner Center Referrals API only supports delegated permissions (user_impersonation)
# Application permissions (Referrals.Read/ReadWrite) do NOT exist for this API
# We use MSAL + Device Code Flow (MFA compatible, Microsoft recommended approach)
# HUNTER_PARTNER_CENTER_ENABLED=false
# HUNTER_PARTNER_CENTER_CLIENT_ID=your-client-id
# HUNTER_PARTNER_CENTER_CLIENT_SECRET=your-client-secret
# HUNTER_PARTNER_CENTER_TENANT_ID=your-tenant-id
# HUNTER_PARTNER_CENTER_BASE_URL=https://api.partnercenter.microsoft.com
# MSAL + Device Code Flow (delegated permissions - application permissions not available):
# HUNTER_PARTNER_CENTER_SCOPE=https://api.partner.microsoft.com/.default
# HUNTER_PARTNER_CENTER_TOKEN_CACHE_PATH=.token_cache  # Optional, defaults to .token_cache
# Setup: Run setup script once to authenticate (device code flow with MFA)
# Background jobs will use silent token acquisition (no MFA required after initial setup)
```

**Acceptance Criteria**:
- Partner Center'a authenticate olabiliyor
- Referral'ları başarıyla çekebiliyor
- Rate limiting'e uyuyor
- Token refresh otomatik çalışıyor
- Hatalar graceful handle ediliyor
- Logging structured ve PII maskelenmiş

**Referans Pattern**: `app/core/analyzer_enrichment.py` - Feature flag pattern'i (enrichment_enabled gibi)

---

### Task 2.2: Referral Data Model (raw_leads + partner_center_referrals hybrid)

**Dosyalar**: 
- `app/db/models.py` (modify)
- `alembic/versions/XXXX_add_partner_center_referrals.py` (YENİ)

**Hybrid Database Model**:

#### 2.2.1: raw_leads Ingestion (Mevcut Pattern)
- [ ] `raw_leads` table'ını kullan (mevcut pattern'e uyumlu)
- [ ] `source='partnercenter'` olarak kaydet
- [ ] `payload` JSONB field'ına full referral JSON'ı kaydet
- [ ] `domain` field'ına normalized domain kaydet
- [ ] `company_name`, `email`, `website` field'larını doldur

**Referans**: `app/db/models.py` - `RawLead` model (source='csv', 'domain', 'webhook' pattern'i)

#### 2.2.2: partner_center_referrals Tracking (Referral Lifecycle)
**Model** (`app/db/models.py`):
```python
class PartnerCenterReferral(Base):
    """Partner Center referral lifecycle tracking."""
    
    __tablename__ = "partner_center_referrals"
    
    id = Column(Integer, primary_key=True, index=True)
    referral_id = Column(String(255), nullable=False, unique=True, index=True)  # Partner Center referral ID (UNIQUE)
    referral_type = Column(String(50), nullable=True, index=True)  # 'co-sell', 'marketplace', 'solution-provider'
    company_name = Column(String(255), nullable=True)  # Company name from referral
    domain = Column(String(255), nullable=True, index=True)  # Normalized domain
    azure_tenant_id = Column(String(255), nullable=True, index=True)  # Azure Tenant ID (M365 signal)
    status = Column(String(50), nullable=False, index=True)  # 'Active', 'In Progress', 'Won', 'Lost', etc.
    raw_data = Column(JSONB, nullable=True)  # Full referral data from Partner Center (for debugging)
    synced_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True)  # Last sync time
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_partner_center_referrals_domain", "domain"),  # For querying by domain
        Index("idx_partner_center_referrals_status", "status"),  # For filtering by status
        Index("idx_partner_center_referrals_synced_at", "synced_at"),  # For sync tracking
        Index("idx_partner_center_referrals_type", "referral_type"),  # For filtering by type
        Index("idx_partner_center_referrals_tenant_id", "azure_tenant_id"),  # For M365 signal queries
    )
```

**Migration** (`alembic/versions/XXXX_add_partner_center_referrals.py`):
- [ ] Alembic migration script oluştur
- [ ] `partner_center_referrals` table'ı oluştur
- [ ] Index'leri ekle (referral_id unique, domain, status, synced_at)
- [ ] Migration'ı test et (upgrade/downgrade)

**Referans Pattern**: `alembic/versions/e7196f7e556b_add_ip_enrichment_table.py` - Migration pattern'i

**Acceptance Criteria**:
- Hybrid model çalışıyor (raw_leads ingestion + partner_center_referrals tracking)
- raw_leads pattern'e uyumlu (source='partnercenter')
- partner_center_referrals model tüm required field'ları içeriyor (referral_type, azure_tenant_id dahil)
- Migration script çalışıyor
- Index'ler oluşturulmuş
- Migration rollback edilebiliyor

---

### Task 2.3: Referral Ingestion

**Dosya**: `app/core/referral_ingestion.py` (YENİ)

**Görevler**:

#### 2.3.1: Lead Tipi Detection
- [ ] `detect_referral_type()` - Referral tipini tespit et
  - Co-sell → `'co-sell'` (priority boost için)
  - Marketplace → `'marketplace'`
  - Solution Provider → `'solution-provider'`
- [ ] Lead tipini `partner_center_referrals.referral_type` field'ına kaydet

#### 2.3.2: Domain Extraction Fallback
- [ ] `extract_domain_from_referral()` - Referral'dan domain çıkar (fallback chain)
  - **1. Try website**: `referral.website` → `extract_domain_from_website()` → `normalize_domain()`
  - **2. Try email**: `referral.contact.email` → `extract_domain_from_email()` → `normalize_domain()`
  - **3. Skip**: Domain yoksa → referral'ı skip et (log warning)
- [ ] `app/core/normalizer.py`'deki `normalize_domain()` kullan

#### 2.3.3: Azure Tenant ID → Company Override (Ingestion Only)
- [ ] `apply_azure_tenant_signal()` - Azure Tenant ID sinyalini company'ye uygula
  - **Eğer `azureTenantId` varsa**:
    - `Company.provider = 'M365'` (override provider detection)
    - `Company` model'ine `azure_tenant_id` field'ı ekle (optional, tracking için)
  - **Eğer `azureTenantId` yoksa**:
    - Provider detection normal akışta
- [ ] **NOT**: Segment override scoring pipeline'da yapılacak (Task 2.3.7'de değil, scorer.py'de)

#### 2.3.4: raw_leads Ingestion (Mevcut Pattern)
- [ ] `ingest_to_raw_leads()` - Referral'ı `raw_leads` table'ına kaydet
  - `source='partnercenter'`
  - `payload` → Full referral JSON (JSONB)
  - `domain` → Normalized domain
  - `company_name`, `email`, `website` → Referral'dan al
- [ ] Mevcut `RawLead` model'ini kullan (mevcut pattern'e uyumlu)

#### 2.3.5: partner_center_referrals Tracking
- [ ] `upsert_referral_tracking()` - Referral lifecycle tracking
  - `referral_id` unique olduğu için duplicate check yap
  - `referral_type`, `azure_tenant_id`, `status` kaydet
  - Varsa update et, yoksa insert et

#### 2.3.6: Company Upsert & Domain Scan (Idempotent)
- [ ] `upsert_company_from_referral()` - Referral'dan company oluştur/update et
  - Domain normalize edilmiş olmalı
  - Azure Tenant ID varsa → `provider='M365'` override
  - `app/db/models.py`'deki `Company` model'ini kullan
  - Domain unique olduğu için duplicate check yap
- [ ] `trigger_domain_scan()` - Domain scan tetikle (**IDEMPOTENT**)
  - **Kritik**: Aynı domain için tekrar scan yapılmamalı
  - `domain_signals` table'ında domain var mı kontrol et
  - Eğer domain zaten scan edilmişse → skip (log info)
  - Eğer domain scan edilmemişse → `scan_single_domain()` çağır
  - **NOT**: Referral bazlı değil, domain bazlı scan (aynı şirkete 3 referral gelirse 1 scan yeterli)

#### 2.3.7: Ana Sync Fonksiyonu
- [ ] `sync_referrals_from_partner_center()` - Ana sync fonksiyonu
  - Partner Center'dan referral'ları çek
  - Her referral için:
    1. Lead tipi detection
    2. Domain extraction (fallback chain)
    3. Domain yoksa → skip (log warning)
    4. raw_leads ingestion
    5. partner_center_referrals tracking
    6. Azure Tenant ID sinyali → company provider override (segment değil)
    7. Company upsert
    8. Domain scan trigger (idempotent - domain bazlı)
  - Duplicate referral'ları skip et
  - Her referral bağımsız işlenir (bir hata diğerlerini etkilemez)

**NOT**: 
- Segment override ve priority boost **scoring pipeline'da** yapılacak (ingestion'da değil)
- Scoring pipeline entegrasyonu Task 2.3.8'de

#### 2.3.8: Scoring Pipeline Entegrasyonu (Kritik)
- [ ] `app/core/scorer.py`'ye Azure Tenant ID override ekle
  - `determine_segment()` fonksiyonuna `azure_tenant_id` parametresi ekle
  - Eğer `azure_tenant_id` varsa:
    - `segment = 'Existing'` (Migration değil, existing customer)
    - `reason = 'M365 existing customer (Azure Tenant ID)'`
    - Score override: 55 (M365 existing baseline, configurable)
- [ ] `app/core/scorer.py`'ye Co-sell priority boost ekle
  - `score_domain()` fonksiyonuna `referral_type` parametresi ekle
  - Eğer `referral_type == 'co-sell'`:
    - `score += settings.partner_center_cosell_bonus` (default: 15)
- [ ] Config'e ekle (`app/config.py`):
  ```python
  partner_center_cosell_bonus: int = 15  # Co-sell referral priority boost
  partner_center_azure_tenant_score: int = 55  # M365 existing customer baseline score
  ```

#### 2.3.9: Logging & Error Handling
- [ ] Structured logging ekle
- [ ] Error handling (her referral bağımsız, bir hata diğerlerini etkilemez)

**Referans Pattern**: 
- `app/core/normalizer.py` - Domain normalization
- `app/core/tasks.py` - Domain scan trigger
- `app/core/enrichment_service.py` - Service layer pattern (DB session management)

**Acceptance Criteria**:
- Lead tipi detection çalışıyor (Co-sell, Marketplace, Solution Provider)
- Domain extraction fallback çalışıyor (website → email → skip)
- Azure Tenant ID sinyali çalışıyor (Company.provider='M365' override)
- raw_leads ingestion çalışıyor (mevcut pattern'e uyumlu)
- partner_center_referrals tracking çalışıyor (referral lifecycle)
- Referral'lar doğru normalize ediliyor
- Company'ler doğru upsert ediliyor (Azure Tenant ID override ile)
- Domain scan idempotent çalışıyor (aynı domain için tekrar scan yapılmıyor)
- Scoring pipeline entegrasyonu çalışıyor (Azure Tenant ID → Segment='Existing', Co-sell → priority boost)
- Duplicate'ler graceful handle ediliyor
- Her referral bağımsız işleniyor (bir hata diğerlerini etkilemez)
- Domain yoksa referral skip ediliyor (log warning)

---

### Task 2.4: API Endpoints (MVP: Sadece Sync)

**Dosyalar**:
- `app/api/referrals.py` (YENİ - Basit endpoint)
- `app/main.py` (modify - router register)

**MVP Endpoint** (Sadece Bu):

#### 2.4.1: `POST /api/referrals/sync` - Manual Sync (MVP Primary)
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

**Pydantic Models** (`app/api/referrals.py`):
```python
class ReferralResponse(BaseModel):
    id: int
    referral_id: str
    referral_type: Optional[str]  # 'co-sell', 'marketplace', 'solution-provider'
    company_name: Optional[str]
    domain: Optional[str]
    azure_tenant_id: Optional[str]  # M365 signal
    status: str
    synced_at: datetime
    created_at: datetime
    updated_at: datetime

class SyncReferralsRequest(BaseModel):
    force: bool = False  # Force re-sync even if already synced

class SyncReferralsResponse(BaseModel):
    status: str  # 'success', 'failed', 'partial'
    total: int
    succeeded: int
    failed: int
    errors: List[str] = []
```

**Router Registration** (`app/main.py`):
```python
from app.api import referrals

# Direct router (MVP için v1 versioning gerek yok):
app.include_router(referrals.router)  # Already has /referrals prefix
```

**Referans Pattern**: 
- `app/api/ingest.py` - `/ingest/webhook` pattern'i (basit endpoint referansı)

**Acceptance Criteria**:
- MVP endpoint çalışıyor (`POST /api/referrals/sync`)
- Response model validate ediliyor
- Error handling complete
- Endpoint main app'e register edilmiş
- Feature flag kontrolü yapılıyor
- Polling sync çalışıyor (10 minutes interval)

---

### Task 2.5: UI Integration (MVP: Sadece Lead Listesine Kolon)

**Dosyalar**:
- `mini-ui/js/ui-leads.js` (modify)
- `mini-ui/styles.css` (modify - minimal)
- `mini-ui/js/api.js` (modify - sadece sync call)

**MVP Yaklaşımı**: Mini UI zaten lead listesi gösteriyor. Yeni tab + modal + filter = 2 gün iş, gereksiz. **Sadece lead listesine 1 kolon ekle**.

**Görevler**:

#### 2.5.1: Lead Listesine Referral Kolonu
- [ ] Leads API'ye referral bilgisi ekle (`app/api/leads.py`)
  - `LeadResponse` model'ine `referral_type: Optional[str]` field'ı ekle
  - SQL query'ye LEFT JOIN `partner_center_referrals` ekle (domain bazlı)
  - Referral varsa `referral_type` doldur, yoksa `None`
- [ ] Leads table'a "Referral" kolonu ekle (`mini-ui/js/ui-leads.js`)
- [ ] Kolon gösterimi:
  - Referral yoksa → "-"
  - Referral varsa → Referral tipi: "Co-sell" / "Marketplace" / "SP"
- [ ] Badge styling (minimal, mevcut badge pattern'ine uyumlu)

#### 2.5.2: API Integration (Minimal)
- [ ] `api.js`'e sadece sync call ekle:
  - `syncReferrals()` - POST /api/referrals/sync
- [ ] Error handling (API errors)
- [ ] Toast notification (sync başarılı/başarısız)

**Future Enhancement** (Post-MVP - Şimdilik YOK):
- ⏳ Referral detail modal
- ⏳ Referral filter
- ⏳ Referral status badges
- ⏳ Referral listesi (ayrı tab)

**Referans Pattern**:
- `mini-ui/js/ui-leads.js` - Table rendering pattern'i (mevcut kolon ekleme pattern'i)
- `mini-ui/styles.css` - Badge styling pattern'i (segment-badge, provider-badge gibi)

**Acceptance Criteria**:
- Leads API response'unda referral_type field'ı var (JOIN ile partner_center_referrals)
- Lead listesinde referral kolonu görünüyor
- Referral tipi doğru gösteriliyor (Co-sell / Marketplace / SP)
- Sync button çalışıyor (opsiyonel, admin için)
- Toast notification çalışıyor

---

### Task 2.6: Background Sync

**Dosyalar**:
- `app/core/celery_app.py` (modify - beat_schedule)
- `app/core/tasks.py` (modify - yeni task)

**Görevler**:

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

**Celery Beat Schedule** (`app/core/celery_app.py`):
```python
# Development mode override (test edilebilir olsun)
sync_interval = 30 if settings.environment == "development" else settings.partner_center_sync_interval

beat_schedule={
    # ... existing schedules ...
    "sync-partner-center-referrals": {
        "task": "app.core.tasks.sync_partner_center_referrals_task",
        "schedule": float(sync_interval),  # Dev: 30s, Prod: 600s (10 minutes)
        "options": {"expires": 3600},  # Task expires after 1 hour if not picked up
    },
}
```

**Config Eklenecekler** (`app/config.py`):
```python
partner_center_sync_interval: int = 600  # Production: 10 minutes (600 seconds) - configurable
# Development mode: Auto-override to 30-60 seconds (celery_app.py'de)
```

**Referans Pattern**:
- `app/core/tasks.py` - `daily_rescan_task()` - Celery task pattern'i
- `app/core/celery_app.py` - Beat schedule pattern'i

**Acceptance Criteria**:
- Sync task schedule'da çalışıyor
- Hatalar graceful handle ediliyor
- Progress tracked (success/failure counts)
- Results logged (structured logging)

---

## 🔧 Feature Flag Yapısı

**Pattern**: IP Enrichment feature flag pattern'ini takip et (`enrichment_enabled`)

**Config** (`app/config.py`):
```python
# Partner Center (Feature flag: disabled by default)
partner_center_enabled: bool = False
partner_center_api_url: Optional[str] = None
partner_center_client_id: Optional[str] = None
partner_center_client_secret: Optional[str] = None
partner_center_tenant_id: Optional[str] = None
# ROPC Flow için (delegated permissions - application permissions yok):
partner_center_username: Optional[str] = None  # Service user username
partner_center_password: Optional[str] = None  # Service user password
partner_center_resource: str = "https://api.partner.microsoft.com"  # ROPC resource
partner_center_sync_interval: int = 600  # Production: 10 minutes (600 seconds) - configurable
partner_center_cosell_bonus: int = 15  # Co-sell referral priority boost (scoring'de kullanılır)
partner_center_azure_tenant_score: int = 55  # M365 existing customer baseline score (scoring'de kullanılır)
```

**Environment Variables** (`.env.example`):
```bash
# Partner Center Integration (Feature flag: disabled by default)
# NOTE: Partner Center Referrals API only supports delegated permissions (user_impersonation)
# Application permissions (Referrals.Read/ReadWrite) do NOT exist for this API
# We use ROPC (Resource Owner Password Credentials) flow with a service user
# HUNTER_PARTNER_CENTER_ENABLED=false
# HUNTER_PARTNER_CENTER_CLIENT_ID=your-client-id
# HUNTER_PARTNER_CENTER_CLIENT_SECRET=your-client-secret
# HUNTER_PARTNER_CENTER_TENANT_ID=your-tenant-id
# HUNTER_PARTNER_CENTER_BASE_URL=https://api.partnercenter.microsoft.com
# HUNTER_PARTNER_CENTER_SYNC_INTERVAL=600  # MVP: 10 minutes (600 seconds) - configurable
# ROPC Flow (delegated permissions - application permissions not available):
# HUNTER_PARTNER_CENTER_USERNAME=referrals-sync@seninfirma.com
# HUNTER_PARTNER_CENTER_PASSWORD=service-user-password
# HUNTER_PARTNER_CENTER_RESOURCE=https://api.partner.microsoft.com
```

**Feature Flag Check Pattern**:
- API endpoint'lerde: `if not settings.partner_center_enabled: raise HTTPException(400, "Partner Center integration is disabled")`
- Celery task'larda: `if not settings.partner_center_enabled: return {"status": "skipped", "reason": "feature_disabled"}`
- UI'da: Feature flag kontrolü yap, disabled ise UI element'lerini gizle

**Important**: 
- **Production'a deploy edilir ama default kapalı** (`partner_center_enabled=false`)
- Feature flag açıldığında gradual rollout yapılabilir
- Rollback mekanizması: Feature flag kapatılabilir

**Referans**: `app/config.py` - `enrichment_enabled` pattern'i

---

## 📁 Dosya Yapısı

### Yeni Dosyalar
```
app/core/partner_center.py          # Partner Center API client (MVP: 50-70 satır, minimal)
app/core/referral_ingestion.py      # Referral ingestion logic (lead tipi, Azure Tenant ID, domain extraction)
app/api/referrals.py                 # Referrals endpoint (MVP: sadece sync endpoint)
alembic/versions/XXXX_add_partner_center_referrals.py  # Database migration (partner_center_referrals table)
```

**Not**: 
- `raw_leads` table'ı zaten var, sadece `source='partnercenter'` kullanılacak (yeni migration gerekmez)
- v1 API versioning MVP'de yok (nice-to-have, post-MVP)

### Değiştirilecek Dosyalar
```
app/config.py                        # Feature flag ve config ekle (cosell_bonus, azure_tenant_score)
app/db/models.py                     # PartnerCenterReferral model ekle
app/core/scorer.py                    # Azure Tenant ID override + Co-sell boost (scoring pipeline)
app/api/leads.py                      # LeadResponse'a referral_type field ekle, SQL query'ye JOIN ekle
app/main.py                          # referrals router register et
app/core/celery_app.py                # Beat schedule ekle (dev override ile)
app/core/tasks.py                     # Sync task ekle
mini-ui/js/ui-leads.js                # UI integration (sadece referral kolonu)
mini-ui/js/api.js                     # API calls (sadece sync)
mini-ui/styles.css                    # Styling (minimal, badge için)
.env.example                          # Environment variables
```

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
  - Azure Tenant ID → Segment='Existing', Score=55
  - Co-sell → Priority boost +15
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

## 🔗 İlgili Dokümantasyon

- `docs/plans/2025-01-28-INTEGRATION-ROADMAP-v1.0.md` - Integration roadmap
- `docs/plans/2025-01-28-INTEGRATION-TASKS.md` - Integration tasks
- `docs/active/KALAN-ISLER-PRIORITY.md` - Priority list
- `docs/archive/2025-01-28-IP-ENRICHMENT-IMPLEMENTATION.md` - Feature flag pattern reference

---

## 📝 Notlar

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

## 🚀 Implementation Order

1. **Task 2.1**: Partner Center API Client (foundation)
2. **Task 2.2**: Referral Data Model (database)
3. **Task 2.3**: Referral Ingestion (business logic)
4. **Task 2.4**: API Endpoints (API layer)
5. **Task 2.5**: UI Integration (frontend)
6. **Task 2.6**: Background Sync (automation)

**Dependency Chain**: 2.1 → 2.2 → 2.3 → 2.4 → 2.5 → 2.6

---

**Son Güncelleme**: 2025-01-28  
**Revize**: 2025-01-28 (MVP-focused, hybrid DB model, Azure Tenant ID signal, lead types, polling strategy)  
**Final Revize**: 2025-01-28 (Minimal API client, scoring pipeline entegrasyonu, domain scan idempotent, minimal UI, dev sync override)

