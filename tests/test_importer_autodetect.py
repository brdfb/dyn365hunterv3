"""Tests for column auto-detection in importer."""

import pytest
import pandas as pd
from app.core.importer import guess_company_column, guess_domain_column


class TestColumnGuessing:
    """Test column detection heuristics."""

    def test_guess_company_column_by_name(self):
        """Test company column detection by column name hints."""
        df = pd.DataFrame(
            {
                "Firma Adı": ["A Şirketi", "B Şirketi"],
                "Web": ["example.com", "test.com"],
            }
        )
        result = guess_company_column(df)

        assert result == "Firma Adı"

    def test_guess_company_column_by_unvan(self):
        """Test company column detection with 'ünvan' hint."""
        df = pd.DataFrame({"Ünvan": ["A Şirketi"], "Website": ["example.com"]})
        result = guess_company_column(df)

        assert result == "Ünvan"

    def test_guess_company_column_fallback(self):
        """Test company column fallback to first column."""
        df = pd.DataFrame({"Company": ["A Şirketi"], "Domain": ["example.com"]})
        result = guess_company_column(df)

        assert result == "Company"

    def test_guess_company_column_empty_dataframe(self):
        """Test company column detection with empty DataFrame."""
        df = pd.DataFrame()
        result = guess_company_column(df)

        assert result is None

    def test_guess_domain_column_by_name(self):
        """Test domain column detection by column name hints."""
        df = pd.DataFrame({"Firma": ["A Şirketi"], "Website": ["example.com"]})
        result = guess_domain_column(df)

        assert result == "Website"

    def test_guess_domain_column_by_web(self):
        """Test domain column detection with 'web' hint."""
        df = pd.DataFrame({"Firma": ["A Şirketi"], "Web": ["example.com"]})
        result = guess_domain_column(df)

        assert result == "Web"

    def test_guess_domain_column_by_content(self):
        """Test domain column detection by content analysis."""
        df = pd.DataFrame(
            {
                "Firma": ["A Şirketi", "B Şirketi"],
                "Adres": ["https://example.com", "www.test.com"],
            }
        )
        result = guess_domain_column(df)

        assert result == "Adres"

    def test_guess_domain_column_by_email_content(self):
        """Test domain column detection with email addresses."""
        df = pd.DataFrame({"Firma": ["A Şirketi"], "İletişim": ["info@example.com"]})
        result = guess_domain_column(df)

        assert result == "İletişim"

    def test_guess_domain_column_empty_dataframe(self):
        """Test domain column detection with empty DataFrame."""
        df = pd.DataFrame()
        result = guess_domain_column(df)

        assert result is None

    def test_guess_domain_column_no_matches(self):
        """Test domain column detection when no hints match."""
        df = pd.DataFrame({"Column1": ["Value1"], "Column2": ["Value2"]})
        result = guess_domain_column(df)

        # Should return None or best guess based on content
        assert result is None or result in df.columns


class TestOSBFormatExamples:
    """Test column detection with real OSB format examples."""

    def test_osb_format_turkish(self):
        """Test with Turkish OSB format."""
        df = pd.DataFrame(
            {
                "Firma Ünvanı": ["ABC Teknoloji A.Ş.", "XYZ İnşaat Ltd."],
                "Web Sitesi": ["https://abc.com.tr", "www.xyz.com"],
            }
        )

        company_col = guess_company_column(df)
        domain_col = guess_domain_column(df)

        assert company_col == "Firma Ünvanı"
        assert domain_col == "Web Sitesi"

    def test_osb_format_mixed(self):
        """Test with mixed Turkish/English column names."""
        df = pd.DataFrame({"Company Name": ["ABC Corp"], "Website": ["example.com"]})

        company_col = guess_company_column(df)
        domain_col = guess_domain_column(df)

        assert company_col == "Company Name"
        assert domain_col == "Website"

    def test_osb_format_url_in_domain_column(self):
        """Test with full URLs in domain column."""
        df = pd.DataFrame(
            {
                "Firma": ["A Şirketi", "B Şirketi"],
                "İnternet Adresi": ["http://example.com/path", "https://test.com.tr"],
            }
        )

        domain_col = guess_domain_column(df)

        assert domain_col == "İnternet Adresi"
