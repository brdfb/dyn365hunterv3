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

## 🖥️ Mini UI (Web Arayüzü) - YENİ

**Tarayıcıdan kullanım için basit web arayüzü:**

### Mini UI'ye Erişim

Tarayıcınızda açın:
```
http://localhost:8000/mini-ui/
```

### Özellikler

1. **CSV/Excel Upload**
   - Dosya seçme (CSV, Excel)
   - Otomatik kolon tespiti (OSB dosyaları için)
   - **Progress Tracking**: Yükleme sırasında ilerleme çubuğu ve istatistikler gösterilir
   - Yükleme sonrası otomatik lead listesi güncelleme

2. **Tek Domain Scan**
   - Domain ve şirket adı girişi
   - Otomatik ingest (domain yoksa)
   - Tarama sonucu gösterimi (skor, segment, provider)
   - Otomatik lead listesi güncelleme

3. **Leads Table + Filtreler** (G19: UI Upgrade) ✨ YENİ
   - Segment filtresi (Migration, Existing, Cold, Skip)
   - Min skor filtresi
   - Provider filtresi
   - **Sorting** (G19): Tablo başlıklarına tıklayarak sıralama (domain, skor, segment, vb.)
     - Tablo başlıklarında sıralama ikonları görünür (⇅)
     - Aktif sıralama yönü gösterilir (▲ asc, ▼ desc)
   - **Pagination** (G19): Sayfa numaraları ile sayfalama (50 kayıt/sayfa varsayılan)
     - Sayfa numaraları görünür (1, 2, 3, ...)
     - Aktif sayfa vurgulanır
     - Önceki/Sonraki butonları
   - **Search** (G19): Arama kutusu ile anlık arama (debounce ile optimize edilmiş)
   - Tablo görüntüleme (Domain, Şirket, Provider, Segment, Skor)
   - **Score Breakdown** (G19): Skorlara tıklayarak detaylı skor analizi modal'ı açma
     - Skorlar tıklanabilir (altı çizili görünür)
     - Modal'da detaylı skor analizi gösterilir (temel skor, provider puanları, sinyal puanları, risk faktörleri)

4. **Export CSV**
   - Filtrelenmiş lead'leri CSV olarak export
   - Otomatik dosya indirme

5. **Dashboard Stats (KPI)** (G19: Enhanced) ✨ YENİ
   - Toplam lead sayısı
   - Migration lead sayısı
   - **Yüksek Öncelik** (G19): Priority Score 1-2 olan lead sayısı
   - En yüksek skor

6. **Microsoft SSO Authentication** (G19) ✨ YENİ
   - Microsoft hesabı ile giriş yapma
   - Oturum yönetimi (token-based)
   - Güvenli çıkış (logout)
   - Kullanıcı bazlı favoriler (session-based → user-based migration)

**Detaylı bilgi için:** [mini-ui/README-mini-ui.md](../../mini-ui/README-mini-ui.md)

