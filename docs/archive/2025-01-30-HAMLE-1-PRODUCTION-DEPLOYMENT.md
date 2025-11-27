# 🚀 HAMLE 1: Partner Center - Production Deployment

**Tarih**: 2025-01-30  
**Durum**: Dev'de çalışıyor → Production'a deploy  
**Hedef**: Gerçek referral'ları production'da görmek

---

## 🎯 **KARAR**

**Öneri**: Production'a deploy et, gerçek referral'ları gör, sonra Hamle 2'ye geç.

**Neden**:
1. Gerçek data ile D365 mapping'i daha doğru yapılır
2. Production'da sorun varsa şimdi görürüz
3. Hamle 2'ye geçmeden önce veri kalitesini doğrulamak önemli

---

## 📋 **PRODUCTION DEPLOYMENT CHECKLIST**

### **Phase 1: Pre-Deployment** (30 dakika)

#### 1.1. Git Tag & Branch

```bash
# Son commit'leri push'la
git push origin feature/partner-center-phase1

# Production için merge et (main/master branch'e)
# veya feature branch'i production'a merge et
```

#### 1.2. Production Environment Variables

**Production `.env` dosyasında kontrol et**:

```bash
# Partner Center Integration
HUNTER_PARTNER_CENTER_ENABLED=true
HUNTER_PARTNER_CENTER_CLIENT_ID=<production-client-id>
HUNTER_PARTNER_CENTER_TENANT_ID=<production-tenant-id>
HUNTER_PARTNER_CENTER_API_URL=https://api.partner.microsoft.com
HUNTER_PARTNER_CENTER_SCOPE=https://api.partner.microsoft.com/.default
HUNTER_PARTNER_CENTER_TOKEN_CACHE_PATH=.token_cache
HUNTER_PARTNER_CENTER_SYNC_INTERVAL=600  # Production: 10 minutes
```

