# Dyn365Hunter - Segment ve Skor Rehberi

**Satış Ekibi İçin Segment ve Skor Açıklamaları**

---

## 🎯 Priority Score (Öncelik Skoru)

### Priority Score Nedir?

Priority Score, segment ve readiness score kombinasyonuna göre hesaplanan öncelik seviyesidir (1-6).

| Priority | Segment + Skor | Anlam | Aksiyon Zamanı |
|----------|----------------|-------|----------------|
| **1** | Migration + 80+ | 🟢 En yüksek öncelik | Hemen (1 gün) |
| **2** | Migration + 70-79 | 🟢 Yüksek öncelik | Hemen (1-2 gün) |
| **3** | Existing + 70+ | 🟡 Orta-yüksek öncelik | 1 hafta içinde |
| **4** | Existing + 50-69 | 🟡 Orta öncelik | 1-2 hafta |
| **5** | Cold + 40+ | 🟠 Düşük öncelik | 1-2 ay |
| **6** | Diğerleri | 🔴 En düşük öncelik | 3-6 ay |

**Kullanım:**
- Lead listelerinde `priority_score` field'ı ile sıralama yapabilirsiniz
- Priority Score 1-2 olan lead'lere öncelik verin
- Dashboard'da yüksek öncelikli lead sayısını görebilirsiniz

---

## 📊 Skor Sistemi (0-100)

### Skor Aralıkları

| Skor | Anlam | Aksiyon |
|------|-------|---------|
| **70-100** | 🟢 **Yüksek Hazırlık** | Hemen aksiyon alınabilir, yüksek öncelik |
| **50-69** | 🟡 **Orta Hazırlık** | Takip edilebilir, orta öncelik |
| **20-49** | 🟠 **Düşük Hazırlık** | Daha fazla sinyal gerekli, düşük öncelik |
| **0-19** | 🔴 **Çok Düşük** | Şimdilik atlanabilir, çok düşük öncelik |

### Skor Nasıl Hesaplanır?

**Skor = Provider Puanı + Sinyal Puanları - Risk Puanları**

> **Not:** Skor 0'dan küçük olamaz (0'a yuvarlanır) ve 100'den büyük olamaz (100'e sınırlanır).

### Hard-Fail Kuralları ⚠️ YENİ

Bazı durumlarda domain otomatik olarak **Skip** segmentine atanır (skor 0):

- **MX kaydı yok**: Domain'de hiç MX kaydı yoksa → Hard-fail → Skip

> **Not:** Hard-fail kuralları diğer tüm kurallardan önce kontrol edilir. Hard-fail durumunda skor hesaplaması yapılmaz.

#### Provider Puanları
- **M365**: 50 puan
- **Google**: 50 puan
- **Yandex**: 30 puan
- **Zoho**: 30 puan
- **Amazon**: 20 puan
- **SendGrid**: 20 puan
- **Mailgun**: 20 puan
- **Hosting**: 20 puan ⬆️ (güncellendi: 10'dan 20'ye)
- **Local**: 10 puan ⬆️ (güncellendi: 0'dan 10'a)
- **Unknown**: 0 puan

#### Sinyal Puanları (Pozitif)
- **SPF kaydı var**: +10 puan
- **DKIM kaydı var**: +10 puan
- **DMARC policy = quarantine**: +15 puan
- **DMARC policy = reject**: +20 puan
- **DMARC policy = none**: 0 puan

#### Risk Puanları (Negatif) ⚠️ YENİ
- **SPF kaydı yok**: -10 puan
- **DKIM kaydı yok**: -10 puan
- **DMARC policy = none**: -10 puan (ek risk)
- **Hosting + SPF/DKIM yok**: -10 puan (zayıf hosting MX)

**Örnek 1 (Pozitif):**
- Provider: M365 (50 puan)
- SPF var (10 puan)
- DKIM var (10 puan)
- DMARC reject (20 puan)
- **Toplam Skor: 90**

