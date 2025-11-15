# Dyn365Hunter - Satış Ekibi Eğitim Materyali

**Persona v2.0: "Sistematik Avcı" Eğitim Rehberi**

**Tarih**: 2025-01-28  
**Versiyon**: 2.0  
**Hedef Kitle**: Yeni satış ekibi üyeleri, mevcut satışçılar (v2.0 güncellemesi)

---

## 🎯 Eğitim Hedefleri

Bu eğitim sonunda satış ekibi:

1. ✅ Hunter'ın tüm özelliklerini kullanabilecek (G17, G18, G20)
2. ✅ Hunter → Dynamics CRM pipeline mapping'i anlayacak
3. ✅ Multi-threaded outreach stratejisini uygulayacak
4. ✅ Rejection handling senaryolarını bilecek
5. ✅ Pricing strategy'sini uygulayacak
6. ✅ Competition awareness'a sahip olacak

---

## 📚 Eğitim Modülleri

### Modül 1: Hunter Temelleri (30 dakika)

#### 1.1 Hunter'a Giriş
- Hunter nedir?
- Hunter'ın satışçı için değeri
- Hunter'ın temel özellikleri

#### 1.2 Priority Score ve Segment
- Priority Score nedir? (1-7)
- Segment nedir? (Migration, Existing, Cold, Skip)
- Hangi lead'lere öncelik verilmeli?

**Pratik Egzersiz:**
```bash
# Priority 1-2 lead'leri filtrele
curl "http://localhost:8000/leads?priority_score=1,2"

# Migration segment'indeki yüksek skorlu lead'leri filtrele
curl "http://localhost:8000/leads?segment=Migration&min_score=70"
```

#### 1.3 Hunter'ın Temel Workflow'u
1. Domain ekle (`POST /ingest/domain`)
2. Domain tara (`POST /scan/domain`)
3. Lead'leri gör (`GET /leads`)
4. Export et (`GET /leads/export`)

**Pratik Egzersiz:**
- 3 domain ekle ve tara
- Sonuçları görüntüle
- CSV export yap

---

### Modül 2: Hunter-native Özellikler (45 dakika) - v2.0

#### 2.1 Notes, Tags, Favorites (G17)

**Notes (Notlar):**
- Lead için not ekleme
- Notları görüntüleme
- Notları güncelleme
- Notları silme

**Pratik Egzersiz:**
```bash
# Not ekle
curl -X POST http://localhost:8000/leads/example.com/notes \
  -H "Content-Type: application/json" \
  -d '{"note": "IT Direktörü ile görüşüldü, migration planı hazırlanıyor"}'

# Notları listele
curl "http://localhost:8000/leads/example.com/notes"
```

**Tags (Etiketler):**
- Tag ekleme
- Auto-tag'ler (migration-ready, security-risk, expire-soon)
- Tag'leri görüntüleme
- Tag'leri silme

**Pratik Egzersiz:**
```bash
# Tag ekle
curl -X POST http://localhost:8000/leads/example.com/tags \
  -H "Content-Type: application/json" \
  -d '{"tag": "high-priority"}'

# Tag'leri listele
curl "http://localhost:8000/leads/example.com/tags"
```

**Favorites (Favoriler):**
- Favorilere ekleme
- Favorileri görüntüleme
- Favorilerden çıkarma

**Pratik Egzersiz:**
```bash
# Favorilere ekle
curl -X POST http://localhost:8000/leads/example.com/favorite

# Favorileri listele
curl "http://localhost:8000/leads?favorite=true"
```

#### 2.2 ReScan ve Alerts (G18)

**ReScan:**
- Tek domain rescan
- Toplu rescan
- Değişiklik tespiti

**Pratik Egzersiz:**
```bash
# Tek domain rescan
curl -X POST http://localhost:8000/scan/example.com/rescan

# Toplu rescan
curl -X POST "http://localhost:8000/scan/bulk/rescan?domain_list=example1.com,example2.com"
```

**Alerts:**
- Alert türleri (mx_changed, dmarc_added, expire_soon, score_changed)
- Alert'leri görüntüleme
- Alert konfigürasyonu

