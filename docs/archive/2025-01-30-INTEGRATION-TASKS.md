# Integration Tasks - Exact Task List

**Date**: 2025-01-28  
**Status**: 🔄 **In Progress** (Phase 1: ✅ Completed, Phase 2: Next)  
**Sequence**: Phase 1 → Phase 2 → Phase 3 (non-negotiable)

---

## 🎯 Phase 1: Mini UI Stabilization (P0.5)

**Branch**: `feature/ui-stabilization-v1.1`  
**Duration**: 1 day  
**Priority**: P0.5 (CRITICAL - blocks everything)

### Task 1.1: Button & Modal Fixes

**Files**: `mini-ui/js/ui-leads.js`, `mini-ui/styles.css`

- [x] Fix button hover states (scale transform + color change)
- [x] Fix modal backdrop click behavior (only close on overlay click)
- [x] Fix modal ESC key handling (keyboard event listener)
- [x] Fix modal scroll optimization (max-height: 80vh, overflow-y: auto)

**Acceptance Criteria**:
- All buttons have smooth hover effects
- Modal closes on backdrop click (not on modal content)
- ESC key closes modal
- Modal scrolls smoothly when content is long

---

### Task 1.2: Score Breakdown Improvements

**Files**: `mini-ui/js/ui-leads.js`, `mini-ui/styles.css`

- [x] Fix score breakdown modal bugs (if any)
- [x] Improve tooltip positioning (CSS-based tooltip system)
- [x] Fix signal/risk display order (SPF → DKIM → DMARC → Risks)
- [x] Add loading states for score breakdown (spinner while fetching)

**Acceptance Criteria**:
- Score breakdown modal works flawlessly
- Tooltips appear in correct position
- Signal/risk order is consistent
- Loading spinner shows while fetching score breakdown

---

### Task 1.3: Loading States

**Files**: `mini-ui/js/ui-leads.js`, `mini-ui/styles.css`, `mini-ui/index.html`

- [x] Add loading spinner for table (show while fetching leads)
- [x] Add loading states for filters (disable during fetch)
- [x] Add loading states for export buttons (disable during export)
- [x] Optimize loading transitions (smooth fade-in/out)

**Acceptance Criteria**:
- Table shows spinner while loading
- Filters disabled during fetch
- Export buttons show loading state
- Transitions are smooth

---

### Task 1.4: Filter Bar UX

**Files**: `mini-ui/js/ui-leads.js`, `mini-ui/styles.css`, `mini-ui/index.html`

- [x] Fix filter bar layout (responsive, proper spacing)
- [x] Improve filter dropdown UX (better styling, hover effects)
- [x] Add filter clear button (clear all filters at once)
- [x] Add filter state persistence (remember filters in localStorage)

**Acceptance Criteria**:
- Filter bar looks good on all screen sizes
- Dropdowns are easy to use
- Clear button works
- Filters persist across page reloads

---

### Task 1.5: General UX Polish

**Files**: `mini-ui/js/ui-leads.js`, `mini-ui/styles.css`, `mini-ui/index.html`

- [x] Fix table row hover effects (smooth highlight)
- [x] Improve pagination UX (better button styling, page info)
- [x] Fix empty state messages (clear CTA)
- [x] Add toast notification improvements (better positioning, auto-dismiss)

**Acceptance Criteria**:
- Table rows highlight smoothly on hover
- Pagination is intuitive
- Empty state is helpful
- Toast notifications are non-intrusive

---

## 🔄 Phase 2: Partner Center Referrals Integration (P1)

**Branch**: `feature/partner-center-referrals`  
**Duration**: 2-3 days  
**Priority**: P1

### Task 2.1: Partner Center API Client (MVP: Minimal)

**Files**: `app/core/partner_center.py` (NEW)

**MVP Yaklaşımı**: Hunter max 20-200 referral çekecek, full enterprise client gereksiz. **50-70 satır minimal client yeterli**.

- [ ] Create Partner Center API client class (minimal, 50-70 satır)
- [ ] Implement minimal OAuth 2.0 authentication (token al, expiry kontrolü)
- [ ] Implement `get_referrals()` function (GET referrals endpoint)
- [ ] Basic rate limiting: `time.sleep(1)` between requests (1 satır)
- [ ] Basic retry: 2 deneme (transient failures için)
- [ ] Token expiry kontrolü (refresh sadece gerektiğinde)
- [ ] Add error handling (network errors, API errors)
- [ ] Add logging (structured logging with PII masking)

**NOT**: Aşırı abstraction çıkarılmalı. Client class basit tutulmalı (150 satır yerine 50-70 satır).

