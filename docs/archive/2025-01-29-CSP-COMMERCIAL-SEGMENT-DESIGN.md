# 🎯 CSP Commercial Segment & Heat Tasarımı

**Tarih:** 2025-01-29  
**Durum:** Tasarım Aşaması  
**Versiyon:** v1.0-draft

---

## 📋 Genel Bakış

CSP P-modeli entegrasyonu için **Commercial Segment** ve **Commercial Heat** kavramlarını netleştiriyoruz.

### İkili Model

1. **Commercial Segment** (Kategorik): `GREENFIELD | COMPETITIVE | RENEWAL | LOW_INTENT | NO_GO`
2. **Commercial Heat** (Seviye): `HIGH | MEDIUM | LOW`

---

## 🎯 Commercial Segment Kategorileri

### 1. **GREENFIELD** (Yeşil Alan)

**Tanım:** Self-hosted / on-premise mail sunucusundan M365'e geçiş fırsatı.

**Senaryo:**
- Self-hosted mail server (cPanel, Plesk, Exchange on-prem)
- Local provider (TürkHost, Natro, vb.)
- Hosting provider (shared hosting mail)
- Partner yok veya zayıf
- Migration + full setup fırsatı

**Provider Pattern:**
- `Local` (self-hosted)
- `Hosting` (shared hosting)
- `Unknown` (teknik sinyal zayıf ama domain aktif)

**Segment Mapping:**
- `Migration` segment + `Local`/`Hosting` provider
- `Cold` segment + `Local` provider + score 5-59

**Commercial Heat:** `HIGH`

**Neden Yüksek:**
- Lowest cost of acquisition
- Highest revenue potential
- Migration = yüksek kâr
- İlk kurulum → destek + güvenlik satılabilir

---

### 2. **COMPETITIVE** (Rekabetçi Geçiş)

**Tanım:** Başka bir cloud provider'dan M365'e geçiş fırsatı.

**Senaryo:**
- Google Workspace → EXO geçiş fırsatı
- Zoho → EXO
- Yandex → EXO
- Partner yok veya zayıf
- Müşteri zaten değişime açık (cloud kullanıyor)

**Provider Pattern:**
- `Google` (Google Workspace)
- `Zoho` (Zoho Mail)
- `Yandex` (Yandex Mail)

**Segment Mapping:**
- `Migration` segment + `Google`/`Zoho`/`Yandex` provider

**Commercial Heat:** `HIGH`

**Neden Yüksek:**
- Migration var
- M365'e geçiş fırsatı büyük
- Müşteri zaten değişime açık
- Cloud-to-cloud geçiş = daha kolay

---

### 3. **RENEWAL** (Yenileme Baskısı)

**Tanım:** Zaten M365 kullanıyor, partner güçlü, müşteri memnun, transfer friksiyon yüksek.

**Senaryo:**
- M365 var
- Partner güçlü (iyi hizmet veriyor)
- Müşteri memnun
- Transfer friksiyon yüksek
- Upsell yapılabilir ama kapama süresi uzun

**Provider Pattern:**
- `M365` (zaten kullanıyor)

**Segment Mapping:**
- `Existing` segment + `M365` provider + score >= 70

**Commercial Heat:** `MEDIUM`

**Neden Orta:**
- Kazanması zor
- Fiyat rekabetli
- Migration yok (gelir düşük)
- Upsell yapılabilir ama kapama süresi uzun

---

### 4. **WEAK_PARTNER** (Zayıf Partner)

**Tanım:** M365 var ama memnuniyetsizlik sinyalleri var, partner zayıf.

**Senaryo:**
- M365 var ama memnuniyetsizlik sinyalleri:
  - IT çağrı yoğunluğu
  - Backup yok
  - Güvenlik yok
  - Partner ilgilenmiyor
  - Tamamlanmamış migration

**Provider Pattern:**
- `M365` (zaten kullanıyor)

**Segment Mapping:**
- `Existing` segment + `M365` provider + score < 70

**Commercial Heat:** `MEDIUM` veya `HIGH` (skor ve sinyallere göre)

**Neden Orta/Yüksek:**
- Migration yok
- Ama partner değişikliği → hızlı kazanç
- Upsell + güvenlik fırsatı
- Partner değiştirme bariyerini kıracak değer önerisi

---

### 5. **LOW_INTENT** (Düşük Niyet)

**Tanım:** Self-hosted ama küçük firma, IT kapalı, değişim istemiyor, bütçe zayıf.

**Senaryo:**
- Self-hosted ama küçük firma
- IT kapalı
- Değişim istemiyor
- Bütçe zayıf
- "Şimdilik ilgimiz yok" kitlesi