**Not:** Mini UI demo ve iç kullanım için tasarlandı. API endpoint'leri de kullanılabilir (curl komutları aşağıda).

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
- `domain` zorunlu (otomatik normalize edilir: büyük/küçük harf, www kaldırılır, URL'lerden domain çıkarılır)
- `company_name`, `email`, `website` opsiyonel
- Email veya website'den domain otomatik çıkarılır
- **Domain validation**: Geçersiz domain'ler (nan, web sitesi, vb.) otomatik olarak filtrelenir

**Başarılı Yanıt:**
```json
{
  "domain": "ornek-firma.com",
  "company_id": 1,
  "message": "Domain ornek-firma.com ingested successfully"
}
```

### CSV/Excel ile Toplu Ekleme

```bash
# CSV dosyası (otomatik scan ile)
curl -X POST "http://localhost:8000/ingest/csv?auto_scan=true" \
  -F "file=@domain-listesi.csv"

# Excel dosyası (.xlsx, .xls) - otomatik scan ile
curl -X POST "http://localhost:8000/ingest/csv?auto_scan=true" \
  -F "file=@domain-listesi.xlsx"
```

**Otomatik Scan (`auto_scan=true`):**
- Domain'ler yüklendikten sonra otomatik olarak scan edilir
- Her domain için DNS/WHOIS analizi yapılır ve skor hesaplanır
- Sonuçlar otomatik olarak lead listesine eklenir
- **Progress tracking**: İşlem sırasında ilerleme takibi yapılabilir (job_id ile)

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

**CSV/Excel Formatı:**
```csv
domain,company_name,email,website
ornek1.com,Örnek 1 A.Ş.,info@ornek1.com,https://www.ornek1.com
ornek2.com,Örnek 2 Ltd.,,https://www.ornek2.com
ornek3.com,,info@ornek3.com,
```

**Not:** CSV/Excel'de sadece `domain` kolonu zorunlu (auto_detect_columns=false ise), diğerleri opsiyonel.

**Excel Kolon Otomatik Tespiti (OSB Dosyaları için):**

OSB Excel dosyalarında kolon isimleri farklı olabilir (örn: "Firma Adı", "Ünvan", "Web", vb.). Bu durumda otomatik tespit kullanabilirsiniz:

```bash
# Kolon otomatik tespiti ile (OSB Excel dosyaları için)
curl -X POST "http://localhost:8000/ingest/csv?auto_detect_columns=true" \
  -F "file=@osb-listesi.xlsx"
```

**Ne Yapıyor?**
- Firma/şirket kolonunu otomatik tespit eder (Firma Adı, Ünvan, Company, vb.)
- Domain kolonunu otomatik tespit eder (Domain, Web, Website, vb.)
- Heuristic-based detection kullanır (%80+ doğruluk)

**Ne Zaman Kullanılır?**
- OSB Excel dosyaları için (kolon isimleri standart değilse)
- Farklı formatlardaki Excel dosyaları için
- Manuel kolon mapping yapmak istemiyorsanız

**Not:** `auto_detect_columns=false` (default) → Mevcut CSV formatı çalışmaya devam eder (backward compatible).

---

## 🔍 Adım 2: Domain Analizi (Scan)

### Tek Domain Analizi

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
- **Provider değişikliği tespit eder** - Eğer domain daha önce farklı bir provider kullanıyorsa, bu değişiklik otomatik olarak kaydedilir
- **Readiness Score** hesaplar (0-100)
- **Segment** belirler (Migration, Existing, Cold, Skip)
- **Duplicate önleme** - Aynı domain için eski kayıtları temizler, yeni sonuçları kaydeder

**Süre:** 10-15 saniye (soğuk başlangıç: 15-20 saniye)

### Toplu Domain Analizi (Bulk Scan) ⚡ YENİ

Birden fazla domain'i asenkron olarak analiz etme:

```bash
# Bulk scan job oluştur
curl -X POST http://localhost:8000/scan/bulk \
  -H "Content-Type: application/json" \
  -d '{"domain_list": ["ornek1.com", "ornek2.com", "ornek3.com"]}'
```

**Yanıt:**
```json
{
  "job_id": "uuid-string",
  "message": "Bulk scan job created successfully",
  "total": 3
}
```

**İlerleme Takibi:**
```bash
# Job durumunu kontrol et
curl "http://localhost:8000/scan/bulk/{job_id}"
```

**Yanıt:**
```json
{
  "job_id": "uuid-string",
  "status": "running",
  "progress": 50,
  "total": 3,
  "processed": 1,
  "succeeded": 1,
  "failed": 0,
  "errors": []
}
```

**Sonuçları Alma:**
```bash
# İşlem tamamlandığında sonuçları al
curl "http://localhost:8000/scan/bulk/{job_id}/results"
```

**Özellikler:**
- ✅ **Async processing** - Arka planda çalışır, HTTP timeout yok
- ✅ **Progress tracking** - Gerçek zamanlı ilerleme takibi (progress bar, istatistikler)
- ✅ **Rate limiting** - DNS (10 req/s), WHOIS (5 req/s) otomatik sınırlama
- ✅ **Error handling** - Hata olan domain'ler işlenmeye devam eder, hata mesajları Türkçe gösterilir
- ✅ **Max 1000 domain** - Tek job'da en fazla 1000 domain
- ✅ **Polling-based** - İlerleme kontrolü için polling kullanın

**Ne Zaman Kullanılır?**
- 10+ domain analiz edilecekse bulk scan kullanın
- Tek domain için `/scan/domain` endpoint'i yeterli
- Toplu analiz için bulk scan daha hızlı ve verimli

**Başarılı Yanıt:**
```json
{
  "domain": "ornek-firma.com",
  "score": 85,
  "segment": "Migration",
  "reason": "High readiness score with known cloud provider. Score: 85, Provider: M365",
  "provider": "M365",
  "tenant_size": "medium",
  "local_provider": null,
  "mx_root": "outlook.com",
  "spf": true,
  "dkim": true,
  "dmarc_policy": "reject",
  "dmarc_coverage": 100,
  "scan_status": "success"
}
```

**G20: Domain Intelligence (YENİ) ✨**
- **tenant_size**: Tenant büyüklüğü tahmini (M365/Google için: "small", "medium", "large")
- **local_provider**: Local provider adı (Local provider için: "TürkHost", "Natro", vb.)
- **dmarc_coverage**: DMARC coverage yüzdesi (0-100, pct parametresi)

**Skor Ne Anlama Geliyor?**
- **70-100**: Yüksek hazırlık → Hemen aksiyon alınabilir
- **50-69**: Orta hazırlık → Takip edilebilir
- **20-49**: Düşük hazırlık → Daha fazla sinyal gerekli
- **0-19**: Çok düşük → Şimdilik atlanabilir

**Segment Ne Anlama Geliyor?**
- **Migration**: Yüksek öncelik, hemen iletişime geç (Provider: Google/Yandex/Zoho/Hosting/Local + Score ≥ 60)
- **Existing**: Zaten müşteri olabilir, takip et (Provider: M365, her koşulda)
- **Cold**: Düşük öncelik, daha fazla sinyal gerekli (Score: 5-59 Local / 40-59 diğer)
- **Skip**: Şimdilik atla (Score: 0-39)

**Detaylı Segment-Priority Matrisi:** [SEGMENT-GUIDE.md](SEGMENT-GUIDE.md) - Kanonik Segment-Priority Matrisi bölümüne bakın.

---

## 📊 Adım 3: Lead Listesini Görüntüleme

### Tüm Lead'leri Görüntüle

```bash
curl "http://localhost:8000/leads"
```

### Filtreleme ve UI Upgrade (G19) ✨ YENİ

#### Migration Segment'i (Yüksek Öncelik)

```bash
curl "http://localhost:8000/leads?segment=Migration&min_score=60"
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
curl "http://localhost:8000/leads?segment=Migration&min_score=60"
```

**Filtre Seçenekleri:**
- `segment`: Migration, Existing, Cold, Skip
- `min_score`: Minimum skor (0-100)
- `provider`: M365, Google, Yandex, Zoho, Amazon, SendGrid, Mailgun, Hosting, Local, Unknown

### UI Upgrade Özellikleri (G19) ✨ YENİ

#### Sorting (Sıralama)

```bash
# Skora göre sıralama (yüksekten düşüğe)
curl "http://localhost:8000/leads?sort_by=readiness_score&sort_order=desc"

# Domain'e göre sıralama (alfabetik)
curl "http://localhost:8000/leads?sort_by=domain&sort_order=asc"

# Segment'e göre sıralama
curl "http://localhost:8000/leads?sort_by=segment&sort_order=asc"
```

**Sıralama Seçenekleri:**
- `sort_by`: `domain`, `readiness_score`, `segment`, `provider`, `company_name`
- `sort_order`: `asc` (artan) veya `desc` (azalan)

**Mini UI'de:** Tablo başlıklarına tıklayarak sıralama yapılabilir.

#### Pagination (Sayfalama)

```bash
# İlk sayfa (varsayılan: 10 kayıt/sayfa)
curl "http://localhost:8000/leads?page=1"

# İkinci sayfa, 25 kayıt/sayfa
curl "http://localhost:8000/leads?page=2&page_size=25"

# Üçüncü sayfa, 50 kayıt/sayfa
curl "http://localhost:8000/leads?page=3&page_size=50"
```

**Pagination Parametreleri:**
- `page`: Sayfa numarası (1'den başlar)
- `page_size`: Sayfa başına kayıt sayısı (10, 25, 50, 100)

**Mini UI'de:** Sayfa numaraları ve önceki/sonraki butonları ile sayfalama yapılabilir.

#### Search (Arama)

```bash
# Domain veya şirket adında arama
curl "http://localhost:8000/leads?search=example"

# Kombine: Arama + Filtre + Sıralama
curl "http://localhost:8000/leads?search=example&segment=Migration&sort_by=readiness_score&sort_order=desc"
```

**Search Parametresi:**
- `search`: Domain veya company_name içinde arama (case-insensitive, partial match)

**Mini UI'de:** Arama kutusuna yazıldığında otomatik arama yapılır (debounce ile optimize edilmiş, 300ms gecikme).

#### Kombine Kullanım Örneği

```bash
# Migration segment'indeki, "example" içeren, skora göre sıralanmış, 2. sayfa (25 kayıt/sayfa)
curl "http://localhost:8000/leads?segment=Migration&search=example&sort_by=readiness_score&sort_order=desc&page=2&page_size=25"
```

### Tek Lead Detayı

```bash
curl "http://localhost:8000/leads/ornek-firma.com"
```

**Ne Döner?**
- Tüm domain bilgileri
- DNS sinyalleri (SPF, DKIM, DMARC)
- **DMARC Coverage** (G20): DMARC coverage yüzdesi (0-100) ✨ YENİ
- WHOIS bilgileri
- Skor ve segment detayları
- **Priority Score** (1-7, 1 en yüksek öncelik) - Her seviye farklı görsel ile gösteriliyor (🔥⭐🟡🟠⚪⚫🔴)
- **Tenant Size** (G20): Tenant büyüklüğü tahmini (M365/Google için: small/medium/large) ✨ YENİ
- **Local Provider** (G20): Local provider adı (Local provider için: TürkHost, Natro, vb.) ✨ YENİ
- **Lead Enrichment** (G16): Contact emails, quality score, LinkedIn pattern
- Güncelleme tarihleri

**Priority Score Nedir?**
- **1** 🔥: Migration + Skor 80+ → En yüksek öncelik
- **2** ⭐: Migration + Skor 70-79 → Yüksek öncelik
- **3** 🟡: Migration + Skor 60-69, Existing + Skor 70+ → Orta-yüksek öncelik
- **4** 🟠: Migration + Skor 0-59 (artık mümkün değil, Migration için min 60), Existing + Skor 50-69 → Orta öncelik
- **5** ⚪: Existing + Skor 30-49, Cold + Skor 40+ (Local: 5-39) → Düşük-orta öncelik
- **6** ⚫: Existing + Skor 0-29, Cold + Skor 20-39 → Düşük öncelik
- **7** 🔴: Cold + Skor 0-19 (Local: 5-19), Skip (0-39) → En düşük öncelik

**Önemli:** Migration segmenti artık düşük skorlu olsa bile öncelikli (Priority 3-4)!

### Dashboard (Özet Görünüm)

```bash
# Legacy dashboard endpoint (backward compatible)
curl "http://localhost:8000/dashboard"

# New KPI endpoint (G19) ✨ YENİ
curl "http://localhost:8000/dashboard/kpis"
```

**Legacy Dashboard Yanıtı:**
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

**New KPI Endpoint Yanıtı (G19):**
```json
{
  "total_leads": 150,
  "migration_leads": 25,
  "high_priority": 10
}
```

**Ne İşe Yarar?**
- Hızlı özet görünüm
- Segment dağılımını görme
- Ortalama skor takibi
- Yüksek öncelikli lead sayısı (Priority Score 1-2)
- **G19 Enhancement**: High Priority KPI metric eklendi

### Score Breakdown (G19) ✨ YENİ

Bir domain'in skor detaylarını görüntüleme:

```bash
curl "http://localhost:8000/leads/ornek-firma.com/score-breakdown"
```

**Ne Döner?**
```json
{
  "domain": "ornek-firma.com",
  "readiness_score": 85,
  "breakdown": {
    "base_score": 0,
    "provider_points": 50,
    "signal_points": 35,
    "risk_points": 0,
    "total": 85
  },
  "signals": {
    "spf": true,
    "dkim": true,
    "dmarc_policy": "reject",
    "dmarc_coverage": 100,
    "spf_record": "v=spf1 include:spf.protection.outlook.com -all"
  },
  "provider": "M365",
  "tenant_size": "medium",
  "local_provider": null,
  "mx_root": "outlook.com"
}
```

**Mini UI'de Kullanım:**
- Skorlara tıklayarak modal açılır
- Detaylı skor analizi görüntülenir
- Provider, sinyaller ve risk puanları gösterilir

**Ne İşe Yarar?**
- Skorun nasıl hesaplandığını anlama
- Hangi sinyallerin eksik olduğunu görme
- Risk puanlarını değerlendirme
- Migration hazırlık seviyesini anlama

### Sales Summary (G21 Phase 2) ✨ YENİ

Bir domain için satış zekası özeti:

```bash
# API v1 endpoint (önerilen)
curl "http://localhost:8000/api/v1/leads/ornek-firma.com/sales-summary"

# Legacy endpoint (backward compatible)
curl "http://localhost:8000/leads/ornek-firma.com/sales-summary"
```

**Ne Döner?**
```json
{
  "domain": "ornek-firma.com",
  "one_liner": "ornek-firma.com - Migration fırsatı, yüksek hazırlık skoru (85), Enterprise teklif hazırlanabilir.",
  "call_script": [
    "Merhaba, ornek-firma.com için email altyapınızı inceledik...",
    "..."
  ],
  "discovery_questions": [
    "Şu anki email altyapınızdan memnun musunuz?",
    "..."
  ],
  "offer_tier": {
    "tier": "Enterprise",
    "license": "Enterprise",
    "price_per_user_per_month": 20,
    "migration_fee": 10000,
    "defender_price_per_user_per_month": 10,
    "consulting_fee": 50000,
    "recommendation": "Enterprise çözümü önerilir..."
  },
  "opportunity_potential": 88,
  "urgency": "high",
  "metadata": {
    "domain": "ornek-firma.com",
    "provider": "M365",
    "segment": "Migration",
    "readiness_score": 85,
    "priority_score": 1,
    "tenant_size": "large",
    "local_provider": null,
    "generated_at": "2025-01-28T..."
  }
}
```

**Mini UI'de Kullanım:**
- Lead tablosunda "📞 Sales" butonuna tıklayarak sales summary modal'ı açılır
- One-liner, call script, discovery questions, offer tier, opportunity potential ve urgency bilgileri görüntülenir

**Ne İşe Yarar?**
- Satış ekibi için hazır call script ve discovery questions
- Offer tier önerisi (tenant size'a göre)
- Opportunity potential skoru (0-100)
- Urgency seviyesi (low/medium/high)

### Lead Enrichment (G16) ✨ YENİ

Lead'leri contact email'leri ile zenginleştirme:

```bash
# Bir lead'i contact email'leri ile zenginleştir
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

**Ne Yapıyor?**
- Contact email'lerini kaydeder
- **Contact Quality Score** hesaplar (0-100):
  - Email sayısı (daha fazla email = daha yüksek skor)
  - Domain eşleşmesi (email domain = company domain)
- **LinkedIn Pattern** tespit eder:
  - `firstname.lastname@domain.com`
  - `f.lastname@domain.com`
  - `firstname@domain.com`

**Başarılı Yanıt:**
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

**Ne İşe Yarar?**
- Satış ekibi için iletişim bilgilerini toplama
- Email kalitesi skorlaması (hangi lead'lerde daha fazla contact var)
- LinkedIn outreach için pattern tespiti
- Lead'leri daha iyi değerlendirme

**Not:** Enrichment bilgileri `GET /leads/{domain}` endpoint'inde de görüntülenir.

### Notes, Tags, Favorites (G17: CRM-lite) ✨ YENİ

**Notes (Notlar):**
- `POST /leads/{domain}/notes` - Not ekle
- `GET /leads/{domain}/notes` - Notları listele
- `PUT /leads/{domain}/notes/{note_id}` - Notu güncelle
- `DELETE /leads/{domain}/notes/{note_id}` - Notu sil

**Tags (Etiketler):**
- `POST /leads/{domain}/tags` - Tag ekle
- `GET /leads/{domain}/tags` - Tag'leri listele
- `DELETE /leads/{domain}/tags/{tag_id}` - Tag'i sil
- **Auto-tagging**: Sistem otomatik tag'ler ekler (security-risk, migration-ready, expire-soon, vb.)

**Favorites (Favoriler):**
- `POST /leads/{domain}/favorite` - Favorilere ekle
- `GET /leads?favorite=true` - Favorileri listele
- `DELETE /leads/{domain}/favorite` - Favorilerden çıkar

**PDF Summary:**
- `GET /leads/{domain}/summary.pdf` - PDF özet oluştur
- Satış sunumu için hazır PDF raporu

### ReScan ve Alerts (G18: Automation) ✨ YENİ

**ReScan:**
- `POST /scan/{domain}/rescan` - Tek domain'i yeniden tara
- `POST /scan/bulk/rescan?domain_list=...` - Toplu rescan
- Değişiklikleri tespit eder (MX, DMARC, skor, expiry)
- Alert oluşturur (değişiklik varsa)

**Alerts:**
- `GET /alerts` - Alert'leri listele (filtrelerle)
- `POST /alerts/config` - Alert konfigürasyonu
- `GET /alerts/config` - Konfigürasyonları listele
- Alert türleri: mx_changed, dmarc_added, expire_soon, score_changed
- Notification: Webhook (HTTP POST), Email (placeholder), Slack (optional)

**Daily Rescan:**
- Sistem otomatik olarak günlük rescan yapar (Celery Beat scheduler)
- Tüm domain'ler için değişiklikleri tespit eder
- Alert'ler oluşturulur ve bildirim gönderilir

### Lead Export (CSV/Excel) 📥 YENİ

Lead'leri CSV veya Excel formatında export etme:

```bash
# CSV formatında export (default)
curl "http://localhost:8000/leads/export?format=csv" -o leads.csv

# Excel formatında export
curl "http://localhost:8000/leads/export?format=xlsx" -o leads.xlsx
```

**Filtreleme ile Export:**
```bash
# Migration segment'indeki lead'leri export et
curl "http://localhost:8000/leads/export?format=csv&segment=Migration&min_score=60" -o migration-leads.csv

# Belirli provider'ı export et
curl "http://localhost:8000/leads/export?format=csv&provider=M365" -o m365-leads.csv

# Kombine filtre
curl "http://localhost:8000/leads/export?format=xlsx&segment=Migration&min_score=60&provider=Google" -o google-migration.xlsx
```

**Export Parametreleri:**
- `format`: `csv` (default) veya `xlsx`
- `segment`: Migration, Existing, Cold, Skip
- `min_score`: Minimum skor (0-100)
- `provider`: M365, Google, Yandex, vb.

**Export İçeriği:**
- Domain, company_name, provider, country
- **Tenant Size** (G20): tenant_size (small/medium/large) ✨ YENİ
- **Local Provider** (G20): local_provider (TürkHost, Natro, vb.) ✨ YENİ
- Segment, readiness_score, priority_score
- **Lead Enrichment** (G16): contact_emails, contact_quality_score, linkedin_pattern
- SPF, DKIM, DMARC policy
- **DMARC Coverage** (G20): dmarc_coverage (0-100) ✨ YENİ
- MX root, registrar, expires_at
- Nameservers, scan_status, scanned_at
- Reason (skor açıklaması)

**Dosya Adı Formatı:**
- `leads_YYYY-MM-DD_HH-MM-SS.csv`
- `leads_YYYY-MM-DD_HH-MM-SS.xlsx`

**Ne İşe Yarar?**
- Excel'de analiz yapma
- CRM'e import etme
- Raporlama ve paylaşım
- Filtrelenmiş lead listelerini kaydetme

---

## 📧 Email Araçları

### Generic Email Üretme

Bir domain için yaygın generic email adreslerini üretme:

```bash
curl -X POST http://localhost:8000/email/generate \
  -H "Content-Type: application/json" \
  -d '{"domain": "ornek-firma.com"}'
```

**Ne Üretir?**
- Türkçe: iletisim, satis, muhasebe, ik
- International: info, sales, admin, support, hr
- Toplam 9 generic email adresi

**Başarılı Yanıt:**
```json
{
  "domain": "ornek-firma.com",
  "emails": [
    "admin@ornek-firma.com",
    "hr@ornek-firma.com",
    "ik@ornek-firma.com",
    "iletisim@ornek-firma.com",
    "info@ornek-firma.com",
    "muhasebe@ornek-firma.com",
    "sales@ornek-firma.com",
    "satis@ornek-firma.com",
    "support@ornek-firma.com"
  ]
}
```

**Ne İşe Yarar?**
- Satış ekibi için iletişim email'lerini bulma
- Domain'e özel generic email'leri hızlıca üretme
- Outreach için email listesi hazırlama

### Email Üretme ve Doğrulama

Generic email'leri üretip doğrulama (syntax, MX, opsiyonel SMTP):

```bash
# Light validation (hızlı, önerilen)
curl -X POST http://localhost:8000/email/generate-and-validate \
  -H "Content-Type: application/json" \
  -d '{"domain": "ornek-firma.com", "use_smtp": false}'
```

**Ne Yapıyor?**
- Generic email'leri üretir
- Her email'i doğrular:
  - Syntax kontrolü (regex)
  - MX kaydı kontrolü (DNS)
  - SMTP kontrolü (opsiyonel, `use_smtp=true` ile)

**Başarılı Yanıt:**
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
    ...
  ]
}
```

**Status Değerleri:**
- `valid`: Email geçerli (syntax + MX OK)
- `invalid`: Email geçersiz (syntax veya MX hatası)
- `unknown`: Belirsiz (catch-all veya SMTP hatası)

**Confidence Değerleri:**
- `high`: Yüksek güven (SMTP ile doğrulandı)
- `medium`: Orta güven (sadece syntax + MX)
- `low`: Düşük güven (belirsiz durum)

**SMTP Doğrulama (Opsiyonel):**
```bash
# Full validation (yavaş, 10-30 saniye sürebilir)
curl -X POST http://localhost:8000/email/generate-and-validate \
  -H "Content-Type: application/json" \
  -d '{"domain": "ornek-firma.com", "use_smtp": true}'
```

**Not:** SMTP doğrulama yavaş olabilir (her email için 3 saniye timeout). Light validation (use_smtp=false) önerilir.

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
curl "http://localhost:8000/leads?segment=Migration&min_score=60"
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

### Senaryo 4: Email Üretme ve Doğrulama

```bash
# 1. Domain için generic email'leri üret ve doğrula
curl -X POST http://localhost:8000/email/generate-and-validate \
  -H "Content-Type: application/json" \
  -d '{"domain": "ornek-firma.com", "use_smtp": false}'

# 2. Sadece email listesi istiyorsanız (doğrulama olmadan)
curl -X POST http://localhost:8000/email/generate \
  -H "Content-Type: application/json" \
  -d '{"domain": "ornek-firma.com"}'
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

### Analiz Et (Tek Domain)
```bash
curl -X POST http://localhost:8000/scan/domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "DOMAIN-BURAYA"}'
```

### Toplu Analiz (Bulk Scan) ⚡ YENİ
```bash
# Bulk scan job oluştur
curl -X POST http://localhost:8000/scan/bulk \
  -H "Content-Type: application/json" \
  -d '{"domain_list": ["domain1.com", "domain2.com", "domain3.com"]}'

# İlerleme kontrolü (job_id'yi yukarıdaki yanıttan alın)
curl "http://localhost:8000/scan/bulk/{job_id}"

# Sonuçları alma (tamamlandığında)
curl "http://localhost:8000/scan/bulk/{job_id}/results"
```

### Migration Lead'leri Gör
```bash
curl "http://localhost:8000/leads?segment=Migration&min_score=60"
```

### Tek Lead Detayı
```bash
curl "http://localhost:8000/leads/DOMAIN-BURAYA"
```

### Dashboard Özeti
```bash
# Legacy dashboard
curl "http://localhost:8000/dashboard"

# New KPI endpoint (G19) ✨ YENİ
curl "http://localhost:8000/dashboard/kpis"
```

### Score Breakdown (G19) ✨ YENİ
```bash
curl "http://localhost:8000/leads/DOMAIN-BURAYA/score-breakdown"
```

### Sales Summary (G21 Phase 2) ✨ YENİ
```bash
# API v1 endpoint (önerilen)
curl "http://localhost:8000/api/v1/leads/DOMAIN-BURAYA/sales-summary"

# Legacy endpoint (backward compatible)
curl "http://localhost:8000/leads/DOMAIN-BURAYA/sales-summary"
```

### UI Upgrade: Sorting, Pagination, Search (G19) ✨ YENİ
```bash
# Sorting (skora göre sıralama)
curl "http://localhost:8000/leads?sort_by=readiness_score&sort_order=desc"

# Pagination (2. sayfa, 25 kayıt/sayfa)
curl "http://localhost:8000/leads?page=2&page_size=25"

# Search (domain veya şirket adında arama)
curl "http://localhost:8000/leads?search=example"

# Kombine: Arama + Filtre + Sıralama + Sayfalama
curl "http://localhost:8000/leads?segment=Migration&search=example&sort_by=readiness_score&sort_order=desc&page=1&page_size=25"
```

### Microsoft SSO Authentication (G19) ✨ YENİ
```bash
# Login (redirect to Azure AD)
curl "http://localhost:8000/auth/login"

# Current user info (requires Authorization header)
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" "http://localhost:8000/auth/me"

# Logout
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Refresh token
curl -X POST http://localhost:8000/auth/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"
```

### Lead Export (CSV/Excel)
```bash
# CSV export
curl "http://localhost:8000/leads/export?format=csv" -o leads.csv

# Excel export
curl "http://localhost:8000/leads/export?format=xlsx" -o leads.xlsx

# Filtreli export (Migration, skor 60+)
curl "http://localhost:8000/leads/export?format=csv&segment=Migration&min_score=60" -o migration-leads.csv
```

### Email Üret ve Doğrula
```bash
curl -X POST http://localhost:8000/email/generate-and-validate \
  -H "Content-Type: application/json" \
  -d '{"domain": "DOMAIN-BURAYA", "use_smtp": false}'
```

### Lead Enrichment (G16) ✨ YENİ
```bash
# Bir lead'i contact email'leri ile zenginleştir
curl -X POST http://localhost:8000/leads/DOMAIN-BURAYA/enrich \
  -H "Content-Type: application/json" \
  -d '{"contact_emails": ["email1@domain.com", "email2@domain.com"]}'
```

### Notes, Tags, Favorites (G17: CRM-lite) ✨ YENİ
```bash
# Not ekle
curl -X POST http://localhost:8000/leads/DOMAIN-BURAYA/notes \
  -H "Content-Type: application/json" \
  -d '{"note": "Müşteri ile görüşüldü, migration planı hazırlanıyor"}'

# Tag ekle
curl -X POST http://localhost:8000/leads/DOMAIN-BURAYA/tags \
  -H "Content-Type: application/json" \
  -d '{"tag": "important"}'

# Favorilere ekle
curl -X POST http://localhost:8000/leads/DOMAIN-BURAYA/favorite

# PDF özet oluştur
curl "http://localhost:8000/leads/DOMAIN-BURAYA/summary.pdf" -o domain-summary.pdf
```

### ReScan ve Alerts (G18: Automation) ✨ YENİ
```bash
# Domain'i yeniden tara (değişiklikleri tespit et)
curl -X POST http://localhost:8000/scan/DOMAIN-BURAYA/rescan

# Toplu rescan
curl -X POST "http://localhost:8000/scan/bulk/rescan?domain_list=domain1.com,domain2.com"

# Alert'leri listele
curl "http://localhost:8000/alerts?alert_type=mx_changed"

# Alert konfigürasyonu
curl -X POST http://localhost:8000/alerts/config \
  -H "Content-Type: application/json" \
  -d '{"alert_type": "mx_changed", "notification_method": "webhook", "webhook_url": "https://example.com/webhook"}'
```

---

## 📖 Dokümantasyon

### Mini UI Dokümantasyonu
- [Mini UI README](../../mini-ui/README-mini-ui.md) - Kullanım kılavuzu ve özellikler

### API Dokümantasyonu

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
**A:** `auto_scan=true` parametresi ile CSV upload sonrası otomatik analiz yapılır. Varsayılan olarak `auto_scan=true` kullanılır (Mini UI'de otomatik). Eğer `auto_scan=false` kullandıysanız, manuel olarak `/scan/domain` endpoint'ini kullanmalısınız.

### Q: Domain değişikliklerini nasıl takip ederim?
**A:** G18 ile birlikte ReScan özelliği eklendi. `POST /scan/{domain}/rescan` ile domain'i yeniden tarayabilir ve değişiklikleri (MX, DMARC, skor) tespit edebilirsiniz. Alert sistemi ile değişiklikler için bildirim alabilirsiniz.

### Q: Alert'ler nasıl çalışır?
**A:** Alert sistemi domain değişikliklerini (MX değişti, DMARC eklendi, domain expire soon, skor değişti) otomatik olarak tespit eder ve webhook/email ile bildirim gönderir. Alert konfigürasyonu `/alerts/config` endpoint'i ile yapılır.

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

### Q: Tenant Size nedir? (G20) ✨ YENİ
**A:** M365 ve Google Workspace kullanan domain'ler için MX pattern'den tahmin edilen tenant büyüklüğü:
- **small**: Küçük işletmeler (genelde 1-50 kullanıcı)
- **medium**: Orta ölçekli işletmeler (genelde 50-500 kullanıcı)
- **large**: Büyük kurumsal işletmeler (genelde 500+ kullanıcı)

### Q: Local Provider nedir? (G20) ✨ YENİ
**A:** Local provider kullanan domain'ler için spesifik provider adı (örn: TürkHost, Natro, Turhost, Superonline, TTNET, DNS, İsimtescil). Bu bilgi satış ekibi için hangi local hosting provider'ın kullanıldığını gösterir.

### Q: DMARC Coverage nedir? (G20) ✨ YENİ
**A:** DMARC policy'nin coverage yüzdesi (pct parametresi). 0-100 arası değer:
- **100**: Tüm email'ler DMARC policy'ye tabi (default, pct belirtilmemişse)
- **50**: Email'lerin %50'si DMARC policy'ye tabi
- **1**: Sadece %1'i DMARC policy'ye tabi (test aşamasında)

**Önemli:** DMARC policy "reject" olsa bile coverage düşükse (örn: pct=1), gerçek uygulama sınırlıdır.

### Q: Sistem çalışmıyor, ne yapmalıyım?
**A:** 
1. `curl http://localhost:8000/healthz` ile kontrol edin
2. Docker container'ları çalışıyor mu kontrol edin: `docker-compose ps`
3. Log'lara bakın: `docker-compose logs api`

### Q: Hata mesajları İngilizce görünüyor?
**A:** Tüm hata mesajları artık Türkçe gösterilir. Eğer İngilizce görüyorsanız, API'yi yeniden başlatın: `docker-compose restart api`

### Q: CSV yükleme sırasında ilerleme göremiyorum?
**A:** Mini UI'de CSV yükleme sonrası otomatik olarak progress bar gösterilir. Eğer görünmüyorsa, tarayıcı konsolunu kontrol edin (F12).

### Q: Skorlara tıklayınca modal açılmıyor?
**A:** Skorlar tıklanabilir olmalı (altı çizili görünür). Eğer çalışmıyorsa, tarayıcı konsolunu kontrol edin ve API endpoint'inin çalıştığından emin olun: `curl http://localhost:8000/leads/{domain}/score-breakdown`

### Q: Tablo başlıklarına tıklayınca sıralama yapılmıyor?
**A:** Tablo başlıklarında sıralama ikonları (⇅) görünmeli. Eğer çalışmıyorsa, tarayıcı konsolunu kontrol edin.

### Q: Sayfa numaraları görünmüyor?
**A:** Pagination UI'de sayfa numaraları otomatik olarak gösterilir. Eğer görünmüyorsa, toplam sayfa sayısı 1'den fazla olmalı.

---

## 👤 Satışçı Personası: "Sistematik Avcı" v2.0

**Hunter-native, CRM-integrated, multi-threaded satış avcısı profili**

### 🎭 Temel Profil

**İsim**: Emir Kara  
**Rol**: B2B Cloud Solutions Sales Specialist  
**Kıdem**: 2-3 yıl (SAAS + Cloud satış tecrübesi)  
**Kullanılan Araçlar**: Dyn365Hunter, LinkedIn Sales Navigator, Power BI, Dynamics CRM  
**Odak Alanı**: Domain → IT Decision Maker → Migration fırsatı → Teklif → Kapanış  
**KPI**: M365 Migration, Security Upsell (Defender), Cloud App Consulting, yıllık MRR

**v2.0 Farkı**: Hunter'ın tüm özelliklerini kullanan, CRM pipeline'a entegre, multi-threaded, sistematik satış avcısı.

### 🎯 Günlük Çalışma Akışı

#### 1. Sabah (09:00 – 10:00): Hunter Taraması + Alert Kontrolü + Automation

**Hunter Taraması:**
- Priority 1–2 lead'leri filtreler (`GET /leads?priority_score=1,2`)
- Migration segmenti ve 80+ skorları direkt işaretler
- Domain expire <60 gün olanları ayırır
- Provider change history'ye bakar

**Alert Kontrolü (v2.0):**
- Alert'leri kontrol eder (`GET /alerts`)
  - `mx_changed` → Migration fırsatı! Hemen aksiyon
  - `dmarc_added` → Güvenlik iyileştirmesi, upsell fırsatı!
  - `expire_soon` → Domain yenileme fırsatı!
  - `score_changed` → Lead durumu değişti, pipeline güncelle

**Hunter-native Özellikler (v2.0):**
- **Favorilere ekler** (`POST /leads/{domain}/favorite`)
- **Auto-tag'leri kontrol eder** (migration-ready, security-risk, expire-soon)
- **Tenant size'a göre filtreleme** (large → yüksek bütçe)
- **Local provider detayına bakar** (TürkHost → migration stratejisi)

**Aksiyon:** 5 firmayı listesine alır → hemen outreach

#### 2. Öğle Öncesi (10:30 – 12:00): İlk Temas + Lead Enrichment + Multi-Threaded Outreach

**Lead Enrichment (v2.0):**
- Generic email üretme ve doğrulama (`POST /email/generate-and-validate`)
- Contact enrichment (`POST /leads/{domain}/enrich`)
- Contact quality score'a bakar

**Multi-Threaded Outreach (v2.0):**
- **IT Direktörü**: Teknik mesaj (MX, SPF, DKIM, DMARC)
- **CFO**: Finansal mesaj (Mail deliverability, müşteri kaybı riski)
- **Genel Müdür**: Stratejik mesaj (Güvenlik açığı, risk yönetimi)
- **CTO**: Teknik + Stratejik mesaj (DMARC, phishing riski)

**Champion Building (v2.0):**
- IT ekibinden, güvenlik ekibinden contact bulur
- Champion'a özel mesaj
- Hunter'a not ekler: "IT ekibinden Ahmet Bey champion"

#### 3. Öğleden Sonra (13:00 – 16:00): Lead Qualification / Demo + Hunter Notları

**Demo Süreci:**
- 15 dakikalık hızlı Zoom
- Hunter ekran görüntüsü ile risk ve fırsat anlatımı
- **Tenant size'a göre teklif hazırlar** (v2.0)
  - Small → Business Basic
  - Medium → Business Standard
  - Large → Enterprise + Defender
- **Local provider detayına göre migration stratejisi** (v2.0)

**Hunter Notları ve Tag'ler (v2.0):**
- Görüşme sonrası not ekler (`POST /leads/{domain}/notes`)
- Tag ekler (`POST /leads/{domain}/tags`)
- PDF summary oluşturur (`GET /leads/{domain}/summary.pdf`)

#### 4. Gün Sonu (16:00 – 17:00): CRM Güncelleme & Follow-Up + ReScan Pipeline

**Hunter → Dynamics CRM Entegrasyonu (v2.0):**
- Hunter'dan export alır (`GET /leads/export?format=csv`)
- Dynamics CRM'e import eder
- Notes/tags senkronizasyonu
- Alert konfigürasyonu (`POST /alerts/config`)

**CRM Pipeline Mapping (v2.0):**

| Hunter Priority | Dynamics CRM Stage | Aksiyon Zamanı |
|----------------|-------------------|----------------|
| 1-2 🔥⭐ | "Qualified Lead" | Hemen (1-2 gün) |
| 3 🟡 | "Nurturing" | 1 hafta içinde |
| 4 🟠 | "Cold Lead" | 1-2 hafta |
| 5-7 ⚪⚫🔴 | "Long-term" | 1-6 ay |

**ReScan Pipeline (v2.0):**
- Favorilere eklediği lead'leri rescan eder (`POST /scan/{domain}/rescan`)
- Toplu rescan (`POST /scan/bulk/rescan`)
- Alert konfigürasyonu

### 🧨 Rejection Handling Stratejisi (v2.0)

#### 1. "Şu An İlgilenmiyoruz"
- Hunter'a not ekler: "6 ay sonra tekrar denenecek"
- Tag ekler: `not-interested`, `follow-up-6months`
- Alert konfigürasyonu: 6 ay sonra rescan

#### 2. "Zaten Başka Bir Çözüm Kullanıyoruz"
- Upsell fırsatı: Defender, Power Automate, Dynamics 365
- Hunter'a not ekler: "Existing customer, Defender upsell fırsatı"
- Tag ekler: `existing-customer`, `upsell-opportunity`

#### 3. "Bütçe Yok"
- Alternatif çözümler: Business Basic, aşamalı migration, free trial
- Hunter'a not ekler: "3 ay sonra tekrar denenecek"
- Tag ekler: `budget-constraint`, `follow-up-3months`

### 💰 Pricing Strategy (v2.0)

**Tenant Size'a Göre Pricing:**
- **Small (1-50)**: Business Basic €5/kullanıcı/ay, Migration €500
- **Medium (50-500)**: Business Standard €10/kullanıcı/ay, Migration €2,000
- **Large (500+)**: Enterprise €20/kullanıcı/ay, Migration €10,000, Consulting €50,000

**Value-Based Pricing:**
- ROI hesaplama: Mail deliverability artışı, phishing önleme, IT maliyeti düşüşü
- Hunter'dan risk sinyallerini kullanır (SPF yok, DMARC none, domain expire soon)

### 📚 Detaylı Persona Dokümantasyonu

Daha detaylı bilgi için:
- [SALES-PERSONA-v2.0.md](SALES-PERSONA-v2.0.md) - Tam persona dokümantasyonu
- [SALES-TRAINING.md](SALES-TRAINING.md) - Eğitim materyali

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

### Yöntem 1: Mini UI (Önerilen - Kolay) 🖥️

1. **Mini UI'yi Aç**
   ```
   http://localhost:8000/mini-ui/
   ```

2. **CSV Yükle veya Domain Tara**
   - CSV/Excel dosyası yükle
   - Veya tek domain tara (otomatik ingest + scan)

3. **Lead'leri Gör ve Export Et**
   - Filtrelerle lead listesini görüntüle
   - Export butonu ile CSV indir

**Hepsi bu kadar! 🎉**

### Yöntem 2: API (curl komutları) 💻

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
   curl "http://localhost:8000/leads?segment=Migration&min_score=60"
   
   # Lead'leri CSV/Excel olarak export et
   curl "http://localhost:8000/leads/export?format=csv&segment=Migration&min_score=60" -o migration-leads.csv
   ```

**İpuçları:**
- **Mini UI kullanın** - Daha kolay ve hızlı! 🖥️
- Priority Score 1-2 olan lead'lere öncelik verin!
- Lead'leri Excel'e export edip detaylı analiz yapabilirsiniz!

