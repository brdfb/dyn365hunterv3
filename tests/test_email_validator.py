"""Tests for email validator module."""

import pytest
from unittest.mock import patch, MagicMock
import smtplib
from app.core.email_validator import (
    validate_email_syntax,
    validate_email_mx,
    validate_email_smtp,
    validate_email,
    EmailValidationResult,
)


class TestEmailSyntaxValidation:
    """Test email syntax validation."""

    def test_validate_email_syntax_valid(self):
        """Test valid email syntax."""
        assert validate_email_syntax("test@example.com") is True
        assert validate_email_syntax("user.name@example.com") is True
        assert validate_email_syntax("user+tag@example.co.uk") is True
        assert validate_email_syntax("user_name@example-domain.com") is True

    def test_validate_email_syntax_invalid(self):
        """Test invalid email syntax."""
        assert validate_email_syntax("invalid-email") is False
        assert validate_email_syntax("@example.com") is False
        assert validate_email_syntax("user@") is False
        assert validate_email_syntax("user@example") is False  # No TLD
        assert validate_email_syntax("user @example.com") is False  # Space
        assert validate_email_syntax("") is False


class TestEmailMXValidation:
    """Test MX record validation."""

    @patch("app.core.email_validator.get_mx_records")
    def test_validate_email_mx_with_records(self, mock_get_mx):
        """Test MX validation when records exist."""
        mock_get_mx.return_value = ["mail.example.com", "mail2.example.com"]

        has_mx, error = validate_email_mx("example.com")

        assert has_mx is True
        assert error is None
        mock_get_mx.assert_called_once_with("example.com")

    @patch("app.core.email_validator.get_mx_records")
    def test_validate_email_mx_no_records(self, mock_get_mx):
        """Test MX validation when no records exist."""
        mock_get_mx.return_value = []

        has_mx, error = validate_email_mx("example.com")

        assert has_mx is False
        assert error is None
        mock_get_mx.assert_called_once_with("example.com")

    @patch("app.core.email_validator.get_mx_records")
    def test_validate_email_mx_exception(self, mock_get_mx):
        """Test MX validation when exception occurs."""
        mock_get_mx.side_effect = Exception("DNS error")

        has_mx, error = validate_email_mx("example.com")

        assert has_mx is False
        assert error == "DNS error"


class TestEmailSMTPValidation:
    """Test SMTP validation."""

    @patch("app.core.email_validator.get_mx_records")
    @patch("smtplib.SMTP")
    def test_validate_email_smtp_valid(self, mock_smtp_class, mock_get_mx):
        """Test SMTP validation when email is valid."""
        mock_get_mx.return_value = ["mail.example.com"]
        mock_server = MagicMock()
        mock_smtp_class.return_value = mock_server
        mock_server.rcpt.return_value = (250, "OK")

        status, reason = validate_email_smtp("test@example.com")

        assert status == "valid"
        assert "SMTP 250" in reason
        mock_server.helo.assert_called_once()
        mock_server.mail.assert_called_once()
        mock_server.rcpt.assert_called_once_with("test@example.com")
        mock_server.quit.assert_called_once()

    @patch("app.core.email_validator.get_mx_records")
    @patch("smtplib.SMTP")
    def test_validate_email_smtp_invalid(self, mock_smtp_class, mock_get_mx):
        """Test SMTP validation when email is invalid."""
        mock_get_mx.return_value = ["mail.example.com"]
        mock_server = MagicMock()
        mock_smtp_class.return_value = mock_server
        mock_server.rcpt.return_value = (550, "User unknown")

        status, reason = validate_email_smtp("invalid@example.com")

        assert status == "invalid"
        assert "SMTP 550" in reason

    @patch("app.core.email_validator.get_mx_records")
    @patch("smtplib.SMTP")
    def test_validate_email_smtp_unknown(self, mock_smtp_class, mock_get_mx):
        """Test SMTP validation when status is unknown (catch-all)."""
        mock_get_mx.return_value = ["mail.example.com"]
        mock_server = MagicMock()
        mock_smtp_class.return_value = mock_server
        mock_server.rcpt.return_value = (451, "Temporary failure")

        status, reason = validate_email_smtp("test@example.com")

        assert status == "unknown"
        assert "SMTP 451" in reason

    @patch("app.core.email_validator.get_mx_records")
    def test_validate_email_smtp_no_mx(self, mock_get_mx):
        """Test SMTP validation when no MX records exist."""
        mock_get_mx.return_value = []

        status, reason = validate_email_smtp("test@example.com")

        assert status == "unknown"
        assert "No MX records" in reason

    @patch("app.core.email_validator.get_mx_records")
    @patch("smtplib.SMTP")
    def test_validate_email_smtp_connection_error(self, mock_smtp_class, mock_get_mx):
        """Test SMTP validation when connection fails."""
        mock_get_mx.return_value = ["mail.example.com"]
        mock_smtp_class.side_effect = smtplib.SMTPConnectError(
            421, "Connection refused"
        )

        status, reason = validate_email_smtp("test@example.com")

        assert status == "unknown"
        assert "SMTP connection failed" in reason

    @patch("app.core.email_validator.get_mx_records")
    @patch("smtplib.SMTP")
    def test_validate_email_smtp_timeout(self, mock_smtp_class, mock_get_mx):
        """Test SMTP validation when timeout occurs."""
        import socket

        mock_get_mx.return_value = ["mail.example.com"]
        mock_smtp_class.side_effect = socket.timeout("Connection timeout")

        status, reason = validate_email_smtp("test@example.com")

        assert status == "unknown"
        assert "timeout" in reason.lower() or "Connection timeout" in reason

    def test_validate_email_smtp_invalid_format(self):
        """Test SMTP validation with invalid email format."""
        status, reason = validate_email_smtp("invalid-email")

        assert status == "invalid"
        assert "Invalid email format" in reason


