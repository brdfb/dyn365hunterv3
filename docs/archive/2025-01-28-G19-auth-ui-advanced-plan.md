# G19 - Auth + UI + Advanced Features - Detaylı Teknik Plan

> ⚠️ **DEPRECATED** (2025-01-28): SSO authentication has been removed. Hunter now uses Internal Access Mode (network-level authentication). See CHANGELOG.md for details.

**Tarih**: 2025-01-28  
**Durum**: ✅ **Tamamlandı (P0/P1)** - SSO REMOVED (2025-01-28) - P2 optional features backlog'a taşındı  
**Sprint**: G19 (Post-MVP Sprint 6)  
**Süre**: 2-3 hafta  
**Tamamlanma**: 2025-11-15 (SSO removed: 2025-01-28)

---

## 🎯 Sprint Hedefi

Advanced features - Auth, UI upgrade, AI features (optional).

**Strateji**: Artık ürün şekillendi → kozmetik + güvenlik + AI sprint'i.

---

## 📊 Mevcut Durum Analizi

### Authentication
- ✅ API Key auth var (`app/core/api_key_auth.py`) - Webhook için
- ❌ Microsoft SSO yok
- ❌ Users tablosu yok
- ❌ Session management yok (sadece session-based favorites var)

### UI/Dashboard
- ✅ Mini UI var (`mini-ui/`) - Basit HTML/JS/CSS
- ✅ Filters var (segment, min_score, provider)
- ❌ Sorting yok
- ❌ Pagination yok
- ❌ Search yok
- ❌ PDF preview yok
- ❌ Dashboard upgrade yok (KPI cards, charts)

### Database
- ✅ Favorites tablosu var (user_id VARCHAR(255) - session-based)
- ✅ Notes/Tags var (domain-based, user_id yok)
- ❌ Users tablosu yok

---

## 🏗️ Teknik Mimari

### 1. Microsoft SSO Authentication

#### Azure AD App Registration
- **Endpoint**: `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize`
- **Token Endpoint**: `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token`
- **Required Scopes**: `openid`, `profile`, `email`, `User.Read`

#### OAuth 2.0 Flow
1. User clicks "Login with Microsoft" → `GET /auth/login`
2. Redirect to Azure AD authorization endpoint
3. User authenticates → Azure AD redirects to `GET /auth/callback?code=...`
4. Exchange code for tokens (access_token, id_token, refresh_token)
5. Validate tokens (JWT validation)
6. Create/update user in database
7. Create session (JWT or session cookie)
8. Redirect to frontend

#### Token Storage Strategy
- **Access Token**: Short-lived (1 hour), stored in session/JWT
- **Refresh Token**: Long-lived (90 days), stored in database (encrypted)
- **ID Token**: Used for user info, not stored

#### Session Management
- **Option 1**: JWT tokens (stateless)
  - Access token in Authorization header
  - Refresh token in HTTP-only cookie
- **Option 2**: Server-side sessions (stateful)
  - Session ID in cookie
  - Session data in Redis/DB

**Öneri**: JWT tokens (stateless, scalable)

---

