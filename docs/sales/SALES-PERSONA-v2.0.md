# 🚀 Gibibyte Satışçı Personası v2.0: "Sistematik Avcı"

**Versiyon**: 2.0  
**Tarih**: 2025-01-28  
**Durum**: Güncellenmiş - Hunter-native, CRM-integrated, Multi-threaded  
**Önceki Versiyon**: v1.0 "Akıllı Avcı" (MVP seviyesi)

---

## 🎭 Temel Profil

**İsim**: Emir Kara  
**Rol**: B2B Cloud Solutions Sales Specialist  
**Kıdem**: 2-3 yıl (SAAS + Cloud satış tecrübesi)  
**Kullanılan Araçlar**: Dyn365Hunter, LinkedIn Sales Navigator, Power BI, Dynamics CRM  
**Odak Alanı**: Domain → IT Decision Maker → Migration fırsatı → Teklif → Kapanış  
**KPI**: M365 Migration, Security Upsell (Defender), Cloud App Consulting, yıllık MRR

**v2.0 Farkı**: Hunter'ın tüm özelliklerini kullanan, CRM pipeline'a entegre, multi-threaded, sistematik satış avcısı.

---

## 🧠 Zihniyeti (Mindset) - v2.0 Güncellemesi

### 1) "Kolay av yoktur; doğru sinyal vardır."
Domain datası onun için pusuladır. Hunter'daki skor + segment + **automation sinyalleri** = hangi firmaya ne zaman saldıracağını belirler.

**v2.0 Eklentisi**: Alert'ler, ReScan sonuçları, auto-tag'ler → otomatik fırsat tespiti.

### 2) "Bilgi güçtür, fakat doğru bilgi paradır."
MX + SPF + DKIM + DMARC bilgisi = altyapı zayıflığı  
Expire sorunu = IT tarafında ihmal → fırsat  
Local hosting + 0 sinyal = sıcak bir migration potansiyeli

**v2.0 Eklentisi**: Tenant size + Local provider detayı → daha doğru bütçe tahmini ve teklif hazırlama.

### 3) "Pahalı teknoloji yoktur; kötü anlatılmış teknoloji vardır."
Müşteride ihtiyacı trigger edecek doğru cümleyi bilir:
- "Mail deliverability %40 düşüyor farkında mısınız?"
- "DMARC none → phishing riskiniz yüksek, bunu hemen çözebiliriz."

**v2.0 Eklentisi**: Multi-threaded mesajlaşma (IT Direktörü, CFO, Genel Müdür, CTO) → her role özel value proposition.

### 4) "Zaman yönetimi > Efort."
Priority Score 1–2 ile başlar, Cold/Skip'e boş vakit ayırmaz.

