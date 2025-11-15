# Dyn365Hunter - Satış Senaryoları

**Gerçek Hayat Senaryoları ve En İyi Pratikler**

---

## 📋 Senaryo 1: Yeni Lead Listesi Analizi

### Durum
Satış ekibi yeni bir lead listesi aldı (100 domain). Hangi domain'ler öncelikli?

### Mini UI ile Hızlı Analiz (Önerilen) 🖥️

1. **Mini UI'yi Aç**
   ```
   http://localhost:8000/mini-ui/
   ```

2. **CSV/Excel Yükle**
   - Dosya seç (CSV veya Excel)
   - Otomatik kolon tespiti (OSB dosyaları için checkbox'ı işaretle)
   - "Yükle ve İşle" butonuna tıkla
   - **Progress bar** ile ilerlemeyi takip et (işlenen, kalan, başarılı, başarısız)
   - Başarı mesajını bekle (domain'ler otomatik olarak scan edilir)

3. **Domain'leri Tara (Opsiyonel)**
   - Her domain için "Tek Domain Tara" formunu kullan
   - Domain + şirket adı gir
   - "Tara" butonuna tıkla (otomatik ingest + scan yapar)
   - Sonuçları gör
   - **Not:** CSV upload ile otomatik scan yapıldıysa, bu adım gerekli değildir

4. **Lead'leri Gör ve Filtrele** (G19: UI Upgrade) ✨ YENİ
   - Segment filtresi: Migration
   - Min skor: 70
   - **Search** (G19): Arama kutusuna domain veya şirket adı yaz (anlık arama)
   - **Sorting** (G19): Tablo başlıklarına tıklayarak sıralama (skor, domain, segment)
   - **Pagination** (G19): Sayfa numaraları ile sayfalama (10, 25, 50, 100 kayıt/sayfa)
   - "Filtrele" butonuna tıkla
   - Tabloda yüksek öncelikli lead'leri gör
   - **Score Breakdown** (G19): Skorlara tıklayarak detaylı skor analizi modal'ı aç

5. **Export Et**
   - Filtreleri ayarla
   - "Export CSV" butonuna tıkla
   - Dosya otomatik indirilir

**Avantajlar:**
- ✅ Kolay kullanım (tarayıcıdan)
- ✅ Görsel arayüz
- ✅ Otomatik refresh
- ✅ Hızlı export

### API ile Analiz (Alternatif) 💻

### Dashboard ile Hızlı Kontrol
```bash
# Legacy dashboard (backward compatible)
curl "http://localhost:8000/dashboard"

# New KPI endpoint (G19) ✨ YENİ
curl "http://localhost:8000/dashboard/kpis"
```

**Örnek Sonuç:**
```json
{
  "total_leads": 100,
  "migration": 15,
  "existing": 25,
  "cold": 40,
  "skip": 20,
  "avg_score": 45.5,
  "high_priority": 8
}
```

**Yorum:**
- 15 Migration lead var → Hemen bakılmalı
- 8 yüksek öncelikli lead (Priority 1-2) → En öncelikli
- Ortalama skor 45.5 → Genel olarak orta seviye

### Adımlar

#### 1. CSV/Excel'den Domain'leri Ekle (Otomatik Scan ile) ⚡ YENİ
```bash
# CSV dosyası (otomatik scan ile - önerilen)
curl -X POST "http://localhost:8000/ingest/csv?auto_scan=true" \
  -F "file=@yeni-leadler.csv"

# Excel dosyası (OSB formatı için otomatik kolon tespiti + otomatik scan)
curl -X POST "http://localhost:8000/ingest/csv?auto_detect_columns=true&auto_scan=true" \
  -F "file=@yeni-leadler.xlsx"
```

**Otomatik Scan (`auto_scan=true`):**
- ✅ Domain'ler yüklendikten sonra otomatik olarak scan edilir
- ✅ Her domain için DNS/WHOIS analizi yapılır ve skor hesaplanır
- ✅ Sonuçlar otomatik olarak lead listesine eklenir
- ✅ **Progress tracking**: İşlem sırasında ilerleme takibi yapılabilir (job_id ile)

**Progress Tracking:**
```bash
# CSV yükleme sonrası job_id alınır
# İlerleme durumunu kontrol etmek için:
curl "http://localhost:8000/jobs/{job_id}"

# Yanıt:
{
  "job_id": "...",
  "status": "processing",
  "processed": 50,
  "total": 100,
  "successful": 48,
  "failed": 2,
  "progress_percent": 50.0,
  "message": "İşleniyor: 50/100 domain yüklendi"
}
```

**Not:** `auto_scan=false` (default) → Sadece domain'leri ekler, scan yapmaz (eski davranış).

**CSV/Excel Formatı:**
```csv
domain,company_name,email,website
firma1.com,Firma 1 A.Ş.,info@firma1.com,https://www.firma1.com
firma2.com,Firma 2 Ltd.,,https://www.firma2.com
firma3.com,,info@firma3.com,
```

**Excel Otomatik Kolon Tespiti:**
- OSB Excel dosyaları için `auto_detect_columns=true` kullanın
- Firma/şirket ve domain kolonlarını otomatik tespit eder
- Standart CSV formatı için `auto_detect_columns=false` (default) yeterli

#### 2. Toplu Analiz (Bulk Scan) ⚡ YENİ

**Not:** `auto_scan=true` kullanıyorsanız, bu adım gerekli değildir. Domain'ler otomatik olarak scan edilir.

**Bulk Scan (Önerilen - 10+ Domain için):**
```bash
# Domain listesini hazırla (CSV'den veya manuel)
DOMAINS='["domain1.com", "domain2.com", "domain3.com", ...]'

# Bulk scan job oluştur
RESPONSE=$(curl -X POST http://localhost:8000/scan/bulk \
  -H "Content-Type: application/json" \
  -d "{\"domain_list\": $DOMAINS}")

# Job ID'yi al
JOB_ID=$(echo $RESPONSE | jq -r '.job_id')
echo "Job ID: $JOB_ID"

# İlerleme takibi (polling)
while true; do
  STATUS=$(curl -s "http://localhost:8000/scan/bulk/$JOB_ID" | jq -r '.status')
  PROGRESS=$(curl -s "http://localhost:8000/scan/bulk/$JOB_ID" | jq -r '.progress')
  echo "Status: $STATUS, Progress: $PROGRESS%"
  
  if [ "$STATUS" = "completed" ]; then
    echo "İşlem tamamlandı!"
    break
  fi
  
  sleep 5  # 5 saniye bekle
done

# Sonuçları al
curl "http://localhost:8000/scan/bulk/$JOB_ID/results" | jq '.'
```

**Manuel Tek Tek Scan (Sadece Gerekirse - 10'dan az domain):**
```bash
# Eğer auto_scan=false kullandıysanız ve az sayıda domain varsa
while IFS=, read -r domain rest; do
  if [ "$domain" != "domain" ]; then
    echo "Analiz ediliyor: $domain"
    curl -X POST http://localhost:8000/scan/domain \
      -H "Content-Type: application/json" \
      -d "{\"domain\": \"$domain\"}"
    sleep 2  # Rate limiting için bekle
  fi
done < yeni-leadler.csv
```

**Provider Değişikliği Tespiti:**
- Scan sırasında provider değişiklikleri otomatik olarak tespit edilir ve kaydedilir
- Örnek: Google → M365 geçişi otomatik olarak `provider_change_history` tablosuna kaydedilir

#### 3. Öncelikli Lead'leri Görüntüle (G19: UI Upgrade) ✨ YENİ
```bash
# Migration segment'i (yüksek öncelik) - Basit filtre
curl "http://localhost:8000/leads?segment=Migration&min_score=70"

# Migration segment'i + Sorting (skora göre sıralama) - G19
curl "http://localhost:8000/leads?segment=Migration&min_score=70&sort_by=readiness_score&sort_order=desc"

# Migration segment'i + Search + Sorting + Pagination - G19
curl "http://localhost:8000/leads?segment=Migration&min_score=70&search=example&sort_by=readiness_score&sort_order=desc&page=1&page_size=25"

# Existing segment'i (orta öncelik)
curl "http://localhost:8000/leads?segment=Existing&min_score=50"
```

**G19 UI Upgrade Özellikleri:**
- **Sorting**: `sort_by` (domain, readiness_score, segment, provider) + `sort_order` (asc, desc)
- **Pagination**: `page` (sayfa numarası) + `page_size` (10, 25, 50, 100)
- **Search**: `search` (domain veya company_name içinde arama)
- **Score Breakdown**: Skorlara tıklayarak detaylı analiz modal'ı açılır

#### 4. Dashboard Özeti (G19: Enhanced) ✨ YENİ
```bash
# Legacy dashboard (backward compatible)
curl "http://localhost:8000/dashboard"

# New KPI endpoint (G19)
curl "http://localhost:8000/dashboard/kpis"
```

**G19 KPI Endpoint Yanıtı:**
```json
{
  "total_leads": 100,
  "migration_leads": 15,
  "high_priority": 8
}
```

**G19 Enhancement:**
- **High Priority KPI**: Priority Score 1-2 olan lead sayısı
- **Optimized Response**: Sadece gerekli KPI metrikleri (daha hızlı)

**Ne Gösterir?**
- Toplam lead sayısı
- Segment dağılımı (Migration, Existing, Cold, Skip)
- Ortalama skor
- Yüksek öncelikli lead sayısı (Migration + skor >= 70)

#### 5. Lead'leri Export Et (CSV/Excel) 📥 YENİ
```bash
# Migration lead'lerini CSV olarak export et
curl "http://localhost:8000/leads/export?format=csv&segment=Migration&min_score=70" -o migration-leads.csv

# Excel formatında export
curl "http://localhost:8000/leads/export?format=xlsx&segment=Migration&min_score=70" -o migration-leads.xlsx
```

**Ne İşe Yarar?**
- Excel'de detaylı analiz yapma
- CRM'e import etme
- Raporlama ve paylaşım
- Filtrelenmiş lead listelerini kaydetme

### Sonuç
- **Migration**: Hemen aksiyon alınacak lead'ler
- **Existing**: Takip edilecek lead'ler
- **Cold/Skip**: Düşük öncelikli, sonra bakılacak
- **Export**: Lead'leri CSV/Excel olarak export edip analiz edebilirsiniz

---

## 📋 Senaryo 2: Tek Domain Hızlı Kontrol

### Durum
Bir müşteri adayından domain aldınız. Hızlıca kontrol etmek istiyorsunuz.

**Hızlı Kontrol Akışı:**
1. Domain ekle → Analiz et → Priority Score'a bak → Aksiyon al

### Mini UI ile Hızlı Kontrol (Önerilen) 🖥️

1. **Mini UI'yi Aç**
   ```
   http://localhost:8000/mini-ui/
   ```

2. **Domain Tara**
   - "Tek Domain Tara" formunda domain gir
   - Şirket adı (opsiyonel) gir
   - "Tara" butonuna tıkla
   - Sonuç panelinde skor, segment, provider görüntülenir

3. **Sonucu Yorumla**
   - Skor 70+ → Yüksek hazırlık
   - Segment Migration → Hemen aksiyon
   - Priority Score 1-2 → En yüksek öncelik

**Avantajlar:**
- ✅ Tek tıkla tarama (otomatik ingest + scan)
- ✅ Anında sonuç görüntüleme
- ✅ Lead listesi otomatik güncellenir

### API ile Kontrol (Alternatif) 💻

### Adımlar

#### 1. Domain Ekle
```bash
curl -X POST http://localhost:8000/ingest/domain \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "yeni-firma.com",
    "company_name": "Yeni Firma A.Ş.",
    "email": "info@yeni-firma.com"
  }'
```

#### 2. Analiz Et
```bash
curl -X POST http://localhost:8000/scan/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "yeni-firma.com"}'
```

#### 3. Sonucu Yorumla
```json
{
  "domain": "yeni-firma.com",
  "score": 85,
  "segment": "Migration",
  "provider": "M365",
  "priority_score": 1
}
```

**Yorum:**
- ✅ Skor 85 → Yüksek hazırlık
- ✅ Segment Migration → Hemen aksiyon
- ✅ Provider M365 → Cloud kullanıyor
- ✅ Priority Score 1 → En yüksek öncelik

**Aksiyon:** Hemen iletişime geç, migration teklifi hazırla

---

## 📋 Senaryo 3: Mevcut Müşteri Takibi

### Durum
Mevcut müşterilerin durumunu kontrol etmek istiyorsunuz. Upsell/cross-sell fırsatı var mı?

### Dashboard ile Genel Bakış
```bash
# Önce genel durumu gör
curl "http://localhost:8000/dashboard"
```

**Yorum:**
- `existing` sayısı → Mevcut müşteri potansiyeli
- `avg_score` → Genel hazırlık seviyesi
- `high_priority` → Yüksek öncelikli fırsatlar

### Adımlar

#### 1. Existing Segment'indeki Lead'leri Görüntüle
```bash
curl "http://localhost:8000/leads?segment=Existing&min_score=50"
```

#### 2. Yüksek Skorlu Lead'leri Filtrele
```bash
curl "http://localhost:8000/leads?segment=Existing&min_score=70"
```

#### 3. Belirli Provider'a Göre Filtrele
```bash
# M365 kullanan mevcut müşteriler
curl "http://localhost:8000/leads?segment=Existing&provider=M365&min_score=50"
```

### Sonuç
- **Skor 70+**: Upsell fırsatı olabilir
- **Skor 50-69**: Düzenli takip
- **Provider değişikliği**: Migration fırsatı

---

## 📋 Senaryo 4: Migration Fırsatı Tespiti

### Durum
Hangi müşteri adayları migration için hazır?

### Dashboard ile Hızlı Tespit
```bash
# Dashboard'da migration sayısını gör
curl "http://localhost:8000/dashboard"
```

**Yorum:**
- `migration` sayısı → Migration fırsatı olan lead sayısı
- `high_priority` → Priority 1-2 olan en öncelikli lead'ler

### Adımlar

#### 1. Migration Segment'indeki Tüm Lead'leri Görüntüle
```bash
curl "http://localhost:8000/leads?segment=Migration"
```

#### 2. Yüksek Skorlu Lead'leri Sırala
```bash
curl "http://localhost:8000/leads?segment=Migration&min_score=80"
```

#### 3. Belirli Provider'a Göre Filtrele
```bash
# M365'ten başka provider'a geçiş fırsatı
curl "http://localhost:8000/leads?segment=Migration&provider=Google&min_score=70"
```

### Sonuç
- **Migration + Skor 80+**: En yüksek öncelik
- **Migration + Skor 70-79**: Yüksek öncelik
- **Provider çeşitliliği**: Farklı provider'lara göre strateji

**Export ile Analiz:**
```bash
# Migration lead'lerini Excel'e export et
curl "http://localhost:8000/leads/export?format=xlsx&segment=Migration&min_score=70" -o migration-opportunities.xlsx

# Excel'de detaylı analiz yapabilirsiniz
```

---

## 📋 Senaryo 5: Düzenli Takip (Aylık)

### Durum
Aylık olarak tüm lead'leri kontrol etmek, skor değişikliklerini takip etmek.

### Adımlar

#### 1. Tüm Segment'leri Kontrol Et
```bash
# Migration
curl "http://localhost:8000/leads?segment=Migration"

# Existing
curl "http://localhost:8000/leads?segment=Existing"

# Cold
curl "http://localhost:8000/leads?segment=Cold"
```

#### 2. Skor Değişikliklerini Takip Et
```bash
# Yüksek skorlu lead'ler (öncelikli)
curl "http://localhost:8000/leads?min_score=70"

# Orta skorlu lead'ler (takip)
curl "http://localhost:8000/leads?min_score=50&max_score=69"
```

#### 3. Provider Değişikliklerini Kontrol Et
```bash
# M365 kullananlar
curl "http://localhost:8000/leads?provider=M365"

# Google kullananlar
curl "http://localhost:8000/leads?provider=Google"
```

#### 4. ReScan ile Değişiklikleri Tespit Et (G18) ✨ YENİ
```bash
# Tek domain'i yeniden tara
curl -X POST http://localhost:8000/scan/ornek-firma.com/rescan

# Toplu rescan (tüm domain'ler için)
curl -X POST "http://localhost:8000/scan/bulk/rescan?domain_list=domain1.com,domain2.com,domain3.com"

# Alert'leri kontrol et
curl "http://localhost:8000/alerts?alert_type=mx_changed"
```

**ReScan Ne Yapıyor?**
- Domain'i yeniden tarar (DNS + WHOIS)
- Değişiklikleri tespit eder (MX, DMARC, skor, expiry)
- Alert oluşturur (değişiklik varsa)
- History kayıtları oluşturur

**Alert Türleri:**
- `mx_changed`: MX root değişti
- `dmarc_added`: DMARC policy eklendi (none → quarantine/reject)
- `expire_soon`: Domain 30 gün içinde expire olacak
- `score_changed`: Priority score veya segment değişti

### Sonuç
- **Skor artışı**: Segment değişikliği olabilir (Cold → Existing)
- **Provider değişikliği**: Migration fırsatı
- **Yeni lead'ler**: Yeni eklenen domain'ler
- **Değişiklikler**: ReScan ile otomatik tespit edilir ve alert oluşturulur

**Export ile Takip:**
```bash
# Tüm segment'leri CSV olarak export et (aylık rapor)
curl "http://localhost:8000/leads/export?format=csv" -o monthly-report-$(date +%Y-%m).csv

# Excel'de skor değişikliklerini takip edebilirsiniz
```

**Not:** G18 ile birlikte daily rescan scheduler eklendi. Tüm domain'ler otomatik olarak günlük olarak yeniden taranır ve değişiklikler tespit edilir.

---

## 📋 Senaryo 6: Lead Enrichment (Contact Emails) ✨ YENİ

### Durum
Bir lead için contact email'lerini topladınız ve sisteme eklemek istiyorsunuz.

### Adımlar

#### 1. Lead'i Contact Email'leri ile Zenginleştir

```bash
curl -X POST http://localhost:8000/leads/ornek-firma.com/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "contact_emails": [
      "john.doe@ornek-firma.com",
      "jane.smith@ornek-firma.com",
      "bob@ornek-firma.com"
    ]
  }'
```

**Örnek Sonuç:**
```json
{
  "domain": "ornek-firma.com",
  "contact_emails": [
    "john.doe@ornek-firma.com",
    "jane.smith@ornek-firma.com",
    "bob@ornek-firma.com"
  ],
  "contact_quality_score": 75,
  "linkedin_pattern": "firstname.lastname",
  "message": "Domain ornek-firma.com enriched successfully"
}
```

**Yorum:**
- ✅ 3 contact email eklendi
- ✅ Quality score: 75 (yüksek - domain eşleşmesi var)
- ✅ LinkedIn pattern: firstname.lastname (LinkedIn outreach için kullanılabilir)

#### 2. Enrichment Bilgilerini Görüntüle

```bash
# Lead detaylarında enrichment bilgileri görüntülenir
curl "http://localhost:8000/leads/ornek-firma.com"
```

**Ne Döner?**
- Contact emails listesi
- Contact quality score (0-100)
- LinkedIn pattern (firstname.lastname, f.lastname, firstname, veya null)

#### 3. Export ile Enrichment Bilgilerini Kaydet

```bash
# Enrichment bilgileri export'ta da yer alır
curl "http://localhost:8000/leads/export?format=csv&segment=Migration" -o migration-leads.csv
```

**Export İçeriği:**
- Contact emails (virgülle ayrılmış)
- Contact quality score
- LinkedIn pattern

### Sonuç

**Enrichment Avantajları:**
- ✅ Satış ekibi için iletişim bilgileri toplama
- ✅ Email kalitesi skorlaması (hangi lead'lerde daha fazla contact var)
- ✅ LinkedIn outreach için pattern tespiti
- ✅ Lead'leri daha iyi değerlendirme

**Kullanım Senaryoları:**
- **Toplu Enrichment**: Birçok lead için contact email'leri topladıysanız, tek tek enrichment yapabilirsiniz
- **Quality Score**: Yüksek quality score'lu lead'lere öncelik verin (daha fazla contact = daha iyi fırsat)
- **LinkedIn Outreach**: LinkedIn pattern tespit edildiyse, LinkedIn'de benzer pattern'lerle arama yapabilirsiniz

---

## 📋 Senaryo 7: Email Üretme ve Doğrulama

### Durum
Bir domain için iletişim email'lerini bulmak ve doğrulamak istiyorsunuz.

### Adımlar

#### 1. Generic Email'leri Üret ve Doğrula

```bash
# Light validation (hızlı, önerilen)
curl -X POST http://localhost:8000/email/generate-and-validate \
  -H "Content-Type: application/json" \
  -d '{"domain": "ornek-firma.com", "use_smtp": false}'
```

**Örnek Sonuç:**
```json
{
  "domain": "ornek-firma.com",
  "emails": [
    {
      "email": "info@ornek-firma.com",
      "status": "valid",
      "confidence": "medium",
      "checks": {
        "syntax": true,
        "mx": true,
        "smtp": "skipped"
      },
      "reason": "Valid syntax and MX records (SMTP not checked)"
    },
    {
      "email": "sales@ornek-firma.com",
      "status": "valid",
      "confidence": "medium",
      "checks": {
        "syntax": true,
        "mx": true,
        "smtp": "skipped"
      },
      "reason": "Valid syntax and MX records (SMTP not checked)"
    }
  ]
}
```

**Yorum:**
- ✅ `status: "valid"` → Email geçerli
- ✅ `confidence: "medium"` → Syntax + MX OK (SMTP kontrol edilmedi)
- ✅ `checks.mx: true` → Domain'de MX kaydı var

#### 2. Sadece Email Listesi (Doğrulama Olmadan)

```bash
# Sadece email listesi istiyorsanız
curl -X POST http://localhost:8000/email/generate \
  -H "Content-Type: application/json" \
  -d '{"domain": "ornek-firma.com"}'
```

**Ne Döner?**
- 9 generic email adresi (Türkçe + International)
- Doğrulama yok, sadece liste

#### 3. Full Validation (SMTP ile)

```bash
# Full validation (yavaş, 10-30 saniye sürebilir)
curl -X POST http://localhost:8000/email/generate-and-validate \
  -H "Content-Type: application/json" \
  -d '{"domain": "ornek-firma.com", "use_smtp": true}'
```

**Ne Döner?**
- Syntax + MX + SMTP kontrolü
- Daha yüksek confidence (high)
- Daha yavaş (her email için 3 saniye timeout)

### Sonuç

**Light Validation (Önerilen):**
- Hızlı (<1 saniye)
- Syntax + MX kontrolü
- Medium confidence
- Outreach için yeterli

**Full Validation:**
- Yavaş (10-30 saniye)
- Syntax + MX + SMTP kontrolü
- High confidence
- Kritik durumlar için

**Kullanım Senaryoları:**
- **Outreach**: Light validation yeterli
- **Kritik İletişim**: Full validation önerilir
- **Toplu İşlem**: Light validation kullanın (hız önemli)

---

## 📋 Senaryo 8: ReScan ve Change Detection (G18) ✨ YENİ

### Durum
Domain'lerdeki değişiklikleri (MX, DMARC, skor) takip etmek ve alert almak istiyorsunuz.

### Adımlar

#### 1. Tek Domain'i ReScan Et
```bash
# Domain'i yeniden tara ve değişiklikleri tespit et
curl -X POST http://localhost:8000/scan/ornek-firma.com/rescan
```

**Yanıt:**
```json
{
  "domain": "ornek-firma.com",
  "success": true,
  "changes_detected": true,
  "signal_changes": 1,
  "score_changes": 0,
  "alerts_created": 1,
  "changes": [
    {
      "type": "mx_changed",
      "old_value": "outlook.com",
      "new_value": "google.com"
    }
  ]
}
```

**Yorum:**
- ✅ MX root değişti (outlook.com → google.com)
- ✅ Alert oluşturuldu
- ✅ History kaydı oluşturuldu

#### 2. Toplu ReScan
```bash
# Birden fazla domain'i yeniden tara
curl -X POST "http://localhost:8000/scan/bulk/rescan?domain_list=domain1.com,domain2.com,domain3.com"
```

**Yanıt:**
```json
{
  "job_id": "uuid-string",
  "status": "pending",
  "total": 3,
  "message": "Bulk rescan job created"
}
```

**İlerleme Takibi:**
```bash
# Job durumunu kontrol et
curl "http://localhost:8000/scan/bulk/{job_id}"
```

#### 3. Alert'leri Görüntüle
```bash
# Tüm alert'leri listele
curl "http://localhost:8000/alerts"

# MX değişikliği alert'lerini filtrele
curl "http://localhost:8000/alerts?alert_type=mx_changed"

# Belirli domain için alert'leri görüntüle
curl "http://localhost:8000/alerts?domain=ornek-firma.com"
```

#### 4. Alert Konfigürasyonu
```bash
# Webhook notification için alert config
curl -X POST http://localhost:8000/alerts/config \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "mx_changed",
    "notification_method": "webhook",
    "enabled": true,
    "frequency": "immediate",
    "webhook_url": "https://example.com/webhook"
  }'

# Email notification için alert config
curl -X POST http://localhost:8000/alerts/config \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "expire_soon",
    "notification_method": "email",
    "enabled": true,
    "frequency": "immediate",
    "email_address": "sales@example.com"
  }'
```

### Sonuç

**ReScan Avantajları:**
- ✅ Domain değişikliklerini otomatik tespit
- ✅ MX, DMARC, skor değişikliklerini takip
- ✅ Alert sistemi ile bildirim alma
- ✅ History kayıtları ile geçmiş takibi

**Alert Türleri:**
- **MX Changed**: Provider değişikliği tespit edildi
- **DMARC Added**: DMARC policy eklendi (güvenlik iyileştirmesi)
- **Expire Soon**: Domain yakında expire olacak
- **Score Changed**: Priority score veya segment değişti

**Kullanım Senaryoları:**
- **Migration Fırsatı**: MX değişikliği migration fırsatı gösterebilir
- **Güvenlik İyileştirmesi**: DMARC eklenmesi güvenlik iyileştirmesi gösterebilir
- **Domain Expiry**: Domain expire uyarısı ile yenileme fırsatı
- **Skor Takibi**: Skor değişiklikleri ile lead durumu takibi

**Not:** Daily rescan scheduler ile tüm domain'ler otomatik olarak günlük olarak yeniden taranır.

---

## 📋 Senaryo 9: Notes, Tags ve Favorites (G17: CRM-lite) ✨ YENİ

### Durum
Lead'leri organize etmek, notlar eklemek ve favorilere eklemek istiyorsunuz.

### Adımlar

#### 1. Not Ekleyin
```bash
# Domain için not ekle
curl -X POST http://localhost:8000/leads/ornek-firma.com/notes \
  -H "Content-Type: application/json" \
  -d '{"note": "Müşteri ile görüşüldü, migration planı hazırlanıyor"}'

# Notları listele
curl "http://localhost:8000/leads/ornek-firma.com/notes"

# Notu güncelle
curl -X PUT http://localhost:8000/leads/ornek-firma.com/notes/{note_id} \
  -H "Content-Type: application/json" \
  -d '{"note": "Güncellenmiş not"}'

# Notu sil
curl -X DELETE http://localhost:8000/leads/ornek-firma.com/notes/{note_id}
```

#### 2. Tag Ekleyin
```bash
# Tag ekle
curl -X POST http://localhost:8000/leads/ornek-firma.com/tags \
  -H "Content-Type: application/json" \
  -d '{"tag": "important"}'

# Tag'leri listele
curl "http://localhost:8000/leads/ornek-firma.com/tags"

# Tag'i sil
curl -X DELETE http://localhost:8000/leads/ornek-firma.com/tags/{tag_id}
```

**Auto-Tagging:**
- Sistem otomatik olarak tag'ler ekler:
  - `security-risk`: SPF ve DKIM yok
  - `migration-ready`: Migration segment + skor >= 70
  - `expire-soon`: Domain 30 gün içinde expire olacak
  - `weak-spf`: SPF var ama DMARC none
  - `google-workspace`: Provider Google
  - `local-mx`: Provider Local

#### 3. Favorilere Ekleyin
```bash
# Favorilere ekle
curl -X POST http://localhost:8000/leads/ornek-firma.com/favorite

# Favorileri listele
curl "http://localhost:8000/leads?favorite=true"

# Favorilerden çıkar
curl -X DELETE http://localhost:8000/leads/ornek-firma.com/favorite
```

#### 4. PDF Özet Oluşturun
```bash
# Domain için PDF özet oluştur
curl "http://localhost:8000/leads/ornek-firma.com/summary.pdf" -o ornek-firma-summary.pdf
```

**PDF İçeriği:**
- Provider bilgisi
- SPF/DKIM/DMARC durumu
- Expiry date
- Signals (MX, nameservers)
- Scores (Readiness, Priority)
- Risks (no SPF, no DKIM, DMARC none)

### Sonuç

**CRM-lite Avantajları:**
- ✅ Notlar ile lead takibi
- ✅ Tag'ler ile lead organizasyonu
- ✅ Favoriler ile öncelikli lead'ler
- ✅ PDF özet ile satış sunumu

**Kullanım Senaryoları:**
- **Notlar**: Müşteri görüşmeleri, migration planları, takip notları
- **Tag'ler**: Öncelik belirleme, kategori organizasyonu
- **Favoriler**: Öncelikli lead'leri hızlıca erişim
- **PDF**: Satış sunumu, müşteri raporu

---

## 💡 En İyi Pratikler

### 0. Mini UI Kullanın (Önerilen) 🖥️

**Mini UI avantajları:**
- ✅ Kolay kullanım (tarayıcıdan)
- ✅ Görsel arayüz (tablo, filtreler, KPI)
- ✅ Otomatik refresh (upload/scan sonrası)
- ✅ Hızlı export (tek tıkla CSV indirme)
- ✅ Hata mesajları görsel
- ✅ **G19: UI Upgrade** - Sorting, pagination, search ile gelişmiş tablo yönetimi
- ✅ **G19: Score Breakdown** - Skorlara tıklayarak detaylı analiz
- ✅ **G19: Microsoft SSO** - Güvenli giriş ve kullanıcı bazlı favoriler

**Ne Zaman API Kullanılır?**
- Script'ler ve otomasyon için
- Toplu işlemler için
- Entegrasyonlar için

**Erişim:**
```
http://localhost:8000/mini-ui/
```

### 1. Öncelik Sıralaması (Priority Score)
1. **Priority 1**: Migration + Skor 80+ → En yüksek öncelik, hemen aksiyon
2. **Priority 2**: Migration + Skor 70-79 → Yüksek öncelik, hemen aksiyon
3. **Priority 3**: Existing + Skor 70+ → Orta-yüksek öncelik, 1 hafta içinde
4. **Priority 4**: Existing + Skor 50-69 → Orta öncelik, takip et
5. **Priority 5**: Cold + Skor 40+ → Düşük öncelik, 1-2 ay sonra kontrol
6. **Priority 6**: Diğerleri → En düşük öncelik, 3-6 ay sonra kontrol

**Eski Segment Bazlı Sıralama:**
1. **Migration (70+)**: Hemen aksiyon
2. **Existing (50+)**: Takip et
3. **Cold (20-49)**: 1-2 ay sonra kontrol
4. **Skip (0-19)**: 3-6 ay sonra kontrol

### 2. Toplu Analiz
- CSV'den ekleme yaparken batch processing kullanın
- Her analiz arasında 2 saniye bekleyin (rate limiting)
- Hata durumlarını log'layın

### 2.1. UI Upgrade ile Verimli Çalışma (G19) ✨ YENİ
- **Sorting**: Skora göre sıralama yaparak yüksek öncelikli lead'leri üstte görün
- **Pagination**: Büyük listelerde sayfalama kullanarak performansı artırın
- **Search**: Domain veya şirket adı ile hızlı arama yapın (debounce ile optimize)
- **Score Breakdown**: Skorlara tıklayarak detaylı analiz yapın, eksik sinyalleri görün
- **Kombine Kullanım**: Search + Filter + Sort + Pagination ile güçlü filtreleme

### 3. Düzenli Kontrol
- **Migration/Existing**: Haftalık kontrol
- **Cold**: Aylık kontrol
- **Skip**: 3-6 ayda bir kontrol

### 4. Skor Takibi
- Skor değişikliklerini takip edin
- Segment değişikliklerini not edin
- Provider değişikliklerini değerlendirin

### 5. Veri Kalitesi
- Domain'leri normalize edin (www, büyük/küçük harf, URL'lerden domain çıkarılır)
- Email ve website'den domain çıkarın
- **Domain validation**: Geçersiz domain'ler (nan, web sitesi, vb.) otomatik olarak filtrelenir
- **Duplicate prevention**: Aynı domain için eski kayıtlar otomatik olarak temizlenir (tekrar scan edildiğinde)

### 6. ReScan ve Change Detection (G18) ✨ YENİ
- **Düzenli ReScan**: Aylık olarak domain'leri yeniden tarayın
- **Alert Konfigürasyonu**: Önemli değişiklikler için alert ayarlayın
- **Change Tracking**: MX, DMARC, skor değişikliklerini takip edin
- **Daily Rescan**: Sistem otomatik olarak günlük rescan yapar (scheduler ile)

### 6. Email Üretme ve Doğrulama
- **Light validation** kullanın (use_smtp=false) - Hızlı ve yeterli
- **Full validation** sadece kritik durumlarda (use_smtp=true) - Yavaş ama kesin
- Generic email'leri outreach için kullanın
- Valid status'lu email'lere öncelik verin

### 7. Notes, Tags ve Favorites (G17) ✨ YENİ
- **Notlar**: Müşteri görüşmeleri, migration planları için notlar ekleyin
- **Tag'ler**: Öncelik belirleme, kategori organizasyonu için tag'ler kullanın
- **Favoriler**: Öncelikli lead'leri favorilere ekleyin, hızlıca erişin
- **PDF Özet**: Satış sunumu için PDF özet oluşturun
- **Auto-Tagging**: Sistem otomatik tag'ler ekler, manuel tag'ler de ekleyebilirsiniz

---

## 🔧 Yardımcı Script'ler

### Toplu Analiz Script'i
```bash
#!/bin/bash
# Toplu domain analizi

API_URL="http://localhost:8000"
CSV_FILE="domain-listesi.csv"

while IFS=, read -r domain rest; do
  if [ "$domain" != "domain" ]; then
    echo "Analiz: $domain"
    curl -X POST "${API_URL}/scan/domain" \
      -H "Content-Type: application/json" \
      -d "{\"domain\": \"$domain\"}"
    sleep 2
  fi
done < "$CSV_FILE"
```

### Migration Lead'leri Export (CSV/Excel) 📥 YENİ
```bash
#!/bin/bash
# Migration lead'lerini CSV olarak export et

API_URL="http://localhost:8000"
OUTPUT_FILE="migration-leads-$(date +%Y-%m-%d_%H-%M-%S).csv"

curl -s "${API_URL}/leads/export?format=csv&segment=Migration&min_score=70" -o "$OUTPUT_FILE"
echo "Migration lead'leri $OUTPUT_FILE dosyasına kaydedildi"
```

**Excel Formatında:**
```bash
#!/bin/bash
# Migration lead'lerini Excel olarak export et

API_URL="http://localhost:8000"
OUTPUT_FILE="migration-leads-$(date +%Y-%m-%d_%H-%M-%S).xlsx"

curl -s "${API_URL}/leads/export?format=xlsx&segment=Migration&min_score=70" -o "$OUTPUT_FILE"
echo "Migration lead'leri $OUTPUT_FILE dosyasına kaydedildi"
```

---

## 📊 Örnek Sonuçlar

### Senaryo 1 Sonucu
```
100 domain analiz edildi:
- Migration (70+): 15 domain → Hemen aksiyon
- Existing (50-69): 25 domain → Takip et
- Cold (20-49): 30 domain → 1-2 ay sonra kontrol
- Skip (0-19): 30 domain → 3-6 ay sonra kontrol
```

### Senaryo 2 Sonucu
```
Domain: yeni-firma.com
Skor: 85
Segment: Migration
Priority Score: 1 (En yüksek öncelik)
Aksiyon: Hemen iletişime geç, migration teklifi hazırla
```

### Senaryo 3 Sonucu
```
50 mevcut müşteri kontrol edildi:
- Skor 70+: 10 müşteri → Upsell fırsatı
- Skor 50-69: 20 müşteri → Düzenli takip
- Skor 20-49: 20 müşteri → 1-2 ay sonra kontrol
```

### Senaryo 6 Sonucu
```
Domain: ornek-firma.com
3 contact email eklendi:
- john.doe@ornek-firma.com
- jane.smith@ornek-firma.com
- bob@ornek-firma.com
Quality Score: 75 (yüksek - domain eşleşmesi var)
LinkedIn Pattern: firstname.lastname
Aksiyon: LinkedIn'de benzer pattern'lerle arama yap, outreach başlat
```

### Senaryo 7 Sonucu
```
Domain: ornek-firma.com
9 generic email üretildi:
- Valid: 7 email (info, sales, admin, iletisim, satis, support, hr)
- Invalid: 2 email (muhasebe, ik - MX kaydı yok)
- Confidence: Medium (syntax + MX kontrolü)
- Aksiyon: Valid email'leri outreach için kullan
```

---

## ❓ Sık Sorulan Sorular

### Q: Toplu analiz ne kadar sürer?
**A:** Domain başına 10-15 saniye. 100 domain için yaklaşık 20-25 dakika (rate limiting ile).

### Q: Hangi segment'e öncelik vermeliyim?
**A:** Migration (70+) → Existing (50+) → Cold (20-49) → Skip (0-19)

### Q: Skor değişir mi?
**A:** Evet, domain'in DNS/WHOIS bilgileri değiştiğinde skor da değişir. Düzenli kontrol önerilir.

### Q: CSV'den ekledim, otomatik analiz olmuyor mu?
**A:** `auto_scan=true` parametresi ile CSV upload sonrası otomatik analiz yapılır. Varsayılan olarak `auto_scan=true` kullanılır (Mini UI'de otomatik). Eğer `auto_scan=false` kullandıysanız, manuel olarak `/scan/domain` endpoint'ini kullanmalısınız.

---

**Son Güncelleme:** 2025-01-28