### 2. Database Schema Changes

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    microsoft_id VARCHAR(255) UNIQUE NOT NULL,  -- Azure AD object ID
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    refresh_token_encrypted TEXT,  -- Encrypted refresh token
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_microsoft_id ON users(microsoft_id);
CREATE INDEX idx_users_email ON users(email);
```

#### Favorites Migration
- **Current**: `user_id VARCHAR(255)` (session-based)
- **New**: `user_id INTEGER` (foreign key to users.id)
- **Migration**: Map session-based favorites to user-based favorites on first login

#### Notes/Tags Migration (Optional)
- **Current**: Domain-based (no user_id)
- **New**: Add `user_id INTEGER` (optional, nullable for backward compatibility)
- **Migration**: Keep existing notes/tags as "shared" (user_id = NULL)

---

### 3. UI/Dashboard Upgrade

#### Lead Table Upgrade
- **Filters**: Segment, min_score, provider, tags (✅ var, geliştirilecek)
- **Sorting**: Priority, score, domain, updated_at
- **Pagination**: Server-side pagination (page, page_size)
- **Search**: Full-text search (domain, company_name)

#### Priority Order Display
- **Priority Badge**: Visual indicator (1-6 scale, color-coded)
- **Priority Sorting**: Default sort by priority (descending)

#### PDF Preview
- **In-browser Viewer**: PDF.js or native browser viewer
- **Download Button**: Direct download link

#### Score Explanation
- **Tooltip/Modal**: Score breakdown (base_score, provider_points, signal_points, risk_points)
- **Score Factors**: Visual breakdown of scoring components

#### Bulk Upload UI
- **File Drag-Drop**: HTML5 drag-and-drop API
- **Upload Progress**: Real-time progress bar (using `/jobs/{job_id}` endpoint)
- **Error Display**: Per-domain error messages

#### Sales Panel (Dashboard Upgrade)
- **KPI Cards**: Total leads, migration leads, high priority leads
- **Charts**: Segment distribution (pie chart), score distribution (histogram)
- **Recent Activity**: Last 10 scans, last 10 favorites, last 10 notes

---

### 4. AI Features (Optional)

#### AI Recommendation Engine
- **Model**: OpenAI GPT-4 or local model (Ollama)
- **Recommendations**:
  - Migration readiness (based on score, signals, provider)
  - Risk assessment (SPF/DKIM/DMARC issues)
  - Next steps (actionable recommendations)

#### AI Endpoints
- `POST /leads/{domain}/recommendations` - Get AI recommendations
- `GET /leads/{domain}/summary` - AI-enhanced summary

#### Cost Considerations
- **OpenAI API**: ~$0.01-0.03 per request (GPT-4)
- **Local Model**: Free but slower (Ollama)
- **Caching**: Cache recommendations (24 hours)

---

### 5. Contact Finder (Optional)

#### Web Scraping
- **Legal Considerations**: Robots.txt, rate limiting, terms of service
- **Contact Page Scraping**: Extract email patterns from contact pages
- **Email Pattern Extraction**: Regex patterns for email addresses

#### Pattern Generation
- `firstname.lastname@domain.com`
- `f.lastname@domain.com`
- `firstname@domain.com`

#### SMTP-check Integration
- **Email Validation**: Syntax + MX check (existing)
- **SMTP Verification**: Verify email exists (existing `email_validator.py`)

#### Rate Limiting
- **Web Scraping**: 1 request per second per domain
- **SMTP Check**: 5 requests per second per domain

---

## 📋 Implementation Plan

### Phase 1: Microsoft SSO (Week 1)

#### Day 1-2: Azure AD Setup
- [x] Azure AD app registration (documentation ready)
- [x] Environment variables (`HUNTER_AZURE_CLIENT_ID`, `HUNTER_AZURE_CLIENT_SECRET`, `HUNTER_AZURE_TENANT_ID`)
- [x] Redirect URI configuration

#### Day 3-4: OAuth 2.0 Flow
- [x] `app/core/auth.py` - OAuth 2.0 client
- [x] `app/api/auth.py` - Auth endpoints
  - [x] `GET /auth/login` - Login redirect
  - [x] `GET /auth/callback` - OAuth callback
  - [x] `POST /auth/logout` - Logout
  - [x] `GET /auth/me` - Current user
  - [x] `POST /auth/refresh` - Refresh token
- [x] JWT token generation/validation
- [x] Token refresh logic
- [x] Security hardening (state/nonce storage, token revocation, refresh token encryption)

#### Day 5: Database Migration
- [x] Users table migration (`app/db/migrations/g19_users_auth.sql`)
- [x] Favorites migration (session-based → user-based)
- [x] Update `app/db/models.py` (User model)

#### Day 6-7: Testing
- [x] Unit tests (auth flow) - 22 tests
- [x] Integration tests (end-to-end OAuth flow)
- [x] Manual testing (Azure AD login)

---

### Phase 2: UI/Dashboard Upgrade (Week 2)

#### Day 1-2: Lead Table Upgrade
- [x] Backend: Sorting endpoint (`GET /leads?sort_by=priority&sort_order=desc`)
- [x] Backend: Pagination (`GET /leads?page=1&page_size=50`)
- [x] Backend: Search (`GET /leads?search=example.com`)
- [x] Frontend: Table sorting UI
- [x] Frontend: Pagination UI
- [x] Frontend: Search input

#### Day 3: Priority & Score Display
- [x] Frontend: Priority badge component (UI Patch v1.1'de eklendi)
- [x] Frontend: Score explanation tooltip/modal (UI Patch v1.1'de eklendi)
- [x] Backend: Score breakdown endpoint (`GET /leads/{domain}/score-breakdown`)

#### Day 4: PDF Preview
- [ ] Frontend: PDF.js integration
- [ ] Frontend: PDF download button
- [ ] Backend: PDF endpoint already exists (`GET /leads/{domain}/summary.pdf`)

#### Day 5: Bulk Upload UI
- [ ] Frontend: Drag-and-drop component
- [ ] Frontend: Upload progress bar
- [ ] Frontend: Error display
- [ ] Backend: Progress tracking already exists (`GET /jobs/{job_id}`)

#### Day 6-7: Sales Panel (Dashboard)
- [x] Backend: KPI endpoint (`GET /dashboard/kpis`)
- [ ] Backend: Charts data endpoint (`GET /dashboard/charts`) - **P2: Backlog**
- [ ] Backend: Recent activity endpoint (`GET /dashboard/activity`) - **P2: Backlog**
- [x] Frontend: KPI cards component
- [ ] Frontend: Charts component (Chart.js or similar) - **P2: Backlog**
- [ ] Frontend: Recent activity component - **P2: Backlog**

---

### Phase 3: AI Features (Optional, Week 3)

#### Day 1-2: AI Integration
- [ ] OpenAI API client (`app/core/ai_client.py`)
- [ ] Recommendation prompt engineering
- [ ] Caching strategy (Redis)

#### Day 3-4: AI Endpoints
- [ ] `POST /leads/{domain}/recommendations` - Get AI recommendations
- [ ] `GET /leads/{domain}/summary` - AI-enhanced summary
- [ ] Error handling (API failures, rate limits)

#### Day 5-7: Testing & Optimization
- [ ] Unit tests (AI client)
- [ ] Integration tests (AI endpoints)
- [ ] Cost optimization (caching, batch requests)
- [ ] Performance testing

---

### Phase 4: Contact Finder (Optional, Week 3)

#### Day 1-2: Web Scraping
- [ ] Legal compliance check (robots.txt, terms of service)
- [ ] Contact page scraper (`app/core/contact_finder.py`)
- [ ] Email pattern extraction
- [ ] Rate limiting

#### Day 3-4: Pattern Generation & Validation
- [ ] Pattern generator (firstname.lastname, f.lastname, etc.)
- [ ] SMTP-check integration (existing `email_validator.py`)
- [ ] Contact finder endpoint (`POST /leads/{domain}/find-contacts`)

#### Day 5-7: Testing
- [ ] Unit tests (scraper, pattern generator)
- [ ] Integration tests (contact finder endpoint)
- [ ] Legal compliance verification

---

## 🔧 Teknik Detaylar

### Dependencies

#### New Python Packages
```txt
# Microsoft SSO
msal>=1.24.0  # Microsoft Authentication Library
python-jose[cryptography]>=3.3.0  # JWT token handling
passlib[bcrypt]>=1.7.4  # Password hashing (if needed)

