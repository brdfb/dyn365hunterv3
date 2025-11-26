# Token Cache Setup - Adım Adım Rehber (Dummy Proof)

**Date**: 2025-01-30  
**Last Updated**: 2025-11-26  
**Purpose**: Partner Center token cache'i oluşturma - Dummy-proof step-by-step guide

---

## 🎯 Amaç

Token cache'i oluşturup kalıcı hale getirmek. Böylece container restart sonrası da token kaybolmayacak.

---

## ✅ Ön Hazırlık (Kontrol)

### 1. Feature Flag Açık mı? (Önerilen, zorunlu değil)

> **Not**: Token cache oluşturmak için flag'in açık olması zorunlu değil (Device Code Flow sadece MSAL + AAD tarafı). Ancak genelde test akışında ON tutmak işleri kolaylaştırır.

```bash
grep HUNTER_PARTNER_CENTER_ENABLED .env
```

**Beklenen**: `HUNTER_PARTNER_CENTER_ENABLED=true`

Eğer `false` ise:
```bash
sed -i.bak 's/HUNTER_PARTNER_CENTER_ENABLED=false/HUNTER_PARTNER_CENTER_ENABLED=true/' .env
docker-compose restart api worker
```

---

### 2. Container'lar Çalışıyor mu?

```bash
docker-compose ps
```

**Beklenen**: `api` ve `worker` container'ları `Up` durumunda

Eğer değilse:
```bash
docker-compose up -d
sleep 5
```

---

## 📝 ADIM 1: Python Shell'e Gir

**Terminal'inizde şu komutu çalıştırın:**

```bash
docker-compose exec api python
```

**Beklenen çıktı:**
```
Python 3.10.19 (main, Nov 18 2025, 05:59:40) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

✅ **Kontrol**: `>>>` görünüyor mu? Evet ise ADIM 2'ye geç.

---

## 📝 ADIM 2: Import'ları Yap

**Python shell'de (>>> sonrası) şu satırları yazın ve Enter'a basın:**

```python
from msal import PublicClientApplication, SerializableTokenCache
from app.config import settings
import os
```

**Beklenen**: Hata yok, tekrar `>>>` görünüyor.

✅ **Kontrol**: Hata var mı? Hayır ise ADIM 3'e geç.

---

## 📝 ADIM 3: Token Cache Hazırlığı

**Python shell'de şu kodu yazın:**

```python
authority = f'https://login.microsoftonline.com/{settings.partner_center_tenant_id}'
cache_path = '.token_cache'

token_cache = SerializableTokenCache()
if os.path.exists(cache_path):
    with open(cache_path, 'r') as f:
        token_cache.deserialize(f.read())
    print('✅ Existing token cache loaded')
else:
    print('ℹ️  No existing token cache (will create new)')
```

**Beklenen**: `✅ Existing token cache loaded` veya `ℹ️  No existing token cache (will create new)`

✅ **Kontrol**: Hata var mı? Hayır ise ADIM 4'e geç.

---

## 📝 ADIM 4: MSAL App Oluştur

**Python shell'de şu kodu yazın:**

```python
app = PublicClientApplication(
    client_id=settings.partner_center_client_id,
    authority=authority,
    token_cache=token_cache,
)
print('✅ MSAL app created')
```

**Beklenen**: `✅ MSAL app created`

✅ **Kontrol**: Hata var mı? Hayır ise ADIM 5'e geç.

---

## 📝 ADIM 5: Device Code Flow Başlat

**Python shell'de şu kodu yazın:**

```python
flow = app.initiate_device_flow(scopes=[settings.partner_center_scope])
```

**Beklenen**: Hata yok.

✅ **Kontrol**: Hata var mı? Hayır ise ADIM 6'ya geç.

---

## 📝 ADIM 6: URL ve Kodu Göster

**Python shell'de şu kodu yazın:**

```python
print('=' * 70)
print('📱 DEVICE CODE FLOW')
print('=' * 70)
print()
print('1. Browser\'da şu URL\'ye git:')
print(f'   {flow["verification_uri"]}')
print()
print('2. Şu kodu gir:')
print(f'   {flow["user_code"]}')
print()
print('3. Login + consent işlemini tamamla')
print()
print('=' * 70)
print('💡 Browser\'da login yaptıktan sonra buraya dön ve Enter\'a bas')
print('=' * 70)
```

**Beklenen**: URL ve kod görünüyor.

✅ **Kontrol**: URL ve kod görünüyor mu? Evet ise ADIM 7'ye geç.

---

## 📝 ADIM 7: Browser'da Login Yap

1. **Browser'ı aç**
2. **Gösterilen URL'ye git** (genellikle `https://microsoft.com/devicelogin`)
3. **Gösterilen kodu gir**
4. **Login + consent işlemini tamamla** (MFA varsa onu da yap)

