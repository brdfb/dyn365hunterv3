# HAMLE 2'ye Geçiş Kararı

**Tarih**: 2025-01-30  
**Karar**: HAMLE 1 tamamlandı → HAMLE 2'ye geçildi  
**Format**: Kullanıcının sevdiği format (öneri, neden, risk, alternatif, execution window)

---

## 🧲 Öneri

**HAMLE 2: D365 Phase 2.9 E2E Wiring'e geç.**

Partner Center tarafı şu anda "kod bazında DONE, ürün bazında yeterince iyi" seviyesinde.

---

## 🔍 Neden

1. **Pipeline'ın gerçek değeri = D365'e indiğin anda açılıyor**

   * Şu an Hunter + PC sadece "hazırlık katmanı".
   * Satış için anlamlı olan yer: **lead'in D365 pipeline'a düşmesi**.

2. **HAMLE 1 şu an "riskli değil, eksik testli" durumda**

   * OAuth, flag, initial auth, manual sync, error handling → **kod olarak temiz**.
   * UI JS & error handling senaryoları → **manuel smoke test ile kapanacak**, mimari değişiklik gerektirmiyor.
   * Yani teknik borç **kontrollü**.

3. **Beating dead horse riskini kesiyoruz**

   * Partner Center'da daha fazla oyalanmak = asıl değerli entegrasyon olan D365'i geciktirmek.
   * D365 wiring bittiğinde, PC + Hunter + D365 üçlüsü ilk kez **uçtan uca anlam kazanacak**.

---

## ⚠️ Risk

* **Risk:** UI'da beklenmedik küçük bug çıkarsa sen D365 ile uğraşırken can sıkabilir.
* **Etki:** Medium (kullanıcı tarafında küçük UX bug'ları).
* **Mitigation:**

  * D365'e başlamadan önce **UI için 1 tur XS-S smoke test** (10–20 dk) atarsın:

    * Sync butonu → request gidiyor mu?
    * Referral modal → doğru data'yı gösteriyor mu?
    * Hata halinde toast/snackbar geliyor mu?

---

## 🔁 Alternatif (kısa)

1. **B → A → C Sırası (Safe Mode)**

   * 30–60 dk UI & error handling testlerini yap
   * Sonra HAMLE 2'ye geç
   * En sonda Beat service'i aktif et
   * Daha "kurumsal-safe", biraz daha yavaş

2. **B → C → A (Ops-Öncelikli)**

   * UI test + Beat servisi
   * Sonra D365
   * Bu da olur ama asıl business value'yu (D365) gereksiz geriye atar.

---

## ⏱ Execution Window Tahmini

* **A) D365 Phase 2.9 E2E Wiring:** **M** ( <1 gün net odaklı iş, toplam 1–2 gün takvim )
* **B) UI JS + Error Handling Smoke Test:** **S** (30–60 dk)
* **C) Beat Service Eklemek:** **S** ( <30 dk, mevcut infra hazırsa )

---

### Benim net sıram:

1. **B (S):** 1 sprintlik kahve molası kadar smoke test
2. **A (M):** D365 Phase 2.9 E2E Wiring
3. **C (S):** Beat service, D365 sonrası ops tuning

Ama "tek seçenek söyle" dersen:

👉 **A'yı seçiyorum.**

---

## 📝 Karar

**Seçilen Seçenek:** A (HAMLE 2: D365 Phase 2.9 E2E Wiring)

**Gerekçe:**
- Pipeline'ın gerçek değeri D365'e indiğin anda açılıyor
- HAMLE 1 kod bazında DONE, ürün bazında yeterince iyi seviyesinde
- UI JS & error handling manuel smoke test ile kapanacak (mimari değişiklik gerektirmiyor)
- Beating dead horse riskini kesiyoruz

**Sonraki Adımlar:**
1. Azure AD App Registration oluştur
2. D365 Application User oluştur ve security role ata
3. Hunter config güncelle (`.env` - D365 credentials)
4. Feature flag aktifleştir: `HUNTER_D365_ENABLED=true` (DEV)
5. Manual E2E testler (3 core senaryo):
   - Single lead push test
   - Bulk lead push test
   - Error handling test (auth, rate limit, validation)
6. Go/No-Go gate (Dev → Prod)

**Referans:** `docs/active/D365-PHASE-2.9-E2E-RUNBOOK.md`

---

**Son Güncelleme**: 2025-01-30

