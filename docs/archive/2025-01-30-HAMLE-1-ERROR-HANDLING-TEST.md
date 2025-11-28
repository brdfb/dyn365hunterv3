# HAMLE 1: Error Handling Test Plan

**Tarih**: 2025-01-30  
**Durum**: 🔄 **TEST EDİLECEK**  
**Amaç**: Partner Center sync error handling'in robust olduğunu doğrulamak

---

## 📋 Test Senaryoları

### 1. Auth Hatası Testi (401/403)

**Senaryo**: Geçersiz token veya yetkisiz erişim

**Beklenen Davranış:**
- `PartnerCenterAuthError` raise edilmeli
- Error log'lanmalı (`partner_center_auth_error`)
- 401 durumunda token refresh denenmeli (1 retry)
- 403 durumunda retry yapılmamalı

**Test Adımları:**
1. Token cache dosyasını sil veya geçersiz token ekle
2. Sync tetikle
3. 401/403 hatası alınmalı
4. Error log'larını kontrol et

**Kod Referansı**: `app/core/partner_center.py` satır 247-270

---

### 2. Rate Limit Testi (429)

**Senaryo**: Partner Center API rate limit aşımı

**Beklenen Davranış:**
- `PartnerCenterRateLimitError` raise edilmeli
- Error log'lanmalı (`partner_center_rate_limit`)
- `Retry-After` header varsa kullanılmalı (clamped 1-3600s)
- `Retry-After` header yoksa exponential backoff with jitter kullanılmalı
- Max 2 retry yapılmalı

**Test Adımları:**
1. Çok fazla request gönder (rate limit tetikle)
2. 429 hatası alınmalı
3. Retry mekanizması çalışmalı
4. Error log'larını kontrol et

**Kod Referansı**: `app/core/partner_center.py` satır 272-314

---

### 3. Network Hatası Testi

**Senaryo**: API erişilemez (timeout, connection error)

**Beklenen Davranış:**
- `httpx.RequestError` catch edilmeli
- Error log'lanmalı (`partner_center_network_error`)
- Retry mekanizması çalışmalı (max 2 retry)
- Exponential backoff with jitter kullanılmalı

**Test Adımları:**
1. Network'ü kes veya API URL'ini geçersiz yap
2. Sync tetikle
3. Network hatası alınmalı
4. Retry mekanizması çalışmalı
5. Error log'larını kontrol et

**Kod Referansı**: `app/core/partner_center.py` satır 349-362

---

### 4. Server Hatası Testi (5xx)

**Senaryo**: Partner Center API server hatası (500, 502, 503)

**Beklenen Davranış:**
- `httpx.HTTPStatusError` catch edilmeli
- Error log'lanmalı (`partner_center_server_error`)
- Retry mekanizması çalışmalı (max 2 retry)
- Exponential backoff with jitter kullanılmalı

**Test Adımları:**
1. Mock API 5xx döndür (test için)
2. Sync tetikle
3. Server hatası alınmalı
4. Retry mekanizması çalışmalı
5. Error log'larını kontrol et

**Kod Referansı**: `app/core/partner_center.py` satır 315-334

---

### 5. Client Hatası Testi (4xx - 401/403/429 hariç)

**Senaryo**: Geçersiz request (400, 404, etc.)

**Beklenen Davranış:**
- `httpx.HTTPStatusError` catch edilmeli
- Error log'lanmalı (`partner_center_client_error`)
- Retry yapılmamalı (client error, retry faydasız)

**Test Adımları:**
1. Mock API 400 döndür (test için)
2. Sync tetikle
3. Client hatası alınmalı
4. Retry yapılmamalı
5. Error log'larını kontrol et

**Kod Referansı**: `app/core/partner_center.py` satır 336-347

---

### 6. Retry Mekanizması Doğrulama

**Beklenen Davranış:**
- Max retry: 2 (3 deneme toplam)
- Exponential backoff: `2^attempt * base_delay + jitter`
- Jitter: Random 0-1 saniye
- Retry-After header: Clamped 1-3600s

