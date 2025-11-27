# 🔥 HAMLE 1: Partner Center Sync - EXECUTION RUNBOOK

**Tarih**: 2025-01-30  
**Durum**: Kritik Yol - Kopyala Yapıştır Komutlar  
**Hedef**: Partner Center'ı 2-2.5 saatte "gerçekten çalışan" hale getirmek

---

## 🎯 **KRİTİK YOL vs POST-ACTIVATION**

### ✅ **KRİTİK YOL** (İlk Oturuşta - 2-2.5 saat)
**Hedef**: "Partner Center canlı, referral'lar geliyor, UI'da görüyorum, sistem çökmeden dönüyor."

- Phase 1: Config + Credentials (30 dk)
- Phase 2: Initial Auth (15 dk)
- Phase 3: Manual Sync (30 dk)
- Phase 5 (Light): UI Validation - Sync button + Badge görünüyor mu? (15 dk)
- Phase 4 (Light): Background Sync - Beat çalışıyor mu? (15 dk)

**Toplam**: ~2 saat (ideal) / 2.5 saat (gerçekçi)

### 🎀 **POST-ACTIVATION** (Aynı gün veya sonraki gün)
- Phase 5 (Detay): Filter dropdown, tooltip'ler, inbox tab detayları
- Phase 6: Error scenarios, performance tests, data quality deep dive

---

## 🚀 **PHASE 1: CONFIGURATION & CREDENTIALS** (30 dakika)

### 1.1. `.env` Dosyasını Kontrol Et

