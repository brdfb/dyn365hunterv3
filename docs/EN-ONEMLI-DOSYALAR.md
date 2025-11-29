# 📋 Docs Klasörü - En Önemli Dosyalar

**Tarih:** 2025-01-30  
**Amaç:** Docs klasöründeki en kritik dosyaların hızlı referans listesi

---

## 🔥 **KRİTİK AKTİF DOSYALAR** (Öncelik: P0)

### 1. **CRITICAL-3-HAMLE-PRODUCT-READY.md** ⭐⭐⭐
**Konum:** `docs/active/CRITICAL-3-HAMLE-PRODUCT-READY.md`  
**Önemi:** 🔥 **EN KRİTİK** - Şu anki acil aksiyon planı  
**İçerik:**
- Partner Center Sync aktifleştirme (Hamle 1)
- Dynamics 365 Push entegrasyonu (Hamle 2)
- UI Polish (Hamle 3)
- Hunter'ı gerçek ürüne dönüştürecek 3 kritik hamle

**Ne Zaman Bakılır:** Her gün - Şu anki öncelikli işler

---

### 2. **HUNTER-STATE-v1.0.md** ⭐⭐⭐
**Konum:** `docs/active/HUNTER-STATE-v1.0.md`  
**Önemi:** 🔥 **SİSTEM DURUMU** - Tek resmi durum dokümanı  
**İçerik:**
- Hunter v1.0 sistem durumu
- Core engine yetkinlikleri
- Feature durumları
- Production readiness durumu

**Ne Zaman Bakılır:** Sistem durumunu öğrenmek için

---

### 3. **CORE-FREEZE-D365-PUSH-PLAN.md** ⭐⭐⭐
**Konum:** `docs/archive/2025-01-30-CORE-FREEZE-D365-PUSH-PLAN.md` (Archived)  
**Önemi:** 🔥 **MİMARİ PLAN** - Core Freeze + D365 Push mimari planı  
**İçerik:**
- Core Freeze protokolü (CODEOWNERS, CI regression job, feature flags)
- D365 Push adapter pattern mimarisi
- 4 fazlı implementation planı (S + M + S-M + S)
- Core vs Integration fiziksel ayrımı
- Health check guardrails (D365 down olsa bile Hunter ready)

**Ne Zaman Bakılır:** D365 Push implementasyonu başlamadan önce ve sırasında (referans için arşivde)

---

### 4. **D365-PHASE-2.9-E2E-RUNBOOK.md** ⭐⭐
**Konum:** `docs/reference/D365-PHASE-2.9-E2E-RUNBOOK.md` (Reference)  
**Önemi:** D365 Phase 2.9 E2E wiring runbook  
**İçerik:**
- Tenant & App Registration (Azure AD + D365)
- Hunter config & feature flag setup
- Manual E2E tests (3 core senaryo)
- Error & rate limit senaryoları
- Go/No-Go gate (Dev → Prod)

**Ne Zaman Bakılır:** D365 tenant setup ve E2E test yaparken (reference guide)

---

### 5. **PRE-D365-ROAST-SPRINT-TASK-BOARD.md** ⭐⭐
**Konum:** `docs/archive/2025-01-30-PRE-D365-ROAST-SPRINT-TASK-BOARD.md` (Archived)  
**Önemi:** Pre-D365 hotfix sprint task board (✅ Completed)  
**İçerik:**
- 5 kritik fix (security, idempotency, token cache, session lifecycle, retry)
- Implementation details
- Test plans
- Decision log

**Ne Zaman Bakılır:** D365 entegrasyonu öncesi hotfix'leri referans almak için (arşivde)

---

## 🚀 **PRODUCTION REHBERLERİ** (Öncelik: P0 - Production için)

### 6. **PRODUCTION-DEPLOYMENT-GUIDE.md** ⭐⭐⭐
**Konum:** `docs/reference/PRODUCTION-DEPLOYMENT-GUIDE.md`  
**Önemi:** 🔥 **PRODUCTION DEPLOYMENT** - Adım adım rehber  
**İçerik:**
- Pre-deployment checks
- Deployment script usage
- Environment verification
- Backup & restore procedures
- Migration flow
- Smoke tests
- Rollback procedures

**Ne Zaman Bakılır:** Production'a deployment yaparken

---

### 7. **PRODUCTION-ENGINEERING-GUIDE-V1.md** ⭐⭐⭐
**Konum:** `docs/reference/PRODUCTION-ENGINEERING-GUIDE-V1.md`  
**Önemi:** 🔥 **SRE RUNBOOK** - Production operasyonları  
**İçerik:**
- Health checks & probes
- Monitoring & alerting
- Logging & observability
- Deployment strategies
- Incident response
- Runbook (common operations)

**Ne Zaman Bakılır:** Production operasyonları için

---

### 8. **PRODUCTION-DEPLOYMENT-CHECKLIST.md** ⭐⭐
**Konum:** `docs/reference/PRODUCTION-DEPLOYMENT-CHECKLIST.md`  
**Önemi:** Pre-deployment kontrol listesi  
**İçerik:**
- Pre-deployment checklist
- Deployment steps
- Smoke tests
- Post-deployment monitoring
- Rollback plan