**Provider Pattern:**
- `Local` (self-hosted)
- `Hosting` (shared hosting)
- `Unknown` (teknik sinyal zayıf)

**Segment Mapping:**
- `Cold` segment + score 20-59
- `Migration` segment + düşük skor (edge case)

**Commercial Heat:** `LOW`

**Neden Düşük:**
- Potansiyel var
- Ama zamanlama kötü
- "Şimdilik ilgimiz yok" kitlesi
- Uzun nurturing gerekiyor

---

### 6. **NO_GO** (Yapılmayacak)

**Tanım:** Tek kişilik işletme, domain park edilmiş, spam domain, teknik sinyal zayıf, gelir yok.

**Senaryo:**
- Tek kişilik işletme
- Domain park edilmiş
- Natro-hosted mikro site
- Spam domain
- Teknik sinyal zayıf
- Gelir yok

**Provider Pattern:**
- `Unknown` (teknik sinyal yok)
- `Local` (ama çok düşük skor)

**Segment Mapping:**
- `Skip` segment
- `Cold` segment + score < 20

**Commercial Heat:** `LOW` (aslında "VERY_LOW" ama LOW olarak işaretleniyor)

**Neden Çok Düşük:**
- Arama bile yok
- Sadece arşiv
- Zaman kaybı

---

## 🔥 Commercial Heat Seviyeleri

### **HIGH** (Yüksek)

**Kriterler:**
- `GREENFIELD` segment
- `COMPETITIVE` segment
- `WEAK_PARTNER` segment (yüksek skorlu)

**Aksiyon:** Hemen aksiyon (48 saat - 3 gün)

---

### **MEDIUM** (Orta)

**Kriterler:**
- `RENEWAL` segment
- `WEAK_PARTNER` segment (düşük skorlu)

**Aksiyon:** Soft nurturing (5 gün - 2 hafta)

---

### **LOW** (Düşük)

**Kriterler:**
- `LOW_INTENT` segment
- `NO_GO` segment

**Aksiyon:** Aylık e-mail nurturing veya arşiv

---

## 📊 Mapping Tablosu

| Commercial Segment | Provider Pattern | Technical Segment | Score Range | Commercial Heat | P-Model |
|-------------------|------------------|-------------------|------------|-----------------|---------|
| **GREENFIELD** | Local, Hosting | Migration, Cold | 5-100 | HIGH | P1 |
| **COMPETITIVE** | Google, Zoho, Yandex | Migration | 60-100 | HIGH | P2 |
| **WEAK_PARTNER** | M365 | Existing | 30-69 | MEDIUM/HIGH | P3 |
| **RENEWAL** | M365 | Existing | 70-100 | MEDIUM | P4 |
| **LOW_INTENT** | Local, Hosting, Unknown | Cold | 20-59 | LOW | P5 |
| **NO_GO** | Unknown, Local | Skip, Cold | 0-19 | LOW | P6 |

---

## 🔧 Hesaplama Mantığı (Taslak)

### Commercial Segment Hesaplama

```python
def calculate_commercial_segment(
    technical_segment: str,
    provider: str,
    readiness_score: int,
    tenant_size: Optional[str] = None
) -> str:
    """
    Calculate Commercial Segment based on technical segment, provider, and score.
    
    Returns: GREENFIELD | COMPETITIVE | WEAK_PARTNER | RENEWAL | LOW_INTENT | NO_GO
    """
    # NO_GO: Skip segment veya çok düşük skor
    if technical_segment == "Skip":
        return "NO_GO"
    
    if technical_segment == "Cold" and readiness_score < 20:
        return "NO_GO"
    
    # GREENFIELD: Self-hosted → M365 migration
    if technical_segment == "Migration" and provider in ["Local", "Hosting"]:
        return "GREENFIELD"
    
    if technical_segment == "Cold" and provider == "Local" and 5 <= readiness_score <= 59:
        return "GREENFIELD"
    
    # COMPETITIVE: Cloud-to-cloud migration
    if technical_segment == "Migration" and provider in ["Google", "Zoho", "Yandex"]:
        return "COMPETITIVE"
    
    # Existing M365 scenarios
    if technical_segment == "Existing" and provider == "M365":
        if readiness_score >= 70:
            return "RENEWAL"  # Güçlü partner, memnun müşteri
        else:
            return "WEAK_PARTNER"  # Zayıf partner, memnuniyetsizlik sinyalleri
    
    # LOW_INTENT: Düşük sinyal, uzun nurturing
    if technical_segment == "Cold" and 20 <= readiness_score <= 59:
        return "LOW_INTENT"
    
    # Default fallback
    return "NO_GO"
```

