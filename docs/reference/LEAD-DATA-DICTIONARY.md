# 📚 Lead Table - Full Data Dictionary (Hunter CORE)

**Version:** v1.1  
**Last Updated:** 2025-01-30  
**Entity:** Lead (Dynamics 365 Sales)  
**Publisher Prefix:** `hnt_` (Custom Hunter fields - **CONFIRMED**)

---

## 📋 İçindekiler

1. [Core D365 Fields](#1-core-d365-fields)
2. [Hunter Intelligence Fields](#2-hunter-intelligence-fields)
3. [Partner Center Fields](#3-partner-center-fields)
4. [Sync & Operations Fields](#4-sync--operations-fields)
5. [Field Mapping Reference](#5-field-mapping-reference)

---

## 1. Core D365 Fields

### Business Card Section

| Display Name | Logical Name | Data Type | Required Level | Max Length | Description |
| ------------ | ------------ | --------- | -------------- | ---------- | ----------- |
| **Topic** | `subject` | Single Line of Text | Business Required | 200 | Lead başlığı (ör: "M365 migration – XYZ") |
| **Company Name** | `companyname` | Single Line of Text | Business Required | 100 | Firma adı (grid'de "Name" olarak da kullanılır) |
| **Company Email** | `emailaddress1` | Email | None | 100 | Şirketin genel e-postası (info@, sales@ vb.) |
| **Website** | `websiteurl` | URL | None | 200 | Firmanın web adresi |
| **Business Phone** | `telephone1` | Phone | None | 50 | Ana firma telefonu |

### Contact Details Section

| Display Name | Logical Name | Data Type | Required Level | Max Length | Description |
| ------------ | ------------ | --------- | -------------- | ---------- | ----------- |
| **First Name** | `firstname` | Single Line of Text | Business Required | 50 | Kişinin adı |
| **Last Name** | `lastname` | Single Line of Text | Business Required | 50 | Soyadı |
| **Job Title** | `jobtitle` | Single Line of Text | None | 100 | Ünvan (IT Manager, CEO vb) |
| **Email** | `emailaddress1` | Email | None | 100 | Kişinin e-postası |
| **Mobile Phone** | `mobilephone` | Phone | None | 50 | Mobil telefon |

### Address Section

| Display Name | Logical Name | Data Type | Required Level | Max Length | Description |
| ------------ | ------------ | --------- | -------------- | ---------- | ----------- |
| **Street 1** | `address1_line1` | Single Line of Text | None | 250 | Adres satırı 1 |
| **Street 2** | `address1_line2` | Single Line of Text | None | 250 | Adres satırı 2 |
| **Street 3** | `address1_line3` | Single Line of Text | None | 250 | Adres satırı 3 |
| **City** | `address1_city` | Single Line of Text | None | 80 | Şehir |
| **State/Province** | `address1_stateorprovince` | Single Line of Text | None | 50 | Eyalet/İl |
| **ZIP/Postal Code** | `address1_postalcode` | Single Line of Text | None | 20 | Posta kodu |
| **Country/Region** | `address1_country` | Single Line of Text | None | 80 | Ülke |

### Header Fields

| Display Name | Logical Name | Data Type | Required Level | Description |
| ------------ | ------------ | --------- | -------------- | ----------- |
| **Status Reason** | `statuscode` | Option Set | Business Required | New / Qualified / Disqualified vb. |
| **Lead Source** | `leadsourcecode` | Option Set | None | Web, Partner, Phone call vs. |
| **Rating** | `leadqualitycode` | Option Set | None | Warm / Hot / Cold |
| **Owner** | `ownerid` | Lookup (User/Team) | Business Required | Lead sahibi |

### Description

| Display Name | Logical Name | Data Type | Required Level | Max Length | Description |
| ------------ | ------------ | --------- | -------------- | ---------- | ----------- |
| **Description** | `description` | Multiple Lines of Text | None | Unlimited | Özet not, hikâye, deal context |

---

## 2. Hunter Intelligence Fields

**Section:** Hunter Intelligence  
**Source:** Custom (Hunter)  
**Used In Forms:** Information (Main), Advanced Debug  
**Used In Views:** My Open Leads, Hunter Intelligence Leads

| Display Name | Logical Name | Data Type | Required Level | Searchable | Description | Source Field (Hunter) |
| ------------ | ------------ | --------- | -------------- | --------- | ----------- | ---------------------- |
| **Hunter Final Score** | `hnt_finalscore` | Whole Number | None | Yes | 0–100 arası final skor. UI'de lead kalitesi için kullanılır. | `readiness_score` |
| **Hunter Priority Score** | `hnt_priorityscore` | Whole Number | None | Yes | İç öncelik skoru (1-7). Queue / job scheduling için kullanılabilir. | `priority_score` |
| **Hunter Segment** | `hnt_segment` | Choice (Option Set) | None | Yes | SMB / Mid / Enterprise vb. segment etiketi. | `segment` |
| **Hunter Provider** | `hnt_provider` | Single Line of Text | None | Yes | Hangi provider'dan geldi (M365, GWS, vb.) | `provider` |
| **Hunter Tenant Size** | `hnt_huntertenantsize` | Choice (Option Set) | None | Yes | Small (1–50), Mid, Large gibi tenant büyüklüğü. | `tenant_size` |
| **Hunter Infrastructure Summary** | `hnt_infrasummary` | Multiple Lines of Text | None | No | Hunter'ın altyapı analizi (MX, SPF, DNS, cloud provider vb. özet). | `infrastructure_summary` |
| **Hunter Confidence** | `hnt_confidence` | Decimal | None | Yes | Skor güven seviyesi (ör: 3.00 gibi decimal görünüyor). | Calculated |

---

## 3. Partner Center Fields

**Section:** Partner Center  
**Source:** Custom (Hunter PC Connector)  
**Used In Forms:** Information (Main)  
**Used In Views:** Partner Center Leads (önerilen)

| Display Name | Logical Name | Data Type | Required Level | Searchable | Description | Source Field (Hunter) |
| ------------ | ------------ | --------- | -------------- | --------- | ----------- | ---------------------- |
| **Hunter Referral ID** | `hnt_referralid` | Single Line of Text | None | Yes | PC referral kaydının ID'si. | `referral_id` |
| **Hunter Referral Type** | `hnt_referraltype` | Choice (Option Set) | None | Yes | Co-sell, marketplace, solution workspace vb. tip. | `referral_type` |
| **Hunter Tenant ID** | `hnt_tenantid` | Single Line of Text | None | Yes | Azure Tenant GUID / ID. | `azure_tenant_id` |
| **Hunter Source** | `hnt_source` | Choice (Option Set) | None | Yes | Skorun kaynağı (Partner Center, Manual, Import vs). | Logic: `"Partner Center" if referral_id else "Manual"` |
| **Hunter M365 Fit Score** | `hnt_m365fitscore` | Whole Number | None | Yes | M365 uyumluluk skorun (fit). | `readiness_score` (if provider == "M365") |
| **Hunter M365 Match Tags** | `hnt_m365matchtags` | Multiple Lines of Text | None | No | M365 workload eşleşme tagleri (Exchange, SharePoint, Teams…). | None (Post-MVP) |

> **Note:** `Hunter Is Partner Center Referral` field not found in D365. May be calculated from `hnt_referralid` (if not null = Yes).

---

## 4. Sync & Operations Fields

**Section:** AI & Sync Analytics  
**Source:** Custom (Hunter)  
**Used In Forms:** Information (Main), Advanced Debug  
**Used In Views:** Hunter Intelligence Leads (önerilen)

| Display Name | Logical Name | Data Type | Required Level | Searchable | Description | Source Field (Hunter) |
| ------------ | ------------ | --------- | -------------- | --------- | ----------- | ---------------------- |
| **D365 Lead ID** | `hnt_d365leadid` | Single Line of Text | None | Yes | Hunter tarafında D365 lead referansını taşır. | D365 Lead GUID |
| **Hunter Last Sync Time** | `hnt_lastsynctime` | Date and Time | None | Yes | Hunter ile en son sync timestamp'i. | `d365_sync_last_at` |
| **Hunter Sync Attempt Count** | `hnt_syncattemptcount` | Whole Number | None | Yes | Kaç defa sync denemesi yapıldığını tutar. | `d365_sync_attempt_count` |
| **Hunter Processing Status** | `hnt_processingstatus` | Choice (Option Set) | None | Yes | Pipeline durumu (Idle, Working, Completed, Error). | `d365_sync_status` (mapped) |
| **Hunter Sync Error Message** | `hnt_syncerrormessage` | Multiple Lines of Text | None | Yes | Son hata mesajı (varsa). | `d365_sync_error` |
| **Hunter Push Status** | `hnt_pushstatus` | Choice (Option Set) | None | Yes | Hunter'dan D365'e push state (synced, not synced, error vs). | Calculated |

---

## 5. Advanced Debug Fields (Technical Only)

**Tab:** Advanced Debug (Technical Only)  
**Source:** Custom (Hunter)  
**Used In Forms:** Advanced Debug tab only  
**Used In Views:** None (technical only)

| Display Name | Logical Name | Data Type | Required Level | Searchable | Description | Source Field (Hunter) |
| ------------ | ------------ | --------- | -------------- | --------- | ----------- | ---------------------- |
| **Hunter AutoScore Version** | `hnt_HunterAutoScoreVersi...` | Single Line of Text | None | Yes | Hangi scoring engine versiyonu kullanıldı (v1, v1.1, v2…). | Version string |
| **Hunter Domain** | `hnt_domain` | Single Line of Text | None | Yes | Analiz edilen domain (xyz.co, abc.com). | `domain` |
| **Hunter Is Re-Enriched** | `hnt_isreenriched` | Yes/No (Boolean) | None | Yes | Bu lead tekrar enrich edildi mi? (Evet/Hayır). | Calculated |
| **Hunter ML Weight JSON** | `hnt_HunterMLWeightJSON` | Multiple Lines of Text | None | No | ML ağırlıklarının ham JSON'ı (feature weights). | ML weights JSON |
| **Hunter Intelligence JSON** | `hnt_intelligencejson` | Multiple Lines of Text | None | Yes | Tam ham JSON payload (debug / data science için). | Full lead JSON |

---

## 6. Field Mapping Reference

### Hunter → D365 Mapping

**File:** `app/integrations/d365/mapping.py`  
**Function:** `map_lead_to_d365(lead_data: Dict[str, Any])`

#### Core Intelligence Mapping

**Note:** Mapping uses logical names with `hnt_` prefix (confirmed from D365)

```python
hunter_fields = {
    "hnt_finalscore": lead_data.get("readiness_score"),  # Hunter Final Score
    "hnt_priorityscore": lead_data.get("priority_score"),  # Hunter Priority Score
    "hnt_segment": lead_data.get("segment"),  # Hunter Segment
    "hnt_provider": lead_data.get("provider"),  # Hunter Provider
    "hnt_huntertenantsize": lead_data.get("tenant_size"),  # Hunter Tenant Size
    "hnt_infrasummary": lead_data.get("infrastructure_summary"),  # Hunter Infrastructure Summary
    "hnt_confidence": calculate_confidence(lead_data),  # Hunter Confidence (calculated)
    # Note: priority_category, priority_label, technical_heat, commercial_segment, commercial_heat
    # not found in D365 - may be calculated or not yet implemented
}
```

#### Partner Center Mapping

```python
referral_id = lead_data.get("referral_id")
if referral_id:
    hunter_fields["hnt_referralid"] = referral_id  # Hunter Referral ID

hunter_fields["hnt_tenantid"] = lead_data.get("azure_tenant_id")  # Hunter Tenant ID
hunter_fields["hnt_referraltype"] = lead_data.get("referral_type")  # Hunter Referral Type
hunter_fields["hnt_source"] = "Partner Center" if referral_id else "Manual"  # Hunter Source
hunter_fields["hnt_m365fitscore"] = (
    lead_data.get("readiness_score") if lead_data.get("provider") == "M365" else None
)  # Hunter M365 Fit Score
# Note: hunter_is_partner_center_referral not found - may be calculated from hnt_referralid
```

#### Sync/Ops Mapping

```python
hunter_fields["hnt_d365leadid"] = d365_lead_id  # D365 Lead ID (from D365 response)
hunter_fields["hnt_lastsynctime"] = lead_data.get("d365_sync_last_at")  # Hunter Last Sync Time
hunter_fields["hnt_syncerrormessage"] = lead_data.get("d365_sync_error")  # Hunter Sync Error Message
hunter_fields["hnt_syncattemptcount"] = lead_data.get("d365_sync_attempt_count")  # Hunter Sync Attempt Count
hunter_fields["hnt_processingstatus"] = _map_processing_status(
    lead_data.get("d365_sync_status")
)  # Hunter Processing Status
hunter_fields["hnt_pushstatus"] = calculate_push_status(lead_data)  # Hunter Push Status (calculated)
```

### Processing Status Mapping

**Function:** `_map_processing_status(sync_status: Optional[str])`

| Hunter Status | D365 Processing Status |
| ------------- | ---------------------- |
| `pending` | `Idle` |
| `in_progress` | `Working` |
| `synced` | `Completed` |
| `error` | `Error` |
| `None` | `Idle` |

---

## 7. Field Summary by Category

### Total Field Count

- **Core D365 Fields:** 20+ (standard Lead entity)
- **Hunter Intelligence Fields:** 7 (confirmed in D365)
- **Partner Center Fields:** 6 (confirmed in D365)
- **Sync & Operations Fields:** 6 (confirmed in D365)
- **Advanced Debug Fields:** 5 (confirmed in D365)

**Total Custom Fields:** 24 (confirmed in D365)

### Field Status

- ✅ **Active (24):** All fields confirmed in D365
- ⚠️ **Missing Fields:** Some fields from mapping.py not found in D365:
  - `hunter_priority_category` (may be calculated or not implemented)
  - `hunter_priority_label` (may be calculated or not implemented)
  - `hunter_technical_heat` (may be calculated or not implemented)
  - `hunter_commercial_segment` (may be calculated or not implemented)
  - `hunter_commercial_heat` (may be calculated or not implemented)
  - `hunter_is_partner_center_referral` (may be calculated from `hnt_referralid`)

---

## 8. Field Naming Convention

### Logical Name Format

- **Custom Fields:** `hnt_<field_name>` (camelCase)
- **Example:** `hnt_finalscore`, `hnt_segment`, `hnt_referralid`

### Display Name Format

- **Format:** `Hunter <Field Name>`
- **Example:** `Hunter Final Score`, `Hunter Segment`

### Publisher Prefix

- **Confirmed Prefix:** `hnt_` (Hunter)
- **Note:** All custom Hunter fields use `hnt_` prefix

---

## 📝 Notlar

- **Logical Names:** All confirmed from D365 Power Apps interface (2025-01-30)
- **Publisher Prefix:** `hnt_` confirmed for all custom Hunter fields
- **Data Types:** D365 data types (Decimal, Whole Number, Single Line of Text, Multiple Lines of Text, Choice, Yes/No, Date and Time)
- **Required Level:** All custom fields are None (not required)
- **Searchable:** Most fields are searchable; some MLT fields are not (for performance)
- **Missing Fields:** Some fields from `mapping.py` not found in D365 (may be calculated or not yet implemented)

---

## 🔄 Güncelleme Geçmişi

- **2025-01-30:** v1.1 - Logical names confirmed from D365 Power Apps interface (`hnt_` prefix), searchable properties added
- **2025-01-30:** v1.0 - İlk versiyon oluşturuldu (mapping.py'den logical name'ler çıkarıldı)