**Beklenen**: Browser'da "You have signed in..." mesajı görünüyor.

✅ **Kontrol**: Browser'da login tamamlandı mı? Evet ise ADIM 8'e geç.

---

## 📝 ADIM 8: Token'ı Al ve Kaydet

**Python shell'e dön ve şu kodu yazın:**

```python
result = app.acquire_token_by_device_flow(flow)
```

**Beklenen**: Biraz bekler (5-10 saniye), sonra hata yok.

✅ **Kontrol**: Hata var mı? Hayır ise ADIM 9'a geç.

---

## 📝 ADIM 9: Token Kontrolü ve Kaydetme

**Python shell'de şu kodu yazın:**

```python
if 'access_token' in result:
    print('✅ Token acquired!')
    print(f'   Expires in: {result.get("expires_in")} seconds')
    
    # Token cache'i kaydet
    if token_cache.has_state_changed:
        with open(cache_path, 'w') as f:
            f.write(token_cache.serialize())
        print(f'✅ Token cache saved to: {os.path.abspath(cache_path)}')
    else:
        print('ℹ️  Token cache unchanged (already saved)')
    
    # Account kontrolü
    accounts = app.get_accounts()
    if accounts:
        print(f'✅ Account cached: {accounts[0].get("username")}')
        print()
        print('✅✅✅ BAŞARILI! Token cache oluşturuldu!')
    else:
        print('⚠️  No accounts in cache (unexpected)')
else:
    print('❌ Token acquisition failed')
    print(f'   Error: {result.get("error")}')
    print(f'   Description: {result.get("error_description")}')
```

**Beklenen**: 
```
✅ Token acquired!
   Expires in: 3600 seconds
✅ Token cache saved to: /app/.token_cache
✅ Account cached: bered.gonultasi@gibibyte.com.tr

✅✅✅ BAŞARILI! Token cache oluşturuldu!
```

✅ **Kontrol**: `✅✅✅ BAŞARILI!` görünüyor mu? Evet ise ADIM 10'a geç.

---

## 📝 ADIM 10: Python Shell'den Çık

**Python shell'de:**

```python
exit()
```

veya `Ctrl+D`

---

## 📝 ADIM 11: Token Cache Kontrolü

**Terminal'inizde:**

```bash
docker-compose exec api ls -la .token_cache
```

**Beklenen**: Dosya görünüyor (örnek: `-rw-r--r-- 1 root root 1234 Nov 26 21:45 .token_cache`)

✅ **Kontrol**: Dosya var mı? Evet ise ADIM 12'ye geç.

---

## 📝 ADIM 12: Sync Test

**Terminal'inizde:**

```bash
curl -X POST http://localhost:8000/api/referrals/sync -H "Content-Type: application/json"
```

**Beklenen**: 
```json
{
  "success": true,
  "message": "Referral sync task enqueued. Check logs for results.",
  "enqueued": true,
  "task_id": "...",
  ...
}
```

✅ **Kontrol**: `200 OK` ve `enqueued: true` görünüyor mu? Evet ise ADIM 13'e geç.

---

## 📝 ADIM 13: Log Kontrolü (Referral Sayısı)

**Terminal'inizde (5 saniye bekleyin):**

