# D365 Phase 2.9 — E2E Wiring Runbook

**Status:** ⏳ **PENDING** (Roast Sprint completed, ready for tenant setup)  
**Created:** 2025-01-30  
**Goal:** Hunter → D365 bağlantısını production-ready hale getirmek

---

## 📋 Overview

Bu runbook, D365 Phase 2.9 (E2E wiring) için adım adım uygulama rehberidir. Roast Sprint'teki 5 kritik fix tamamlandıktan sonra, gerçek D365 tenant'a bağlanma sürecini kapsar.

**Prerequisites:**
- ✅ Roast Sprint completed (5/5 tasks)
- ✅ Backend & UI adapter implemented (Phase 2.5 + Phase 3)
- ✅ All tests passing
- ✅ Code review completed

---

## 🎯 Phase 2.9 Scope

**Goal:** Azure AD + D365 tarafını Hunter'ın bağlanabileceği hale getirmek ve 3 core senaryoyu manuel test etmek.

**Deliverables:**
1. Azure AD App Registration + D365 Application User
2. Hunter config & feature flag (DEV)
3. Manual E2E tests (3 core senaryo)
4. Error & rate limit senaryoları (opsiyonel)
5. Go/No-Go gate (Dev → Prod)

---

## 📝 A. Tenant & App Registration (Day 0)

**Goal:** Azure AD + D365 tarafını Hunter'ın bağlanabileceği hale getirmek.

**Effort:** 1-2 saat (ops)

### A.1. Azure AD App Registration

1. **Azure Portal → Azure Active Directory → App registrations**
   - Click "New registration"
   - Name: `Hunter-D365-Integration` (veya uygun isim)
   - Supported account types: "Single tenant" (veya multi-tenant, ihtiyaca göre)
   - Redirect URI: Leave empty (client credentials flow)
   - Click "Register"

2. **API Permissions**
   - Go to "API permissions"
   - Click "Add a permission"
   - Select "Dynamics CRM"
   - Select "Delegated permissions"
   - Check: `user_impersonation`
   - Click "Add permissions"
   - **Important:** Click "Grant admin consent" (if required)

3. **Client Secret**
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Description: `Hunter-D365-Integration-Secret`
   - Expires: 24 months (veya uygun süre)
   - Click "Add"
   - **⚠️ CRITICAL:** Copy the secret value immediately (only shown once)
   - Store in KeyVault (production) or secure location

4. **Collect Required Values**
   - **CLIENT_ID:** Application (client) ID (from Overview page)
   - **TENANT_ID:** Directory (tenant) ID (from Overview page)
   - **CLIENT_SECRET:** Secret value (from step 3)

### A.2. D365 Application User

1. **D365 → Settings → Security → Users**
   - Click "Application Users"
   - Click "New"
   - User type: "Application User"
   - Application ID: Paste `CLIENT_ID` from Azure AD
   - Full name: `Hunter Integration User` (veya uygun isim)
   - Primary email: (optional, can be dummy)
   - Click "Save"

2. **Security Roles**
   - Click "Manage Security Roles"
   - Select appropriate roles:
     - **Lead:** Read, Write (required)
     - **Account:** Read (optional, for future mapping)
     - **Contact:** Read (optional, for future mapping)
     - **Custom Role:** "Hunter Integration" (if created)
   - Click "OK"

### A.3. D365 Custom Fields (Optional, Future Enhancement)

If you want to store Hunter-specific data in D365:

1. **D365 → Settings → Customization → Customize the System**
2. **Lead Entity → Fields**
   - Add custom fields:
     - `hunter_score` (Whole Number)
     - `hunter_segment` (Single Line of Text)
     - `hunter_priority` (Whole Number)
     - `hunter_domain` (Single Line of Text)
   - Save and publish

**Note:** Custom fields are optional for Phase 2.9. Basic lead creation works without them.

### A.4. Output Checklist

