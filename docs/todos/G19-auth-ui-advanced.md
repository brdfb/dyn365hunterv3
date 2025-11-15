# TODO: Sprint 6 (G19) - Auth + UI + Advanced Features

**Date Created**: 2025-11-14  
**Status**: 🚧 In Progress (Backend: ~70% complete)  
**Phase**: G19 (Post-MVP Sprint 6)  
**Süre**: 2-3 hafta  
**Last Updated**: 2025-01-28

---

## 🎯 Sprint Hedefi

**Düzeltilmiş Scope (Critique Sonrası):**

P0: Microsoft SSO + Temel UI upgrade (sorting, pagination, search)  
P1: Dashboard KPI + Score breakdown  
P2: Optional (PDF preview, Charts - zaman kalırsa)

**❌ Çıkarılanlar:**
- AI Features → G20'ye taşındı (detaylı plan ile)
- Contact Finder → G21'ye taşındı (legal review ile)

**Strateji**: Auth + temel UI upgrade. AI ve Contact Finder ayrı sprint'lerde.

---

## 📋 Tasks

### Microsoft SSO Authentication (P0)

- [x] Microsoft Identity Platform entegrasyonu
  - [x] Azure AD app registration (documentation ready)
  - [x] OAuth 2.0 flow setup
  - [x] Token validation
  - [x] User management (users tablosu)
  - [x] **State/nonce storage (Redis)** - Security hardening
  - [x] **Token revocation table** - Security hardening
  - [x] **Refresh token encryption (Fernet)** - Security hardening

- [x] Session management
  - [x] Token storage
  - [x] Token refresh
  - [x] Session timeout

- [x] Auth endpoints
  - [x] `GET /auth/login` - Login redirect
  - [x] `GET /auth/callback` - OAuth callback
  - [x] `POST /auth/logout` - Logout
  - [x] `GET /auth/me` - Current user
  - [x] `POST /auth/refresh` - Refresh token

- [x] Favorites migration
  - [x] Migration script (session-based → user-based)
  - [x] First login migration logic

### UI / Dashboard Upgrade

#### P0 - Lead Table Upgrade
- [x] Backend endpoints
  - [x] `GET /leads?sort_by={field}&sort_order={asc|desc}` - Sorting
  - [x] `GET /leads?page={n}&page_size={n}` - Pagination
  - [x] `GET /leads?search={query}` - Full-text search
- [x] Frontend implementation
  - [x] Sorting UI (table headers clickable)
  - [x] Pagination UI (page numbers, prev/next)
  - [x] Search input + debounce

#### P1 - Dashboard & Score Breakdown
- [x] Score breakdown
  - [x] Backend: `GET /leads/{domain}/score-breakdown` - Score breakdown endpoint
  - [ ] Frontend: Tooltip/modal with score breakdown
- [x] Dashboard KPI
  - [x] Backend: `GET /dashboard/kpis` - KPI data contract
  - [ ] Frontend: KPI cards (total leads, migration leads, high priority)

#### P2 - Optional (Zaman Kalırsa)
- [ ] PDF preview
  - [ ] In-browser PDF viewer (PDF.js)
  - [ ] PDF download button
- [ ] Charts
  - [ ] Backend: `GET /dashboard/charts` - Chart data contract
  - [ ] Frontend: Segment distribution chart (Chart.js)
- [ ] Recent activity
  - [ ] Backend: `GET /dashboard/activity` - Activity data contract
  - [ ] Frontend: Recent activity feed

### ❌ AI Features (G20'ye Taşındı)

**Not:** AI features detaylı plan ile G20'ye taşındı.

### ❌ Contact Finder (G21'ye Taşındı)

**Not:** Contact Finder legal review + risk analizi ile G21'ye taşındı.

### API Endpoints

- [x] Auth endpoints (5 endpoint: login, callback, logout, me, refresh)
- [x] UI upgrade endpoints (sorting, pagination, search)
- [x] Dashboard endpoints (KPI, score-breakdown)
- [ ] ❌ AI endpoints (G20'ye taşındı)
- [ ] ❌ Contact Finder endpoints (G21'ye taşındı)

### Testing (P0 - Zorunlu)

- [x] Unit tests (≥15 test cases) - ✅ 22 test cases completed
  - [x] Auth tests (OAuth flow, token generation, user management)
  - [ ] UI upgrade tests (sorting, pagination, search) - ⏳ Pending
  - [x] Dashboard tests (KPI, score-breakdown) - Backend ready
  - [x] Migration tests (favorites migration) - Logic implemented

- [ ] Integration tests
  - [ ] Auth end-to-end test (login → callback → me)
  - [ ] UI upgrade end-to-end test (sorting, pagination, search) - ⏳ Pending
  - [ ] Protected routes test (auth required endpoints)

### Documentation

- [ ] API documentation
  - [ ] Auth endpoints docs (OpenAPI/Swagger)
  - [ ] UI upgrade docs (sorting, pagination, search) - ⏳ Pending
  - [ ] Dashboard endpoints docs (KPI, score-breakdown data contracts)

- [x] Setup guide
  - [x] Azure AD setup guide (`docs/active/G19-AZURE-AD-SETUP.md`)
  - [ ] Screenshot'lar (Azure Portal) - Optional
  - [x] Troubleshooting guide - Included in setup guide

- [ ] README.md güncellemesi
  - [ ] Microsoft SSO setup
  - [ ] UI upgrade features - ⏳ Pending

- [ ] CHANGELOG.md güncellemesi
  - [ ] G19: Auth + UI upgrade added

---

## ✅ Acceptance Criteria

### P0 - Zorunlu
- [x] Microsoft SSO çalışıyor (login, callback, logout, me, refresh) - ✅ Backend ready
- [x] Security hardening tamamlandı (state storage, token revocation, encryption) - ✅ Implemented
- [x] Favorites migration çalışıyor (session-based → user-based) - ✅ Migration script + logic ready
- [x] UI upgrade tamamlandı (sorting, pagination, search) - ✅ Frontend completed
- [x] Tests passing (≥15 test cases) - ✅ 22 test cases passing

### P1 - İdeal
- [x] Dashboard KPI çalışıyor - ✅ Backend endpoint ready
- [x] Score breakdown çalışıyor (endpoint + modal) - ✅ Backend endpoint ready, frontend pending

### P2 - Optional (Zaman Kalırsa)
- [ ] PDF preview çalışıyor
- [ ] Charts çalışıyor

---

## 📝 Notes

### Çıkarılanlar (Critique Sonrası)

- ❌ **AI Features** → G20'ye taşındı (detaylı plan ile)
- ❌ **Contact Finder** → G21'ye taşındı (legal review + risk analizi ile)
- ✅ **Kapsam daraltıldı** - Gerçekçi 2-3 hafta scope'a indirildi

### Security Hardening (Critique Sonrası Eklendi)

- ✅ State/nonce storage (Redis)
- ✅ Token revocation table
- ✅ Refresh token encryption (Fernet)
- ✅ Setup guide (Azure AD)

### Bağımlılıklar

- ✅ Sprint 4 tamamlandı (favorites için auth gerekli)
- ✅ Sprint 5 tamamlandı (alerts için UI gerekli)

### Risk Mitigation

- **Microsoft SSO**: Azure AD app registration gerekli (production için)
- **AI Features**: OpenAI API key gerekli (cost consideration)
- **Contact Finder**: Legal/ethical considerations (web scraping)

---

**Son Güncelleme**: 2025-11-14  
**Sprint Başlangıç**: TBD  
**Sprint Bitiş**: TBD

