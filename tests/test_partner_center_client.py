"""Unit tests for Partner Center API client."""

import pytest
from unittest.mock import patch, MagicMock
import httpx
from app.core.partner_center import PartnerCenterClient
from app.core.exceptions import PartnerCenterAuthError, PartnerCenterRateLimitError


@pytest.fixture
def mock_settings():
    """Mock settings for Partner Center."""
    with patch("app.core.partner_center.settings") as mock:
        mock.partner_center_enabled = True
        mock.partner_center_client_id = "test-client-id"
        mock.partner_center_tenant_id = "test-tenant-id"
        mock.partner_center_api_url = "https://api.partner.microsoft.com"
        mock.partner_center_scope = "https://api.partner.microsoft.com/.default"
        mock.partner_center_token_cache_path = None
        mock.partner_center_api_version = "v1.0"
        mock.partner_center_referral_max_pages = 10
        mock.partner_center_referral_default_direction = "Incoming"
        mock.partner_center_referral_default_status = "Active"
        mock.partner_center_referral_default_top = 200
        yield mock


@pytest.fixture
def mock_msal():
    """Mock MSAL PublicClientApplication."""
    with patch("app.core.partner_center.PublicClientApplication") as mock:
        mock_app = MagicMock()
        mock.return_value = mock_app
        
        # Mock token acquisition
        mock_account = MagicMock()
        mock_account.get.return_value = "test@example.com"
        mock_app.get_accounts.return_value = [mock_account]
        mock_app.acquire_token_silent.return_value = {"access_token": "test-token"}
        
        yield mock_app


class TestGetReferrals:
    """Test Phase 6.1: PartnerCenterClient.get_referrals()."""
    
    def test_get_referrals_single_page(self, mock_settings, mock_msal):
        """Test: 200 OK + single page → returns referrals."""
        client = PartnerCenterClient()
        
        # Mock _fetch_page to return single page
        with patch.object(client, "_fetch_page") as mock_fetch:
            mock_fetch.return_value = {
                "value": [
                    {"id": "ref-1", "name": "Referral 1"},
                    {"id": "ref-2", "name": "Referral 2"},
                ]
            }
            
            referrals = client.get_referrals()
            
            assert len(referrals) == 2
            assert referrals[0]["id"] == "ref-1"
            assert referrals[1]["id"] == "ref-2"
    
    def test_get_referrals_pagination(self, mock_settings, mock_msal):
        """Test: 200 OK + pagination (@odata.nextLink) → returns all pages."""
        client = PartnerCenterClient()
        
        # Mock _fetch_page to return paginated responses
        with patch.object(client, "_fetch_page") as mock_fetch:
            mock_fetch.side_effect = [
                {
                    "value": [{"id": "ref-1", "name": "Referral 1"}],
                    "@odata.nextLink": "https://api.partner.microsoft.com/v1.0/engagements/referrals?$skip=1"
                },
                {
                    "value": [{"id": "ref-2", "name": "Referral 2"}]
                }
            ]
            
            with patch("time.sleep"):  # Skip sleep for faster tests
                referrals = client.get_referrals()
            
            assert len(referrals) == 2
            assert referrals[0]["id"] == "ref-1"
            assert referrals[1]["id"] == "ref-2"
            assert mock_fetch.call_count == 2
    
    def test_get_referrals_401_auth_error(self, mock_settings, mock_msal):
        """Test: 401 → raises PartnerCenterAuthError."""
        client = PartnerCenterClient()
        
        # Mock _fetch_page to raise 401 error
        with patch.object(client, "_fetch_page") as mock_fetch:
            mock_fetch.side_effect = PartnerCenterAuthError(
                "Authentication failed", 401, "req-123"
            )
            
            with pytest.raises(PartnerCenterAuthError) as exc_info:
                client.get_referrals()
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.request_id == "req-123"
    
    def test_get_referrals_403_auth_error(self, mock_settings, mock_msal):
        """Test: 403 → raises PartnerCenterAuthError (no retry)."""
        client = PartnerCenterClient()
        
        # Mock _fetch_page to raise 403 error
        with patch.object(client, "_fetch_page") as mock_fetch:
            mock_fetch.side_effect = PartnerCenterAuthError(
                "Forbidden", 403, "req-456"
            )
            
            with pytest.raises(PartnerCenterAuthError) as exc_info:
                client.get_referrals()
            
            assert exc_info.value.status_code == 403
            assert exc_info.value.request_id == "req-456"
    
    def test_get_referrals_429_rate_limit_error(self, mock_settings, mock_msal):
        """Test: 429 → raises PartnerCenterRateLimitError after retries."""
        client = PartnerCenterClient()
        
        # Mock 429 response with Retry-After header
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {
            "request-id": "req-789",
            "Retry-After": "5"
        }
        # Mock _fetch_page to raise rate limit error
        # Note: Retry logic (3 retries) is tested in _fetch_page unit tests
        with patch.object(client, "_fetch_page") as mock_fetch:
            mock_fetch.side_effect = PartnerCenterRateLimitError(
                "Rate limit exceeded", 5, "req-789"
            )
            
            with patch("time.sleep"):  # Skip sleep for faster tests
                with pytest.raises(PartnerCenterRateLimitError) as exc_info:
                    client.get_referrals()
            
            assert exc_info.value.retry_after == 5
            assert exc_info.value.request_id == "req-789"
    
    def test_get_referrals_500_server_error_retry(self, mock_settings, mock_msal):
        """Test: 5xx → retries with exponential backoff, then raises."""
        client = PartnerCenterClient()
        
        # Mock 500 response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.headers = {"request-id": "req-500"}
        # Mock _fetch_page to raise 500 error
        # Note: Retry logic (3 retries) is tested in _fetch_page unit tests
        with patch.object(client, "_fetch_page") as mock_fetch:
            http_error = httpx.HTTPStatusError(
                "Internal Server Error",
                request=MagicMock(),
                response=mock_response
            )
            mock_fetch.side_effect = http_error
            
            with patch("time.sleep"):  # Skip sleep for faster tests
                with pytest.raises(httpx.HTTPStatusError):
                    client.get_referrals()