**Kod Referansı**: 
- `app/core/partner_center.py` satır 208-212 (backoff)
- `app/core/retry_utils.py` (backoff ve jitter fonksiyonları)

---

### 7. Error Logging Doğrulama

**Beklenen Log Formatları:**
- `partner_center_auth_error` - Auth hataları
- `partner_center_rate_limit` - Rate limit hataları
- `partner_center_network_error` - Network hataları
- `partner_center_server_error` - Server hataları
- `partner_center_client_error` - Client hataları

**Log Alanları:**
- `status_code`: HTTP status code
- `request_id`: Request ID (varsa)
- `retry`: Retry attempt number
- `error`: Error message
- `retry_after`: Retry-After header value (rate limit için)

**Kod Referansı**: `app/core/partner_center.py` satır 250-290, 318-344

---

## 🧪 Test Execution

### Test 1: Auth Hatası (401)

```bash
# 1. Token cache'i geçersiz yap
docker-compose exec api rm .token_cache

# 2. Sync tetikle
curl -X POST http://localhost:8000/api/v1/partner-center/referrals/sync

# 3. Log'ları kontrol et
docker-compose logs worker | grep "partner_center_auth_error"
```

**Beklenen**: 401 hatası, `PartnerCenterAuthError` raise edilmeli

---

### Test 2: Rate Limit (429)

**Not**: Rate limit testi için gerçek API'ye çok fazla request göndermek gerekir. Production'da dikkatli test edilmeli.

**Alternatif**: Mock API kullanarak test edilebilir (unit test).

---

### Test 3: Network Hatası

```bash
# 1. API URL'ini geçersiz yap (geçici)
# .env dosyasında:
HUNTER_PARTNER_CENTER_API_URL=https://invalid-api-url.test

# 2. Container'ı restart et
docker-compose restart api worker

# 3. Sync tetikle
curl -X POST http://localhost:8000/api/v1/partner-center/referrals/sync

# 4. Log'ları kontrol et
docker-compose logs worker | grep "partner_center_network_error"
```

**Beklenen**: Network hatası, retry mekanizması çalışmalı

---

## 📊 Test Sonuçları

**Test Tarihi**: _______________  
**Test Eden**: _______________  

### Test 1: Auth Hatası (401)
- [ ] Test edildi
- [ ] Sonuç: _______________

### Test 2: Rate Limit (429)
- [ ] Test edildi
- [ ] Sonuç: _______________

### Test 3: Network Hatası
- [ ] Test edildi
- [ ] Sonuç: _______________

### Test 4: Server Hatası (5xx)
- [ ] Test edildi
- [ ] Sonuç: _______________

### Test 5: Client Hatası (4xx)
- [ ] Test edildi
- [ ] Sonuç: _______________

### Test 6: Retry Mekanizması
- [ ] Test edildi
- [ ] Sonuç: _______________

### Test 7: Error Logging
- [ ] Test edildi
- [ ] Sonuç: _______________

---

## ✅ Kod İncelemesi Sonuçları

### ✅ İyi Yapılanlar

1. **Comprehensive Error Handling**: Tüm HTTP status code'ları handle ediliyor
2. **Retry Mekanizması**: Exponential backoff with jitter kullanılıyor
3. **Rate Limit Handling**: Retry-After header kontrolü var
4. **Structured Logging**: Tüm error'lar structured log formatında
5. **Error Types**: Custom exception'lar (`PartnerCenterAuthError`, `PartnerCenterRateLimitError`)

### ⚠️ İyileştirme Önerileri

1. **Rate Limit Test**: Mock API ile unit test eklenebilir
2. **Error Metrics**: Error rate metrics tracking eklenebilir
3. **Circuit Breaker**: Çok fazla error durumunda circuit breaker pattern eklenebilir

---

**Son Güncelleme**: 2025-01-30

