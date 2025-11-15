# TODO: P1 Hazırlık - Zemin Hazırlama

**Date Created**: 2025-01-28  
**Status**: ✅ **TAMAMLANDI**  
**Phase**: P1 Preparation (Pre-Implementation)  
**Goal**: Dev ortamını yormadan, hiçbir şeyi kırmadan, P1'e zemin hazırlamak

---

## 🎯 Genel Strateji

**Prensip**: Kod değiştirmeyeceğiz, sadece analiz, dokümantasyon ve planlama yapacağız.

**Hedef**: P1 implementasyonuna başlamadan önce tüm hazırlık işlerini tamamlamak.

---

## 📋 Hazırlık İşleri

### 1. Alembic Migration Hazırlığı ⏱️ 2 saat ✅ **TAMAMLANDI**

**Amaç**: Alembic implementasyonuna zemin hazırlamak

- [x] **Mevcut migration dosyalarını analiz et**
  - [x] `g16_webhook_enrichment.sql` - İçeriği, bağımlılıkları
  - [x] `g17_notes_tags_favorites.sql` - İçeriği, bağımlılıkları
  - [x] `g18_rescan_alerts_scoring.sql` - İçeriği, bağımlılıkları
  - [x] `g19_favorites_migration.sql` - İçeriği, bağımlılıkları
  - [x] `g19_users_auth.sql` - İçeriği, bağımlılıkları
  - [x] `g20_domain_intelligence.sql` - İçeriği, bağımlılıkları
  - [x] **DÜZELTME**: KALAN-ISLER-PRIORITY.md'de 7 migration geçiyordu ama dosya sisteminde 6 tane var - sayı düzeltildi (6 migration)
  - [x] Her migration'ın SQLAlchemy model karşılığını belirle

- [x] **Schema snapshot planı**
  - [x] Mevcut production schema'yı dokümante et (tablo listesi, kolonlar, indexler)
  - [x] `app/db/schema.sql` ile migration'ların uyumunu kontrol et
  - [x] Base revision stratejisini dokümante et (autogenerate + manuel diff)

- [x] **Migration dependency grafiği**
  - [x] Migration'ların sıralama bağımlılıklarını çıkar
  - [x] Alembic revision sırasını planla

- [x] **Dokümantasyon**
  - [x] `docs/active/P1-ALEMBIC-PREPARATION.md` oluştur
  - [x] Migration mapping tablosu (SQL → Alembic revision)
  - [x] Base revision stratejisi dokümante et

**Çıktı**: `docs/active/P1-ALEMBIC-PREPARATION.md`

---

### 2. Distributed Rate Limiting Hazırlığı ⏱️ 1 saat ✅ **TAMAMLANDI**

**Amaç**: Redis-based distributed rate limiting için zemin hazırlamak

- [x] **Mevcut rate limiter analizi**
  - [x] `app/core/rate_limiter.py` - RateLimiter class yapısı
  - [x] `app/core/api_key_auth.py` - API key rate limiter kullanımı
  - [x] DNS rate limiter kullanım yerleri (grep ile bul)
  - [x] WHOIS rate limiter kullanım yerleri (grep ile bul)
  - [x] Mevcut rate limit değerleri (10 req/s DNS, 5 req/s WHOIS)

- [x] **Redis setup kontrolü**
  - [x] `docker-compose.yml` - Redis service var mı?
  - [x] `app/config.py` - Redis URL config var mı?
  - [x] Redis connection test script'i hazırla (test için)

- [x] **Migration stratejisi**
  - [x] In-memory → Redis migration planı
  - [x] Fallback stratejisi (Redis down → in-memory)
  - [x] Circuit breaker tasarımı

- [x] **Dokümantasyon**
  - [x] `docs/active/P1-RATE-LIMITING-PREPARATION.md` oluştur
  - [x] Mevcut kullanım yerleri listesi
  - [x] Redis migration planı
  - [x] Fallback ve circuit breaker stratejisi

**Çıktı**: `docs/active/P1-RATE-LIMITING-PREPARATION.md` ✅ **TAMAMLANDI**

---

### 3. Caching Layer Hazırlığı ⏱️ 1.5 saat ✅ **TAMAMLANDI**

**Amaç**: Redis-based distributed caching için zemin hazırlamak

- [x] **Mevcut cache durumu analizi**
  - [x] `app/core/analyzer_whois.py` - In-memory WHOIS cache (`_whois_cache`)
  - [x] `app/core/analyzer_dns.py` - DNS cache var mı? (yok)
  - [x] `app/core/provider_map.py` - Provider mapping cache var mı? (yok)
  - [x] `app/core/scorer.py` - Scoring cache var mı? (yok)
  - [x] Cache kullanım yerlerini grep ile bul

- [x] **Cache key design**
  - [x] DNS cache key: `dns:{domain}` - TTL: 1 saat
  - [x] WHOIS cache key: `whois:{domain}` - TTL: 24 saat
  - [x] Provider cache key: `provider:{mx_root}` - TTL: 24 saat
  - [x] Scoring cache key: `scoring:{domain}:{provider}:{signals_hash}` - TTL: 1 saat
  - [x] Scan cache key: `scan:{domain}` - TTL: 1 saat
  - [x] Signals hash generation stratejisi (sha256, sort_keys=True)

