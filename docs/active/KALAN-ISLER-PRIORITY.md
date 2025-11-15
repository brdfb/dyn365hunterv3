# Kalan İşler - Öncelik Sırası

**Tarih**: 2025-01-28  
**Durum**: G19 Tamamlandı → P0 Hardening Tamamlandı, P1/P2 Backlog  
**Son Güncelleme**: 2025-01-28  
**Not**: P0 maddelerin tamamı G19'da tamamlandı. Artık production blocker yok.

---

## 🚨 P0 - CRITICAL (Production'a Çıkmadan Önce - Zorunlu)

**Durum**: ✅ **TAMAMLANDI (G19'da)** - Artık production blocker değil

Bu maddeler **production blocker** idi - G19'da tamamlandı.

### 1. Database Connection Pooling ⏱️ 1 saat
- **Durum**: ✅ **Tamamlandı (G19)**
- **Etki**: Yüksek - Concurrent request'lerde connection exhaustion riski
- **Lokasyon**: `app/db/session.py`
- **Tamamlanan İşler**:
  - [x] `pool_size=20`, `max_overflow=10`, `pool_recycle=3600` eklendi
  - [x] Environment variable'lara taşındı (`HUNTER_DB_POOL_SIZE`, `HUNTER_DB_MAX_OVERFLOW`)
  - [x] Concurrent request test (100+ parallel requests)
- **Blocker**: ✅ Evet (artık çözüldü)

### 2. API Key Security (bcrypt/Argon2) ⏱️ 2 saat
- **Durum**: ✅ **Tamamlandı (G19)**
- **Etki**: Yüksek - Security vulnerability
- **Lokasyon**: `app/core/api_key_auth.py`
- **Tamamlanan İşler**:
  - [x] `bcrypt` dependency eklendi
  - [x] `hash_api_key()` ve `verify_api_key()` fonksiyonları güncellendi
  - [x] Migration stratejisi (eski key'ler için backward compatibility)
  - [x] Test: API key verification testleri
- **Blocker**: ✅ Evet (artık çözüldü)

### 3. Structured Logging ⏱️ 4 saat
- **Durum**: ✅ **Tamamlandı (G19)**
- **Etki**: Orta - Production debugging zor
- **Lokasyon**: `app/core/logging.py`
- **Tamamlanan İşler**:
  - [x] Structured logging setup (structlog, JSON format)
  - [x] Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - [x] Request ID tracking
  - [x] PII maskeleme (email, domain)
  - [x] Tüm endpoint'lere logging eklendi
  - [x] Test: Log output kontrolü
- **Blocker**: ✅ Evet (artık çözüldü)

### 4. Error Tracking (Sentry) ⏱️ 2 saat
- **Durum**: ✅ **Tamamlandı (G19)**
- **Etki**: Orta - Production error tracking yok
- **Lokasyon**: `app/core/error_tracking.py`
- **Tamamlanan İşler**:
  - [x] `sentry-sdk` dependency eklendi
  - [x] `HUNTER_SENTRY_DSN` environment variable eklendi
  - [x] Sentry initialization (`app/main.py`)
  - [x] FastAPI + SQLAlchemy integrations
  - [x] Test: Exception fırlat, Sentry'de görünüyor mu?
- **Blocker**: ✅ Evet (artık çözüldü)

### 5. Health Checks & Probes ⏱️ 2 saat
- **Durum**: ✅ **Tamamlandı (G19)**
- **Etki**: Yüksek - Kubernetes/Docker orchestration için kritik
- **Lokasyon**: `app/api/health.py`
- **Tamamlanan İşler**:
  - [x] `/healthz/live` - Liveness probe
  - [x] `/healthz/ready` - Readiness probe (DB + Redis ping)
  - [x] `/healthz/startup` - Startup probe
  - [x] Legacy `/healthz` endpoint'i güncellendi (Redis eklendi)
  - [x] HTTP status code'ları düzeltildi (503 Service Unavailable)
  - [x] Kubernetes deployment örneği eklendi (docs)
- **Blocker**: ✅ Evet (artık çözüldü)

**P0 Toplam Süre**: ✅ **Tamamlandı (G19'da ~11 saat)**

---

## ⚠️ P1 - HIGH PRIORITY (Bu Ay - 1-2 Sprint)

Bu maddeler production için önemli ama blocker değil.

### 6. Caching Layer (DNS/WHOIS) ⏱️ 1 gün
- **Durum**: ❌ Eksik
- **Etki**: Yüksek - Performance ve rate limit koruması
- **Lokasyon**: `app/core/cache.py` (yeni dosya)
- **Aksiyon**:
  - [ ] DNS cache implementasyonu (1 saat TTL)
  - [ ] WHOIS cache implementasyonu (24 saat TTL)
  - [ ] `analyzer_dns.py` ve `analyzer_whois.py`'ye cache ekle
  - [ ] Test: Aynı domain'i 2 kez scan et, cache hit kontrol et
- **Blocker**: ❌ Hayır - Performance optimization

### 7. Database Migration System (Alembic) ⏱️ 1 gün
- **Durum**: ❌ Eksik - Şu an manual SQL migration files
- **Etki**: Orta - Migration history ve rollback yok
- **Lokasyon**: `alembic/` (yeni dizin)
- **Aksiyon**:
  - [ ] Alembic setup (`alembic init alembic`)
  - [ ] Mevcut migration'ları Alembic'e migrate et
  - [ ] Migration script güncelle
  - [ ] Rollback testleri
- **Blocker**: ❌ Hayır - Code quality improvement

### 8. API Versioning ⏱️ 4 saat
- **Durum**: ❌ Eksik
- **Etki**: Düşük - Backward compatibility için
- **Lokasyon**: `app/api/v1/` (yeni dizin yapısı)
- **Aksiyon**:
  - [ ] API versioning yapısı (`/api/v1/`, `/api/v2/`)
  - [ ] Mevcut endpoint'leri `/api/v1/` altına taşı
  - [ ] Version deprecation strategy
- **Blocker**: ❌ Hayır - Future-proofing

### 9. Bulk Operations Optimization ⏱️ 4 saat
- **Durum**: ⚠️ Kısmi - Bulk scan var ama optimize edilebilir
- **Etki**: Yüksek - Performance improvement
- **Lokasyon**: `app/api/scan.py`, `app/core/tasks.py`
- **Aksiyon**:
  - [ ] Batch insert optimization (bulk insert)
  - [ ] Database transaction optimization
  - [ ] Memory usage optimization (streaming)
- **Blocker**: ❌ Hayır - Performance optimization

**P1 Toplam Süre**: ~2.5 gün

---

## 📋 P2 - MEDIUM PRIORITY (Backlog - İhtiyaç Olduğunda)

Bu maddeler code quality ve maintainability için iyi ama acil değil.

### 10. Sync-First Refactor ⏱️ 2 gün
- **Durum**: ❌ Eksik - Şu an async-first yaklaşım
- **Etki**: Düşük - Code maintainability
- **Açıklama**: Async fonksiyonları sync'e çevir (gereksiz async'ler)
- **Blocker**: ❌ Hayır - Code quality

### 11. Repository/Service Layer ⏱️ 3 gün
- **Durum**: ❌ Eksik - Şu an direct DB access
- **Etki**: Düşük - Code organization
- **Açıklama**: Repository pattern ve service layer ekle
- **Blocker**: ❌ Hayır - Architecture improvement

### 12. Distributed Rate Limiting ⏱️ 1 gün
- **Durum**: ⚠️ Kısmi - Şu an in-memory rate limiting
- **Etki**: Düşük - Multi-instance deployment için
- **Açıklama**: Redis-based distributed rate limiting
- **Blocker**: ❌ Hayır - Scale için

### 13. N+1 Query Prevention ⏱️ 1 gün
- **Durum**: ⚠️ Potansiyel sorun - Dashboard query'leri
- **Etki**: Orta - Performance (scale için)
- **Açıklama**: Eager loading (joinedload, selectinload) ekle
- **Blocker**: ❌ Hayır - Performance optimization

**P2 Toplam Süre**: ~1 hafta

---

## 🎨 G19 - Incomplete Optional Features

G19 tamamlandı ama bazı optional feature'lar ertelendi.

### 14. PDF Preview (Frontend) ⏱️ 2 saat
- **Durum**: ❌ Eksik - Backend var, frontend yok
- **Etki**: Düşük - UX improvement
- **Lokasyon**: `mini-ui/` (frontend)
- **Aksiyon**:
  - [ ] PDF.js integration
  - [ ] In-browser PDF viewer
  - [ ] PDF download button
- **Öncelik**: 🟢 Düşük - Nice to have

### 15. Dashboard Charts ⏱️ 4 saat
- **Durum**: ❌ Eksik - Backend endpoint yok
- **Etki**: Düşük - Dashboard visualization
- **Lokasyon**: `app/api/dashboard.py`, `mini-ui/`
- **Aksiyon**:
  - [ ] Backend: `GET /dashboard/charts` endpoint
  - [ ] Frontend: Chart.js integration
  - [ ] Segment distribution chart (pie chart)
  - [ ] Score distribution chart (histogram)
- **Öncelik**: 🟢 Düşük - Nice to have

### 16. Recent Activity Feed ⏱️ 4 saat
- **Durum**: ❌ Eksik
- **Etki**: Düşük - Dashboard activity tracking
- **Lokasyon**: `app/api/dashboard.py`, `mini-ui/`
- **Aksiyon**:
  - [ ] Backend: `GET /dashboard/activity` endpoint
  - [ ] Activity tracking (last 10 scans, favorites, notes)
  - [ ] Frontend: Recent activity feed component
- **Öncelik**: 🟢 Düşük - Nice to have

### 17. AI Features (G20'ye Taşındı) ⏱️ 1 hafta
- **Durum**: 📋 Planlandı - G20 sprint'ine taşındı
- **Etki**: Orta - AI-enhanced recommendations
- **Açıklama**: AI recommendation engine, AI-enhanced summary
- **Öncelik**: 🟡 Orta - Future sprint

### 18. Contact Finder (G21'ye Taşındı) ⏱️ 1 hafta
- **Durum**: 📋 Planlandı - G21 sprint'ine taşındı
- **Etki**: Orta - Contact discovery
- **Açıklama**: Web scraping, pattern generation, SMTP-check
- **Öncelik**: 🟡 Orta - Future sprint (legal review gerekli)

---

## 🔧 G18 - Incomplete Features

G18 tamamlandı ama bazı optional feature'lar eksik.

### 19. Schedule Configuration Endpoint ⏱️ 2 saat
- **Durum**: ❌ Eksik - Schedule hardcoded
- **Etki**: Düşük - Schedule sadece kod içinde değiştirilebilir
- **Lokasyon**: `app/api/scheduler.py` (yeni dosya)
- **Aksiyon**:
  - [ ] `GET /scheduler/config` - Mevcut schedule'ı göster
  - [ ] `POST /scheduler/config` - Schedule'ı değiştir (daily/weekly/monthly)
- **Öncelik**: 🟢 Düşük - Nice to have

### 20. Slack Notifications ⏱️ 3 saat
- **Durum**: ❌ Eksik - Sadece webhook ve email var
- **Etki**: Düşük - Optional notification method
- **Lokasyon**: `app/core/notifications.py`
- **Aksiyon**:
  - [ ] `send_slack_notification()` fonksiyonu ekle
  - [ ] Slack webhook URL ile HTTP POST
  - [ ] Alert config'e Slack seçeneği ekle
- **Öncelik**: 🟢 Düşük - Optional

### 21. Daily Digest Frequency ⏱️ 4 saat
- **Durum**: ❌ Eksik - Alert config'de var ama implementasyon yok
- **Etki**: Orta - Feature eksik
- **Lokasyon**: `app/core/notifications.py`
- **Aksiyon**:
  - [ ] Daily digest için ayrı Celery Beat task
  - [ ] Veya `process_pending_alerts()` içinde frequency kontrolü
  - [ ] Daily digest aggregation logic
- **Öncelik**: 🟡 Orta - Feature completion

---

## 📊 Öncelik Özeti

| Öncelik | Madde Sayısı | Toplam Süre | Prod Blocker? | Durum |
|---------|--------------|-------------|---------------|-------|
| **P0** | 5 | ~11 saat (1.5 gün) | ✅ Evet (artık çözüldü) | ✅ **Tamamlandı (G19)** |
| **P1** | 4 | ~2.5 gün | ❌ Hayır | 📋 Backlog |
| **P2** | 4 | ~1 hafta | ❌ Hayır | 📋 Backlog |
| **G19 Optional** | 3 | ~10 saat | ❌ Hayır | 📋 Backlog |
| **G18 Optional** | 3 | ~9 saat | ❌ Hayır | 📋 Backlog |
| **Future Sprints** | 2 | ~2 hafta | ❌ Hayır | 📋 Planlandı |

---

## 🎯 Önerilen Aksiyon Planı

### ✅ Tamamlandı (G19 - P0 Hardening)
1. ✅ DB Connection Pooling (1 saat) - **Tamamlandı**
2. ✅ API Key Security (2 saat) - **Tamamlandı**
3. ✅ Structured Logging (4 saat) - **Tamamlandı**
4. ✅ Error Tracking (2 saat) - **Tamamlandı**
5. ✅ Health Checks & Probes (2 saat) - **Tamamlandı**

**Toplam**: ✅ ~11 saat (1.5 gün) - **G19'da tamamlandı**

### Bu Ay (2-3 Hafta - P1 Performance)
1. ✅ Caching Layer (1 gün)
2. ✅ Bulk Operations Optimization (4 saat)
3. ✅ Alembic Migration (1 gün)
4. ✅ API Versioning (4 saat)

**Toplam**: ~2.5 gün

### Backlog (İhtiyaç Olduğunda - P2 Refactor)
- Sync-First Refactor
- Repository/Service Layer
- Distributed Rate Limiting
- N+1 Query Prevention

### Optional Features (Zaman Kalırsa)
- PDF Preview
- Dashboard Charts
- Recent Activity
- Schedule Configuration
- Slack Notifications
- Daily Digest Frequency

### Future Sprints
- **G20**: AI Features (1 hafta)
- **G21**: Contact Finder (1 hafta)

---

## 🚦 Production Go/No-Go Checklist

### ✅ Go (Production'a Çıkabilir) - G19'da Tamamlandı
- [x] P0 maddelerin tamamı tamamlandı ✅ **G19'da**
- [x] Microsoft SSO authentication çalışıyor ✅ **G19'da**
- [x] Error tracking aktif ✅ **G19'da**
- [x] Structured logging aktif ✅ **G19'da**
- [x] DB connection pooling yapılandırıldı ✅ **G19'da**
- [x] API key security (bcrypt) aktif ✅ **G19'da**
- [x] Health checks & probes (liveness/readiness/startup) aktif ✅ **G19'da**

**Sonuç**: ✅ **Production'a çıkılabilir** - Tüm P0 maddeler G19'da tamamlandı.

### ⚠️ No-Go (Production'a Çıkmadan Önce) - Artık Geçerli Değil
- ~~[ ] P0 maddelerden herhangi biri eksik~~ → ✅ **Tümü tamamlandı**
- ~~[ ] Authentication yok~~ → ✅ **Microsoft SSO eklendi**
- ~~[ ] Error tracking yok~~ → ✅ **Sentry eklendi**
- ~~[ ] Structured logging yok~~ → ✅ **structlog eklendi**
- ~~[ ] DB connection pooling yok~~ → ✅ **Pooling yapılandırıldı**
- ~~[ ] API key security (SHA-256, salt yok)~~ → ✅ **bcrypt'e migrate edildi**
- ~~[ ] Health checks eksik~~ → ✅ **Liveness/readiness/startup eklendi**

---

**Son Güncelleme**: 2025-01-28  
**Durum**: Active - Production hardening + future planning

