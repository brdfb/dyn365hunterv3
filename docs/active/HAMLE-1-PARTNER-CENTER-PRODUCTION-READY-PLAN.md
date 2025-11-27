# 🔥 HAMLE 1: Partner Center Sync - Production Ready Plan

**Tarih**: 2025-01-30  
**Durum**: Analiz Tamamlandı → Execution Plan  
**Hedef**: Partner Center Sync'i production-ready hale getirmek

---

## 📊 **MEVCUT DURUM ANALİZİ**

### ✅ **Ne Var (Backend - %100 Hazır):**

1. **API Client** (`app/core/partner_center.py`):
   - ✅ MSAL + Device Code Flow implement edilmiş
   - ✅ Token cache persistence (`.token_cache` file)
   - ✅ Silent token acquisition (background jobs için)
   - ✅ Rate limiting handling (429 retry with exponential backoff)
   - ✅ Error handling (auth, network, API errors)
   - ✅ Pagination support (OData `@odata.nextLink`)

2. **Sync Logic** (`app/core/referral_ingestion.py`):
   - ✅ `sync_referrals_from_partner_center()` - Ana sync fonksiyonu
   - ✅ Filter rules (direction=Incoming, status=Active/New, substatus exclusion)
   - ✅ Domain extraction (fallback chain)
   - ✅ Referral type detection (co-sell, marketplace, solution-provider)
   - ✅ Company upsert + Azure Tenant ID signal
   - ✅ Domain scan trigger (idempotent)
   - ✅ Duplicate prevention (IntegrityError handling)
   - ✅ Structured logging (success/failure/skipped counts)

3. **Database** (`app/db/models.py`):
   - ✅ `PartnerCenterReferral` model hazır
   - ✅ Indexes: domain, status, synced_at, referral_type, azure_tenant_id, link_status
   - ✅ Migration: `622ba66483b9_add_partner_center_referrals.py`

4. **Celery Task** (`app/core/tasks.py`):
   - ✅ `sync_partner_center_referrals_task()` - Background sync task
   - ✅ Feature flag check
   - ✅ Error handling (graceful degradation)
   - ✅ Metrics tracking (sync_runs, sync_success, sync_failed)

5. **Celery Beat Schedule** (`app/core/celery_app.py`):
   - ✅ Schedule configured: Production 600s (10 min), Development 30s
   - ✅ Auto-override for development environment
   - ✅ Task expiration: 1 hour

6. **API Endpoints** (`app/api/referrals.py`):
   - ✅ `POST /api/referrals/sync` - Manual sync endpoint
   - ✅ `GET /api/referrals/inbox` - Referral inbox list
   - ✅ Feature flag check (400 if disabled)

