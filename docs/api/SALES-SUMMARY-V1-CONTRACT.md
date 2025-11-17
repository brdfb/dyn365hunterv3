# Sales Summary API – v1 Contract

**Version**: 1.1.0  
**Date**: 2025-01-28  
**Status**: Stable (UI Contract)  
**Breaking Change Policy**: Field names and types are frozen. New fields must be optional and backward-compatible.

---

## Endpoint

```
GET /api/v1/leads/{domain}/sales-summary
GET /leads/{domain}/sales-summary  # Legacy endpoint (backward compatible)
```

### Path Parameters

- `domain` (string, required): Domain name (will be normalized)

### Response

- **Status Code**: `200 OK` (success) or `404 Not Found` (domain not found)
- **Content-Type**: `application/json`
- **Encoding**: UTF-8

---

## Response Schema (JSON)

### Root Object

```json
{
  "domain": "string",
  "one_liner": "string",
  "segment_explanation": "string",
  "provider_reasoning": "string",
  "security_reasoning": {
    "risk_level": "string",
    "summary": "string",
    "details": "string[]",
    "sales_angle": "string",
    "recommended_action": "string"
  } | null,
  "call_script": "string[]",
  "discovery_questions": "string[]",
  "offer_tier": {
    "tier": "string",
    "license": "string",
    "price_per_user_per_month": "number",
    "migration_fee": "number | null",
    "defender_price_per_user_per_month": "number | null",
    "consulting_fee": "number | null",
    "recommendation": "string"
  },
  "opportunity_potential": "number",
  "urgency": "string",
  "metadata": {
    "domain": "string",
    "provider": "string | null",
    "segment": "string | null",
    "readiness_score": "number | null",
    "priority_score": "number | null",
    "tenant_size": "string | null",
    "local_provider": "string | null",
    "generated_at": "string"
  }
}
```

### Field Definitions

#### `domain` (string, required)
- Domain name (normalized)
- Example: `"example.com"`

#### `one_liner` (string, required)
- One-sentence sales summary
- Language: Turkish
- Example: `"example.com - Migration fırsatı, yüksek hazırlık skoru (85), Enterprise teklif hazırlanabilir."`

#### `segment_explanation` (string, required)
- Human-readable explanation for segment classification
- Language: Turkish
- Explains why a lead belongs to Migration, Existing, Cold, or Skip segment
- Example: `"Bu lead **Migration** segmentinde çünkü: Şu anda TürkHost gibi yerel bir hosting sağlayıcısı kullanıyor..."`

#### `provider_reasoning` (string, required)
- Human-readable explanation for provider classification
- Language: Turkish
- Explains why an email provider is classified as M365, Google, Hosting, Local, or Unknown
- Example: `"Bu lead **Microsoft 365 (M365)** kullanıyor çünkü: MX kayıtları outlook.com adresine işaret ediyor..."`

#### `security_reasoning` (object | null, required)
- Security risk assessment with sales angle and recommended action
- Returns `null` if all security signals are unknown/None
- **Fields**:
  - `risk_level` (string, required): `"high" | "medium" | "low"`
  - `summary` (string, required): Short summary in Turkish
  - `details` (array of strings, required): List of security issues found
  - `sales_angle` (string, required): Sales conversation angle
  - `recommended_action` (string, required): Recommended action for sales rep
- **Example**:
  ```json
  {
    "risk_level": "high",
    "summary": "DMARC yok, SPF ve DKIM eksik. Spoofing ve phishing riski yüksek.",
    "details": ["SPF kaydı eksik", "DKIM kaydı eksik", "DMARC politikası yok"],
    "sales_angle": "Güvenlik açığı üzerinden konuşma aç: phishing, sahte fatura, iç yazışma taklidi.",
    "recommended_action": "Microsoft 365 + Defender ile DMARC/SPF/DKIM tam koruma öner."
  }
  ```

#### `call_script` (array of strings, required)
- Call script bullets for sales outreach
- Language: Turkish
- Minimum length: 1
- Example: `["Merhaba, example.com için email altyapınızı inceledik...", "..."]`

#### `discovery_questions` (array of strings, required)
- Discovery questions for sales qualification
- Language: Turkish
- Minimum length: 1
- Example: `["Şu anki email altyapınızdan memnun musunuz?", "..."]`

#### `offer_tier` (object, required)
- Offer tier recommendation

**Fields:**
- `tier` (string, required): `"Business Basic" | "Business Standard" | "Enterprise"`
- `license` (string, required): License type (same as tier)
- `price_per_user_per_month` (number, required): Price in EUR
- `migration_fee` (number | null): One-time migration fee in EUR
- `defender_price_per_user_per_month` (number | null): Defender price in EUR per user per month
- `consulting_fee` (number | null): One-time consulting fee in EUR
- `recommendation` (string, required): Human-readable recommendation

