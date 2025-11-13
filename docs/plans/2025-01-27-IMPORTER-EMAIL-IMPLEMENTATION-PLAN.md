# Importer + Email Module Implementation Plan

**Tarih:** 2025-01-27  
**Durum:** Implementation Ready  
**Versiyon:** v2 (Critique Uyumlu)  
**TODO:** `docs/todos/G11-importer-email.md`

---

## 🎯 Priority & Implementation Order

### P0: Importer Module (G11) - MUST HAVE
**Start here first** - Critical for OSB Excel ingestion

### P1: Email Generator (G12) - SHOULD HAVE  
**After G11** - Quick win, simple implementation

### P2: Email Validator (G13) - NICE TO HAVE
**After G12** - Can be added incrementally

---

## 📋 Kararlar Özeti

### ✅ Karar 1: Mevcut `/ingest/csv` Genişletme
- Yeni endpoint yok, mevcut endpoint genişletilecek
- Excel desteği (.xlsx, .xls)
- `auto_detect_columns` parametresi (default: False)

### ✅ Karar 2: Importer Core Sadece Column Guessing
- `app/core/importer.py` sadece `guess_company_column()` ve `guess_domain_column()`
- Normalization için mevcut `normalizer` modülü kullanılacak

### ✅ Karar 3: Backward Compatibility
- `auto_detect_columns=False` default
- Mevcut CSV formatı bozulmayacak

### ✅ Karar 4: Light Email Validation (MVP)
- Syntax check (regex)
- MX lookup (DNS)
- SMTP opsiyonel (flag ile)

### ✅ Karar 5: Confidence Score
- `confidence: "high" | "medium" | "low"`
- `checks: {syntax, mx, smtp}` detayları

---

## 🎯 Implementation Task List (Prioritized)

### Phase 1: G11 - Importer Module (P0)

#### 1️⃣ DEPENDENCIES

**Dosya:** `requirements.txt`

**Değişiklik:**
```python
# Zaten var: pandas==2.1.3
# Eklenecek:
openpyxl==3.1.2  # Excel support
```

**Not:** `pandas` zaten var, sadece `openpyxl` eklenecek.

**Priority:** P0 - Required for Excel support

---

#### 2️⃣ IMPORTER CORE (Column Guessing Only)

**Dosya:** `app/core/importer.py` (YENİ)

**İçerik:**
```python
"""Column detection utilities for Excel/CSV import."""
from typing import Optional
import pandas as pd
import re

COMPANY_HINTS = ["firma", "ünvan", "unvan", "company", "name", "title", "şirket"]
DOMAIN_HINTS = ["web", "website", "site", "domain", "url", "internet", "adres"]

def guess_company_column(df: pd.DataFrame) -> Optional[str]:
    """
    Guess company name column from DataFrame.
    
    Uses heuristics based on column name hints.
    Falls back to first column if no match found.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Column name if found, None otherwise
    """
    cols = [str(c).lower() for c in df.columns]
    
    # Check column names for company hints
    for col in df.columns:
        low = str(col).lower()
        if any(h in low for h in COMPANY_HINTS):
            return col
    
    # Fallback: first column (often company name in OSB lists)
    return df.columns[0] if len(df.columns) > 0 else None

def guess_domain_column(df: pd.DataFrame) -> Optional[str]:
    """
    Guess domain/website column from DataFrame.
    
    Uses heuristics:
    1. Column name hints
    2. Content analysis (URL/domain patterns)
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Column name if found, None otherwise
    """
    # 1) Check column names for domain hints
    for col in df.columns:
        low = str(col).lower()
        if any(h in low for h in DOMAIN_HINTS):
            return col
    
    # 2) Content analysis: look for URL/domain patterns
    url_pattern = re.compile(
        r"(https?://|www\.|\.com|\.com\.tr|\.net|\.org|\.tr|@)",
        re.IGNORECASE
    )
    
    best_col = None
    best_hits = 0
    
    for col in df.columns:
        # Count rows with URL/domain patterns
        hits = df[col].astype(str).str.contains(url_pattern, na=False).sum()
        if hits > best_hits:
            best_hits = hits
            best_col = col
    
    return best_col
```

**Önemli:** Normalization logic burada YOK, sadece column guessing.

**Priority:** P0 - Core functionality

---

#### 3️⃣ INGEST API REFACTOR

**Dosya:** `app/api/ingest.py` (GÜNCELLENECEK)

