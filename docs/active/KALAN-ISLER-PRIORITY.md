# Kalan İşler - Öncelik Sırası (CRITIQUE GÜNCELLEMESİ)

**Tarih**: 2025-01-28  
**Durum**: ✅ P0 Hardening Tamamlandı (G19) → ✅ P1 Performance Tamamlandı (2025-01-28) → 🔄 **Stabilization Sprint (3 Gün)** - ✅ Gün 1 Tamamlandı → ✅ Gün 2 Tamamlandı → Gün 3: UI Stabilizasyon → P2 Backlog  
**Son Güncelleme**: 2025-01-28 (Gün 2 tamamlandı)  
**Not**: P0 maddelerin tamamı G19'da tamamlandı. P1 maddelerin tamamı 2025-01-28'de tamamlandı. **Stabilization Sprint (3 gün) entegrasyondan önce yapılmalı.** Gün 1 ve Gün 2 tamamlandı. P2 backlog olarak kaldı.

---

## 🔄 STABILIZATION SPRINT (Entegrasyondan Önce - 3 Gün)

**Durum**: 🔄 **In Progress** - ✅ Gün 1 Tamamlandı → ✅ Gün 2 Tamamlandı → Gün 3: UI Stabilizasyon

**Hedef**: Enterprise-Ready / UI-Stable / Integration-Ready

**Süre**: 3 Gün (18 saat) - Gün 1: ✅ Tamamlandı, Gün 2: ✅ Tamamlandı

### Neden Stabilization Sprint?

Hunter'ın "motoru" çalışıyor ama entegrasyondan önce:
- ✅ Test & Doğrulama katmanları → Gün 1'de tamamlandı
- ✅ Monitoring & Metrics → Gün 2'de tamamlandı
- ❌ UI Experience %60-70 stabil → Gün 3'te yapılacak

**Entegrasyon kararı UI üzerinden verilir** → UI stabilization olmadan entegrasyona girmek product flow'u bozar.

### 3 Günlük Plan

**🟦 Gün 1 - Core Stabilizasyon (6-7 saat) ✅ TAMAMLANDI**
- ✅ Alembic drift check + rollback testleri
- ✅ Multi-worker rate limiting test
- ✅ Bulk operations test düzeltmeleri
- ✅ API backward compatibility testleri
- ✅ Redis health check

**🟩 Gün 2 - Monitoring ve Safety (6-7 saat) ✅ TAMAMLANDI**
- ✅ Cache hit metrics
- ✅ Rate limit metrics
- ✅ Bulk operations metrics
- ✅ Error trend logging (Sentry tags)
- ✅ Deadlock simulation testleri
- ✅ Cache invalidation simulation

**🟧 Gün 3 - UI Stabilizasyon (5-6 saat)**
- [ ] Table view cleanup
- [ ] Score breakdown modal iyileştirme
- [ ] Header/Footer sadeleştirme
- [ ] Export/PDF basic
- [ ] Tooltip + hover behavior
- [ ] Favori/Tag UI mini düzenleme

### Detaylı Plan

**Referans**: `docs/active/STABILIZATION-SPRINT-PLAN-v1.0.md` (tam detaylı plan)  
**UI Checklist**: `docs/active/UI-STABILIZATION-CHECKLIST-v1.0.md` (UI detayları)

### Success Criteria

- ✅ Tüm testler geçiyor mu? (`pytest tests/ -v`) - ✅ Gün 1 ve Gün 2 testleri geçti
- ✅ Alembic rollback çalışıyor mu? - ✅ Gün 1'de tamamlandı
- ✅ Multi-worker rate limiting test başarılı mı? - ✅ Gün 1'de tamamlandı
- [ ] UI 2 dakikada kullanılabilir mi? (dogfooding test) - Gün 3'te yapılacak
- ✅ Metrics endpoint çalışıyor mu? (`/healthz/metrics`) - ✅ Gün 2'de tamamlandı
- ✅ Sentry error tracking aktif mi? - ✅ Gün 2'de tamamlandı

**Sonuç**: Hunter v1.1 → **v1.1-stable** (Enterprise-Ready / UI-Stable / Integration-Ready)

---

## 🚨 P0 - CRITICAL (Production'a Çıkmadan Önce - Zorunlu)

