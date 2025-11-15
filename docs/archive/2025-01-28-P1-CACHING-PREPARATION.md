# P1 Caching Layer Hazırlığı

**Tarih**: 2025-01-28  
**Durum**: Hazırlık Tamamlandı  
**Amaç**: Redis-based distributed caching için zemin hazırlamak (read-only analiz)

---

## 📋 Mevcut Cache Durumu Analizi

### ✅ Mevcut Cache'ler

#### 1. WHOIS Cache (In-Memory)
- **Lokasyon**: `app/core/analyzer_whois.py`
- **Tip**: In-memory dictionary (`_whois_cache: Dict[str, Tuple[Optional[Dict], float]]`)
- **TTL**: 1 saat (3600 saniye)
- **Kullanım**: `get_whois_info()` fonksiyonunda
- **Sorun**: Multi-worker için uygun değil (her worker kendi cache'ini tutuyor)

**Kod Örneği:**
```python
# app/core/analyzer_whois.py
_whois_cache: Dict[str, Tuple[Optional[Dict], float]] = {}
CACHE_TTL = 3600  # 1 hour

def _check_cache(domain: str) -> Optional[Dict[str, Any]]:
    if domain in _whois_cache:
        result, timestamp = _whois_cache[domain]
        if time.time() - timestamp < CACHE_TTL:
            return result
```

---

### ❌ Eksik Cache'ler

#### 2. DNS Cache
- **Lokasyon**: `app/core/analyzer_dns.py`
- **Durum**: ❌ **YOK** - Her seferinde DNS query yapılıyor
- **Fonksiyon**: `analyze_dns()` - MX, SPF, DKIM, DMARC kontrolü
- **Etki**: Yüksek - DNS query'leri pahalı ve rate limit riski var

**Kullanım Yerleri:**
- `app/core/tasks.py` - `scan_single_domain()` fonksiyonunda
- `app/api/scan.py` - `/scan/domain` endpoint'inde

#### 3. Provider Mapping Cache
- **Lokasyon**: `app/core/provider_map.py`
- **Durum**: ❌ **YOK** - Her seferinde `classify_provider()` çalışıyor
- **Fonksiyon**: `classify_provider(mx_root)` - MX root'dan provider name döndürür
- **Etki**: 🔴 **KRİTİK** - En çok tekrar eden pattern (aynı MX root → aynı provider)
- **NOT**: `_PROVIDERS_CACHE` var ama bu `providers.json` dosyasını cache'liyor, mapping sonuçlarını değil

**Kullanım Yerleri:**
- `app/core/tasks.py` - `scan_single_domain()` fonksiyonunda
- Her domain scan'de `classify_provider(mx_root)` çağrılıyor

#### 4. Scoring Cache
- **Lokasyon**: `app/core/scorer.py`
- **Durum**: ❌ **YOK** - Her seferinde `score_domain()` çalışıyor
- **Fonksiyon**: `score_domain()` - Domain, signals, provider'dan score hesaplar
- **Etki**: 🔴 **KRİTİK** - Aynı domain + aynı signals → aynı score (gereksiz hesaplama)
- **NOT**: `_RULES_CACHE` var ama bu `rules.json` dosyasını cache'liyor, scoring sonuçlarını değil

**Kullanım Yerleri:**
- `app/core/tasks.py` - `scan_single_domain()` fonksiyonunda
- Her domain scan'de `score_domain()` çağrılıyor

#### 5. Domain-Level Full Scan Cache
- **Lokasyon**: `app/core/tasks.py`
- **Durum**: ❌ **YOK** - Her seferinde full scan yapılıyor
- **Fonksiyon**: `scan_single_domain()` - Tüm scan result'ı cache'lenebilir
- **Etki**: 🔴 **BÜYÜK EKSİK** - Aynı domain tekrar scan edilince tüm işlemler tekrar yapılıyor

**Kullanım Yerleri:**
- `app/api/scan.py` - `/scan/domain` endpoint'inde
- `app/core/tasks.py` - `bulk_scan_task()` içinde

---

## 🔑 Cache Key Design

### Redis Cache Key Stratejisi

| Cache Tipi | Key Format | TTL | Açıklama |
|-----------|------------|-----|----------|
| **DNS** | `dns:{domain}` | 1 saat (3600s) | DNS analysis result (MX, SPF, DKIM, DMARC) |
| **WHOIS** | `whois:{domain}` | 24 saat (86400s) | WHOIS data (değişmez, uzun TTL) |
| **Provider** | `provider:{mx_root}` | 24 saat (86400s) | Provider mapping (mx_root → provider name) |
| **Scoring** | `scoring:{domain}:{provider}:{signals_hash}` | 1 saat (3600s) | Scoring result (signals hash ile) |
| **Scan** | `scan:{domain}` | 1 saat (3600s) | Full scan result (tüm scan output) |

### Signals Hash Generation

**Strateji**: `sha256(json.dumps(signals, sort_keys=True).encode())[:16]`

**Neden `sort_keys=True`?**
- Aynı signals farklı sırada gelirse aynı hash üretmeli
- Örnek: `{'spf': True, 'dkim': True}` ve `{'dkim': True, 'spf': True}` → aynı hash

**Kod Örneği:**
```python
import hashlib
import json

signals = {'spf': True, 'dkim': True, 'dmarc_policy': 'reject'}
signals_hash = hashlib.sha256(
    json.dumps(signals, sort_keys=True).encode()
).hexdigest()[:16]
# Örnek: "a1b2c3d4e5f6g7h8"
```

**Cache Key Örnekleri:**
```
dns:example.com
whois:example.com
provider:outlook.com
scoring:example.com:M365:a1b2c3d4e5f6g7h8
scan:example.com
```

---

## ⏱️ TTL Alignment Analizi

### TTL Hiyerarşisi

```
WHOIS Cache (24 saat) ← En uzun (data değişmez)
  ↓
Provider Cache (24 saat) ← Değişmez
  ↓
DNS Cache (1 saat) ← Orta
  ↓
Scoring Cache (1 saat) ← DNS'e bağımlı
  ↓
Scan Cache (1 saat) ← En kısa (tüm cache'lere bağımlı)
```

### TTL Uyumu Kuralları

1. **Scan Cache TTL ≤ DNS/WHOIS TTL**
   - Scan cache, DNS ve WHOIS cache'lerinden uzun olmamalı
   - Konsistensi için üst sınır: 1 saat

2. **Scoring Cache TTL ≤ DNS Cache TTL**
   - Scoring, DNS signals'e bağımlı
   - DNS değişirse scoring de değişmeli

3. **Provider Cache TTL = WHOIS Cache TTL**
   - Provider mapping değişmez (MX root → provider name)
   - WHOIS ile aynı TTL mantıklı (24 saat)

### Cache Invalidation Stratejisi

**Otomatik Expire (TTL):**
- Redis TTL mekanizması kullanılacak
- Manuel invalidation gerekmez (TTL otomatik expire eder)

**Versioned Cache Keys (Gelecek için):**
- Cache key format: `{type}:{version}:{identifier}`
- Örnek: `dns:v1:example.com`
- Version değiştiğinde eski cache'ler otomatik expire olur

---

## 📊 Cache Hit Rate Tahmini

### Senaryo: 100 Domain Bulk Scan

**Cache Hit Senaryoları:**

1. **İlk Scan (Cold Start)**
   - DNS Cache: 0% hit (tüm domain'ler için DNS query)
   - WHOIS Cache: 0% hit (tüm domain'ler için WHOIS query)
   - Provider Cache: 0% hit (tüm MX root'lar için mapping)
   - Scoring Cache: 0% hit (tüm domain'ler için scoring)
   - Scan Cache: 0% hit (tüm domain'ler için full scan)

2. **İkinci Scan (1 saat içinde)**
   - DNS Cache: ~100% hit (TTL: 1 saat)
   - WHOIS Cache: ~100% hit (TTL: 24 saat)
   - Provider Cache: ~80% hit (aynı MX root'lar tekrar eder)
   - Scoring Cache: ~90% hit (aynı signals → aynı score)
   - Scan Cache: ~100% hit (TTL: 1 saat)

3. **Gerçek Dünya Senaryosu**
   - 100 domain → 50 farklı MX root → Provider cache: 50% hit
   - Aynı domain'ler tekrar scan → Scan cache: 100% hit
   - Farklı domain'ler ama aynı MX root → Provider cache: 100% hit

---

## 🔄 Migration Stratejisi (In-Memory → Redis)

### WHOIS Cache Migration

**Mevcut:**
```python
# app/core/analyzer_whois.py
_whois_cache: Dict[str, Tuple[Optional[Dict], float]] = {}

def _check_cache(domain: str):
    if domain in _whois_cache:
        result, timestamp = _whois_cache[domain]
        if time.time() - timestamp < CACHE_TTL:
            return result
```

**Yeni (Redis):**
```python
# app/core/cache.py
def get_cached_whois_result(domain: str) -> Optional[Dict]:
    key = f"whois:{domain}"
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None

def cache_whois_result(domain: str, result: Dict, ttl: int = 86400):
    key = f"whois:{domain}"
    redis_client.setex(key, ttl, json.dumps(result))
```

**Migration Adımları:**
1. `app/core/cache.py` oluştur (Redis cache utilities)
2. `analyzer_whois.py`'de `_check_cache()` ve `_set_cache()` fonksiyonlarını Redis'e migrate et
3. In-memory `_whois_cache` dict'ini kaldır
4. Test: Multi-worker'da cache paylaşımı çalışıyor mu?

---

## 🎯 Cache Implementation Planı

### 1. DNS Cache
- **Fonksiyon**: `analyze_dns()` sonucunu cache'le
- **Key**: `dns:{domain}`
- **TTL**: 1 saat (3600s)
- **Lokasyon**: `app/core/analyzer_dns.py`

### 2. WHOIS Cache (Migration)
- **Fonksiyon**: `get_whois_info()` sonucunu Redis'e migrate et
- **Key**: `whois:{domain}`
- **TTL**: 24 saat (86400s) - WHOIS data değişmez
- **Lokasyon**: `app/core/analyzer_whois.py`

### 3. Provider Mapping Cache
- **Fonksiyon**: `classify_provider(mx_root)` sonucunu cache'le
- **Key**: `provider:{mx_root}`
- **TTL**: 24 saat (86400s) - Provider mapping değişmez
- **Lokasyon**: `app/core/provider_map.py`

### 4. Scoring Cache
- **Fonksiyon**: `score_domain()` sonucunu cache'le
- **Key**: `scoring:{domain}:{provider}:{signals_hash}`
- **TTL**: 1 saat (3600s)
- **Lokasyon**: `app/core/scorer.py`
- **Signals Hash**: `sha256(json.dumps(signals, sort_keys=True).encode())[:16]`

### 5. Domain-Level Full Scan Cache
- **Fonksiyon**: `scan_single_domain()` sonucunu cache'le
- **Key**: `scan:{domain}`
- **TTL**: 1 saat (3600s) - DNS/WHOIS TTL'lerinden uzun olmayacak
- **Lokasyon**: `app/core/tasks.py`

---

## ⚠️ Dikkat Edilmesi Gerekenler

### 1. Cache Consistency
- Scan cache TTL'i, DNS/WHOIS TTL'lerinden uzun olmamalı
- DNS değişirse scan cache de expire olmalı (TTL uyumu)

### 2. Signals Hash Stability
- `sort_keys=True` kullanılmalı (aynı signals → aynı hash)
- Hash length: 16 karakter (yeterli uniqueness)

### 3. Multi-Worker Cache Sharing
- Redis-based cache multi-worker'da paylaşılır
- In-memory cache kaldırılmalı (her worker kendi cache'ini tutuyor)

### 4. Cache Miss Handling
- Cache miss durumunda normal flow devam eder
- Cache hit durumunda external API call'lar skip edilir

### 5. Redis Down Senaryosu
- Cache miss olarak davranılır (graceful degradation)
- Circuit breaker pattern kullanılabilir (P1-2: Distributed Rate Limiting ile birlikte)

---

## ✅ Hazırlık Checklist

- [x] Mevcut cache durumu analiz edildi (WHOIS in-memory var, diğerleri yok)
- [x] Cache key design hazırlandı (5 cache tipi)
- [x] TTL alignment stratejisi dokümante edildi
- [x] Signals hash generation stratejisi belirlendi
- [x] Migration planı hazırlandı (in-memory → Redis)
- [x] Cache hit rate tahmini yapıldı

---

## 🚀 Sonraki Adımlar

1. **Redis Cache Utilities Oluştur**
   - `app/core/cache.py` dosyası oluştur
   - Redis connection ve cache helper fonksiyonları

2. **DNS Cache Implementasyonu**
   - `analyzer_dns.py`'ye Redis cache ekle
   - `analyze_dns()` fonksiyonunu cache-aware yap

3. **WHOIS Cache Migration**
   - In-memory cache'i Redis'e migrate et
   - `analyzer_whois.py`'yi güncelle

4. **Provider Mapping Cache**
   - `provider_map.py`'ye Redis cache ekle
   - `classify_provider()` fonksiyonunu cache-aware yap

5. **Scoring Cache**
   - `scorer.py`'ye Redis cache ekle
   - Signals hash generation implementasyonu
   - `score_domain()` fonksiyonunu cache-aware yap

6. **Scan Cache**
   - `tasks.py`'ye Redis cache ekle
   - `scan_single_domain()` fonksiyonunu cache-aware yap

---

**Referans**: `docs/active/P1-IMPLEMENTATION-PLAYBOOK.md` - Caching Layer bölümü

