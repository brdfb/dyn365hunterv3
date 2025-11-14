"""Email validation utilities (syntax, MX, optional SMTP)."""

from dataclasses import dataclass
from typing import Literal, Dict, Optional, Any
import re
import smtplib
from app.core.analyzer_dns import get_mx_records

EmailStatus = Literal["valid", "invalid", "unknown"]
ConfidenceLevel = Literal["high", "medium", "low"]

# Email syntax regex (RFC 5322 simplified)
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass
class EmailValidationResult:
    """Email validation result."""

    email: str
    status: EmailStatus
    confidence: ConfidenceLevel
    checks: Dict[str, Any]
    reason: Optional[str] = None


def validate_email_syntax(email: str) -> bool:
    """
    Check email syntax validity.

    Args:
        email: Email address to validate

    Returns:
        True if syntax is valid, False otherwise
    """
    return bool(EMAIL_PATTERN.match(email))


def validate_email_mx(domain: str) -> tuple[bool, Optional[str]]:
    """
    Check if domain has MX records.

    Args:
        domain: Domain name to check

    Returns:
        Tuple of (has_mx, error_message)
        - has_mx: True if MX records exist, False otherwise
        - error_message: Error message if check failed, None otherwise
    """
    try:
        mx_records = get_mx_records(domain)
        return (len(mx_records) > 0, None)
    except Exception as e:
        return (False, str(e))


def validate_email_smtp(email: str, timeout: float = 3.0) -> tuple[EmailStatus, str]:
    """
    Validate email via SMTP RCPT TO check.

    Args:
        email: Email address to validate
        timeout: SMTP connection timeout in seconds (default: 3.0)

    Returns:
        Tuple of (status, reason)
        - status: "valid", "invalid", or "unknown"
        - reason: Human-readable reason for the status
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
    except (smtplib.SMTPException, TimeoutError, OSError) as e:
        # Handle timeout and other connection errors
        return ("unknown", f"SMTP error: {str(e)}")
    except Exception as e:
        return ("unknown", str(e))


def validate_email(
    email: str, use_smtp: bool = False, smtp_timeout: float = 3.0
) -> EmailValidationResult:
    """
    Validate email address (syntax + MX + optional SMTP).

    Args:
        email: Email address to validate
        use_smtp: If True, perform SMTP check (default: False)
        smtp_timeout: SMTP connection timeout in seconds (default: 3.0)

    Returns:
        EmailValidationResult with status, confidence, and checks
    """
    checks: Dict[str, Any] = {"syntax": False, "mx": False, "smtp": "skipped"}

    # 1) Syntax check
    syntax_valid = validate_email_syntax(email)
    checks["syntax"] = syntax_valid

    if not syntax_valid:
        return EmailValidationResult(
            email=email,
            status="invalid",
            confidence="high",
            checks=checks,
            reason="Invalid email syntax",
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
            reason="Invalid email format",
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
            reason=f"No MX records: {mx_error}" if mx_error else "No MX records",
        )

    # 3) SMTP check (optional)
    if use_smtp:
        smtp_status, smtp_reason = validate_email_smtp(email, timeout=smtp_timeout)
        checks["smtp"] = smtp_status

        # Determine confidence based on SMTP result
        if smtp_status == "valid":
            confidence: ConfidenceLevel = "high"
        elif smtp_status == "invalid":
            confidence = "high"
        else:  # unknown (catch-all, greylisting, etc.)
            confidence = "medium"

        return EmailValidationResult(
            email=email,
            status=smtp_status,
            confidence=confidence,
            checks=checks,
            reason=smtp_reason,
        )
    else:
        # Syntax + MX valid → medium confidence (no SMTP check)
        return EmailValidationResult(
            email=email,
            status="valid",
            confidence="medium",
            checks=checks,
            reason="Valid syntax and MX records (SMTP not checked)",
        )
