# P1 Alembic Migration Hazırlığı

**Tarih**: 2025-01-28  
**Durum**: Hazırlık Tamamlandı  
**Amaç**: Alembic implementasyonuna zemin hazırlamak (read-only analiz)

---

## 📋 Mevcut Migration Dosyaları Analizi

### Toplam: 6 Migration Dosyası

| # | Migration Dosyası | Phase | Tarih | Açıklama |
|---|------------------|------|-------|----------|
| 1 | `g16_webhook_enrichment.sql` | G16 | 2025-11-14 | Webhook + Lead Enrichment |
| 2 | `g17_notes_tags_favorites.sql` | G17 | 2025-11-14 | Notes, Tags, Favorites (CRM-lite) |
| 3 | `g18_rescan_alerts_scoring.sql` | G18 | 2025-11-14 | ReScan + Alerts + Enhanced Scoring |
| 4 | `g19_favorites_migration.sql` | G19 | 2025-01-28 | Favorites Migration (Session → User) |
| 5 | `g19_users_auth.sql` | G19 | 2025-01-28 | Users & Authentication (Microsoft SSO) |
| 6 | `g20_domain_intelligence.sql` | G20 | 2025-01-28 | Domain Intelligence Layer |

---

## 🔍 Migration Detay Analizi

### 1. g16_webhook_enrichment.sql

**İçerik:**
- `ALTER TABLE companies` - 3 yeni kolon ekler:
  - `contact_emails JSONB`
  - `contact_quality_score INTEGER`
  - `linkedin_pattern VARCHAR(255)`
- `CREATE TABLE api_keys` - API key authentication tablosu
- `CREATE TABLE webhook_retries` - Webhook retry mekanizması
- `CREATE INDEX` - 7 index oluşturur
- `DROP VIEW leads_ready` + `CREATE VIEW leads_ready` - View güncelleme (enrichment fields ekler)