- [x] **TTL alignment analizi**
  - [x] Scan cache TTL <= DNS/WHOIS TTL (konsistensi)
  - [x] Cache invalidation stratejisi

- [x] **Dokümantasyon**
  - [x] `docs/active/P1-CACHING-PREPARATION.md` oluştur
  - [x] Cache key design tablosu
  - [x] TTL alignment stratejisi
  - [x] Migration planı (in-memory → Redis)

**Çıktı**: `docs/active/P1-CACHING-PREPARATION.md` ✅ **TAMAMLANDI**

---

### 4. Bulk Operations Hazırlığı ⏱️ 1 saat ✅ **TAMAMLANDI**

**Amaç**: Bulk operations optimization için zemin hazırlamak

- [x] **Mevcut bulk scan analizi**
  - [x] `app/core/tasks.py` - `bulk_scan_task` yapısı
  - [x] Sequential processing analizi (her domain için ayrı transaction)
  - [x] Rate limiting entegrasyonu
  - [x] Progress tracking mekanizması

- [x] **Batch size hesaplama**
  - [x] DNS rate limit: 10 req/s → batch size hesaplama
  - [x] WHOIS rate limit: 5 req/s → batch size hesaplama
  - [x] Optimal batch size formülü (rate-limit aware)

- [x] **Deadlock prevention stratejisi**
  - [x] Transaction timeout değeri (örn: 30 saniye)
  - [x] Retry logic tasarımı
  - [x] Batch isolation stratejisi

- [x] **Partial commit log tasarımı**
  - [x] Log format: `{bulk_id, batch_no, total_batches, committed: [], failed: []}`
  - [x] Recovery mekanizması

- [x] **Dokümantasyon**
  - [x] `docs/active/P1-BULK-OPERATIONS-PREPARATION.md` oluştur
  - [x] Batch size hesaplama formülü
  - [x] Deadlock prevention stratejisi
  - [x] Partial commit log formatı

**Çıktı**: `docs/active/P1-BULK-OPERATIONS-PREPARATION.md` ✅ **TAMAMLANDI**

---

### 5. API Versioning Hazırlığı ⏱️ 0.5 saat ✅ **TAMAMLANDI**

**Amaç**: API versioning için zemin hazırlamak

- [x] **Router listesi**
  - [x] `app/main.py` - Tüm router'ları listele (14 router)
  - [x] Her router'ın endpoint'lerini dokümante et
  - [x] Router bağımlılıkları (varsa)

- [x] **Versioning stratejisi**
  - [x] `/api/v1/` yapısı planı
  - [x] Backward compatibility stratejisi (legacy `/api/...` endpoint'leri)
  - [x] Zero downtime deployment planı

- [x] **Dokümantasyon**
  - [x] `docs/active/P1-API-VERSIONING-PREPARATION.md` oluştur
  - [x] Router mapping tablosu (eski → yeni path)
  - [x] Backward compatibility planı

**Çıktı**: `docs/active/P1-API-VERSIONING-PREPARATION.md` ✅ **TAMAMLANDI**

---

## 📊 Toplam Süre Tahmini

- Alembic Hazırlık: 2 saat
- Rate Limiting Hazırlık: 1 saat
- Caching Hazırlık: 1.5 saat
- Bulk Operations Hazırlık: 1 saat
- API Versioning Hazırlık: 0.5 saat

**Toplam**: ~6 saat (1 gün)

---

## ✅ Hazırlık Tamamlandı

Tüm hazırlık işleri tamamlandı:

1. ✅ 5 adet preparation dokümantasyonu hazır
2. ✅ P1 implementasyonuna başlamak için tüm zemin hazır
3. ✅ Risk analizi ve migration stratejileri dokümante edilmiş
4. ✅ Dev ortamı hiç yorulmamış (kod değişikliği yok)
5. ✅ Hiçbir şey kırılmamış (sadece analiz ve dokümantasyon)

### Oluşturulan Dokümantasyonlar

1. ✅ `docs/active/P1-ALEMBIC-PREPARATION.md` - Alembic migration hazırlığı
2. ✅ `docs/active/P1-CACHING-PREPARATION.md` - Caching layer hazırlığı
3. ✅ `docs/active/P1-RATE-LIMITING-PREPARATION.md` - Distributed rate limiting hazırlığı
4. ✅ `docs/active/P1-BULK-OPERATIONS-PREPARATION.md` - Bulk operations hazırlığı
5. ✅ `docs/active/P1-API-VERSIONING-PREPARATION.md` - API versioning hazırlığı

---

## 🚀 Sonraki Adım

Hazırlık tamamlandıktan sonra:
- `docs/active/P1-IMPLEMENTATION-PLAYBOOK.md` ile implementasyona başla
- Her P1 maddesi için hazırlık dokümantasyonunu referans al
- Branch stratejisine göre implementasyon yap

---

**Not**: Bu hazırlık aşamasında **hiçbir kod değişikliği yapılmayacak**. Sadece analiz, dokümantasyon ve planlama yapılacak.

