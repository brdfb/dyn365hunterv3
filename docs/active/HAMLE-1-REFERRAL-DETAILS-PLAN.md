## Referral Detail Modal Plan

**Date**: 2025-01-30  
**Owner**: Partner Center HAMLE 1  
**Goal**: Tek tıkla Microsoft Partner Center referral detaylarını görüntülemek

### 🎯 Objectives
- Backend'de tek referral detay endpoint'i
- UI'da “Partner Center Detay” butonu
- Modal içinde:
  - Özet alanları (status, substatus, contact, deal info)
  - Ham JSON sekmesi (debug için)

### 📐 Scope
1. **Backend**
   - Endpoint: `GET /api/v1/partner-center/referrals/{referral_id}`
   - Response fields:
     - `referral_id`, `status`, `substatus`, `direction`, `referral_type`
     - `company_name`, `customer_name`, `customer_country`, `organization_size`
     - `contact` -> `name`, `email`, `phone`
     - `details` -> `lead_name`, `lead_id`, `estimated_close_date`, `estimated_value`, `notes`
     - `raw_data` (opsiyonel, admin/debug flag ile döndürülebilir)
   - Error handling:
     - 404 -> referral yok
     - 400 -> feature flag kapalıysa
     - 500 -> DB hatası log

2. **UI**
   - Trigger: `Referrals` tablosunda partner center badge’i olan satırlara `Detay` butonu
   - Modal layout:
     - Header: `Company + referral_id`
     - Body:
       - `Status Badge`, `Substatus Badge`
       - `Contact Info`
       - `Lead Details` (value, close date, notes)
       - Tab/Switch: `Özet` / `Ham JSON`
   - Loading state (spinner) & error toast

3. **Telemetry**
   - `partner_center_detail_opened` log + referral_id
   - API response süresi `window.performance`? (opsiyonel)

### 🛠 Implementation Steps
1. Backend schema + endpoint
2. Mini UI fetch helper (`api.js`)
3. UI component (modal)
4. QA: KOCAELIKAYA örneği ile test

### ✅ Acceptance Criteria
- Butona basınca modal açılıyor, contact email vb. görünür
- Ham JSON sekmesi ile Microsoft datası incelebilir
- Feature flag kapalıysa UI butonu göstermez
- Devtools network’te detail endpoint 200 döner


