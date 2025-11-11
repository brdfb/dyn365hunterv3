# Dyn365Hunter MVP - Plan Critique

## Red Flags (Bloklayıcılar)

### 1. Kapsam Hatası: UI ve Webhook MVP'de Gereksiz
- **Sorun**: Phase 6 (UI) ve `/ingest/webhook` endpoint'i MVP kapsamında değil. "Kahvelik" analiz için API yeterli.
- **Etki**: Geliştirme süresi +2-3 gün, test yükü artar.
- **Çözüm**: Phase 6 ve webhook'u MVP'den çıkar, Post-MVP'e taşı.

### 2. Belirsiz Bağımlılıklar: providers.json ve rules.json İçeriği Yok
- **Sorun**: Dosya yapıları ve örnek veriler belirtilmemiş. Provider mapping mantığı açık ama veri formatı belirsiz.
- **Etki**: Implementasyon sırasında geri dönüşler, tutarsızlıklar.
- **Çözüm**: Her iki dosya için JSON şeması ve örnek içerik ekle (en az 10 provider, 5-7 scoring rule).

### 3. Bulk Processing Timeout/Rate-Limit Stratejisi Yok
- **Sorun**: `/scan/bulk` endpoint'i sequential processing yapıyor ama timeout, rate-limit, partial failure handling yok.
- **Etki**: 100 domain için 15-20 dakika sürebilir, kullanıcı timeout alabilir.
- **Çözüm**: MVP'de bulk'u çıkar, sadece `/scan/domain` kalsın. Bulk sonra async queue ile.

### 4. Schema Migration Otomasyonu Eksik
- **Sorun**: `setup_dev.sh` içinde `schema.sql` manuel çalıştırılıyor (`docker-compose exec`). Hata durumunda sessizce fail olabilir.
- **Etki**: Setup başarısız olabilir, kullanıcı fark etmez.
- **Çözüm**: Alembic veya basit Python migration script (startup hook) ekle.

### 5. WHOIS Rate-Limiting ve Fallback Stratejisi Belirsiz
- **Sorun**: `python-whois` kütüphanesi rate-limit'e takılabilir, bazı TLD'ler için çalışmayabilir.
- **Etki**: WHOIS lookup'ları fail olabilir, scoring eksik kalır.
- **Çözüm**: WHOIS'i optional yap, fail durumunda scoring devam etsin (WHOIS puanı 0).

### 6. Error Handling Detayları Eksik
- **Sorun**: DNS timeout sonrası `domain_signals` tablosuna ne yazılacak? `scan_status` field'ı var ama değerleri belirsiz.
- **Etki**: Partial failure durumlarında veri tutarsızlığı.
- **Çözüm**: `scan_status` enum tanımla: `pending`, `success`, `dns_timeout`, `whois_failed`, `invalid_domain`.

## Yellow Flags (Riskler)

### 1. Test Coverage Kapsamı Belirsiz
- **Risk**: 3 test dosyası var ama edge case'ler (invalid domain, malformed CSV, DNS timeout, WHOIS fail) test edilecek mi?
- **Mitigation**: Her test dosyasına 2-3 edge case testi ekle.

### 2. Performance Target Gerçekçi Değil
- **Risk**: "CSV 100 rows: First 20 processed in ≤2min" - sequential DNS lookup'lar için optimistik.
- **Mitigation**: MVP'de CSV ingestion'ı basitleştir: sadece parse+normalize+insert, scan ayrı endpoint'te.

### 3. Segment Logic Karmaşık ve Test Edilebilirlik Sorunu
- **Risk**: "order matters" diyor ama test senaryoları yok. Segment override mantığı (`score_override=55`) scorer'da nasıl handle edilecek?
- **Mitigation**: Segment logic'i ayrı fonksiyona çıkar, unit test ile doğrula.

### 4. PII ve GDPR Risk
- **Risk**: Email ve company_name DB'de saklanıyor. Loglarda yok ama DB'de var. GDPR compliance için retention policy yok.
- **Mitigation**: MVP'de sadece domain sakla, email/company_name opsiyonel (nullable). Retention policy Post-MVP.