**Değişiklikler:**

1. **Excel support ekle:**
```python
# Mevcut CSV okuma:
if file.filename.endswith('.csv'):
    contents = await file.read()
    df = pd.read_csv(pd.io.common.BytesIO(contents))

# YENİ: Excel support
elif file.filename.lower().endswith(('.xlsx', '.xls')):
    contents = await file.read()
    df = pd.read_excel(pd.io.common.BytesIO(contents))
else:
    raise HTTPException(status_code=400, detail="File must be CSV or Excel (.xlsx, .xls)")
```

2. **Query parameter ekle:**
```python
@router.post("/csv", status_code=201)
async def ingest_csv(
    file: UploadFile = File(..., description="CSV or Excel file to ingest"),
    auto_detect_columns: bool = Query(False, description="Auto-detect company/domain columns"),
    db: Session = Depends(get_db)
):
```

3. **Column detection logic:**
```python
# Normalize column names (case-insensitive)
df.columns = df.columns.str.lower().str.strip()

# Column detection (if auto_detect_columns=True)
if auto_detect_columns:
    from app.core.importer import guess_company_column, guess_domain_column
    
    company_col = guess_company_column(df)
    domain_col = guess_domain_column(df)
    
    if not company_col or not domain_col:
        raise HTTPException(
            status_code=400,
            detail=f"Could not detect columns. Company: {company_col}, Domain: {domain_col}"
        )
    
    # Rename columns to standard names
    df = df.rename(columns={company_col: 'company_name', domain_col: 'domain'})
else:
    # Mevcut mantık: required 'domain' column
    if 'domain' not in df.columns:
        raise HTTPException(
            status_code=400,
            detail="CSV must contain a 'domain' column (or use auto_detect_columns=true)"
        )
```

4. **Normalization (mevcut normalizer kullan):**
```python
# Mevcut kod zaten normalizer kullanıyor:
from app.core.normalizer import (
    normalize_domain,
    extract_domain_from_email,
    extract_domain_from_website
)
# Değişiklik yok, zaten doğru kullanılıyor
```

**Backward Compatibility:**
- `auto_detect_columns=False` default → mevcut CSV'ler çalışmaya devam eder
- Required `domain` column mantığı korunur

**Priority:** P0 - Critical for OSB ingestion

**Tests Required:**
- `tests/test_importer_autodetect.py` - Column detection tests
- Update `tests/test_ingest_csv.py` - Excel support tests

---

### Phase 2: G12 - Email Generator (P1)

#### 4️⃣ EMAIL GENERATOR

**Dosya:** `app/core/email_generator.py` (YENİ)

**İçerik:**
```python
"""Generic email address generation utilities."""
from typing import List
from app.core.normalizer import normalize_domain

# Generic local parts (Türkiye + International)
GENERIC_LOCAL_PARTS = [
    "info",
    "iletisim",
    "muhasebe",
    "satis",
    "sales",
    "admin",
    "support",
    "ik",
    "hr",
]

def generate_generic_emails(domain: str) -> List[str]:
    """
    Generate generic email addresses for a domain.
    
    Args:
        domain: Domain name (will be normalized)
        
    Returns:
        List of generic email addresses (unique, sorted)
        
    Examples:
        >>> generate_generic_emails("example.com")
        ['admin@example.com', 'hr@example.com', 'ik@example.com', ...]
    """
    # Normalize domain
    normalized = normalize_domain(domain)
    if not normalized:
        return []
    
    # Generate emails
    emails = [f"{local}@{normalized}" for local in GENERIC_LOCAL_PARTS]
    
    # Remove duplicates and sort
        return sorted(set(emails))
```

**Priority:** P1 - Quick win, simple implementation

**Tests Required:**
- `tests/test_email_generator.py` - Email generation tests

---

### Phase 3: G13 - Email Validator (P2)

#### 5️⃣ EMAIL VALIDATOR (MVP - Light Validation)

**Dosya:** `app/core/email_validator.py` (YENİ)

