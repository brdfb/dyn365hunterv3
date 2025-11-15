# P1 API Versioning Hazırlığı

**Tarih**: 2025-01-28  
**Durum**: Hazırlık Tamamlandı  
**Amaç**: API versioning için zemin hazırlamak (read-only analiz)

---

## 📋 Router Listesi

### Toplam: 14 Router

| # | Router Modülü | Router Adı | Prefix | Açıklama |
|---|--------------|------------|--------|----------|
| 1 | `health` | `health.router` | `/` | Health check endpoints |
| 2 | `auth` | `auth.router` | `/auth` | Microsoft SSO authentication (G19) |
| 3 | `ingest` | `ingest.router` | `/ingest` | Domain/CSV/Webhook ingestion |
| 4 | `scan` | `scan.router` | `/scan` | Single domain scan, bulk scan |
| 5 | `leads` | `leads.router` | `/leads` | Leads query, export |
| 6 | `dashboard` | `dashboard.router` | `/dashboard` | Dashboard statistics |
| 7 | `email_tools` | `email_tools.router` | `/email` | Email generation, validation |
| 8 | `progress` | `progress.router` | `/jobs` | Progress tracking |
| 9 | `admin` | `admin.router` | `/admin` | Admin operations |
| 10 | `notes` | `notes.router` | `/notes` | Notes CRUD (G17) |
| 11 | `tags` | `tags.router` | `/tags` | Tags CRUD (G17) |
| 12 | `favorites` | `favorites.router` | `/favorites` | Favorites CRUD (G17) |
| 13 | `pdf` | `pdf.router` | `/leads/{domain}/summary.pdf` | PDF summary generation (G17) |
| 14 | `rescan` | `rescan.router` | `/scan` | Rescan endpoints (G18) |
| 15 | `alerts` | `alerts.router` | `/alerts` | Alerts system (G18) |

**NOT**: `rescan.router` ve `scan.router` aynı prefix'i kullanıyor (`/scan`) - bu versioning'de dikkat edilmeli.

---

## 🔍 Router Detay Analizi

### 1. health.router
- **Prefix**: `/` (root)
- **Endpoints**:
  - `GET /healthz` - Health check
  - `GET /healthz/ready` - Readiness probe
  - `GET /healthz/live` - Liveness probe
- **Versioning**: Health check endpoint'leri genelde versioning'e dahil edilmez (infrastructure)

### 2. auth.router
- **Prefix**: `/auth`
- **Endpoints**:
  - `GET /auth/login` - Microsoft SSO login
  - `GET /auth/callback` - OAuth callback
  - `GET /auth/logout` - Logout
  - `GET /auth/me` - Current user info
- **Versioning**: Auth endpoint'leri genelde versioning'e dahil edilmez (authentication infrastructure)

### 3. ingest.router
- **Prefix**: `/ingest`
- **Endpoints**:
  - `POST /ingest/domain` - Single domain ingestion
  - `POST /ingest/csv` - CSV/Excel ingestion
  - `POST /ingest/webhook` - Webhook ingestion (API key auth)
- **Versioning**: ✅ Versioning'e dahil edilmeli

### 4. scan.router
- **Prefix**: `/scan`
- **Endpoints**:
  - `POST /scan/domain` - Single domain scan
  - `POST /scan/bulk` - Bulk scan
  - `GET /scan/bulk/{job_id}` - Bulk scan status
- **Versioning**: ✅ Versioning'e dahil edilmeli

### 5. leads.router
- **Prefix**: `/leads`
- **Endpoints**:
  - `GET /leads` - Leads query (with filters)
  - `GET /leads/{domain}` - Single lead query
  - `GET /leads/export` - CSV/Excel export
- **Versioning**: ✅ Versioning'e dahil edilmeli

### 6. dashboard.router
- **Prefix**: `/dashboard`
- **Endpoints**:
  - `GET /dashboard` - Dashboard statistics
- **Versioning**: ✅ Versioning'e dahil edilmeli