class TestEmailValidation:
    """Test full email validation flow."""

    @patch("app.core.email_validator.validate_email_mx")
    def test_validate_email_syntax_invalid(self, mock_mx):
        """Test validation with invalid syntax."""
        result = validate_email("invalid-email", use_smtp=False)

        assert result.status == "invalid"
        assert result.confidence == "high"
        assert result.checks["syntax"] is False
        assert result.checks["mx"] is False
        assert result.checks["smtp"] == "skipped"
        assert "Invalid email syntax" in result.reason

    @patch("app.core.email_validator.validate_email_mx")
    def test_validate_email_no_mx(self, mock_mx):
        """Test validation when no MX records exist."""
        mock_mx.return_value = (False, "No MX records found")

        result = validate_email("test@example.com", use_smtp=False)

        assert result.status == "invalid"
        assert result.confidence == "high"
        assert result.checks["syntax"] is True
        assert result.checks["mx"] is False
        assert result.checks["smtp"] == "skipped"
        assert "No MX records" in result.reason

    @patch("app.core.email_validator.validate_email_mx")
    def test_validate_email_valid_no_smtp(self, mock_mx):
        """Test validation with valid syntax and MX, no SMTP."""
        mock_mx.return_value = (True, None)

        result = validate_email("test@example.com", use_smtp=False)

        assert result.status == "valid"
        assert result.confidence == "medium"
        assert result.checks["syntax"] is True
        assert result.checks["mx"] is True
        assert result.checks["smtp"] == "skipped"
        assert "Valid syntax and MX records" in result.reason

    @patch("app.core.email_validator.validate_email_smtp")
    @patch("app.core.email_validator.validate_email_mx")
    def test_validate_email_valid_with_smtp(self, mock_mx, mock_smtp):
        """Test validation with SMTP check (valid)."""
        mock_mx.return_value = (True, None)
        mock_smtp.return_value = ("valid", "SMTP 250")

        result = validate_email("test@example.com", use_smtp=True)

        assert result.status == "valid"
        assert result.confidence == "high"
        assert result.checks["syntax"] is True
        assert result.checks["mx"] is True
        assert result.checks["smtp"] == "valid"
        assert "SMTP 250" in result.reason

    @patch("app.core.email_validator.validate_email_smtp")
    @patch("app.core.email_validator.validate_email_mx")
    def test_validate_email_invalid_with_smtp(self, mock_mx, mock_smtp):
        """Test validation with SMTP check (invalid)."""
        mock_mx.return_value = (True, None)
        mock_smtp.return_value = ("invalid", "SMTP 550")

        result = validate_email("test@example.com", use_smtp=True)

        assert result.status == "invalid"
        assert result.confidence == "high"
        assert result.checks["syntax"] is True
        assert result.checks["mx"] is True
        assert result.checks["smtp"] == "invalid"
        assert "SMTP 550" in result.reason

    @patch("app.core.email_validator.validate_email_smtp")
    @patch("app.core.email_validator.validate_email_mx")
    def test_validate_email_unknown_with_smtp(self, mock_mx, mock_smtp):
        """Test validation with SMTP check (unknown/catch-all)."""
        mock_mx.return_value = (True, None)
        mock_smtp.return_value = ("unknown", "SMTP 451")

        result = validate_email("test@example.com", use_smtp=True)

        assert result.status == "unknown"
        assert result.confidence == "medium"
        assert result.checks["syntax"] is True
        assert result.checks["mx"] is True
        assert result.checks["smtp"] == "unknown"
        assert "SMTP 451" in result.reason

    def test_validate_email_invalid_format(self):
        """Test validation with invalid email format (no @)."""
        result = validate_email("invalid-email", use_smtp=False)

        assert result.status == "invalid"
        assert result.confidence == "high"
        assert "Invalid email syntax" in result.reason  # Syntax check happens first
