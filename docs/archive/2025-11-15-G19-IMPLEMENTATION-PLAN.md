# G19 - Implementation Plan

**Tarih**: 2025-01-28  
**Durum**: 📋 Planlama  
**Sprint**: G19 (Post-MVP Sprint 6)  
**Süre**: 2-3 hafta

---

## 🎯 Sprint Hedefi

Advanced features - Auth, UI upgrade, AI features (optional).

---

## 📋 Implementation Phases

### Phase 1: Microsoft SSO (Week 1)
- Azure AD app registration
- OAuth 2.0 flow implementation
- Users table migration
- Auth endpoints (4 endpoints)
- Session management (JWT tokens)

### Phase 2: UI/Dashboard Upgrade (Week 2)
- Lead table upgrade (sorting, pagination, search)
- Priority & score display
- PDF preview
- Bulk upload UI
- Sales panel (KPI cards, charts, recent activity)

### Phase 3: AI Features (Optional, Week 3)
- AI recommendation engine
- AI endpoints (2 endpoints)
- Caching strategy

### Phase 4: Contact Finder (Optional, Week 3)
- Web scraping (legal compliance)
- Pattern generation
- SMTP-check integration
- Contact finder endpoint

---

## 🔧 Key Technical Decisions

### Authentication
- **Strategy**: JWT tokens (stateless, scalable)
- **Library**: `msal` (Microsoft Authentication Library)
- **Token Storage**: Access token in Authorization header, refresh token in HTTP-only cookie

### UI Upgrade
- **Frontend**: Vanilla JavaScript (no framework change)
- **PDF Viewer**: PDF.js
- **Charts**: Chart.js

### AI Features
- **Model**: OpenAI GPT-4 (or local Ollama)
- **Caching**: Redis (24 hours)

---

## 📦 New Dependencies

```txt
msal>=1.24.0
python-jose[cryptography]>=3.3.0
openai>=1.0.0  # Optional
beautifulsoup4>=4.12.0  # Optional
```

---

## 🗄️ Database Changes

### New Tables
- `users` - User management (Microsoft SSO)

### Migrations
- Favorites: session-based → user-based (on first login)
- Notes/Tags: Add user_id (optional, nullable)

---

## 🧪 Testing

- Unit tests: Auth flow, UI endpoints, AI client
- Integration tests: End-to-end OAuth, protected endpoints
- Manual testing: Azure AD login, UI features

---

## 📚 Documentation

- API documentation (OpenAPI/Swagger)
- README updates (Microsoft SSO setup, UI features)
- CHANGELOG updates (G19 features)

---

## ✅ Acceptance Criteria

- [ ] Microsoft SSO çalışıyor
- [ ] UI upgrade tamamlandı
- [ ] PDF preview çalışıyor
- [ ] AI features çalışıyor (optional)
- [ ] Contact Finder çalışıyor (optional)
- [ ] Tests passing (≥15 test cases)

---

**Detaylı Plan**: [.cursor/plans/G19-auth-ui-advanced-plan.md](../../.cursor/plans/G19-auth-ui-advanced-plan.md)  
**TODO**: [docs/todos/G19-auth-ui-advanced.md](../todos/G19-auth-ui-advanced.md)

