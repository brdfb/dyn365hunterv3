# 📊 Lead Views Reference (Full View Dictionary)

**Version:** v1.0  
**Last Updated:** 2025-01-30  
**Entity:** Lead (Dynamics 365 Sales)  
**App:** Sales Hub (Dynamics 365 Sales)

---

## 📋 İçindekiler

1. [Standard Views](#1-standard-views)
2. [Hunter Intelligence Views](#2-hunter-intelligence-views)
3. [Partner Center Views](#3-partner-center-views)
4. [View Configuration Details](#4-view-configuration-details)
5. [View Best Practices](#5-view-best-practices)

---

## 1. Standard Views

### My Open Leads

**Purpose:** Default view for sales users - shows open leads assigned to current user  
**Type:** Personal View (can be converted to System View)  
**Default:** Yes (for Sales Hub)

#### Columns

| Column | Field (Logical Name) | Width | Sort Order |
| ------ | -------------------- | ----- | ---------- |
| **Name** | `companyname` / `subject` | Auto | None |
| **Topic** | `subject` | Auto | None |
| **Status Reason** | `statuscode` | Auto | None |
| **Created On** | `createdon` | Auto | Descending |

#### Filter Criteria

```
Status Reason (statuscode) != Disqualified
AND
Owner (ownerid) = Current User
```

#### Sort Criteria

- **Primary:** Created On (Descending)
- **Secondary:** None

#### Usage

- **Primary View:** Sales users' default lead view
- **Quick Actions:** Create, Qualify, Disqualify
- **Bulk Actions:** Assign, Qualify, Disqualify

---

### All Leads

**Purpose:** System-wide view of all leads (administrative)  
**Type:** System View  
**Default:** No

#### Columns

| Column | Field (Logical Name) | Width | Sort Order |
| ------ | -------------------- | ----- | ---------- |
| **Name** | `companyname` / `subject` | Auto | None |
| **Topic** | `subject` | Auto | None |
| **Status Reason** | `statuscode` | Auto | None |
| **Owner** | `ownerid` | Auto | None |
| **Created On** | `createdon` | Auto | Descending |

#### Filter Criteria

```
Status Reason (statuscode) != Disqualified
```

#### Sort Criteria

- **Primary:** Created On (Descending)
- **Secondary:** Owner (Ascending)

#### Usage

- **Administrative View:** System administrators and managers
- **Bulk Actions:** Assign, Qualify, Disqualify, Delete

---

### Qualified Leads

**Purpose:** View of qualified leads ready for conversion  
**Type:** System View  
**Default:** No

#### Columns

| Column | Field (Logical Name) | Width | Sort Order |
| ------ | -------------------- | ----- | ---------- |
| **Name** | `companyname` / `subject` | Auto | None |
| **Topic** | `subject` | Auto | None |
| **Status Reason** | `statuscode` | Auto | None |
| **Rating** | `leadqualitycode` | Auto | None |
| **Created On** | `createdon` | Auto | Descending |

#### Filter Criteria

```
Status Reason (statuscode) = Qualified
```

#### Sort Criteria

- **Primary:** Created On (Descending)
- **Secondary:** Rating (Descending)

#### Usage

- **Conversion View:** Leads ready to convert to Opportunities
- **Quick Actions:** Convert to Opportunity

---

## 2. Hunter Intelligence Views

### Hunter Intelligence Leads (Önerilen)

**Purpose:** View focused on Hunter scoring and intelligence fields  
**Type:** System View (Önerilen)  
**Default:** No  
**Status:** Önerilen (henüz oluşturulmadı)

#### Columns

| Column | Field (Logical Name) | Width | Sort Order |
| ------ | -------------------- | ----- | ---------- |
| **Name** | `companyname` / `subject` | Auto | None |
| **Topic** | `subject` | Auto | None |
| **Hunter Final Score** | `hnt_finalscore` | 80px | Descending |
| **Hunter Segment** | `hnt_segment` | 100px | Ascending |
| **Hunter Priority Score** | `hnt_priorityscore` | 80px | Descending |
| **Hunter Provider** | `hnt_provider` | 100px | Ascending |
| **Hunter Tenant Size** | `hnt_huntertenantsize` | 100px | Ascending |
| **Hunter Processing Status** | `hnt_processingstatus` | 120px | Ascending |
| **Status Reason** | `statuscode` | Auto | None |
| **Created On** | `createdon` | Auto | Descending |

#### Filter Criteria

```
Status Reason (statuscode) != Disqualified
AND
Hunter Final Score (hnt_finalscore) != null
```

#### Sort Criteria

- **Primary:** Hunter Final Score (Descending)
- **Secondary:** Hunter Priority Score (Descending)
- **Tertiary:** Created On (Descending)

#### Usage

- **Intelligence View:** Sales and operations teams
- **Prioritization:** Sort by Hunter scores for lead prioritization
- **Quick Actions:** Qualify, Assign, View Details

---

### High Priority Leads (Önerilen)

**Purpose:** View of high-priority leads based on Hunter scoring  
**Type:** System View (Önerilen)  
**Default:** No  
**Status:** Önerilen (henüz oluşturulmadı)

#### Columns

| Column | Field (Logical Name) | Width | Sort Order |
| ------ | -------------------- | ----- | ---------- |
| **Name** | `companyname` / `subject` | Auto | None |
| **Topic** | `subject` | Auto | None |
| **Hunter Final Score** | `hnt_finalscore` | 80px | Descending |
| **Hunter Priority Score** | `hnt_priorityscore` | 80px | Descending |
| **Hunter Segment** | `hnt_segment` | 100px | Ascending |
| **Status Reason** | `statuscode` | Auto | None |
| **Owner** | `ownerid` | Auto | None |
| **Created On** | `createdon` | Auto | Descending |

#### Filter Criteria

```
Status Reason (statuscode) != Disqualified
AND
Hunter Priority Score (hnt_priorityscore) <= 3
AND
Hunter Final Score (hnt_finalscore) >= 70
```

#### Sort Criteria

- **Primary:** Hunter Priority Score (Ascending)
- **Secondary:** Hunter Final Score (Descending)
- **Tertiary:** Created On (Descending)

#### Usage

- **Priority View:** High-priority leads requiring immediate attention
- **Sales Focus:** Focus on best opportunities
- **Quick Actions:** Qualify, Assign, Convert

---

### Hunter Sync Status (Önerilen)

**Purpose:** View of leads with sync status for operations monitoring  
**Type:** System View (Önerilen)  
**Default:** No  
**Status:** Önerilen (henüz oluşturulmadı)

#### Columns

| Column | Field (Logical Name) | Width | Sort Order |
| ------ | -------------------- | ----- | ---------- |
| **Name** | `companyname` / `subject` | Auto | None |
| **Topic** | `subject` | Auto | None |
| **Hunter Processing Status** | `hnt_processingstatus` | 120px | Ascending |
| **Hunter Last Sync Time** | `hnt_lastsynctime` | 120px | Descending |
| **Hunter Sync Attempt Count** | `hnt_syncattemptcount` | 100px | Descending |
| **Hunter Sync Error Message** | `hnt_syncerrormessage` | 200px | None |
| **Status Reason** | `statuscode` | Auto | None |
| **Created On** | `createdon` | Auto | Descending |

#### Filter Criteria

```
Hunter Processing Status (hnt_processingstatus) != null
```

#### Sort Criteria

- **Primary:** Hunter Processing Status (Ascending)
- **Secondary:** Hunter Last Sync Time (Descending)
- **Tertiary:** Hunter Sync Attempt Count (Descending)

#### Usage

- **Operations View:** Monitor integration health
- **Troubleshooting:** Identify sync issues and errors
- **Quick Actions:** Retry Sync, View Error Details

---

## 3. Partner Center Views

### Partner Center Leads (Önerilen)

**Purpose:** View of leads sourced from Partner Center  
**Type:** System View (Önerilen)  
**Default:** No  
**Status:** Önerilen (henüz oluşturulmadı)

#### Columns

| Column | Field (Logical Name) | Width | Sort Order |
| ------ | -------------------- | ----- | ---------- |
| **Name** | `companyname` / `subject` | Auto | None |
| **Topic** | `subject` | Auto | None |
| **Hunter Referral ID** | `hnt_referralid` | 150px | None |
| **Hunter Referral Type** | `hnt_referraltype` | 120px | Ascending |
| **Hunter Provider** | `hnt_provider` | 100px | Ascending |
| **Hunter M365 Fit Score** | `hnt_m365fitscore` | 100px | Descending |
| **Hunter Final Score** | `hnt_finalscore` | 80px | Descending |
| **Status Reason** | `statuscode` | Auto | None |
| **Created On** | `createdon` | Auto | Descending |

#### Filter Criteria

```
Hunter Referral ID (hnt_referralid) != null
AND
Status Reason (statuscode) != Disqualified
```

#### Sort Criteria

- **Primary:** Hunter M365 Fit Score (Descending)
- **Secondary:** Hunter Final Score (Descending)
- **Tertiary:** Created On (Descending)

#### Usage

- **Partner Center View:** Track PC-sourced leads
- **Referral Tracking:** Monitor referral performance
- **Quick Actions:** Qualify, Assign, View Referral Details

---

### M365 Fit Leads (Önerilen)

**Purpose:** View of leads with high M365 fit scores  
**Type:** System View (Önerilen)  
**Default:** No  
**Status:** Önerilen (henüz oluşturulmadı, Post-MVP)

#### Columns

| Column | Field (Logical Name) | Width | Sort Order |
| ------ | -------------------- | ----- | ---------- |
| **Name** | `companyname` / `subject` | Auto | None |
| **Topic** | `subject` | Auto | None |
| **Hunter M365 Fit Score** | `hnt_m365fitscore` | 100px | Descending |
| **Hunter M365 Match Tags** | `hnt_m365matchtags` | 200px | None |
| **Hunter Provider** | `hnt_provider` | 100px | Ascending |
| **Hunter Final Score** | `hnt_finalscore` | 80px | Descending |
| **Status Reason** | `statuscode` | Auto | None |
| **Created On** | `createdon` | Auto | Descending |

#### Filter Criteria

```
Hunter M365 Fit Score (hnt_m365fitscore) >= 70
AND
Hunter Provider (hnt_provider) = M365
AND
Status Reason (statuscode) != Disqualified
```

#### Sort Criteria

- **Primary:** Hunter M365 Fit Score (Descending)
- **Secondary:** Hunter Final Score (Descending)
- **Tertiary:** Created On (Descending)

#### Usage

- **M365 Focus:** Leads with high M365 fit
- **Post-MVP:** Requires M365 Fit Score implementation
- **Quick Actions:** Qualify, Assign, View M365 Details

---

## 4. View Configuration Details

### Column Configuration

#### Column Width

- **Auto:** D365 default width (recommended for most columns)
- **Fixed:** Specify pixel width for consistent layout (e.g., scores, status fields)
- **Recommended Fixed Widths:**
  - Scores: 80-100px
  - Status/Choice fields: 100-120px
  - Text fields: 150-200px
  - Dates: 120px

#### Column Sort

- **Primary Sort:** Most important sort (e.g., Hunter Final Score)
- **Secondary Sort:** Tie-breaker (e.g., Created On)
- **Tertiary Sort:** Additional tie-breaker (if needed)

---

### Filter Configuration

#### Filter Operators

- **Equals (=):** Exact match
- **Not Equals (!=):** Exclude values
- **Greater Than (>):** Numeric comparison
- **Greater Than or Equal (>=):** Numeric comparison
- **Less Than (<):** Numeric comparison
- **Less Than or Equal (<=):** Numeric comparison
- **Contains:** Text search
- **Does Not Contain:** Exclude text
- **Null / Not Null:** Check for empty values

#### Filter Logic

- **AND:** All conditions must be true
- **OR:** Any condition can be true
- **Grouping:** Use parentheses for complex logic

---

### View Types

#### Personal Views

- **Scope:** User-specific
- **Usage:** Custom views for individual users
- **Example:** "My High Priority Leads"

#### System Views

- **Scope:** Organization-wide
- **Usage:** Standard views for all users
- **Example:** "Hunter Intelligence Leads"

---

## 5. View Best Practices

### Column Selection

1. **Limit Columns:** Keep to 8-10 columns for readability
2. **Prioritize:** Show most important fields first
3. **Group Related:** Group related fields together
4. **Hide Unused:** Hide columns that aren't frequently used

### Sort Configuration

1. **Primary Sort:** Most important field (e.g., Hunter Final Score)
2. **Secondary Sort:** Tie-breaker (e.g., Created On)
3. **User-Friendly:** Sort by fields users care about most

### Filter Configuration

1. **Default Filters:** Set sensible default filters (e.g., exclude disqualified)
2. **Performance:** Avoid complex filters that slow down queries
3. **User-Friendly:** Make filters easy to understand and modify

### View Naming

1. **Clear Names:** Use descriptive names (e.g., "Hunter Intelligence Leads")
2. **Consistent:** Follow naming conventions (e.g., "Hunter [Category] Leads")
3. **Purpose-Driven:** Name reflects view purpose

---

## 6. View Implementation Checklist

### Standard Views

- [x] My Open Leads (exists)
- [x] All Leads (exists)
- [x] Qualified Leads (exists)

### Hunter Intelligence Views

- [ ] Hunter Intelligence Leads (önerilen)
- [ ] High Priority Leads (önerilen)
- [ ] Hunter Sync Status (önerilen)

### Partner Center Views

- [ ] Partner Center Leads (önerilen)
- [ ] M365 Fit Leads (önerilen, Post-MVP)

---

## 📝 Notlar

- **Önerilen Views:** Marked views are recommended but not yet created
- **Post-MVP Views:** Require Post-MVP field implementation
- **Column Widths:** Recommendations based on typical field content
- **Filter Logic:** Adjust based on business requirements

---

## 🔄 Güncelleme Geçmişi

- **2025-01-30:** v1.0 - İlk versiyon oluşturuldu (standard views documented, recommended views added)

