"""Tests for D365 client (Faz 2: Client + Mapping)."""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from app.integrations.d365.client import D365Client
from app.integrations.d365.errors import (
    D365AuthenticationError,
    D365APIError,
    D365RateLimitError,
    D365DuplicateError,
)


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock D365 settings."""
    mock_settings_obj = Mock()
    mock_settings_obj.d365_enabled = True
    mock_settings_obj.d365_base_url = "https://testorg.crm.dynamics.com"
    mock_settings_obj.d365_client_id = "test_client_id"
    mock_settings_obj.d365_client_secret = "test_client_secret"
    mock_settings_obj.d365_tenant_id = "test_tenant_id"
    mock_settings_obj.d365_api_version = "v9.2"
    monkeypatch.setattr("app.integrations.d365.client.settings", mock_settings_obj)
    return mock_settings_obj


@pytest.fixture
def d365_client(mock_settings):
    """Create D365 client instance."""
    # Mock MSAL ConfidentialClientApplication to avoid real tenant discovery
    with patch("app.integrations.d365.client.ConfidentialClientApplication") as mock_msal:
        mock_app = MagicMock()
        mock_msal.return_value = mock_app
        client = D365Client()
        client.app = mock_app  # Use mocked app
        return client


def test_d365_client_init_disabled(monkeypatch):
    """Test D365 client initialization fails when disabled."""
    monkeypatch.setattr("app.integrations.d365.client.settings", Mock(
        d365_enabled=False,
    ))
    
    with pytest.raises(ValueError, match="disabled"):
        D365Client()


def test_d365_client_init_missing_credentials(monkeypatch):
    """Test D365 client initialization fails when credentials missing."""
    monkeypatch.setattr("app.integrations.d365.client.settings", Mock(
        d365_enabled=True,
        d365_base_url=None,
        d365_client_id=None,
    ))
    
    with pytest.raises(ValueError, match="credentials"):
        D365Client()


def test_get_access_token_success(d365_client):
    """Test successful token acquisition."""
    d365_client.app.acquire_token_for_client.return_value = {
        "access_token": "test_token",
        "expires_in": 3600,
    }
    
    token = d365_client._get_access_token()
    
    assert token == "test_token"
    assert d365_client._token == "test_token"
    d365_client.app.acquire_token_for_client.assert_called_once()


def test_get_access_token_failure(d365_client):
    """Test token acquisition failure."""
    d365_client.app.acquire_token_for_client.return_value = {
        "error": "invalid_client",
        "error_description": "Client authentication failed",
    }
    
    with pytest.raises(D365AuthenticationError):
        d365_client._get_access_token()


@pytest.mark.asyncio
async def test_create_or_update_lead_create(d365_client):
    """Test creating a new lead in D365."""
    # Mock token acquisition
    d365_client.app.acquire_token_for_client.return_value = {
        "access_token": "test_token",
        "expires_in": 3600,
    }
    
    # Mock HTTP client
    payload = {
        "subject": "Hunter: example.com",
        "companyname": "Example Inc",
    }
    
    # Mock _find_lead_by_email to return None (no existing lead)
    d365_client._find_lead_by_email = AsyncMock(return_value=None)
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 201
        # httpx response.json() is synchronous, not async
        mock_response.json = Mock(return_value={"leadid": "test_lead_id"})
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        result = await d365_client.create_or_update_lead(payload)
        
        assert result["leadid"] == "test_lead_id"
        mock_client_instance.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_or_update_lead_rate_limit(d365_client):
    """Test rate limit error handling."""
    d365_client.app.acquire_token_for_client.return_value = {
        "access_token": "test_token",
        "expires_in": 3600,
    }
    
    payload = {"subject": "Hunter: example.com"}
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 429
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        with pytest.raises(D365RateLimitError):
            await d365_client.create_or_update_lead(payload)


@pytest.mark.asyncio
async def test_create_or_update_lead_duplicate(d365_client):
    """Test duplicate lead error handling."""
    d365_client.app.acquire_token_for_client.return_value = {
        "access_token": "test_token",
        "expires_in": 3600,
    }
    
    payload = {"subject": "Hunter: example.com", "emailaddress1": "test@example.com"}
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 409
        mock_response.text = "Duplicate lead"
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        with pytest.raises(D365DuplicateError):
            await d365_client.create_or_update_lead(payload)

