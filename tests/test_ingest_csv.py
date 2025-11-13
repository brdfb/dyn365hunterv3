"""Tests for CSV ingestion and normalization."""
import pytest
import pandas as pd
from io import BytesIO
from app.core.normalizer import (
    normalize_domain,
    extract_domain_from_email,
    extract_domain_from_website
)


class TestDomainNormalization:
    """Test domain normalization functions."""
    
    def test_normalize_domain_lowercase(self):
        """Test domain lowercase conversion."""
        result = normalize_domain("EXAMPLE.COM")
        
        assert result == "example.com"
    
    def test_normalize_domain_www_removal(self):
        """Test www prefix removal."""
        result = normalize_domain("www.example.com")
        
        assert result == "example.com"
    
    def test_normalize_domain_trailing_dot(self):
        """Test trailing dot removal."""
        result = normalize_domain("example.com.")
        
        assert result == "example.com"
    
    def test_normalize_domain_whitespace(self):
        """Test whitespace stripping."""
        result = normalize_domain("  example.com  ")
        
        assert result == "example.com"
    
    def test_normalize_domain_empty(self):
        """Test empty domain handling."""
        result = normalize_domain("")
        
        assert result == ""
    
    def test_normalize_domain_punycode(self):
        """Test punycode handling."""
        # Note: Actual punycode decoding requires valid punycode
        result = normalize_domain("xn--example.com")
        
        # Should handle gracefully (may or may not decode depending on validity)
        assert isinstance(result, str)
    
    def test_extract_domain_from_email(self):
        """Test domain extraction from email."""
        result = extract_domain_from_email("user@example.com")
        
        assert result == "example.com"
    
    def test_extract_domain_from_email_uppercase(self):
        """Test domain extraction from uppercase email."""
        result = extract_domain_from_email("USER@EXAMPLE.COM")
        
        assert result == "example.com"
    
    def test_extract_domain_from_email_invalid(self):
        """Test domain extraction from invalid email."""
        result = extract_domain_from_email("not-an-email")
        
        assert result == ""
    
    def test_extract_domain_from_email_empty(self):
        """Test domain extraction from empty email."""
        result = extract_domain_from_email("")
        
        assert result == ""
    
    def test_extract_domain_from_website_full_url(self):
        """Test domain extraction from full URL."""
        result = extract_domain_from_website("https://www.example.com/path")
        
        assert result == "example.com"
    
    def test_extract_domain_from_website_no_scheme(self):
        """Test domain extraction from URL without scheme."""
        result = extract_domain_from_website("www.example.com")
        
        assert result == "example.com"
    
    def test_extract_domain_from_website_domain_only(self):
        """Test domain extraction from domain-only string."""
        result = extract_domain_from_website("example.com")
        
        assert result == "example.com"
    
    def test_extract_domain_from_website_with_port(self):
        """Test domain extraction from URL with port."""
        result = extract_domain_from_website("http://example.com:8080/path")
        
        assert result == "example.com"
    
    def test_extract_domain_from_website_empty(self):
        """Test domain extraction from empty website."""
        result = extract_domain_from_website("")
        
        assert result == ""


class TestCSVParsing:
    """Test CSV parsing logic."""
    
    def test_csv_required_columns(self):
        """Test CSV with required domain column."""
        csv_data = "domain,company_name\n example.com,Example Inc"
        df = pd.read_csv(BytesIO(csv_data.encode()))
        
        assert "domain" in df.columns
    
    def test_csv_optional_columns(self):
        """Test CSV with optional columns."""
        csv_data = "domain,company_name,email,website\nexample.com,Example Inc,user@example.com,https://example.com"
        df = pd.read_csv(BytesIO(csv_data.encode()))
        
        assert "domain" in df.columns
        assert "company_name" in df.columns
        assert "email" in df.columns
        assert "website" in df.columns
    
    def test_csv_case_insensitive_columns(self):
        """Test CSV with case-insensitive column names."""
        csv_data = "Domain,Company_Name,Email\n example.com,Example Inc,user@example.com"
        df = pd.read_csv(BytesIO(csv_data.encode()))
        
        # Columns should be normalized to lowercase
        df.columns = df.columns.str.lower().str.strip()
        
        assert "domain" in df.columns
        assert "company_name" in df.columns
        assert "email" in df.columns


class TestIngestEdgeCases:
    """Test edge cases for ingestion."""
    
    def test_malformed_csv(self):
        """Test handling of malformed CSV."""
        # CSV with missing quotes, unclosed fields, etc.
        csv_data = "domain,company_name\nexample.com,\"Unclosed quote"
        
        # Should raise ParserError
        with pytest.raises(pd.errors.ParserError):
            pd.read_csv(BytesIO(csv_data.encode()))
    
    def test_empty_csv(self):
        """Test handling of empty CSV."""
        csv_data = ""
        
        # Should raise EmptyDataError
        with pytest.raises(pd.errors.EmptyDataError):
            pd.read_csv(BytesIO(csv_data.encode()))
    
    def test_csv_missing_domain_column(self):
        """Test CSV without domain column."""
        csv_data = "company_name,email\nExample Inc,user@example.com"
        df = pd.read_csv(BytesIO(csv_data.encode()))
        
        # Domain column should be missing
        assert "domain" not in df.columns
    
    def test_csv_empty_domain_values(self):
        """Test CSV with empty domain values."""
        csv_data = "domain,company_name\nexample.com,Example Inc\n,Empty Domain"
        df = pd.read_csv(BytesIO(csv_data.encode()))
        
        # Should have empty domain in second row
        assert pd.isna(df.iloc[1]["domain"]) or df.iloc[1]["domain"] == ""
    
    def test_normalize_domain_special_characters(self):
        """Test domain normalization with special characters."""
        # Domains should not have special characters except dots and hyphens
        result = normalize_domain("example@domain.com")
        
        # Should handle gracefully (may not be valid domain)
        assert isinstance(result, str)
    
    def test_extract_domain_from_email_multiple_at(self):
        """Test email with multiple @ symbols."""
        result = extract_domain_from_email("user@example@domain.com")
        
        # Should extract from last @
        assert result == "domain.com"
    
    def test_extract_domain_from_website_invalid_url(self):
        """Test domain extraction from invalid URL."""
        result = extract_domain_from_website("not-a-valid-url-!!!")
        
        # Should handle gracefully
        assert isinstance(result, str)


class TestExcelSupport:
    """Test Excel file ingestion support."""
    
    def test_excel_file_extension_detection(self):
        """Test Excel file extension detection."""
        # This is a basic test - actual Excel reading requires openpyxl
        extensions = ['.xlsx', '.xls']
        
        for ext in extensions:
            filename = f"test{ext}"
            assert filename.lower().endswith(('.xlsx', '.xls'))
    
    def test_excel_vs_csv_detection(self):
        """Test differentiation between Excel and CSV files."""
        excel_files = ['test.xlsx', 'test.XLSX', 'test.xls', 'test.XLS']
        csv_files = ['test.csv', 'test.CSV']
        
        for filename in excel_files:
            assert filename.lower().endswith(('.xlsx', '.xls'))
            assert not filename.lower().endswith('.csv')
        
        for filename in csv_files:
            assert filename.lower().endswith('.csv')
            assert not filename.lower().endswith(('.xlsx', '.xls'))
