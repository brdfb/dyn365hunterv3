# IP Enrichment - Quick Start Setup Guide

**Durum**: ✅ Kod hazır, sadece DB dosyalarını indirip flag'i açmanız gerekiyor  
**Süre**: ~10 dakika  
**Gereksinimler**: 3 ücretsiz DB dosyası indirip proje dizinine koymak

---

## 🎯 Özet

IP Enrichment feature'ı **teknik olarak tamamen hazır**. Tek eksik: 3 DB dosyasını indirip `.env`'ye path yazmak.

**Şu anda**: Feature flag kapalı → Hunter hiçbir davranış değişikliği yapmıyor  
**Açtıktan sonra**: `infrastructure_summary` field'ı API response'larda görünecek

---

## 📥 Adım 1: DB Dosyalarını İndir

### 1.1 MaxMind GeoLite2 (2 dosya)

**Kayıt**: https://www.maxmind.com/en/geolite2/signup
- Ücretsiz hesap oluştur (email + şifre)
- Email doğrulama yap

**İndirme**:
1. Login ol: https://www.maxmind.com/en/accounts/current/geoip/downloads
2. **GeoLite2-City** → Download `GeoLite2-City.mmdb` (required)
3. **GeoLite2-Country** → Download `GeoLite2-Country.mmdb` (optional fallback)
4. **GeoLite2-ASN** → Download `GeoLite2-ASN.mmdb` (optional - only if you need ASN data)

**Not**: MaxMind artık GeoLite2'yi ücretsiz dağıtmıyor, ama eski versiyonları hala bulunabilir. Alternatif olarak MaxMind'in ücretli GeoIP2 servisini kullanabilirsiniz.

### 1.2 IP2Location LITE (1 dosya)

**İndirme**: https://lite.ip2location.com/
- Email adresi gir
- **IP2Location LITE Database** → Download `IP2LOCATION-LITE-DB11.BIN`
- Email'deki download link'ini kullan

### 1.3 IP2Proxy LITE (1 dosya)

**İndirme**: https://lite.ip2proxy.com/
- Email adresi gir
- **IP2Proxy LITE Database** → Download `IP2PROXY-LITE-PX11.BIN`
- Email'deki download link'ini kullan

---

## 📁 Adım 2: Dosyaları Proje Dizinine Koy

### 2.1 Dizin Yapısını Oluştur

```bash
# Proje root dizininde
mkdir -p app/data/maxmind
mkdir -p app/data/ip2location
mkdir -p app/data/ip2proxy
```

### 2.2 Dosyaları Kopyala

**Windows (PowerShell/Git Bash)**:
```bash
# MaxMind dosyaları
copy "C:\Downloads\GeoLite2-City.mmdb" "app\data\maxmind\"
copy "C:\Downloads\GeoLite2-Country.mmdb" "app\data\maxmind\"
# copy "C:\Downloads\GeoLite2-ASN.mmdb" "app\data\maxmind\"  # Optional

# IP2Location
copy "C:\Downloads\IP2LOCATION-LITE-DB11.BIN" "app\data\ip2location\"

# IP2Proxy
copy "C:\Downloads\IP2PROXY-LITE-PX11.BIN" "app\data\ip2proxy\"
```

**Linux/WSL**:
```bash
# MaxMind dosyaları
cp ~/Downloads/GeoLite2-City.mmdb app/data/maxmind/
cp ~/Downloads/GeoLite2-Country.mmdb app/data/maxmind/
# cp ~/Downloads/GeoLite2-ASN.mmdb app/data/maxmind/  # Optional

# IP2Location
cp ~/Downloads/IP2LOCATION-LITE-DB11.BIN app/data/ip2location/

# IP2Proxy
cp ~/Downloads/IP2PROXY-LITE-PX11.BIN app/data/ip2proxy/
```

### 2.3 Dosya Kontrolü

```bash
# Kontrol et
ls -lh app/data/maxmind/
ls -lh app/data/ip2location/
ls -lh app/data/ip2proxy/
```

**Beklenen çıktı**:
```
app/data/maxmind/
  - GeoLite2-City.mmdb (~50-70 MB)        # Required
  - GeoLite2-Country.mmdb (~2-5 MB)       # Optional fallback
  - GeoLite2-ASN.mmdb (~5-10 MB)          # Optional

app/data/ip2location/
  - IP2LOCATION-LITE-DB11.BIN (~100-150 MB)

app/data/ip2proxy/
  - IP2PROXY-LITE-PX11.BIN (~50-100 MB)
```

---

## ⚙️ Adım 3: .env Dosyasını Güncelle

### 3.1 .env Dosyasını Aç

```bash
# Proje root dizininde
code .env  # veya notepad .env, nano .env, vs.
```

### 3.2 Enrichment Config'i Aktif Et

`.env` dosyasına şunları ekle (veya yorum satırlarını kaldır):

```bash
# IP Enrichment (Feature flag: enabled)
HUNTER_ENRICHMENT_ENABLED=true

# MaxMind GeoIP Databases (new format - recommended)
MAXMIND_CITY_DB=app/data/maxmind/GeoLite2-City.mmdb
MAXMIND_COUNTRY_DB=app/data/maxmind/GeoLite2-Country.mmdb
# MAXMIND_ASN_DB=app/data/maxmind/GeoLite2-ASN.mmdb  # Optional - only add if you use ASN database

# IP2Location & IP2Proxy
IP2LOCATION_DB=app/data/ip2location/IP2LOCATION-LITE-DB11.BIN
IP2PROXY_DB=app/data/ip2proxy/IP2PROXY-LITE-PX11.BIN
```

