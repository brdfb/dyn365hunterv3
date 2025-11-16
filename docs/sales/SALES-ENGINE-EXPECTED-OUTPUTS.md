# Sales Engine - Expected Output Skeleton

**Date**: 2025-01-28  
**Purpose**: Expected output skeletons for manual smoke testing  
**Status**: Reference Document

---

## Test Domain Scenarios

### Scenario 1: Migration Segment - High Score, Large Tenant

**Domain**: `migration-test.com` (or real domain)  
**Expected Input**:
- Segment: `Migration`
- Provider: `Local`
- Local Provider: `TürkHost`
- Readiness Score: `85`
- Priority Score: `1`
- Tenant Size: `large`
- SPF: `false`
- DKIM: `false`
- DMARC: `none`
- Contact Quality: `80`
- Expires: `45 days`

**Expected Output Skeleton**:

```json
{
  "domain": "migration-test.com",
  "one_liner": "migration-test.com - Büyük ölçekli migration fırsatı, yüksek hazırlık skoru (85), Enterprise teklif hazırlanabilir.",
  "call_script": [
    "Merhaba, migration-test.com için email altyapınızı inceledik. Şu anda TürkHost kullanıyorsunuz ve Microsoft 365'e geçiş için uygun bir fırsat görüyoruz.",
    "Güvenlik analizi: SPF kaydı eksik, DKIM kaydı eksik, DMARC politikası yok. Bu durum email spoofing ve phishing saldırılarına karşı risk oluşturuyor.",
    "Enterprise çözümümüz ile büyük ölçekli migration yapabilir, IT maliyetlerinizi düşürebilir ve güvenliği artırabiliriz.",
    "15 dakikalık kısa bir görüşme yapabilir miyiz? Size özel bir teklif hazırlayabilirim."
  ],
  "discovery_questions": [
    "Şu anki email altyapınızdan memnun musunuz? Hangi zorluklarla karşılaşıyorsunuz?",
    "Email güvenliği konusunda endişeleriniz var mı? Son dönemde phishing veya spam sorunları yaşadınız mı?",
    "IT ekibinizin büyüklüğü nedir? Email yönetimi için ne kadar zaman harcıyorsunuz?",
    "Local hosting sağlayıcınızdan memnun musunuz? Ölçeklenebilirlik ve güvenlik konusunda endişeleriniz var mı?",
    "Büyük ölçekli bir organizasyonsunuz. Email yönetimi ve güvenlik için merkezi bir stratejiniz var mı?",
    "Compliance ve regülasyon gereksinimleriniz neler? (GDPR, KVKK, vb.)",
    "Email altyapısı için yıllık bütçeniz nedir?",
    "Bu konuda karar verme süreciniz nasıl işliyor? Kimler dahil oluyor?",
    "Zaman çizelgeniz nedir? Acil bir ihtiyaç var mı yoksa planlama aşamasında mısınız?"
  ],
  "offer_tier": {
    "tier": "Enterprise",
    "license": "Enterprise",
    "price_per_user_per_month": 20,
    "migration_fee": 10000,
    "defender_price_per_user_per_month": 10,
    "consulting_fee": 50000,
    "recommendation": "Enterprise çözümü önerilir. Büyük ölçekli organizasyonlar için Defender ve Consulting hizmetleri dahil."
  },
  "opportunity_potential": 88,
  "urgency": "high",
  "metadata": {
    "domain": "migration-test.com",
    "provider": "Local",
    "segment": "Migration",
    "readiness_score": 85,
    "priority_score": 1,
    "tenant_size": "large",
    "local_provider": "TürkHost",
    "generated_at": "2025-01-28T..."
  }
}
```

**Validation Checklist**:
- [ ] Segment = `Migration` ✓
- [ ] Offer Tier = `Enterprise` ✓
- [ ] Opportunity Potential = `70-100` (high) ✓
- [ ] Urgency = `high` (high score + migration) ✓
- [ ] One-liner mentions "Enterprise" or "büyük ölçekli" ✓
- [ ] Call script mentions "TürkHost" ✓
- [ ] Call script mentions security issues (SPF/DKIM/DMARC) ✓
- [ ] Discovery questions include compliance/GDPR for large tenant ✓

---

### Scenario 2: Existing Segment - Medium Score, Medium Tenant