# AI Features (Optional)
openai>=1.0.0  # OpenAI API client
# or
ollama>=0.1.0  # Local model client

# Contact Finder (Optional)
beautifulsoup4>=4.12.0  # Web scraping
requests>=2.31.0  # HTTP client
```

#### Frontend Libraries (Optional)
```html
<!-- PDF.js for PDF preview -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>

<!-- Chart.js for dashboard charts -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

---

### Environment Variables

```bash
# Microsoft SSO
HUNTER_AZURE_CLIENT_ID=your-client-id
HUNTER_AZURE_CLIENT_SECRET=your-client-secret
HUNTER_AZURE_TENANT_ID=your-tenant-id
HUNTER_AZURE_REDIRECT_URI=http://localhost:8000/auth/callback

# JWT
HUNTER_JWT_SECRET_KEY=your-secret-key
HUNTER_JWT_ALGORITHM=HS256
HUNTER_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
HUNTER_JWT_REFRESH_TOKEN_EXPIRE_DAYS=90

# AI Features (Optional)
HUNTER_OPENAI_API_KEY=your-openai-api-key
HUNTER_OPENAI_MODEL=gpt-4-turbo-preview
# or
HUNTER_OLLAMA_BASE_URL=http://localhost:11434
HUNTER_OLLAMA_MODEL=llama2

# Contact Finder (Optional)
HUNTER_CONTACT_FINDER_ENABLED=true
HUNTER_CONTACT_FINDER_RATE_LIMIT=1  # requests per second
```