**v2.0 Eklentisi**: Automation (Alerts, ReScan, Auto-tag'ler) → zaman tasarrufu, proaktif satış.

### 5) **YENİ**: "Sistematik avcı, avını takip eder."
Hunter'daki notes, tags, favorites, alerts → lead takibi ve pipeline yönetimi.

**v2.0 Eklentisi**: Hunter → Dynamics CRM pipeline mapping → net aksiyon planı.

---

## 🎯 Günlük Çalışma Akışı - v2.0 (Güncellenmiş)

### 1. Sabah (09:00 – 10:00): Hunter Taraması + Alert Kontrolü + Automation

#### Hunter Taraması
- Priority 1–2 lead'leri filtreler
- Migration segmenti ve 80+ skorları direkt işaretler
- Domain expire <60 gün olanları ayırır
- Provider change history'ye bakar (Google → M365 geçmiş mi?)

#### **YENİ v2.0**: Alert Kontrolü
- Alert'leri kontrol eder (`GET /alerts`)
  - `mx_changed` → Migration fırsatı! Hemen aksiyon.
  - `dmarc_added` → Güvenlik iyileştirmesi, upsell fırsatı!
  - `expire_soon` → Domain yenileme fırsatı!
  - `score_changed` → Lead durumu değişti, pipeline güncelle.

#### **YENİ v2.0**: Hunter-native Özellikler
- **Favorilere ekler** (`POST /leads/{domain}/favorite`)
  - Priority 1-2 lead'leri favorilere ekler
  - `GET /leads?favorite=true` ile takip eder
- **Auto-tag'leri kontrol eder**
  - `migration-ready` → Migration segment + score >= 70
  - `security-risk` → SPF/DKIM yok
  - `expire-soon` → Domain 30 gün içinde expire
  - `google-workspace` → Provider Google
  - `local-mx` → Provider Local
- **Tenant size'a göre filtreleme**
  - `large` → Yüksek bütçe, Enterprise teklif
  - `medium` → Orta bütçe, Business Standard teklif
  - `small` → Küçük bütçe, Business Basic teklif
- **Local provider detayına bakar**
  - TürkHost → "TürkHost'tan M365'e geçiş" stratejisi
  - Natro → "Natro'dan M365'e geçiş" stratejisi

#### Aksiyon
5 firmayı listesine alır → hemen outreach.

---

### 2. Öğle Öncesi (10:30 – 12:00): İlk Temas + Lead Enrichment + Multi-Threaded Outreach

#### **YENİ v2.0**: Lead Enrichment
- **Generic email üretme ve doğrulama** (`POST /email/generate-and-validate`)
  - Hunter'dan generic email'leri üretir (info, satis, iletisim, vb.)
  - Email doğrulama yapar (syntax + MX + opsiyonel SMTP)
  - Geçerli email'leri listeler
- **Contact enrichment** (`POST /leads/{domain}/enrich`)
  - Contact email'lerini ekler
  - Contact quality score'a bakar (hangi lead'lerde daha fazla contact var)
  - LinkedIn pattern tespiti (firstname.lastname, f.lastname, vb.)

#### **YENİ v2.0**: Multi-Threaded Outreach

Emir artık sadece IT Direktörü'ne değil, **birden fazla karar vericiye** ulaşır:

**🔥 IT Direktörü için kısa mesaj (Teknik)**
```
"MX kayıtlarınız Google'dan görünse de SPF/DKIM eksik. Bunu iyileştirmek email deliverability'nizi %25 artırır. 5 dakikada ücretsiz check yapayım ister misiniz?"
```

**💰 CFO için kısa mesaj (Finansal)**
```
"Mail deliverability %40 düşüyor, müşteri kaybı riski var. M365 migration ile bu riski ortadan kaldırabiliriz. ROI hesaplaması hazır, 15 dakikalık görüşme yapabilir miyiz?"
```

**🎯 Genel Müdür için kısa mesaj (Stratejik)**
```
"Şirket mail altyapınızda güvenlik açığı tespit ettik (DMARC none → phishing riski). İsterseniz raporlayıp öneri çıkarayım. 10 dakikalık görüşme yeterli."
```

**🛠️ CTO için kısa mesaj (Teknik + Stratejik)**
```
"DMARC none → phishing riskiniz yüksek. M365 + Defender ile bunu hemen çözebiliriz. Migration planı hazır, 15 dakikalık teknik görüşme yapabilir miyiz?"
```

#### **YENİ v2.0**: Champion Building
- IT ekibinden, güvenlik ekibinden, sistem yöneticisinden contact bulur
- Champion'a özel mesaj: "Sizin gibi teknik ekibin görüşü önemli, migration planı hazırlayalım"
- Hunter'a not ekler: "IT ekibinden Ahmet Bey champion, migration planı hazırlanıyor"
- Tag ekler: `champion-found`, `technical-champion`, `migration-champion`

---

### 3. Öğleden Sonra (13:00 – 16:00): Lead Qualification / Demo + Hunter Notları

#### Demo Süreci
- 15 dakikalık hızlı Zoom
- Hunter ekran görüntüsü ile risk ve fırsat anlatımı
- **YENİ v2.0**: Tenant size'a göre teklif hazırlar
  - Small (1-50 kullanıcı) → Business Basic €5/kullanıcı/ay
  - Medium (50-500 kullanıcı) → Business Standard €10/kullanıcı/ay
  - Large (500+ kullanıcı) → Enterprise €20/kullanıcı/ay + Defender + Consulting