**Domain**: `existing-test.com` (or real domain)  
**Expected Input**:
- Segment: `Existing`
- Provider: `M365`
- Readiness Score: `75`
- Priority Score: `3`
- Tenant Size: `medium`
- SPF: `true`
- DKIM: `true`
- DMARC: `quarantine` (75% coverage)
- Contact Quality: `70`
- Expires: `200 days`

**Expected Output Skeleton**:

```json
{
  "domain": "existing-test.com",
  "one_liner": "existing-test.com - Mevcut müşteri, yüksek skor (75), Defender veya ek güvenlik çözümleri için upsell fırsatı.",
  "call_script": [
    "Merhaba, existing-test.com için mevcut Microsoft 365 altyapınızı inceledik ve güvenlik iyileştirmeleri için önerilerimiz var.",
    "Güvenlik analizi: DMARC kapsamı sadece %75. Bu durum email spoofing ve phishing saldırılarına karşı risk oluşturuyor.",
    "Microsoft Defender for Office 365 ve ek güvenlik çözümlerimiz ile mevcut altyapınızı güçlendirebiliriz.",
    "Mevcut altyapınızı değerlendirmek için kısa bir görüşme yapabilir miyiz?"
  ],
  "discovery_questions": [
    "Mevcut Microsoft 365 altyapınızdan memnun musunuz? Hangi özellikleri kullanıyorsunuz?",
    "Güvenlik konusunda ek ihtiyaçlarınız var mı? Defender veya ek güvenlik çözümleri düşünüyor musunuz?",
    "Email deliverability konusunda sorunlar yaşıyor musunuz? Spam klasörüne düşme oranınız nedir?",
    "Orta ölçekli bir organizasyonsunuz. Büyüme planlarınız var mı? Email altyapınız büyümeye hazır mı?",
    "Email altyapısı için yıllık bütçeniz nedir?",
    "Bu konuda karar verme süreciniz nasıl işliyor? Kimler dahil oluyor?",
    "Zaman çizelgeniz nedir? Acil bir ihtiyaç var mı yoksa planlama aşamasında mısınız?"
  ],
  "offer_tier": {
    "tier": "Business Standard",
    "license": "Business Standard",
    "price_per_user_per_month": 10,
    "migration_fee": 2000,
    "defender_price_per_user_per_month": 5,
    "consulting_fee": null,
    "recommendation": "Business Standard çözümü önerilir. Orta ölçekli organizasyonlar için Defender opsiyonel."
  },
  "opportunity_potential": 65,
  "urgency": "medium",
  "metadata": {
    "domain": "existing-test.com",
    "provider": "M365",
    "segment": "Existing",
    "readiness_score": 75,
    "priority_score": 3,
    "tenant_size": "medium",
    "local_provider": null,
    "generated_at": "2025-01-28T..."
  }
}
```

**Validation Checklist**:
- [ ] Segment = `Existing` ✓
- [ ] Offer Tier = `Business Standard` (medium tenant) ✓
- [ ] Opportunity Potential = `50-80` (medium) ✓
- [ ] Urgency = `medium` (existing + high score) ✓
- [ ] One-liner mentions "upsell" or "Defender" ✓
- [ ] Call script mentions "mevcut Microsoft 365" ✓
- [ ] Call script mentions DMARC coverage issue ✓
- [ ] Discovery questions focus on upsell/security improvements ✓

---

### Scenario 3: Cold Segment - Low Score, Small Tenant

**Domain**: `cold-test.com` (or real domain)  
**Expected Input**:
- Segment: `Cold`
- Provider: `Google`
- Readiness Score: `40`
- Priority Score: `6`
- Tenant Size: `small`
- SPF: `true`
- DKIM: `false`
- DMARC: `none`
- Contact Quality: `50`
- Expires: `300 days`

**Expected Output Skeleton**:

```json
{
  "domain": "cold-test.com",
  "one_liner": "cold-test.com - Soğuk lead, orta skor (40), uzun vadeli takip edilebilir.",
  "call_script": [
    "Merhaba, cold-test.com için email güvenliği ve altyapı analizi yaptık ve sizinle paylaşmak istediğimiz önemli bulgular var.",
    "Güvenlik analizi: DKIM kaydı eksik, DMARC politikası yok. Bu durum email spoofing ve phishing saldırılarına karşı risk oluşturuyor.",
    "Microsoft 365'e geçiş ile mail deliverability'yi artırabilir, güvenliği iyileştirebilir ve IT maliyetlerinizi düşürebiliriz.",
    "Detaylı analiz sonuçlarını paylaşmak için kısa bir görüşme yapabilir miyiz?"
  ],
  "discovery_questions": [
    "Email altyapınız hakkında genel olarak ne düşünüyorsunuz?",
    "Güvenlik ve email yönetimi konusunda öncelikleriniz neler?",
    "Küçük ölçekli bir organizasyonsunuz. Email yönetimi için ne kadar bütçe ayırıyorsunuz?",
    "Email altyapısı için yıllık bütçeniz nedir?",
    "Bu konuda karar verme süreciniz nasıl işliyor? Kimler dahil oluyor?",
    "Zaman çizelgeniz nedir? Acil bir ihtiyaç var mı yoksa planlama aşamasında mısınız?"
  ],
  "offer_tier": {
    "tier": "Business Basic",
    "license": "Business Basic",
    "price_per_user_per_month": 5,
    "migration_fee": 500,
    "defender_price_per_user_per_month": null,
    "consulting_fee": null,
    "recommendation": "Business Basic çözümü önerilir. Küçük ölçekli organizasyonlar için maliyet-etkin çözüm."
  },
  "opportunity_potential": 35,
  "urgency": "low",
  "metadata": {
    "domain": "cold-test.com",
    "provider": "Google",
    "segment": "Cold",
    "readiness_score": 40,
    "priority_score": 6,
    "tenant_size": "small",
    "local_provider": null,
    "generated_at": "2025-01-28T..."
  }
}
```

**Validation Checklist**:
- [ ] Segment = `Cold` ✓
- [ ] Offer Tier = `Business Basic` (small tenant) ✓
- [ ] Opportunity Potential = `0-50` (low) ✓
- [ ] Urgency = `low` (cold + low priority) ✓
- [ ] One-liner mentions "soğuk lead" or "uzun vadeli" ✓
- [ ] Call script is generic (not segment-specific) ✓
- [ ] Discovery questions are basic/generic ✓

---

## Common Validation Rules

### Offer Tier Logic
- **Large tenant** → Always `Enterprise`
- **Medium tenant** → `Business Standard`
- **Small tenant** → `Business Basic`
- **No tenant size + Migration + High score** → `Business Standard`
- **No tenant size + Low score** → `Business Basic`

### Opportunity Potential Ranges
- **Migration + High score + High priority + Large tenant** → `70-100`
- **Migration + Medium score** → `50-80`
- **Existing + Medium score** → `40-70`
- **Cold + Low score** → `0-50`
- **Skip** → `0-30`

### Urgency Logic
- **Priority 1** → Always `high`
- **Migration + Score >= 80** → `high`
- **Domain expires < 60 days** → `high`
- **Priority 2** → `medium`
- **Migration + Score >= 60** → `medium` (Migration threshold 60)
- **Existing + Score >= 70** → `medium`
- **Domain expires 60-90 days** → `medium`
- **Default** → `low`

### Call Script Requirements
- **Migration segment** → Must mention migration opportunity
- **Local provider** → Must mention provider name (TürkHost, Natro, etc.)
- **Security issues** → Must mention specific issues (SPF/DKIM/DMARC)
- **Existing segment** → Must mention upsell/Defender opportunity
- **All segments** → Must have call-to-action at the end

### Discovery Questions Requirements
- **All segments** → Must include budget question
- **All segments** → Must include timeline question
- **All segments** → Must include decision process question
- **Large tenant** → Must include compliance/GDPR questions
- **Migration segment** → Must include current provider satisfaction question
- **Existing segment** → Must include current M365 usage question

---

## Tuning Notes

### If Offer Tier is Wrong
- Check tenant_size field in database
- Verify segment calculation
- Review `recommend_offer_tier()` logic

### If Opportunity Potential is Off
- Check priority_score calculation
- Verify contact_quality_score
- Review segment weight in `calculate_opportunity_potential()`

### If Urgency is Wrong
- Check domain expiration date
- Verify priority_score
- Review `calculate_urgency()` logic

### If Call Script is Generic/Empty
- Check if security signals are being passed correctly
- Verify local_provider field
- Review `generate_call_script()` logic

### If Discovery Questions are Missing
- Check tenant_size field
- Verify segment
- Review `generate_discovery_questions()` logic

---

## Next Steps After Smoke Test

1. **Document Anomalies**: Note any mismatches between expected and actual outputs
2. **Tuning Session**: Review anomalies and adjust business rules if needed
3. **UI Integration**: Decide where Sales Summary will appear in UI
4. **Logging**: Add telemetry for Sales Summary usage
5. **Configuration**: Consider making thresholds configurable

