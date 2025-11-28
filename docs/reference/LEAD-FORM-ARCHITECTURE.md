# 🏗️ Lead Form Architecture Map (Technical Blueprint)

**Version:** v1.1  
**Last Updated:** 2025-01-30  
**Entity:** Lead (Dynamics 365 Sales)  
**Primary Form:** Information (Main Form Type)  
**Publisher Prefix:** `hnt_` (confirmed from D365)

---

## 📋 İçindekiler

1. [Form Overview](#1-form-overview)
2. [Form Tree Structure](#2-form-tree-structure)
3. [Tab Structure](#3-tab-structure)
4. [Section Details](#4-section-details)
5. [Control Types](#5-control-types)
6. [Form Behavior](#6-form-behavior)
7. [Security & Visibility](#7-security--visibility)

---

## 1. Form Overview

### Primary Form

- **Form Name:** Information
- **Form Type:** Main
- **App:** Sales Hub (Dynamics 365 Sales)
- **Purpose:** Primary form for Lead entity in Sales Hub

### Secondary Forms

- **Lead Insights:** AI-powered insights (Sales Insights)
- **Sales Insights:** Sales intelligence panel
- **In Context Form:** Quick create/edit form
- **Lead (Classic):** Legacy form (backward compatibility)

---

## 2. Form Tree Structure

```
Information Form (Main)
│
├── Header (BPF & Quick Actions)
│   ├── Status Reason (Option Set)
│   ├── Lead Source (Option Set)
│   ├── Rating (Option Set)
│   └── Owner (Lookup)
│
├── Tab: General
│   ├── Section: Business Card
│   │   ├── Topic (Text)
│   │   ├── Company Name (Text)
│   │   ├── Company Email (Email)
│   │   ├── Website (URL)
│   │   └── Business Phone (Phone)
│   │
│   ├── Section: Hunter Intelligence
│   │   ├── Hunter Final Score (Whole Number) - `hnt_finalscore`
│   │   ├── Hunter Priority Score (Whole Number) - `hnt_priorityscore`
│   │   ├── Hunter Segment (Choice) - `hnt_segment`
│   │   ├── Hunter Provider (Single Line of Text) - `hnt_provider`
│   │   ├── Hunter Tenant Size (Choice) - `hnt_huntertenantsize`
│   │   ├── Hunter Infrastructure Summary (MLT) - `hnt_infrasummary`
│   │   └── Hunter Confidence (Decimal) - `hnt_confidence`
│   │
│   ├── Section: Partner Center
│   │   ├── Hunter Referral ID (Single Line of Text) - `hnt_referralid`
│   │   ├── Hunter Referral Type (Choice) - `hnt_referraltype`
│   │   ├── Hunter Tenant ID (Single Line of Text) - `hnt_tenantid`
│   │   ├── Hunter Source (Choice) - `hnt_source`
│   │   ├── Hunter M365 Fit Score (Whole Number) - `hnt_m365fitscore`
│   │   └── Hunter M365 Match Tags (MLT) - `hnt_m365matchtags`
│   │
│   ├── Section: AI & Sync Analytics
│   │   ├── D365 Lead ID (Single Line of Text) - `hnt_d365leadid`
│   │   ├── Hunter Last Sync Time (Date and Time) - `hnt_lastsynctime`
│   │   ├── Hunter Sync Attempt Count (Whole Number) - `hnt_syncattemptcount`
│   │   ├── Hunter Processing Status (Choice) - `hnt_processingstatus`
│   │   ├── Hunter Sync Error Message (MLT) - `hnt_syncerrormessage`
│   │   └── Hunter Push Status (Choice) - `hnt_pushstatus`
│   │
│   ├── Section: Contact Details
│   │   ├── First Name (Text)
│   │   ├── Last Name (Text)
│   │   ├── Job Title (Text)
│   │   ├── Email (Email)
│   │   └── Mobile Phone (Phone)
│   │
│   ├── Section: Address
│   │   ├── Street 1 (Text)
│   │   ├── Street 2 (Text)
│   │   ├── Street 3 (Text)
│   │   ├── City (Text)
│   │   ├── State/Province (Text)
│   │   ├── ZIP/Postal Code (Text)
│   │   └── Country/Region (Text)
│   │
│   └── Section: Description
│       └── Description (MLT)
│
├── Tab: Details
│   └── [Standard D365 Details fields]
│
├── Tab: Notes & Activities
│   └── [Standard D365 Notes & Activities]
│
├── Tab: Preferences
│   └── [Standard D365 Preferences]
│
└── Tab: Advanced Debug (Technical Only)
    └── Section: Advanced Debug (Technical Only)
        ├── Hunter AutoScore Version (Single Line of Text) - `hnt_HunterAutoScoreVersi...`
        ├── Hunter Domain (Single Line of Text) - `hnt_domain`
        ├── Hunter Is Re-Enriched (Yes/No) - `hnt_isreenriched`
        ├── Hunter ML Weight JSON (MLT) - `hnt_HunterMLWeightJSON`
        └── Hunter Intelligence JSON (MLT) - `hnt_intelligencejson`
```

---

## 3. Tab Structure

### Tab: General

**Purpose:** Primary form content - all main sections

**Sections:**
1. Business Card
2. Hunter Intelligence
3. Partner Center
4. AI & Sync Analytics
5. Contact Details
6. Address
7. Description

**Visibility:** All users (Sales, Operations, Management)

---

### Tab: Details

**Purpose:** Standard D365 Details fields

**Content:** Standard Lead entity details (inherited from D365)

**Visibility:** All users

---

### Tab: Notes & Activities

**Purpose:** Standard D365 Notes & Activities

**Content:** 
- Notes
- Activities (Tasks, Appointments, Phone Calls, Emails)
- Timeline

**Visibility:** All users

---

### Tab: Preferences

**Purpose:** Standard D365 Preferences

**Content:** Lead preferences and settings

**Visibility:** All users

---

### Tab: Advanced Debug (Technical Only)

**Purpose:** Technical debugging and data science fields

**Sections:**
1. Advanced Debug (Technical Only)

**Visibility:** 
- **Current:** All users (will be restricted)
- **Planned:** Technical roles only (Security Role-based)

**Note:** This tab contains duplicate fields from other sections (for historical reference) and Post-MVP fields.

---

## 4. Section Details

### Section: Business Card

**Location:** Tab: General  
**Purpose:** Company/account level information  
**Layout:** 2-column layout (recommended)

**Fields:**
- Topic (required)
- Company Name (required)
- Company Email
- Website
- Business Phone

**Design Notes:**
- First section in form (top of General tab)
- Company-level information (not personal contact)
- Used as primary identifier in grid views

---

### Section: Hunter Intelligence

**Location:** Tab: General  
**Purpose:** Hunter scoring & enrichment dashboard  
**Layout:** 2-column layout (recommended)

**Fields:**
- Hunter Final Score (Whole Number, 0-100) - `hnt_finalscore`
- Hunter Priority Score (Whole Number, 1-7) - `hnt_priorityscore`
- Hunter Segment (Choice) - `hnt_segment`
- Hunter Provider (Single Line of Text) - `hnt_provider`
- Hunter Tenant Size (Choice) - `hnt_huntertenantsize`
- Hunter Infrastructure Summary (MLT) - `hnt_infrasummary`
- Hunter Confidence (Decimal) - `hnt_confidence`

> **Note:** Fields not found in D365 (may be calculated or not yet implemented):
> - Hunter Priority Category
> - Hunter Priority Label
> - Hunter Technical Heat
> - Hunter Commercial Segment
> - Hunter Commercial Heat

**Design Notes:**
- Core Hunter intelligence fields
- Read-only for most users (populated by Hunter)
- Used for lead quality assessment and prioritization

---

### Section: Partner Center

**Location:** Tab: General  
**Purpose:** Partner Center referral tracking  
**Layout:** 2-column layout (recommended)

**Fields:**
- Hunter Referral ID (Single Line of Text) - `hnt_referralid`
- Hunter Referral Type (Choice) - `hnt_referraltype`
- Hunter Tenant ID (Single Line of Text) - `hnt_tenantid`
- Hunter Source (Choice) - `hnt_source`
- Hunter M365 Fit Score (Whole Number) - `hnt_m365fitscore`
- Hunter M365 Match Tags (MLT) - `hnt_m365matchtags`

> **Note:** `Hunter Is Partner Center Referral` field not found in D365. May be calculated from `hnt_referralid` (if not null = Yes).

**Design Notes:**
- Only populated for Partner Center referrals
- Empty fields are normal for manual leads
- Used to identify and track PC-sourced leads

---

### Section: AI & Sync Analytics

**Location:** Tab: General  
**Purpose:** Integration health dashboard  
**Layout:** 2-column layout (recommended)

**Fields:**
- D365 Lead ID (Single Line of Text) - `hnt_d365leadid`
- Hunter Last Sync Time (Date and Time) - `hnt_lastsynctime`
- Hunter Sync Attempt Count (Whole Number) - `hnt_syncattemptcount`
- Hunter Processing Status (Choice) - `hnt_processingstatus`
- Hunter Sync Error Message (MLT) - `hnt_syncerrormessage`
- Hunter Push Status (Choice) - `hnt_pushstatus`

**Design Notes:**
- Operational/debugging section
- Not customer-facing
- Used for integration monitoring and troubleshooting

---

### Section: Contact Details

**Location:** Tab: General  
**Purpose:** Personal contact information (Decision Maker)  
**Layout:** 2-column layout (recommended)

**Fields:**
- First Name (required)
- Last Name (required)
- Job Title
- Email
- Mobile Phone

**Design Notes:**
- Personal contact (not company-level)
- Primary decision maker information
- Separate from Business Card (company vs. person)

---

### Section: Address

**Location:** Tab: General  
**Purpose:** Physical address information  
**Layout:** 2-column layout (recommended)

**Fields:**
- Street 1
- Street 2
- Street 3
- City
- State/Province
- ZIP/Postal Code
- Country/Region

**Design Notes:**
- Standard D365 address block
- Used for mailing and field operations

---

### Section: Description

**Location:** Tab: General  
**Purpose:** Free-form notes and context  
**Layout:** Full-width layout (recommended)

**Fields:**
- Description (MLT)

**Design Notes:**
- Free-form text field
- Used for manual notes, deal context, Hunter/PC data summary

---

### Section: Advanced Debug (Technical Only)

**Location:** Tab: Advanced Debug (Technical Only)  
**Purpose:** Technical debugging fields  
**Layout:** 2-column layout (recommended)

**Fields:**
- Hunter AutoScore Version (Single Line of Text) - `hnt_HunterAutoScoreVersi...`
- Hunter Domain (Single Line of Text) - `hnt_domain`
- Hunter Is Re-Enriched (Yes/No) - `hnt_isreenriched`
- Hunter ML Weight JSON (MLT) - `hnt_HunterMLWeightJSON`
- Hunter Intelligence JSON (MLT) - `hnt_intelligencejson`

**Design Notes:**
- Technical-only section
- Contains duplicates (for historical reference)
- Post-MVP fields for future implementation
- Will be restricted to technical roles

---

## 5. Control Types

### Standard Field Controls

**Type:** Standard field  
**Usage:** Most text, number, and choice fields  
**Examples:** Topic, Company Name, Hunter Final Score

---

### Multiline Text Controls

**Type:** Multiple Lines of Text  
**Usage:** Long-form text fields  
**Examples:** Description, Hunter Infrastructure Summary, Hunter Sync Error Message

**Configuration:**
- Number of lines: 3-5 (recommended)
- Rich text: Disabled (for JSON fields)

---

### Lookup Controls

**Type:** Lookup  
**Usage:** Related entity references  
**Examples:** Owner (User/Team)

**Configuration:**
- Allow filtering: Yes
- Allow search: Yes

---

### Date/Time Controls

**Type:** Date and Time  
**Usage:** Timestamp fields  
**Examples:** Hunter Last Sync Time

**Configuration:**
- Behavior: User Local
- Format: Date and Time

---

### Option Set Controls

**Type:** Choice (Option Set)  
**Usage:** Predefined value lists  
**Examples:** Status Reason, Hunter Segment, Hunter Processing Status

**Configuration:**
- Display format: Radio buttons or Dropdown (context-dependent)
- Default value: Set where applicable

---

### Boolean Controls

**Type:** Two Options (Yes/No)  
**Usage:** Yes/No fields  
**Examples:** Hunter Is Re-Enriched (`hnt_isreenriched`)

> **Note:** `Hunter Is Partner Center Referral` field not found in D365. May be calculated from `hnt_referralid`.

**Configuration:**
- Display format: Checkbox or Radio buttons
- Default value: No (unchecked)

---

### Read-Only Fields

**Fields:** Most Hunter Intelligence fields  
**Configuration:**
- Locked: Yes
- Populated by: Hunter integration (backend)

**Rationale:** Prevents manual editing of calculated/scored fields

---

## 6. Form Behavior

### Auto-Save

**Enabled:** Yes  
**Behavior:** Standard D365 auto-save (30 seconds or on field change)

---

### Fallback Forms

**Primary:** Information (Main)  
**Fallback:** Lead (Classic) - for legacy compatibility

**Order:**
1. Information (Main) - Primary
2. Lead (Classic) - Fallback

---

### Form Order

**Default:** Information (Main)  
**Mobile:** Information (Main)  
**Tablet:** Information (Main)

---

### Business Rules

**Visibility Rules:**
- Partner Center section: Show only if `hnt_referralid` != null (calculated: Is Partner Center Referral = Yes)
- Advanced Debug tab: Show only for technical roles (planned)

**Validation Rules:**
- Company Name: Required
- Topic: Required
- First Name: Required
- Last Name: Required

---

## 7. Security & Visibility

### Field-Level Security

**Current:** All fields visible to all users  
**Planned:** Advanced Debug tab restricted to technical roles

---

### Security Roles

**Sales User:**
- Full access to General tab
- Read-only access to Hunter Intelligence fields
- No access to Advanced Debug tab (planned)

**Operations User:**
- Full access to General tab
- Read/write access to AI & Sync Analytics section
- Read-only access to Hunter Intelligence fields
- Access to Advanced Debug tab (planned)

**System Administrator:**
- Full access to all tabs and fields
- Can modify form structure

---

### Form Visibility

**Information Form:**
- Visible to: All users
- Default: Yes

**Advanced Debug Tab:**
- Visible to: Technical roles only (planned)
- Current: All users (will be restricted)

---

## 8. Form Design Best Practices

### Layout Recommendations

1. **2-Column Layout:** Use for most sections (better space utilization)
2. **Full-Width Layout:** Use for Description and long MLT fields
3. **Section Order:** Business Card → Hunter Intelligence → Partner Center → AI & Sync Analytics → Contact Details → Address → Description

### Field Grouping

1. **Logical Grouping:** Group related fields together (e.g., all Hunter Intelligence fields)
2. **Visual Hierarchy:** Use section headers to create clear visual separation
3. **Required Fields:** Place required fields at the top of sections

### Performance Considerations

1. **Field Count:** Keep sections manageable (max 10-12 fields per section)
2. **Lazy Loading:** Consider lazy loading for Advanced Debug tab
3. **Caching:** Leverage D365 form caching for better performance

---

## 📝 Notlar

- **Logical Names:** All confirmed from D365 Power Apps interface (2025-01-30)
- **Publisher Prefix:** `hnt_` confirmed for all custom Hunter fields
- **Missing Fields:** Some fields from `mapping.py` not found in D365 (may be calculated or not yet implemented):
  - `hunter_priority_category`
  - `hunter_priority_label`
  - `hunter_technical_heat`
  - `hunter_commercial_segment`
  - `hunter_commercial_heat`
  - `hunter_is_partner_center_referral` (may be calculated from `hnt_referralid`)
- **Security:** Advanced Debug tab visibility will be restricted to technical roles
- **Form Order:** Information form is primary; classic form is fallback

---

## 🔄 Güncelleme Geçmişi

- **2025-01-30:** v1.1 - Logical names confirmed from D365 (`hnt_` prefix), field list updated to match actual D365 fields
- **2025-01-30:** v1.0 - İlk versiyon oluşturuldu (form structure documented)