**Durum**: ✅ **TAMAMLANDI (G19'da)** - Artık production blocker değil

Bu maddeler **production blocker** idi - G19'da tamamlandı.

### 1-5. P0 Hardening (G19) ✅
- ✅ Database Connection Pooling
- ✅ API Key Security (bcrypt)
- ✅ Structured Logging
- ✅ Error Tracking (Sentry)
- ✅ Health Checks & Probes

**P0 Toplam Süre**: ✅ **Tamamlandı (G19'da ~11 saat)**

---

## ⚠️ P1 - HIGH PRIORITY (Bu Ay - 1-2 Sprint)

**⚠️ KRİTİK**: P1 maddeleri birbirine bağımlı. **Sıralama ve bağımlılık grafiği aşağıda.**

### 📊 P1 Bağımlılık Grafiği

```
┌─────────────────┐
│  1. Alembic     │ ← En önce (migration foundation)
└────────┬────────┘
         │
         ├─→ ┌─────────────────┐
         │   │ 2. Distributed   │ ← Alembic sonrası (DB stable)
         │   │    Rate Limiting │
         └──→└────────┬──────────┘
                      │
                      ├─→ ┌─────────────────┐
                      │   │ 3. Caching      │ ← Rate limit + DB stable
                      │   │    Layer        │
                      └──→└────────┬────────┘
                                   │
                                   ├─→ ┌─────────────────┐
                                   │   │ 4. Bulk         │ ← Cache + Rate limit
                                   │   │    Operations   │
                                   └──→└────────┬────────┘
                                                │
                                                └─→ ┌─────────────────┐
                                                    │ 5. API          │ ← EN SON
                                                    │    Versioning   │
                                                    └─────────────────┘
```

**Sıralama Mantığı:**
1. **Alembic** → Migration foundation (diğer her şey DB'ye dokunuyor)
2. **Distributed Rate Limiting** → Multi-worker için kritik (P2'den P1'e çekildi)
3. **Caching Layer** → Rate limit + DB stable olmalı
4. **Bulk Operations** → Cache + Rate limit olmalı
5. **API Versioning** → EN SON (tüm router'lar stabil olmalı)

---

### 1. Database Migration System (Alembic) ⏱️ **2-3 gün** (revize) ✅ **TAMAMLANDI**

- **Durum**: ✅ **TAMAMLANDI (2025-01-28)** - Alembic migration system implemented (collapsed history strategy)
- **Etki**: Orta - Migration history ve rollback yok
- **Öncelik**: 🔴 **EN ÖNCE** - Diğer P1 maddeleri DB'ye dokunuyor
- **Prerequisites**: None (en önce yapılmalı)
- **Mevcut Durum** (Tamamlandı):
  - ✅ Alembic setup tamamlandı (`alembic/` dizini, `alembic.ini` mevcut)
  - ✅ Base revision oluşturuldu (`08f51db8dce0_base_revision.py`)
  - ✅ Migration history tracking aktif (Alembic version table)
  - ✅ Rollback capability mevcut (`alembic downgrade` komutları)
  - ✅ 6 manual SQL migration file legacy olarak arşivlendi (`app/db/migrations/legacy/`)
  - ✅ Collapsed history stratejisi uygulandı (base revision tüm geçmiş migration'ları temsil ediyor)
- **Lokasyon**: `alembic/` (yeni dizin), `app/db/migrations/` (mevcut)
- **Gerçekçi Süre Tahmini**:
  - Alembic setup: 2 saat
  - 6 migration'ı çevirme: 1 gün (ortalama 20-40 satır SQL → manual rewrite)
  - Test suite backtest: 4 saat
  - Docker/CI entegrasyonu: 4 saat
  - Rollback verification: 4 saat
  - Dev/prod config ayrımı: 2 saat
  - **Toplam: 2-3 gün** (1 gün değil)
- **Base Revision Stratejisi**:
  - Base revision, current production schema'ya göre oluşturulacak (`alembic revision --autogenerate`)
  - Manuel diff ile doğrulanacak (production DB schema vs. autogenerated revision)
  - Empty base revision değil, mevcut schema snapshot'ı base olacak
- **Risksiz Migration Planı**:
  - [x] Alembic setup (`alembic init alembic`) ✅
  - [x] Base revision oluştur (current production schema'dan autogenerate) ✅
  - [x] Base revision'ı stamp et (`alembic stamp 08f51db8dce0`) ✅
  - [x] Eski SQL migration'ları legacy olarak işaretle (`app/db/migrations/legacy/`) ✅
  - [ ] **Schema drift kontrolü**: Alembic migration sonrası canlı DB şeması ile SQLAlchemy modelleri diff kontrolü (`alembic --autogenerate dry-run`)
  - [ ] `run_migration.py` script'ini Alembic kullanacak şekilde güncelle
  - [ ] **Test**: Rollback testleri (`alembic downgrade -1` - gelecekteki migration'lar için)
  - [ ] **Test**: Yeni migration oluşturma testi (`alembic revision --autogenerate`)
  - [ ] CI/CD'ye migration check ekle (pre-commit hook)
  - [ ] Dev/prod config ayrımı (env-based migration path)
  
**NOT**: g16-g20 manuel SQL migration'ları Alembic revision'ına çevrilmedi. Bunun yerine "collapsed history" stratejisi kullanıldı:
- Base revision (`08f51db8dce0`) tüm geçmiş migration'ların sonucunu temsil ediyor
- Eski SQL dosyaları `app/db/migrations/legacy/` altına taşındı (sadece referans için)
- Bundan sonraki tüm schema değişiklikleri Alembic ile yönetilecek
- **Blocker**: ❌ Hayır - Code quality improvement
- **Bağımlılık**: Hiçbiri (en önce yapılmalı)

---

### 2. Distributed Rate Limiting ⏱️ 1 gün (P2'den P1'e çekildi) ✅ **TAMAMLANDI**

- **Durum**: ✅ **TAMAMLANDI** - Redis-based distributed rate limiting implementasyonu tamamlandı
- **Etki**: 🔴 **YÜKSEK** - Multi-instance deployment için kritik
- **Öncelik**: 🔴 **P1** (P2'den çekildi)
- **Prerequisites**: Alembic (DB stable olmalı) ✅
- **Neden P1?**
  - Hunter gerçek dünyada 2 node'a çıkarsa **WHOIS + DNS rate limit** sıradan şekilde kırılır
  - Satış ekibi birden fazla kişi kullanırsa yanlış sonuç çıkarır
  - Microsoft SSO geldi → concurrency artacak
- **Tamamlanan İşler**:
  - ✅ Redis client wrapper oluşturuldu (`app/core/redis_client.py` - connection pooling)
  - ✅ DistributedRateLimiter class oluşturuldu (`app/core/distributed_rate_limiter.py`)
  - ✅ Circuit breaker pattern eklendi (5 failure threshold, 60s recovery timeout)
  - ✅ DNS rate limiter Redis'e migrate edildi (10 req/s, shared across all workers)
  - ✅ WHOIS rate limiter Redis'e migrate edildi (5 req/s, shared across all workers)
  - ✅ API key rate limiter Redis'e migrate edildi (per-key limits, shared across all workers)
  - ✅ In-memory limiter fallback olarak bırakıldı (Redis down durumu için)
  - ✅ Degrade mode logging eklendi (WARN level + Sentry tags)
  - ✅ Health check endpoint'te Redis kontrolü zaten var (`/healthz/ready`)
- **Kalan Testler**:
  - [ ] **Test**: Multi-worker rate limiting test (2 worker, aynı API key, limit kontrolü)
  - [ ] **Test**: Redis down durumu (fallback to in-memory, circuit breaker test)
- **Lokasyon**: `app/core/rate_limiter.py`, `app/core/api_key_auth.py`, `app/core/distributed_rate_limiter.py`, `app/core/redis_client.py`
- **Blocker**: ❌ Hayır - Scale için
- **Bağımlılık**: Alembic (DB stable olmalı) ✅

---

### 3. Caching Layer (DNS/WHOIS/Provider/Scoring) ⏱️ 1.5 gün (revize) ✅ **TAMAMLANDI**

- **Durum**: ✅ **TAMAMLANDI** - Redis-based distributed caching implementasyonu tamamlandı
- **Etki**: Yüksek - Performance ve rate limit koruması
- **Öncelik**: 🔴 **P1** - En pahalı işlemler için kritik
- **Prerequisites**: Alembic + Distributed Rate Limiting (Redis stable olmalı) ✅
- **Tamamlanan İşler**:
  - ✅ Redis-based cache utilities oluşturuldu (`app/core/cache.py`)
  - ✅ DNS cache implementasyonu (1 saat TTL, `analyze_dns()`)
  - ✅ WHOIS cache'i Redis'e migrate edildi (24 saat TTL, in-memory cache kaldırıldı)
  - ✅ Provider mapping cache eklendi (24 saat TTL, `classify_provider()`)
  - ✅ Scoring cache eklendi (1 saat TTL, signals hash ile, `score_domain()`)
  - ✅ Domain-level full scan cache eklendi (1 saat TTL, `scan_single_domain()`)
  - ✅ Cache invalidation on rescan eklendi (`rescan_domain()`)
  - ✅ Graceful fallback when Redis unavailable (tüm cache fonksiyonları)
  - ✅ Test coverage: 14 test (cache hit/miss, Redis unavailable, signals hash)
- **Gerçek Yük Analizi**:
  - 100 domain → DNS root → provider mapping (en çok tekrar eden)
  - Birçok MX root tekrar eden pattern → cache burada daha kritik
  - WHOIS → doğru (zaten var)
  - DNS → doğru (eklenmeli)
  - **Provider mapping → EKSİK** (kritik)
  - **Scoring → EKSİK** (kritik)
- **Lokasyon**: `app/core/cache.py` (yeni dosya), `app/core/analyzer_dns.py`, `app/core/analyzer_whois.py`, `app/core/provider_map.py`, `app/core/scorer.py`
- **Redis Tasarımı (Final)**:
  ```python
  # app/core/cache.py
  # Cache keys:
  # - dns:{domain} → TTL: 1 saat
  # - whois:{domain} → TTL: 24 saat (WHOIS data değişmez)
  # - provider:{mx_root} → TTL: 24 saat (provider mapping değişmez)
  # - scoring:{domain}:{provider}:{signals_hash} → TTL: 1 saat
  # - scan:{domain} → TTL: 1 saat (full scan result cache)
  
  # Signals hash generation:
  # signals_hash = sha256(json.dumps(signals, sort_keys=True).encode())[:16]
  # (sort_keys=True ensures stable hash for same signals)
  
  # Cache invalidation:
  # - DNS: 1 saat TTL (otomatik expire)
  # - WHOIS: 24 saat TTL (otomatik expire)
  # - Provider: 24 saat TTL (otomatik expire)
  # - Scoring: 1 saat TTL (otomatik expire)
  # - Scan: 1 saat TTL (otomatik expire)
  
  # TTL uyumu:
  # Scan cache TTL'i, DNS/WHOIS TTL'lerinden uzun olmayacak;
  # konsistensi bozmamak için üst sınır 1 saat.
  ```
- **Lokasyon**: `app/core/cache.py`, `app/core/analyzer_dns.py`, `app/core/analyzer_whois.py`, `app/core/provider_map.py`, `app/core/scorer.py`, `app/core/tasks.py`, `app/core/rescan.py`, `app/api/scan.py`, `tests/test_cache.py`
- **Blocker**: ❌ Hayır - Performance optimization
- **Bağımlılık**: Distributed Rate Limiting (Redis stable olmalı) ✅

---

### 4. Bulk Operations Optimization ⏱️ **1 gün** (revize - 4 saat değil)

- **Durum**: ✅ **TAMAMLANDI (2025-01-28)** - Batch processing optimization implemented
- **Etki**: Yüksek - Performance improvement
- **Prerequisites**: Alembic + Distributed Rate Limiting + Caching Layer (cache hit rate yüksek olmalı)
- **Tamamlanan Özellikler**:
  - ✅ Batch size calculation (rate-limit aware) - Optimal batch size based on DNS/WHOIS rate limits (default: 50 domains/batch)
  - ✅ Batch commit optimization - Reduces transaction overhead by batching commits
  - ✅ Deadlock prevention - Transaction timeout (30s) and retry logic (3 attempts with exponential backoff)
  - ✅ Partial commit log - Redis-based recovery mechanism for batch failures
  - ✅ Batch isolation - One batch failure doesn't affect other batches
  - ✅ Bulk log context - Structured logging with batch information
  - ✅ scan_single_domain commit=False support - Allows batch-level commit control
  - ✅ Test coverage - 13 tests (8 passed, 2 skipped, 3 errors - test isolation issues)
- **Implementation Files**:
  - `app/core/bulk_operations.py` - Batch utilities
  - `app/core/tasks.py` - Updated bulk_scan_task with batch processing
  - `requirements.txt` - Added tenacity>=8.2.3
  - `tests/test_bulk_operations_p1.py` - P1-4 test suite
- **Lokasyon**: `app/core/tasks.py` (`bulk_scan_task`), `app/api/scan.py`
- **Tamamlanan Güvenlik Katmanı**:
  - [x] ✅ Batch commit optimization - Batch-level commits instead of per-domain commits
  - [x] ✅ Database transaction optimization (batch'ler halinde commit - 50 domain/batch, rate-limit aware)
  - [x] ✅ **Deadlock prevent strategy** (transaction timeout 30s, retry logic with tenacity - 3 attempts)
  - [x] ✅ **Batch failure recovery** (partial commit log, batch isolation)
  - [x] ✅ **Partial commit log** (Redis-based, committed/failed domains tracked)
  - [x] ✅ **Bulk işlemler için ayrı log context** (bulk_id, batch_no, total_batches, batch_size)
  - [x] ✅ **Batch size adaptasyonu** (DNS/WHOIS rate limitlerine göre optimal batch size calculation)
  - [x] ✅ **Rate-limit aware**: Bulk scan, default olarak rate-limit aware; batch boyutu, DNS/WHOIS rate limitlerine göre hesaplanıyor (default: 50 domains/batch)
  - [x] ✅ **Test**: Batch size calculation tests (5 tests)
  - [x] ✅ **Test**: Partial commit log tests (2 tests)
  - [x] ✅ **Test**: Bulk log context tests (1 test)
  - [ ] Memory usage optimization (streaming - generator kullan) - Future optimization
  - [ ] Progress tracking optimize et (her domain yerine batch bazlı) - Future optimization
- **Blocker**: ❌ Hayır - Performance optimization
- **Bağımlılık**: Caching Layer (cache hit rate yüksek olmalı)

---

### 5. API Versioning ⏱️ 4 saat (EN SON) ✅ **TAMAMLANDI**

- **Durum**: ✅ **TAMAMLANDI (2025-01-28)** - API versioning structure implemented with backward compatibility
- **Etki**: Düşük - Backward compatibility için
- **Öncelik**: 🔴 **EN SON** - Tüm router'lar stabil olmalı
- **Prerequisites**: ✅ Alembic + ✅ Distributed Rate Limiting + ✅ Caching Layer + ✅ Bulk Operations (tüm router'lar stabil - P1-4 tamamlandı)
- **Tamamlanan Özellikler**:
  - ✅ API v1 router structure (`/api/v1/...`) - All API endpoints now available under `/api/v1/` prefix
  - ✅ Backward compatibility - Legacy endpoints (`/...`) continue to work for zero downtime migration
  - ✅ Dual-path routing - Both v1 and legacy endpoints active simultaneously
  - ✅ 13 versioned routers: ingest, scan, leads, dashboard, email_tools, progress, admin, notes, tags, favorites, pdf, rescan, alerts
  - ✅ Health and auth endpoints excluded from versioning (infrastructure endpoints)
  - ✅ Proxy pattern - V1 routers proxy to legacy handlers (no code duplication)
  - ✅ Test coverage - 10 tests (backward compatibility, dual-path routing)
- **Implementation Files**:
  - `app/api/v1/` - V1 router directory with proxy pattern handlers
  - `app/api/v1/__init__.py` - V1 router exports
  - `app/api/v1/*.py` - Individual v1 router files (13 routers)
  - `app/main.py` - Updated to register v1 routers and maintain legacy routers
  - `tests/test_api_versioning.py` - API versioning tests
- **Lokasyon**: `app/api/v1/` (yeni dizin yapısı), `app/main.py` (router registration)
- **Zero Downtime Geçiş Planı**:
  - [x] ✅ API versioning yapısı oluştur (`/api/v1/`)
  - [x] ✅ Tüm router'ları `/api/v1/` altına taşı (13 router: ingest, scan, leads, dashboard, email_tools, progress, admin, notes, tags, favorites, pdf, rescan, alerts)
  - [x] ✅ **Backward compatibility**: Eski endpoint'leri `/...` altında bırak (proxy pattern)
  - [ ] OpenAPI docs'u güncelle (version bilgisi) - Future enhancement
  - [ ] Version deprecation strategy belirle (örn: v1 6 ay desteklenir) - Future enhancement
  - [x] ✅ **Test**: Eski endpoint'ler çalışıyor mu kontrol et (backward compatibility)
  - [x] ✅ **Test**: Zero downtime deployment (yeni version deploy, eski version çalışmaya devam)
- **Blocker**: ❌ Hayır - Future-proofing
- **Bağımlılık**: Bulk Operations (tüm router'lar stabil olmalı) ✅

---

## 🔴 P1 Operasyonel Risk Değerlendirmesi

**Prod v1.1 devreye alma sırasında beklenen hata olasılığı ve risk profili**

| Madde | Teknik Karmaşıklık | Prod Risk | Başarısızlık Tipi | Etki | Mitigation |
|-------|-------------------|-----------|-------------------|------|------------|
| **Alembic Migration** | Yüksek | 🔴 **HIGH** | Migration drift, downgrade fail, schema mismatch | Yüksek | Base revision snapshot, dry-run, rollback test, schema drift kontrolü |
| **Distributed Rate Limiting** | Orta | 🟡 **MEDIUM** | Redis unavailable, limiter mismatch, fallback failure | Orta | Circuit breaker + fallback in-memory, degrade mode logging |
| **Caching Layer** (DNS/WHOIS/Provider/Scoring) | Orta | 🔴 **HIGH** | Stale cache, TTL mismatch, consistency loss, cache invalidation | Orta/Yüksek | TTL alignment, versioned cache keys, metrics, signals hash stability |
| **Bulk Operations** | Orta/Yüksek | 🔴 **HIGH** | Deadlock, batch corruption, partial commit, transaction timeout | Yüksek | Retry logic, partial commit log, batch isolation, deadlock prevention |
| **API Versioning** | Düşük | 🟢 **LOW** | 404/route mismatch, BC break, dual-path routing failure | Düşük | Dual-path routing (v1 + legacy), backward compatibility tests, zero downtime deployment |

**Risk Özeti:**
- **HIGH Risk**: Alembic, Caching, Bulk Operations → Detaylı test ve rollback planı gerekli
- **MEDIUM Risk**: Distributed Rate Limiting → Fallback mekanizması kritik
- **LOW Risk**: API Versioning → En az riskli, son yapılacak

**Sprint Planlaması İçin:**
- HIGH risk maddeleri için ekstra buffer süre ayrılmalı (test + rollback verification)
- MEDIUM risk maddeleri için fallback senaryoları test edilmeli
- LOW risk maddeleri için minimal buffer yeterli

---

**P1 Toplam Süre**: ✅ **TAMAMLANDI** (~5-6 gün - 2025-01-28'de tamamlandı)

**P1 Tamamlanma Tarihleri**:
- ✅ **P1-1: Alembic** - 2025-01-28 (Core implementation)
- ✅ **P1-2: Distributed Rate Limiting** - 2025-01-28
- ✅ **P1-3: Caching Layer** - 2025-01-28
- ✅ **P1-4: Bulk Operations** - 2025-01-28
- ✅ **P1-5: API Versioning** - 2025-01-28

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

### 12. N+1 Query Prevention ⏱️ 1 gün (revize)

- **Durum**: ⚠️ Potansiyel sorun - Doğru risk bölgeleri analiz edilmeli
- **Etki**: Orta - Performance (scale için)
- **Mevcut Durum**:
  - ✅ Dashboard query'leri VIEW kullanıyor (`leads_ready` VIEW - raw SQL, N+1 riski düşük)
  - ✅ Leads endpoint raw SQL JOIN kullanıyor (`get_lead` - LEFT JOIN, N+1 yok)
  - ⚠️ Leads list endpoint (`get_leads`) VIEW kullanıyor ama eager loading kontrolü gerekli
  - ❌ **Gerçek N+1 riski**: `leads_ready` VIEW'ın SQL optimize edilmemesi
  - ❌ **Gerçek N+1 riski**: JOIN + ORDER BY + LIMIT pattern'i
  - ❌ **Gerçek N+1 riski**: Provider filtering sırasında unnecessary join'ler
  - ❌ **Gerçek N+1 riski**: Pagination'da yanlış COUNT(*) stratejisi
  - ⚠️ Notes/tags/favorites → **küçük dataset** (N+1 riski düşük)
- **Lokasyon**: `app/api/dashboard.py`, `app/api/leads.py`, `app/db/schema.sql` (VIEW definition)
- **Doğru Risk Bölgeleri**:
  1. `leads_ready` VIEW'ın SQL optimize edilmemesi
  2. JOIN + ORDER BY + LIMIT pattern'i (pagination)
  3. Provider filtering sırasında unnecessary join'ler
  4. Pagination'da yanlış COUNT(*) stratejisi
- **Aksiyon**:
  - [ ] `leads_ready` VIEW SQL'ini audit et (N+1 var mı?)
  - [ ] JOIN + ORDER BY + LIMIT pattern'ini optimize et
  - [ ] Provider filtering'de unnecessary join'leri kaldır
  - [ ] Pagination COUNT(*) stratejisini optimize et (window function?)
  - [ ] Eager loading ekle (joinedload, selectinload) - gerekli yerlerde
  - [ ] **Test**: Query count kontrol et (N+1 yok mu? - SQLAlchemy query logging)
- **Blocker**: ❌ Hayır - Performance optimization

**P2 Toplam Süre**: ~1 hafta

---

## 🎨 G19 - Incomplete Optional Features

G19 tamamlandı ama bazı optional feature'lar ertelendi.

### 14-18. Optional Features (Backlog)
- PDF Preview (Frontend) ⏱️ 2 saat
- Dashboard Charts ⏱️ 4 saat
- Recent Activity Feed ⏱️ 4 saat
- AI Features (G20'ye Taşındı) ⏱️ 1 hafta
- Contact Finder (G21'ye Taşındı) ⏱️ 1 hafta

---

## 🔧 G18 - Incomplete Features

G18 tamamlandı ama bazı optional feature'lar eksik.

### 19-21. Optional Features (Backlog)
- Schedule Configuration Endpoint ⏱️ 2 saat
- Slack Notifications ⏱️ 3 saat
- Daily Digest Frequency ⏱️ 4 saat

---

## 📊 Öncelik Özeti (Revize)

| Öncelik | Madde Sayısı | Toplam Süre | Prod Blocker? | Durum |
|---------|--------------|-------------|---------------|-------|
| **P0** | 5 | ~11 saat (1.5 gün) | ✅ Evet (artık çözüldü) | ✅ **Tamamlandı (G19)** |
| **P1** | 5 | **~5-6 gün** | ❌ Hayır | ✅ **Tamamlandı (2025-01-28)** |
| **🔄 Stabilization Sprint** | 3 gün | **~18 saat (3 gün)** | ⚠️ Entegrasyon öncesi | 🔄 **In Progress** - Gün 1 ✅, Gün 2 ✅ |
| **P2** | 3 | ~1 hafta | ❌ Hayır | 📋 Backlog |
| **G19 Optional** | 3 | ~10 saat | ❌ Hayır | 📋 Backlog |
| **G18 Optional** | 3 | ~9 saat | ❌ Hayır | 📋 Backlog |
| **Future Sprints** | 2 | ~2 hafta | ❌ Hayır | 📋 Planlandı |

---

## 🎯 Önerilen Aksiyon Planı (Revize)

### ✅ Tamamlandı (G19 - P0 Hardening)
1. ✅ DB Connection Pooling (1 saat) - **Tamamlandı**
2. ✅ API Key Security (2 saat) - **Tamamlandı**
3. ✅ Structured Logging (4 saat) - **Tamamlandı**
4. ✅ Error Tracking (2 saat) - **Tamamlandı**
5. ✅ Health Checks & Probes (2 saat) - **Tamamlandı**

**Toplam**: ✅ ~11 saat (1.5 gün) - **G19'da tamamlandı**

### ✅ P1 Performance - **TAMAMLANDI (2025-01-28)**

**Tamamlanan İşler:**
1. ✅ Alembic Migration (P1-1) - **TAMAMLANDI**
2. ✅ Distributed Rate Limiting (P1-2) - **TAMAMLANDI**
3. ✅ Caching Layer (P1-3) - **TAMAMLANDI**
4. ✅ Bulk Operations Optimization (P1-4) - **TAMAMLANDI**
5. ✅ API Versioning (P1-5) - **TAMAMLANDI**

**Toplam**: ✅ **~5-6 gün** - **2025-01-28'de tamamlandı**

### 🔄 Stabilization Sprint - **IN PROGRESS (3 Gün)**

**Hedef**: Enterprise-Ready / UI-Stable / Integration-Ready

**Durum**: ✅ Gün 1 Tamamlandı → ✅ Gün 2 Tamamlandı → Gün 3: UI Stabilizasyon

**3 Günlük Plan:**
1. **Gün 1 - Core Stabilizasyon** (6-7 saat) ✅ **TAMAMLANDI**
   - ✅ Alembic drift check + rollback testleri
   - ✅ Multi-worker rate limiting test
   - ✅ Bulk operations test düzeltmeleri
   - ✅ API backward compatibility testleri
   - ✅ Redis health check

2. **Gün 2 - Monitoring ve Safety** (6-7 saat) ✅ **TAMAMLANDI**
   - ✅ Cache hit metrics
   - ✅ Rate limit metrics
   - ✅ Bulk operations metrics
   - ✅ Error trend logging (Sentry tags)
   - ✅ Deadlock simulation testleri
   - ✅ Cache invalidation simulation

3. **Gün 3 - UI Stabilizasyon** (5-6 saat)
   - [ ] Table view cleanup
   - [ ] Score breakdown modal iyileştirme
   - [ ] Header/Footer sadeleştirme
   - [ ] Export/PDF basic
   - [ ] Tooltip + hover behavior
   - [ ] Favori/Tag UI mini düzenleme

**Detaylı Plan**: `docs/active/STABILIZATION-SPRINT-PLAN-v1.0.md`  
**UI Checklist**: `docs/active/UI-STABILIZATION-CHECKLIST-v1.0.md`

**Toplam**: 📋 **~18 saat (3 gün)** - **Entegrasyondan önce yapılmalı**

### Backlog (İhtiyaç Olduğunda - P2 Refactor)
- Sync-First Refactor
- Repository/Service Layer
- N+1 Query Prevention (doğru risk bölgeleri)

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

### ✅ Prod v1.0 (P0-only) - G19'da Tamamlandı

**Şartlar**: P0 checklist yeşil

- [x] P0 maddelerin tamamı tamamlandı ✅ **G19'da**
- [x] Microsoft SSO authentication çalışıyor ✅ **G19'da**
- [x] Error tracking aktif ✅ **G19'da**
- [x] Structured logging aktif ✅ **G19'da**
- [x] DB connection pooling yapılandırıldı ✅ **G19'da**
- [x] API key security (bcrypt) aktif ✅ **G19'da**
- [x] Health checks & probes (liveness/readiness/startup) aktif ✅ **G19'da**

**Sonuç**: ✅ **Production v1.0'a çıkılabilir** - Tüm P0 maddeler G19'da tamamlandı.

---

### ⚠️ Prod v1.1 (P1-enabled) - P1 Sonrası Checklist

**Şartlar**: P0 + P1 Go/No-Go (Redis health, Alembic rollback tested, DRL tested, cache hit metrics, bulk tests)

**P1 tamamlandıktan sonra eklenmesi gerekenler:**

- [ ] Redis health check eklendi (`/healthz/ready` - Redis ping)
- [ ] Versioning paths test edildi (backward compatibility)
- [ ] Alembic migration test eklendi (rollback verification)
- [ ] Bulk transaction test eklendi (deadlock, recovery)
- [ ] Cache hit rate monitoring eklendi (Redis metrics)
- [ ] Distributed rate limiting test eklendi (multi-worker)
- [ ] Provider/Scoring cache test eklendi (performance improvement)

**Not**: P1 maddeleri production için önemli ama blocker değil. P0 tamamlandığı için production v1.0'a çıkılabilir. P1 tamamlandıktan sonra v1.1'e geçilebilir.

---

| Versiyon | Şartlar                                                                                             |
| -------- | --------------------------------------------------------------------------------------------------- |
| **v1.0** | P0 checklist yeşil                                                                                  |
| **v1.1** | P0 + P1 Go/No-Go (Redis health, Alembic rollback tested, DRL tested, cache hit metrics, bulk tests) |

---

## 📝 Derinleştirilmiş Analiz Notları

### Codebase Analizi (2025-01-28 - Critique Sonrası)

**Caching Durumu:**
- ✅ Redis-based distributed caching tamamlandı (P1-3)
- ✅ DNS cache eklendi (1 saat TTL)
- ✅ WHOIS cache Redis'e migrate edildi (24 saat TTL)
- ✅ Provider mapping cache eklendi (24 saat TTL)
- ✅ Scoring cache eklendi (1 saat TTL, signals hash ile)
- ✅ Domain-level full scan cache eklendi (1 saat TTL)
- ✅ Cache invalidation on rescan eklendi

**Migration Durumu:**
- ✅ Alembic migration system tamamlandı (P1-1)
- ✅ Base revision oluşturuldu (`08f51db8dce0`)
- ✅ Manual SQL migration'lar legacy olarak arşivlendi
- ✅ Collapsed history stratejisi uygulandı

**API Versioning:**
- ✅ API versioning tamamlandı (P1-5)
- ✅ V1 router structure (`/api/v1/...`) aktif
- ✅ Backward compatibility korundu (legacy endpoints çalışıyor)
- ✅ 13 versioned router aktif

**Bulk Operations:**
- ✅ Batch processing optimization tamamlandı (P1-4)
- ✅ Deadlock prevention strategy eklendi (transaction timeout + retry)
- ✅ Batch failure recovery eklendi (partial commit log)
- ✅ Batch isolation ve bulk log context eklendi

**Rate Limiting:**
- ✅ Redis-based distributed rate limiting tamamlandı (P1-2)
- ✅ Circuit breaker pattern eklendi
- ✅ Fallback to in-memory limiter eklendi
- ✅ Multi-worker rate limiting desteği aktif

**Query Optimization:**
- Dashboard ve leads endpoint'leri VIEW/raw SQL kullanıyor (N+1 riski düşük)
- **Gerçek N+1 riski**: VIEW SQL optimize edilmemesi, JOIN + ORDER BY + LIMIT, pagination COUNT(*)
- Notes/tags/favorites → küçük dataset (N+1 riski düşük)

**Eksik Analizler (Durum Tag'leri ile):**
- `[PLANNED]` Log volume & log rotation strategy
- `[PLANNED]` Connection leak detection
- `[NOT STARTED]` WHOIS fallback strategy (API fallback? third party?)
- `[NOT STARTED]` DNS retry mekanizması
- `[DEFERRED]` Provider mapping override mekanizması (UI gerekli)
- `[PLANNED]` Data normalizasyon conflict resolution
- `[PLANNED]` Duplicate lead resolution
- `[NOT STARTED]` VIEW refresh frequency (PostgreSQL materialized view?)
- `[PLANNED]` Error code matrix
- `[PLANNED]` Test suite coverage target mapping
- `[PLANNED]` Sentry categorization strategy
- `[NOT STARTED]` P1 ve P2'nin WSL2 + Docker'da resource consumption analizi
- `[PLANNED]` Production-ready memory footprint
- `[PLANNED]` Health check metrics (scanner latency + DNS latency)

---

**Son Güncelleme**: 2025-01-28  
**Durum**: Active - Production hardening + future planning  
**Analiz**: Critique sonrası P1/P2 öncelikleri ve bağımlılıklar revize edildi. Gerçekçi süre tahminleri ve risksiz migration planları eklendi.