- [ ] `CLIENT_ID` collected
- [ ] `TENANT_ID` collected
- [ ] `CLIENT_SECRET` stored securely
- [ ] Application User created in D365
- [ ] Security roles assigned (Lead Read/Write minimum)
- [ ] D365 base URL collected (e.g., `https://yourorg.crm.dynamics.com`)

---

## 📝 B. Hunter Config & Feature Flag (Dev) — (XS–S)

**Goal:** Hunter → D365 bağlantısını sadece **DEV tenant + DEV Hunter** üstünde açmak.

**Effort:** 15-30 dakika

### B.1. Environment Variables

Add to `.env` (DEV environment):

```bash
# D365 Integration (DEV)
HUNTER_D365_ENABLED=true
HUNTER_D365_BASE_URL=https://yourorg.crm.dynamics.com
HUNTER_D365_CLIENT_ID=<CLIENT_ID>
HUNTER_D365_CLIENT_SECRET=<CLIENT_SECRET>
HUNTER_D365_TENANT_ID=<TENANT_ID>
HUNTER_D365_API_VERSION=v9.2
```

**Security Note:**
- **DEV:** `.env` file is acceptable (local development)
- **PROD:** Use KeyVault or secure secret management (never commit secrets)

### B.2. Container Restart

```bash
# Restart API and worker containers
docker-compose restart api worker

# Or if using Kubernetes
kubectl rollout restart deployment/api deployment/worker
```

### B.3. Smoke Tests

1. **Health Check:**
   ```bash
   curl http://localhost:8000/healthz/live
   curl http://localhost:8000/healthz/ready
   ```

2. **D365 Token Acquisition Test:**
   - Check logs for `d365_token_acquired` event
   - Or create a small test endpoint (optional):
     ```python
     @router.get("/test/d365-token")
     async def test_d365_token():
         from app.integrations.d365.client import D365Client
         client = D365Client()
         token = client._get_access_token()
         return {"status": "ok", "token_length": len(token)}
     ```

### B.4. Output Checklist

- [ ] Environment variables added to `.env`
- [ ] Containers restarted
- [ ] Health checks passing
- [ ] D365 token acquisition working (check logs)

---

## 📝 C. Manual E2E Tests (Core 3 Senaryo) — (S)

**Goal:** 3 core senaryoyu manuel test etmek ve D365 → Hunter sync'in çalıştığını doğrulamak.

**Effort:** 1-2 saat

### C.1. Senaryo 1 — Happy Path: Create

**Test:** Hunter UI'den D365'e hiç gitmemiş bir lead'i push etmek.

**Steps:**

1. **Hunter UI'de lead seç:**
   - `d365_sync_status = not_synced` olan bir lead bul
   - Lead detail modal'ı aç
   - "Push to Dynamics" butonuna bas

2. **Celery task çalışır:**
   - Check Celery logs: `push_lead_to_d365` task started
   - Check D365 logs: New lead created

3. **Hunter DB kontrolü:**
   ```sql
   SELECT d365_lead_id, d365_sync_status, d365_sync_last_at
   FROM companies
   WHERE domain = '<test_domain>';
   ```
   - Expected: `d365_lead_id` dolu (GUID format)
   - Expected: `d365_sync_status = 'synced'`
   - Expected: `d365_sync_last_at` set (timestamp)

4. **D365 UI kontrolü:**
   - D365 → Sales → Leads
   - Search for the lead (by email or company name)
   - Verify lead exists with correct data

5. **Hunter UI kontrolü:**
   - Lead listesinde badge → `Synced` görünmeli
   - Lead detail modal'da D365 link → doğru URL açıyor
   - D365 link format: `https://yourorg.crm.dynamics.com/main.aspx?etc=1&id=<lead_id>`

**Acceptance Criteria:**
- ✅ Lead D365'te oluşturuldu
- ✅ Hunter DB'de `d365_lead_id` set
- ✅ `d365_sync_status = synced`
- ✅ UI badge ve link çalışıyor

---

### C.2. Senaryo 2 — Update / Idempotent

**Test:** Aynı lead'i tekrar push etmek (duplicate prevention).

**Steps:**

