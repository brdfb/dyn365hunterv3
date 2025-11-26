# FAZ 2: Device Code Flow - Manuel Adımlar

**Durum**: FAZ 0 ve FAZ 1 PASSED ✅  
**Sıra**: FAZ 2 - Device Code Flow Authentication

---

## Adım 1: Python Shell'e Gir

```bash
docker-compose exec api python
```

---

## Adım 2: Device Code Flow Script'ini Çalıştır

Python shell'de şu kodu çalıştır:

```python
from msal import PublicClientApplication
from app.config import settings

# Check configuration
if not all([settings.partner_center_client_id, settings.partner_center_tenant_id, settings.partner_center_api_url]):
    print('❌ ERROR: Partner Center credentials not configured!')
    exit(1)

# Create MSAL app
authority = f'https://login.microsoftonline.com/{settings.partner_center_tenant_id}'
app = PublicClientApplication(
    client_id=settings.partner_center_client_id,
    authority=authority,
)

print('=' * 60)
print('Partner Center - Device Code Flow Authentication')
print('=' * 60)
print()

# Initiate device code flow
flow = app.initiate_device_flow(scopes=[settings.partner_center_scope])

# Display instructions
print('📱 Authentication Instructions:')
print()
print(f'1. Open your browser and go to:')
print(f'   {flow["verification_uri"]}')
print()
print(f'2. Enter this code:')
print(f'   {flow["user_code"]}')
print()
print('3. Complete the authentication (login + consent)')
print('   (MFA will be required if enabled)')
print()
print('=' * 60)
print('⏳ Waiting for authentication...')
print('   (This may take up to 15 minutes)')
print('=' * 60)
print()

# Wait for authentication
result = app.acquire_token_by_device_flow(flow)

# Check result
if 'access_token' in result:
    print('✅ SUCCESS: Token acquired!')
    print()
    print('Token Information:')
    print(f'  - Expires in: {result.get("expires_in", "N/A")} seconds')
    print(f'  - Token type: {result.get("token_type", "N/A")}')
    print(f'  - Scope: {result.get("scope", "N/A")}')
    print()
    print('Token cache saved to: .token_cache')
    print()
    print('✅ FAZ 2 PASSED: Authentication successful!')
else:
    print('❌ ERROR: Token acquisition failed')
    print()
    print('Error details:')
    print(f'  - Error: {result.get("error", "Unknown")}')
    print(f'  - Description: {result.get("error_description", "N/A")}')
```

---

## Adım 3: Browser'da Login Yap

1. Script'in gösterdiği URL'ye git
2. Verilen kodu gir
3. Login + consent ver (MFA dahil)
4. Python shell'de token gelene kadar bekle

---

## Adım 4: Silent Token Test (Opsiyonel)

Token cache oluştuktan sonra, silent token acquisition'ı test et:

```python
from app.core.partner_center import PartnerCenterClient

# Not: Feature flag OFF olsa bile test için geçici olarak açabilirsin
# Veya direkt MSAL ile test edebilirsin:

accounts = app.get_accounts()
if accounts:
    account = accounts[0]
    result = app.acquire_token_silent(
        scopes=[settings.partner_center_scope],
        account=account
    )
    if result and 'access_token' in result:
        print('✅ SUCCESS: Silent token acquisition works!')
        print(f'   Token: {result["access_token"][:20]}...')
    else:
        print('❌ ERROR: Silent token acquisition failed')
else:
    print('❌ ERROR: No accounts found in cache')
```

---

## Beklenen Sonuç

✅ **SUCCESS**: Token acquired + Token cache saved  
✅ **Silent Test**: Silent token acquisition works

**Sonra**: FAZ 3'e geç (Feature Flag ON + Integration Test)

---

## Troubleshooting

### Problem: Token acquisition failed

**Olası nedenler**:
1. Azure AD App Registration permissions eksik
2. Partner Center API permissions eksik
3. Admin consent gerekli
4. CLIENT_ID veya TENANT_ID yanlış

**Çözüm**:
1. Azure Portal'da App Registration'ı kontrol et
2. Partner Center API permissions'ı kontrol et
3. Admin consent ver
4. .env dosyasındaki credentials'ı kontrol et

---

**Son Güncelleme**: 2025-01-30