**Pratik Egzersiz:**
```bash
# Alert'leri listele
curl "http://localhost:8000/alerts"

# Alert konfigürasyonu
curl -X POST http://localhost:8000/alerts/config \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "mx_changed",
    "notification_method": "webhook",
    "webhook_url": "https://example.com/webhook"
  }'
```

#### 2.3 Lead Enrichment (G16)

**Generic Email Üretme ve Doğrulama:**
- Generic email'leri üretme
- Email doğrulama (syntax + MX + SMTP)

**Pratik Egzersiz:**
```bash
# Generic email üret ve doğrula
curl -X POST http://localhost:8000/email/generate-and-validate \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "use_smtp": false}'
```

**Contact Enrichment:**
- Contact email'leri ekleme
- Contact quality score
- LinkedIn pattern tespiti

**Pratik Egzersiz:**
```bash
# Contact enrichment
curl -X POST http://localhost:8000/leads/example.com/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "contact_emails": [
      "john.doe@example.com",
      "jane.smith@example.com"
    ]
  }'
```

#### 2.4 Tenant Size ve Local Provider (G20)

**Tenant Size:**
- Tenant size nedir? (small, medium, large)
- Tenant size'a göre pricing stratejisi

**Pratik Egzersiz:**
```bash
# Lead detayını gör (tenant_size bilgisi ile)
curl "http://localhost:8000/leads/example.com"
```

**Local Provider:**
- Local provider detayı (TürkHost, Natro, vb.)
- Local provider'a göre migration stratejisi

**Pratik Egzersiz:**
```bash
# Lead detayını gör (local_provider bilgisi ile)
curl "http://localhost:8000/leads/example.com"
```

#### 2.5 PDF Summary

**PDF Summary Oluşturma:**
- PDF summary nedir?
- Satış sunumu için kullanımı

**Pratik Egzersiz:**
```bash
# PDF summary oluştur
curl "http://localhost:8000/leads/example.com/summary.pdf" -o example-summary.pdf
```

---

### Modül 3: CRM Entegrasyonu (30 dakika) - v2.0

#### 3.1 Hunter → Dynamics CRM Veri Akışı

**Export ve Import:**
- Hunter'dan export (CSV/Excel)
- Dynamics CRM'e import
- Notes/tags senkronizasyonu

**Pratik Egzersiz:**
```bash
# Hunter'dan export
curl "http://localhost:8000/leads/export?format=csv&segment=Migration&min_score=70" -o migration-leads.csv

# Dynamics CRM'e import (manuel veya webhook)
```

#### 3.2 CRM Pipeline Mapping

**Priority Score → CRM Stage Mapping:**

| Hunter Priority | Dynamics CRM Stage | Aksiyon Zamanı |
|----------------|-------------------|----------------|
| 1-2 🔥⭐ | "Qualified Lead" | Hemen (1-2 gün) |
| 3 🟡 | "Nurturing" | 1 hafta içinde |
| 4 🟠 | "Cold Lead" | 1-2 hafta |
| 5-7 ⚪⚫🔴 | "Long-term" | 1-6 ay |

**Pratik Egzersiz:**
- Priority 1-2 lead'leri Dynamics CRM'de "Qualified Lead" stage'ine taşı
- Priority 3 lead'leri "Nurturing" stage'ine taşı
- Priority 4 lead'leri "Cold Lead" stage'ine taşı

#### 3.3 Alert Webhook Konfigürasyonu

**Webhook → Dynamics CRM:**
- Alert webhook konfigürasyonu
- Dynamics CRM'e alert gönderme

**Pratik Egzersiz:**
```bash
# Alert webhook konfigürasyonu
curl -X POST http://localhost:8000/alerts/config \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "mx_changed",
    "notification_method": "webhook",
    "webhook_url": "https://dynamics-crm.example.com/webhook"
  }'
```

---

### Modül 4: Multi-Threaded Outreach (30 dakika) - v2.0

#### 4.1 Birden Fazla Karar Vericiye Ulaşma