**Example:**
```json
{
  "tier": "Enterprise",
  "license": "Enterprise",
  "price_per_user_per_month": 20,
  "migration_fee": 10000,
  "defender_price_per_user_per_month": 10,
  "consulting_fee": 50000,
  "recommendation": "Enterprise çözümü önerilir. Büyük ölçekli organizasyonlar için Defender ve Consulting hizmetleri dahil."
}
```

#### `opportunity_potential` (number, required)
- Opportunity potential score (0-100)
- Higher = better opportunity
- Interpretation:
  - `70-100`: High priority, immediate action
  - `50-69`: Medium priority, follow up within 1 week
  - `30-49`: Low priority, long-term nurture
  - `0-29`: Very low priority, quarterly check

#### `urgency` (string, required)
- Urgency level: `"low" | "medium" | "high"`
- Interpretation:
  - `high`: Immediate action required (priority 1, domain expiring soon, etc.)
  - `medium`: Follow up within 1 week
  - `low`: Long-term nurture

#### `metadata` (object, required)
- Additional metadata for debugging and context

**Fields:**
- `domain` (string, required): Domain name
- `provider` (string | null): Provider name (`"M365" | "Google" | "Local" | "Yandex" | "Unknown" | null`)
- `segment` (string | null): Lead segment (`"Migration" | "Existing" | "Cold" | "Skip" | null`)
- `readiness_score` (number | null): Readiness score (0-100)
- `priority_score` (number | null): Priority score (1-7, 1 is highest)
- `tenant_size` (string | null): Tenant size (`"small" | "medium" | "large" | null`)
- `local_provider` (string | null): Local provider name (e.g., `"TürkHost"`, `"Natro"`)
- `generated_at` (string, required): ISO 8601 timestamp

**Example:**
```json
{
  "domain": "example.com",
  "provider": "Local",
  "segment": "Migration",
  "readiness_score": 85,
  "priority_score": 1,
  "tenant_size": "large",
  "local_provider": "TürkHost",
  "generated_at": "2025-01-28T12:00:00.000000"
}
```

---

## Breaking Change Rules

### ❌ FORBIDDEN Changes

1. **Field Names**: Cannot be renamed or removed
   - ❌ `domain` → `domain_name`
   - ❌ Remove `one_liner`

2. **Field Types**: Cannot be changed
   - ❌ `opportunity_potential: number` → `opportunity_potential: string`
   - ❌ `call_script: string[]` → `call_script: string`

3. **Required Fields**: Cannot become optional (backward compatible)
   - ❌ `domain: required` → `domain: optional`

4. **Enum Values**: Cannot be removed (can be extended)
   - ❌ Remove `"Business Basic"` from `offer_tier.tier`
   - ❌ Remove `"low"` from `urgency`

### ✅ ALLOWED Changes

1. **New Optional Fields**: Can be added if optional
   ```json
   {
     "domain": "...",
     "new_field": "optional value"  // ✅ OK if optional
   }
   ```

2. **Extended Enums**: Can add new values
   - ✅ Add `"Business Premium"` to `offer_tier.tier`
   - ✅ Add `"critical"` to `urgency` (but keep `low/medium/high`)

3. **Nested Object Extensions**: Can add new fields to nested objects if optional
   ```json
   {
     "offer_tier": {
       "tier": "...",
       "new_field": "optional"  // ✅ OK if optional
     }
   }
   ```

4. **Response Enhancements**: Can add new top-level optional fields
   ```json
   {
     "domain": "...",
     "sales_notes": "optional"  // ✅ OK if optional
   }
   ```

---

## Versioning Strategy

### Current Version: v1.0.0

- **Stable**: Field names and types are frozen
- **Backward Compatible**: Legacy endpoint (`/leads/{domain}/sales-summary`) continues to work
- **Future Versions**: New versions will use `/api/v2/leads/{domain}/sales-summary` pattern

### Migration Path

- **v1 → v2**: When breaking changes are needed, create new endpoint
- **Deprecation**: v1 will be supported for at least 6 months after v2 release
- **Announcement**: Breaking changes will be announced 30 days in advance

---

## Error Responses

### 404 Not Found

```json
{
  "detail": "Domain not found: example.com"
}
```

**When**: Domain doesn't exist in database or hasn't been scanned

### 400 Bad Request

```json
{
  "detail": "Invalid domain format"
}
```

**When**: Domain format is invalid (cannot be normalized)

### 500 Internal Server Error

```json
{
  "detail": "Internal server error: ..."
}
```

**When**: Unexpected server error (should be logged and investigated)

---

## Example Responses

### Migration Segment (High Score, Large Tenant)

