# IP Enrichment Docker Setup Guide

## Quick Setup Checklist

### 1. DB Dosyalarını Doğru Yere Koy

DB dosyalarını host'ta şu dizinlere yerleştir:

```text
project-root/
  app/
    data/
      maxmind/
        GeoLite2-City.mmdb
        GeoLite2-Country.mmdb  # Optional
      ip2location/
        IP2LOCATION-LITE-DB11.BIN
      ip2proxy/
        IP2PROXY-LITE-PX11.BIN
```

**Not**: Docker volume mapping sayesinde bu dosyalar container içinde `/app/app/data/...` path'inde otomatik olarak erişilebilir olacak.

### 2. Docker Compose Volume Mapping

`docker-compose.yml` içinde API servisi için volume mapping eklendi:

```yaml
services:
  api:
    volumes:
      - ./app/data:/app/app/data:ro  # IP enrichment DB files (read-only)
```

Bu mapping sayesinde:
- Host: `./app/data/...`
- Container: `/app/app/data/...`
- Read-only (`:ro`) - DB dosyaları sadece okunur

### 3. Env Değişkenlerini Aç

`.env` dosyasında (veya `docker-compose.yml` environment section'ında):

```env
# IP Enrichment - Enable for testing
HUNTER_ENRICHMENT_ENABLED=true

# MaxMind GeoIP Databases (container içi path)
MAXMIND_CITY_DB=app/data/maxmind/GeoLite2-City.mmdb
MAXMIND_COUNTRY_DB=app/data/maxmind/GeoLite2-Country.mmdb

# IP2Location & IP2Proxy (container içi path)
IP2LOCATION_DB=app/data/ip2location/IP2LOCATION-LITE-DB11.BIN
IP2PROXY_DB=app/data/ip2proxy/IP2PROXY-LITE-PX11.BIN
```

**Önemli**: Path'ler container içi path olarak tanımlı (`app/data/...`), çünkü container içinde working directory `/app` ve kod `app/data/...` path'ini kullanıyor.

### 4. Container'ı Rebuild ve Restart

```bash
# Rebuild API container (env değişiklikleri için)
docker-compose up -d --build api

# Veya tüm servisleri restart et
docker-compose restart api
```

### 5. Test Script'ini Container İçinde Çalıştır

```bash
# Test script'ini container içinde çalıştır
docker-compose exec api python -m scripts.test_ip_enrichment_validation
```

**Beklenen Çıktı**:
- IP resolution: ✅ 11/11 success
- Enrichment: ✅ Gerçek data (country, city, ISP, ASN, proxy signals)
- Logs: `ip_enrichment_success` mesajları

### 6. Sanity Check (Manuel)

Test sonuçlarından 2-3 önemli domain seç:

**TR Hosting Domain** (örn: `otega.com.tr`):
- ✅ `country` = "TR" (veya "Turkey")
- ✅ `isp` = Hosting firması adı (veya benzer)
- ✅ `usage_type` = "DATA CENTER" veya "CORPORATE" (hosting için normal)

**M365 Domain** (örn: `asteknikvana.com`):
- ✅ `country` = "TR" veya "US" (M365 global)
- ✅ `isp` = "Microsoft" veya benzer
- ✅ `usage_type` = "CORPORATE" veya "DATA CENTER"

**Global Big Tech** (örn: `microsoft.com`):
- ✅ `country` = "US" veya "EU"
- ✅ `isp` = "Microsoft" veya benzer
- ✅ `usage_type` = "CORPORATE"

### 7. Status Notu ve Flag Kararı

Test sonuçlarını `docs/active/IP-ENRICHMENT-STATUS.md` dosyasına ekle:

- Test edilen domain sayısı
- Genel doğruluk gözlemi
- Bilinen limitler
- MVP flag kararı:
  - **Prod'da false**: Sadece internal test ortamında true
  - **Prod'da true**: Data kalitesi kabul edilebilir, destekleyici yerlerde kullan

## Troubleshooting

### DB Files Not Found

**Hata**: `ip_enrichment_config_invalid` warning

**Çözüm**:
1. DB dosyalarının `app/data/...` altında olduğunu kontrol et
2. Docker volume mapping'in doğru olduğunu kontrol et
3. Container içinden kontrol et:
   ```bash
   docker-compose exec api ls -la /app/app/data/maxmind/
   docker-compose exec api ls -la /app/app/data/ip2location/
   docker-compose exec api ls -la /app/app/data/ip2proxy/
   ```

### Enrichment Still Disabled

**Hata**: Enrichment hala "skipped" görünüyor

**Çözüm**:
1. `.env` dosyasında `HUNTER_ENRICHMENT_ENABLED=true` olduğunu kontrol et
2. Container'ı restart et: `docker-compose restart api`
3. Log'larda `ip_enrichment_config_valid` mesajını kontrol et

### Path Issues

**Hata**: `FileNotFoundError` veya path hataları

**Çözüm**:
- Path'ler container içi path olmalı: `app/data/...` (host path değil)
- Docker volume mapping doğru olmalı: `./app/data:/app/app/data:ro`

## Next Steps

1. ✅ Docker setup tamamlandı
2. ⏳ Test script çalıştırılacak
3. ⏳ Sanity check yapılacak
4. ⏳ Status notu eklenecek
5. ⏳ Flag kararı verilecek

---

**Last Updated**: 2025-01-28  
**Status**: Setup ready, awaiting test execution