1. **Hunter tarafında lead'i değiştir:**
   - Senaryo 1'deki lead'i kullan
   - Company name veya segment'i ufak değiştir (test için)
   - "Push to Dynamics" butonuna tekrar bas

2. **Idempotency check:**
   - Check Celery logs: `d365_lead_already_exists` event
   - Check task response: `{"status": "skipped", "reason": "already_exists"}`

3. **D365 kontrolü:**
   - D365'te **duplicate lead yok** (tek lead olmalı)
   - Existing lead'in ID'si aynı kalmalı

4. **Hunter DB kontrolü:**
   - `d365_lead_id` değişmemeli
   - `d365_sync_status = synced` kalmalı

**Acceptance Criteria:**
- ✅ Duplicate lead üretilmedi
- ✅ Task skip edildi (`already_exists`)
- ✅ D365'te tek lead var
- ✅ Hunter DB'de ID değişmedi

---

### C.3. Senaryo 3 — "DB var, D365 yok" Edge Case

**Test:** DB'de `d365_lead_id` var ama D365'te lead yok (orphaned ID).

**Steps:**

1. **Test DB'de sahte ID yaz:**
   ```sql
   UPDATE companies
   SET d365_lead_id = '00000000-0000-0000-0000-000000000000',
       d365_sync_status = 'synced'
   WHERE domain = '<test_domain>';
   ```

2. **Task'ı tetikle:**
   - Hunter UI'den "Push to Dynamics" butonuna bas
   - Veya API endpoint: `POST /api/v1/d365/push-lead`

3. **Verification fail log:**
   - Check Celery logs: `d365_lead_verification_failed` veya `d365_lead_lookup_error`
   - Expected: `_find_lead_by_id` → 404 → verification fail

4. **Task normal push path:**
   - Task verification fail sonrası normal create path'e girer
   - Yeni lead D365'te oluşturulur
   - Yeni `d365_lead_id` Hunter DB'ye yazılır

5. **Hunter DB kontrolü:**
   - `d365_lead_id` yeni GUID ile güncellenmiş olmalı
   - `d365_sync_status = synced`

**Acceptance Criteria:**
- ✅ Verification fail log'u görüldü
- ✅ Task normal push path'e girdi
- ✅ Yeni lead D365'te oluşturuldu
- ✅ Hunter DB'de yeni ID set edildi

---

## 📝 D. Error & Rate Limit Senaryoları — (S, Opsiyonel)

**Goal:** Error handling ve rate limit davranışını doğrulamak.

**Effort:** 30-60 dakika (opsiyonel)

### D.1. Authentication Error

**Test:** Yanlış Client ID/Secret ile token acquisition.

**Steps:**

1. **Yanlış secret:**
   ```bash
   HUNTER_D365_CLIENT_SECRET=wrong_secret
   ```

2. **Task'ı tetikle:**
   - Push lead attempt

3. **Expected behavior:**
   - `D365AuthenticationError` raised
   - Task fails with meaningful error
   - UI'de anlamlı hata mesajı
   - Log: `d365_token_acquisition_failed`

**Acceptance Criteria:**
- ✅ Authentication error handled gracefully
- ✅ UI'de anlamlı hata mesajı
- ✅ Log'da error event

---

### D.2. Rate Limit (429)

**Test:** D365 endpoint'ini bilinçli 429'a zorlamak (opsiyonel, zor test).

**Steps:**

1. **Rate limit simülasyonu:**
   - Multiple concurrent push requests
   - Or D365 API throttling (if possible)

2. **Expected behavior:**
   - `D365RateLimitError` raised
   - Retry backoff + jitter çalışıyor
   - Task retry with exponential backoff
   - Log: `d365_rate_limit_retry`

3. **Retry verification:**
   - Check Celery logs: Retry countdown values
   - Expected: Exponential backoff (60s, 120s, 240s, capped at 3600s)
   - Expected: Jitter added (0-10s random)

**Acceptance Criteria:**
- ✅ Rate limit error handled
- ✅ Retry backoff exponential + capped
- ✅ Jitter added (prevents thundering herd)
- ✅ Task eventually succeeds or fails gracefully