### 7. email_tools.router
- **Prefix**: `/email`
- **Endpoints**:
  - `POST /email/generate` - Generate generic emails
  - `POST /email/generate-and-validate` - Generate and validate emails
- **Versioning**: ✅ Versioning'e dahil edilmeli

### 8. progress.router
- **Prefix**: `/jobs`
- **Endpoints**:
  - `GET /jobs/{job_id}` - Job progress
- **Versioning**: ✅ Versioning'e dahil edilmeli

### 9. admin.router
- **Prefix**: `/admin`
- **Endpoints**:
  - Admin operations (API key management, etc.)
- **Versioning**: ✅ Versioning'e dahil edilmeli

### 10. notes.router
- **Prefix**: `/notes`
- **Endpoints**:
  - `POST /notes` - Create note
  - `GET /notes/{domain}` - Get notes for domain
  - `PUT /notes/{note_id}` - Update note
  - `DELETE /notes/{note_id}` - Delete note
- **Versioning**: ✅ Versioning'e dahil edilmeli

### 11. tags.router
- **Prefix**: `/tags`
- **Endpoints**:
  - `POST /tags` - Add tag
  - `GET /tags/{domain}` - Get tags for domain
  - `DELETE /tags/{domain}/{tag}` - Remove tag
- **Versioning**: ✅ Versioning'e dahil edilmeli

### 12. favorites.router
- **Prefix**: `/favorites`
- **Endpoints**:
  - `POST /favorites` - Add favorite
  - `GET /favorites` - Get favorites
  - `DELETE /favorites/{domain}` - Remove favorite
- **Versioning**: ✅ Versioning'e dahil edilmeli

### 13. pdf.router
- **Prefix**: `/leads/{domain}/summary.pdf`
- **Endpoints**:
  - `GET /leads/{domain}/summary.pdf` - Generate PDF summary
- **Versioning**: ✅ Versioning'e dahil edilmeli

### 14. rescan.router
- **Prefix**: `/scan`
- **Endpoints**:
  - `POST /scan/{domain}/rescan` - Single domain rescan
  - `POST /scan/bulk/rescan` - Bulk rescan
- **Versioning**: ✅ Versioning'e dahil edilmeli
- **NOT**: `scan.router` ile aynı prefix (`/scan`) - versioning'de dikkat edilmeli

### 15. alerts.router
- **Prefix**: `/alerts`
- **Endpoints**:
  - `GET /alerts` - Get alerts
  - `POST /alerts/config` - Configure alerts
- **Versioning**: ✅ Versioning'e dahil edilmeli

---

## 🔄 Versioning Stratejisi

### API Version Structure

**Yeni Yapı:**
```
/api/v1/ingest/domain
/api/v1/scan/domain
/api/v1/leads
/api/v1/dashboard
...
```

**Legacy Yapı (Backward Compatibility):**
```
/ingest/domain
/scan/domain
/leads
/dashboard
...
```

### Router Registration Strategy

**Mevcut (app/main.py):**
```python
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(ingest.router)
app.include_router(scan.router)
# ... 14 router
```

**Yeni (app/main.py):**
```python
# Health and auth (no versioning)
app.include_router(health.router)
app.include_router(auth.router)

# Versioned API routers
from app.api.v1 import (
    ingest as ingest_v1,
    scan as scan_v1,
    leads as leads_v1,
    # ... other routers
)

# V1 routers
v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(ingest_v1.router, prefix="/ingest", tags=["ingest"])
v1_router.include_router(scan_v1.router, prefix="/scan", tags=["scan"])
# ... other routers
app.include_router(v1_router)

# Legacy routers (backward compatibility)
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(scan.router, prefix="/scan", tags=["scan"])
# ... other routers
```

---

## 🔙 Backward Compatibility Planı

### Dual-Path Routing

**Strateji**: Hem `/api/v1/...` hem de `/...` endpoint'leri çalışacak

**Örnek:**
- Yeni: `GET /api/v1/leads?segment=Migration`
- Legacy: `GET /leads?segment=Migration`
- Her ikisi de aynı handler'ı kullanacak (proxy pattern)

