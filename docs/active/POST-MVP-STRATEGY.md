# Hunter — Post-MVP Strategy

**Versiyon:** v1.0 sonrası  

**Odak:** 3 ana iş paketi  

1) IP Enrichment (G20)  

2) Partner Center Referrals Sync (G21 Phase 1)  

3) Dynamics 365 Sales Integration

---

## 1. IP Enrichment (G20) — "Derinlik"

### 1.1. Amaç

Hunter'ın zaten sahip olduğu IP bazlı bilgiyi:

- Daha zengin,

- Daha tutarlı,

- Satışçı için gerçekten anlamlı

hale getirmek. Amaç "tool olmak" değil, **satış içgörüsü üretmek**.

### 1.2. Scope

- MaxMind, IP2Location, IP2Proxy entegrasyonlarının netleştirilmesi

- Ortak bir **IP Enrichment Service** katmanı:

  - Input: IP (veya inferred IP)

  - Output: `infrastructure_summary` + structured alanlar

- Hunter API'de:

  - Sales summary içinde tutarlı gösterim

  - Gerektiğinde ayrı bir "IP enrichment details" endpoint'i

- Feature flag:

  - `IP_ENRICHMENT_ENABLED` (ON/OFF)

- Quick-start dokümanının production seviyesine çıkarılması:

  - Kurulum

  - Lisans/DB dosyaları

  - Test komutları

### 1.3. Out of Scope (Post–Post-MVP)

- Gerçek zamanlı IP reputation score

- Abuse/blacklist servisleri

- Otomatik risk-based throttling

### 1.4. Riskler

- DB update frekansı (MaxMind vs IP2Location)

- Yanlış pozitif altyapı tahminleri

- Network gecikmesi (offline DB ile minimize edilmeli)

### 1.5. Başarı Kriterleri

- Hunter sales summary içinde:

  - "Bu firma hangi tip altyapı kullanıyor?" sorusuna net cevap

- Tüm enrichment çağrıları **cache'lenmiş** ve stabil

- IP enrichment kapatılsa bile core scoring bozulmuyor

---

## 2. Partner Center Referrals Sync (G21 Phase 1) — "Kaynak"

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

- Günlük job sorunsuz çalışıyor (retry + logging ile)

- Hunter lead ekranında:

  - "Bu domain Partner Center referral mı?" sorusuna net yanıt

- Partner Center kapalıyken Hunter core fonksiyonları tam çalışır (flag OFF)

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

## 4. Öncelik Sırası (Execution Order)

1. **IP Enrichment (G20)** — XS/S  

   - Zaten Level 1 exposure var

   - Kısa sürede "kalite hissi" artırır

2. **Partner Center Referrals Sync** — S/M  

   - Hunter'a resmi kaynak kazandırır

   - Domain datasını daha anlamlı yapar

3. **Dynamics 365 Sales Integration** — M/L  

   - Ürün → Gerçek satış pipeline entegrasyonu

   - Doğrudan ticari değer

---

## 5. Özet

- Hunter v1.0 core engine hazır.

- Post-MVP odağı: **derinlik** (IP), **kaynak** (Partner Center), **pipeline** (D365).

- Tüm işler feature flag'ler ve adapter mantığıyla, core engine'i bozmadan ilerlemeli.