**Not**: 
- Path'ler relative path (`app/data/...`) veya absolute path (`/app/data/...`) olabilir
- Docker container içinde `/app/data/...` formatı kullanılabilir
- Local development için `app/data/...` formatı önerilir
- ASN database opsiyoneldir - sadece kullanıyorsanız ekleyin

---

## 🐳 Adım 4: Docker Compose'u Yeniden Başlat

### 4.1 Container'ları Durdur

```bash
docker-compose down
```

### 4.2 Yeniden Başlat

```bash
docker-compose up -d
```

**Not**: `app/data/` dizini Docker volume'üne mount edilmiş olmalı. `docker-compose.yml`'de kontrol edin:

```yaml
volumes:
  - ./app/data:/app/data
```

---

## ✅ Adım 5: Test Et

### 5.1 Health Check

```bash
curl http://localhost:8000/healthz | jq '.enrichment_enabled'
```

**Beklenen**: `true`

### 5.2 Config Check

```bash
curl http://localhost:8000/debug/ip-enrichment/config | jq '.availability'
```

**Beklenen**:
```json
{
  "at_least_one_db_available": true
}
```

### 5.3 Test Enrichment

```bash
curl http://localhost:8000/debug/ip-enrichment/8.8.8.8 | jq '.enrichment'
```

**Beklenen**: Enrichment data (ASN, country, ISP, etc.)

### 5.4 API Response Test

```bash
# Bir domain scan et
curl -X POST http://localhost:8000/scan/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'

# Lead'i getir
curl http://localhost:8000/leads/example.com | jq '.infrastructure_summary'
```

**Beklenen**: `"Hosted on DataCenter, ISP: Google, Country: US"` gibi bir string

---

## 🚨 Sorun Giderme

### Problem: `at_least_one_db_available: false`

**Çözüm**:
1. Dosyaların doğru yerde olduğunu kontrol et:
   ```bash
   docker-compose exec api ls -lh /app/data/maxmind/
   ```
2. Path'lerin doğru olduğunu kontrol et (`.env` dosyasında)
3. Container'ı yeniden başlat:
   ```bash
   docker-compose restart api
   ```

### Problem: `infrastructure_summary: null`

**Nedenler**:
1. Domain'in IP'si resolve edilemedi (MX record yok)
2. Enrichment DB'lerinde IP için data yok
3. Enrichment henüz çalışmadı (ilk scan'den sonra enrichment çalışır)

**Çözüm**:
- Debug endpoint'i kullan: `GET /debug/ip-enrichment/{ip}`
- Log'ları kontrol et: `docker-compose logs api | grep enrichment`

### Problem: MaxMind dosyaları bulunamıyor

**Not**: MaxMind artık GeoLite2'yi ücretsiz dağıtmıyor. Alternatifler:
1. MaxMind'in ücretli GeoIP2 servisini kullan
2. Eski GeoLite2 versiyonlarını bul (archive'lerden)
3. Sadece IP2Location + IP2Proxy kullan (MaxMind olmadan da çalışır)

---

## 📋 Checklist

- [ ] MaxMind hesabı oluşturuldu
- [ ] `GeoLite2-City.mmdb` indirildi → `app/data/maxmind/` (required)
- [ ] `GeoLite2-Country.mmdb` indirildi → `app/data/maxmind/` (optional fallback)
- [ ] `GeoLite2-ASN.mmdb` indirildi → `app/data/maxmind/` (optional - only if needed)
- [ ] `IP2LOCATION-LITE-DB11.BIN` indirildi → `app/data/ip2location/`
- [ ] `IP2PROXY-LITE-PX11.BIN` indirildi → `app/data/ip2proxy/`
- [ ] `.env` dosyası güncellendi (yeni format: `MAXMIND_*`, `IP2LOCATION_DB`, `IP2PROXY_DB`)
- [ ] Docker Compose yeniden başlatıldı
- [ ] `.env` dosyası güncellendi (`HUNTER_ENRICHMENT_ENABLED=true`)
- [ ] Docker container'lar yeniden başlatıldı
- [ ] `/healthz` endpoint'i `enrichment_enabled: true` döndürüyor
- [ ] `/debug/ip-enrichment/config` `at_least_one_db_available: true` döndürüyor
- [ ] Test enrichment çalışıyor (`/debug/ip-enrichment/8.8.8.8`)
- [ ] API response'da `infrastructure_summary` görünüyor

---

## 🎯 Sonraki Adımlar

Setup tamamlandıktan sonra:

1. **Stage Environment**: Aynı setup'ı stage'de yap
2. **Production Rollout**: Rollout planını takip et (`docs/active/IP-ENRICHMENT-IMPLEMENTATION.md` → Deployment Strategy)
3. **Monitoring**: Sentry'de `hunter_enrichment_error` tag'ini izle
4. **Verification**: `ip_enrichment` tablosunda data biriktiğini kontrol et

---

## 📚 İlgili Dokümantasyon

- **Implementation Guide**: `docs/active/IP-ENRICHMENT-IMPLEMENTATION.md`
- **Rollout Plan**: `docs/active/IP-ENRICHMENT-IMPLEMENTATION.md` → Deployment Strategy
- **API Documentation**: `README.md` → API Endpoints → Leads

---

**Durum**: ✅ Setup rehberi hazır - Sadece dosyaları indirip flag'i açmanız yeterli!

