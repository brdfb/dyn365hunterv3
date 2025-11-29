# Hunter — Post-MVP Strategy

**Versiyon:** v1.0 sonrası  
**Son Güncelleme:** 2025-01-30  
**Merkezi Roadmap**: `docs/active/DEVELOPMENT-ROADMAP.md` - Tüm aktif TODO'lar ve planlar

**Odak:** 3 ana iş paketi  

1) IP Enrichment Production Activation  

2) Partner Center Referrals Sync (G21 Phase 1)  

3) Dynamics 365 Sales Integration

---

## 1. IP Enrichment Production Activation — "Derinlik"

### 1.1. Durum

**✅ Implement Edilmiş** (2025-01-28)  
**✅ Production Activated** (2025-01-28) - Feature Flag: `HUNTER_ENRICHMENT_ENABLED=true`

IP Enrichment özelliği tamamen implement edilmiş ve production'da aktif. Feature flag açıldı, DB dosyaları kuruldu, validation testleri geçti.

**Not:** G20 Domain Intelligence Layer (Local Provider, Tenant Size, DMARC Coverage) ayrı bir özellik ve ✅ tamamlanmış durumda. IP Enrichment ile karıştırılmamalı.

### 1.2. Mevcut Durum

- ✅ **Core Implementation**: MaxMind, IP2Location, IP2Proxy entegrasyonları tamamlandı
- ✅ **Database Schema**: `ip_enrichment` tablosu ve migration hazır
- ✅ **Service Layer**: `enrichment_service.py` ile fire-and-forget pattern
- ✅ **IP Resolution**: MX records ve root domain'den otomatik IP çözümleme
- ✅ **Caching**: 24-hour TTL ile Redis-based caching
- ✅ **Thread Safety**: Thread-safe lazy loading
- ✅ **Graceful Degradation**: DB dosyaları yoksa crash olmuyor
- ✅ **Level 1 Exposure**: `infrastructure_summary` field API response'larda mevcut
- ✅ **Debug Endpoints**: `/debug/ip-enrichment/{ip}` ve `/debug/ip-enrichment/config`
- ✅ **Documentation**: Quick-start guide ve implementation docs hazır
- 🔄 **Production Activation**: Feature flag aktifleştirme ve validation bekliyor

### 1.3. Production Activation Scope

- Feature flag aktifleştirme (`HUNTER_ENRICHMENT_ENABLED=true`)
- DB dosyalarının production'a kurulumu (MaxMind, IP2Location, IP2Proxy)
- Production validation ve smoke tests
- Sales summary entegrasyonu doğrulama
- Monitoring ve alerting kurulumu
- Performance validation (cache hit rates, enrichment latency)

### 1.4. Out of Scope (Post–Post-MVP)

- Gerçek zamanlı IP reputation score

- Abuse/blacklist servisleri

- Otomatik risk-based throttling

### 1.5. Riskler

- DB update frekansı (MaxMind vs IP2Location) - ✅ Mitigated: Offline DB files, no network dependency
- Yanlış pozitif altyapı tahminleri - ✅ Mitigated: Graceful degradation, optional field
- Network gecikmesi - ✅ Mitigated: Offline DB files, caching, fire-and-forget pattern

### 1.6. Başarı Kriterleri

- ✅ Hunter sales summary içinde IP enrichment bilgisi görünür
- ✅ "Bu firma hangi tip altyapı kullanıyor?" sorusuna net cevap
- ✅ Tüm enrichment çağrıları **cache'lenmiş** ve stabil
- ✅ IP enrichment kapatılsa bile core scoring bozulmuyor (no-break upgrade)
- 🔄 Production'da feature flag aktif ve validation tamamlandı

---

## 2. Partner Center Referrals Sync (G21 Phase 1) — "Kaynak"

**Durum**: ✅ **COMPLETED** (2025-01-30) - Integration Roadmap Phase 2 tamamlandı

### 2.1. Amaç

Microsoft Partner Center'dan gelen **resmi referrals** verisini Hunter'a çekmek:

- Hunter'da domain sinyalleri ile birleştirmek,

- Satışçıya "bu zaten Microsoft tarafında da kayıtlı bir fırsat" diyebilmek.

### 2.2. Scope