**Ne Zaman Bakılır:** Deployment öncesi hızlı kontrol

---

### 9. **TROUBLESHOOTING-GUIDE.md** ⭐⭐
**Konum:** `docs/reference/TROUBLESHOOTING-GUIDE.md`  
**Önemi:** Sorun giderme rehberi  
**İçerik:**
- Common issues & solutions
- Database reset issues
- Script safety guards
- Error handling

**Ne Zaman Bakılır:** Sorun yaşandığında

---

## 📊 **STRATEJİ VE ROADMAP** (Öncelik: P1)

### 10. **G21-ROADMAP-CURRENT.md** ⭐⭐
**Konum:** `docs/active/G21-ROADMAP-CURRENT.md`  
**Önemi:** Mimari refactor roadmap  
**İçerik:**
- G21 architecture & integration roadmap
- Phase durumları
- Integration planları

**Ne Zaman Bakılır:** Mimari refactor planlaması için

---

### 11. **POST-MVP-STRATEGY.md** ⭐⭐
**Konum:** `docs/plans/2025-01-30-POST-MVP-STRATEGY.md`  
**Önemi:** v1.0 sonrası strateji  
**İçerik:**
- Post-MVP iş paketleri
- IP Enrichment
- Partner Center
- Dynamics 365

**Ne Zaman Bakılır:** v1.0 sonrası planlama için

---

### 12. **KALAN-ISLER-PRIORITY.md** ⭐
**Konum:** `docs/active/KALAN-ISLER-PRIORITY.md`  
**Önemi:** Kalan işler öncelik listesi  
**İçerik:**
- Öncelikli işler
- Task listesi

**Ne Zaman Bakılır:** Öncelik belirleme için

---

## 📖 **SATIŞ EKİBİ DOKÜMANTASYONU** (Öncelik: P1)

### 13. **SALES-GUIDE.md** ⭐⭐
**Konum:** `docs/sales/SALES-GUIDE.md`  
**Önemi:** Satış ekibi kullanım kılavuzu  
**İçerik:**
- Quick start
- API endpoints
- Scenarios
- Best practices

**Ne Zaman Bakılır:** Satış ekibi eğitimi için

---

### 14. **SEGMENT-GUIDE.md** ⭐⭐
**Konum:** `docs/sales/SEGMENT-GUIDE.md`  
**Önemi:** 🔥 **KANONİK KAYNAK** - Segment-Priority matrisi  
**İçerik:**
- Segment açıklamaları
- Priority açıklamaları
- Kanonik Segment-Priority Matrisi (Single Source of Truth)

**Ne Zaman Bakılır:** Segment ve priority anlamak için

---

### 15. **SALES-ENGINE-V1.1.md** ⭐
**Konum:** `docs/archive/2025-01-30-SALES-ENGINE-V1.1.md` (Archived)  
**Önemi:** Sales Engine v1.1 dokümantasyonu  
**İçerik:**
- Sales Engine intelligence layer
- CSP P-Model
- Commercial Segment & Heat

**Ne Zaman Bakılır:** Sales Engine detayları için (arşivde)

---

## 🛠️ **DEVELOPMENT REHBERLERİ** (Öncelik: P2)

### 16. **DEVELOPMENT-ENVIRONMENT.md** ⭐
**Konum:** `docs/reference/DEVELOPMENT-ENVIRONMENT.md`  
**Önemi:** Development environment setup  
**İçerik:**
- Development environment kurulumu
- Docker setup
- Database setup

**Ne Zaman Bakılır:** Development environment kurarken

---

### 17. **BRANCH-MANAGEMENT.md** ⭐
**Konum:** `docs/reference/BRANCH-MANAGEMENT.md`  
**Önemi:** Git branch stratejisi  
**İçerik:**
- Branch naming conventions
- Workflow
- Merge strategies

**Ne Zaman Bakılır:** Branch yönetimi için

---

## 📝 **ANA DOKÜMANTASYON** (Öncelik: P0 - Index)

### 16. **README.md** ⭐⭐⭐
**Konum:** `docs/README.md`  
**Önemi:** 🔥 **ANA İNDEX** - Dokümantasyon haritası  
**İçerik:**
- Documentation map (quick reference)
- Folder organization
- Documentation lifecycle
- Current status

**Ne Zaman Bakılır:** Hangi dokümana bakacağını bilmediğinde

---

### 18. **ACTIVE-STATUS-SUMMARY.md** ⭐⭐
**Konum:** `docs/ACTIVE-STATUS-SUMMARY.md`  
**Önemi:** 🔥 **AKTİF DOKÜMANTASYON DURUMU** - Güncel durum özeti  
**İçerik:**
- Active dosya sayısı ve durumu
- Kritik durumlar (Partner Center, D365, Core Freeze, UI)
- Dosya kategorileri
- Tutarlılık kontrolü
- Cleanup önerileri

