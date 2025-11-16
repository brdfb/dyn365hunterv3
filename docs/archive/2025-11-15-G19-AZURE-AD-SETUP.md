# Azure AD Setup Guide (G19)

> ⚠️ **DEPRECATED** (2025-01-28): This feature has been removed. SSO implementation was not used in any core flows. Hunter now uses Internal Access Mode (network-level authentication). See CHANGELOG.md for details.

**Tarih**: 2025-01-28  
**Sprint**: G19 (Post-MVP Sprint 6)  
**Feature**: Microsoft SSO Authentication (REMOVED)

---

## 📋 Genel Bakış

Bu dokümantasyon, DomainHunter v3 için Microsoft Azure AD (Azure Active Directory) entegrasyonunu kurmak için adım adım talimatlar içerir.

### Gereksinimler

- Azure AD tenant (Microsoft 365 veya Azure AD)
- Azure Portal erişimi
- DomainHunter v3 backend erişimi (environment variables)

---

## 🔧 Adım 1: Azure AD App Registration

### 1.1 Azure Portal'a Giriş

1. [Azure Portal](https://portal.azure.com) adresine gidin
2. Azure AD tenant'ınızda oturum açın
3. **Azure Active Directory** > **App registrations** bölümüne gidin

### 1.2 Yeni App Registration Oluştur

1. **+ New registration** butonuna tıklayın
2. **Name**: `DomainHunter v3` (veya istediğiniz isim)
3. **Supported account types**: 
   - **Single tenant** (sadece kendi tenant'ınız)
   - **Multi-tenant** (tüm Azure AD tenant'ları)
4. **Redirect URI**: 
   - **Platform**: Web
   - **URI**: `http://localhost:8000/auth/callback` (development)
   - Production için: `https://yourdomain.com/auth/callback`
5. **Register** butonuna tıklayın

### 1.3 Application (Client) ID ve Tenant ID Kaydet

1. **Overview** sayfasında:
   - **Application (client) ID** → Kopyalayın (bu `AZURE_CLIENT_ID` olacak)
   - **Directory (tenant) ID** → Kopyalayın (bu `AZURE_TENANT_ID` olacak)

---

## 🔐 Adım 2: Client Secret Oluştur

### 2.1 Client Secret Oluştur

1. Sol menüden **Certificates & secrets** bölümüne gidin
2. **+ New client secret** butonuna tıklayın
3. **Description**: `DomainHunter v3 Secret` (veya istediğiniz açıklama)
4. **Expires**: 
   - **24 months** (önerilen)
   - **12 months** (daha güvenli)
   - **Never** (production için önerilmez)
5. **Add** butonuna tıklayın
6. **Value** kolonundaki secret değerini **hemen kopyalayın** (bir daha gösterilmeyecek!)
   - Bu `AZURE_CLIENT_SECRET` olacak

⚠️ **ÖNEMLİ**: Secret değerini güvenli bir yerde saklayın. Bir daha gösterilmeyecek!

---

## 🔗 Adım 3: Redirect URI Yapılandırması

### 3.1 Redirect URI Ekleme

1. Sol menüden **Authentication** bölümüne gidin
2. **+ Add a platform** butonuna tıklayın
3. **Web** platformunu seçin
4. **Redirect URIs** bölümüne ekleyin:
   - Development: `http://localhost:8000/auth/callback`
   - Production: `https://yourdomain.com/auth/callback`
5. **Configure** butonuna tıklayın

### 3.2 Implicit Grant (Opsiyonel)

- **Access tokens** ve **ID tokens** seçeneklerini işaretleyin (gerekirse)
- Genellikle gerekli değildir (authorization code flow kullanıyoruz)

---

## 📝 Adım 4: API Permissions (Opsiyonel)

### 4.1 Microsoft Graph API Permissions

1. Sol menüden **API permissions** bölümüne gidin
2. **+ Add a permission** butonuna tıklayın
3. **Microsoft Graph** > **Delegated permissions** seçin
4. Aşağıdaki permissions'ları ekleyin:
   - `openid` (OpenID Connect sign-in)
   - `profile` (View users' basic profile)
   - `email` (View users' email address)
   - `User.Read` (Sign in and read user profile)

⚠️ **Not**: Bu permissions genellikle default olarak eklenir. Kontrol edin.

### 4.2 Admin Consent (Gerekirse)

- **Grant admin consent** butonuna tıklayın (tenant admin iseniz)
- Veya tenant admin'den onay isteyin

---

## 🔧 Adım 5: Environment Variables Yapılandırması

### 5.1 Backend Environment Variables

DomainHunter v3 backend'inde aşağıdaki environment variables'ları ayarlayın:

```bash
# Azure AD Configuration
AZURE_CLIENT_ID=your-application-client-id
AZURE_CLIENT_SECRET=your-client-secret-value
AZURE_TENANT_ID=your-tenant-id
AZURE_REDIRECT_URI=http://localhost:8000/auth/callback  # Development
# AZURE_REDIRECT_URI=https://yourdomain.com/auth/callback  # Production
```

### 5.2 .env Dosyası Örneği

```env
# Azure AD (G19)
AZURE_CLIENT_ID=12345678-1234-1234-1234-123456789abc
AZURE_CLIENT_SECRET=your-secret-value-here
AZURE_TENANT_ID=87654321-4321-4321-4321-cba987654321
AZURE_REDIRECT_URI=http://localhost:8000/auth/callback
```

### 5.3 Docker Compose Örneği

```yaml
services:
  api:
    environment:
      - AZURE_CLIENT_ID=${AZURE_CLIENT_ID}
      - AZURE_CLIENT_SECRET=${AZURE_CLIENT_SECRET}
      - AZURE_TENANT_ID=${AZURE_TENANT_ID}
      - AZURE_REDIRECT_URI=${AZURE_REDIRECT_URI}
```

---

## ✅ Adım 6: Test Etme

### 6.1 Backend Test

1. Backend'i başlatın:
   ```bash
   docker-compose up api
   # veya
   python -m uvicorn app.main:app --reload
   ```

2. Auth endpoint'ini test edin:
   ```bash
   curl http://localhost:8000/auth/login
   ```
   - Azure AD login sayfasına redirect olmalı

### 6.2 OAuth Flow Test

1. Browser'da `http://localhost:8000/auth/login` adresine gidin
2. Microsoft hesabınızla giriş yapın
3. İzinleri onaylayın
4. `http://localhost:8000/auth/callback` adresine redirect olmalı
5. Frontend'e tokens ile redirect olmalı

### 6.3 Token Test

```bash
# Get access token (callback'den sonra)
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://localhost:8000/auth/me
```

---

## 🐛 Troubleshooting

### Problem: "Authentication is not configured"

**Çözüm**: Environment variables'ları kontrol edin:
```bash
echo $AZURE_CLIENT_ID
echo $AZURE_CLIENT_SECRET
echo $AZURE_TENANT_ID
```

### Problem: "Invalid redirect URI"

**Çözüm**: 
1. Azure Portal'da **Authentication** > **Redirect URIs** bölümünü kontrol edin
2. Backend'deki `AZURE_REDIRECT_URI` ile eşleştiğinden emin olun
3. URI'lerin tam olarak eşleştiğinden emin olun (http vs https, trailing slash, etc.)

### Problem: "AADSTS70011: Invalid scope"

**Çözüm**: 
1. Azure Portal'da **API permissions** bölümünü kontrol edin
2. `openid`, `profile`, `email`, `User.Read` permissions'larının ekli olduğundan emin olun

### Problem: "AADSTS50020: User account not found"

**Çözüm**: 
1. Kullanıcının Azure AD tenant'ında mevcut olduğundan emin olun
2. Multi-tenant yapılandırması kullanıyorsanız, kullanıcının doğru tenant'ta olduğundan emin olun

### Problem: Token verification fails

**Çözüm**:
1. JWT secret key'in doğru yapılandırıldığından emin olun
2. Token expiration time'ı kontrol edin
3. Redis bağlantısını kontrol edin (token revocation için)

---

## 🔒 Security Best Practices

### 1. Client Secret Güvenliği

- ✅ Client secret'ı **asla** version control'a commit etmeyin
- ✅ Environment variables veya secret management (Azure Key Vault, etc.) kullanın
- ✅ Secret'ı düzenli olarak rotate edin (24 months önerilir)

### 2. Redirect URI Güvenliği

- ✅ Production için HTTPS kullanın
- ✅ Sadece güvenilir domain'leri ekleyin
- ✅ Wildcard redirect URI'lerden kaçının

### 3. Token Güvenliği

- ✅ Access token'ları HTTP-only cookies'de saklayın (frontend)
- ✅ Refresh token'ları encrypt edin (Fernet encryption)
- ✅ Token revocation'ı etkinleştirin (Redis)

### 4. Multi-Tenant Yapılandırması

- ✅ Production için **single-tenant** önerilir (daha güvenli)
- ✅ Multi-tenant kullanıyorsanız, admin consent gerektirin

---

## 📚 Ek Kaynaklar

- [Microsoft Identity Platform Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [OAuth 2.0 Authorization Code Flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
- [MSAL Python Library](https://github.com/AzureAD/microsoft-authentication-library-for-python)

---

## ✅ Checklist

- [ ] Azure AD App Registration oluşturuldu
- [ ] Application (Client) ID kaydedildi
- [ ] Directory (Tenant) ID kaydedildi
- [ ] Client Secret oluşturuldu ve kaydedildi
- [ ] Redirect URI yapılandırıldı
- [ ] API Permissions eklendi
- [ ] Environment variables yapılandırıldı
- [ ] Backend test edildi
- [ ] OAuth flow test edildi
- [ ] Token verification test edildi

---

**Son Güncelleme**: 2025-01-28  
**Durum**: ✅ Ready for Production