**Örnek 2 (Risk Puanları ile):**
- Provider: Local (10 puan)
- SPF yok (-10 puan risk)
- DKIM yok (-10 puan risk)
- **Toplam Skor: 0** (10 - 10 - 10 = -10 → 0'a yuvarlanır)

**Örnek 3 (Hosting Zayıf):**
- Provider: Hosting (20 puan)
- SPF yok (-10 puan risk)
- DKIM yok (-10 puan risk)
- Hosting MX zayıf (-10 puan risk)
- **Toplam Skor: 0** (20 - 10 - 10 - 10 = -10 → 0'a yuvarlanır)

---

## 🎯 Segment'ler

### 1. Migration (Yüksek Öncelik) 🟢

**Ne Demek?**
- Yüksek hazırlık skoru (70+) ile bilinen cloud provider kullanıyor
- Migration için hazır görünüyor
- Hemen iletişime geçilebilir

**Koşullar:**
- Skor: **70 ve üzeri**
- Provider: M365, Google, Yandex, Zoho

**Aksiyon Planı:**
1. ✅ **Hemen iletişime geç** - Yüksek öncelik
2. ✅ **Migration teklifi hazırla** - Hazır görünüyor
3. ✅ **Teknik detayları topla** - SPF/DKIM/DMARC zaten var
4. ✅ **Hızlı karar beklenebilir** - Yüksek hazırlık

**Örnek Senaryo:**
```
Domain: ornek-firma.com
Skor: 85
Provider: M365
Segment: Migration
Aksiyon: Hemen arama yap, migration teklifi hazırla
```

---

### 2. Existing (Mevcut Müşteri) 🟡

**Ne Demek?**
- Orta-yüksek hazırlık skoru (50+) ile cloud/hosting provider kullanıyor
- Zaten müşteri olabilir veya yakın zamanda olabilir
- Takip edilmeli

**Koşullar:**
- Skor: **50 ve üzeri**
- Provider: M365, Google, Yandex, Zoho, Amazon, SendGrid, Mailgun

**Aksiyon Planı:**
1. ✅ **Müşteri durumunu kontrol et** - Zaten müşteri mi?
2. ✅ **Takip et** - Migration fırsatı olabilir
3. ✅ **Upsell/Cross-sell değerlendir** - Mevcut müşteri ise
4. ✅ **Düzenli kontrol** - Skor değişikliklerini takip et

**Örnek Senaryo:**
```
Domain: mevcut-musteri.com
Skor: 65
Provider: M365
Segment: Existing
Aksiyon: CRM'de kontrol et, müşteri ise upsell değerlendir
```

---

### 3. Cold (Soğuk Lead) 🟠

**Ne Demek?**
- Düşük-orta hazırlık skoru (20-49)
- Daha fazla sinyal gerekli
- Şimdilik düşük öncelik

**Koşullar:**
- Skor: **20-49 arası**
- Provider: Herhangi biri (veya bilinmeyen)

**Aksiyon Planı:**
1. ⏸️ **Şimdilik bekle** - Düşük öncelik
2. 📅 **1-2 ay sonra tekrar kontrol et** - Skor değişebilir
3. 📧 **Genel bilgilendirme gönder** - Soğuk lead nurturing
4. 🔍 **Daha fazla sinyal topla** - SPF/DKIM/DMARC eksik olabilir

**Örnek Senaryo:**
```
Domain: soguk-lead.com
Skor: 35
Provider: Hosting
Segment: Cold
Aksiyon: 1 ay sonra tekrar analiz et, genel bilgilendirme gönder
```

---

### 4. Skip (Atla) 🔴

**Ne Demek?**
- Çok düşük hazırlık skoru (0-19)
- Şimdilik atlanabilir
- Zaman kaybı olabilir

**Koşullar:**
- Skor: **0-19 arası**
- Provider: Herhangi biri (genelde Local veya Unknown)

**Aksiyon Planı:**
1. ❌ **Şimdilik atla** - Çok düşük öncelik
2. 📅 **3-6 ay sonra tekrar kontrol et** - Durum değişebilir
3. 🗑️ **Zaman kaybı olabilir** - Diğer lead'lere odaklan
4. 📊 **İstatistik için kaydet** - Gelecekte değerlendirilebilir

**Örnek Senaryo:**
```
Domain: atlanabilir.com
Skor: 5
Provider: Local
Segment: Skip
Aksiyon: Şimdilik atla, 3 ay sonra tekrar kontrol et
```

---

## 📈 Segment Karşılaştırması

| Segment | Skor Aralığı | Öncelik | Aksiyon Zamanı | Başarı Olasılığı |
|---------|--------------|---------|----------------|-----------------|
| **Migration** | 70-100 | 🟢 Yüksek | Hemen | Yüksek |
| **Existing** | 50-69 | 🟡 Orta | 1-2 hafta | Orta-Yüksek |
| **Cold** | 20-49 | 🟠 Düşük | 1-2 ay | Düşük-Orta |
| **Skip** | 0-19 | 🔴 Çok Düşük | 3-6 ay | Çok Düşük |

---

## 🎯 Segment'e Göre Aksiyon Planı

### Migration Segment'i İçin

**Hedef:** Hızlı karar ve migration

**Aksiyonlar:**
1. ✅ İlk iletişim (1-2 gün içinde)
2. ✅ Migration teklifi hazırla
3. ✅ Teknik detayları topla
4. ✅ Hızlı karar bekle

**Başarı Kriterleri:**
- İlk görüşme: 1 hafta içinde
- Teklif: 2 hafta içinde
- Karar: 1 ay içinde

---

### Existing Segment'i İçin

**Hedef:** Takip ve upsell/cross-sell

**Aksiyonlar:**
1. ✅ Müşteri durumunu kontrol et
2. ✅ Düzenli takip (aylık)
3. ✅ Upsell/Cross-sell değerlendir
4. ✅ Migration fırsatı ara

**Başarı Kriterleri:**
- Müşteri ise: Upsell başarısı
- Müşteri değilse: Migration fırsatı

---

### Cold Segment'i İçin

**Hedef:** Nurturing ve sinyal toplama

**Aksiyonlar:**
1. ⏸️ Genel bilgilendirme gönder
2. 📅 1-2 ay sonra tekrar kontrol et
3. 📧 Düzenli içerik paylaş
4. 🔍 Skor değişikliklerini takip et

**Başarı Kriterleri:**
- Skor artışı: 20+ → 50+
- Segment değişimi: Cold → Existing/Migration

---

### Skip Segment'i İçin

**Hedef:** Zaman kaybını önle

**Aksiyonlar:**
1. ❌ Şimdilik atla
2. 📅 3-6 ay sonra tekrar kontrol et
3. 🗑️ Diğer lead'lere odaklan
4. 📊 İstatistik için kaydet

**Başarı Kriterleri:**
- Zaman tasarrufu
- Diğer segment'lere odaklanma

---

## 🔍 Skor Yorumlama Örnekleri

### Örnek 1: Yüksek Skor (Migration)

```json
{
  "domain": "ornek-firma.com",
  "score": 90,
  "segment": "Migration",
  "provider": "M365",
  "spf": true,
  "dkim": true,
  "dmarc_policy": "reject",
  "priority_score": 1
}
```

**Yorum:**
- ✅ M365 kullanıyor (50 puan)
- ✅ SPF var (10 puan)
- ✅ DKIM var (10 puan)
- ✅ DMARC reject (20 puan)
- **Toplam: 90 puan** → Migration segment'i
- **Priority Score: 1** → En yüksek öncelik
- **Aksiyon:** Hemen iletişime geç, migration teklifi hazırla

---

### Örnek 2: Orta Skor (Existing)

```json
{
  "domain": "mevcut-musteri.com",
  "score": 60,
  "segment": "Existing",
  "provider": "Google",
  "spf": true,
  "dkim": false,
  "dmarc_policy": "quarantine",
  "priority_score": 4
}
```

**Yorum:**
- ✅ Google kullanıyor (50 puan)
- ✅ SPF var (10 puan)
- ❌ DKIM yok (0 puan)
- ⚠️ DMARC quarantine (15 puan)
- **Toplam: 60 puan** → Existing segment'i
- **Priority Score: 4** → Orta öncelik
- **Aksiyon:** Müşteri durumunu kontrol et, takip et

---

### Örnek 3: Düşük Skor (Cold)

```json
{
  "domain": "soguk-lead.com",
  "score": 30,
  "segment": "Cold",
  "provider": "Hosting",
  "spf": true,
  "dkim": false,
  "dmarc_policy": "none"
}
```

**Yorum:**
- ⚠️ Hosting kullanıyor (10 puan)
- ✅ SPF var (10 puan)
- ❌ DKIM yok (0 puan)
- ❌ DMARC none (0 puan)
- **Toplam: 30 puan** → Cold segment'i
- **Aksiyon:** 1-2 ay sonra tekrar kontrol et, genel bilgilendirme gönder

---

### Örnek 4: Çok Düşük Skor (Skip)

```json
{
  "domain": "atlanabilir.com",
  "score": 5,
  "segment": "Skip",
  "provider": "Local",
  "spf": false,
  "dkim": false,
  "dmarc_policy": "none"
}
```

**Yorum:**
- ❌ Local kullanıyor (0 puan)
- ❌ SPF yok (0 puan)
- ❌ DKIM yok (0 puan)
- ❌ DMARC none (0 puan)
- **Toplam: 5 puan** → Skip segment'i
- **Aksiyon:** Şimdilik atla, 3-6 ay sonra tekrar kontrol et

---

## 📧 Lead Enrichment (G16) ✨ YENİ

### Enrichment Nedir?

Lead enrichment, lead'leri contact email'leri ile zenginleştirme özelliğidir.

**Enrichment Fields:**
- **contact_emails**: Contact email adresleri listesi
- **contact_quality_score**: Email kalitesi skoru (0-100)
  - Email sayısı (daha fazla email = daha yüksek skor)
  - Domain eşleşmesi (email domain = company domain)
- **linkedin_pattern**: LinkedIn email pattern'i
  - `firstname.lastname@domain.com`
  - `f.lastname@domain.com`
  - `firstname@domain.com`

### Enrichment Nasıl Kullanılır?

**Manuel Enrichment:**
```bash
curl -X POST http://localhost:8000/leads/example.com/enrich \
  -H "Content-Type: application/json" \
  -d '{"contact_emails": ["john@example.com", "jane@example.com"]}'
```

**Otomatik Enrichment:**
- Webhook endpoint'i ile otomatik enrichment yapılabilir
- Contact emails webhook payload'ında gönderilirse, otomatik olarak enrichment yapılır

### Enrichment ve Segment İlişkisi

**Önemli Not:** Enrichment fields segment hesaplamasına dahil değildir. Segment sadece DNS/WHOIS sinyalleri ve provider bilgisine göre hesaplanır.

**Ancak:**
- Enrichment bilgileri lead değerlendirmesinde kullanılabilir
- Yüksek quality score'lu lead'ler daha değerli olabilir
- LinkedIn pattern tespit edildiyse, LinkedIn outreach yapılabilir

### Enrichment Kullanım Senaryoları

1. **Contact Email Toplama**: Satış ekibi contact email'lerini toplar ve sisteme ekler
2. **Quality Score**: Yüksek quality score'lu lead'lere öncelik verilir
3. **LinkedIn Outreach**: LinkedIn pattern tespit edildiyse, LinkedIn'de benzer pattern'lerle arama yapılır
4. **Lead Değerlendirme**: Daha fazla contact email'i olan lead'ler daha değerli olabilir

---

## 💡 İpuçları

### Skor Artırma Stratejileri

1. **SPF/DKIM/DMARC Kontrolü**
   - Bu sinyaller skoru önemli ölçüde artırır
   - Toplam +40 puan (SPF: 10, DKIM: 10, DMARC reject: 20)

2. **Provider Değişikliği**
   - Local → Cloud provider geçişi skoru artırır
   - Örnek: Local (0) → M365 (50) = +50 puan

3. **Düzenli Kontrol**
   - Skorlar zamanla değişebilir
   - Aylık kontrol önerilir

### Segment Değişikliği

**Cold → Existing:**
- Skor: 30 → 55
- Provider değişikliği veya sinyal eklenmesi

**Existing → Migration:**
- Skor: 60 → 75
- DMARC reject eklenmesi veya provider iyileştirmesi

**Skip → Cold:**
- Skor: 5 → 25
- SPF eklenmesi veya provider değişikliği

### Provider Değişikliği Takibi ⚡ YENİ

**Otomatik Tespit:**
- Domain scan edildiğinde, önceki provider ile karşılaştırılır
- Provider değişikliği tespit edilirse, `provider_change_history` tablosuna kaydedilir
- Örnek: Google → M365 geçişi otomatik olarak kaydedilir

**Kullanım Senaryoları:**
- **Migration fırsatı**: Provider değişikliği migration fırsatı gösterebilir
- **Müşteri takibi**: Müşterilerin provider değişikliklerini takip edebilirsiniz
- **Trend analizi**: Hangi provider'lara geçiş yapıldığını analiz edebilirsiniz

**SQL Sorgusu (Gelecekte API endpoint eklenecek):**
```sql
-- Son 30 günde provider değişikliği olan domain'ler
SELECT domain, previous_provider, new_provider, changed_at
FROM provider_change_history
WHERE changed_at >= NOW() - INTERVAL '30 days'
ORDER BY changed_at DESC;
```

---

## 📊 Özet Tablo

| Segment | Skor | Priority Score | Öncelik | İlk Aksiyon | Takip |
|---------|------|----------------|---------|-------------|-------|
| **Migration** | 80+ | 1 | 🟢 En Yüksek | 1 gün | Haftalık |
| **Migration** | 70-79 | 2 | 🟢 Yüksek | 1-2 gün | Haftalık |
| **Existing** | 70+ | 3 | 🟡 Orta-Yüksek | 1 hafta | Aylık |
| **Existing** | 50-69 | 4 | 🟡 Orta | 1-2 hafta | Aylık |
| **Cold** | 40+ | 5 | 🟠 Düşük | 1-2 ay | 2-3 ayda bir |
| **Diğerleri** | - | 6 | 🔴 Çok Düşük | 3-6 ay | 6 ayda bir |

---

## ❓ Sık Sorulan Sorular

### Q: Skor 70 ama segment Migration değil, neden?
**A:** Segment belirlenirken hem skor hem de provider kontrol edilir. Migration için skor 70+ VE provider M365/Google/Yandex/Zoho olmalı.

### Q: Skor 50 ama segment Existing değil, neden?
**A:** Existing için skor 50+ VE provider cloud/hosting provider olmalı. Local veya Unknown provider ise Existing olmaz.

### Q: Skor nasıl artırılır?
**A:** SPF, DKIM, DMARC sinyalleri eklenerek veya provider cloud provider'a geçirilerek skor artırılabilir.

### Q: Segment değişir mi?
**A:** Evet, skor değiştiğinde segment de değişir. Düzenli kontrol önerilir.

### Q: Provider değişikliği nasıl takip edilir?
**A:** Provider değişiklikleri otomatik olarak tespit edilir ve `provider_change_history` tablosuna kaydedilir. SQL sorgusu ile veya gelecekte eklenecek API endpoint ile sorgulanabilir.

---

**Son Güncelleme:** 2025-01-28

