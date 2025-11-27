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
**Konum:** `docs/active/CORE-FREEZE-D365-PUSH-PLAN.md`  
**Önemi:** 🔥 **MİMARİ PLAN** - Core Freeze + D365 Push mimari planı  
**İçerik:**
- Core Freeze protokolü (CODEOWNERS, CI regression job, feature flags)
- D365 Push adapter pattern mimarisi
- 4 fazlı implementation planı (S + M + S-M + S)
- Core vs Integration fiziksel ayrımı
- Health check guardrails (D365 down olsa bile Hunter ready)

**Ne Zaman Bakılır:** D365 Push implementasyonu başlamadan önce ve sırasında

---

### 4. **HAMLE-1-PRODUCTION-DEPLOYMENT.md** ⭐⭐
**Konum:** `docs/active/HAMLE-1-PRODUCTION-DEPLOYMENT.md`  
**Önemi:** Partner Center production deployment planı  
**İçerik:**
- Partner Center feature flag aktifleştirme
- Production deployment adımları
- Test ve validation

**Ne Zaman Bakılır:** Partner Center'ı production'a çıkarırken

---

## 🚀 **PRODUCTION REHBERLERİ** (Öncelik: P0 - Production için)

### 4. **PRODUCTION-DEPLOYMENT-GUIDE.md** ⭐⭐⭐
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

### 5. **PRODUCTION-ENGINEERING-GUIDE-V1.md** ⭐⭐⭐
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

### 6. **PRODUCTION-DEPLOYMENT-CHECKLIST.md** ⭐⭐
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

### 7. **TROUBLESHOOTING-GUIDE.md** ⭐⭐
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

### 8. **G21-ROADMAP-CURRENT.md** ⭐⭐
**Konum:** `docs/active/G21-ROADMAP-CURRENT.md`  
**Önemi:** Mimari refactor roadmap  
**İçerik:**
- G21 architecture & integration roadmap
- Phase durumları
- Integration planları

**Ne Zaman Bakılır:** Mimari refactor planlaması için

---

### 9. **POST-MVP-STRATEGY.md** ⭐⭐
**Konum:** `docs/active/POST-MVP-STRATEGY.md`  
**Önemi:** v1.0 sonrası strateji  
**İçerik:**
- Post-MVP iş paketleri
- IP Enrichment
- Partner Center
- Dynamics 365

**Ne Zaman Bakılır:** v1.0 sonrası planlama için

---

### 10. **KALAN-ISLER-PRIORITY.md** ⭐
**Konum:** `docs/active/KALAN-ISLER-PRIORITY.md`  
**Önemi:** Kalan işler öncelik listesi  
**İçerik:**
- Öncelikli işler
- Task listesi

**Ne Zaman Bakılır:** Öncelik belirleme için

---

## 📖 **SATIŞ EKİBİ DOKÜMANTASYONU** (Öncelik: P1)

### 11. **SALES-GUIDE.md** ⭐⭐
**Konum:** `docs/sales/SALES-GUIDE.md`  
**Önemi:** Satış ekibi kullanım kılavuzu  
**İçerik:**
- Quick start
- API endpoints
- Scenarios
- Best practices

**Ne Zaman Bakılır:** Satış ekibi eğitimi için

---

### 12. **SEGMENT-GUIDE.md** ⭐⭐
**Konum:** `docs/sales/SEGMENT-GUIDE.md`  
**Önemi:** 🔥 **KANONİK KAYNAK** - Segment-Priority matrisi  
**İçerik:**
- Segment açıklamaları
- Priority açıklamaları
- Kanonik Segment-Priority Matrisi (Single Source of Truth)

**Ne Zaman Bakılır:** Segment ve priority anlamak için

---

### 13. **SALES-ENGINE-V1.1.md** ⭐
**Konum:** `docs/active/SALES-ENGINE-V1.1.md`  
**Önemi:** Sales Engine v1.1 dokümantasyonu  
**İçerik:**
- Sales Engine intelligence layer
- CSP P-Model
- Commercial Segment & Heat

**Ne Zaman Bakılır:** Sales Engine detayları için

---

## 🛠️ **DEVELOPMENT REHBERLERİ** (Öncelik: P2)

### 14. **DEVELOPMENT-ENVIRONMENT.md** ⭐
**Konum:** `docs/reference/DEVELOPMENT-ENVIRONMENT.md`  
**Önemi:** Development environment setup  
**İçerik:**
- Development environment kurulumu
- Docker setup
- Database setup

**Ne Zaman Bakılır:** Development environment kurarken

---

### 15. **BRANCH-MANAGEMENT.md** ⭐
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

### 17. **DOCUMENTATION-STATUS-2025-01-29.md** ⭐
**Konum:** `docs/DOCUMENTATION-STATUS-2025-01-29.md`  
**Önemi:** Dokümantasyon durum raporu  
**İçerik:**
- Cleanup işlemleri
- Güncellik durumu
- Archive durumu

**Ne Zaman Bakılır:** Dokümantasyon durumunu kontrol etmek için

---

## 📋 **TODO VE ROADMAP** (Öncelik: P1)

### 18. **G21-architecture-refactor.md** ⭐
**Konum:** `docs/todos/G21-architecture-refactor.md`  
**Önemi:** G21 refactor TODO  
**İçerik:**
- G21 refactor task listesi
- Phase durumları

**Ne Zaman Bakılır:** G21 refactor takibi için

---

### 19. **INTEGRATION-ROADMAP.md** ⭐
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
- `G21-ROADMAP-CURRENT.md`
- `POST-MVP-STRATEGY.md`
- `KALAN-ISLER-PRIORITY.md`

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

**Son Güncelleme:** 2025-01-30