**Role-Based Mesajlaşma:**
- IT Direktörü: Teknik mesaj (MX, SPF, DKIM, DMARC)
- CFO: Finansal mesaj (Mail deliverability, müşteri kaybı riski)
- Genel Müdür: Stratejik mesaj (Güvenlik açığı, risk yönetimi)
- CTO: Teknik + Stratejik mesaj (DMARC, phishing riski)

**Pratik Egzersiz:**
- 4 farklı role için mesaj şablonu hazırla
- Her role için özel value proposition belirle

#### 4.2 Champion Building

**Champion Bulma:**
- IT ekibinden contact bulma
- Güvenlik ekibinden contact bulma
- Sistem yöneticisinden contact bulma

**Pratik Egzersiz:**
- Hunter'dan contact enrichment kullan
- Champion'a özel mesaj hazırla
- Hunter'a not ekle: "IT ekibinden Ahmet Bey champion"

---

### Modül 5: Rejection Handling (30 dakika) - v2.0

#### 5.1 "Şu An İlgilenmiyoruz" Senaryosu

**Strateji:**
1. Hunter'a not ekle: "6 ay sonra tekrar denenecek"
2. Tag ekle: `not-interested`, `follow-up-6months`
3. Alert konfigürasyonu: 6 ay sonra rescan
4. Dynamics CRM'de "Long-term" stage'ine taşı

**Pratik Egzersiz:**
```bash
# Not ekle
curl -X POST http://localhost:8000/leads/example.com/notes \
  -H "Content-Type: application/json" \
  -d '{"note": "Müşteri şu an ilgilenmiyor, 6 ay sonra tekrar denenecek"}'

# Tag ekle
curl -X POST http://localhost:8000/leads/example.com/tags \
  -H "Content-Type: application/json" \
  -d '{"tag": "not-interested"}'
```

#### 5.2 "Zaten Başka Bir Çözüm Kullanıyoruz" Senaryosu

**Strateji:**
1. Upsell fırsatı: Defender, Power Automate, Dynamics 365
2. Hunter'a not ekle: "Existing customer, Defender upsell fırsatı"
3. Tag ekle: `existing-customer`, `upsell-opportunity`

**Pratik Egzersiz:**
```bash
# Not ekle
curl -X POST http://localhost:8000/leads/example.com/notes \
  -H "Content-Type: application/json" \
  -d '{"note": "Müşteri zaten M365 kullanıyor, Defender upsell fırsatı"}'

# Tag ekle
curl -X POST http://localhost:8000/leads/example.com/tags \
  -H "Content-Type: application/json" \
  -d '{"tag": "upsell-opportunity"}'
```

#### 5.3 "Bütçe Yok" Senaryosu

**Strateji:**
1. Alternatif çözümler: Business Basic, aşamalı migration, free trial
2. Hunter'a not ekle: "3 ay sonra tekrar denenecek"
3. Tag ekle: `budget-constraint`, `follow-up-3months`

**Pratik Egzersiz:**
```bash
# Not ekle
curl -X POST http://localhost:8000/leads/example.com/notes \
  -H "Content-Type: application/json" \
  -d '{"note": "Bütçe yok, 3 ay sonra tekrar denenecek"}'

# Tag ekle
curl -X POST http://localhost:8000/leads/example.com/tags \
  -H "Content-Type: application/json" \
  -d '{"tag": "budget-constraint"}'
```

---

### Modül 6: Pricing Strategy (30 dakika) - v2.0

#### 6.1 Tenant Size'a Göre Pricing

**Pricing Tablosu:**

| Tenant Size | Lisans | Migration | Toplam (50 kullanıcı) |
|-------------|--------|-----------|----------------------|
| Small (1-50) | Business Basic €5/kullanıcı/ay | €500 | €5,500/yıl |
| Medium (50-500) | Business Standard €10/kullanıcı/ay | €2,000 | €60,000/yıl |
| Large (500+) | Enterprise €20/kullanıcı/ay | €10,000 | €1,200,000/yıl |

