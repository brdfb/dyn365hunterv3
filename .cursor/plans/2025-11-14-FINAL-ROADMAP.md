# Final Roadmap - Post-MVP Sprint 2-6

**Tarih**: 2025-11-14  
**Durum**: Planlama Tamamlandı  
**Kapsam**: Post-MVP Sprint 2-6 (G15-G19)

**Referans**: Detaylı plan için `docs/plans/2025-11-14-FINAL-ROADMAP.md` dosyasına bakın.

---

## 🎯 Sprint Özeti

| Sprint | Phase | Odak | Süre | Durum |
|--------|-------|------|------|-------|
| **Sprint 1** | G14 | MVP Kapanış | ✅ | ✅ Completed |
| **Sprint 2** | G15 | Bulk Scan & Async | 1-2 hafta | 📋 Planned |
| **Sprint 3** | G16 | Webhook + Enrichment | 1 hafta | 📋 Planned |
| **Sprint 4** | G17 | Notes/Tags/PDF | 2 hafta | 📋 Planned |
| **Sprint 5** | G18 | ReScan + Alerts | 2 hafta | 📋 Planned |
| **Sprint 6** | G19 | Auth + UI + AI | 2-3 hafta | 📋 Planned |

---

## 📌 Sprint 2 (G15) – Bulk Scan & Async Queue

**Odak**: Core altyapı - Bulk scan için async queue sistemi

**Yapılacaklar:**
- Async queue (Celery / RQ / FastAPI BackgroundTasks)
- Rate limiting (DNS: 10 req/s, WHOIS: 5 req/s)
- Progress tracking (Redis / DB)
- Error handling (partial failure, retry)
- Timeout strategy

**Çıkarılanlar:**
- ❌ Priority Score Engine (zaten var)
- ❌ ReScan Infrastructure (Sprint 5'e taşındı)

---

## 📌 Sprint 3 (G16) – Webhook + Basit Lead Enrichment

**Odak**: Veri akışı - Webhook ingestion + basit lead enrichment

**Yapılacaklar:**
- Webhook endpoint (`POST /ingest/webhook`)
- API Key auth (basit)
- Retry logic
- Lead enrichment (contact_emails, contact_quality_score, linkedin_pattern)

**Çıkarılanlar:**
- ❌ Contact Finder (Sprint 6+'ya taşındı)
- ❌ Auto-tagging (Sprint 4'e taşındı)

---

## 📌 Sprint 4 (G17) – Notes/Tags/Favorites + Basit PDF

**Odak**: CRM-lite - Notes, tags, favorites + satış sunumu

**Yapılacaklar:**
- Notes CRUD
- Tags CRUD + Auto-tagging
- Favorites CRUD (session-based)
- Basit PDF Summary (AI yok)

**Çıkarılanlar:**
- ❌ AI Recommendation (Sprint 6+'ya taşındı)
- ❌ Microsoft Auth (Sprint 6'ya taşındı)

---

## 📌 Sprint 5 (G18) – ReScan + Alerts + Enhanced Scoring

**Odak**: Otomasyon - ReScan jobs + change alerts + enhanced scoring

**Yapılacaklar:**
- ReScan engine
- History tables (signal/score/provider changes)
- Change detection
- Alerts (email/webhook/slack)
- Enhanced scoring (AI yok)
- Daily cron job

**Çıkarılanlar:**
- ❌ AI-enhanced scoring (Sprint 6+'ya taşındı)

---

## 📌 Sprint 6 (G19) – Auth + UI + Advanced Features

**Odak**: Advanced features - Auth, UI upgrade, AI features (optional)

**Yapılacaklar:**
- Microsoft SSO
- UI / Dashboard upgrade
- AI Features (optional)
- Contact Finder (optional)

---

## 🎯 Öncelik Matrisi

| Sprint | Öncelik | Zorluk | Satış Değeri |
|--------|---------|--------|--------------|
| **Sprint 2** | 🔴 Yüksek | 🔴 Yüksek | ⭐⭐⭐ Yüksek |
| **Sprint 3** | 🔴 Yüksek | 🟡 Orta | ⭐⭐⭐ Yüksek |
| **Sprint 4** | 🔴 Yüksek | 🟡 Orta | ⭐⭐⭐ Yüksek |
| **Sprint 5** | 🟡 Orta | 🔴 Yüksek | ⭐⭐ Orta |
| **Sprint 6** | 🟢 Düşük | 🔴 Yüksek | ⭐⭐ Orta |

---

**Detaylı plan**: `docs/plans/2025-11-14-FINAL-ROADMAP.md`  
**TODO dosyaları**: `docs/todos/G15-G19-*.md`