**Acceptance Criteria**:
- Can authenticate with Partner Center
- Can fetch referrals successfully
- Basic rate limiting respected (sleep(1))
- Basic retry works (2 deneme)
- Token expiry kontrolü çalışıyor
- Errors handled gracefully

---

### Task 2.2: Referral Data Model (raw_leads + partner_center_referrals hybrid)

**Files**: `app/db/models.py`, `alembic/versions/XXXX_add_partner_center_referrals.py` (NEW)

**Hybrid Database Model**:

#### 2.2.1: raw_leads Ingestion (Mevcut Pattern)
- [ ] `raw_leads` table'ını kullan (mevcut pattern'e uyumlu)
- [ ] `source='partnercenter'` olarak kaydet
- [ ] `payload` JSONB field'ına full referral JSON'ı kaydet
- [ ] `domain` field'ına normalized domain kaydet
- [ ] `company_name`, `email`, `website` field'larını doldur

#### 2.2.2: partner_center_referrals Tracking (Referral Lifecycle)
- [ ] Create `PartnerCenterReferral` SQLAlchemy model
- [ ] Fields: `id`, `referral_id` (unique), `referral_type`, `company_name`, `domain`, `azure_tenant_id`, `status`, `raw_data`, `synced_at`, `created_at`, `updated_at`
- [ ] Create Alembic migration script
- [ ] Add indexes: `referral_id` (unique), `domain`, `status`, `synced_at`, `referral_type`, `azure_tenant_id`
- [ ] Test migration (upgrade/downgrade)

**Acceptance Criteria**:
- Hybrid model çalışıyor (raw_leads ingestion + partner_center_referrals tracking)
- raw_leads pattern'e uyumlu (source='partnercenter')
- Model created with all required fields (referral_type, azure_tenant_id dahil)
- Migration script works
- Indexes created
- Migration can be rolled back

---

### Task 2.3: Referral Ingestion

**Files**: `app/core/referral_ingestion.py` (NEW), `app/core/scorer.py` (modify)

- [ ] Create referral ingestion module
- [ ] Lead tipi detection (Co-sell, Marketplace, Solution Provider)
- [ ] Domain extraction fallback (website → email → skip)
- [ ] Azure Tenant ID → Company provider override (M365 signal)
- [ ] Implement referral → domain normalization (`normalize_domain()`)
- [ ] Implement referral → company upsert (`upsert_companies()`)
- [ ] Implement referral → domain scan trigger (idempotent - domain bazlı, referral bazlı değil)
- [ ] Scoring pipeline entegrasyonu:
  - [ ] `app/core/scorer.py`'ye Azure Tenant ID override ekle (Segment='Existing', Score=55)
  - [ ] `app/core/scorer.py`'ye Co-sell priority boost ekle (+15)
- [ ] Handle duplicate referrals (skip if already exists)
- [ ] Add logging (structured logging)

**Acceptance Criteria**:
- Lead tipi detection çalışıyor (Co-sell, Marketplace, Solution Provider)
- Domain extraction fallback çalışıyor (website → email → skip)
- Azure Tenant ID sinyali çalışıyor (Company.provider='M365' override)
- Referrals normalized correctly
- Companies upserted correctly
- Domain scans triggered automatically (idempotent - aynı domain için tekrar scan yapılmıyor)
- Scoring pipeline entegrasyonu çalışıyor (Azure Tenant ID + Co-sell boost)
- Duplicates handled gracefully

---

### Task 2.4: API Endpoints (MVP: Sadece Sync)

**Files**: `app/api/referrals.py` (NEW), `app/main.py`

**MVP Endpoint** (Sadece Bu):
- [ ] Create referrals router
- [ ] **MVP**: `POST /api/referrals/sync` - Manual sync from Partner Center
- [ ] Add response models (Pydantic: SyncReferralsRequest, SyncReferralsResponse)
- [ ] Add error handling (400 feature disabled, 500)
- [ ] Feature flag check: `partner_center_enabled` kontrolü
- [ ] Register router in `app/main.py`