### 5. Docker Compose Healthcheck Detayları Eksik
- **Risk**: PostgreSQL healthcheck var ama FastAPI healthcheck yok. `depends_on` sadece container start'ı bekler, DB ready'i değil.
- **Mitigation**: FastAPI'ye healthcheck ekle, `depends_on` yerine `depends_on.condition: service_healthy` kullan.

## Cut List (MVP'den Atılacaklar)

1. **Phase 6: UI** - Optional zaten, MVP'de gereksiz.
2. **`/ingest/webhook` endpoint** - Webhook entegrasyonu sonra.
3. **`/scan/bulk` endpoint** - Sequential bulk processing riskli, async queue sonra.
4. **`POST /export` endpoint** - CSV export sonra, `/leads` JSON yeterli.
5. **`scripts/demo_run.sh`** - Gereksiz, README'de curl örnekleri yeterli.
6. **`app/core/exporter.py`** - Export endpoint'i ile birlikte çıkar.

## Quick Wins (≤1 Gün)

1. **`/healthz` endpoint** - 30 dk. DB connection check ile.
2. **`providers.json` ve `rules.json` örnek içerik** - 1 saat. 10 provider, 5-7 rule.
3. **Domain normalization unit test** - 30 dk. Edge case'ler (www, punycode, email).
4. **Docker Compose healthcheck düzeltmesi** - 15 dk. FastAPI healthcheck ekle.
5. **`.env.example` validation** - 15 dk. Pydantic Settings ile required field check.
6. **README.md minimal setup** - 30 dk. 3 komut: clone, setup_dev.sh, curl test.

## Open Questions

1. **WHOIS timeout değeri?** Plan'da belirtilmemiş. Öneri: 5s (DNS'ten daha kısa).
2. **Segment override vs normal score?** `score_override=55` kullanılınca normal scoring skip edilecek mi? Öneri: Evet, override varsa normal scoring skip.
3. **`leads_ready` VIEW içeriği?** Plan'da VIEW var ama SELECT içeriği belirsiz. Öneri: Company + DomainSignal + LeadScore JOIN.
4. **CSV ingestion validation?** Domain format validation yapılacak mı? Öneri: Evet, regex ile domain format check.
5. **Bulk scan için rate-limit?** MVP'de bulk yok ama sonra için: 10 domain/dk? Öneri: Post-MVP'de async queue ile.

## Assumption Log

| Assumption | Validation Yolu | Risk |
|------------|----------------|------|
| `python-whois` TLD coverage yeterli | Test: 10 farklı TLD (com, org, net, io, co.uk, de, fr) | Orta |
| DNS timeout 10s yeterli | Test: 50 domain, timeout oranı <%5 olmalı | Düşük |
| Provider mapping %90+ accuracy | Test: 100 domain, manuel doğrulama | Orta |
| PostgreSQL 15-alpine WSL2'de sorunsuz | Test: `docker-compose up` WSL2'de | Düşük |
| FastAPI hot-reload volumes çalışıyor | Test: Kod değişikliği → otomatik reload | Düşük |
| Scoring rules config-driven çalışıyor | Test: `rules.json` değişikliği → restart → yeni skor | Düşük |

## Risk Table

| Risk | Etki | Olasılık | Mitigation | Sahip | Son Tarih |
|------|------|----------|------------|-------|-----------|
| WHOIS rate-limit | Yüksek (scoring eksik) | Orta | WHOIS optional, fail durumunda scoring devam | Dev | G1 |
| DNS timeout >10s | Orta (kullanıcı bekleme) | Düşük | Timeout 10s, error status döndür | Dev | G3 |
| Provider mapping yanlış | Orta (yanlış segment) | Orta | Test: 100 domain manuel doğrulama | Dev | G7 |
| Schema migration fail | Yüksek (setup çalışmaz) | Düşük | Alembic veya Python migration script | Dev | G1 |
| Bulk processing timeout | Yüksek (kullanıcı timeout) | Yüksek | MVP'de bulk çıkar, sadece single domain | Dev | G0 (cut) |
| PII GDPR risk | Yüksek (compliance) | Düşük | Email/company_name nullable, retention policy sonra | Dev | Post-MVP |
| Test coverage yetersiz | Orta (bug'lar production'da) | Orta | Her modül için 3+ edge case testi | Dev | G8-G9 |
| Docker Compose healthcheck eksik | Düşük (manual retry) | Düşük | FastAPI healthcheck ekle | Dev | G1 |