- **YENİ v2.0**: Local provider detayına göre migration stratejisi belirler
  - TürkHost → "TürkHost'tan M365'e geçiş yapıyoruz, sorunsuz migration garantisi"
  - Natro → "Natro'dan M365'e geçiş yapıyoruz, sorunsuz migration garantisi"

#### **YENİ v2.0**: Hunter Notları ve Tag'ler
- **Görüşme sonrası Hunter'a not ekler** (`POST /leads/{domain}/notes`)
  - "IT Direktörü ile görüşüldü, migration planı hazırlanıyor"
  - "CFO ile görüşüldü, bütçe onayı bekleniyor"
  - "Demo yapıldı, teklif hazırlanıyor"
- **Tag ekler** (`POST /leads/{domain}/tags`)
  - `demo-scheduled` → Demo planlandı
  - `migration-ready` → Migration'a hazır
  - `high-priority` → Yüksek öncelik
  - `upsell-opportunity` → Upsell fırsatı
  - `existing-customer` → Mevcut müşteri
- **PDF summary oluşturur** (`GET /leads/{domain}/summary.pdf`)
  - Satış sunumu için hazır PDF raporu
  - Provider bilgisi, SPF/DKIM/DMARC durumu, skorlar, riskler

---

### 4. Gün Sonu (16:00 – 17:00): CRM Güncelleme & Follow-Up + ReScan Pipeline

#### **YENİ v2.0**: Hunter → Dynamics CRM Entegrasyonu
- **Hunter'dan export alır** (`GET /leads/export?format=csv`)
  - Filtrelenmiş lead'leri CSV/Excel olarak export eder
  - Dynamics CRM'e import eder (webhook veya manuel)
- **Hunter'daki notes/tags → Dynamics CRM'deki notes/tags ile senkronize eder**
  - Hunter notes → Dynamics CRM notes
  - Hunter tags → Dynamics CRM tags
- **Alert konfigürasyonu yapar** (`POST /alerts/config`)
  - Webhook → Dynamics CRM'e alert gönderir
  - MX değişikliği → Dynamics CRM'de lead güncelle
  - DMARC eklendi → Dynamics CRM'de upsell fırsatı oluştur

#### **YENİ v2.0**: CRM Pipeline Mapping

Hunter Priority Score → Dynamics CRM Stage Mapping:

| Hunter Priority | Segment + Skor | Dynamics CRM Stage | Aksiyon Zamanı |
|----------------|----------------|-------------------|----------------|
| **1** 🔥 | Migration + 80+ | "Qualified Lead" | Hemen (1 gün) |
| **2** ⭐ | Migration + 70-79 | "Qualified Lead" | Hemen (1-2 gün) |
| **3** 🟡 | Migration + 50-69<br>Existing + 70+ | "Nurturing" | 1 hafta içinde |
| **4** 🟠 | Migration + 0-49<br>Existing + 50-69 | "Cold Lead" | 1-2 hafta |
| **5** ⚪ | Existing + 30-49<br>Cold + 40+ | "Long-term" | 1-2 ay |
| **6** ⚫ | Existing + 0-29<br>Cold + 20-39 | "Long-term" | 2-3 ay |
| **7** 🔴 | Cold + 0-19<br>Skip | "Archive" | 3-6 ay |

#### **YENİ v2.0**: ReScan Pipeline
- **Favorilere eklediği lead'leri rescan eder** (`POST /scan/{domain}/rescan`)
  - Değişiklikleri tespit eder (MX, DMARC, skor, expiry)
  - Alert oluşturur (değişiklik varsa)
- **Toplu rescan** (`POST /scan/bulk/rescan`)
  - Priority 1-2 lead'leri toplu rescan eder
  - Değişiklikleri tespit eder
- **Alert konfigürasyonu**
  - Daily rescan scheduler ile otomatik rescan
  - Değişiklik varsa alert gönder

#### Follow-Up Pipeline
- 7 günlük follow-up pipeline oluşturur
- Hunter'daki notes/tags ile takip eder
- Dynamics CRM'deki stage'lere göre aksiyon alır

---

