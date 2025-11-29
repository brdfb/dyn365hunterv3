# Tools Usage Guide

**Tarih**: 2025-01-30  
**Versiyon**: v1.0.0

---

## 📋 Genel Bakış

Container içinde çalışması gereken Python utility scriptleri `app/tools/` klasörü altında bulunur. Bu scriptler Docker image build edilirken otomatik olarak dahil edilir (`app/` klasörü kopyalandığı için).

---

## 🔧 Kullanılabilir Tools

### 1. Partner Center Device Code Flow

**Amaç**: Partner Center için ilk authentication (Device Code Flow)

**Kullanım**:
```bash
docker-compose exec api python -m app.tools.partner_center_device_code_flow
```

**Ne Zaman Kullanılır**:
- Partner Center entegrasyonu ilk kez aktifleştirildiğinde
- Token cache kaybolduğunda veya geçersiz olduğunda
- Authentication sorunlarını debug etmek için

**Not**: Bu script sadece **ilk authentication** için kullanılır. Normal akışta background sync otomatik olarak silent token acquisition kullanır.

---

### 2. Partner Center Manual Sync

**Amaç**: Partner Center referral'larını manuel olarak sync etmek

**Kullanım**:
```bash
docker-compose exec api python -m app.tools.sync_partner_center
```

**Ne Zaman Kullanılır**:
- Background sync çalışmıyorsa
- Hızlı bir test sync yapmak istediğinizde
- Debug amaçlı

---

### 3. D365 Smoke Test

**Amaç**: D365 configuration ve authentication'ı test etmek

**Kullanım**:
```bash
docker-compose exec api python -m app.tools.d365_smoketest
```

**Ne Zaman Kullanılır**:
- D365 entegrasyonu ilk kez kurulduğunda
- D365 credential'ları değiştirildiğinde
- Authentication sorunlarını debug etmek için

---

### 4. D365 Error Handling Test

**Amaç**: D365 error handling senaryolarını test etmek

**Kullanım**:
```bash
docker-compose exec api python -m app.tools.test_d365_error_handling
```

**Ne Zaman Kullanılır**:
- Error handling logic'ini test etmek için
- Rate limit, authentication error gibi senaryoları test etmek için

---

## 📁 Dosya Yapısı

```
app/
  tools/
    __init__.py                          # Module initialization
    partner_center_device_code_flow.py  # PC Device Code Flow
    sync_partner_center.py              # PC Manual Sync
    d365_smoketest.py                   # D365 Smoke Test
    test_d365_error_handling.py          # D365 Error Handling Test
```

---

## 🔄 Migration Notu

**Eski Kullanım** (Deprecated):
```bash
docker-compose exec api python scripts/partner_center_device_code_flow.py
docker-compose exec api python -m scripts.sync_partner_center
```

**Yeni Kullanım** (2025-01-30):
```bash
docker-compose exec api python -m app.tools.partner_center_device_code_flow
docker-compose exec api python -m app.tools.sync_partner_center
```

**Neden Değişti**:
- `scripts/` klasörü Docker image'a kopyalanmıyordu
- `app/tools/` klasörü `app/` içinde olduğu için otomatik olarak image'a dahil ediliyor
- Daha tutarlı bir yapı (tüm container içi scriptler `app/` altında)

---

## ✅ Doğrulama

Scriptlerin container içinde çalıştığını doğrulamak için:

```bash
# Container içinde tools klasörünü kontrol et
docker-compose exec api ls -la /app/app/tools/

# Script'i çalıştır
docker-compose exec api python -m app.tools.partner_center_device_code_flow
```

---

**Son Güncelleme**: 2025-01-30  
**Durum**: ✅ **Kalıcı Çözüm Uygulandı**

