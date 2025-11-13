# Dyn365Hunter - Satış Ekibi Kullanım Kılavuzu

**Hızlı Başlangıç Rehberi** - 5 dakikada başlayın!

---

## 🚀 Hızlı Başlangıç (5 Dakika)

### 1. Sistemi Başlatın

```bash
# Proje klasörüne gidin
cd /path/to/dyn365hunterv3

# Sistemi başlatın (ilk kez)
bash setup_dev.sh

# Sistem çalışıyor mu kontrol edin
curl http://localhost:8000/healthz
```

**Beklenen Sonuç:**
```json
{
  "status": "ok",
  "database": "connected",
  "environment": "development"
}
```

✅ Sistem hazır!

---

## 📋 Temel İş Akışı

### Senaryo: Yeni Bir Domain Analiz Etmek

**3 Adım:**
1. **Domain Ekle** → Domain'i sisteme ekle
2. **Analiz Et** → DNS/WHOIS analizi yap, skor hesapla
3. **Sonuçları Gör** → Lead listesinden sonuçları görüntüle

---

## 📥 Adım 1: Domain Ekleme

### Tek Domain Ekleme

```bash
curl -X POST http://localhost:8000/ingest/domain \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "ornek-firma.com",
    "company_name": "Örnek Firma A.Ş.",
    "email": "info@ornek-firma.com",
    "website": "https://www.ornek-firma.com"
  }'
```

**Önemli Notlar:**
- `domain` zorunlu (otomatik normalize edilir: büyük/küçük harf, www kaldırılır)
- `company_name`, `email`, `website` opsiyonel
- Email veya website'den domain otomatik çıkarılır

**Başarılı Yanıt:**
```json
{
  "domain": "ornek-firma.com",
  "company_id": 1,
  "message": "Domain ornek-firma.com ingested successfully"
}
```

### CSV ile Toplu Ekleme

```bash
curl -X POST http://localhost:8000/ingest/csv \
  -F "file=@domain-listesi.csv"
```

**CSV Formatı:**
```csv
domain,company_name,email,website
ornek1.com,Örnek 1 A.Ş.,info@ornek1.com,https://www.ornek1.com
ornek2.com,Örnek 2 Ltd.,,https://www.ornek2.com
ornek3.com,,info@ornek3.com,
```

**Not:** CSV'de sadece `domain` kolonu zorunlu, diğerleri opsiyonel.

---

## 🔍 Adım 2: Domain Analizi (Scan)

Domain'i analiz edip skor hesaplama:

```bash
curl -X POST http://localhost:8000/scan/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "ornek-firma.com"}'
```

**Ne Yapıyor?**
- DNS kayıtlarını kontrol eder (MX, SPF, DKIM, DMARC)
- WHOIS bilgilerini çeker (opsiyonel, başarısız olursa devam eder)
- Provider'ı tespit eder (M365, Google, Yandex, vb.)
- **Readiness Score** hesaplar (0-100)
- **Segment** belirler (Migration, Existing, Cold, Skip)

**Süre:** 10-15 saniye (soğuk başlangıç: 15-20 saniye)

**Başarılı Yanıt:**
```json
{
  "domain": "ornek-firma.com",
  "score": 85,
  "segment": "Migration",
  "reason": "High readiness score with known cloud provider. Score: 85, Provider: M365",
  "provider": "M365",
  "mx_root": "outlook.com",
  "spf": true,
  "dkim": true,
  "dmarc_policy": "reject",
  "scan_status": "success"
}
```

**Skor Ne Anlama Geliyor?**
- **70-100**: Yüksek hazırlık → Hemen aksiyon alınabilir
- **50-69**: Orta hazırlık → Takip edilebilir
- **20-49**: Düşük hazırlık → Daha fazla sinyal gerekli
- **0-19**: Çok düşük → Şimdilik atlanabilir

**Segment Ne Anlama Geliyor?**
- **Migration**: Yüksek öncelik, hemen iletişime geç
- **Existing**: Zaten müşteri olabilir, takip et
- **Cold**: Düşük öncelik, daha fazla sinyal gerekli
- **Skip**: Şimdilik atla