**Kod Örneği:**
```python
# app/api/v1/leads.py
from app.api.leads import get_leads as _get_leads

@router.get("/leads")
async def get_leads_v1(...):
    """V1 endpoint - proxy to legacy handler."""
    return await _get_leads(...)

# app/api/leads.py (legacy)
@router.get("/leads")
async def get_leads(...):
    """Legacy endpoint - will be deprecated."""
    # ... implementation ...
```

### Deprecation Strategy

**Timeline:**
- **v1.1 Release**: `/api/v1/...` endpoint'leri aktif, legacy endpoint'ler çalışmaya devam eder
- **v1.2 Release**: Legacy endpoint'ler deprecated warning döner (6 ay sonra)
- **v2.0 Release**: Legacy endpoint'ler kaldırılır (12 ay sonra)

**Deprecation Header:**
```python
@router.get("/leads", deprecated=True)
async def get_leads(...):
    """Legacy endpoint - use /api/v1/leads instead."""
    response = await get_leads_v1(...)
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "2026-01-28"  # 12 months from now
    return response
```

---

## 🚀 Zero Downtime Deployment Planı

### Deployment Stratejisi

**Adım 1: V1 Router'ları Ekle (Legacy Çalışmaya Devam Eder)**
```python
# app/main.py
# V1 routers ekle
v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(ingest_v1.router, prefix="/ingest")
app.include_router(v1_router)

# Legacy routers hala çalışıyor
app.include_router(ingest.router, prefix="/ingest")
```

**Adım 2: Test**
- Her iki endpoint'i test et
- Response'ların aynı olduğunu doğrula

**Adım 3: Client Migration**
- Client'ları `/api/v1/...` endpoint'lerine migrate et
- Legacy endpoint'ler çalışmaya devam eder

**Adım 4: Deprecation (6 ay sonra)**
- Legacy endpoint'ler deprecated warning döner
- Client'lar migrate olur

**Adım 5: Removal (12 ay sonra)**
- Legacy endpoint'ler kaldırılır
- Sadece `/api/v1/...` endpoint'leri kalır

---

## 📊 Router Mapping Tablosu (Eski → Yeni Path)

| Eski Path | Yeni Path (v1) | Router | Notes |
|-----------|---------------|--------|-------|
| `GET /healthz` | `GET /healthz` | health | No versioning (infrastructure) |
| `GET /auth/login` | `GET /auth/login` | auth | No versioning (authentication) |
| `POST /ingest/domain` | `POST /api/v1/ingest/domain` | ingest | Versioned |
| `POST /ingest/csv` | `POST /api/v1/ingest/csv` | ingest | Versioned |
| `POST /ingest/webhook` | `POST /api/v1/ingest/webhook` | ingest | Versioned |
| `POST /scan/domain` | `POST /api/v1/scan/domain` | scan | Versioned |
| `POST /scan/bulk` | `POST /api/v1/scan/bulk` | scan | Versioned |
| `GET /scan/bulk/{job_id}` | `GET /api/v1/scan/bulk/{job_id}` | scan | Versioned |
| `POST /scan/{domain}/rescan` | `POST /api/v1/scan/{domain}/rescan` | rescan | Versioned |
| `POST /scan/bulk/rescan` | `POST /api/v1/scan/bulk/rescan` | rescan | Versioned |
| `GET /leads` | `GET /api/v1/leads` | leads | Versioned |
| `GET /leads/{domain}` | `GET /api/v1/leads/{domain}` | leads | Versioned |
| `GET /leads/export` | `GET /api/v1/leads/export` | leads | Versioned |
| `GET /dashboard` | `GET /api/v1/dashboard` | dashboard | Versioned |
| `POST /email/generate` | `POST /api/v1/email/generate` | email_tools | Versioned |
| `POST /email/generate-and-validate` | `POST /api/v1/email/generate-and-validate` | email_tools | Versioned |
| `GET /jobs/{job_id}` | `GET /api/v1/jobs/{job_id}` | progress | Versioned |
| `POST /notes` | `POST /api/v1/notes` | notes | Versioned |
| `GET /notes/{domain}` | `GET /api/v1/notes/{domain}` | notes | Versioned |
| `PUT /notes/{note_id}` | `PUT /api/v1/notes/{note_id}` | notes | Versioned |
| `DELETE /notes/{note_id}` | `DELETE /api/v1/notes/{note_id}` | notes | Versioned |
| `POST /tags` | `POST /api/v1/tags` | tags | Versioned |
| `GET /tags/{domain}` | `GET /api/v1/tags/{domain}` | tags | Versioned |
| `DELETE /tags/{domain}/{tag}` | `DELETE /api/v1/tags/{domain}/{tag}` | tags | Versioned |
| `POST /favorites` | `POST /api/v1/favorites` | favorites | Versioned |
| `GET /favorites` | `GET /api/v1/favorites` | favorites | Versioned |
| `DELETE /favorites/{domain}` | `DELETE /api/v1/favorites/{domain}` | favorites | Versioned |
| `GET /leads/{domain}/summary.pdf` | `GET /api/v1/leads/{domain}/summary.pdf` | pdf | Versioned |
| `GET /alerts` | `GET /api/v1/alerts` | alerts | Versioned |
| `POST /alerts/config` | `POST /api/v1/alerts/config` | alerts | Versioned |