---

### API Endpoints

#### Auth Endpoints
- `GET /auth/login` - Redirect to Microsoft login
- `GET /auth/callback` - OAuth callback handler
- `POST /auth/logout` - Logout (invalidate session)
- `GET /auth/me` - Get current user info
- `POST /auth/refresh` - Refresh access token

#### UI Upgrade Endpoints
- `GET /leads?sort_by={field}&sort_order={asc|desc}&page={n}&page_size={n}&search={query}` - Enhanced leads endpoint
- `GET /leads/{domain}/score-breakdown` - Score breakdown
- `GET /dashboard/kpis` - KPI cards data
- `GET /dashboard/charts` - Charts data
- `GET /dashboard/activity` - Recent activity

#### AI Endpoints (Optional)
- `POST /leads/{domain}/recommendations` - Get AI recommendations
- `GET /leads/{domain}/summary` - AI-enhanced summary

#### Contact Finder Endpoints (Optional)
- `POST /leads/{domain}/find-contacts` - Find contacts for domain

---

### Database Migrations

#### G19 Users Migration
```sql
-- Migration: G19 - Users & Authentication
-- Date: 2025-01-28
-- Description: Adds users table and migrates favorites to user-based

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    microsoft_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    refresh_token_encrypted TEXT,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_microsoft_id ON users(microsoft_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Migrate favorites: session-based → user-based
-- Note: This migration requires manual mapping or user login
-- Existing favorites will be migrated on first login
```

---

## 🧪 Testing Strategy

### Unit Tests
- Auth flow (OAuth 2.0)
- Token generation/validation
- User management
- UI upgrade endpoints
- AI client (mocked)
- Contact finder (mocked)

### Integration Tests
- End-to-end OAuth flow
- Auth-protected endpoints
- UI upgrade features
- AI endpoints (with mocked API)
- Contact finder endpoints

### Manual Testing
- Azure AD login flow
- UI features (sorting, pagination, search)
- PDF preview
- Dashboard charts
- AI recommendations
- Contact finder

---

## 📚 Documentation

### API Documentation
- Auth endpoints (OpenAPI/Swagger)
- UI upgrade endpoints
- AI endpoints (optional)
- Contact finder endpoints (optional)

### README Updates
- Microsoft SSO setup instructions
- UI upgrade features
- AI features (optional)
- Contact finder (optional)

### CHANGELOG Updates
- G19: Auth + UI + Advanced Features added

---

## 🚨 Risk Mitigation

### Microsoft SSO
- **Risk**: Azure AD app registration gerekli (production için)
- **Mitigation**: Development'ta test tenant kullan, production'da production tenant

### AI Features
- **Risk**: OpenAI API key gerekli (cost consideration)
- **Mitigation**: Caching, rate limiting, optional feature (can be disabled)

### Contact Finder
- **Risk**: Legal/ethical considerations (web scraping)
- **Mitigation**: Robots.txt check, rate limiting, terms of service check, optional feature

---

## ✅ Acceptance Criteria

- [ ] Microsoft SSO çalışıyor (login, logout, token refresh)
- [ ] UI upgrade tamamlandı (filters, search, pagination, sorting)
- [ ] PDF preview çalışıyor
- [ ] Dashboard upgrade tamamlandı (KPI cards, charts, recent activity)
- [ ] AI features çalışıyor (optional)
- [ ] Contact Finder çalışıyor (optional)
- [ ] Tests passing (≥15 test cases)
- [ ] Documentation updated

---

**Son Güncelleme**: 2025-01-28  
**Durum**: 📋 Planlama Tamamlandı

