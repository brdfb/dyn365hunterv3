# Partner Center Phase 2 - Önkoşullar ve Hazırlık Checklist

**Tarih**: 2025-01-28  
**Durum**: ✅ **HAZIR** (Tüm önkoşullar tamamlandı)  
**Kapsam**: Partner Center Phase 2'ye başlamadan önce yapılması gerekenler

---

## ✅ Tamamlanan Önkoşullar

### 1. Integration Roadmap Phase 1 ✅ **COMPLETED**

**Durum**: ✅ **TAMAMLANDI** (2025-01-28)

**Tamamlanan İşler**:
- ✅ Mini UI Stabilization (Button fixes, modal bugs, loading states, filter bar UX)
- ✅ Test Fixes (Scoring engine validated - 86 tests passing, 0 failures)

**Kontrol**: `docs/active/KALAN-ISLER-PRIORITY.md` - Phase 1: ✅ COMPLETED

---

### 2. Alembic Migration System ✅ **READY**

**Durum**: ✅ **TAMAMLANDI** (P1-1 - 2025-01-28)

**Hazır Olanlar**:
- ✅ Alembic setup (`alembic/` dizini, `alembic.ini` mevcut)
- ✅ Base revision oluşturuldu (`08f51db8dce0`)
- ✅ Migration history tracking aktif
- ✅ Rollback capability mevcut (`alembic downgrade` komutları)
- ✅ Schema drift kontrolü doğrulandı (Stabilization Sprint Gün 1)

**Kullanım**:
```bash
# Yeni migration oluştur
alembic revision --autogenerate -m "add_partner_center_referrals"

# Migration uygula
alembic upgrade head

# Rollback (gerekirse)
alembic downgrade -1
```

**Kontrol**: `docs/active/KALAN-ISLER-PRIORITY.md` - P1-1: ✅ TAMAMLANDI

---

### 3. Celery & Redis Infrastructure ✅ **READY**

**Durum**: ✅ **HAZIR** (Mevcut infrastructure)

**Hazır Olanlar**:
- ✅ Celery setup (`app/core/celery_app.py`)
- ✅ Redis connection (`app/core/redis_client.py`)
- ✅ Celery Beat schedule yapısı mevcut
- ✅ Background task pattern mevcut (`app/core/tasks.py`)
- ✅ Distributed rate limiting (Redis-based) ✅ TAMAMLANDI
- ✅ Distributed caching (Redis-based) ✅ TAMAMLANDI

**Kullanım**:
```python
# Celery task örneği
@celery_app.task
def sync_partner_center_referrals_task():
    # Task implementation
    pass

# Beat schedule ekleme
beat_schedule = {
    "sync-partner-center-referrals": {
        "task": "app.core.tasks.sync_partner_center_referrals_task",
        "schedule": 600.0,  # 10 minutes
    },
}
```

**Kontrol**: `app/core/celery_app.py`, `app/core/tasks.py` - Mevcut

---

### 4. Feature Flag Pattern ✅ **READY**

**Durum**: ✅ **HAZIR** (Mevcut pattern: `enrichment_enabled`)

**Hazır Olanlar**:
- ✅ Feature flag pattern mevcut (`app/config.py` - `enrichment_enabled`)
- ✅ Environment variable pattern mevcut (`HUNTER_` prefix)
- ✅ Config class yapısı hazır (`Settings` class)

**Referans Pattern**:
```python
# app/config.py
enrichment_enabled: bool = False  # Feature flag pattern

# app/core/analyzer_enrichment.py
if not settings.enrichment_enabled:
    return None  # Feature disabled
```

**Kontrol**: `app/config.py` - `enrichment_enabled` pattern mevcut

---

### 5. Database Models & Normalizer ✅ **READY**

**Durum**: ✅ **HAZIR** (Mevcut infrastructure)