---

## ⚠️ Özel Durumlar ve Dikkat Edilmesi Gerekenler

### 1. scan.router ve rescan.router Aynı Prefix
- **Sorun**: Her ikisi de `/scan` prefix'i kullanıyor
- **Çözüm**: Versioning'de aynı prefix'i koru, endpoint path'leri farklı:
  - `/api/v1/scan/domain` (scan.router)
  - `/api/v1/scan/{domain}/rescan` (rescan.router)
  - `/api/v1/scan/bulk` (scan.router)
  - `/api/v1/scan/bulk/rescan` (rescan.router)

### 2. pdf.router Özel Path
- **Path**: `/leads/{domain}/summary.pdf`
- **Versioning**: `/api/v1/leads/{domain}/summary.pdf`
- **NOT**: PDF endpoint'i leads router'ına dahil edilebilir

### 3. Health ve Auth Endpoint'leri
- **Strateji**: Versioning'e dahil edilmez (infrastructure endpoint'leri)
- **Neden**: Health check ve authentication genelde versioning'e dahil edilmez

### 4. OpenAPI Docs Güncelleme
- **Strateji**: OpenAPI docs'u version bilgisi ile güncelle
- **Path**: `/docs` (v1) ve `/docs` (legacy) ayrı ayrı gösterilebilir

---

## ✅ Hazırlık Checklist

- [x] Router listesi çıkarıldı (14 router)
- [x] Her router'ın endpoint'leri dokümante edildi
- [x] Router bağımlılıkları kontrol edildi (scan/rescan aynı prefix)
- [x] Versioning stratejisi hazırlandı (`/api/v1/...` yapısı)
- [x] Backward compatibility planı dokümante edildi (dual-path routing)
- [x] Zero downtime deployment planı hazırlandı
- [x] Router mapping tablosu oluşturuldu (eski → yeni path)

---

## 🚀 Sonraki Adımlar

1. **API v1 Dizin Yapısı Oluştur**
   - `app/api/v1/` dizini oluştur
   - Her router için v1 versiyonu oluştur

2. **V1 Router'ları Oluştur**
   - Her router için v1 versiyonu (proxy pattern)
   - Legacy handler'ları kullan

3. **Main.py Güncelle**
   - V1 router'ları ekle (`/api/v1/...`)
   - Legacy router'ları koru (backward compatibility)

4. **OpenAPI Docs Güncelle**
   - Version bilgisi ekle
   - Deprecation warning'leri ekle

5. **Test**
   - Her iki endpoint'i test et (v1 ve legacy)
   - Response'ların aynı olduğunu doğrula
   - Zero downtime deployment test et

---

**Referans**: `docs/active/P1-IMPLEMENTATION-PLAYBOOK.md` - API Versioning bölümü

