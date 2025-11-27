# Core Freeze + D365 Push Architecture Plan

**Tarih:** 2025-01-30  
**Durum:** Planlama - Execution Ready  
**Hedef:** Core'u kutsal alan yapma + D365 push katmanını yan taraftan takma

---

## 🎯 **GENEL YAKLAŞIM**

### İki Ana Prensip

1. **Core Freeze Pack** — Hunter Altar'ı koruma (dokunulmaz çekirdek)
2. **D365 Push Adapter** — Üzerine D365 push katmanını "yan taraftan" takma

---

## 1. CORE FREEZE PACK — Hunter Altar'ı Nasıl Koruyoruz?

**Durum:** Core zaten resmen production Go almış durumda: 497 test, P0/P1/P-Stabilization hepsi yeşil.

**Prensip:** Core'a dokunursak enayi oluruz, o yüzden "dokunma protokolü" uygulanacak.

---

### 1.1. Kodu Böl: Core vs Adapter

#### **Core (Freeze — Dokunulmaz)**

Aşağıdaki path'ler **"dokunulmaz"** olacak:

**Core Modüller:**
- `app/core/dns/` (yoksa `analyzer_dns.py`)
- `app/core/whois/` (yoksa `analyzer_whois.py`)
- `app/core/scorer.py`
- `app/core/enrichment.py` (veya `enrichment_service.py`)
- `app/core/sales_engine.py`
- `app/core/normalizer.py`
- `app/core/provider_map.py`
- `app/core/priority.py`
- `app/core/priority_category.py`
- `app/core/commercial.py`
- `app/core/technical_heat.py`

**Analyzer Modülleri:**
- `app/core/analyzer_*.py` (analyzer_dns, analyzer_whois, analyzer_enrichment)

**IP Enrichment:**
- `app/core/ip_enrichment/` (L1 zaten prod active)
- `app/core/enrichment_service.py` (IP enrichment service)

**CLI Komutları:**
- `cli/` içindeki mevcut komutlar

**Test Suite:**
- `tests/test_scorer_*.py`
- `tests/test_regression_dataset.py`
- `tests/test_sales_*.py`
- `tests/test_analyzer_*.py`

#### **Yeni Kod Yeri (D365 + Diğer Entegrasyonlar)**

**D365 Entegrasyonu:**
- `app/integrations/d365/` (yeni klasör)
  - `client.py` — D365 Web API client
  - `mapping.py` — Hunter → D365 DTO mapping
  - `dto.py` — D365 data transfer objects
  - `errors.py` — D365-specific exceptions
- `app/tasks/d365_push.py` — Celery task (yeni dosya)
- `app/api/v1/d365_routes.py` — Sadece yeni endpoint'ler
- `mini-ui/js/d365_actions.ts` (veya `.js`) — Frontend buton + state

**Diğer Entegrasyonlar (Gelecek):**
- `app/integrations/` — Tüm external entegrasyonlar burada

**Böylece "core" ile "entegrasyon" fiziksel olarak ayrılmış oluyor.**

---

### 1.2. Git / CI Seviyesi Koruma

#### **1. Branch Modeli**

- **`main`** = Sadece bugfix + prod ops
- **`feature/d365-push-v1`** = Bütün D365 işi burada
- **Core'da değişiklik gerekiyorsa:**
  - `core-hotfix/*` branch
  - PR üzerinde **"Hotfix Reason"** zorunlu text (template)

#### **2. CODEOWNERS**

`.github/CODEOWNERS` dosyası oluşturulacak:

```
# Core (Freeze Zone)
/app/core/scorer.py @bered
/app/core/analyzer_*.py @bered
/app/core/normalizer.py @bered
/app/core/provider_map.py @bered
/app/core/priority.py @bered
/app/core/sales_engine.py @bered
/app/core/enrichment*.py @bered
/app/core/ip_enrichment/ @bered
/tests/test_scorer_*.py @bered
/tests/test_regression_dataset.py @bered
/tests/test_sales_*.py @bered

# D365 Integration (Free to modify)
/app/integrations/d365/ @bered
/app/tasks/d365_push.py @bered
/app/api/v1/d365_routes.py @bered
```

**Not:** Core değişiklikleri için **2 reviewer** zorunlu (sen + 1 kişi).

#### **3. CI'de Ayrı "Core Regression Job"**

`.github/workflows/ci.yml` içinde:

```yaml
jobs:
  core-regression:
    name: Core Regression Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Core Regression Tests
        run: |
          pytest tests/test_scorer_*.py tests/test_regression_dataset.py tests/test_sales_*.py tests/test_analyzer_*.py -v
```

**Kural:** Bu job fail → merge yok. (Go/No-Go checklist'in CI versiyonu)

#### **4. Feature Flag Kuralı**

Yeni her şey (D365, Partner Center activation v2 vs) **flag altında**:

- `HUNTER_D365_ENABLED` (default: `false`)
- `PARTNER_CENTER_ENABLED` (zaten var, default: `false`)

**Prod'da default:** `false`. Core her durumda aynı davranmalı.

**Feature flag kontrolü:**
```python
# app/config.py
class Settings(BaseSettings):
    HUNTER_D365_ENABLED: bool = False
    HUNTER_PARTNER_CENTER_ENABLED: bool = False
```

---

### 1.3. Operasyonel Guardrail

Production Engineering Guide'daki health, logging, deployment kurallarına **D365 tarafını da uyduruyoruz**:

#### **D365 Entegrasyonu:**

- **Ayrı log context:** `d365_push`, PII'siz
- **Health check:** `/healthz/ready` içinde D365 bağımlılığı **yok** → D365 down olsa bile Hunter **ready**
- **Metrics:** Sadece `metrics`'te `d365_push_fail_total` gibi sayaçlar

**Örnek:**
```python
# app/api/v1/d365_routes.py
@router.post("/push-lead")
async def push_lead_to_d365(lead_id: int):
    if not settings.HUNTER_D365_ENABLED:
        raise HTTPException(403, "D365 integration disabled")
    # ...
```

**Health check:**
```python
# app/main.py
@router.get("/healthz/ready")
async def healthz_ready():
    # D365 check YOK - Core her zaman ready
    return {"status": "ready"}
```

**Bu şekilde D365 ne kadar çökerse çöksün, Hunter core **her zaman Ferrari** olarak kalıyor.**

---

## 2. D365 PUSH — Hedef Mimari (Üzerine Takılan Katman)

**Mimari:** UI → Hunter API (push endpoint) → Celery queue → D365 Adapter → D365 Web API

---

### 2.1. Akış (Step-by-Step)

#### **1. Kullanıcı UI'da lead satırında "Push to Dynamics" butonuna basar**

- **Request:** `POST /api/v1/d365/push-lead`
- **Body:** `{ "lead_id": 123 }` veya `{ "domain": "example.com" }`

#### **2. Hunter API**

- Lead'i DB'den okuyup minimal payload çıkarır:
  - `domain`
  - `company_name`
  - `segment`
  - `readiness_score`
  - `priority_score`
  - `provider`
  - `tenant_size`
  - `infrastructure_summary`
  - `is_partner_center_referral`
  - `referral_id`
- Celery task enqueue: `push_lead_to_d365.delay(lead_id)`
- Hemen `202 Accepted` döner + `job_id`

#### **3. Celery Task (D365 Adapter Entry)**

- Lead'i tekrar DB'den çeker (single source of truth)
- `app/integrations/d365/mapping.py` ile D365 DTO'ya çevirir:
  - D365 Lead fields + custom hunter field'ler:
    - `hunter_score`
    - `hunter_segment`
    - `hunter_priority`
    - `hunter_infrastructure`
    - `hunter_referral_id`
    - vb.
- D365 Web API'ye çağrı yapar (client credentials)

#### **4. D365'den Response**

**Success:**
- D365 Lead ID'yi kaydeder: `d365_lead_id`
- Lead satırına:
  - `d365_status = "synced"`
  - `d365_last_synced_at`

**Duplicate / Update Case:**
- Upsert (domain / email'e göre "alternate key" ile)

**Hata:**
- Retry policy (örn. 3 deneme, exponential backoff)
- `d365_status = "error"`, `d365_last_error` log

#### **5. UI Tarafı**

- `GET /api/v1/leads/{id}` zaten lead'i çekiyor. Bu response'a:
  - `d365_status`
  - `d365_last_synced_at`
  - `d365_lead_url` (isteğe bağlı) eklenir
- UI badge:
  - `Not Synced` / `Syncing` / `Synced` / `Error`

---

### 2.2. Yeni DB Alanları

#### **`leads` Tablosuna Minimal Ek:**

```sql
ALTER TABLE leads ADD COLUMN d365_lead_id VARCHAR(255) NULL;
ALTER TABLE leads ADD COLUMN d365_sync_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE leads ADD COLUMN d365_sync_last_at TIMESTAMP NULL;
ALTER TABLE leads ADD COLUMN d365_sync_error TEXT NULL;

-- Enum constraint (PostgreSQL)
CREATE TYPE d365_sync_status_enum AS ENUM ('pending', 'in_progress', 'synced', 'error');
ALTER TABLE leads ALTER COLUMN d365_sync_status TYPE d365_sync_status_enum USING d365_sync_status::d365_sync_status_enum;
```

**Not:** Bu tablo tamamen **adapter tarafına ait**, core scoring vs. ile ilişkisi yok.

#### **Audit İçin Hafif Tablo:**

```sql
CREATE TABLE d365_push_jobs (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER NOT NULL REFERENCES leads(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    attempt_count INTEGER DEFAULT 0,
    last_error TEXT NULL,
    d365_lead_id VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_d365_push_jobs_lead_id ON d365_push_jobs(lead_id);
CREATE INDEX idx_d365_push_jobs_status ON d365_push_jobs(status);
```

**Bu tablo tamamen **adapter tarafına ait**, core scoring vs. ile ilişkisi yok.**

---

### 2.3. D365 Client + Mapping

#### **`app/integrations/d365/client.py`**

```python
"""D365 Web API client."""
from typing import Optional, Dict, Any
import httpx
from app.config import settings

class D365Client:
    def __init__(self):
        self.base_url = settings.D365_BASE_URL
        self.client_id = settings.D365_CLIENT_ID
        self.client_secret = settings.D365_CLIENT_SECRET
        self.tenant_id = settings.D365_TENANT_ID
        self._token: Optional[str] = None
    
    async def get_token(self) -> str:
        """Get OAuth 2.0 token (client credentials)."""
        # Implementation: Azure AD token endpoint
        pass
    
    async def create_or_update_lead(
        self, 
        payload: Dict[str, Any], 
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create or update lead in D365."""
        # Implementation: D365 Web API call
        pass
```

**Ortak base URL, headers, telemetry.**

#### **`app/integrations/d365/mapping.py`**

```python
"""Pure functions, unit-test friendly."""
from typing import Dict, Any
from app.db.models import Lead

def map_lead_to_d365(lead: Lead) -> Dict[str, Any]:
    """Map Hunter lead to D365 Lead DTO."""
    return {
        "subject": f"Hunter: {lead.domain}",
        "companyname": lead.company_name or lead.domain,
        "emailaddress1": lead.primary_email,  # varsa
        "websiteurl": f"https://{lead.domain}",
        "hunter_score": lead.readiness_score,
        "hunter_segment": lead.segment,
        "hunter_priority": lead.priority_score,
        "hunter_infrastructure": lead.infrastructure_summary,
        "hunter_referral_id": lead.referral_id,
        # ...
    }
```

**Bu modül değişse bile core umursamıyor.**

---

## 3. D365 PUSH — Faz Bazlı İş Planı

Her faz için Execution Window veriyorum.

---

### **Faz 1 — Skeleton + Plumbing (S)**

**Hedef:** API endpoint + Celery task + boş D365 client.

**Tasks:**
- [ ] `POST /api/v1/d365/push-lead` (lead_id/domain alır, job başlatır)
- [ ] `push_lead_to_d365` Celery task (şimdilik sadece log yazar)
- [ ] `d365_sync_status` alanlarını ekleyen migration
- [ ] Basit unit test'ler

**Efor:** **S** (0.5–1 gün)

**Dosyalar:**
- `app/integrations/d365/__init__.py` (yeni klasör)
- `app/integrations/d365/client.py` (boş skeleton)
- `app/tasks/d365_push.py` (Celery task)
- `app/api/v1/d365_routes.py` (endpoint)
- `alembic/versions/XXXX_add_d365_sync_fields.py` (migration)

---

### **Faz 2 — D365 Client + Mapping (M)**

**Hedef:** Gerçekten D365'e lead gönderme.

**Tasks:**
- [ ] `client.py` (token, create/update)
- [ ] `mapping.py` (map_lead_to_d365)
- [ ] Retry + idempotency
- [ ] Testler:
  - Mapping unit tests
  - Client için mock-based tests
- [ ] `.env` + Prod Engineering Guide'a uygun secret yönetimi

**Efor:** **M** (~1 gün)

**Dosyalar:**
- `app/integrations/d365/client.py` (tam implementasyon)
- `app/integrations/d365/mapping.py` (tam implementasyon)
- `app/integrations/d365/dto.py` (DTOs)
- `app/integrations/d365/errors.py` (exceptions)
- `tests/test_d365_client.py`
- `tests/test_d365_mapping.py`

---

### **Faz 3 — UI & Status + Monitoring (S–M)**

**Hedef:** Satışçı için görülebilir hale getirmek.

**Tasks:**
- [ ] Lead tablosuna `D365` column (badge)
- [ ] Lead detail modal'a `D365 status` bölümü
- [ ] "Push to Dynamics" butonu (single + bulk)
- [ ] Metrics:
  - `d365_push_total`
  - `d365_push_fail_total`
- [ ] Sentry breadcrumb'ler (hangi lead, hangi status)

**Efor:** **S–M** (~1 gün)

**Dosyalar:**
- `mini-ui/js/d365_actions.js` (frontend logic)
- `mini-ui/index.html` (UI elements)
- `app/api/v1/leads.py` (d365_status field ekle)

---

### **Faz 4 — Hardening & Guardrails (S)**

**Hedef:** Çökerse core'a zarar vermesin.

**Tasks:**
- [ ] D365 down ise:
  - Task retry + exponential backoff
  - 3 fail sonrası `error` state, UI'da kırmızı badge
- [ ] `GO-NO-GO` fikrine paralel küçük bir **D365 mini-checklist**:
  - Token alınıyor mu?
  - Lead create çalışıyor mu?
  - Mapping testleri yeşil mi?

**Efor:** **S** (~0.5 gün)

**Toplam D365 v1 scope:** **M–L** bandı; 1 hafta civarı net bir sprintle biter.

---

## 4. IP ENRICHMENT LEVEL 2 NE ZAMAN?

**Sorun:** "Post-MVP G20'yi, D365'ten önce derinleştirmek mantıklı mı?"

**Cevap:** **Hayır, D365 v1 bitmeden L2'ye girme.**

**Neden:**
- L1 zaten production active ve hunter_state'de düzgün expose edilmiş durumda
- Post-MVP Strategy'de IP Enrichment "activation + polishing" diye konumlanmış; D365 ise direkt ticari değer yaratan modül
- D365 v1 çıktıktan sonra:
  - Hangi enrichment alanlarının D365'te gerçekten iş gördüğünü biliyor olacağız
  - L2'nin schema'sını D365 mapping'e göre kurgularız, tersi değil

**Dolayısıyla sıra:**
1. **Hamle 2:** D365 Push v1 (tek yönlü, create/update by domain)
2. **Hamle 3:** UI Polish (D365 aksiyonlarıyla birlikte)
3. **Sonra:** IP Enrichment L2 (D365'te gerçekten kullanılan field set'ine göre genişletme)

---

## 5. ÖZET

### **Core Freeze:**
- Core şu an zaten **"don't touch"** modunda; biz bunu branch + path + CI ile resmileştiriyoruz
- CODEOWNERS, CI regression job, feature flags ile koruma altında

### **D365 Adapter:**
- D365 entegrasyonu **tamamen adapter katmanı**; core'a dependency değil, core'un client'ı
- Fiziksel ayrım: `app/integrations/d365/` vs `app/core/`

### **Roadmap:**
- **D365 Push v1 → UI görünürlük → sonra L2 enrichment**

---

## 6. BAŞARI KRİTERLERİ

### **Core Freeze:**
- ✅ CODEOWNERS dosyası var ve çalışıyor
- ✅ CI'de core regression job var ve fail → merge yok
- ✅ Feature flags ile core korunuyor
- ✅ Health check'te D365 bağımlılığı yok

### **D365 Push v1:**
- ✅ Hunter'dan bir lead, tek tıkla D365'te lead olarak görünebiliyor
- ✅ Duplicate detection çalışıyor (upsert)
- ✅ Error handling robust (auth, rate limit, validation)
- ✅ UI'da sync butonu ve status çalışıyor
- ✅ D365 down olsa bile Hunter core çalışıyor

---

## 7. İLGİLİ DOKÜMANTASYON

- `CRITICAL-3-HAMLE-PRODUCT-READY.md` — Hamle 2 (D365 Push)
- `HUNTER-STATE-v1.0.md` — Core freeze durumu
- `G21-ROADMAP-CURRENT.md` — Mimari roadmap
- `INTEGRATION-ROADMAP.md` — Phase 3 (D365 Integration)

---

**Son Güncelleme:** 2025-01-30  
**Durum:** Planlama tamamlandı, execution'a hazır