**Future Enhancement** (Post-MVP - Şimdilik YOK):
- ⏳ `GET /api/referrals` - List referrals with filters (nice-to-have, MVP'de gerek yok)
- ⏳ `GET /api/referrals/{referral_id}` - Get single referral (nice-to-have, MVP'de gerek yok)
- ⏳ v1 API versioning (nice-to-have, MVP'de gerek yok)

**Acceptance Criteria**:
- MVP endpoint çalışıyor (`POST /api/referrals/sync`)
- Response models validated
- Error handling complete
- Feature flag kontrolü yapılıyor
- Endpoints registered in main app

---

### Task 2.5: UI Integration (MVP: Sadece Lead Listesine Kolon)

**Files**: `mini-ui/js/ui-leads.js`, `mini-ui/styles.css`, `app/api/leads.py` (modify)

**MVP Yaklaşımı**: Mini UI zaten lead listesi gösteriyor. Yeni tab + modal + filter = 2 gün iş, gereksiz. **Sadece lead listesine 1 kolon ekle**.

#### 2.5.1: Lead Listesine Referral Kolonu
- [ ] Leads API'ye referral bilgisi ekle (`app/api/leads.py`)
  - [ ] `LeadResponse` model'ine `referral_type: Optional[str]` field'ı ekle
  - [ ] SQL query'ye LEFT JOIN `partner_center_referrals` ekle (domain bazlı)
- [ ] Lead listesine "Referral" kolonu ekle (`mini-ui/js/ui-leads.js`)
- [ ] Kolon gösterimi: Referral yoksa "-", varsa Referral tipi (Co-sell / Marketplace / SP)
- [ ] Badge styling (minimal, mevcut badge pattern'ine uyumlu)

#### 2.5.2: API Integration (Minimal)
- [ ] `api.js`'e sadece sync call ekle: `syncReferrals()` - POST /api/referrals/sync
- [ ] Error handling (API errors)
- [ ] Toast notification (sync başarılı/başarısız)

**Future Enhancement** (Post-MVP - Şimdilik YOK):
- ⏳ Referrals section to Mini UI (new tab or section)
- ⏳ Referral status badges (Active, In Progress, Won)
- ⏳ Referral filter to leads table (filter by referral status)
- ⏳ Referral sync status indicator (last sync time)

**Acceptance Criteria**:
- Leads API response'unda referral_type field'ı var (JOIN ile partner_center_referrals)
- Lead listesinde referral kolonu görünüyor
- Referral tipi doğru gösteriliyor (Co-sell / Marketplace / SP)
- Sync button çalışıyor (opsiyonel, admin için)
- Toast notification çalışıyor

---

### Task 2.6: Background Sync (MVP: Polling, Dev Override)

**Files**: `app/core/celery_app.py`, `app/core/tasks.py`

- [ ] Create Celery task `sync_partner_center_referrals()`
- [ ] Feature flag check: `partner_center_enabled` kontrolü
- [ ] Configure sync schedule: **Production 10 minutes (600s), Development 30-60 seconds** (test edilebilir)
- [ ] Dev mode override: Auto-override to 30-60 seconds if `environment == "development"`
- [ ] Handle sync errors gracefully (log, don't crash)
- [ ] Add sync progress tracking (success/failure counts)
- [ ] Add sync result logging (structured logging)

**Acceptance Criteria**:
- Sync task runs on schedule (10 min prod, 30s dev)
- Dev mode override çalışıyor (test edilebilir)
- Errors handled gracefully
- Progress tracked (success/failure counts)
- Results logged (structured logging)

---

## ⚡ Phase 3: Dynamics 365 Integration (P2)

**Branch**: `feature/dynamics365-integration`  
**Duration**: 6-10 days  
**Priority**: P2

### Task 3.1: Dynamics 365 API Client

**Files**: `app/core/dynamics365.py` (NEW)

- [ ] Create Dynamics 365 API client class
- [ ] Implement OAuth 2.0 authentication (Azure AD)
- [ ] Implement token refresh mechanism (automatic renewal)
- [ ] Implement rate limiting handling (respect Dynamics limits)
- [ ] Implement batch request API (efficient bulk operations)
- [ ] Add error handling (network, API, authentication errors)
- [ ] Add logging (structured logging)

**Acceptance Criteria**:
- Can authenticate with Dynamics 365
- Token refresh works automatically
- Rate limiting respected
- Batch requests work
- Errors handled gracefully

---

### Task 3.2: Data Mapping

**Files**: `app/core/dynamics_mapping.py` (NEW)

- [ ] Create data mapping module
- [ ] Map Hunter lead → Dynamics Lead (field mapping)
- [ ] Map Hunter score → Dynamics Opportunity Stage (score thresholds)
- [ ] Map Hunter segment → Dynamics Lead Source (segment mapping)
- [ ] Map IP enrichment → Dynamics Custom Fields (infrastructure data)
- [ ] Handle missing fields gracefully (default values)
- [ ] Add mapping validation (required fields check)

**Acceptance Criteria**:
- All Hunter fields mapped to Dynamics
- Score → Stage mapping accurate
- Segment → Source mapping correct
- IP enrichment data included
- Validation works

---

### Task 3.3: Pipeline Integration

**Files**: `app/core/dynamics_pipeline.py` (NEW)

- [ ] Create pipeline integration module
- [ ] Implement Lead → Contact → Account → Opportunity flow
- [ ] Implement duplicate detection (check existing records)
- [ ] Implement account merge logic (merge if exists)
- [ ] Implement opportunity creation (from Hunter lead)
- [ ] Handle pipeline errors (rollback on failure)
- [ ] Add transaction logging (audit trail)

**Acceptance Criteria**:
- Pipeline flow works end-to-end
- Duplicates detected and handled
- Account merge works correctly
- Opportunities created successfully
- Errors handled with rollback

---

### Task 3.4: Sync Mechanisms

**Files**: `app/core/dynamics_sync.py` (NEW), `app/db/models.py`

- [ ] Create sync module
- [ ] Implement Hunter → Dynamics sync (push leads to Dynamics)
- [ ] Implement Dynamics → Hunter sync (pull updates from Dynamics) - optional
- [ ] Implement conflict resolution (last-write-wins or manual)
- [ ] Implement audit logging (sync history table)
- [ ] Add sync status tracking (synced, failed, pending)
- [ ] Create sync tracking models (DynamicsSyncLog)

**Acceptance Criteria**:
- Push sync works
- Pull sync works (if implemented)
- Conflicts resolved correctly
- Audit log complete
- Status tracking accurate

---

### Task 3.5: API Endpoints

**Files**: `app/api/dynamics.py` (NEW), `app/main.py`

- [ ] Create Dynamics router
- [ ] `POST /dynamics/sync/{domain}` - Manual sync to Dynamics
- [ ] `GET /dynamics/status/{domain}` - Check sync status
- [ ] `POST /dynamics/bulk-sync` - Bulk sync to Dynamics
- [ ] Add response models (Pydantic)
- [ ] Add error handling (404, 400, 500)
- [ ] Register router in `app/main.py`

**Acceptance Criteria**:
- All endpoints work correctly
- Response models validated
- Error handling complete
- Endpoints registered in main app

---

### Task 3.6: UI Integration

**Files**: `mini-ui/js/ui-leads.js`, `mini-ui/index.html`, `mini-ui/styles.css`

- [ ] Add Dynamics sync button to Mini UI (per lead)
- [ ] Add Dynamics status indicator (synced, failed, pending)
- [ ] Add Dynamics sync history (last sync time, status)
- [ ] Add Dynamics error handling UI (show errors to user)
- [ ] Add bulk sync button (sync all leads)
- [ ] Style Dynamics UI elements

**Acceptance Criteria**:
- Sync button works
- Status indicator accurate
- Sync history visible
- Errors shown to user
- Bulk sync works

---

### Task 3.7: Background Sync

**Files**: `app/core/celery_app.py`, `app/core/tasks.py`

- [ ] Create Celery task `sync_to_dynamics365()`
- [ ] Configure sync schedule (daily/hourly via Celery Beat)
- [ ] Handle sync errors and retries (exponential backoff)
- [ ] Implement exponential backoff (retry with increasing delay)
- [ ] Add sync progress tracking (Redis-based)
- [ ] Add sync result logging (success/failure counts)

**Acceptance Criteria**:
- Sync task runs on schedule
- Errors retried with backoff
- Progress tracked
- Results logged

---

## 📝 Branch Strategy

### Phase 1 Branch
```bash
git checkout -b feature/ui-stabilization-v1.1
# Work on UI fixes
git commit -m "feat: UI stabilization - button fixes, modal improvements"
git push origin feature/ui-stabilization-v1.1
# Create PR → merge to main
```

### Phase 2 Branch
```bash
git checkout -b feature/partner-center-referrals
# Work on Partner Center integration
git commit -m "feat: Partner Center referrals integration"
git push origin feature/partner-center-referrals
# Create PR → merge to main
```

### Phase 3 Branch
```bash
git checkout -b feature/dynamics365-integration
# Work on Dynamics 365 integration
git commit -m "feat: Dynamics 365 integration - pipeline and sync"
git push origin feature/dynamics365-integration
# Create PR → merge to main
```

---

## ✅ Success Criteria Summary

### Phase 1 (UI)
- [ ] Zero UI bugs
- [ ] Sales team feedback: Positive
- [ ] UI 100% functional

### Phase 2 (Partner Center)
- [ ] Referrals syncing successfully
- [ ] Sync success rate > 95%
- [ ] Referrals visible in UI

### Phase 3 (Dynamics)
- [ ] Dynamics sync success rate > 90%
- [ ] Pipeline accuracy > 95%
- [ ] Error recovery automatic

---

## 🔗 Related Documents

- `docs/plans/2025-01-28-INTEGRATION-ROADMAP-v1.0.md` - Detailed roadmap
- `docs/active/KALAN-ISLER-PRIORITY.md` - Priority list
- `docs/active/NO-BREAK-REFACTOR-PLAN.md` - G21 Architecture Refactor (overlaps with Phase 3)