7. **UI Integration** (`mini-ui/`):
   - ✅ Sync button (header'da "🔄 Partner Center Sync")
   - ✅ Sync status indicator (last sync time + status)
   - ✅ Referral column (lead listesinde badge'ler)
   - ✅ Referral type filter (dropdown)
   - ✅ Referral inbox tab (referral listesi)

8. **Scripts**:
   - ✅ `scripts/partner_center_device_code_flow.py` - Initial auth script
   - ✅ `scripts/sync_partner_center.py` - Manual sync script

9. **Tests**:
   - ✅ 59/59 tests passing (referral ingestion, sync task, API endpoints)

---

### ❌ **Ne Yok (Production Activation İçin Gerekli):**

1. **Feature Flag**: `HUNTER_PARTNER_CENTER_ENABLED=false` (kapalı)
2. **Credentials**: `.env` dosyasında yapılandırılmamış
   - `HUNTER_PARTNER_CENTER_CLIENT_ID` - Boş
   - `HUNTER_PARTNER_CENTER_TENANT_ID` - Boş
   - `HUNTER_PARTNER_CENTER_API_URL` - Default var ama kontrol edilmeli
3. **Token Cache**: `.token_cache` dosyası yok (initial auth gerekli)
4. **Production Validation**: Test edilmemiş (local'de çalışıyor mu?)

---

## 🎯 **PRODUCTION-READY CHECKLIST**

### **Phase 1: Configuration & Credentials Setup** (30 dakika)

#### 1.1. Environment Variables Check

**Dosya**: `.env`

**Gerekli Değişkenler**:
```bash
# Feature Flag (AÇILACAK)
HUNTER_PARTNER_CENTER_ENABLED=true

# OAuth Credentials (DOLDURULACAK)
HUNTER_PARTNER_CENTER_CLIENT_ID=your-client-id-here
HUNTER_PARTNER_CENTER_TENANT_ID=your-tenant-id-here
HUNTER_PARTNER_CENTER_API_URL=https://api.partner.microsoft.com

# Optional (default değerler var)
HUNTER_PARTNER_CENTER_SCOPE=https://api.partner.microsoft.com/.default
HUNTER_PARTNER_CENTER_TOKEN_CACHE_PATH=.token_cache
HUNTER_PARTNER_CENTER_SYNC_INTERVAL=600  # Production: 10 minutes
```

**Kontrol Listesi**:
- [ ] `.env` dosyasında `HUNTER_PARTNER_CENTER_ENABLED=true` var mı?
- [ ] `HUNTER_PARTNER_CENTER_CLIENT_ID` dolu mu? (Azure AD App Registration'dan)
- [ ] `HUNTER_PARTNER_CENTER_TENANT_ID` dolu mu? (Azure AD Tenant ID)
- [ ] `HUNTER_PARTNER_CENTER_API_URL` doğru mu? (`https://api.partner.microsoft.com`)

**Not**: `HUNTER_PARTNER_CENTER_CLIENT_SECRET` **gerekli değil** (PublicClientApplication kullanılıyor, Device Code Flow için secret gerekmiyor)

---

#### 1.2. Azure AD App Registration Check

**Azure Portal → Azure Active Directory → App Registrations**

**Gerekli Permissions**:
- [ ] Partner Center API permissions granted
- [ ] Admin consent granted (delegated permissions için)
- [ ] Redirect URI configured (Device Code Flow için gerekli değil ama kontrol et)

**API Permissions**:
- `https://api.partner.microsoft.com/.default` (delegated permission)
- Admin consent: **Required**

---

### **Phase 2: Initial Authentication** (15 dakika)

#### 2.1. Device Code Flow Authentication

**Script**: `scripts/partner_center_device_code_flow.py`

**Adımlar**:
1. Feature flag'i aç (`.env` → `HUNTER_PARTNER_CENTER_ENABLED=true`)
2. API container'ı restart et: `docker-compose restart api`
3. Device Code Flow script'ini çalıştır:
   ```bash
   docker-compose exec api python scripts/partner_center_device_code_flow.py
   ```
4. Browser'da authentication yap (verification URI + user code)
5. Token cache dosyası oluşturulacak: `.token_cache`

**Beklenen Sonuç**:
```
✅ SUCCESS: Token acquired!
Token cache saved to: .token_cache
```

**Kontrol Listesi**:
- [ ] Script başarıyla çalıştı mı?
- [ ] `.token_cache` dosyası oluşturuldu mu?
- [ ] Token bilgileri log'da görünüyor mu? (expires_in, token_type, scope)

---

### **Phase 3: Manual Sync Test** (30 dakika)

#### 3.1. Manual Sync Script Test

**Script**: `scripts/sync_partner_center.py`

**Adımlar**:
1. Manual sync script'ini çalıştır:
   ```bash
   docker-compose exec api python -m scripts.sync_partner_center
   ```
2. Log'ları kontrol et (success/failure/skipped counts)
3. Database'de kayıt var mı kontrol et:
   ```sql
   SELECT COUNT(*) FROM partner_center_referrals;
   SELECT * FROM partner_center_referrals LIMIT 5;
   ```

**Beklenen Sonuç**:
```
Partner Center sync completed:
  - Success: X
  - Failed: 0
  - Skipped: Y
  - Total processed: X + Y
```

**Kontrol Listesi**:
- [ ] Script başarıyla çalıştı mı?
- [ ] Success count > 0 mı? (en az 1 referral sync edildi mi?)
- [ ] Database'de `partner_center_referrals` tablosunda kayıt var mı?
- [ ] Log'larda hata var mı? (auth, rate limit, network)

---

#### 3.2. API Endpoint Test

**Endpoint**: `POST /api/referrals/sync`

**Adımlar**:
1. API endpoint'ini test et:
   ```bash
   curl -X POST http://localhost:8000/api/referrals/sync \
     -H "Content-Type: application/json" \
     -v
   ```
2. Response'u kontrol et (task_id, success, message)
3. Celery task log'larını kontrol et (worker container)

**Beklenen Sonuç**:
```json
{
  "success": true,
  "message": "Referral sync task enqueued. Check logs for results.",
  "enqueued": true,
  "task_id": "abc-123-def-456",
  "success_count": 0,
  "failure_count": 0,
  "skipped_count": 0,
  "errors": []
}
```

**Kontrol Listesi**:
- [ ] API endpoint 200 OK döndü mü?
- [ ] `task_id` döndü mü?
- [ ] Celery task çalıştı mı? (worker log'larında görünüyor mu?)
- [ ] Task başarıyla tamamlandı mı? (success_count > 0)

---

### **Phase 4: Background Sync Validation** (15 dakika)

#### 4.1. Celery Beat Schedule Check

**Dosya**: `app/core/celery_app.py`

**Kontrol**:
- [ ] Celery Beat schedule'da `sync-partner-center-referrals` task var mı?
- [ ] Schedule interval doğru mu? (Production: 600s, Development: 30s)
- [ ] Celery Beat çalışıyor mu? (`docker-compose ps` → `beat` container running)

**Test**:
1. Celery Beat log'larını kontrol et:
   ```bash
   docker-compose logs -f beat
   ```
2. Schedule'ın çalıştığını doğrula (log'larda "sync-partner-center-referrals" görünmeli)
3. Development mode'da 30s interval çalışıyor mu? (test için)

**Kontrol Listesi**:
- [ ] Celery Beat container çalışıyor mu?
- [ ] Schedule log'larında "sync-partner-center-referrals" görünüyor mu?
- [ ] Task periyodik olarak çalışıyor mu? (30s dev, 600s prod)

---

#### 4.2. Background Sync Test

**Adımlar**:
1. Celery Beat'in çalıştığını doğrula
2. 30-60 saniye bekle (development mode'da 30s interval)
3. Database'de yeni kayıtlar var mı kontrol et:
   ```sql
   SELECT COUNT(*) FROM partner_center_referrals;
   SELECT MAX(synced_at) FROM partner_center_referrals;
   ```
4. Log'ları kontrol et (sync success/failure)

**Kontrol Listesi**:
- [ ] Background sync otomatik çalıştı mı?
- [ ] Yeni referral'lar sync edildi mi?
- [ ] `synced_at` timestamp güncellendi mi?
- [ ] Log'larda hata var mı?

---

### **Phase 5: UI Validation** (30 dakika)

#### 5.1. Sync Button Test

**UI**: Mini UI header'da "🔄 Partner Center Sync" butonu

**Adımlar**:
1. Mini UI'ı aç: `http://localhost:8000/mini-ui/`
2. Header'da sync butonunu gör
3. Sync butonuna tıkla
4. Toast notification görünüyor mu? ("Partner Center sync sıraya alındı")
5. Sync status indicator güncellendi mi? ("Son sync: X dk önce (OK)")

**Kontrol Listesi**:
- [ ] Sync butonu görünüyor mu?
- [ ] Butona tıklayınca toast notification gösteriliyor mu?
- [ ] Sync status indicator güncellendi mi?
- [ ] Console'da hata var mı? (F12 → Console)

---

#### 5.2. Referral Column Test

**UI**: Lead listesinde "Referral" kolonu

**Adımlar**:
1. Lead listesini aç
2. "Referral" kolonunu gör (badge'ler: Co-sell, Marketplace, SP)
3. Referral'ı olan lead'lerde badge görünüyor mu?
4. Badge tooltip çalışıyor mu? (hover → "Partner Center Referral: ...")

**Kontrol Listesi**:
- [ ] Referral kolonu görünüyor mu?
- [ ] Badge'ler doğru renklerde mi? (co-sell: blue, marketplace: green, solution-provider: orange)
- [ ] SP badge tooltip çalışıyor mu? ("Solution Provider" açıklaması)
- [ ] Referral'ı olmayan lead'lerde "-" görünüyor mu?

---

#### 5.3. Referral Type Filter Test

**UI**: Filter bar'da "Referral" dropdown

**Adımlar**:
1. Filter bar'da "Referral" dropdown'ını gör
2. "Co-sell" seç → Sadece co-sell referral'ları göster
3. "Marketplace" seç → Sadece marketplace referral'ları göster
4. "Solution Provider" seç → Sadece SP referral'ları göster
5. "Tümü" seç → Tüm lead'ler göster

**Kontrol Listesi**:
- [ ] Referral filter dropdown görünüyor mu?
- [ ] Filter çalışıyor mu? (seçilen tip'e göre lead'ler filtreleniyor mu?)
- [ ] API'ye `referral_type` query parameter gönderiliyor mu? (Network tab)

---

#### 5.4. Referral Inbox Tab Test

**UI**: "🔗 Partner Center Referrals" tab

**Adımlar**:
1. Referrals tab'ını aç
2. Referral listesini gör (company, domain, referral type, status, link status)
3. Filter'ları test et (link status, referral type, status, search)
4. Pagination çalışıyor mu?

**Kontrol Listesi**:
- [ ] Referrals tab görünüyor mu?
- [ ] Referral listesi yükleniyor mu?
- [ ] Filter'lar çalışıyor mu?
- [ ] Pagination çalışıyor mu?

---

### **Phase 6: Production Validation** (30 dakika)

#### 6.1. Error Handling Test

**Test Senaryoları**:
1. **Feature Flag OFF**: `.env` → `HUNTER_PARTNER_CENTER_ENABLED=false`
   - [ ] API endpoint 400 döndü mü?
   - [ ] Celery task skip edildi mi?
   - [ ] UI'da sync butonu disabled mı?

2. **Invalid Credentials**: `.env` → `HUNTER_PARTNER_CENTER_CLIENT_ID=invalid`
   - [ ] Client initialization hatası log'landı mı?
   - [ ] Graceful degradation çalışıyor mu? (sistem çökmedi mi?)

3. **Token Expiry**: Token cache'i sil → Token refresh çalışıyor mu?
   - [ ] Silent token acquisition başarısız oldu mu?
   - [ ] Error log'landı mı? (re-authentication gerekli)

4. **Rate Limit**: API rate limit'e takıldı mı?
   - [ ] 429 error handle edildi mi?
   - [ ] Retry with exponential backoff çalışıyor mu?

**Kontrol Listesi**:
- [ ] Tüm error senaryoları test edildi mi?
- [ ] Error handling robust mu? (sistem çökmedi mi?)
- [ ] Error log'ları yeterli mi? (debug için)

---

#### 6.2. Performance Test

**Test Senaryoları**:
1. **Sync Duration**: Manual sync ne kadar sürdü?
   - [ ] Sync duration log'da görünüyor mu?
   - [ ] Duration makul mu? (< 5 dakika for 2000 referrals)

2. **Database Load**: Sync sırasında database load artıyor mu?
   - [ ] Database connection pool yeterli mi?
   - [ ] Deadlock/contention var mı?

3. **Memory Usage**: Sync sırasında memory kullanımı artıyor mu?
   - [ ] Memory leak var mı?
   - [ ] Pagination doğru çalışıyor mu? (tüm referral'lar memory'ye yüklenmiyor)

**Kontrol Listesi**:
- [ ] Performance metrics log'lanıyor mu?
- [ ] Performance kabul edilebilir mi?

---

#### 6.3. Data Quality Test

**Test Senaryoları**:
1. **Referral Data**: Database'deki referral'lar doğru mu?
   - [ ] `referral_id` unique mi? (duplicate yok mu?)
   - [ ] `referral_type` doğru mu? (co-sell, marketplace, solution-provider)
   - [ ] `domain` normalize edilmiş mi? (www. strip, punycode decode)
   - [ ] `link_status` doğru mu? (auto_linked, unlinked, multi_candidate)

2. **Company Linking**: Referral'lar company'lere link edildi mi?
   - [ ] Domain match olan referral'lar `auto_linked` mi?
   - [ ] `linked_lead_id` doğru mu?
   - [ ] Domain match olmayan referral'lar `unlinked` mi?

3. **Azure Tenant ID**: M365 signal doğru mu?
   - [ ] `azure_tenant_id` referral'lardan çekildi mi?
   - [ ] Company'lere Azure Tenant ID override edildi mi?

**Kontrol Listesi**:
- [ ] Data quality kabul edilebilir mi?
- [ ] Duplicate prevention çalışıyor mu?
- [ ] Domain normalization doğru mu?

---

## 🚨 **RİSKLER VE MİTİGASYON**

### Risk 1: OAuth Token Expiry
**Risk**: Token cache expire olursa background sync çalışmaz  
**Mitigasyon**: 
- Token cache persistence (`.token_cache` file)
- Silent token acquisition (refresh token kullanarak)
- Error logging (re-authentication gerekli olduğunda log)

### Risk 2: API Rate Limits
**Risk**: Partner Center API rate limit'e takılabilir  
**Mitigasyon**:
- Rate limiting handling (429 retry with exponential backoff)
- `Retry-After` header respect ediliyor
- Pagination arasında `time.sleep(1)` (basic rate limiting)

### Risk 3: Network Errors
**Risk**: Network hatası sync'i bozabilir  
**Mitigasyon**:
- Retry mechanism (3 deneme, exponential backoff)
- Graceful error handling (bir referral hatası diğerlerini etkilemez)
- Structured logging (hangi referral'da hata oldu?)

### Risk 4: Database Contention
**Risk**: Sync sırasında database lock/contention olabilir  
**Mitigasyon**:
- Connection pooling (20 connections, 10 overflow)
- Transaction isolation (her referral bağımsız)
- Duplicate prevention (IntegrityError handling)

---

## ✅ **BAŞARI KRİTERLERİ**

### Minimum Viable (MVP):
- ✅ Feature flag açık ve sync çalışıyor
- ✅ Manual sync başarılı (en az 1 referral sync edildi)
- ✅ UI'da referral'lar görünüyor
- ✅ Background sync otomatik çalışıyor (30s dev, 600s prod)
- ✅ Error handling robust (sistem çökmedi)

### Production Ready:
- ✅ Tüm test senaryoları geçti
- ✅ Performance kabul edilebilir (< 5 dakika for 2000 referrals)
- ✅ Data quality kabul edilebilir (duplicate yok, normalization doğru)
- ✅ Monitoring/alerting kuruldu (opsiyonel - post-MVP)

---

## 📝 **EXECUTION ORDER**

### 🧵 **KRİTİK YOL** (İlk Oturuşta - 2-2.5 saat)
**Hedef**: "Partner Center canlı, referral'lar geliyor, UI'da görüyorum, sistem çökmeden dönüyor."

1. **Phase 1**: Configuration & Credentials Setup (30 dk) → **BLOKAJ**
2. **Phase 2**: Initial Authentication (15 dk) → **BLOKAJ**
3. **Phase 3**: Manual Sync Test (30 dk) → **BLOKAJ**
4. **Phase 5 (Light)**: UI Validation - Sync button + Badge görünüyor mu? (15 dk)
5. **Phase 4 (Light)**: Background Sync - Beat çalışıyor mu? (15 dk)

**Toplam**: ~2 saat (ideal) / 2.5 saat (gerçekçi)

**Detaylı Komutlar**: `docs/active/HAMLE-1-EXECUTION-RUNBOOK.md` dosyasına bak

### 🎀 **POST-ACTIVATION** (Aynı gün veya sonraki gün)
- **Phase 5 (Detay)**: Filter dropdown, tooltip'ler, inbox tab detayları
- **Phase 6**: Error scenarios, performance tests, data quality deep dive

**Not**: Bu adımlar lüks değil, gerekli, ama ilk gün "mutlaka" bitmesi gerekmeyenler. "Hamle 1 - Round 2" olarak yapılabilir.

---

## 🎯 **SONRAKI ADIM**

### Kritik Yol Tamamlandığında:
- ✅ Partner Center sync production-ready
- ✅ D365 entegrasyonuna temiz zemin hazır
- ✅ Hamle 2'ye geçilebilir (Dynamics 365 Push)

**Hamle 2'de kullanılacak Partner Center alanları**:
- `is_partner_center_referral` (boolean)
- `referral_type` (co-sell, marketplace, solution-provider)
- `referral_status` (Active, New, etc.)

---

## 📚 **REFERANS DOKÜMANLAR**

- **`docs/active/HAMLE-1-EXECUTION-RUNBOOK.md`** ⭐ **KOPYALA-YAPIŞTIR KOMUTLAR** - Terminal komutları, SQL sorguları, log kontrol noktaları
- `docs/active/CRITICAL-3-HAMLE-PRODUCT-READY.md` - Ana strateji
- `docs/reference/PARTNER-CENTER-TEST-GUIDE.md` - Test guide
- `docs/reference/PARTNER-CENTER-PRODUCTION-CHECKLIST.md` - Production checklist
- `scripts/partner_center_device_code_flow.py` - Auth script
- `scripts/sync_partner_center.py` - Manual sync script