---

### D.3. D365 API Error (500/503)

**Test:** D365 API'den 500/503 error (opsiyonel, zor test).

**Steps:**

1. **API error simülasyonu:**
   - D365 maintenance window (if possible)
   - Or network issue

2. **Expected behavior:**
   - `D365APIError` raised
   - Task retry with backoff
   - After max retries: `d365_sync_status = error`
   - `d365_sync_error` field populated

3. **Error state verification:**
   - Check Hunter DB: `d365_sync_status = error`
   - Check `d365_sync_error` field (error message)

**Acceptance Criteria:**
- ✅ API error handled gracefully
- ✅ Task retries with backoff
- ✅ Error state persisted in DB
- ✅ UI'de error badge görünüyor

---

## 📝 E. Go/No-Go Gate (Dev → Prod) — (XS)

**Goal:** Dev E2E tamamlandıktan sonra production'a geçiş kararı vermek.

**Effort:** 15-30 dakika (review)

### E.1. Go/No-Go Checklist

**Core Functionality:**
- [ ] Senaryo 1 (Happy Path) ✅ PASSED
- [ ] Senaryo 2 (Idempotency) ✅ PASSED
- [ ] Senaryo 3 (Edge Case) ✅ PASSED

**Error Handling:**
- [ ] Authentication error handled ✅
- [ ] Rate limit retry working ✅
- [ ] API error handling working ✅

**Data Integrity:**
- [ ] Duplicate lead üretilmiyor ✅
- [ ] DB sync status correct ✅
- [ ] D365 lead data correct ✅

**Performance:**
- [ ] Token cache working (Redis) ✅
- [ ] Retry backoff reasonable ✅
- [ ] No connection pool exhaustion ✅

**UI/UX:**
- [ ] Status badge correct ✅
- [ ] D365 link working ✅
- [ ] Error messages user-friendly ✅

### E.2. Production Deployment Steps

If all checklist items pass:

1. **Production Config:**
   - Add environment variables to production KeyVault
   - Set `HUNTER_D365_ENABLED=true` (production)
   - Use production D365 tenant URL

2. **Production App Registration:**
   - Create separate App Registration for production (or reuse)
   - Create Application User in production D365
   - Assign security roles

3. **Deploy:**
   - Deploy code to production
   - Restart containers
   - Smoke test (health checks)

4. **Production E2E Test:**
   - Run Senaryo 1 (Happy Path) with production data
   - Monitor logs and metrics
   - Verify no duplicate leads

### E.3. Decision Log

**Date:** [TBD]  
**Decision:** [GO / NO-GO]  
**Reason:** [Brief explanation]  
**Approved by:** [Name]

---

## 📊 Test Results Template

```markdown
## Test Results - [Date]

### Senaryo 1: Happy Path
- Status: ✅ PASSED / ❌ FAILED
- Notes: [Any issues or observations]

### Senaryo 2: Idempotency
- Status: ✅ PASSED / ❌ FAILED
- Notes: [Any issues or observations]

### Senaryo 3: Edge Case
- Status: ✅ PASSED / ❌ FAILED
- Notes: [Any issues or observations]

### Error Handling Tests
- Authentication Error: ✅ / ❌
- Rate Limit: ✅ / ❌
- API Error: ✅ / ❌

### Go/No-Go Decision
- Decision: GO / NO-GO
- Blockers: [List any blockers]
```

---

## 🔗 Related Documentation

- `PRE-D365-ROAST-SPRINT-TASK-BOARD.md` - Pre-D365 hotfix sprint
- `CORE-FREEZE-D365-PUSH-PLAN.md` - Architecture plan
- `D365-PHASE-3-UI-STATUS-TODO.md` - UI implementation details
- `HUNTER-STATE-v1.0.md` - System status
- `G21-ROADMAP-CURRENT.md` - Integration roadmap

---

## 📝 Notes

- **Created:** 2025-01-30
- **Status:** Pending (waiting for tenant setup)
- **Next:** Execute runbook when D365 tenant is ready