**Bağımlılıklar:**
- `companies` tablosu (G2 - schema.sql'de oluşturulmuş)
- `leads_ready` VIEW (G2 - schema.sql'de oluşturulmuş)

**SQLAlchemy Model Karşılığı:**
- `Company` model - `contact_emails`, `contact_quality_score`, `linkedin_pattern` kolonları
- `ApiKey` model (yeni tablo)
- `WebhookRetry` model (yeni tablo)

**Alembic Revision Stratejisi:**
- `alembic revision --autogenerate -m "g16_webhook_enrichment"`
- Manuel kontrol: `ALTER TABLE` ve `CREATE TABLE` komutları

---

### 2. g17_notes_tags_favorites.sql

**İçerik:**
- `CREATE TABLE notes` - User notes tablosu
- `CREATE TABLE tags` - Tags tablosu (many-to-many)
- `CREATE TABLE favorites` - Favorites tablosu (session-based)
- `CREATE INDEX` - 9 index oluşturur
- Foreign key constraints: `companies(domain)` referansı

**Bağımlılıklar:**
- `companies` tablosu (G2 - schema.sql'de oluşturulmuş)

**SQLAlchemy Model Karşılığı:**
- `Note` model (yeni tablo)
- `Tag` model (yeni tablo)
- `Favorite` model (yeni tablo)

**Alembic Revision Stratejisi:**
- `alembic revision --autogenerate -m "g17_notes_tags_favorites"`
- Manuel kontrol: `CREATE TABLE` komutları ve foreign key constraints

---

### 3. g18_rescan_alerts_scoring.sql

**İçerik:**
- `CREATE TABLE signal_change_history` - Signal change history tablosu
- `CREATE TABLE score_change_history` - Score change history tablosu
- `CREATE TABLE alerts` - Alerts tablosu
- `CREATE TABLE alert_config` - Alert configuration tablosu
- `CREATE INDEX` - 12 index oluşturur
- Foreign key constraints: `companies(domain)` referansı

**Bağımlılıklar:**
- `companies` tablosu (G2 - schema.sql'de oluşturulmuş)

**SQLAlchemy Model Karşılığı:**
- `SignalChangeHistory` model (yeni tablo)
- `ScoreChangeHistory` model (yeni tablo)
- `Alert` model (yeni tablo)
- `AlertConfig` model (yeni tablo)

**Alembic Revision Stratejisi:**
- `alembic revision --autogenerate -m "g18_rescan_alerts_scoring"`
- Manuel kontrol: `CREATE TABLE` komutları ve foreign key constraints

---

### 4. g19_favorites_migration.sql

**İçerik:**
- `ALTER TABLE favorites` - `user_id_new INTEGER` kolonu ekler
- `CREATE INDEX` - 1 index oluşturur
- `DROP CONSTRAINT` - Eski unique constraint'i kaldırır
- **NOT**: Bu migration partial - application code migration gerektirir

**Bağımlılıklar:**
- `favorites` tablosu (G17 - g17_notes_tags_favorites.sql'de oluşturulmuş)
- `users` tablosu (G19 - g19_users_auth.sql'de oluşturulmuş) - **DİKKAT**: Foreign key henüz eklenmemiş

**SQLAlchemy Model Karşılığı:**
- `Favorite` model - `user_id_new` kolonu (nullable, migration için)

**Alembic Revision Stratejisi:**
- `alembic revision --autogenerate -m "g19_favorites_migration"`
- Manuel kontrol: `ALTER TABLE` komutları ve constraint değişiklikleri
- **ÖNEMLİ**: Application code migration sonrası cleanup migration'ı gerekli

---

### 5. g19_users_auth.sql

**İçerik:**
- `CREATE TABLE users` - Users tablosu (Microsoft SSO)
- `CREATE INDEX` - 3 index oluşturur

**Bağımlılıklar:**
- Hiçbiri (yeni tablo)

**SQLAlchemy Model Karşılığı:**
- `User` model (yeni tablo)

**Alembic Revision Stratejisi:**
- `alembic revision --autogenerate -m "g19_users_auth"`
- Manuel kontrol: `CREATE TABLE` komutları

**NOT**: `g19_favorites_migration.sql` ile sıralama önemli - `users` tablosu önce oluşturulmalı (foreign key için)

---

### 6. g20_domain_intelligence.sql

**İçerik:**
- `ALTER TABLE domain_signals` - 2 yeni kolon ekler:
  - `local_provider VARCHAR(255)`
  - `dmarc_coverage INTEGER`
- `ALTER TABLE companies` - 1 yeni kolon ekler:
  - `tenant_size VARCHAR(50)`
- `CREATE INDEX` - 3 index oluşturur
- `DROP VIEW leads_ready` + `CREATE VIEW leads_ready` - View güncelleme (yeni kolonlar ekler)

**Bağımlılıklar:**
- `domain_signals` tablosu (G2 - schema.sql'de oluşturulmuş)
- `companies` tablosu (G2 - schema.sql'de oluşturulmuş)
- `leads_ready` VIEW (G16 - g16_webhook_enrichment.sql'de güncellenmiş)

**SQLAlchemy Model Karşılığı:**
- `DomainSignal` model - `local_provider`, `dmarc_coverage` kolonları
- `Company` model - `tenant_size` kolonu

**Alembic Revision Stratejisi:**
- `alembic revision --autogenerate -m "g20_domain_intelligence"`
- Manuel kontrol: `ALTER TABLE` komutları ve VIEW güncelleme

---

## 📊 Migration Dependency Grafiği

```
schema.sql (G2 - Base Schema)
├── g16_webhook_enrichment.sql
│   ├── companies (ALTER TABLE)
│   ├── api_keys (CREATE TABLE)
│   ├── webhook_retries (CREATE TABLE)
│   └── leads_ready (DROP/CREATE VIEW)
│
├── g17_notes_tags_favorites.sql
│   ├── notes (CREATE TABLE → companies FK)
│   ├── tags (CREATE TABLE → companies FK)
│   └── favorites (CREATE TABLE → companies FK)
│
├── g18_rescan_alerts_scoring.sql
│   ├── signal_change_history (CREATE TABLE → companies FK)
│   ├── score_change_history (CREATE TABLE → companies FK)
│   ├── alerts (CREATE TABLE → companies FK)
│   └── alert_config (CREATE TABLE)
│
├── g19_users_auth.sql
│   └── users (CREATE TABLE)
│
├── g19_favorites_migration.sql
│   └── favorites (ALTER TABLE → users FK - deferred)
│
└── g20_domain_intelligence.sql
    ├── domain_signals (ALTER TABLE)
    ├── companies (ALTER TABLE)
    └── leads_ready (DROP/CREATE VIEW)
```

**Sıralama Önemi:**
1. `g19_users_auth.sql` → `g19_favorites_migration.sql` (users tablosu önce oluşturulmalı)
2. `g16_webhook_enrichment.sql` → `g20_domain_intelligence.sql` (leads_ready VIEW güncelleme sırası)

---

## 🗄️ Schema Snapshot Planı

### Mevcut Production Schema (G2 Base + 6 Migration)

**Tablo Listesi:**
1. `raw_leads` (G2 - schema.sql)
2. `companies` (G2 - schema.sql, G16/G20 ALTER)
3. `domain_signals` (G2 - schema.sql, G20 ALTER)
4. `lead_scores` (G2 - schema.sql)
5. `api_keys` (G16)
6. `webhook_retries` (G16)
7. `notes` (G17)
8. `tags` (G17)
9. `favorites` (G17, G19 ALTER)
10. `signal_change_history` (G18)
11. `score_change_history` (G18)
12. `alerts` (G18)
13. `alert_config` (G18)
14. `users` (G19)
15. `provider_change_history` (G2 - schema.sql'de yok, models.py'de var - kontrol et!)

**VIEW Listesi:**
1. `leads_ready` (G2 - schema.sql, G16/G20 güncelleme)

**Index Listesi:**
- Toplam ~40+ index (her tablo için 2-4 index)

---

## 🔄 Base Revision Stratejisi

### Strateji: Autogenerate + Manual Diff

**Adımlar:**

1. **Production DB Schema Snapshot**
   ```bash
   # Production DB'den schema dump al
   docker-compose exec postgres pg_dump -U dyn365hunter -d dyn365hunter --schema-only > schema_snapshot.sql
   ```

2. **Alembic Base Revision Oluştur**
   ```bash
   # Alembic init (ilk kez)
   alembic init alembic
   
   # Base revision oluştur (autogenerate)
   alembic revision --autogenerate -m "base_revision"
   ```

3. **Manuel Diff Kontrolü**
   - `schema_snapshot.sql` ile autogenerated revision'ı karşılaştır
   - Eksik/yanlış tabloları düzelt
   - Index'leri kontrol et
   - VIEW'leri kontrol et

4. **Base Revision Doğrulama**
   ```bash
   # Fresh DB'de test et
   alembic upgrade head
   alembic downgrade base
   alembic upgrade head
   ```

**ÖNEMLİ NOT:**
- Base revision **empty revision değil**, mevcut production schema snapshot'ı olacak
- Tüm 6 migration'ı Alembic revision'lara çevirdikten sonra base revision'dan upgrade path'i test edilmeli

---

## 📝 Migration → Alembic Revision Mapping

| SQL Migration | Alembic Revision | Sıra | Bağımlılık |
|--------------|------------------|------|------------|
| `schema.sql` (G2) | `base_revision` | 0 | None |
| `g16_webhook_enrichment.sql` | `g16_webhook_enrichment` | 1 | base_revision |
| `g17_notes_tags_favorites.sql` | `g17_notes_tags_favorites` | 2 | g16_webhook_enrichment |
| `g18_rescan_alerts_scoring.sql` | `g18_rescan_alerts_scoring` | 3 | g17_notes_tags_favorites |
| `g19_users_auth.sql` | `g19_users_auth` | 4 | g18_rescan_alerts_scoring |
| `g19_favorites_migration.sql` | `g19_favorites_migration` | 5 | g19_users_auth |
| `g20_domain_intelligence.sql` | `g20_domain_intelligence` | 6 | g19_favorites_migration |

**Revision Sırası:**
```
base_revision
  ↓
g16_webhook_enrichment
  ↓
g17_notes_tags_favorites
  ↓
g18_rescan_alerts_scoring
  ↓
g19_users_auth
  ↓
g19_favorites_migration
  ↓
g20_domain_intelligence (head)
```

---

## ⚠️ Özel Durumlar ve Dikkat Edilmesi Gerekenler

### 1. VIEW Güncellemeleri
- `leads_ready` VIEW 3 kez güncelleniyor:
  - G2 (schema.sql) - Base
  - G16 (g16_webhook_enrichment.sql) - Enrichment fields
  - G20 (g20_domain_intelligence.sql) - Intelligence fields
- Alembic'te VIEW migration'ları manuel olarak yönetilmeli (autogenerate VIEW'leri algılamayabilir)

### 2. Partial Migration (g19_favorites_migration.sql)
- Bu migration application code migration gerektirir
- Foreign key constraint henüz eklenmemiş (deferred)
- Cleanup migration'ı gerekli (user_id drop, user_id_new → user_id rename)

### 3. Provider Change History Tablosu
- `schema.sql`'de yok ama `models.py`'de `ProviderChangeHistory` model var
- Kontrol et: Bu tablo başka bir migration'da mı oluşturulmuş?
- Yoksa Alembic base revision'da eklenmeli

### 4. Index İsimleri
- Bazı migration'larda `IF NOT EXISTS` kullanılıyor
- Alembic autogenerate index'leri algılayabilir ama isimleri kontrol et

---

## ✅ Hazırlık Checklist

- [x] Tüm migration dosyaları analiz edildi (6 dosya)
- [x] Migration dependency grafiği çıkarıldı
- [x] SQLAlchemy model karşılıkları belirlendi
- [x] Base revision stratejisi dokümante edildi
- [x] Migration → Alembic revision mapping hazırlandı
- [x] Özel durumlar ve dikkat edilmesi gerekenler listelendi

---

## 🚀 Sonraki Adımlar

1. **Alembic Setup**
   - `alembic init alembic`
   - `alembic.ini` config düzenle
   - `alembic/env.py` düzenle (SQLAlchemy models import)

2. **Base Revision Oluştur**
   - Production DB schema snapshot al
   - `alembic revision --autogenerate -m "base_revision"`
   - Manuel diff kontrolü

3. **Migration'ları Alembic Revision'lara Çevir**
   - Her migration için `alembic revision --autogenerate` veya manuel revision
   - Dependency sırasına göre revision'ları oluştur

4. **Test**
   - Fresh DB'de tüm migration'ları test et
   - Rollback testleri (`alembic downgrade`)
   - Schema drift kontrolü (`alembic --autogenerate --dry-run`)

---

**Referans**: `docs/active/P1-IMPLEMENTATION-PLAYBOOK.md` - Alembic Migration bölümü