**İçerik:**
```python
"""Email validation utilities (syntax, MX, optional SMTP)."""
from dataclasses import dataclass
from typing import Literal, Dict, Optional
import re
import smtplib
import dns.resolver
from app.core.analyzer_dns import get_mx_records  # Reuse existing DNS logic

EmailStatus = Literal["valid", "invalid", "unknown"]
ConfidenceLevel = Literal["high", "medium", "low"]

@dataclass
class EmailValidationResult:
    """Email validation result."""
    email: str
    status: EmailStatus
    confidence: ConfidenceLevel
    checks: Dict[str, any]
    reason: Optional[str] = None

# Email syntax regex (RFC 5322 simplified)
EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

def validate_email_syntax(email: str) -> bool:
    """Check email syntax validity."""
    return bool(EMAIL_PATTERN.match(email))

def validate_email_mx(domain: str) -> tuple[bool, Optional[str]]:
    """
    Check if domain has MX records.
    
    Returns:
        (has_mx, error_message)
    """
    try:
        mx_records = get_mx_records(domain)
        return (len(mx_records) > 0, None)
    except Exception as e:
        return (False, str(e))

def validate_email_smtp(email: str, timeout: float = 3.0) -> tuple[EmailStatus, str]:
    """
    Validate email via SMTP RCPT TO check.
    
    Returns:
        (status, reason)
    """
    try:
        local_part, domain = email.split("@", 1)
    except ValueError:
        return ("invalid", "Invalid email format")
    
    mx_records = get_mx_records(domain)
    if not mx_records:
        return ("unknown", "No MX records")
    
    # Try first MX server
    host = mx_records[0]
    
    try:
        server = smtplib.SMTP(host=host, timeout=timeout)
        server.helo()
        server.mail("test@example.com")
        code, msg = server.rcpt(email)
        server.quit()
        
        # 200-299: Accepted
        if 200 <= code < 300:
            return ("valid", f"SMTP {code}")
        
        # 500-599: Rejected (invalid)
        if 500 <= code < 600:
            return ("invalid", f"SMTP {code}")
        
        # Other codes: Unknown (catch-all or greylisting)
        return ("unknown", f"SMTP {code}")
        
    except smtplib.SMTPServerDisconnected:
        return ("unknown", "SMTP connection closed")
    except smtplib.SMTPConnectError:
        return ("unknown", "SMTP connection failed")
    except Exception as e:
        return ("unknown", str(e))

def validate_email(email: str, use_smtp: bool = False) -> EmailValidationResult:
    """
    Validate email address (syntax + MX + optional SMTP).
    
    Args:
        email: Email address to validate
        use_smtp: If True, perform SMTP check (default: False)
        
    Returns:
        EmailValidationResult with status, confidence, and checks
    """
    checks = {
        "syntax": False,
        "mx": False,
        "smtp": "skipped"
    }
    
    # 1) Syntax check
    syntax_valid = validate_email_syntax(email)
    checks["syntax"] = syntax_valid
    
    if not syntax_valid:
        return EmailValidationResult(
            email=email,
            status="invalid",
            confidence="high",
            checks=checks,
            reason="Invalid email syntax"
        )
    
    # Extract domain
    try:
        _, domain = email.split("@", 1)
    except ValueError:
        return EmailValidationResult(
            email=email,
            status="invalid",
            confidence="high",
            checks=checks,
            reason="Invalid email format"
        )
    
    # 2) MX check
    has_mx, mx_error = validate_email_mx(domain)
    checks["mx"] = has_mx
    
    if not has_mx:
        return EmailValidationResult(
            email=email,
            status="invalid",
            confidence="high",
            checks=checks,
            reason=f"No MX records: {mx_error}"
        )
    
    # 3) SMTP check (optional)
    if use_smtp:
        smtp_status, smtp_reason = validate_email_smtp(email)
        checks["smtp"] = smtp_status
        
        # Determine confidence based on SMTP result
        if smtp_status == "valid":
            confidence = "high"
        elif smtp_status == "invalid":
            confidence = "high"
        else:  # unknown (catch-all, greylisting, etc.)
            confidence = "medium"
        
        return EmailValidationResult(
            email=email,
            status=smtp_status,
            confidence=confidence,
            checks=checks,
            reason=smtp_reason
        )
    else:
        # Syntax + MX valid → medium confidence (no SMTP check)
        return EmailValidationResult(
            email=email,
            status="valid",
            confidence="medium",
            checks=checks,
            reason="Valid syntax and MX records (SMTP not checked)"
        )
```

**Priority:** P2 - Can be added incrementally

**Tests Required:**
- `tests/test_email_validator.py` - Validation tests with mocks

---

#### 6️⃣ EMAIL API

**Dosya:** `app/api/email_tools.py` (YENİ)