- Auth stratejisi:

  - Service user (MFA'sız)

  - ROPC veya benzer app+user akışı

- Referrals API client:

  - Sadece okuma

  - Minimum alan: tenant ID, domain, company name, status

- Hunter DB tarafı:

  - Yeni tablo/view: `pc_referrals` (veya benzeri)

  - Domain bazlı merge

- Background job:

  - Günlük sync (Celery task)

  - Basit "delta" mantığı (created/updated sonrası güncelleme)

- Feature flag:

  - `PARTNER_CENTER_SYNC_ENABLED` (varsayılan OFF)

### 2.3. Out of Scope

- Partner Center üzerinden aksiyon almak (status update vs.)

- Multi-tenant / multi-partner senaryoları

- Co-sell / marketplace derin entegrasyonları

### 2.4. Riskler

- Auth flow değişiklikleri (Microsoft tarafı)

- Rate limit / quota yönetimi

- Tenant/domain eşleşme hataları

### 2.5. Başarı Kriterleri

- ✅ Günlük job sorunsuz çalışıyor (retry + logging ile) - Celery Beat schedule (10 min prod, 30s dev)

- ✅ Hunter lead ekranında:

  - ✅ "Bu domain Partner Center referral mı?" sorusuna net yanıt - Referral column with badges (co-sell: blue, marketplace: green, solution-provider: orange)
  - ✅ Referral type filter - "Sadece Partner Center gelenleri göster" filtresi
  - ✅ Sync button - Header'da "🔄 Partner Center Sync" butonu
  - ✅ Sync status indicator - "Son sync: X dk önce (OK/FAIL/queued)" göstergesi

- ✅ Partner Center kapalıyken Hunter core fonksiyonları tam çalışır (flag OFF)

**Tamamlanan Özellikler** (2025-01-30):
- ✅ Backend: API client, referral ingestion, sync endpoint, Celery task
- ✅ UI: Referral column, referral type filter, sync button, sync status indicator
- ✅ Background sync: Celery Beat schedule
- ✅ All tests passing (59/59 tests)
- ✅ Production-ready, feature flag OFF (MVP-safe)

---

## 3. Dynamics 365 Sales Integration — "Pipeline"

### 3.1. Amaç

Hunter'daki lead intelligence verisini:

- Dynamics 365 Sales pipeline'ına taşımak,

- Satışçının tek ekrandan çalışmasını sağlamak,

- Hunter'ı "akıllı sinyal motoru", D365'i "pipeline yöneticisi" yapmak.

### 3.2. Scope

- Data model mapping:

  - Hunter lead → D365 Lead/Contact/Account

  - Scoring / segment / priority → D365 alanları

- Entegrasyon katmanı:

  - Hunter → D365 push (primary)

  - Basit ack mekanizması

- Kullanım senaryosu:

  - Hunter UI'dan:

    - "Create/Update in Dynamics" aksiyonu

  - D365'te:

    - Hunter score'ları görünür (field veya panel)

### 3.3. Out of Scope

- Tam çift yönlü sync (D365 → Hunter full sync)

- Activity, task, appointment gibi CRM detay kurguları

- Gelişmiş workflow/Power Automate senaryoları

### 3.4. Riskler

- Field mapping karmaşıklığı

- Kullanıcı rolleri ve lisans modeli (Sales Pro vs Enterprise)

- API limitleri ve throttling

### 3.5. Başarı Kriterleri

- Hunter'daki bir lead, tek aksiyonla D365'te lead/opp olarak görülebiliyor.

- Sales ekibi:

  - Hunter'da analiz

  - D365'te takip/pipeline yönetimi

- Arızalı entegrasyon durumunda:

  - Hunter tarafı yine tek başına çalışabilir

  - Hata log'ları açık ve anlaşılır

---

## 4. DNS Analyzer Advanced Features — "Reliability" (Optional/Post-MVP)

### 4.1. Amaç

DNS analiz modülünün güvenilirliğini ve dayanıklılığını artırmak (opsiyonel iyileştirmeler):

- Geçici DNS hatalarında otomatik retry
- Daha robust DMARC parsing
- DNS server rotation/fallback mekanizması

### 4.2. Scope

**Faz 3 İyileştirmeleri** (Opsiyonel - Post-MVP - 2025-01-29'da planlandı):

- **7. Retry Mekanizması** (Configurable):
  - Geçici DNS timeout'larında otomatik retry (3 deneme, exponential backoff)
  - Sadece geçici hatalar için (Timeout, NoNameservers)
  - Configurable max timeout limiti (default: 30 saniye)
  - `tenacity` library ile implementasyon
  - **Not:** Yavaş domain'lerde gecikme yaratabilir, dikkatli implement edilmeli

- **8. DMARC Parsing İyileştirmesi** (Test Coverage ile):
  - Daha robust regex-based parsing
  - Edge case handling (malformed records, multiple policies)
  - Comprehensive test coverage
  - Mevcut davranışı koruyarak iyileştirme
  - **Not:** Edge case'lerde farklı sonuç verebilir, test coverage kritik

- **9. DNS Server Rotation** (Fallback olarak):
  - Deterministic rotation veya fallback pattern
  - Public DNS server'lar arasında otomatik geçiş
  - Cache farklılıklarını minimize etme
  - Sadece fallback olarak kullanım (primary DNS başarısız olursa)
  - **Not:** Bazı domain'lerde farklı sonuç verebilir (cache farkları)

### 4.3. Out of Scope

- Async DNS support (büyük refactoring gerektirir)
- Custom DNS server configuration (UI gerekli)
- DNS query batching/parallelization

### 4.4. Riskler

- Retry mekanizması yavaş domain'lerde gecikme yaratabilir
- DNS server rotation bazı domain'lerde farklı sonuç verebilir (cache farkları)
- DMARC parsing değişikliği edge case'lerde farklı sonuç verebilir

### 4.5. Başarı Kriterleri

- Geçici DNS hatalarında otomatik recovery
- DNS query başarı oranı artışı (timeout'lar azalır)
- DMARC parsing daha doğru ve robust
- Mevcut davranış korunur (backward compatible)

### 4.6. Durum

- ✅ **Faz 1 & Faz 2 Tamamlandı** (2025-01-29):
  - Error logging ✅
  - Metrics tracking ✅
  - Code quality improvements ✅
  - Resolver caching ✅
  - Cache invalidation ✅
- ⏳ **Faz 3 Opsiyonel - Post-MVP'ye Bırakıldı**:
  - 7. Retry mekanizması (configurable)
  - 8. DMARC parsing iyileştirmesi (test coverage ile)
  - 9. DNS server rotation (fallback olarak)

**Not:** Faz 1 ve Faz 2 iyileştirmeleri production-ready ve backward-compatible. Faz 3 özellikleri **opsiyonel** olarak post-MVP sprint'inde değerlendirilecek. İhtiyaç duyulursa implement edilecek.

---

## 5. Öncelik Sırası (Execution Order)

1. **IP Enrichment Production Activation** — XS/S  

   - ✅ Zaten implement edilmiş ve production-ready
   - ✅ Level 1 exposure mevcut (`infrastructure_summary` field)
   - 🔄 Sadece feature flag aktifleştirme ve validation gerekiyor
   - Kısa sürede "kalite hissi" artırır

2. **Partner Center Referrals Sync** — S/M ✅ **COMPLETED** (2025-01-30)

   - ✅ Hunter'a resmi kaynak kazandırır

   - ✅ Domain datasını daha anlamlı yapar

   - ✅ UI entegrasyonu tamamlandı (referral filter, sync button, sync status)

3. **Dynamics 365 Sales Integration** — M/L  

   - Ürün → Gerçek satış pipeline entegrasyonu

   - Doğrudan ticari değer

4. **DNS Analyzer Advanced Features** — S/M (Optional)

   - Güvenilirlik ve dayanıklılık artışı
   - Geçici hatalarda otomatik recovery
   - Daha robust parsing ve fallback mekanizmaları
   - **Not:** Opsiyonel - İhtiyaç duyulursa implement edilecek

5. **Mini UI Advanced Improvements** — S/M (Optional)

   - Skeleton loading (HTML + CSS + JS)
   - Keyboard navigation (event handling, focus management)
   - LRU cache (breakdown cache optimization)
   - Toast queue management
   - ARIA + focus trap (accessibility improvements)
   - **Not:** Detaylar için `docs/active/MINI-UI-REFACTOR-PACKAGE-1.md` (Paket 2) - Post-MVP'ye ertelendi
   - **Not:** Paket 1 (escapeHtml refactor, constants extraction, domain validation) ✅ tamamlandı (2025-01-30)

---

## 6. Özet

- ✅ Hunter v1.0 core engine hazır.
- ✅ G20 Domain Intelligence Layer tamamlandı (Local Provider, Tenant Size, DMARC Coverage)
- ✅ IP Enrichment implement edilmiş, production activation bekliyor
- ✅ DNS Analyzer Faz 1 & Faz 2 tamamlandı (2025-01-29) - Error logging, metrics, performance improvements
- Post-MVP odağı: **derinlik** (IP Enrichment activation), **kaynak** (Partner Center), **pipeline** (D365), **reliability** (DNS advanced features).
- Tüm işler feature flag'ler ve adapter mantığıyla, core engine'i bozmadan ilerlemeli.