**Pratik Egzersiz:**
- Tenant size'a göre teklif hazırla
- Hunter'dan tenant size bilgisini kullan

#### 6.2 Value-Based Pricing

**ROI Hesaplama:**
- Mail deliverability %40 artış → Müşteri kaybı önleme
- DMARC reject → Phishing saldırısı önleme
- M365 migration → IT maliyeti düşüşü

**Hunter'dan Risk Sinyallerini Kullan:**
- SPF yok → Phishing riski
- DMARC none → Email spoofing riski
- Domain expire soon → Domain kaybı riski

**Pratik Egzersiz:**
- Hunter'dan risk sinyallerini çıkar
- Value proposition hazırla: "Mail deliverability %40 artış → €X müşteri kaybı önleme"

---

### Modül 7: Competition Awareness (30 dakika) - v2.0

#### 7.1 Google Workspace → M365 Migration

**Strateji:**
1. Migration fırsatı: "M365 daha iyi Office entegrasyonu, Dynamics 365 ile uyumlu"
2. Hunter'a not ekle: "Google Workspace kullanıyor, M365 migration fırsatı"
3. Tag ekle: `google-workspace`, `migration-opportunity`

**Pratik Egzersiz:**
```bash
# Not ekle
curl -X POST http://localhost:8000/leads/example.com/notes \
  -H "Content-Type: application/json" \
  -d '{"note": "Google Workspace kullanıyor, M365 migration fırsatı"}'

# Tag ekle
curl -X POST http://localhost:8000/leads/example.com/tags \
  -H "Content-Type: application/json" \
  -d '{"tag": "google-workspace"}'
```

#### 7.2 Local Provider → M365 Migration

**Strateji:**
1. Migration fırsatı: "M365 daha güvenli, daha profesyonel, daha ölçeklenebilir"
2. Hunter'dan local provider detayını kullan (TürkHost, Natro)
3. Hunter'a not ekle: "TürkHost kullanıyor, M365 migration fırsatı"
4. Tag ekle: `local-mx`, `migration-opportunity`, `turkhost-migration`

**Pratik Egzersiz:**
```bash
# Not ekle
curl -X POST http://localhost:8000/leads/example.com/notes \
  -H "Content-Type: application/json" \
  -d '{"note": "TürkHost kullanıyor, M365 migration fırsatı"}'

# Tag ekle
curl -X POST http://localhost:8000/leads/example.com/tags \
  -H "Content-Type: application/json" \
  -d '{"tag": "turkhost-migration"}'
```

---

## 🎯 Pratik Senaryolar

### Senaryo 1: Yeni Lead Listesi Analizi (v2.0)

**Durum:** 100 domain'lik yeni lead listesi

**Adımlar:**
1. CSV/Excel yükle (otomatik scan ile)
2. Priority 1-2 lead'leri filtrele
3. Favorilere ekle
4. Auto-tag'leri kontrol et
5. Tenant size'a göre filtrele
6. Export et → Dynamics CRM'e import

**Pratik Egzersiz:**
```bash
# CSV yükle
curl -X POST "http://localhost:8000/ingest/csv?auto_scan=true" \
  -F "file=@yeni-leadler.csv"

# Priority 1-2 lead'leri filtrele
curl "http://localhost:8000/leads?priority_score=1,2"

# Favorilere ekle
curl -X POST http://localhost:8000/leads/example.com/favorite

# Export et
curl "http://localhost:8000/leads/export?format=csv&priority_score=1,2" -o priority-leads.csv
```

### Senaryo 2: Alert Tabanlı Proaktif Satış (v2.0)

**Durum:** Alert geldi: MX değişti

**Adımlar:**
1. Alert'i kontrol et
2. Domain'i rescan et
3. Değişiklikleri tespit et
4. Migration fırsatı mı? → Hemen outreach
5. Hunter'a not ekle
6. Tag ekle: `mx-changed`, `migration-opportunity`

