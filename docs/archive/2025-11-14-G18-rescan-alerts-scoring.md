# TODO: Sprint 5 (G18) - ReScan + Alerts + Enhanced Scoring

**Date Created**: 2025-11-14  
**Status**: ✅ Completed  
**Phase**: G18 (Post-MVP Sprint 5)  
**Süre**: 2 hafta

---

## 🎯 Sprint Hedefi

Otomasyon - ReScan jobs + change alerts + enhanced scoring (AI olmadan).

**Strateji**: Bulk scan bittikten sonra tarama otomasyonu yapılır. AI-enhanced scoring çıkarıldı (kritik değerlendirme sonrası).

---

## 📋 Tasks

### ReScan Infrastructure

- [x] Schema değişikliği (history tables)
  - [x] `signal_change_history` tablosu:
    - [x] `id`, `domain`, `signal_type` (spf, dkim, dmarc, mx), `old_value`, `new_value`, `changed_at`
  - [x] `score_change_history` tablosu:
    - [x] `id`, `domain`, `old_score`, `new_score`, `old_segment`, `new_segment`, `changed_at`
  - [x] `provider_change_history` tablosu (zaten var, genişletilecek)
  - [x] Migration script

- [x] ReScan engine
  - [x] Manual trigger: `POST /scan/{domain}/rescan`
  - [x] Bulk rescan: `POST /scan/bulk/rescan?domain_list=...`
  - [x] Change detection logic:
    - [x] Compare old vs new signals
    - [x] Compare old vs new scores
    - [x] Compare old vs new provider

### Change Detection

- [x] MX change detection
  - [x] MX records comparison
  - [x] MX root change detection
  - [x] Alert trigger

- [x] DMARC change detection
  - [x] DMARC policy comparison
  - [x] DMARC none → quarantine/reject detection
  - [x] Alert trigger

- [x] Domain expiry detection
  - [x] Expires_at < 30 days detection
  - [x] Alert trigger

- [x] Score change detection
  - [x] Priority score değişti detection
  - [x] Segment değişti detection
  - [x] Alert trigger

### Alerts System

- [x] Notification engine
  - [x] Email notifications (SMTP placeholder)
  - [x] Webhook notifications
  - [x] Slack notifications (optional)

- [x] Alert triggers
  - [x] MX changed → alert
  - [x] DMARC added → alert
  - [x] Domain expire soon → alert
  - [x] Priority score changed → alert

- [x] Alert configuration
  - [x] Alert preferences (email/webhook/slack)
  - [x] Alert frequency (immediate/daily digest)

### Enhanced Scoring (AI Yok)

- [x] Signal-based scoring improvements
  - [x] DKIM none penalty (mevcut scorer'a ekle)
  - [x] SPF include count (multiple includes = risk)
  - [x] DMARC none penalty (mevcut scorer'a ekle)
  - [x] Enhanced risk scoring

- [x] **AI-enhanced scoring YOK** (Sprint 6+)

### Scheduler

- [x] Daily ReScan cron job
  - [x] Celery beat veya APScheduler setup
  - [x] Daily schedule (configurable)
  - [x] Background worker setup

- [x] Configurable schedule
  - [x] Daily, weekly, monthly options
  - [x] Schedule configuration endpoint

### API Endpoints

- [x] `POST /scan/{domain}/rescan` - Manual rescan
- [x] `POST /scan/bulk/rescan` - Bulk rescan
- [x] `GET /alerts` - List alerts
- [x] `POST /alerts/config` - Alert configuration

### Testing

- [x] Unit tests
  - [x] ReScan engine tests
  - [x] Change detection tests
  - [x] Alert trigger tests
  - [x] Enhanced scoring tests

- [x] Integration tests
  - [x] ReScan end-to-end test
  - [x] Change detection end-to-end test
  - [x] Alert system end-to-end test

### Documentation

- [x] API documentation
  - [x] ReScan endpoints docs
  - [x] Alert system docs
  - [x] Scheduler configuration docs

- [x] README.md güncellemesi
  - [x] ReScan kullanımı
  - [x] Alert configuration

- [x] CHANGELOG.md güncellemesi
  - [x] G18: ReScan + Alerts + Enhanced Scoring added

---

## ✅ Acceptance Criteria

- [x] ReScan engine çalışıyor (manual + bulk)
- [x] Change detection çalışıyor (MX, DMARC, expiry, score)
- [x] Alerts çalışıyor (email/webhook)
- [x] Enhanced scoring çalışıyor (AI olmadan)
- [x] Daily cron job çalışıyor
- [x] Tests passing (≥10 test cases)

---

## 📝 Notes

### Çıkarılanlar (Kritik Değerlendirme Sonrası)

- ❌ AI-enhanced scoring (Sprint 6+'ya taşındı)
- ❌ Ready-to-Migrate Score v2 (AI-enhanced) → "Enhanced Scoring" (AI olmadan)

### Bağımlılıklar

- ✅ Sprint 2 tamamlandı (bulk scan + async queue)
- ✅ Sprint 4 tamamlandı (tags system)

### Risk Mitigation

- **ReScan**: Bulk scan altyapısı kullanılacak (Sprint 2'de kuruldu)
- **Change detection**: History tables kritik (schema değişikliği gerekli)
- **Alerts**: Email/Webhook basit, Slack optional

---

**Son Güncelleme**: 2025-11-14  
**Sprint Başlangıç**: 2025-11-14  
**Sprint Bitiş**: 2025-11-14  
**Tamamlanma Tarihi**: 2025-11-14

