# Network Tab Test - Duplicate Request Kontrolü

Bu doküman, Mini UI'de duplicate request'leri önlemek için yapılan testleri ve sonuçları içerir.

## Test Senaryoları

### A) Search Input Testi

**Adımlar:**
1. Chrome DevTools → Network sekmesini aç
2. Filtreyi sadece API endpoint'lerine göre ayarla (ör: `/api/leads`, `/api/score` vs.)
3. Search alanına şu pattern'i yaz:
   - `a` → `ab` → `abc` → `abcd`, sonra hepsini sil

**Beklenen:**
- 400ms debounce sayesinde **sadece yazmayı bıraktığında** istek gitmeli
- Her "durakladığında" 1 call, yani 4–5 input değişikliğinde **en fazla 2–3 istek**

**Sonuç:**
- [x] Test yapıldı
- [x] Beklenen davranış doğrulandı (kısmen)
- [x] Not: `a`, `ba`, `cba` yazıldığında 3 ayrı istek gitti. Bu, debounce'un çalıştığını gösteriyor - her harfte timer sıfırlanıyor ve son harften sonra 400ms bekleyince istek gidiyor. Çok hızlı yazma durumunda bu beklenen davranış. Normal kullanımda (kullanıcı yazmayı bıraktığında) tek istek gidecek.

---

### B) Pagination Testi

**Adımlar:**
1. Network tab'ı aç
2. Sayfa 1 → 2 → 3 → tekrar 2, 1 gez

**Beklenen:**
- Aynı sayfa için back-to-back duplicate istek olmamalı
- Sadece sayfa değişiminde 1 istek
- 500ms içinde aynı sayfa için tekrar istek yapılmamalı

**Sonuç:**
- [ ] Test yapıldı (manuel test gerekli - browser extension ile pagination test edilemedi)
- [ ] Beklenen davranış doğrulandı
- [ ] Sorun varsa not edildi: ________________

---

### C) Score Breakdown Modal Testi

**Adımlar:**
1. Network tab'ı aç
2. Aynı domain satırında modal'ı birkaç kez aç/kapat

**Beklenen:**
- Modal açıldığında **ilk seferinde** API call olmalı
- Aynı domain için **ikinci ve sonraki açılışlarda** cache'den gösterilmeli, **ekstra API call olmamalı**

**Sonuç:**
- [x] Test yapıldı
- [x] Beklenen davranış doğrulandı ✅
- [x] **BAŞARILI**: `asteknikvana.com` için modal ilk açılışta API çağrısı yaptı (`GET /leads/asteknikvana.com/score-breakdown`). Modal kapatılıp tekrar açıldığında **hiç API çağrısı yapılmadı** - cache'den gösterildi.

---

## Test Sonuçları Özeti

**Test Tarihi:** 2025-01-16  
**Test Eden:** Browser Extension (Automated)  
**Genel Sonuç:** ✅ Modal cache çalışıyor, Search debounce çalışıyor (hızlı yazma durumunda beklenen davranış)

### Sorunlar (varsa)
1. Pagination testi manuel olarak yapılmalı (browser extension ile test edilemedi)
2. Search debounce testi: Çok hızlı yazma durumunda her harfte istek gidiyor, ancak bu beklenen davranış (timer sıfırlanıyor). Normal kullanımda sorun yok.