**Pratik Egzersiz:**
```bash
# Alert'leri kontrol et
curl "http://localhost:8000/alerts?alert_type=mx_changed"

# Domain'i rescan et
curl -X POST http://localhost:8000/scan/example.com/rescan

# Not ekle
curl -X POST http://localhost:8000/leads/example.com/notes \
  -H "Content-Type: application/json" \
  -d '{"note": "MX değişti, migration fırsatı tespit edildi"}'
```

### Senaryo 3: Multi-Threaded Outreach (v2.0)

**Durum:** Priority 1 lead bulundu

**Adımlar:**
1. Lead enrichment yap (generic email, contact enrichment)
2. 4 role'e ulaş (IT Direktörü, CFO, Genel Müdür, CTO)
3. Role-based mesaj gönder
4. Champion bul (IT ekibi, güvenlik ekibi)
5. Hunter'a not ekle
6. Tag ekle: `multi-threaded`, `champion-found`

**Pratik Egzersiz:**
```bash
# Lead enrichment
curl -X POST http://localhost:8000/leads/example.com/enrich \
  -H "Content-Type: application/json" \
  -d '{"contact_emails": ["it@example.com", "cfo@example.com"]}'

# Not ekle
curl -X POST http://localhost:8000/leads/example.com/notes \
  -H "Content-Type: application/json" \
  -d '{"note": "4 role'e ulaşıldı, IT ekibinden Ahmet Bey champion"}'
```

---

## 📊 Değerlendirme

### Pratik Test

**Test 1: Hunter Temelleri**
- [ ] Domain ekle ve tara
- [ ] Priority 1-2 lead'leri filtrele
- [ ] CSV export yap

**Test 2: Hunter-native Özellikler**
- [ ] Not ekle, görüntüle, güncelle
- [ ] Tag ekle, görüntüle
- [ ] Favorilere ekle, görüntüle
- [ ] ReScan yap
- [ ] Alert konfigürasyonu yap
- [ ] Lead enrichment yap
- [ ] PDF summary oluştur

**Test 3: CRM Entegrasyonu**
- [ ] Hunter'dan export yap
- [ ] Priority Score → CRM Stage mapping yap
- [ ] Alert webhook konfigürasyonu yap

**Test 4: Multi-Threaded Outreach**
- [ ] 4 role için mesaj şablonu hazırla
- [ ] Champion bul ve not ekle

**Test 5: Rejection Handling**
- [ ] 3 rejection senaryosunu uygula
- [ ] Not ve tag ekle

**Test 6: Pricing Strategy**
- [ ] Tenant size'a göre pricing hazırla
- [ ] Value-based pricing hazırla

**Test 7: Competition Awareness**
- [ ] Google Workspace → M365 migration stratejisi
- [ ] Local Provider → M365 migration stratejisi

---

## 📚 Ek Kaynaklar

### Dokümantasyon
- [SALES-GUIDE.md](SALES-GUIDE.md) - Satış ekibi kullanım kılavuzu
- [SALES-PERSONA-v2.0.md](SALES-PERSONA-v2.0.md) - Tam persona dokümantasyonu
- [SALES-SCENARIOS.md](SALES-SCENARIOS.md) - Pratik senaryolar
- [SEGMENT-GUIDE.md](SEGMENT-GUIDE.md) - Segment ve skor açıklamaları

### API Dokümantasyonu
- http://localhost:8000/docs - Swagger UI

### Mini UI
- http://localhost:8000/mini-ui/ - Web arayüzü

---

## ✅ Eğitim Tamamlama Checklist

- [ ] Modül 1: Hunter Temelleri tamamlandı
- [ ] Modül 2: Hunter-native Özellikler tamamlandı
- [ ] Modül 3: CRM Entegrasyonu tamamlandı
- [ ] Modül 4: Multi-Threaded Outreach tamamlandı
- [ ] Modül 5: Rejection Handling tamamlandı
- [ ] Modül 6: Pricing Strategy tamamlandı
- [ ] Modül 7: Competition Awareness tamamlandı
- [ ] Pratik Testler tamamlandı
- [ ] Gerçek lead'lerle pratik yapıldı

---

**Son Güncelleme**: 2025-01-28  
**Versiyon**: 2.0  
**Durum**: Eğitim materyali hazır