```bash
sleep 5
docker-compose logs worker | grep -i "partner_center_referrals_fetched\|total_referrals" | tail -5
```

**Beklenen**: 
```
partner_center_referrals_fetched count=X
```

**X > 0 ise**: ✅ Referral'lar çekildi! (Partner Center API'den X adet referral geldi)  
**X = 0 ise**: ⚠️ Partner Center'da referral yok (normal olabilir) veya API'den 0 döndü

> **Not**: Bu log mesajı, Partner Center API'den kaç referral çekildiğini gösterir. Eğer Partner Center portal'da referral varsa ama burada X=0 ise, API response'unu debug etmek gerekir.

✅ **Kontrol**: Log'da `count=X` görünüyor mu? Evet ise ADIM 14'e geç.

---

## 📝 ADIM 14: DB Kontrolü

**Terminal'inizde:**

```bash
docker-compose exec postgres psql -U dyn365hunter -d dyn365hunter -c "SELECT COUNT(*) as total FROM partner_center_referrals;"
```

**Beklenen**: 
```
 total 
-------
     X
(1 row)
```

**X > 0 ise**: ✅✅✅ **BAŞARILI! Referral'lar DB'ye kaydedildi!**  
**X = 0 ise**: 
- Partner Center'da referral yoksa → Normal
- Partner Center'da referral varsa ama DB'de yoksa → Sorun var (debug gerekli)

> **Not**: Partner Center portal'da referral sayısı ile buradaki X değerini kıyaslayın. Büyük fark varsa filtre/parsing kısmını debug etmek gerekir.

---

## 🎉 Başarı Kriterleri

✅ Token cache oluşturuldu  
✅ Token cache dosyası var (`ls -la .token_cache`)  
✅ Sync endpoint 200 döndü  
✅ Log'da `partner_center_referrals_fetched count=X` görünüyor  
✅ DB'de kayıt var (eğer Partner Center'da referral varsa)

**Tüm bunlar ✅ ise**: Partner Center entegrasyonu çalışıyor! 🎉

---

## 🚨 Sorun Giderme

### Problem: "Token acquisition failed"

**Çözüm**: ADIM 7'yi tekrar yap (browser'da login)

---

### Problem: "No accounts in cache"

**Çözüm**: ADIM 8'de `acquire_token_by_device_flow` başarılı oldu mu kontrol et

---

### Problem: Token cache dosyası yok

**Çözüm**: ADIM 9'da `token_cache.has_state_changed` kontrol et, `True` ise kaydetme işlemi çalışmalı

---

### Problem: Sync 500 döndü

**Çözüm**: 
1. Token cache dosyası var mı kontrol et (`ls -la .token_cache`)
2. Container'ı restart et: `docker-compose restart api worker`
3. Tekrar sync yap

---

### Problem: Token Cache'i Reset/Rotate Etmek İstiyorum

**Çözüm**: Token cache'i silip yeniden oluştur:

```bash
# Token cache'i sil
rm -f .token_cache

# Container'ı restart et
docker-compose restart api worker

# ADIM 1'den başlayarak Device Code Flow'u tekrar yap
```

---

## ⚠️ Production Uyarısı

**Bu adımları PROD ortamında çalıştıracaksan:**

1. ✅ **Volume mount doğru mu?** (`docker-compose.yml` veya Kubernetes deployment'ta `.token_cache` dosyası mount edilmiş mi?)
2. ✅ **Doğru tenant'a login oluyor musun?** (Production tenant ID ile mi, yoksa test tenant'ı ile mi?)
3. ✅ **Token cache dosyası kalıcı mı?** (Container restart sonrası kaybolmuyor mu?)

**Kontrol:**
```bash
# Volume mount kontrolü
docker-compose exec api ls -la .token_cache

# Token cache içeriği (opsiyonel, PII içerebilir)
docker-compose exec api cat .token_cache | head -5
```

**Önemli**: Production'da token cache dosyası güvenli bir yerde saklanmalı (encrypted volume, secure storage vb.)

---

**Son Güncelleme**: 2025-01-30