**Ne Zaman Bakılır:** Dokümantasyon durumunu kontrol etmek için (güncel: 2025-01-30)

---

### 19. **DOCUMENTATION-STATUS-2025-01-29.md** ⭐
**Konum:** `docs/DOCUMENTATION-STATUS-2025-01-29.md`  
**Önemi:** Eski dokümantasyon durum raporu (tarihsel referans)  
**Not:** Güncel durum için `ACTIVE-STATUS-SUMMARY.md` dosyasına bakın

---

## 📋 **TODO VE ROADMAP** (Öncelik: P1)

### 20. **G21-architecture-refactor.md** ⭐
**Konum:** `docs/todos/G21-architecture-refactor.md`  
**Önemi:** G21 refactor TODO  
**İçerik:**
- G21 refactor task listesi
- Phase durumları

**Ne Zaman Bakılır:** G21 refactor takibi için

---

### 21. **INTEGRATION-ROADMAP.md** ⭐
**Konum:** `docs/todos/INTEGRATION-ROADMAP.md`  
**Önemi:** Integration roadmap TODO  
**İçerik:**
- Integration phase'leri
- Task listesi

**Ne Zaman Bakılır:** Integration takibi için

---

## 🎯 **ÖNCELİK SIRASI ÖZET**

### 🔥 **Günlük Kullanım (P0)**
1. `CRITICAL-3-HAMLE-PRODUCT-READY.md` - Şu anki acil aksiyon planı
2. `HUNTER-STATE-v1.0.md` - Sistem durumu
3. `PRODUCTION-DEPLOYMENT-GUIDE.md` - Production deployment
4. `PRODUCTION-ENGINEERING-GUIDE-V1.md` - SRE runbook
5. `docs/README.md` - Ana index

### ⚡ **Production İşlemleri (P0)**
- `PRODUCTION-DEPLOYMENT-GUIDE.md`
- `PRODUCTION-DEPLOYMENT-CHECKLIST.md`
- `PRODUCTION-ENGINEERING-GUIDE-V1.md`
- `TROUBLESHOOTING-GUIDE.md`
- `ROLLBACK-PLAN.md`
- `SMOKE-TESTS-RUNBOOK.md`

### 📊 **Strateji ve Planlama (P1)**
- `G21-ROADMAP-CURRENT.md` (Roadmap Mode - Prod Go/No-Go inactive)
- `POST-MVP-STRATEGY.md` (plans klasöründe)
- `KALAN-ISLER-PRIORITY.md` (Prod Go/No-Go inactive)
- `PRE-D365-ROAST-SPRINT-TASK-BOARD.md` (✅ Completed - Archived)
- `D365-PHASE-2.9-E2E-RUNBOOK.md` (Reference)

### 👥 **Satış Ekibi (P1)**
- `SALES-GUIDE.md`
- `SEGMENT-GUIDE.md` (Kanonik kaynak)
- `SALES-ENGINE-V1.1.md`

### 🛠️ **Development (P2)**
- `DEVELOPMENT-ENVIRONMENT.md`
- `BRANCH-MANAGEMENT.md`
- `DOCKER-TROUBLESHOOTING.md`

---

## 📌 **HIZLI REFERANS**

| Soru | Dosya |
|------|-------|
| "Şu an ne yapmalıyım?" | `CRITICAL-3-HAMLE-PRODUCT-READY.md` |
| "Hunter'ın durumu ne?" | `HUNTER-STATE-v1.0.md` |
| "Production'a nasıl deploy ederim?" | `PRODUCTION-DEPLOYMENT-GUIDE.md` |
| "Production'da sorun var, ne yapmalıyım?" | `TROUBLESHOOTING-GUIDE.md` |
| "Hangi dokümana bakmalıyım?" | `docs/README.md` |
| "Segment ve priority nedir?" | `SEGMENT-GUIDE.md` |
| "Satış ekibi nasıl kullanır?" | `SALES-GUIDE.md` |

---

**Son Güncelleme:** 2025-01-30 (Prod Go/No-Go inactive, roadmap moduna geçildi)  
**Not:** 
- `HAMLE-1-PRODUCTION-DEPLOYMENT.md` → Archive edildi (2025-01-30)
- `POST-MVP-STRATEGY.md` → Plans klasörüne taşındı (2025-01-30)
- Prod Go/No-Go dokümanları → Archive edildi (10 dosya - 2025-01-30)
- `CORE-FREEZE-D365-PUSH-PLAN.md` → Archive edildi (2025-01-30)
- `PRE-D365-ROAST-SPRINT-TASK-BOARD.md` → Archive edildi (2025-01-30)
- `SALES-ENGINE-V1.1.md` → Archive edildi (2025-01-30)
- `D365-PHASE-2.9-E2E-RUNBOOK.md` → Reference'a taşındı (2025-01-30)
- **Production Go/No-Go:** ⏸ INACTIVE - Altyapı dokümanları hazır (arşivde), aktif süreç değil. Odak: Feature development.

