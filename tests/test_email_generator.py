"""Tests for email generator module."""
import pytest
from app.core.email_generator import generate_generic_emails, GENERIC_LOCAL_PARTS


class TestEmailGenerator:
    """Test email generation functionality."""
    
    def test_generate_generic_emails_basic(self):
        """Test basic email generation."""
        domain = "example.com"
        emails = generate_generic_emails(domain)
        
        # Should generate emails for all generic local parts
        assert len(emails) == len(GENERIC_LOCAL_PARTS)
        
        # All emails should contain the domain
        assert all(f"@{domain}" in email for email in emails)
        
        # Should be sorted
        assert emails == sorted(emails)
        
        # Should contain expected emails
        assert "info@example.com" in emails
        assert "sales@example.com" in emails
        assert "admin@example.com" in emails
    
    def test_generate_generic_emails_normalization(self):
        """Test that domain normalization works."""
        # Test with www prefix
        emails_www = generate_generic_emails("www.example.com")
        emails_normal = generate_generic_emails("example.com")
        
        # Should produce same results
        assert emails_www == emails_normal
        
        # Test with uppercase
        emails_upper = generate_generic_emails("EXAMPLE.COM")
        assert emails_upper == emails_normal
    
    def test_generate_generic_emails_turkish_domain(self):
        """Test with Turkish domain."""
        # Use punycode encoded Turkish domain (xn--rnek-7ya.com)
        # or test with ASCII domain since normalize_domain converts to punycode
        domain = "xn--rnek-7ya.com"  # "örnek.com" in punycode
        emails = generate_generic_emails(domain)
        
        # Should generate emails (normalize_domain will handle punycode)
        assert len(emails) > 0
        
        # Should contain Turkish generic emails
        assert any("iletisim@" in email for email in emails)
        assert any("satis@" in email for email in emails)
        assert any("muhasebe@" in email for email in emails)
    
    def test_generate_generic_emails_empty_domain(self):
        """Test with empty domain."""
        emails = generate_generic_emails("")
        assert emails == []
    
    def test_generate_generic_emails_invalid_domain(self):
        """Test with invalid domain."""
        emails = generate_generic_emails("   ")
        assert emails == []
    
    def test_generate_generic_emails_no_duplicates(self):
        """Test that no duplicate emails are generated."""
        domain = "example.com"
        emails = generate_generic_emails(domain)
        
        # Should have no duplicates
        assert len(emails) == len(set(emails))
    
    def test_generate_generic_emails_all_local_parts(self):
        """Test that all generic local parts are included."""
        domain = "example.com"
        emails = generate_generic_emails(domain)
        
        # Check that all local parts are present
        for local_part in GENERIC_LOCAL_PARTS:
            expected_email = f"{local_part}@{domain}"
            assert expected_email in emails
    
    def test_generate_generic_emails_subdomain(self):
        """Test with subdomain."""
        domain = "mail.example.com"
        emails = generate_generic_emails(domain)
        
        # Should generate emails with full subdomain
        assert all(f"@{domain}" in email for email in emails)
        assert "info@mail.example.com" in emails