**İçerik:**
```python
"""Email generation and validation endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.core.email_generator import generate_generic_emails
from app.core.email_validator import validate_email, EmailValidationResult

router = APIRouter(prefix="/email", tags=["email"])

class EmailGenerateRequest(BaseModel):
    """Request model for email generation and validation."""
    domain: str
    use_smtp: bool = False  # Default: False (light validation)

class EmailCheck(BaseModel):
    """Email validation result model."""
    email: str
    status: str  # "valid" | "invalid" | "unknown"
    confidence: str  # "high" | "medium" | "low"
    checks: dict
    reason: Optional[str] = None

class EmailGenerateResponse(BaseModel):
    """Response model for email generation and validation."""
    domain: str
    emails: List[EmailCheck]

@router.post("/generate-and-validate", response_model=EmailGenerateResponse)
async def generate_and_validate(req: EmailGenerateRequest):
    """
    Generate generic emails for a domain and validate them.
    
    Args:
        req: Request with domain and use_smtp flag
        
    Returns:
        EmailGenerateResponse with validation results
    """
    domain = req.domain.strip()
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
    
    # Generate generic emails
    emails = generate_generic_emails(domain)
    
    if not emails:
        raise HTTPException(
            status_code=400,
            detail=f"Could not generate emails for domain: {domain}"
        )
    
    # Validate each email
    results: List[EmailValidationResult] = [
        validate_email(email, use_smtp=req.use_smtp)
        for email in emails
    ]
    
    # Convert to response model
    return EmailGenerateResponse(
        domain=domain,
        emails=[
            EmailCheck(
                email=r.email,
                status=r.status,
                confidence=r.confidence,
                checks=r.checks,
                reason=r.reason
            )
            for r in results
        ]
    )
```

**Priority:** P1 (for generator), P2 (for validator)

---

#### 7️⃣ MAIN ROUTER UPDATE

**Dosya:** `app/main.py` (GÜNCELLENECEK)

**Değişiklik:**
```python
from app.api import ingest, scan, leads, dashboard, email_tools

# Register routers
app.include_router(ingest.router)  # Zaten var, sadece genişletildi
app.include_router(scan.router)
app.include_router(leads.router)
app.include_router(dashboard.router)
app.include_router(email_tools.router)  # YENİ
```

**Priority:** P0 (Importer tests), P1 (Email generator tests), P2 (Validator tests)

---

#### 8️⃣ TESTS

**Yeni Test Dosyaları:**

#### `tests/test_importer_autodetect.py`
```python
"""Tests for column auto-detection in importer."""
import pytest
import pandas as pd
from app.core.importer import guess_company_column, guess_domain_column

class TestColumnGuessing:
    def test_guess_company_column_by_name(self):
        df = pd.DataFrame({
            "Firma Adı": ["A Şirketi", "B Şirketi"],
            "Web": ["example.com", "test.com"]
        })
        assert guess_company_column(df) == "Firma Adı"
    
    def test_guess_domain_column_by_name(self):
        df = pd.DataFrame({
            "Firma": ["A Şirketi"],
            "Website": ["example.com"]
        })
        assert guess_domain_column(df) == "Website"
    
    def test_guess_domain_column_by_content(self):
        df = pd.DataFrame({
            "Firma": ["A Şirketi"],
            "Adres": ["https://example.com", "www.test.com"]
        })
        assert guess_domain_column(df) == "Adres"
```

#### `tests/test_email_generator.py`
```python
"""Tests for email generation."""
import pytest
from app.core.email_generator import generate_generic_emails

class TestEmailGenerator:
    def test_generate_generic_emails(self):
        emails = generate_generic_emails("example.com")
        assert len(emails) > 0
        assert all("@" in email for email in emails)
        assert all(email.endswith("@example.com") for email in emails)
    
    def test_generate_emails_normalizes_domain(self):
        emails = generate_generic_emails("WWW.EXAMPLE.COM")
        assert all(email.endswith("@example.com") for email in emails)
```

#### `tests/test_email_validator.py`
```python
"""Tests for email validation."""
import pytest
from app.core.email_validator import (
    validate_email_syntax,
    validate_email_mx,
    validate_email
)

class TestEmailValidation:
    def test_validate_email_syntax_valid(self):
        assert validate_email_syntax("test@example.com") is True
    
    def test_validate_email_syntax_invalid(self):
        assert validate_email_syntax("invalid-email") is False
    
    def test_validate_email_light(self):
        # Light validation (syntax + MX, no SMTP)
        result = validate_email("info@google.com", use_smtp=False)
        assert result.status in ["valid", "invalid"]
        assert result.confidence in ["high", "medium"]
        assert result.checks["smtp"] == "skipped"
```

