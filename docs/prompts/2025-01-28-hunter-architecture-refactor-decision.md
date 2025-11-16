# Hunter Architecture Refactor Decision

**Date**: 2025-01-28  
**Type**: Architectural Decision  
**Status**: Approved  
**Priority**: P0 (Critical)

---

## Decision Summary

**Hunter = İnce, kaslı, pahalı sinyalleri üreten motor.**

**Dynamics + Power Automate + Power BI = Satışçının evi.**

Hunter'ın rolü netleştirildi: Sadece **CRM'in asla yapamayacağı işleri** yapmalı.

---

## Core Principle

> **"Dışarıya çıkıp veri topluyorsa veya ağır analizse → Hunter."**

> **"Zaten Dataverse + Dynamics ile yapılabiliyorsa → Hunter'a koyma."**

---

## Hunter'ın "Kutsal Alanı" (Sadece Bunları Yapsın)

1. **Ağır / teknik / CRM'in yapamayacağı analizler**
   - DNS (MX/SPF/DKIM/DMARC)
   - WHOIS (expiry, registrar, nameserver)
   - Provider tespiti (M365 / Google / Hosting / Local / Hybrid)
   - IT olgunluk skoru
   - Migration / Existing / Skip segmenti
   - Risk flag'ler (DKIM yok, DMARC none, expiry yaklaşıyor vs.)

2. **Zekâ gerektiren özetler**
   - 1 cümlelik satış özeti
   - Call script / discovery soru seti
   - Basic–Pro–Enterprise teklif önerisi
   - Fırsat puanı (opportunity potential / urgency)

3. **Dış dünya ile konuşma**
   - DNS, WHOIS, SMTP check gibi "çıkışlı" işler
   - Bunlar CRM tarafında yapılamaz, burası Hunter'ın ekmeği.

---

## Hunter'ın YAPMAMASI Gerekenler

* Kullanıcı / satışçı yönetimi
* Görev, aktivite, telefon kaydı
* Pipeline, opportunity stage, revenue tahmini
* Teklif dokümanı üretip saklama
* Dashboard / raporlama
* Bildirim, reminder, görev atama
* "UI içinde lead listesi yönetme" tarzı CRM işleri

Bu alanlar **Sales Hub + Power Automate + Power BI**'ın işi.

---

## Feature Filter: Her Yeni Özellik İçin 5 Soru

1. **Bu iş DNS/WHOIS/dış veri gerektiriyor mu?**
   - Evet → Hunter adayı
   - Hayır → Muhtemelen CRM tarafı

2. **Bu iş, aynı şekilde Power Automate + custom fields ile yapılabilir mi?**
   - Evet → CRM'de yap, Hunter'a dokunma.

3. **Bu iş Hunter olmadan da mantıklı mı?**
   - Evet → CRM modudur, Hunter'a girmesin.

4. **Bu iş Hunter'a CPU / network açısından pahalı yük bindiriyor mu?**
   - "Her form açılışında tekrar scan" gibi şeyler → NO.
   - "Gece 1 defa domain'i re-scan" → OK.

5. **Bu işi Hunter yerine sadece 1–2 Power Automate flow + field ile çözemiyor muyum?**
   - Çözebiliyorsan, Hunter'a eklemek = gereksiz karmaşa.

**2+ kere "CRM'de de olur" diyorsan o feature Hunter'dan at.**

---

## Teknik Strateji

1. **Stateless API yaklaşımı**
   - Hunter: `/analyze-domain` gibi fonksiyonel endpoint'ler
   - State = PostgreSQL
   - Hiç kullanıcı yönetme, seans, rol vb. bulaştırma

2. **Az çağrı, çok iş**
   - Dynamics → Power Automate → Hunter'a 1 call
   - Hunter tek seferde bütün skorları, özetleri, flag'leri döner
   - "Chatty API" yok, "tek endpoint = tam analiz"

3. **Scan frekansını kontrol et**
   - **UI açıldıkça scan etme** → server yanar
   - Gece / haftalık scheduled job ile re-scan
   - Dynamics lead formu sadece hazır datayı okur

4. **Config dosya tabanlı kalsın**
   - `providers.json`, `rules.json`, `script_templates.json`
   - Kural: "Yeni özellik için kod yazmadan önce, config ile çözülebiliyor mu?"

---

## Pratik Bölüşüm Örneği

### Örnek: "Domain expires soon → Satışçıya alarm gitmesi"

* **Hunter**: WHOIS çek, expiry hesapla, `hunter_expiry_risk` alanına yansıt.
* **Dataverse**: `hunter_expiry_risk` custom field.
* **Power Automate**: `hunter_expiry_risk = High` ise → satışçıya e-mail / task oluştur.

Sonuç:
* Hunter sadece zor kısmı yapıyor (WHOIS + risk logic).
* Task, bildirim, UI = tamamen CRM + Flow.

---

## Net Çerçeve (Tek Cümlelik)

> **Hunter = Dış dünyadan veri toplayan + bunu işleyip CRM'e atan ince zekâ katmanı.**

> **Dynamics 365 Sales / Sales Hub = Satışçının yaşadığı ana ev.**

---

## Karşı Argümanlar ve Cevaplar

### ✅ Auto-tagging → Kalıyor (Doğru Karar)
- Auto-tagging = sinyal üretimi
- "security-risk", "migration-ready", "expire-soon" → analitik veri, CRM datası değil
- Hunter'da kalacak

### ✅ Manuel Tags / Notes / Favorites → Atılacak
- Bu veri **ilişki yönetimi** verisi, **analiz verisi değil**
- Dynamics zaten timeline, aktiviteler, notlar, custom alanlar için optimize edilmiş
- Hunter'ın CRM'e dönüşmesi sistemin sonu olurdu

### ✅ Email Validation → Kalacak, Email Generation → Kalkacak
- **Kalacak**: MX check, SMTP reachability, domain-based "email quality" sinyali
- **Gitmeli**: Mail template, Mail body üretme, Sales e-mail taslakları (CRM işi)

### ✅ Alerts: "Tespit Hunter'da, Bildirim Automate'te"
- Hunter'ın görevi: "Bu domain'de X değişti" sinyallerini üretmek
- Power Automate'in görevi: Bu sinyalleri alıp mail atmak, Dynamics task açmak
- Hunter'da "alert config tablosu, kanal tercihi, kullanıcı seçimi" olmamalı

### ✅ Dashboard = CRM + Power BI
- Satış dashboard → Power BI
- Operasyon dashboard → Hunter Ops (opsiyonel, DevOps için)

### ✅ SSO → Plugin Olarak Kalacak
- SSO gereksiz değil ama CORE'da zorunlu değil
- Motor ve UI ayrılmalı
- API key auth = CORE güvenlik mekanizması
- SSO = Plugin (opsiyonel)

---

## Sonuç

**Yön: Doğru**

**Katmanlama: Doğru**

**En büyük kazanç**: Hunter artık "CRM'in minyatür kopyası" değil, **özel bir sinyal + sales-intelligence motoru** oluyor.

---

## Related Documents

- `docs/active/NO-BREAK-REFACTOR-PLAN.md` - Detaylı uygulama planı
- `docs/todos/G21-architecture-refactor.md` - TODO listesi