## 🔥 Strengths (Güçlü Yanlar) - v2.0 Güncellemesi

### 1) Teknik veriyi satış diline çevirebilmesi
Hunter skorlarını "müşterinin anlayacağı dile" çevirir:
- "Mail güvenliği zayıf"
- "Spam'e düşme riskiniz yüksek"
- "Şirketinizin domaini expire oluyor—çok kritik."

**v2.0 Eklentisi**: Tenant size + Local provider detayı → daha spesifik value proposition.

### 2) Zamanı çok verimli kullanır
Migration lead'lerine fokus; düşük skorlarla uğraşmaz.

**v2.0 Eklentisi**: Automation (Alerts, ReScan, Auto-tag'ler) → zaman tasarrufu, proaktif satış.

### 3) M365 ekosistemini bilir
Business Basic / Standard farkı  
Shared mailbox  
Tenant structure  
Defender paketleri  
365 → Power Automate → Dynamics bağlamı

**v2.0 Eklentisi**: Tenant size'a göre doğru lisans önerisi, value-based pricing.

### 4) Sahada çalışan bir satışçı gibi düşünür
OSB datası  
LinkedIn pattern search  
Local hosting zafiyetlerini okumayı bilir

**v2.0 Eklentisi**: Multi-threaded outreach, champion building, competition awareness.

### 5) **YENİ**: Hunter-native satışçı
Hunter'ın tüm özelliklerini kullanır:
- Notes, Tags, Favorites
- Alerts, ReScan
- Enrichment
- Tenant Size, Local Provider
- PDF Summary

**v2.0 Eklentisi**: Hunter → Dynamics CRM pipeline mapping → sistematik satış.

---

## 🧩 Sales Hunter Persona Motivasyon Haritası - v2.0

| Motivasyon | Açıklama | v2.0 Eklentisi |
|------------|----------|----------------|
| Başarı (kapanış) | Migration + Security + Consulting MRR | Tenant size'a göre doğru teklif → daha yüksek kapanış oranı |
| Hız | 5 dakikada lead analizi + hızlı outreach | Automation (Alerts, ReScan) → proaktif fırsat tespiti |
| Basitlik | "Kahvelik" analiz → gereksiz karmaşıklık yok | Hunter-native özellikler → tek platform, basit workflow |
| Teknik güvenirlik | Hunter verisi ile konuşmak onu güçlü kılar | Tenant size + Local provider → daha güvenilir veri |
| Kişisel gelişim | M365 + Cloud + Security bilgisini artırmak | Multi-threaded outreach → daha geniş network |

---

## 📦 Hunter İçin Kullanıcı Rehberi (Satışçıya göre) - v2.0

### Hunter'ın Emir için anlamı - v2.0

**v1.0**: Radar, Tehdit analizi, Fırsat bulucu, Prioritization engine

**v2.0**: Radar, Tehdit analizi, Fırsat bulucu, Prioritization engine, **Automation hub**, **CRM bridge**, **Enrichment engine**

### Emir Hunter'da neye bakar? - v2.0

**v1.0**: Segment, Score (0–100), Priority (1–7)

**v2.0**: 
- Segment, Score (0–100), Priority (1–7)
- **Tenant Size** (small/medium/large)
- **Local Provider** (TürkHost, Natro, vb.)
- **Auto-tag'ler** (migration-ready, security-risk, expire-soon)
- **Alerts** (mx_changed, dmarc_added, expire_soon, score_changed)
- **Contact Quality Score** (enrichment sonrası)
- **DMARC Coverage** (pct parametresi)

### Onun için güzel lead tipi - v2.0

**v1.0**:
- Migration
- 70–100 skor
- MX Google / Hosting
- SPF var, DKIM eksik
- DMARC none
- Expire <90 gün

**v2.0**:
- Migration
- 70–100 skor
- MX Google / Hosting
- SPF var, DKIM eksik
- DMARC none (veya coverage düşük)
- Expire <90 gün
- **Tenant Size: Large** (yüksek bütçe)
- **Local Provider: TürkHost/Natro** (migration stratejisi net)
- **Auto-tag: migration-ready** (sistem onayı)
- **Alert: mx_changed** (recent provider change)

Bu firma = **"Acil fırsat + Yüksek bütçe + Net strateji!"**

---

## 🧨 Satışçı Emir'in Rolü Hunter Sürecine Nasıl Oturuyor? - v2.0

### v1.0 Akışı
1. Domain → Fırsat
2. Fırsat → IT Karar Verici
3. Karar Verici → Demo
4. Demo → Migration + Security Bundle
5. Bundle → MRR

### v2.0 Akışı (Geliştirilmiş)

1. **Domain → Fırsat** (Hunter scan)
   - **YENİ**: Alert kontrolü (mx_changed, dmarc_added, expire_soon)
   - **YENİ**: Auto-tag kontrolü (migration-ready, security-risk)
   - **YENİ**: Tenant size + Local provider tespiti

2. **Fırsat → Enrichment** (Hunter enrichment)
   - **YENİ**: Generic email üretme ve doğrulama
   - **YENİ**: Contact enrichment (LinkedIn pattern)
   - **YENİ**: Contact quality score

3. **Enrichment → Multi-Threaded Outreach** (Hunter + LinkedIn)
   - **YENİ**: IT Direktörü, CFO, Genel Müdür, CTO
   - **YENİ**: Champion building
   - **YENİ**: Role-based mesajlaşma

4. **Outreach → Demo** (Hunter notes/tags)
   - **YENİ**: Hunter'a not ekler
   - **YENİ**: Tag ekler (demo-scheduled, migration-ready)
   - **YENİ**: PDF summary oluşturur

5. **Demo → Teklif** (Hunter + Pricing)
   - **YENI**: Tenant size'a göre pricing
   - **YENİ**: Local provider'a göre migration stratejisi
   - **YENİ**: Value-based pricing (ROI hesaplama)

6. **Teklif → Kapanış** (Hunter + CRM)
   - **YENİ**: Hunter → Dynamics CRM pipeline mapping
   - **YENİ**: Hunter notes/tags → CRM notes/tags senkronizasyonu
   - **YENİ**: Alert konfigürasyonu (webhook → CRM)

7. **Kapanış → Upsell** (Hunter + ReScan)
   - **YENİ**: ReScan ile domain değişikliklerini takip
   - **YENİ**: Alert ile upsell fırsatları (DMARC eklendi, MX değişti)
   - **YENİ**: Existing customer upsell (Defender, Power Automate, Dynamics)

---

## 🎯 Rejection Handling Stratejisi - YENİ v2.0

### 1. "Şu An İlgilenmiyoruz"

**Emir'in Stratejisi:**
1. **Hunter'a not ekler** (`POST /leads/{domain}/notes`)
   ```
   "Müşteri şu an ilgilenmiyor, 6 ay sonra tekrar denenecek"
   ```
2. **Tag ekler** (`POST /leads/{domain}/tags`)
   - `not-interested`
   - `follow-up-6months`
3. **Alert konfigürasyonu** (`POST /alerts/config`)
   - 6 ay sonra rescan yap
   - MX değişikliği varsa alert gönder
   - DMARC eklendiğinde alert gönder
4. **Follow-up stratejisi**
   - 6 ay sonra tekrar outreach
   - Domain değişikliği varsa hemen aksiyon
   - Dynamics CRM'de "Long-term" stage'e taşı

### 2. "Zaten Başka Bir Çözüm Kullanıyoruz"

**Emir'in Stratejisi:**
1. **Upsell fırsatı**
   - Defender paketleri
   - Power Automate
   - Dynamics 365
   - Consulting services
2. **Hunter'a not ekler**
   ```
   "Müşteri zaten M365 kullanıyor, Defender upsell fırsatı"
   ```
3. **Tag ekler**
   - `existing-customer`
   - `upsell-opportunity`
   - `defender-ready`
4. **Hunter segment kontrolü**
   - Existing segment → Upsell fırsatı
   - ReScan ile domain değişikliklerini takip
   - Alert ile upsell fırsatları (DMARC eklendi, MX değişti)

### 3. "Bütçe Yok"

**Emir'in Stratejisi:**
1. **Alternatif çözümler**
   - Business Basic (daha ucuz)
   - Aşamalı migration (önce 10 kullanıcı, sonra genişlet)
   - Free trial (3 ay)
2. **Hunter'a not ekler**
   ```
   "Bütçe yok, 3 ay sonra tekrar denenecek"
   ```
3. **Tag ekler**
   - `budget-constraint`
   - `follow-up-3months`
4. **Alert konfigürasyonu**
   - 3 ay sonra rescan
   - Tenant size değişikliği varsa alert
   - Dynamics CRM'de "Long-term" stage'e taşı

---

## 🎯 Competition Awareness Stratejisi - YENİ v2.0

### 1. Google Workspace → M365 Migration

**Emir'in Stratejisi:**
1. **Migration fırsatı**
   - Google Workspace → M365 migration
   - "M365 daha iyi Office entegrasyonu, Dynamics 365 ile uyumlu"
2. **Hunter'a not ekler**
   ```
   "Google Workspace kullanıyor, M365 migration fırsatı"
   ```
3. **Tag ekler**
   - `google-workspace`
   - `migration-opportunity`
   - `m365-migration`
4. **Hunter segment kontrolü**
   - Provider: Google → Migration segment
   - ReScan ile MX değişikliklerini takip
   - Alert ile migration fırsatları (MX değişti)

### 2. Local Provider → M365 Migration

**Emir'in Stratejisi:**
1. **Migration fırsatı**
   - Local provider (TürkHost, Natro) → M365 migration
   - "M365 daha güvenli, daha profesyonel, daha ölçeklenebilir"
2. **Hunter'dan local provider detayını kullanır**
   - TürkHost → "TürkHost'tan M365'e geçiş yapıyoruz"
   - Natro → "Natro'dan M365'e geçiş yapıyoruz"
3. **Hunter'a not ekler**
   ```
   "TürkHost kullanıyor, M365 migration fırsatı"
   ```
4. **Tag ekler**
   - `local-mx`
   - `migration-opportunity`
   - `turkhost-migration` (veya `natro-migration`)
5. **Hunter segment kontrolü**
   - Provider: Local → Migration segment
   - Local provider detayı → Migration stratejisi
   - ReScan ile MX değişikliklerini takip

---

## 💰 Pricing Strategy - YENİ v2.0

### 1. Tenant Size'a Göre Pricing

**Emir'in Stratejisi:**

#### Small (1-50 kullanıcı)
- **Lisans**: Business Basic: €5/kullanıcı/ay
- **Migration**: €500 (tek seferlik)
- **Toplam**: €5,500/yıl (50 kullanıcı)
- **Hunter'dan**: Tenant size = `small` → Business Basic teklif

#### Medium (50-500 kullanıcı)
- **Lisans**: Business Standard: €10/kullanıcı/ay
- **Migration**: €2,000 (tek seferlik)
- **Defender**: €5/kullanıcı/ay (opsiyonel)
- **Toplam**: €60,000/yıl (500 kullanıcı, Defender ile)
- **Hunter'dan**: Tenant size = `medium` → Business Standard teklif

#### Large (500+ kullanıcı)
- **Lisans**: Enterprise: €20/kullanıcı/ay
- **Migration**: €10,000 (tek seferlik)
- **Defender**: €10/kullanıcı/ay (opsiyonel)
- **Consulting**: €50,000 (tek seferlik)
- **Toplam**: €1,200,000/yıl (500 kullanıcı, Defender + Consulting ile)
- **Hunter'dan**: Tenant size = `large` → Enterprise teklif

### 2. Value-Based Pricing

**Emir'in Stratejisi:**

#### ROI Hesaplama
- **Mail deliverability %40 artış** → Müşteri kaybı önleme
- **DMARC reject** → Phishing saldırısı önleme
- **M365 migration** → IT maliyeti düşüşü

#### Hunter'dan Risk Sinyallerini Kullanır
- **SPF yok** → Phishing riski
- **DMARC none** → Email spoofing riski
- **Domain expire soon** → Domain kaybı riski

#### Value Proposition
- "Mail deliverability %40 artış → €X müşteri kaybı önleme"
- "DMARC reject → €Y phishing saldırısı önleme"
- "M365 migration → €Z IT maliyeti düşüşü"

---

## 🥇 Persona Özet Kartı - v2.0

**Emir Kara – "Gibibyte Sistematik Avcısı" v2.0**

### v1.0 Özellikleri (Korundu)
- ✅ Hunter'dan çıkan sinyallere göre hareket eder
- ✅ Priority Score 1–2 lead'leri anında arar
- ✅ Teknik veriyi sade satış diline çevirir
- ✅ Azure/M365/Dynamics ekosistemini bilir
- ✅ Lokal hosting zafiyetlerini migration fırsatına çevirir
- ✅ OSB + LinkedIn + domain datasını harmanlar
- ✅ 5 dakikada analiz → 15 dakikada toplantı → aynı gün teklif

### v2.0 Yeni Özellikleri
- ✅ **Hunter-native**: Notes, Tags, Favorites, Alerts, ReScan, Enrichment kullanır
- ✅ **Tenant Size + Local Provider**: Daha doğru bütçe tahmini ve teklif hazırlama
- ✅ **Multi-threaded outreach**: IT Direktörü, CFO, Genel Müdür, CTO'ya ulaşır
- ✅ **Champion building**: İçerideki destekçiyi bulur ve kullanır
- ✅ **CRM pipeline mapping**: Hunter Priority Score → Dynamics CRM Stage
- ✅ **Rejection handling**: 3 rejection senaryosu, follow-up stratejisi
- ✅ **Competition awareness**: Google Workspace, Local Provider migration stratejisi
- ✅ **Pricing strategy**: Tenant size'a göre pricing, value-based pricing
- ✅ **Automation**: Alerts, ReScan, Auto-tag'ler ile proaktif satış

---

## 📊 v1.0 vs v2.0 Karşılaştırması

| Özellik | v1.0 "Akıllı Avcı" | v2.0 "Sistematik Avcı" |
|---------|-------------------|------------------------|
| **Hunter Özellikleri** | Priority, Segment, Skor | + Notes, Tags, Favorites, Alerts, ReScan, Enrichment, Tenant Size, Local Provider |
| **CRM Entegrasyonu** | "Dynamics CRM'e kaydeder" | + Hunter → Dynamics CRM veri akışı, pipeline mapping |
| **Rejection Handling** | Yok | + 3 rejection senaryosu, follow-up stratejisi |
| **Competition Awareness** | Yok | + Google Workspace, Local Provider migration stratejisi |
| **Multi-Threaded Sales** | Sadece IT Direktörü | + CFO, Genel Müdür, CTO, Champion building |
| **Pricing Strategy** | "Basit anlatılır" | + Tenant size'a göre pricing, value-based pricing |
| **Automation** | Yok | + Alerts, ReScan, Auto-tag'ler |
| **Enrichment** | Yok | + Generic email, Contact enrichment, LinkedIn pattern |

---

## 🎯 Sonuç

**v1.0 "Akıllı Avcı"**: MVP seviyesinde, Hunter'ın temel özelliklerini kullanan satışçı.

**v2.0 "Sistematik Avcı"**: Hunter-native, CRM-integrated, multi-threaded, automation-driven, sistematik satış avcısı.

**v2.0'un Farkı:**
- Hunter'ın tüm özelliklerini kullanır
- CRM pipeline'a entegre çalışır
- Multi-threaded outreach yapar
- Automation ile proaktif satış yapar
- Rejection handling yapar
- Competition awareness'a sahiptir
- Pricing strategy'si vardır

**v2.0'un Hedefi:**
Microsoft CSP partner için ideal satışçı profili → Yüksek kapanış oranı, düşük deal kaybı, sistematik satış süreci.

---

**Son Güncelleme**: 2025-01-28  
**Versiyon**: 2.0  
**Durum**: Güncellenmiş - Hunter-native, CRM-integrated, Multi-threaded  
**Entegrasyon**: ✅ SALES-GUIDE.md'ye entegre edildi (Persona v2.0 özeti eklendi), ✅ SALES-TRAINING.md hazır

