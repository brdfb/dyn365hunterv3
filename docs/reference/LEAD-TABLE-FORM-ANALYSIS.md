# 🧾 Lead Table & Form Analiz Dokümanı (Hunter CORE)

**Version:** v1.0  
**Last Updated:** 2025-01-30  
**App:** Sales Hub (Dynamics 365 Sales)  
**Primary Form:** Information (Main Form)

---

## 📋 İçindekiler

1. [Genel Bilgi](#1-genel-bilgi)
2. [Header Alanları](#2-header-alanları-form-üst-şerit)
3. [Section: Business Card](#3-section-business-card)
4. [Section: Hunter Intelligence](#4-section-hunter-intelligence)
5. [Section: Partner Center](#5-section-partner-center)
6. [Section: AI & Sync Analytics](#6-section-ai--sync-analytics)
7. [Section: Contact Details](#7-section-contact-details)
8. [Section: Address](#8-section-address)
9. [Section: Description](#9-section-description)
10. [Tab: Advanced Debug (Technical Only)](#10-tab-advanced-debug-technical-only)
11. [My Open Leads View](#11-my-open-leads-view-şu-an-gördüğün-grid)
12. [Kullanım Notları (Design Decisions)](#12-kullanım-notları-design-decisions)
13. [Kullanım Senaryoları](#13-bu-dokümanı-nasıl-kullanırsın)

---

## 1. Genel Bilgi

### Tablo Bilgileri
- **Tablo:** `Lead`
- **Kullanılan App:** Sales Hub (Dynamics 365 Sales)
- **Primary Form:** Information (Main Form Type)

### Form Yapısı
- **Ana Form:** Information (Main)
- **Ek Formlar (aktif ama ikincil):**
  - Lead Insights
  - Sales Insights
  - In Context Form
  - Lead (klasik form)

> **Not:** Bu doküman **Information form** üzerindeki yerleşime göre yazıldı.

---

## 2. Header Alanları (Form üst şerit)

Bu alanlar BPF (Business Process Flow) & form header üzerinde görüntülenir.

| Alan (Display)            | Tip                | Kaynak    | Not                                               |
| ------------------------- | ------------------ | --------- | ------------------------------------------------- |
| **Status Reason**         | Option Set         | D365 core | New / Qualified / Disqualified vb.                |
| **Lead Source**           | Option Set         | D365 core | Web, Partner, Phone call vs.                      |
| **Rating**                | Option Set         | D365 core | Warm / Hot / Cold (şu an **Warm** görünüyor)     |
| **Owner**                 | Lookup (User/Team) | D365 core | Lead sahibi (Furağ Bered Günültaşı vb.)           |
| **Business Process Flow** | BPF                | D365 core | **Qualify → Develop → Propose → Close** aşamaları |

---

## 3. Section: Business Card

Formdaki ilk ana blok. Şirket/account seviyesi bilgileri içerir.

| Alan               | Tip (tahmin / bilinen)      | Zorunlu  | Kaynak              | Amaç                                            |
| ------------------ | --------------------------- | -------- | ------------------- | ----------------------------------------------- |
| **Topic**          | Single Line of Text         | **Evet** | D365 core           | Lead başlığı (ör: "M365 migration – XYZ")       |
| **Company Name**   | Single Line of Text         | **Evet** | D365 core           | Firma adı (grid'de "Name" olarak da kullanılır) |
| **Company email**  | Single Line of Text / Email | Hayır    | **Custom (Hunter)** | Şirketin genel e-postası (info@, sales@ vb.)    |
| **Website**        | Single Line of Text / URL   | Hayır    | D365 core           | Firmanın web adresi                             |
| **Business Phone** | Single Line of Text / Phone | Hayır    | D365 core           | Ana firma telefonu                              |

> **Not:** Personel contact bilgilerini aşağıdaki **Contact Details** section'ında tutuyoruz; Business Card daha "account/company" katmanı gibi.

---

## 4. Section: Hunter Intelligence

Hunter'ın scoring & enrichment çıktıları. Lead kalitesi ve segmentasyon için kullanılır.

| Alan                         | Tip                    | Zorunlu | Kaynak | Amaç                                                         |
| ---------------------------- | ---------------------- | ------- | ------ | ------------------------------------------------------------ |
| **Hunter Final Score**       | Number (Whole/Decimal) | Hayır   | Hunter | 0–100 arası final skor. UI'de lead kalitesi için kullanılır. |
| **Hunter Segment**           | Option Set / Text      | Hayır   | Hunter | SMB / Mid / Enterprise vb. segment etiketi.                  |
| **Hunter Confidence**        | Decimal                | Hayır   | Hunter | Skor güven seviyesi (ör: 3.00 gibi decimal görünüyor).       |
| **Hunter Source**            | Option Set / Text      | Hayır   | Hunter | Skorun kaynağı (ör: Hunter, Manual, Import vs).              |
| **Hunter Last Sync Time**    | DateTime               | Hayır   | Hunter | Bu lead için Hunter ile en son ne zaman sync edildi.         |
| **Hunter Intelligence JSON** | Multiple Lines of Text | Hayır   | Hunter | Tam ham JSON payload (debug / data science için).            |

> Buradaki alanlar "Hunter Intelligence" section'ı dışında başka yerde tekrar edilmiyor; bu segment tamamen **scoring & enrichment dashboard** gibi.

---

## 5. Section: Partner Center

Sadece Partner Center'dan gelen referral'lar için dolu olacak alanlar.

| Alan                       | Tip                           | Zorunlu | Kaynak              | Amaç                                                           |
| -------------------------- | ----------------------------- | ------- | ------------------- | -------------------------------------------------------------- |
| **Hunter Provider**        | Option Set / Text             | Hayır   | Hunter PC Connector | Hangi provider'dan geldi (Microsoft Partner Center vb.).       |
| **Hunter Referral ID**     | Single Line of Text           | Hayır   | Partner Center      | PC referral kaydının ID'si.                                    |
| **Hunter Referral Type**   | Option Set / Text             | Hayır   | Partner Center      | Co-sell, marketplace, solution workspace vb. tip.              |
| **Hunter M365 Fit Score**  | Number                        | Hayır   | Hunter              | M365 uyumluluk skorun (fit).                                   |
| **Hunter M365 Match Tags** | Multiple Lines of Text / Text | Hayır   | Hunter              | M365 workload eşleşme tagleri (Exchange, SharePoint, Teams… ). |

> Buradaki alanlar sadece **Partner Center Phase** ile gelen datayı izlemek için; manuel lead girişlerinde boş kalması normal.

---

## 6. Section: AI & Sync Analytics

Bu blok "Hunter ↔ D365 ↔ D365 Sales sync pipeline" sağlık göstergeleri için.

| Alan                          | Tip                    | Kaynak           | Amaç                                                                                                    |
| ----------------------------- | ---------------------- | ---------------- | ------------------------------------------------------------------------------------------------------- |
| **D365 Lead ID**              | Single Line of Text    | Hunter connector | Hunter tarafında D365 lead referansını taşır.                                                           |
| **Hunter Last Sync Time**     | DateTime               | Hunter           | Hunter ile en son sync timestamp'i (tekrar) – bu section'da özellikle sync analizi için yukarı çekildi. |
| **Hunter Sync Attempt Count** | Whole Number           | Hunter           | Kaç defa sync denemesi yapıldığını tutar.                                                               |
| **Hunter Processing Status**  | Option Set / Text      | Hunter           | Pipeline durumu (Idle, Processing, Completed, Failed…).                                                 |
| **Hunter Push Status**        | Option Set / Text      | Hunter           | Hunter'dan D365'e push state (synced, not synced, error vs).                                            |
| **Hunter Sync Error Message** | Multiple Lines of Text | Hunter           | Son hata mesajı (varsa).                                                                                |

> Bu section tamamen **operasyon & debug** amaçlı. Müşteri yüzü değil, "integration health" dashboard'u gibi düşün.

---

## 7. Section: Contact Details

Lead üzerindeki **kişisel** kontakt bilgisi (Decision Maker / ana kişi).

| Alan             | Tip                         | Zorunlu | Kaynak    | Açıklama                                       |
| ---------------- | --------------------------- | ------- | --------- | ---------------------------------------------- |
| **First Name**   | Single Line of Text         | Evet    | D365 core | Kişinin adı                                    |
| **Last Name**    | Single Line of Text         | Evet    | D365 core | Soyadı                                         |
| **Job Title**    | Single Line of Text         | Hayır   | D365 core | Ünvan (IT Manager, CEO vb)                     |
| **Email**        | Single Line of Text / Email | Hayır   | D365 core | Kişinin e-postası                              |
| **Mobile Phone** | Single Line of Text / Phone | Hayır   | D365 core | Mobil telefon (2025 reality: primary kanal 🙂) |

---

## 8. Section: Address

Klasik D365 adres bloğu; hem mailing hem saha işleri için.

| Alan                | Tip  | Kaynak    |
| ------------------- | ---- | --------- |
| **Street 1**        | Text | D365 core |
| **Street 2**        | Text | D365 core |
| **Street 3**        | Text | D365 core |
| **City**            | Text | D365 core |
| **State/Province**  | Text | D365 core |
| **ZIP/Postal Code** | Text | D365 core |
| **Country/Region**  | Text | D365 core |

---

## 9. Section: Description

| Alan            | Tip                    | Amaç                                                                                                    |
| --------------- | ---------------------- | ------------------------------------------------------------------------------------------------------- |
| **Description** | Multiple Lines of Text | Özet not, hikâye, deal context. Hunter / PC dışında manuel girilen tüm hikâyeyi buraya yazmak mantıklı. |

---

## 10. Tab: Advanced Debug (Technical Only)

Ayrı bir tab (Advanced Debug). Tamamen **sadece teknik ekip** için; müşteri/operasyon normalde görmesin.

### Section: Advanced Debug (Technical Only)

| Alan                              | Tip            | Kaynak | Amaç                                                               |
| --------------------------------- | -------------- | ------ | ------------------------------------------------------------------ |
| **Hunter AutoScore Version**      | Text           | Hunter | Hangi scoring engine versiyonu kullanıldı (v1, v1.1, v2… ).        |
| **Hunter Domain**                 | Text           | Hunter | Analiz edilen domain (xyz.co, abc.com).                            |
| **Hunter Infrastructure Summary** | Multiple Lines | Hunter | Hunter'ın altyapı analizi (MX, SPF, DNS, cloud provider vb. özet). |
| **Hunter Is Re-Enriched**         | Boolean        | Hunter | Bu lead tekrar enrich edildi mi? (Evet/Hayır).                     |
| **Hunter ML Weight JSON**         | Multiple Lines | Hunter | ML ağırlıklarının ham JSON'ı (feature weights).                    |
| **Hunter Priority Score**         | Number         | Hunter | İç öncelik skoru (queue / job scheduling için kullanılabilir).     |
| **Hunter Tenant ID**              | Text           | Hunter | Tenant GUID / ID.                                                  |
| **Hunter Tenant Size**            | Option Set     | Hunter | Small (1–50), Mid, Large gibi tenant büyüklüğü.                    |

> Bu tab zaten **ayrı sekme** ve başlığında "Technical Only" yazıyor. Gerekirse security role ile sadece senin/ekibin göreceği şekilde sınırlarız.

---

## 11. My Open Leads View (şu an gördüğün grid)

Şu anda klasik "My Open Leads" view'unda gördüklerin:

| Kolon             | Kaynak                                                              |
| ----------------- | ------------------------------------------------------------------- |
| **Name**          | Company Name / Topic kombinasyonu (D365 default lead primary field) |
| **Topic**         | Lead.Topic                                                          |
| **Status Reason** | Lead.Status Reason                                                  |
| **Created On**    | Lead.Created On                                                     |

### Önerilen View'ler

İleride farklı bir view açıp Hunter alanlarını da ekleyebilirsin:

**Hunter Intelligence Leads View:**
- Hunter Final Score
- Hunter Segment
- Hunter M365 Fit Score
- Hunter Processing Status / Push Status

Bu view'u "Hunter Intelligence Leads" diye ayrı kaydedebiliriz.

---

## 12. Kullanım Notları (Design Decisions)

Kısa tasarım kararlarını da buraya düşüyorum ki ileride "niye böyle yapmıştık?" sorusunu açıp okuyalım:

### 1. Lead vs Opportunity
- Hunter & Partner Center dataları **Lead** seviyesinde toplanıyor.
- Lead qualified olduğunda Opportunity'ye akmasını istersen ayrı mapping yapacağız (şu an lead odaklı).

### 2. Company vs Contact Ayrımı
- Şirket bilgisi → **Business Card**
- Kişi bilgisi → **Contact Details**
- Böylece multi-contact senaryosunda ileride ayrı Contact entity ile ilişki kurmak daha temiz olacak.

### 3. Partner Center Alanları Optional
- Her lead Partner Center'dan gelmiyor, o yüzden PC alanları "boş kalması normal" olarak tasarlandı.
- Sadece geldiğinde dolu olduğunda pipeline bunu "PC-lead" olarak işaretleyebilecek.

### 4. Advanced Debug Tab'ı
- Normal kullanıcılar için **gereksiz ve kafa karıştırıcı**, tamamen ops/engineering için.
- İleride Security Role ile sadece belirli role'lere açacağız.

### 5. Logical Names
> **Not:** Logical name'leri görmedik; o yüzden onları opsiyonel bıraktık. İstersen bir ara Power Apps'ten tek tek bakıp doldururuz.

---

## 13. Bu Dokümanı Nasıl Kullanırsın?

### Yeni Field Eklerken
1. Önce buraya bir satır ekle → sonra Power Apps'te column oluştur.
2. Logical name'i buraya ekle.

### Integration Yaparken
- Hunter – D365 mapping'ini bu tablo üzerinden kontrol et.
- Field mapping'leri bu dokümandan referans al.

### Developer'a İş Anlatırken
- "Şu dokümandaki `Hunter Processing Status` alanına şunu yazacaksın" diye net referans ver.
- Field tipi ve zorunluluk bilgilerini buradan paylaş.

### Form Tasarımı
- Section yapısını bu dokümandan referans al.
- View tasarımı için önerilen view'leri kullan.

---

## 📝 Notlar

- Bu doküman **v1.0** versiyonudur.
- İleride genişletilebilir (logical names, form varyantları, view önerileri).
- Değişiklikler oldukça bu doküman güncellenecektir.

---

## 🔄 Güncelleme Geçmişi

- **2025-01-30:** v1.0 - İlk versiyon oluşturuldu