**Kontrol Listesi**:
- [ ] `HUNTER_PARTNER_CENTER_ENABLED=true` (production'da açık)
- [ ] `HUNTER_PARTNER_CENTER_CLIENT_ID` dolu (production Azure AD App)
- [ ] `HUNTER_PARTNER_CENTER_TENANT_ID` dolu (production tenant)
- [ ] Diğer config'ler doğru

#### 1.3. Azure AD App Registration (Production)

**Azure Portal → Azure Active Directory → App Registrations**

**Kontrol Listesi**:
- [ ] Production App Registration var mı?
- [ ] API Permissions → Partner Center API permissions granted mi?
- [ ] Admin consent granted mi? (delegated permissions için gerekli)
- [ ] Redirect URI configured (Device Code Flow için gerekli değil ama kontrol et)

---

### **Phase 2: Initial Authentication (Production)** (15 dakika)

#### 2.1. Device Code Flow (Production)

**Production server'da**:

```bash
# Production container'a bağlan
docker-compose exec api python scripts/partner_center_device_code_flow.py
```

**Adımlar**:
1. Browser'da authentication yap (verification URI + user code)
2. Token cache oluşturulacak: `.token_cache` (production server'da)
3. Token cache dosyasının production'da kalıcı olduğundan emin ol (volume mount)

**Kontrol**:
- [ ] Token cache oluşturuldu mu? (`ls -la .token_cache`)
- [ ] Token cache production server'da kalıcı mı? (volume mount kontrolü)

---

### **Phase 3: Deployment** (30 dakika)

#### 3.1. Database Backup

**CRITICAL**: Her zaman backup al!

```bash
# Production database backup
pg_dump -h <prod-db-host> -U <user> -d <database> \
  > backups/backup_pre_partner_center_$(date +%Y%m%d_%H%M%S).sql

# Backup integrity check
grep -q "PostgreSQL database dump" backups/backup_pre_partner_center_*.sql && \
  echo "✅ Backup valid" || echo "❌ Backup invalid"
```

#### 3.2. Migration Check

```bash
# Current migration version
docker-compose exec api alembic current

# Expected: Head migration includes partner_center_referrals table
# Migration: 622ba66483b9_add_partner_center_referrals.py
```

**Kontrol**:
- [ ] Migration `622ba66483b9` applied mı? (`alembic current`)
- [ ] `partner_center_referrals` table var mı?

#### 3.3. Deploy Application

**Option 1: Deployment Script (Recommended)**

```bash
# Dry-run first
ENVIRONMENT=production FORCE_PRODUCTION=yes \
  bash scripts/deploy_production.sh --dry-run

# Real deployment
ENVIRONMENT=production FORCE_PRODUCTION=yes \
  bash scripts/deploy_production.sh
```

**Option 2: Manual Deployment**

```bash
# Pull latest code
git pull origin main  # veya production branch

# Restart containers
docker-compose restart api worker beat

# Check health
curl http://localhost:8000/healthz | jq '.partner_center_enabled'
# Expected: true
```

---

### **Phase 4: Post-Deployment Validation** (30 dakika)

#### 4.1. Health Check

```bash
# API health
curl http://<prod-url>/healthz | jq '.partner_center_enabled'
# Expected: true

# API endpoint test
curl -X POST http://<prod-url>/api/v1/partner-center/referrals/sync \
  -H "Content-Type: application/json" \
  -s | jq '.'
# Expected: {"success": true, "task_id": "...", ...}
```

#### 4.2. Manual Sync Test

```bash
# Production'da manual sync
curl -X POST http://<prod-url>/api/v1/partner-center/referrals/sync \
  -H "Content-Type: application/json"

# Worker log'larını kontrol et
docker-compose logs --tail=100 worker | grep partner_center
```

**Beklenen**:
- ✅ Sync task başarıyla çalıştı
- ✅ `success_count > 0` veya `skipped_count > 0` (referral'lar işlendi)

#### 4.3. Database Validation

```bash
# Production database'de referral'lar var mı?
docker-compose exec postgres psql -U <user> -d <database> -c \
  "SELECT COUNT(*) FROM partner_center_referrals;"

# İlk 5 referral
docker-compose exec postgres psql -U <user> -d <database> -c \
  "SELECT referral_id, referral_type, company_name, domain, status, synced_at \
   FROM partner_center_referrals \
   ORDER BY synced_at DESC LIMIT 5;"
```

**Beklenen**:
- ✅ `COUNT(*) > 0` (en az 1 referral var)
- ✅ `referral_type` değerleri: `co-sell`, `marketplace`, `solution-provider`
- ✅ `domain` değerleri dolu (gerçek domain'ler)

#### 4.4. UI Validation

**Production Mini UI**: http://<prod-url>/mini-ui/

**Kontrol Listesi**:
- [ ] Sync button çalışıyor mu?
- [ ] Referral badge'leri görünüyor mu? (gerçek lead'lerde)
- [ ] Sync status indicator çalışıyor mu?

---

## 🚨 **TROUBLESHOOTING**

### Problem: "Token acquisition failed"
**Çözüm**:
```bash
# Production'da token cache'i sil ve Phase 2'yi tekrar çalıştır
rm .token_cache
docker-compose exec api python scripts/partner_center_device_code_flow.py
```

### Problem: "Feature flag disabled"
**Çözüm**:
- Production `.env` dosyasında `HUNTER_PARTNER_CENTER_ENABLED=true` kontrol et
- API container'ı restart et: `docker-compose restart api`

### Problem: "No referrals found"
**Çözüm**:
- Partner Center'da gerçekten referral var mı kontrol et (Azure Portal)
- Filter rules çok sıkı olabilir (direction=Incoming, status=Active/New)
- Log'larda `skipped_reasons` kontrol et

### Problem: "Database migration missing"
**Çözüm**:
```bash
# Migration'ı uygula
docker-compose exec api alembic upgrade head

# Migration version kontrol et
docker-compose exec api alembic current
```

---

## ✅ **BAŞARI KRİTERLERİ**

### Minimum Viable:
- ✅ Production'da feature flag açık
- ✅ Token cache oluşturuldu
- ✅ Manual sync başarılı (en az 1 referral sync edildi)
- ✅ Database'de gerçek referral'lar var
- ✅ UI'da referral badge'leri görünüyor

### Production Ready:
- ✅ Background sync otomatik çalışıyor (10 min interval)
- ✅ Gerçek referral'lar sync ediliyor
- ✅ Error handling robust (sistem çökmedi)

---

## 🎯 **SONRAKI ADIM**

Production deployment tamamlandığında:
- ✅ Gerçek referral'lar production'da görünüyor
- ✅ Veri kalitesi doğrulandı
- ✅ Hamle 2'ye geçilebilir (Dynamics 365 Push)

**Hamle 2'de kullanılacak**:
- Gerçek referral data ile D365 mapping
- `is_partner_center_referral`, `referral_type`, `referral_status` alanları

---

## 📚 **REFERANS**

- `docs/reference/PRODUCTION-DEPLOYMENT-GUIDE.md` - Genel production deployment
- `docs/reference/PARTNER-CENTER-PRODUCTION-CHECKLIST.md` - Partner Center production checklist
- `docs/active/HAMLE-1-EXECUTION-RUNBOOK.md` - Dev execution runbook
- `scripts/deploy_production.sh` - Deployment script

