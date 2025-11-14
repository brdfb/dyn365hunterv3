# Roadmap Kritik Değerlendirme - Sprint 2-6 Planı

**Tarih**: 2025-11-14  
**Değerlendiren**: Technical Review  
**Kapsam**: Sprint 2-6 planının teknik gerçekçilik, öncelik ve risk analizi

---

## 🔴 KRİTİK SORUNLAR

### 1. **Sprint 2: Priority Score Engine - GEREKSIZ DUPLİKASYON**

**Sorun:**
- Plan: "Priority Score Engine" → `lead_score`, `provider`, `risk_signals` → `priority_score`
- **GERÇEK:** Priority Score **ZATEN VAR** ve çalışıyor (`app/core/priority.py`)
- Mevcut implementasyon: `calculate_priority_score(segment, readiness_score)` → 1-6 arası skor
- Plan'da "yeni engine" deniyor ama mevcut sistem yeterli

**Etki:**
- Gereksiz iş yükü
- Scope creep
- Mevcut sistemin değeri göz ardı edilmiş

**Çözüm:**
- ❌ Sprint 2'den "Priority Score Engine" çıkar
- ✅ Mevcut priority score yeterli, sadece bulk scan'de kullanılacak
- ✅ Sprint 2'ye sadece bulk scan + async queue odaklan

**Önem:** 🔴 Yüksek - Gereksiz iş yükü

---

### 2. **Sprint 3: Contact Finder Engine - TEKNİK ZORLUK HAFİFE ALINMIŞ**

**Sorun:**
- Plan: "Domain → website → contact page → e-mail çıkartma"
- **GERÇEK:** Bu Hunter.io'nun core özelliği, çok karmaşık:
  - Web scraping (legal/ethical sorunlar)
  - Pattern generation (firstname.lastname, f.lastname vs.) - ML gerektirir
  - SMTP-check (zaten var ama contact finder için yeterli değil)
  - Rate limiting (web scraping için çok kritik)
  - Anti-bot koruması bypass (legal risk)

**Etki:**
- 1 sprint'te bitmez (2-3 sprint gerekir)
- Legal/ethical riskler
- Teknik borç artar
- Hunter.io ile rekabet (zaten var, neden yeniden yapıyoruz?)

**Çözüm:**
- ❌ Contact Finder'ı Sprint 3'ten çıkar
- ✅ Alternatif: Hunter.io API entegrasyonu (daha mantıklı)
- ✅ Veya: Contact Finder'ı Sprint 6+ (UI upgrade sonrası) yap
- ✅ Sprint 3'e odaklan: Webhook + Lead Enrichment (basit fields)

**Önem:** 🔴 Yüksek - Teknik zorluk + legal risk

---

### 3. **Sprint 4: PDF Account Summary - BAĞIMLILIK SORUNU**

**Sorun:**
- Plan: "PDF içinde Provider, SPF/DKIM/DMARC, Expiry, Signals, Migration Score, Priority Score, Risks, Recommendation (AI)"
- **GERÇEK:**
  - PDF generation: ReportLab/WeasyPrint gerekir (yeni dependency)
  - "Recommendation (AI)" → AI model gerektirir (çok büyük scope)
  - Template engine gerekir
  - Styling/formatting karmaşık

**Etki:**
- 1 sprint'te bitmez
- AI recommendation → çok büyük scope (ayrı sprint gerekir)
- PDF generation → yeni dependency + test yükü

**Çözüm:**
- ✅ PDF generation'ı basitleştir (AI olmadan)
- ✅ "Recommendation (AI)" → Sprint 6+ (ayrı özellik)
- ✅ Sprint 4: Notes/Tags/Favorites + Basit PDF (AI olmadan)

**Önem:** 🟡 Orta - Scope creep riski

---

### 4. **Sprint 5: Ready-to-Migrate Score v2 + AI - SCOPE CREEP**

**Sorun:**
- Plan: "Ready-to-Migrate Score v2 (AI-enhanced logic)"
- **GERÇEK:**
  - "AI-enhanced" → AI model gerektirir
  - Mevcut scoring sistemi zaten çalışıyor (`app/core/scorer.py`)
  - "v2" ne demek? Mevcut sistem yeterli değil mi?
  - Signal-based scoring zaten var (DKIM, SPF, DMARC)

**Etki:**
- AI scope → çok büyük (ayrı sprint gerekir)
- Mevcut scoring sistemi göz ardı edilmiş
- Gereksiz complexity

