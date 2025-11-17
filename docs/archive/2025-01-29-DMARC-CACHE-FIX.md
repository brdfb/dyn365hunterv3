# DMARC Coverage Cache Fix

**Tarih:** 2025-01-29  
**Sorun:** Score Breakdown'da eski cache'den gelen yanlış DMARC coverage değeri  
**Durum:** ✅ **DÜZELTİLDİ**

---

## 🚨 Sorun

### Tutarsızlık

**Score Breakdown Modal:**
- DMARC Coverage: `100%` ❌ (yanlış - eski cache'den)

**Sales Summary:**
- DMARC Coverage: `null` ✅ (doğru - yeni hesaplama)

### Neden Oluyordu?

1. **İlk scan** → DMARC coverage `100` olarak hesaplandı (eski bug)
2. Bu sonuç **Redis cache'de** saklandı
3. Bug düzeltildi → DMARC coverage artık `null` dönüyor
4. Ama **Score Breakdown** hala cache'den eski değeri çekiyor
5. **Sales Summary** farklı pipeline → doğru değeri gösteriyor

### Cache Yapısı

- **Scoring Cache:** `cache:scoring:{domain}:{provider}:{signals_hash}`
- **DNS Cache:** `cache:dns:{domain}`
- **TTL:** 1 saat (3600 saniye)

---

## ✅ Çözüm

### 1. Cache Invalidation Fonksiyonları Eklendi

**Dosya:** `app/core/cache.py`

**Yeni Fonksiyonlar:**
- `invalidate_scoring_cache(domain)` - Domain için tüm scoring cache'lerini temizler
- `invalidate_dns_cache(domain)` - Domain için DNS cache'ini temizler

**Kod:**
```python
def invalidate_scoring_cache(domain: str) -> int:
    """
    Invalidate all scoring cache entries for a specific domain.
    
    Since scoring cache keys include provider and signals_hash,
    we need to pattern match and delete all keys for the domain.
    """
    # Pattern match: cache:scoring:{domain}:*
    # Delete all matching keys
```

### 2. Rescan'de Otomatik Cache Invalidation

**Dosya:** `app/core/rescan.py`

**Değişiklik:**
```python
# Invalidate cache before rescan (force fresh scan)
invalidate_scan_cache(domain)
invalidate_scoring_cache(domain)  # ✅ YENİ - Scoring cache temizleniyor
invalidate_dns_cache(domain)      # ✅ YENİ - DNS cache temizleniyor
```

**Sonuç:**
- Rescan yapıldığında tüm cache'ler otomatik temizleniyor
- Yeni scan sonuçları fresh data ile hesaplanıyor
- DMARC coverage doğru değerle cache'leniyor

### 3. Manuel Cache Invalidation Script'i

**Dosya:** `scripts/invalidate_scoring_cache.py`

**Kullanım:**
```bash
# Tek domain için
python scripts/invalidate_scoring_cache.py dmkimya.com.tr

# Tüm scoring cache'i temizle
python scripts/invalidate_scoring_cache.py --all
```

---

## 🧪 Test Senaryoları

### Senaryo 1: Rescan ile Cache Temizleme

1. Domain scan edildi (eski bug ile → DMARC coverage: 100)
2. Bug düzeltildi
3. Rescan yapıldı → Cache otomatik temizlendi
4. Yeni scan → DMARC coverage: `null` ✅

### Senaryo 2: Manuel Cache Temizleme

1. Domain scan edildi (eski bug ile → DMARC coverage: 100)
2. Bug düzeltildi
3. Script ile cache temizlendi: `python scripts/invalidate_scoring_cache.py dmkimya.com.tr`
4. Score Breakdown açıldı → Cache miss → Yeni hesaplama → DMARC coverage: `null` ✅

---

## 📋 Sonuç

### ✅ Düzeltilenler

1. **Scoring cache invalidation** fonksiyonu eklendi
2. **DNS cache invalidation** fonksiyonu eklendi
3. **Rescan'de otomatik cache temizleme** eklendi
4. **Manuel cache temizleme script'i** eklendi

### 🎯 Etki

- **Score Breakdown** ve **Sales Summary** artık tutarlı
- Rescan yapıldığında cache otomatik temizleniyor
- Manuel cache temizleme mümkün

### 📝 Notlar

- Cache TTL: 1 saat (otomatik expire olur)
- Rescan yapılmadan cache temizlenmez (beklenen davranış)
- Production'da rescan yapıldığında cache otomatik temizlenecek

---

## 🔗 İlgili Dosyalar

- `app/core/cache.py` - Cache invalidation fonksiyonları
- `app/core/rescan.py` - Rescan'de cache temizleme
- `app/core/analyzer_dns.py` - DMARC coverage bug fix
- `scripts/invalidate_scoring_cache.py` - Manuel cache temizleme script'i