```json
{
  "domain": "example.com",
  "one_liner": "example.com - Büyük ölçekli migration fırsatı, yüksek hazırlık skoru (85), Enterprise teklif hazırlanabilir.",
  "call_script": [
    "Merhaba, example.com için email altyapınızı inceledik. Şu anda TürkHost kullanıyorsunuz ve Microsoft 365'e geçiş için uygun bir fırsat görüyoruz.",
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
  "opportunity_potential": 89,
  "urgency": "high",
  "metadata": {
    "domain": "example.com",
    "provider": "Local",
    "segment": "Migration",
    "readiness_score": 85,
    "priority_score": 1,
    "tenant_size": "large",
    "local_provider": "TürkHost",
    "generated_at": "2025-01-28T12:00:00.000000"
  }
}
```

### Existing Segment (Medium Tenant)

```json
{
  "domain": "existing.com",
  "one_liner": "existing.com - Mevcut müşteri, yüksek skor (75), Defender veya ek güvenlik çözümleri için upsell fırsatı.",
  "call_script": [
    "Merhaba, existing.com için mevcut Microsoft 365 altyapınızı inceledik ve güvenlik iyileştirmeleri için önerilerimiz var.",
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
  "opportunity_potential": 79,
  "urgency": "medium",
  "metadata": {
    "domain": "existing.com",
    "provider": "M365",
    "segment": "Existing",
    "readiness_score": 75,
    "priority_score": 3,
    "tenant_size": "medium",
    "local_provider": null,
    "generated_at": "2025-01-28T12:00:00.000000"
  }
}
```

### Cold Segment (Small Tenant)

```json
{
  "domain": "cold.com",
  "one_liner": "cold.com - Soğuk lead, orta skor (45), uzun vadeli takip edilebilir.",
  "call_script": [
    "Merhaba, cold.com için email güvenliği ve altyapı analizi yaptık ve sizinle paylaşmak istediğimiz önemli bulgular var.",
    "Detaylı analiz sonuçlarını paylaşmak için kısa bir görüşme yapabilir miyiz?"
  ],
  "discovery_questions": [
    "Email altyapınız hakkında genel olarak ne düşünüyorsunuz?",
    "Güvenlik ve email yönetimi konusunda öncelikleriniz neler?",
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
    "recommendation": "Business Basic çözümü önerilir. Başlangıç için maliyet-etkin çözüm."
  },
  "opportunity_potential": 39,
  "urgency": "low",
  "metadata": {
    "domain": "cold.com",
    "provider": "Local",
    "segment": "Cold",
    "readiness_score": 45,
    "priority_score": 5,
    "tenant_size": null,
    "local_provider": null,
    "generated_at": "2025-01-28T12:00:00.000000"
  }
}
```

---

## Frontend TypeScript Interface

```typescript
export interface SalesSummary {
  domain: string;
  one_liner: string;
  call_script: string[];
  discovery_questions: string[];
  offer_tier: {
    tier: 'Business Basic' | 'Business Standard' | 'Enterprise';
    license: string;
    price_per_user_per_month: number;
    migration_fee: number | null;
    defender_price_per_user_per_month: number | null;
    consulting_fee: number | null;
    recommendation: string;
  };
  opportunity_potential: number;
  urgency: 'low' | 'medium' | 'high';
  metadata: {
    domain: string;
    provider: string | null;
    segment: 'Migration' | 'Existing' | 'Cold' | 'Skip' | null;
    readiness_score: number | null;
    priority_score: number | null;
    tenant_size: 'small' | 'medium' | 'large' | null;
    local_provider: string | null;
    generated_at: string;
  };
}
```

---

## Testing

### Contract Tests

All contract tests are in `tests/test_sales_summary_api.py`:

- ✅ Response shape validation
- ✅ Field type validation
- ✅ Required field validation
- ✅ Enum value validation
- ✅ Edge cases (minimal data, not found)

### Manual Testing

Use the smoke test script:

```bash
./scripts/smoke_test_sales_engine.sh
```

---

## Related Documentation

- `docs/active/SALES-ENGINE-EXPECTED-OUTPUTS.md` - Expected output skeletons
- `docs/active/SALES-ENGINE-REAL-WORLD-SMOKE-1.md` - Real-world test results
- `app/core/sales_engine.py` - Implementation
- `app/api/sales_summary.py` - API endpoint

---

## Changelog

### v1.1.0 (2025-01-28) - Intelligence Layer
- **Added**: `segment_explanation` field - Explains why a lead belongs to a segment
- **Added**: `provider_reasoning` field - Explains why a provider is classified as such
- **Added**: `security_reasoning` field - Risk assessment with sales angle and recommended action
- **Enhanced**: `call_script` - Cold segment now gets soft, discovery-focused script (v1.1)
- All new fields are optional and backward-compatible
- See `docs/active/SALES-ENGINE-V1.1.md` for detailed feature documentation

### v1.0.0 (2025-01-28)
- Initial stable release
- All fields frozen
- Breaking change policy established