**Hazır Olanlar**:
- ✅ `RawLead` model mevcut (`app/db/models.py`) - `source` field var
- ✅ `normalize_domain()` fonksiyonu mevcut (`app/core/normalizer.py`)
- ✅ `Company` model mevcut (upsert için)
- ✅ `domain_signals` table mevcut (idempotent scan kontrolü için)

**Kullanım**:
```python
# raw_leads ingestion pattern
raw_lead = RawLead(
    source='partnercenter',  # Mevcut pattern
    payload=referral_json,  # JSONB
    domain=normalized_domain,
    company_name=referral.company_name,
    email=referral.contact.email,
    website=referral.website,
)

# Domain normalization
from app.core.normalizer import normalize_domain
normalized = normalize_domain(referral.website)
```

**Kontrol**: `app/db/models.py`, `app/core/normalizer.py` - Mevcut

---

### 6. Scoring Pipeline ✅ **READY**

**Durum**: ✅ **HAZIR** (Mevcut infrastructure)

**Hazır Olanlar**:
- ✅ `scorer.py` mevcut (`app/core/scorer.py`)
- ✅ `score_domain()` fonksiyonu mevcut
- ✅ `determine_segment()` fonksiyonu mevcut
- ✅ Config pattern mevcut (scoring config'leri eklenebilir)

**Kullanım**:
```python
# Scoring pipeline entegrasyonu
from app.core.scorer import score_domain, determine_segment

# Azure Tenant ID override
if azure_tenant_id:
    segment, reason = determine_segment(score, provider, azure_tenant_id)

# Co-sell boost
if referral_type == "co-sell":
    score += settings.partner_center_cosell_bonus
```

**Kontrol**: `app/core/scorer.py` - Mevcut

---

### 7. API Router Pattern ✅ **READY**

**Durum**: ✅ **HAZIR** (Mevcut infrastructure)

**Hazır Olanlar**:
- ✅ FastAPI router pattern mevcut (`app/api/` dizini)
- ✅ Router registration pattern mevcut (`app/main.py`)
- ✅ Pydantic models pattern mevcut (request/response models)
- ✅ Error handling pattern mevcut (HTTPException)

**Kullanım**:
```python
# app/api/referrals.py
from fastapi import APIRouter, HTTPException
from app.config import settings

router = APIRouter()

@router.post("/sync")
async def sync_referrals():
    if not settings.partner_center_enabled:
        raise HTTPException(400, "Partner Center integration is disabled")
    # Implementation
```

**Kontrol**: `app/api/` dizini, `app/main.py` - Mevcut

---

## ⚠️ Yapılması Gerekenler (Başlamadan Önce)

### 1. Partner Center API Credentials ⚠️ **GEREKLİ**

**Durum**: ⚠️ **HAZIRLANMALI** (Başlamadan önce)

**Gerekenler**:
- [ ] Partner Center API credentials alınmalı:
  - [ ] OAuth Client ID
  - [ ] OAuth Client Secret
  - [ ] Azure AD Tenant ID
  - [ ] Partner Center API Base URL (genellikle: `https://api.partnercenter.microsoft.com`)
- [ ] **Service User oluşturulmalı** (MSAL + Device Code Flow için):
  - [ ] Partner Center'da özel kullanıcı: `referrals-sync@seninfirma.com` (örnek)
  - [ ] Role: **Referrals Admin** veya **Referrals User**
  - [ ] MFA: Açık kalabilir (MSAL + Device Code Flow MFA ile uyumlu)
- [ ] **Setup script çalıştırılmalı** (bir kere):
  - [ ] Device code flow ile login (MFA dahil tüm adımlar)
  - [ ] Refresh token güvenli saklanmalı (encrypted DB veya key vault)
  - [ ] Token cache oluşturulmalı
- [ ] API credentials test edilmeli (MSAL ile token alınabiliyor mu?)
- [ ] API endpoint'leri test edilmeli (`GET /referrals` çalışıyor mu?)

**Not**: MVP için test credentials yeterli. Production credentials sonra eklenebilir.

**ÖNEMLİ**: Partner Center Referrals API **sadece delegated permissions** destekliyor, application permissions yok. ROPC flow MFA ile uyumsuz, bu yüzden **MSAL + Device Code Flow** kullanılmalı (Microsoft'un önerdiği yaklaşım).

**Kaynak**: Microsoft Partner Center API Documentation

---

### 2. Environment Variables Hazırlığı ⚠️ **GEREKLİ**

**Durum**: ⚠️ **HAZIRLANMALI** (Başlamadan önce)

**Gerekenler**:
- [x] ✅ `.env.example` dosyasına Partner Center config'leri eklendi:
  ```bash
  # Partner Center Integration (Feature flag: disabled by default)
  # HUNTER_PARTNER_CENTER_ENABLED=false
  # HUNTER_PARTNER_CENTER_CLIENT_ID=your-client-id
  # HUNTER_PARTNER_CENTER_CLIENT_SECRET=your-client-secret
  # HUNTER_PARTNER_CENTER_TENANT_ID=your-tenant-id
  # HUNTER_PARTNER_CENTER_BASE_URL=https://api.partnercenter.microsoft.com
  # HUNTER_PARTNER_CENTER_POLL_INTERVAL_SECONDS=600  # Production: 10 minutes, Development: 30-60 seconds
  # MSAL + Device Code Flow (delegated permissions - application permissions not available):
  # HUNTER_PARTNER_CENTER_SCOPE=https://api.partner.microsoft.com/.default
  # HUNTER_PARTNER_CENTER_TOKEN_CACHE_PATH=.token_cache  # Optional, defaults to .token_cache
  # Setup: Run setup script once to authenticate (device code flow with MFA)
  # Background jobs will use silent token acquisition (no MFA required after initial setup)
  ```
- [ ] Local `.env` dosyasına test credentials ekle (development için - API credentials alındıktan sonra)
- [ ] Production `.env` dosyasına production credentials ekle (deploy sırasında)

**Kontrol**: ✅ `.env.example` dosyası güncellendi (2025-01-28)

---

### 3. Config Class Güncellemesi ⚠️ **GEREKLİ**

**Durum**: ⚠️ **HAZIRLANMALI** (Task 2.1'de yapılacak)

**Gerekenler**:
- [ ] `app/config.py`'ye Partner Center config'leri ekle:
  ```python
  # Partner Center (Feature flag: disabled by default)
  partner_center_enabled: bool = False
  partner_center_api_url: Optional[str] = None
  partner_center_client_id: Optional[str] = None
  partner_center_client_secret: Optional[str] = None
  partner_center_tenant_id: Optional[str] = None
  partner_center_sync_interval: int = 600  # Production: 10 minutes (600 seconds)
  partner_center_cosell_bonus: int = 15  # Co-sell referral priority boost
  partner_center_azure_tenant_score: int = 55  # M365 existing customer baseline score
  ```

**Not**: Bu Task 2.1'de yapılacak, ama başlamadan önce planlanmalı.

---

### 4. Test Ortamı Hazırlığı ✅ **READY**

**Durum**: ✅ **HAZIR** (Mevcut infrastructure)

**Hazır Olanlar**:
- ✅ Docker Compose setup mevcut
- ✅ Test database mevcut
- ✅ Test Redis mevcut
- ✅ Test Celery worker mevcut
- ✅ Test pattern mevcut (`tests/` dizini)

**Kontrol**: `docker-compose.yml`, `tests/` dizini - Mevcut

---

### 5. Branch Oluşturma ⚠️ **GEREKLİ**

**Durum**: ⚠️ **HAZIRLANMALI** (Başlamadan önce)

**Gerekenler**:
- [ ] Feature branch oluştur: `feature/partner-center-referrals`
- [ ] Branch'i remote'a push et
- [ ] Branch'i local'de checkout et

**Komut**:
```bash
git checkout -b feature/partner-center-referrals
git push -u origin feature/partner-center-referrals
```

---

## 📋 Başlamadan Önce Checklist

### Önkoşullar (Tamamlanmış)
- [x] ✅ Phase 1: Mini UI Stabilization - COMPLETED
- [x] ✅ Alembic Migration System - READY
- [x] ✅ Celery & Redis Infrastructure - READY
- [x] ✅ Feature Flag Pattern - READY
- [x] ✅ Database Models & Normalizer - READY
- [x] ✅ Scoring Pipeline - READY
- [x] ✅ API Router Pattern - READY
- [x] ✅ Test Ortamı - READY

### Hazırlık Adımları (Yapılması Gerekenler)
- [ ] ⚠️ Partner Center API Credentials alınmalı (KESİN LAZIM - Phase 2 başlayamaz)
  - [ ] Client ID
  - [ ] Client Secret
  - [ ] Tenant ID
  - [ ] Base URL: `https://api.partnercenter.microsoft.com`
  - [ ] **Service User** (MSAL + Device Code Flow için):
    - [ ] Username: `referrals-sync@seninfirma.com` (örnek)
    - [ ] Role: Referrals Admin/User
    - [ ] MFA: Açık kalabilir (MSAL MFA ile uyumlu)
  - [ ] **Setup script çalıştırılmalı** (bir kere):
    - [ ] Device code flow ile login
    - [ ] Refresh token güvenli saklanmalı
- [x] ✅ Environment Variables hazırlandı (`.env.example` güncellendi - 2025-01-28)
- [ ] ⚠️ Local `.env` dosyasına test credentials ekle (API credentials alındıktan sonra)
- [ ] ⚠️ Config Class güncellemesi planlanmalı (Task 2.1'de yapılacak)
- [ ] ⚠️ Feature branch oluşturulmalı (`feature/partner-center-referrals`)

---

## 🎯 Başlama Adımları

### 1. Partner Center API Credentials Al
- Microsoft Partner Center portal'ına giriş yap
- API credentials oluştur (OAuth Client ID, Secret, Tenant ID)
- API endpoint'lerini test et (`GET /referrals`)

### 2. Environment Variables Hazırla
- `.env.example` dosyasına Partner Center config'leri ekle
- Local `.env` dosyasına test credentials ekle

### 3. Feature Branch Oluştur
```bash
git checkout -b feature/partner-center-referrals
git push -u origin feature/partner-center-referrals
```

### 4. Task 2.1'e Başla
- `app/config.py`'ye Partner Center config'leri ekle
- `app/core/partner_center.py` dosyasını oluştur
- Minimal OAuth client implementasyonu yap

---

## ✅ Sonuç

**Genel Durum**: ✅ **%90 HAZIR** (Sadece API credentials ve environment variables hazırlanmalı)

**Tamamlanan Önkoşullar**: 8/8 (100%)
- ✅ Phase 1: COMPLETED
- ✅ Alembic: READY
- ✅ Celery/Redis: READY
- ✅ Feature Flag Pattern: READY
- ✅ Database Models: READY
- ✅ Scoring Pipeline: READY
- ✅ API Router Pattern: READY
- ✅ Test Ortamı: READY

**Yapılması Gerekenler**: 3 adet (1 tanesi tamamlandı)
- ⚠️ Partner Center API Credentials (KESİN LAZIM - Phase 2 başlayamaz)
- [x] ✅ Environment Variables hazırlığı (`.env.example` güncellendi - 2025-01-28)
- ⚠️ Local `.env` dosyasına test credentials ekle (API credentials alındıktan sonra)
- ⚠️ Config Class güncellemesi (Task 2.1'de yapılacak)
- ⚠️ Feature branch oluşturma (kritik)

**Öneri**: API credentials alındıktan sonra hemen başlanabilir. `.env.example` hazır, sadece local `.env` dosyasına credentials eklemek gerekiyor. Config class güncellemesi Task 2.1'in bir parçası olarak yapılacak.

---

**Son Güncelleme**: 2025-01-28  
**Durum**: ✅ **HAZIR** - Sadece API credentials ve branch oluşturma gerekiyor