Detaylı açıklama için: [SEGMENT-GUIDE.md](SEGMENT-GUIDE.md)

---

## 📊 Adım 3: Lead Listesini Görüntüleme

### Tüm Lead'leri Görüntüle

```bash
curl "http://localhost:8000/leads"
```

### Filtreleme

#### Migration Segment'i (Yüksek Öncelik)

```bash
curl "http://localhost:8000/leads?segment=Migration&min_score=70"
```

**Ne Döner?**
- Segment: Migration
- Skor: 70 ve üzeri
- **Priority Score**: 1-2 (yüksek öncelik)
- Sıralama: Yüksek skordan düşüğe

#### Belirli Provider (Örn: M365)

```bash
curl "http://localhost:8000/leads?provider=M365&min_score=50"
```

#### Kombine Filtre

```bash
curl "http://localhost:8000/leads?segment=Migration&min_score=70&provider=M365"
```

**Filtre Seçenekleri:**
- `segment`: Migration, Existing, Cold, Skip
- `min_score`: Minimum skor (0-100)
- `provider`: M365, Google, Yandex, Zoho, Amazon, SendGrid, Mailgun, Hosting, Local, Unknown

### Tek Lead Detayı

```bash
curl "http://localhost:8000/leads/ornek-firma.com"
```

**Ne Döner?**
- Tüm domain bilgileri
- DNS sinyalleri (SPF, DKIM, DMARC)
- WHOIS bilgileri
- Skor ve segment detayları
- **Priority Score** (1-6, 1 en yüksek öncelik)
- Güncelleme tarihleri

**Priority Score Nedir?**
- **1**: Migration + Skor 80+ → En yüksek öncelik
- **2**: Migration + Skor 70-79 → Yüksek öncelik
- **3**: Existing + Skor 70+ → Orta-yüksek öncelik
- **4**: Existing + Skor 50-69 → Orta öncelik
- **5**: Cold + Skor 40+ → Düşük öncelik
- **6**: Diğerleri → En düşük öncelik

### Dashboard (Özet Görünüm)

```bash
curl "http://localhost:8000/dashboard"
```

**Ne Döner?**
```json
{
  "total_leads": 150,
  "migration": 25,
  "existing": 50,
  "cold": 60,
  "skip": 15,
  "avg_score": 55.5,
  "high_priority": 10
}
```

**Ne İşe Yarar?**
- Hızlı özet görünüm
- Segment dağılımını görme
- Ortalama skor takibi
- Yüksek öncelikli lead sayısı (Migration + skor >= 70)

---

## 🎯 Pratik Senaryolar

### Senaryo 1: Yeni Lead Listesi Analizi

```bash
# 1. CSV'den domain'leri ekle
curl -X POST http://localhost:8000/ingest/csv \
  -F "file=@yeni-leadler.csv"

# 2. Her domain'i analiz et (toplu yapmak için script kullanın)
# Örnek: scripts/sales-demo.sh

# 3. Dashboard ile genel durumu gör
curl "http://localhost:8000/dashboard"

# 4. Migration segment'indeki yüksek skorlu lead'leri görüntüle
curl "http://localhost:8000/leads?segment=Migration&min_score=70"
```

### Senaryo 2: Tek Domain Hızlı Kontrol

```bash
# 1. Domain ekle
curl -X POST http://localhost:8000/ingest/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "yeni-firma.com", "company_name": "Yeni Firma"}'

# 2. Analiz et
curl -X POST http://localhost:8000/scan/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "yeni-firma.com"}'

# 3. Sonucu gör
curl "http://localhost:8000/leads/yeni-firma.com"
```

### Senaryo 3: Mevcut Müşteri Takibi

```bash
# Existing segment'indeki lead'leri görüntüle
curl "http://localhost:8000/leads?segment=Existing&min_score=50"
```

Detaylı senaryolar için: [SALES-SCENARIOS.md](SALES-SCENARIOS.md)

---

## 🛠️ Hızlı Komutlar (Kopyala-Yapıştır)

### Sistem Kontrolü
```bash
curl http://localhost:8000/healthz
```