### Commercial Heat Hesaplama

```python
def calculate_commercial_heat(
    commercial_segment: str,
    readiness_score: int,
    tenant_size: Optional[str] = None
) -> str:
    """
    Calculate Commercial Heat based on commercial segment and additional factors.
    
    Returns: HIGH | MEDIUM | LOW
    """
    if commercial_segment == "GREENFIELD":
        return "HIGH"
    
    if commercial_segment == "COMPETITIVE":
        return "HIGH"
    
    if commercial_segment == "WEAK_PARTNER":
        # Yüksek skorlu weak partner = daha yüksek heat
        if readiness_score >= 50:
            return "HIGH"
        else:
            return "MEDIUM"
    
    if commercial_segment == "RENEWAL":
        return "MEDIUM"
    
    if commercial_segment == "LOW_INTENT":
        return "LOW"
    
    if commercial_segment == "NO_GO":
        return "LOW"
    
    # Default
    return "LOW"
```

---

## 📝 Rules.json Entegrasyonu (Taslak)

Commercial Segment kuralları `app/data/rules.json` içine eklenecek:

```json
{
  "commercial_segment_rules": [
    {
      "segment": "GREENFIELD",
      "condition": {
        "technical_segment": "Migration",
        "provider_in": ["Local", "Hosting"]
      },
      "description": "Self-hosted → M365 migration fırsatı"
    },
    {
      "segment": "GREENFIELD",
      "condition": {
        "technical_segment": "Cold",
        "provider_in": ["Local"],
        "min_score": 5,
        "max_score": 59
      },
      "description": "Self-hosted mail server, greenfield potansiyeli"
    },
    {
      "segment": "COMPETITIVE",
      "condition": {
        "technical_segment": "Migration",
        "provider_in": ["Google", "Zoho", "Yandex"]
      },
      "description": "Cloud-to-cloud migration fırsatı"
    },
    {
      "segment": "WEAK_PARTNER",
      "condition": {
        "technical_segment": "Existing",
        "provider_in": ["M365"],
        "max_score": 69
      },
      "description": "M365 var ama partner zayıf, memnuniyetsizlik sinyalleri"
    },
    {
      "segment": "RENEWAL",
      "condition": {
        "technical_segment": "Existing",
        "provider_in": ["M365"],
        "min_score": 70
      },
      "description": "M365 var, partner güçlü, renewal/upsell fırsatı"
    },
    {
      "segment": "LOW_INTENT",
      "condition": {
        "technical_segment": "Cold",
        "min_score": 20,
        "max_score": 59
      },
      "description": "Düşük sinyal, uzun nurturing gerekiyor"
    },
    {
      "segment": "NO_GO",
      "condition": {
        "technical_segment": "Skip"
      },
      "description": "Yetersiz veri, analiz dışı"
    },
    {
      "segment": "NO_GO",
      "condition": {
        "technical_segment": "Cold",
        "max_score": 19
      },
      "description": "Çok düşük sinyal, no-go"
    }
  ],
  "commercial_heat_rules": [
    {
      "heat": "HIGH",
      "condition": {
        "commercial_segment_in": ["GREENFIELD", "COMPETITIVE"]
      },
      "description": "Yüksek commercial heat - hemen aksiyon"
    },
    {
      "heat": "HIGH",
      "condition": {
        "commercial_segment": "WEAK_PARTNER",
        "min_score": 50
      },
      "description": "Yüksek skorlu weak partner - yüksek heat"
    },
    {
      "heat": "MEDIUM",
      "condition": {
        "commercial_segment_in": ["RENEWAL", "WEAK_PARTNER"]
      },
      "description": "Orta commercial heat - soft nurturing"
    },
    {
      "heat": "LOW",
      "condition": {
        "commercial_segment_in": ["LOW_INTENT", "NO_GO"]
      },
      "description": "Düşük commercial heat - uzun nurturing veya arşiv"
    }
  ]
}
```

---

## ✅ Sonraki Adımlar

1. ✅ Commercial Segment kategorileri netleştirildi
2. ⏳ Rules.json taslağı hazırlandı
3. ⏳ Technical Heat netleştirme
4. ⏳ P1-P6 mapping rule-based tanımlama
5. ⏳ Implementation (Python code)
6. ⏳ UI + API kontratı güncelleme

---

## 📚 Referanslar

- CSP P-Modeli: `docs/active/CSP-P-MODEL-INTEGRATION.md` (oluşturulacak)
- Technical Segment: `app/core/scorer.py`
- Priority Score: `app/core/priority.py`

