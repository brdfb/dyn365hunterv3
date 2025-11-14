# TODO: Sprint 6 (G19) - Auth + UI + Advanced Features

**Date Created**: 2025-11-14  
**Status**: 📋 Planned  
**Phase**: G19 (Post-MVP Sprint 6)  
**Süre**: 2-3 hafta

---

## 🎯 Sprint Hedefi

Advanced features - Auth, UI upgrade, AI features (optional).

**Strateji**: Artık ürün şekillendi → kozmetik + güvenlik + AI sprint'i.

---

## 📋 Tasks

### Microsoft SSO Authentication

- [ ] Microsoft Identity Platform entegrasyonu
  - [ ] Azure AD app registration
  - [ ] OAuth 2.0 flow setup
  - [ ] Token validation
  - [ ] User management (users tablosu)

- [ ] Session management
  - [ ] Token storage
  - [ ] Token refresh
  - [ ] Session timeout

- [ ] Auth endpoints
  - [ ] `GET /auth/login` - Login redirect
  - [ ] `GET /auth/callback` - OAuth callback
  - [ ] `POST /auth/logout` - Logout
  - [ ] `GET /auth/me` - Current user

### UI / Dashboard Upgrade

- [ ] Lead table upgrade
  - [ ] Filters (segment, min_score, provider, tags)
  - [ ] Sorting (priority, score, domain)
  - [ ] Pagination
  - [ ] Search functionality

- [ ] Priority order display
  - [ ] Priority badge/indicator
  - [ ] Priority-based sorting

- [ ] PDF preview
  - [ ] In-browser PDF viewer
  - [ ] PDF download button

- [ ] Score explanation
  - [ ] Tooltip/modal with score breakdown
  - [ ] Score factors explanation

- [ ] Bulk upload UI
  - [ ] File drag-drop
  - [ ] Upload progress
  - [ ] Error display

- [ ] Sales panel (dashboard upgrade)
  - [ ] KPI cards (total leads, migration leads, high priority)
  - [ ] Charts (segment distribution, score distribution)
  - [ ] Recent activity

### AI Features (Optional)

- [ ] AI Recommendation engine
  - [ ] Migration readiness recommendation
  - [ ] Risk assessment recommendation
  - [ ] Next steps recommendation
  - [ ] AI model integration (OpenAI API veya local model)

- [ ] AI endpoints
  - [ ] `POST /leads/{domain}/recommendations` - Get AI recommendations
  - [ ] `GET /leads/{domain}/summary` - AI-enhanced summary

### Contact Finder (Optional)

- [ ] Web scraping (legal/ethical considerations)
  - [ ] Contact page scraping
  - [ ] Email pattern extraction
  - [ ] Legal compliance check

- [ ] Pattern generation
  - [ ] firstname.lastname@domain.com
  - [ ] f.lastname@domain.com
  - [ ] firstname@domain.com

- [ ] SMTP-check integration
  - [ ] Email validation
  - [ ] SMTP verification

- [ ] Rate limiting (web scraping için)

### API Endpoints

- [ ] Auth endpoints (4 endpoint)
- [ ] UI upgrade endpoints (filters, search, etc.)
- [ ] AI endpoints (2 endpoint, optional)
- [ ] Contact Finder endpoints (1 endpoint, optional)

### Testing

- [ ] Unit tests
  - [ ] Auth tests
  - [ ] UI upgrade tests
  - [ ] AI features tests (optional)
  - [ ] Contact Finder tests (optional)

- [ ] Integration tests
  - [ ] Auth end-to-end test
  - [ ] UI upgrade end-to-end test
  - [ ] AI features end-to-end test (optional)

### Documentation

- [ ] API documentation
  - [ ] Auth endpoints docs
  - [ ] UI upgrade docs
  - [ ] AI features docs (optional)
  - [ ] Contact Finder docs (optional)

- [ ] README.md güncellemesi
  - [ ] Microsoft SSO setup
  - [ ] UI upgrade features
  - [ ] AI features (optional)

- [ ] CHANGELOG.md güncellemesi
  - [ ] G19: Auth + UI + Advanced Features added

---

## ✅ Acceptance Criteria

- [ ] Microsoft SSO çalışıyor (login, logout, token refresh)
- [ ] UI upgrade tamamlandı (filters, search, pagination)
- [ ] PDF preview çalışıyor
- [ ] AI features çalışıyor (optional)
- [ ] Contact Finder çalışıyor (optional)
- [ ] Tests passing (≥15 test cases)

---

## 📝 Notes

### Çıkarılanlar (Kritik Değerlendirme Sonrası)

- ❌ Hiçbir şey çıkarılmadı (Sprint 6 advanced features sprint'i)

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

