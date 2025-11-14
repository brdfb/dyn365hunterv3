# TODO: Sprint 5 (G18) - ReScan + Alerts + Enhanced Scoring

**Date Created**: 2025-11-14  
**Status**: 📋 Planned  
**Phase**: G18 (Post-MVP Sprint 5)  
**Süre**: 2 hafta

---

## 🎯 Sprint Hedefi

Otomasyon - ReScan jobs + change alerts + enhanced scoring (AI olmadan).

**Strateji**: Bulk scan bittikten sonra tarama otomasyonu yapılır. AI-enhanced scoring çıkarıldı (kritik değerlendirme sonrası).

---

## 📋 Tasks

### ReScan Infrastructure

- [ ] Schema değişikliği (history tables)
  - [ ] `signal_change_history` tablosu:
    - `id`, `domain`, `signal_type` (spf, dkim, dmarc, mx), `old_value`, `new_value`, `changed_at`
  - [ ] `score_change_history` tablosu:
    - `id`, `domain`, `old_score`, `new_score`, `old_segment`, `new_segment`, `changed_at`
  - [ ] `provider_change_history` tablosu (zaten var, genişletilecek)
  - [ ] Migration script

- [ ] ReScan engine
  - [ ] Manual trigger: `POST /scan/{domain}/rescan`
  - [ ] Bulk rescan: `POST /scan/bulk/rescan?domain_list=...`
  - [ ] Change detection logic:
    - Compare old vs new signals
    - Compare old vs new scores
    - Compare old vs new provider

### Change Detection

- [ ] MX change detection
  - [ ] MX records comparison
  - [ ] MX root change detection
  - [ ] Alert trigger

- [ ] DMARC change detection
  - [ ] DMARC policy comparison
  - [ ] DMARC none → quarantine/reject detection
  - [ ] Alert trigger

- [ ] Domain expiry detection
  - [ ] Expires_at < 30 days detection
  - [ ] Alert trigger

- [ ] Score change detection
  - [ ] Priority score değişti detection
  - [ ] Segment değişti detection
  - [ ] Alert trigger

### Alerts System

- [ ] Notification engine
  - [ ] Email notifications (SMTP)
  - [ ] Webhook notifications
  - [ ] Slack notifications (optional)

- [ ] Alert triggers
  - [ ] MX changed → alert
  - [ ] DMARC added → alert
  - [ ] Domain expire soon → alert
  - [ ] Priority score changed → alert

- [ ] Alert configuration
  - [ ] Alert preferences (email/webhook/slack)
  - [ ] Alert frequency (immediate/daily digest)

### Enhanced Scoring (AI Yok)

- [ ] Signal-based scoring improvements
  - [ ] DKIM none penalty (mevcut scorer'a ekle)
  - [ ] SPF include count (multiple includes = risk)
  - [ ] DMARC none penalty (mevcut scorer'a ekle)
  - [ ] Enhanced risk scoring

- [ ] **AI-enhanced scoring YOK** (Sprint 6+)

### Scheduler

- [ ] Daily ReScan cron job
  - [ ] Celery beat veya APScheduler setup
  - [ ] Daily schedule (configurable)
  - [ ] Background worker setup

- [ ] Configurable schedule
  - [ ] Daily, weekly, monthly options
  - [ ] Schedule configuration endpoint

### API Endpoints

- [ ] `POST /scan/{domain}/rescan` - Manual rescan
- [ ] `POST /scan/bulk/rescan` - Bulk rescan
- [ ] `GET /alerts` - List alerts
- [ ] `POST /alerts/config` - Alert configuration

### Testing

- [ ] Unit tests
  - [ ] ReScan engine tests
  - [ ] Change detection tests
  - [ ] Alert trigger tests
  - [ ] Enhanced scoring tests

- [ ] Integration tests
  - [ ] ReScan end-to-end test
  - [ ] Change detection end-to-end test
  - [ ] Alert system end-to-end test

### Documentation

- [ ] API documentation
  - [ ] ReScan endpoints docs
  - [ ] Alert system docs
  - [ ] Scheduler configuration docs

- [ ] README.md güncellemesi
  - [ ] ReScan kullanımı
  - [ ] Alert configuration

- [ ] CHANGELOG.md güncellemesi
  - [ ] G18: ReScan + Alerts + Enhanced Scoring added

---

## ✅ Acceptance Criteria

- [ ] ReScan engine çalışıyor (manual + bulk)
- [ ] Change detection çalışıyor (MX, DMARC, expiry, score)
- [ ] Alerts çalışıyor (email/webhook)
- [ ] Enhanced scoring çalışıyor (AI olmadan)
- [ ] Daily cron job çalışıyor
- [ ] Tests passing (≥10 test cases)

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
**Sprint Başlangıç**: TBD  
**Sprint Bitiş**: TBD

