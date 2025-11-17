# Partner Center API Permissions Kontrolü - 2025-01-28 (GÜNCELLENDİ)

**Tarih**: 2025-01-28  
**Durum**: ✅ **YETERLİ** - Delegated permissions mevcut (Application permissions yok ve olmaması normal)  
**Kapsam**: Azure AD App Registration - Partner Center API permissions

---

## 🔍 Mevcut Permissions (Azure Portal'dan)

### ✅ Var Olanlar (Delegated Permissions)

1. **Microsoft Graph (4 permissions)** - Delegated:
   - `email`, `openid`, `profile`, `User.Read`
   - **Durum**: SSO için yeterli, Partner Center için gerekli değil

2. **Microsoft Partner Center (3 entries)** - Delegated:
   - `user_impersonation` - "Partner Center" - ✅ Granted
   - `user_impersonation` - "Partner Center" - ✅ Granted
   - `user_impersonation` - "Access Partner Center" - ✅ Granted

---

## ✅ ÖNEMLİ: Application Permissions YOK ve OLMAMASI NORMAL

### Microsoft Partner Center Referrals API Gerçeği

**Referrals API sadece delegated permissions destekliyor, application permissions yok.**

Microsoft'un resmi dokümanları ve API tasarımı:
- ✅ **Delegated permissions**: `user_impersonation` (mevcut)
- ❌ **Application permissions**: `Referrals.Read/ReadWrite` **YOK** (ve olmaması normal)

**Neden?**
- Partner Center Referrals API, yalnızca **delegated `user_impersonation`** ile çalışıyor
- **App-only (client credentials)** modeli desteklenmiyor
- API, bir kullanıcı adına işlem yapmayı gerektiriyor

### Azure Portal'da Neden Göremiyorsun?

Azure Portal'da "Application permissions" altında `Referrals.Read` veya `Referrals.ReadWrite` aramak sonuçsuz kalır çünkü:
- Bu API için **application permissions mevcut değil**
- Portal doğru davranıyor, sen yanlış görmüyorsun
- Bu, API'nin mevcut tasarımına uygun

---

## 🔧 Background Sync İçin Çözüm: MSAL + Device Code Flow (Önerilen)

### Mevcut Durum
- ✅ **Delegated permissions** var (`user_impersonation`) - ✅ Yeterli
- ✅ **Admin consent** verilmiş - ✅ Yeterli

### Background Sync İçin Yaklaşım

Hunter'ın Partner Center entegrasyonu:
- **Background sync** (Celery task, scheduled polling)
- **Non-interactive** (kullanıcı login olmadan)
- **10 dakikada bir** otomatik sync

**Çözüm**: MSAL (Microsoft Authentication Library) + Device Code Flow

#### ⚠️ Neden ROPC Değil?

**ROPC (Resource Owner Password Credentials) flow:**
- ❌ MFA ile uyumsuz (MFA varsa çalışmaz)
- ❌ Conditional Access Policy ile uyumsuz
- ❌ Password saklama güvenlik riski
- ❌ Microsoft tarafından önerilmiyor

**MSAL + Device Code Flow:**
- ✅ MFA ile uyumlu (ilk login'de MFA, sonra sessiz token)
- ✅ Conditional Access Policy ile uyumlu
- ✅ Password saklamaya gerek yok
- ✅ Microsoft'un önerdiği yaklaşım (Secure App Model)

#### 1. Setup: Device Code Flow ile Bir Kere Login

**İlk kurulum (bir kere yapılır):**
1. Setup script çalıştır: `python scripts/setup_partner_center_auth.py`
2. Device code alınır, kullanıcıya gösterilir
3. Kullanıcı `https://microsoft.com/devicelogin` adresine gider
4. Device code'u girer, normal login yapar (MFA dahil)
5. Refresh token güvenli bir yerde saklanır (encrypted DB veya key vault)
6. Token cache oluşturulur

**Sonrasında:**
- Background job MSAL `acquire_token_silent()` kullanır
- Refresh token ile sessizce yeni access token alır
- MFA tekrar istenmez (policy özel bir şey dayatmıyorsa)

#### 2. MSAL Token Acquisition

```python
from msal import ConfidentialClientApplication, PublicClientApplication

# Setup (bir kere)
app = PublicClientApplication(
    client_id=CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}"
)

# Device code flow (setup sırasında)
flow = app.initiate_device_flow(scopes=["https://api.partner.microsoft.com/.default"])
print(f"Go to {flow['verification_uri']} and enter {flow['user_code']}")
result = app.acquire_token_by_device_flow(flow)

# Background job (her seferinde)
account = app.get_accounts()[0]
token = app.acquire_token_silent(
    scopes=["https://api.partner.microsoft.com/.default"],
    account=account
)
```

#### 3. Token Cache Yönetimi

- MSAL otomatik token cache yönetir
- Refresh token'ı güvenli sakla (encrypted)
- Token cache file path configurable

---

## 📋 Checklist

### Mevcut Durum
- [x] ✅ Delegated permissions var (`user_impersonation`)
- [x] ✅ Admin consent verilmiş (Delegated için)
- [x] ✅ **Application permissions YOK** (ve olmaması normal - API bunu desteklemiyor)

### Yapılması Gerekenler
- [ ] ⚠️ Service user oluştur (Referrals Admin/User rolü ile) - MFA açık kalabilir
- [ ] ⚠️ Setup script çalıştır: Device code flow ile bir kere login (MFA dahil)
- [ ] ⚠️ Refresh token'ı güvenli sakla (encrypted DB veya key vault)
- [ ] ⚠️ `PartnerCenterClient` implementasyonunu MSAL + Device Code Flow kullanacak şekilde güncelle
- [ ] ⚠️ Token cache yönetimi implementasyonu

---

## 🎯 Sonuç

**Durum**: ✅ **YETERLİ** - Delegated permissions mevcut ve yeterli

**Mevcut**: Delegated `user_impersonation` var ve admin consent verilmiş ✅  
**Gerekli**: Service user + ROPC flow implementasyonu (Application permissions değil!)

**Aksiyon**: 
1. Service user oluştur (Referrals Admin/User rolü) - MFA açık kalabilir
2. Setup script çalıştır: Device code flow ile bir kere login (MFA dahil)
3. MSAL + Device Code Flow implementasyonu yap
4. Token cache yönetimi implementasyonu

**Not**: Application permissions aramayı bırak - yok ve olmaması normal. API sadece delegated destekliyor. ROPC flow MFA ile uyumsuz, bu yüzden MSAL + Device Code Flow kullanılmalı.

---

**Son Güncelleme**: 2025-01-28 (Revize edildi - Application permissions yok, MSAL + Device Code Flow yaklaşımı)  
**Durum**: ✅ **YETERLİ** - Sadece MSAL + Device Code Flow implementasyonu gerekiyor (MFA uyumlu)

