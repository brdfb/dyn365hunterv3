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
        
    Examples:
        >>> df = pd.DataFrame({"Firma Adı": ["A Şirketi"], "Web": ["example.com"]})
        >>> guess_company_column(df)
        'Firma Adı'
    """
    if df.empty or len(df.columns) == 0:
        return None
    
    # Check column names for company hints (case-insensitive)
    for col in df.columns:
        low = str(col).lower()
        if any(h in low for h in COMPANY_HINTS):
            return col
    
    # Fallback: first column (often company name in OSB lists)
    return df.columns[0]


def guess_domain_column(df: pd.DataFrame) -> Optional[str]:
    """
    Guess domain/website column from DataFrame.
    
    Uses heuristics:
    1. Column name hints (case-insensitive)
    2. Content analysis (URL/domain patterns)
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Column name if found, None otherwise
        
    Examples:
        >>> df = pd.DataFrame({"Firma": ["A Şirketi"], "Website": ["example.com"]})
        >>> guess_domain_column(df)
        'Website'
    """
    if df.empty or len(df.columns) == 0:
        return None
    
    # 1) Check column names for domain hints (case-insensitive)
    for col in df.columns:
        low = str(col).lower()
        if any(h in low for h in DOMAIN_HINTS):
            return col
    
    # 2) Content analysis: look for URL/domain patterns
    # Use non-capturing groups to avoid regex warnings
    url_pattern = re.compile(
        r"(?:https?://|www\.|\.com|\.com\.tr|\.net|\.org|\.tr|@)",
        re.IGNORECASE
    )
    
    best_col = None
    best_hits = 0
    
    for col in df.columns:
        # Count rows with URL/domain patterns
        try:
            hits = df[col].astype(str).str.contains(url_pattern, na=False).sum()
            if hits > best_hits:
                best_hits = hits
                best_col = col
        except Exception:
            # Skip columns that can't be analyzed
            continue
    
    return best_col