---

## 📊 Implementation Checklist (Prioritized)

### ✅ Phase 1: G11 - Importer Module (P0) - START HERE

#### Dependencies
- [ ] Add `openpyxl==3.1.2` to `requirements.txt`

#### Importer Core
- [ ] Create `app/core/importer.py` with column guessing functions
- [ ] Write `tests/test_importer_autodetect.py` for column guessing

#### Ingest API Refactor
- [ ] Add Excel support (.xlsx, .xls) to `/ingest/csv`
- [ ] Add `auto_detect_columns` query parameter (default: False)
- [ ] Integrate column guessing logic
- [ ] Ensure backward compatibility (existing CSV ingestion works)
- [ ] Update `tests/test_ingest_csv.py` with Excel tests

#### Documentation (G11)
- [ ] Update README.md API Endpoints section
- [ ] Update CHANGELOG.md under `[Unreleased]` → `### Added`
- [ ] Mark G11 as completed in TODO

---

### ✅ Phase 2: G12 - Email Generator (P1) - AFTER G11

#### Email Generator
- [ ] Create `app/core/email_generator.py`
- [ ] Write `tests/test_email_generator.py`

#### Email API (Generator Only)
- [ ] Create `app/api/email_tools.py` with generation endpoint
- [ ] Register router in `app/main.py`
- [ ] Endpoint: `POST /email/generate` (validation later)

#### Documentation (G12)
- [ ] Update README.md API Endpoints section
- [ ] Update CHANGELOG.md
- [ ] Mark G12 as completed in TODO

---

### ✅ Phase 3: G13 - Email Validator (P2) - AFTER G12

#### Email Validator
- [ ] Create `app/core/email_validator.py`
- [ ] Implement syntax validation (regex)
- [ ] Implement MX record validation (DNS)
- [ ] Implement optional SMTP validation (flag-based)
- [ ] Write `tests/test_email_validator.py` (with mocks)

#### Email API (Full)
- [ ] Update `app/api/email_tools.py` with validation
- [ ] Endpoint: `POST /email/generate-and-validate`
- [ ] Add `use_smtp` parameter (default: False)

#### Documentation (G13)
- [ ] Update README.md API Endpoints section
- [ ] Update CHANGELOG.md
- [ ] Mark G13 as completed in TODO
- [ ] Archive TODO when all phases complete

---

## 🎯 Success Criteria (By Phase)

### Phase 1: G11 - Importer (P0)
- ✅ Mevcut CSV ingestion çalışmaya devam eder (backward compatible)
- ✅ Excel dosyaları (.xlsx, .xls) desteklenir
- ✅ `auto_detect_columns=true` ile OSB formatları işlenebilir
- ✅ Column guessing %80+ doğrulukta çalışır
- ✅ All tests pass

### Phase 2: G12 - Email Generator (P1)
- ✅ Generic email listesi üretilir (9 emails)
- ✅ Domain normalization çalışır
- ✅ API endpoint responds <1s
- ✅ All tests pass

### Phase 3: G13 - Email Validator (P2)
- ✅ Light validation (syntax + MX) çalışır
- ✅ SMTP validation opsiyonel ve flag ile kontrol edilir
- ✅ Confidence score doğru hesaplanır (high/medium/low)
- ✅ Response time <5s (SMTP olmadan), <30s (SMTP ile)
- ✅ All tests pass

---

## 📝 Notes

### Backward Compatibility
- Mevcut `/ingest/csv` endpoint'i aynı şekilde çalışmaya devam eder
- `auto_detect_columns=False` default → mevcut CSV'ler etkilenmez

### Performance
- Email validation: SMTP olmadan <1s, SMTP ile 10-30s (10 email × 3s timeout)
- Excel parsing: Büyük dosyalar için memory consideration gerekebilir

### Future Enhancements (Post-MVP)
- Preview mode for column mapping
- Configurable generic email list (`generic_emails.json`)
- Async/parallel SMTP validation
- Locale-specific email lists

---

**Hazırlayan:** AI Assistant  
**Tarih:** 2025-01-27  
**Durum:** Implementation Ready

