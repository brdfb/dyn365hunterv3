# 🐛 Leads Endpoint 500 Error - Bug Fix

**Tarih**: 2025-01-30  
**Durum**: ✅ **FIXED**  
**Severity**: 🔴 **P0** (Production Blocker)

---

## 🔍 Problem

**Symptom**: `GET /api/v1/leads` endpoint returns 500 Internal Server Error

**Error Message**:
```
psycopg2.ProgrammingError: can't adapt type 'Query'
[SQL: 
        SELECT COUNT(DISTINCT lr.domain) as total
        FROM leads_ready lr
        LEFT JOIN partner_center_referrals pcr ON lr.domain = pcr.domain
        WHERE 1=1
     AND pcr.referral_type = %(referral_type)s AND lr.readiness_score IS NOT NULL]
[parameters: {'referral_type': Query(None)}]
```

---

## 🔎 Root Cause

**Problem**: `app/api/v1/leads.py` dosyasında `get_leads_v1` fonksiyonu `referral_type` parametresini `get_leads` fonksiyonuna geçirmiyordu.

**Details**:
- `get_leads` fonksiyonu `referral_type` parametresini bekliyor (line 346-348)
- `get_leads_v1` fonksiyonu `referral_type` parametresini tanımlamıyordu
- FastAPI'nin `Query(None)` objesi direkt olarak SQL'e geçiyordu
- SQLAlchemy `Query(None)` objesini adapt edemiyordu

---

## ✅ Fix

**File**: `app/api/v1/leads.py`

**Change**: `referral_type` parametresini `get_leads_v1` fonksiyonuna ekledim ve `get_leads` çağrısına geçirdim.

**Before**:
```python
@router.get("", response_model=LeadsListResponse)
async def get_leads_v1(
    segment: Optional[str] = Query(...),
    min_score: Optional[int] = Query(...),
    provider: Optional[str] = Query(...),
    # referral_type missing!
    favorite: Optional[bool] = Query(...),
    ...
):
    return await get_leads(
        segment=segment,
        min_score=min_score,
        provider=provider,
        # referral_type not passed!
        favorite=favorite,
        ...
    )
```

**After**:
```python
@router.get("", response_model=LeadsListResponse)
async def get_leads_v1(
    segment: Optional[str] = Query(...),
    min_score: Optional[int] = Query(...),
    provider: Optional[str] = Query(...),
    referral_type: Optional[str] = Query(  # ✅ ADDED
        None, description="Filter by Partner Center referral type (co-sell, marketplace, solution-provider)"
    ),
    favorite: Optional[bool] = Query(...),
    ...
):
    return await get_leads(
        segment=segment,
        min_score=min_score,
        provider=provider,
        referral_type=referral_type,  # ✅ ADDED
        favorite=favorite,
        ...
    )
```

---

## ✅ Verification

**Test Results**:
- ✅ `GET /api/v1/leads?limit=1` → 200 OK
- ✅ `GET /api/v1/leads?limit=1&referral_type=co-sell` → 200 OK
- ✅ `GET /api/v1/leads?limit=1&provider=M365` → 200 OK
- ✅ Response contains valid JSON with leads array

**Status**: ✅ **FIXED** - Endpoint çalışıyor

---

## 📊 Impact

**Before Fix**:
- ❌ Leads endpoint 500 error
- ❌ Production deployment blocker

**After Fix**:
- ✅ Leads endpoint 200 OK
- ✅ Production deployment için hazır (bu bug çözüldü)

---

## 🎯 Production Readiness Update

**Previous Status**: 🔴 **NO-GO** (Leads 500 blocker)

**Current Status**: ✅ **GO** (Leads 500 fixed)

**Remaining Blockers**:
- ⚠️ Production environment variables set edilmeli
- ⚠️ Production database backup alınmalı
- ⚠️ Production migration test edilmeli
- ⚠️ Production smoke tests çalıştırılmalı

---

## 📝 Files Changed

1. `app/api/v1/leads.py` - `referral_type` parametresi eklendi ve `get_leads` çağrısına geçirildi

---

**Last Updated**: 2025-01-30  
**Status**: ✅ **FIXED** - Production deployment için hazır (bu bug çözüldü)