### Domain Ekle
```bash
curl -X POST http://localhost:8000/ingest/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "DOMAIN-BURAYA", "company_name": "Firma Adı"}'
```

### Analiz Et
```bash
curl -X POST http://localhost:8000/scan/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "DOMAIN-BURAYA"}'
```

### Migration Lead'leri Gör
```bash
curl "http://localhost:8000/leads?segment=Migration&min_score=70"
```

### Tek Lead Detayı
```bash
curl "http://localhost:8000/leads/DOMAIN-BURAYA"
```

### Dashboard Özeti
```bash
curl "http://localhost:8000/dashboard"
```

---

## 📖 API Dokümantasyonu

Tarayıcınızda açın:
```
http://localhost:8000/docs
```

**Ne Var?**
- Tüm endpoint'lerin listesi
- Request/Response örnekleri
- Interaktif test (doğrudan tarayıcıdan test edebilirsiniz)

---

## ❓ Sık Sorulan Sorular

### Q: Domain'i ekledim ama analiz yapamıyorum?
**A:** Önce `/ingest/domain` ile domain'i eklemelisiniz, sonra `/scan/domain` ile analiz edebilirsiniz.

### Q: Analiz ne kadar sürer?
**A:** Normalde 10-15 saniye. İlk analiz (soğuk başlangıç) 15-20 saniye sürebilir.

### Q: CSV'den ekledim, otomatik analiz olmuyor mu?
**A:** Hayır. CSV sadece domain'leri ekler. Analiz için `/scan/domain` endpoint'ini kullanmalısınız.

### Q: Skor 0-100 arası, hangisi iyi?
**A:** 
- **70-100**: Çok iyi → Hemen aksiyon
- **50-69**: İyi → Takip et
- **20-49**: Orta → Daha fazla sinyal gerekli
- **0-19**: Düşük → Şimdilik atla

### Q: Segment'ler ne anlama geliyor?
**A:** Detaylı açıklama için [SEGMENT-GUIDE.md](SEGMENT-GUIDE.md) dosyasına bakın.

### Q: Hangi provider'lar destekleniyor?
**A:** M365, Google, Yandex, Zoho, Amazon, SendGrid, Mailgun, Hosting, Local, Unknown

### Q: Sistem çalışmıyor, ne yapmalıyım?
**A:** 
1. `curl http://localhost:8000/healthz` ile kontrol edin
2. Docker container'ları çalışıyor mu kontrol edin: `docker-compose ps`
3. Log'lara bakın: `docker-compose logs api`

---

## 🎬 Hızlı Demo

Hazır demo script'i çalıştırın:

```bash
bash scripts/sales-demo.sh
```

Bu script:
- 3 örnek domain ekler
- Her birini analiz eder
- Migration segment'indeki yüksek skorlu lead'leri gösterir

---

## 📞 Yardım

**Teknik Sorunlar:**
- API Dokümantasyonu: http://localhost:8000/docs
- README.md: Proje kök dizininde

**Kullanım Soruları:**
- [SEGMENT-GUIDE.md](SEGMENT-GUIDE.md) - Segment ve skor açıklamaları
- [SALES-SCENARIOS.md](SALES-SCENARIOS.md) - Pratik senaryolar

---

## 🎯 Özet: 3 Adımda Başlayın

1. **Domain Ekle**
   ```bash
   curl -X POST http://localhost:8000/ingest/domain \
     -H "Content-Type: application/json" \
     -d '{"domain": "ornek.com", "company_name": "Örnek Firma"}'
   ```

2. **Analiz Et**
   ```bash
   curl -X POST http://localhost:8000/scan/domain \
     -H "Content-Type: application/json" \
     -d '{"domain": "ornek.com"}'
   ```

3. **Sonuçları Gör**
   ```bash
   # Dashboard ile özet görünüm
   curl "http://localhost:8000/dashboard"
   
   # Detaylı lead listesi (Priority Score ile)
   curl "http://localhost:8000/leads?segment=Migration&min_score=70"
   ```

**Hepsi bu kadar! 🎉**

**İpucu:** Priority Score 1-2 olan lead'lere öncelik verin!

