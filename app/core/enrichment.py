"""Lead enrichment logic for contact emails, quality scores, and LinkedIn patterns."""

import re
from typing import List, Optional
from app.core.normalizer import normalize_domain


def calculate_contact_quality_score(emails: List[str], domain: str) -> int:
    """
    Calculate contact quality score (0-100) based on email count and domain matching.

    Args:
        emails: List of contact email addresses
        domain: Company domain (normalized)

    Returns:
        Quality score (0-100)
    """
    if not emails:
        return 0

    score = 0

    # Email count factor (max 60 points)
    # More emails = higher score, but with diminishing returns
    email_count = len(emails)
    if email_count >= 10:
        score += 60
    elif email_count >= 5:
        score += 45
    elif email_count >= 3:
        score += 30
    elif email_count >= 2:
        score += 20
    else:
        score += 10

    # Domain match factor (max 40 points)
    # Emails matching the company domain get bonus points
    normalized_domain = normalize_domain(domain)
    matching_count = 0

    for email in emails:
        if "@" in email:
            email_domain = email.split("@")[1].lower()
            email_domain = normalize_domain(email_domain)
            if email_domain == normalized_domain:
                matching_count += 1

    if matching_count > 0:
        # Percentage of emails matching domain
        match_ratio = matching_count / email_count
        score += int(40 * match_ratio)

    return min(100, score)


def detect_linkedin_pattern(emails: List[str]) -> Optional[str]:
    """
    Detect LinkedIn email pattern from contact emails.

    Patterns detected:
    - firstname.lastname@domain.com
    - f.lastname@domain.com
    - firstname@domain.com

    Args:
        emails: List of contact email addresses

    Returns:
        Detected pattern string or None
    """
    if not emails:
        return None

    patterns = {
        "firstname.lastname": r"^[a-z]+\.[a-z]+@",
        "f.lastname": r"^[a-z]\.[a-z]+@",
        "firstname": r"^[a-z]+@",
    }

    pattern_counts = {"firstname.lastname": 0, "f.lastname": 0, "firstname": 0}

    for email in emails:
        email_lower = email.lower().strip()
        if "@" not in email_lower:
            continue

        local_part = email_lower.split("@")[0]

        # Check each pattern
        for pattern_name, pattern_regex in patterns.items():
            if re.match(pattern_regex, local_part):
                pattern_counts[pattern_name] += 1
                break

    # Return the most common pattern
    if any(count > 0 for count in pattern_counts.values()):
        most_common = max(pattern_counts.items(), key=lambda x: x[1])
        if most_common[1] > 0:
            return most_common[0]

    return None


def enrich_company_data(emails: List[str], domain: str) -> dict:
    """
    Enrich company data with contact emails, quality score, and LinkedIn pattern.

    Args:
        emails: List of contact email addresses
        domain: Company domain

    Returns:
        Dictionary with enrichment data:
        - contact_emails: List[str]
        - contact_quality_score: int
        - linkedin_pattern: Optional[str]
    """
    # Normalize and deduplicate emails
    normalized_emails = []
    seen = set()

    for email in emails:
        if not email or not isinstance(email, str):
            continue
        email = email.strip().lower()
        if email and "@" in email and email not in seen:
            normalized_emails.append(email)
            seen.add(email)

    # Calculate quality score
    quality_score = calculate_contact_quality_score(normalized_emails, domain)

    # Detect LinkedIn pattern
    linkedin_pattern = detect_linkedin_pattern(normalized_emails)

    return {
        "contact_emails": normalized_emails,
        "contact_quality_score": quality_score,
        "linkedin_pattern": linkedin_pattern,
    }