**Çözüm:**
- ❌ "AI-enhanced" kısmını çıkar
- ✅ Mevcut scoring sistemini iyileştir (signal-based zaten var)
- ✅ "v2" yerine "enhanced scoring" (AI olmadan)
- ✅ Sprint 5: ReScan Jobs + Alerts + Enhanced Scoring (AI olmadan)

**Önem:** 🟡 Orta - AI scope çok büyük

---

### 5. **Sprint 2: ReScan Infrastructure - ERKEN**

**Sorun:**
- Plan: Sprint 2'de "ReScan Infrastructure (Light-V1)"
- **GERÇEK:**
  - Bulk scan henüz yok (Sprint 2'de yapılacak)
  - ReScan için bulk scan'in çalışması gerekir
  - Change detection → schema değişikliği gerekir (history table)
  - "priority score değişti → notify" → notification engine gerekir (Sprint 5'te)

**Etki:**
- Bağımlılık sorunu (bulk scan önce bitmeli)
- Schema değişikliği gerekir (history table)
  - `provider_change_history` var ama yeterli değil
  - `score_change_history` gerekir
  - `signal_change_history` gerekir

**Çözüm:**
- ❌ ReScan Infrastructure'ı Sprint 2'den çıkar
- ✅ Sprint 3'e taşı (bulk scan bitince)
- ✅ Veya Sprint 5'e taşı (alerts ile birlikte mantıklı)

**Önem:** 🟡 Orta - Bağımlılık sorunu

---

## 🟡 ORTA ÖNCELİKLİ SORUNLAR

### 6. **Sprint 3: Lead Auto-Tagging V1 - SCHEMA DEĞİŞİKLİĞİ**

**Sorun:**
- Plan: "security-risk", "migration-ready", "expire-soon", "weak-spf", "google-workspace", "local-mx"
- **GERÇEK:**
  - Tags için schema değişikliği gerekir
  - `tags` tablosu veya `companies.tags` JSONB column
  - Auto-tagging logic → scorer.py'ye eklenmeli
  - Sprint 4'te "Tags CRUD" var → çakışma

**Etki:**
- Schema migration gerekir
- Sprint 3 ve Sprint 4'te tag işi var → çakışma

**Çözüm:**
- ✅ Auto-tagging'i Sprint 4'e taşı (Tags CRUD ile birlikte)
- ✅ Sprint 3: Webhook + Lead Enrichment (basit fields, tag yok)

**Önem:** 🟡 Orta - Schema değişikliği + çakışma

---

### 7. **Sprint 4: Auth Microsoft 365 - BAĞIMLILIK**

**Sorun:**
- Plan: "Auth Microsoft 365 work and school hesabı ile yapılacak"
- **GERÇEK:**
  - Microsoft Identity Platform entegrasyonu gerekir
  - OAuth 2.0 flow
  - Token validation
  - User management
  - Yeni dependency: `msal` veya `azure-identity`

**Etki:**
- 1 sprint'te bitmez (auth kompleks)
  - User table gerekir
  - Session management gerekir
  - Token refresh gerekir
- Favorites için auth gerekir ama Notes/Tags için gerekli değil

**Çözüm:**
- ✅ Auth'u basitleştir (Sprint 4'te sadece Favorites için)
- ✅ Notes/Tags → auth olmadan (public, takım içi)
- ✅ Auth → Sprint 6'ya taşı (UI upgrade ile birlikte)

**Önem:** 🟡 Orta - Auth kompleks, 1 sprint'te bitmez

---

## 🟢 DÜŞÜK ÖNCELİKLİ SORUNLAR

### 8. **Sprint 5: Daily ReScan Cron - SCHEDULER BAĞIMLILIĞI**

**Sorun:**
- Plan: "Daily ReScan cron"
- **GERÇEK:**
  - Cron job → scheduler gerektirir
  - `.cursorrules`'da scheduler **OUT OF SCOPE** olarak belirtilmiş
  - Celery beat veya APScheduler gerekir
  - Background worker gerekir

**Etki:**
- Scheduler infrastructure gerekir
- Sprint 2'de async queue kurulacak ama scheduler ayrı

**Çözüm:**
- ✅ Scheduler'ı Sprint 5'te ekle (Celery beat ile)
- ✅ Veya: Manual trigger endpoint (cron job external)

**Önem:** 🟢 Düşük - Scheduler zaten gerekli (async queue ile)

---

## 📊 DÜZELTİLMİŞ SPRINT PLANI

### Sprint 2: Bulk Scan + Async Queue (Temiz)

**Mevcut planlı işler:**
- ✅ Async queue (RQ / Celery / FastAPI background tasks)
- ✅ Rate-limit handling
- ✅ Timeout strategy
- ✅ Progress tracking (Redis / DB)
- ✅ Partial failure handling
- ✅ WebSocket / polling progress

**Çıkarılanlar:**
- ❌ Priority Score Engine (zaten var)
- ❌ ReScan Infrastructure (erken, Sprint 3/5'e taşı)

**Sprint 2 Output:**
- ✔ Bulk scan çalışıyor
- ✔ Background jobs çalışıyor
- ✔ Progress tracking çalışıyor

---

### Sprint 3: Webhook Ingestion + Lead Enrichment (Basitleştirilmiş)

**Mevcut planlı işler:**
- ✅ Webhook endpoint
- ✅ Auth (basit API key)
- ✅ Rate limit
- ✅ Payload validation
- ✅ Error retry handling

**Yeni özellikler (basitleştirilmiş):**
- ✅ Lead Enrichment Fields (basit):
  - `contact_emails[]` (manuel, webhook'tan gelir)
  - `contact_quality_score` (basit hesaplama)
  - `linkedin_pattern_generated` (basit pattern, ML yok)

**Çıkarılanlar:**
- ❌ Contact Finder Engine (çok karmaşık, Sprint 6+)
- ❌ Lead Auto-Tagging (Sprint 4'e taşı)
- ❌ SMTP-check (zaten var, contact finder için değil)

**Sprint 3 Output:**
- ✔ Webhook from anywhere
- ✔ Lead enrichment (basit fields)
- ✔ Veri akışı hazır

---

### Sprint 4: Notes / Tags / Favorites + Basit PDF (AI Olmadan)

**Mevcut plan:**
- ✅ Notes CRUD
- ✅ Tags CRUD (auto-tagging dahil)
- ✅ Favorites CRUD (auth olmadan, session-based)

**Yeni özellikler:**
- ✅ Lead Auto-Tagging V1 (Sprint 3'ten taşındı)
- ✅ Basit PDF Account Summary (AI olmadan):
  - Provider, SPF/DKIM/DMARC, Expiry, Signals
  - Migration Score, Priority Score, Risks
  - **AI Recommendation YOK** (Sprint 6+)

**Çıkarılanlar:**
- ❌ Auth Microsoft 365 (Sprint 6'ya taşı)
- ❌ AI Recommendation (Sprint 6+)

**Sprint 4 Output:**
- ✔ CRM-lite (notes, tags, favorites)
- ✔ Basit PDF (AI olmadan)
- ✔ Satışçı ekranı hazır

---

### Sprint 5: ReScan Jobs + Alerts + Enhanced Scoring (AI Olmadan)

**İşler:**
- ✅ ReScan Infrastructure (Sprint 2'den taşındı)
- ✅ Change detection (schema değişikliği: history tables)
- ✅ Daily ReScan cron (scheduler)
- ✅ Change triggers:
  - MX değişti
  - DMARC eklendi
  - Domain expire yaklaştı
- ✅ Notification engine (email, webhook, Slack)
- ✅ Enhanced Scoring (AI olmadan, signal-based iyileştirme)

**Çıkarılanlar:**
- ❌ Ready-to-Migrate Score v2 (AI-enhanced) → "Enhanced Scoring" (AI olmadan)
- ❌ AI Recommendation → Sprint 6+

**Sprint 5 Output:**
- ✔ Otomatik ReScan
- ✔ Change alerts
- ✔ Enhanced scoring (AI olmadan)

---

### Sprint 6: UI / Dashboard Upgrade + Auth + AI Features (Optional)

**İşler:**
- ✅ Lead table upgrade
- ✅ Filters upgrade
- ✅ Priority order
- ✅ PDF preview
- ✅ Score explanation
- ✅ Search
- ✅ Bulk upload UI
- ✅ Sales panel
- ✅ Auth Microsoft 365 (Sprint 4'ten taşındı)
- ✅ AI Recommendation (Sprint 4/5'ten taşındı)
- ✅ Contact Finder (Sprint 3'ten taşındı, optional)

**Sprint 6 Output:**
- ✔ Modern dashboard
- ✔ Auth sistemi
- ✔ AI features (optional)

---

## 🎯 ÖNEM SIRALAMASI

### 🔴 Yüksek Öncelik (Mutlaka Yapılmalı)

1. **Sprint 2: Bulk Scan + Async Queue** - Core altyapı
2. **Sprint 3: Webhook Ingestion** - Veri akışı
3. **Sprint 4: Notes/Tags/Favorites** - CRM-lite (satış için kritik)

### 🟡 Orta Öncelik (Yapılmalı Ama Esnek)

4. **Sprint 5: ReScan + Alerts** - Otomasyon (satış için faydalı)
5. **Sprint 4: Basit PDF** - Satış sunumu (faydalı ama kritik değil)

### 🟢 Düşük Öncelik (Nice to Have)

6. **Sprint 6: UI Upgrade** - UX iyileştirme
7. **Sprint 6: Auth Microsoft 365** - Güvenlik (favorites için gerekli ama ertelebilir)
8. **Sprint 6: AI Features** - Advanced features (optional)

---

## 💡 ÖNERİLER

### 1. **Scope Discipline**

- ❌ AI features'ı erken sprint'lere koyma (Sprint 6+)
- ❌ Contact Finder gibi kompleks özellikleri hafife alma
- ✅ Mevcut sistemleri kullan (Priority Score zaten var)
- ✅ Basit versiyonlarla başla (PDF AI olmadan, Auth basit)

### 2. **Bağımlılık Yönetimi**

- ✅ Bulk scan bitmeden ReScan yapma
- ✅ Tags CRUD bitmeden Auto-Tagging yapma
- ✅ Async queue bitmeden Scheduler yapma

### 3. **Teknik Borç vs Satış Değeri**

- ✅ Satış değeri yüksek özelliklere odaklan (Bulk Scan, Webhook, Notes/Tags)
- ❌ Teknik borç yaratacak özellikleri ertele (Contact Finder, AI)

### 4. **Sprint 2-3-4 → Core Sprint'ler**

**Doğru:** Sprint 2-3-4 gerçekten core sprint'ler:
- Sprint 2: Altyapı (bulk scan)
- Sprint 3: Veri akışı (webhook)
- Sprint 4: CRM-lite (notes/tags/favorites)

**Ama:**
- Sprint 2'den gereksiz özellikleri çıkar (Priority Score Engine, ReScan)
- Sprint 3'ten kompleks özellikleri çıkar (Contact Finder)
- Sprint 4'ten AI özelliklerini çıkar (PDF AI olmadan)

---

## 📋 FİNAL ÖNERİ

### ✅ YAPILMASI GEREKENLER

1. **Sprint 2'yi temizle:**
   - ❌ Priority Score Engine çıkar (zaten var)
   - ❌ ReScan Infrastructure çıkar (Sprint 5'e taşı)

2. **Sprint 3'ü basitleştir:**
   - ❌ Contact Finder çıkar (Sprint 6+)
   - ❌ Auto-Tagging çıkar (Sprint 4'e taşı)
   - ✅ Sadece Webhook + Basit Lead Enrichment

3. **Sprint 4'ü basitleştir:**
   - ❌ Auth Microsoft 365 çıkar (Sprint 6'ya taşı)
   - ❌ AI Recommendation çıkar (Sprint 6+)
   - ✅ Notes/Tags/Favorites + Basit PDF

4. **Sprint 5'i düzenle:**
   - ❌ AI-enhanced scoring çıkar
   - ✅ Enhanced scoring (AI olmadan)
   - ✅ ReScan + Alerts

5. **Sprint 6'ya taşı:**
   - ✅ Auth Microsoft 365
   - ✅ AI Features (optional)
   - ✅ Contact Finder (optional)
   - ✅ UI Upgrade

---

## 🎯 SONUÇ

**Plan'ın güçlü yanları:**
- ✅ Sprint 2-3-4 core sprint'ler olarak doğru belirlenmiş
- ✅ Satış değeri yüksek özelliklere odaklanılmış
- ✅ Mantıklı sıralama (altyapı → veri akışı → CRM-lite)

**Plan'ın zayıf yanları:**
- ❌ Scope creep (AI, Contact Finder erken sprint'lerde)
- ❌ Gereksiz duplikasyon (Priority Score Engine)
- ❌ Bağımlılık sorunları (ReScan erken)
- ❌ Teknik zorluk hafife alınmış (Contact Finder, Auth)

**Öneri:**
- ✅ Yukarıdaki düzeltmeleri uygula
- ✅ Sprint 2-3-4'ü temizle ve basitleştir
- ✅ Kompleks özellikleri Sprint 6+'ya taşı
- ✅ Mevcut sistemleri kullan (Priority Score zaten var)

---

**Son Güncelleme:** 2025-11-14  
**Durum:** Kritik değerlendirme tamamlandı, düzeltmeler önerildi