**Dosya**: `.env` (proje root'unda)

**Komut**:
```bash
# .env dosyasını aç
code .env
# veya
notepad .env
```

**Kontrol Listesi**:
- [ ] `HUNTER_PARTNER_CENTER_ENABLED=true` var mı? (yoksa ekle)
- [ ] `HUNTER_PARTNER_CENTER_CLIENT_ID=` dolu mu? (Azure AD App Registration'dan)
- [ ] `HUNTER_PARTNER_CENTER_TENANT_ID=` dolu mu? (Azure AD Tenant ID)
- [ ] `HUNTER_PARTNER_CENTER_API_URL=https://api.partner.microsoft.com` var mı?

**Örnek `.env` Satırları**:
```bash
# Partner Center Integration
HUNTER_PARTNER_CENTER_ENABLED=true
HUNTER_PARTNER_CENTER_CLIENT_ID=1475ed28-175a-45f1-a299-e811147ad068
HUNTER_PARTNER_CENTER_TENANT_ID=aa72d1fe-d762-49f7-b721-c7611d0a6934
HUNTER_PARTNER_CENTER_API_URL=https://api.partner.microsoft.com
HUNTER_PARTNER_CENTER_SCOPE=https://api.partner.microsoft.com/.default
HUNTER_PARTNER_CENTER_TOKEN_CACHE_PATH=.token_cache
HUNTER_PARTNER_CENTER_SYNC_INTERVAL=600
```

**Not**: `HUNTER_PARTNER_CENTER_CLIENT_SECRET` **gerekli değil** (PublicClientApplication kullanılıyor)

---

### 1.2. Azure AD App Registration Kontrolü

**Azure Portal**: https://portal.azure.com → Azure Active Directory → App Registrations

**Kontrol Listesi**:
- [ ] App Registration var mı?
- [ ] `CLIENT_ID` doğru mu? (Application (client) ID)
- [ ] `TENANT_ID` doğru mu? (Directory (tenant) ID)
- [ ] API Permissions → Partner Center API permissions granted mi?
- [ ] Admin consent granted mi? (delegated permissions için gerekli)

**API Permissions Gerekli**:
- `https://api.partner.microsoft.com/.default` (delegated permission)
- Admin consent: **Required**

---

### 1.3. Docker Container'ları Restart Et

**Komut**:
```bash
# API container'ı restart et (config değişiklikleri için)
docker-compose restart api

# Container'ın çalıştığını kontrol et
docker-compose ps
```

**Beklenen Sonuç**:
```
NAME                STATUS
api                 Up (healthy)
worker              Up
beat                Up
```

---

## 🔐 **PHASE 2: INITIAL AUTHENTICATION** (15 dakika)

### 2.1. Device Code Flow Script Çalıştır

**Komut**:
```bash
docker-compose exec api python scripts/partner_center_device_code_flow.py
```

**Beklenen Çıktı**:
```
============================================================
Partner Center - Device Code Flow Authentication
============================================================

📱 Authentication Instructions:

1. Open your browser and go to:
   https://microsoft.com/devicelogin

2. Enter this code:
   ABC123XYZ

3. Complete the authentication (login + consent)
   (MFA will be required if enabled)

============================================================
⏳ Waiting for authentication...
   (This may take up to 15 minutes)
============================================================
```

**Yapılacaklar**:
1. Browser'da `https://microsoft.com/devicelogin` aç
2. User code'u gir (örn: `ABC123XYZ`)
3. Login + consent yap (MFA gerekirse yap)
4. Script otomatik devam edecek

**Başarılı Sonuç**:
```
✅ SUCCESS: Token acquired!

Token Information:
  - Expires in: 3600 seconds
  - Token type: Bearer
  - Scope: https://api.partner.microsoft.com/.default

Token cache saved to: .token_cache

✅ FAZ 2 PASSED: Authentication successful!

Next steps:
  1. Token cache is now available for silent token acquisition
  2. Background jobs can use silent token acquisition
  3. You can proceed to FAZ 3 (Feature Flag ON validation)
```

**Kontrol**:
```bash
# Token cache dosyası oluşturuldu mu?
ls -la .token_cache
# veya Windows'ta
dir .token_cache
```

**Beklenen**: `.token_cache` dosyası var ve boş değil

---

## 🔄 **PHASE 3: MANUAL SYNC TEST** (30 dakika)

### 3.1. Manual Sync Script Çalıştır

**Komut**:
```bash
docker-compose exec api python -m scripts.sync_partner_center
```

**Beklenen Çıktı**:
```
Partner Center sync completed:
  - Success: 15
  - Failed: 0
  - Skipped: 5
  - Total processed: 20
```

**Not**: Eğer `Success: 0, Failed: 0, Skipped: 0` görürsen:
- Feature flag kapalı olabilir → `.env` kontrol et
- Token cache yok olabilir → Phase 2'yi tekrar çalıştır
- Credentials yanlış olabilir → `.env` kontrol et

---

### 3.2. Database'de Kayıt Kontrolü

**Komut**:
```bash
# PostgreSQL container'a bağlan
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter
```

**SQL Sorguları**:
```sql
-- Toplam referral sayısı
SELECT COUNT(*) FROM partner_center_referrals;

-- İlk 5 referral
SELECT 
    referral_id,
    referral_type,
    company_name,
    domain,
    status,
    synced_at
FROM partner_center_referrals
ORDER BY synced_at DESC
LIMIT 5;

-- Referral type dağılımı
SELECT 
    referral_type,
    COUNT(*) as count
FROM partner_center_referrals
GROUP BY referral_type;

-- Exit
\q
```

**Beklenen Sonuç**:
- `COUNT(*)` > 0 (en az 1 referral var)
- `referral_type` değerleri: `co-sell`, `marketplace`, `solution-provider`
- `synced_at` timestamp'ler dolu

---

### 3.3. API Endpoint Test

**Komut**:
```bash
# Manual sync endpoint test
curl -X POST http://localhost:8000/api/referrals/sync \
  -H "Content-Type: application/json" \
  -v
```

**Beklenen Response**:
```json
{
  "success": true,
  "message": "Referral sync task enqueued. Check logs for results.",
  "enqueued": true,
  "task_id": "abc-123-def-456-789",
  "success_count": 0,
  "failure_count": 0,
  "skipped_count": 0,
  "errors": []
}
```

**Not**: `success_count: 0` normal (task async çalışıyor, sonuçlar log'larda)

---

### 3.4. Celery Worker Log Kontrolü

**Komut**:
```bash
# Worker log'larını takip et
docker-compose logs -f worker
```

**Aranacak Log Satırları**:
```
partner_center_sync_task_started
partner_center_sync_started
partner_center_referrals_fetched
partner_center_sync_summary
partner_center_sync_task_completed
```

**Başarılı Log Örneği**:
```
INFO partner_center_sync_task_started source=partner_center task_id=abc-123
INFO partner_center_sync_started total_fetched=20
INFO partner_center_referrals_fetched total_count=20 pages_fetched=1
INFO partner_center_sync_summary success_count=15 failure_count=0 skipped_count=5
INFO partner_center_sync_task_completed success_count=15 failure_count=0 skipped_count=5
```

**Hata Durumunda**:
- `partner_center_auth_error` → Token cache sorunu, Phase 2'yi tekrar çalıştır
- `partner_center_rate_limit` → Rate limit, bekleyip tekrar dene
- `partner_center_config_missing` → `.env` credentials kontrol et

---

## 🖥️ **PHASE 5 (LIGHT): UI VALIDATION** (15 dakika)

### 5.1. Mini UI'ı Aç

**URL**: http://localhost:8000/mini-ui/

**Kontrol Listesi**:
- [ ] Sayfa açılıyor mu?
- [ ] Header'da "🔄 Partner Center Sync" butonu görünüyor mu?

---

### 5.2. Sync Button Test

**Adımlar**:
1. Header'da "🔄 Partner Center Sync" butonuna tıkla
2. Toast notification görünüyor mu? ("Partner Center sync sıraya alındı")
3. Sync status indicator güncellendi mi? ("Son sync: X dk önce (OK)")

**Beklenen**:
- ✅ Toast notification: "Partner Center sync sıraya alındı" (yeşil)
- ✅ Sync status: "Son sync: 1 dk önce (OK)" (yeşil badge)

**Hata Durumunda**:
- Console'u aç (F12 → Console)
- Hata var mı kontrol et
- Network tab'ında API call görünüyor mu? (`POST /api/referrals/sync`)

---

### 5.3. Referral Badge Test

**Adımlar**:
1. Lead listesini aç (ana sayfa)
2. "Referral" kolonunu gör
3. Referral'ı olan lead'lerde badge görünüyor mu?

**Beklenen Badge'ler**:
- **Co-sell**: Mavi badge, "Co-sell" yazısı
- **Marketplace**: Yeşil badge, "Marketplace" yazısı
- **Solution Provider**: Turuncu badge, "SP" yazısı (tooltip: "Solution Provider")

**Kontrol**:
- [ ] En az 1 lead'de referral badge görünüyor mu?
- [ ] Badge renkleri doğru mu?
- [ ] SP badge tooltip çalışıyor mu? (hover → "Partner Center Referral: Solution Provider")
- [ ] Referral'ı olmayan lead'lerde "-" görünüyor mu?

**Eğer Badge Görünmüyorsa**:
```sql
-- Database'de referral var mı kontrol et
SELECT COUNT(*) FROM partner_center_referrals WHERE domain IS NOT NULL;

-- Domain match olan company var mı?
SELECT 
    pc.domain,
    c.domain as company_domain
FROM partner_center_referrals pc
LEFT JOIN companies c ON c.domain = pc.domain
WHERE pc.domain IS NOT NULL
LIMIT 5;
```

---

## ⚙️ **PHASE 4 (LIGHT): BACKGROUND SYNC VALIDATION** (15 dakika)

### 4.1. Celery Beat Log Kontrolü

**Komut**:
```bash
# Beat log'larını takip et
docker-compose logs -f beat
```

**Aranacak Log Satırları**:
```
beat: Scheduler: Sending due task sync-partner-center-referrals
```

**Beklenen**: Her 30 saniyede (dev) veya 10 dakikada (prod) bu log görünmeli

---

### 4.2. Background Sync Test

**Adımlar**:
1. Beat log'larını takip et (yukarıdaki komut)
2. 30-60 saniye bekle (development mode'da 30s interval)
3. Database'de yeni kayıt var mı kontrol et:

**SQL**:
```sql
-- Son sync zamanını kontrol et
SELECT 
    MAX(synced_at) as last_sync,
    COUNT(*) as total_referrals
FROM partner_center_referrals;

-- Son 5 dakikada sync edilen referral'lar
SELECT 
    referral_id,
    domain,
    referral_type,
    synced_at
FROM partner_center_referrals
WHERE synced_at > NOW() - INTERVAL '5 minutes'
ORDER BY synced_at DESC;
```

**Beklenen**:
- `last_sync` timestamp güncel (son 1-2 dakika içinde)
- Yeni referral'lar sync edildi (eğer Partner Center'da yeni referral varsa)

---

### 4.3. Worker Log Kontrolü

**Komut**:
```bash
# Worker log'larında sync task görünüyor mu?
docker-compose logs worker | grep "sync-partner-center-referrals"
```

**Beklenen**: Sync task log'ları görünmeli

---

## ✅ **BAŞARI KRİTERLERİ (Kritik Yol)**

### Minimum Viable:
- ✅ Feature flag açık ve sync çalışıyor
- ✅ Manual sync başarılı (en az 1 referral sync edildi)
- ✅ Database'de `partner_center_referrals` tablosunda kayıt var
- ✅ UI'da referral badge'leri görünüyor (en az 1 lead'de)
- ✅ Sync button çalışıyor (toast notification + status indicator)
- ✅ Background sync otomatik çalışıyor (Beat log'larında görünüyor)

### Bu Noktada:
👉 **Partner Center = Aktif, Hunter = Resmi referral kaynağını görür hale geldi**

---

## 🎀 **POST-ACTIVATION (Sonraki Gün veya İhtiyaç Olduğunda)**

### Phase 5 (Detay):
- Filter dropdown detaylı test (co-sell, marketplace, SP filtreleri)
- Referral inbox tab detaylı test (pagination, search, link status)
- Tooltip'ler ve UI polish

### Phase 6:
- Error scenarios (token expiry, invalid credentials, rate limits)
- Performance tests (sync duration, database load, memory usage)
- Data quality deep dive (duplicate prevention, domain normalization, link_status edge cases)

---

## 🚨 **TROUBLESHOOTING**

### Problem: "Token acquisition failed"
**Çözüm**:
```bash
# Token cache'i sil ve Phase 2'yi tekrar çalıştır
rm .token_cache
docker-compose exec api python scripts/partner_center_device_code_flow.py
```

### Problem: "Partner Center credentials not configured"
**Çözüm**:
- `.env` dosyasında `HUNTER_PARTNER_CENTER_CLIENT_ID` ve `HUNTER_PARTNER_CENTER_TENANT_ID` dolu mu kontrol et
- API container'ı restart et: `docker-compose restart api`

### Problem: "Feature flag disabled"
**Çözüm**:
- `.env` dosyasında `HUNTER_PARTNER_CENTER_ENABLED=true` var mı kontrol et
- API container'ı restart et: `docker-compose restart api`

### Problem: "No referrals found"
**Çözüm**:
- Partner Center'da gerçekten referral var mı kontrol et (Azure Portal)
- Filter rules çok sıkı olabilir (direction=Incoming, status=Active/New)
- Log'larda `skipped_reasons` kontrol et

### Problem: "Badge görünmüyor"
**Çözüm**:
```sql
-- Referral'lar domain'e link edilmiş mi?
SELECT 
    pc.domain,
    pc.link_status,
    c.id as company_id
FROM partner_center_referrals pc
LEFT JOIN companies c ON c.domain = pc.domain
WHERE pc.domain IS NOT NULL
LIMIT 10;
```

---

## 📝 **EXECUTION CHECKLIST**

### Phase 1: Config (30 dk)
- [ ] `.env` dosyasında feature flag açık
- [ ] Credentials dolu (CLIENT_ID, TENANT_ID)
- [ ] Azure AD App Registration permissions granted
- [ ] API container restart edildi

### Phase 2: Auth (15 dk)
- [ ] Device Code Flow script çalıştı
- [ ] Token cache oluşturuldu (`.token_cache` dosyası var)

### Phase 3: Manual Sync (30 dk)
- [ ] Manual sync script başarılı (success_count > 0)
- [ ] Database'de kayıt var (`SELECT COUNT(*) FROM partner_center_referrals`)
- [ ] API endpoint çalışıyor (200 OK)
- [ ] Worker log'larında sync task görünüyor

### Phase 5 (Light): UI (15 dk)
- [ ] Sync button çalışıyor (toast + status indicator)
- [ ] Referral badge'leri görünüyor (en az 1 lead'de)

### Phase 4 (Light): Background (15 dk)
- [ ] Beat log'larında sync task görünüyor
- [ ] Background sync çalışıyor (synced_at güncelleniyor)

**Toplam**: ~2 saat (ideal) / 2.5 saat (gerçekçi)

---

## 🎯 **SONRAKI ADIM**

Bu runbook tamamlandığında:
- ✅ Partner Center sync production-ready
- ✅ D365 entegrasyonuna temiz zemin hazır
- ✅ Hamle 2'ye geçilebilir (Dynamics 365 Push)

**Hamle 2'de kullanılacak**:
- `is_partner_center_referral` (boolean)
- `referral_type` (co-sell, marketplace, solution-provider)
- `referral_status` (Active, New, etc.)

---

## 📚 **REFERANS**

- `docs/active/HAMLE-1-PARTNER-CENTER-PRODUCTION-READY-PLAN.md` - Detaylı plan
- `docs/active/CRITICAL-3-HAMLE-PRODUCT-READY.md` - Ana strateji
- `scripts/partner_center_device_code_flow.py` - Auth script
- `scripts/sync_partner_center.py` - Manual sync script

