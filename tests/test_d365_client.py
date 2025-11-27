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


def test_get_access_token_redis_cache_hit(d365_client):
    """Test token retrieval from Redis cache."""
    from app.core.cache import set_cached_value
    from datetime import datetime, timedelta
    
    # Set cached token in Redis
    expires_at = datetime.now() + timedelta(hours=1)
    set_cached_value("d365_access_token", "cached_token_from_redis", ttl=3600)
    set_cached_value("d365_token_expires_at", expires_at.isoformat(), ttl=3600)
    
    # Mock Redis available
    with patch("app.integrations.d365.client.is_redis_available", return_value=True):
        with patch("app.integrations.d365.client.get_cached_value") as mock_get:
            mock_get.side_effect = lambda key: {
                "d365_access_token": "cached_token_from_redis",
                "d365_token_expires_at": expires_at.isoformat()
            }.get(key)
            
            token = d365_client._get_access_token()
            
            assert token == "cached_token_from_redis"
            # Should not call MSAL
            d365_client.app.acquire_token_for_client.assert_not_called()


def test_get_access_token_redis_cache_miss(d365_client):
    """Test token acquisition when Redis cache miss."""
    d365_client.app.acquire_token_for_client.return_value = {
        "access_token": "new_token_from_msal",
        "expires_in": 3600,
    }
    
    # Mock Redis available but cache miss
    with patch("app.integrations.d365.client.is_redis_available", return_value=True):
        with patch("app.integrations.d365.client.get_cached_value", return_value=None):
            with patch("app.integrations.d365.client.get_redis_client") as mock_redis:
                mock_redis_client = MagicMock()
                mock_redis_client.set.return_value = True  # Lock acquired
                mock_redis_client.delete.return_value = True
                mock_redis.return_value = mock_redis_client
                
                with patch("app.integrations.d365.client.set_cached_value"):
                    token = d365_client._get_access_token()
                    
                    assert token == "new_token_from_msal"
                    d365_client.app.acquire_token_for_client.assert_called_once()


def test_get_access_token_redis_unavailable_fallback(d365_client):
    """Test token acquisition falls back to in-memory cache when Redis unavailable."""
    d365_client.app.acquire_token_for_client.return_value = {
        "access_token": "token_from_msal",
        "expires_in": 3600,
    }
    
    # Mock Redis unavailable
    with patch("app.integrations.d365.client.is_redis_available", return_value=False):
        token = d365_client._get_access_token()
        
        assert token == "token_from_msal"
        assert d365_client._token == "token_from_msal"
        assert d365_client._token_expires_at is not None
        d365_client.app.acquire_token_for_client.assert_called_once()


def test_get_access_token_concurrent_lock(d365_client):
    """Test concurrent token acquisition uses lock to prevent duplicate requests."""
    d365_client.app.acquire_token_for_client.return_value = {
        "access_token": "token_from_msal",
        "expires_in": 3600,
    }
    
    # Mock Redis with lock behavior
    with patch("app.integrations.d365.client.is_redis_available", return_value=True):
        with patch("app.integrations.d365.client.get_cached_value", return_value=None):
            with patch("app.integrations.d365.client.get_redis_client") as mock_redis:
                mock_redis_client = MagicMock()
                # First call: lock not acquired (another worker has it)
                # Second call: lock acquired
                mock_redis_client.set.side_effect = [False, True]
                mock_redis_client.delete.return_value = True
                mock_redis.return_value = mock_redis_client
                
                with patch("app.integrations.d365.client.set_cached_value"):
                    with patch("time.sleep"):  # Skip sleep for faster test
                        token = d365_client._get_access_token()
                        
                        assert token == "token_from_msal"
                        # Should have tried lock twice
                        assert mock_redis_client.set.call_count >= 2


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


@pytest.mark.asyncio
async def test_find_lead_by_email_normal(d365_client):
    """Test finding lead with normal email address."""
    d365_client.app.acquire_token_for_client.return_value = {
        "access_token": "test_token",
        "expires_in": 3600,
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={
            "value": [{"leadid": "test_lead_id", "emailaddress1": "test@example.com"}]
        })
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        result = await d365_client._find_lead_by_email("test@example.com")
        
        assert result is not None
        assert result["leadid"] == "test_lead_id"
        # Verify that email was properly escaped and URL encoded
        call_args = mock_client_instance.get.call_args
        assert call_args is not None
        url = call_args[0][0]  # First positional argument is URL
        assert "test@example.com" in url or "test%40example.com" in url


@pytest.mark.asyncio
async def test_find_lead_by_email_with_single_quote(d365_client):
    """Test finding lead with email containing single quote (OData injection prevention)."""
    d365_client.app.acquire_token_for_client.return_value = {
        "access_token": "test_token",
        "expires_in": 3600,
    }
    
    malicious_email = "test'@example.com"
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={"value": []})
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        result = await d365_client._find_lead_by_email(malicious_email)
        
        # Verify that single quote was properly escaped
        call_args = mock_client_instance.get.call_args
        assert call_args is not None
        url = call_args[0][0]
        # OData escape: ' -> ''
        # Should not contain unescaped single quote that breaks query
        assert "test''" in url or "test%27%27" in url or "test%27" in url


@pytest.mark.asyncio
async def test_find_lead_by_id_success(d365_client):
    """Test finding lead by D365 lead ID."""
    d365_client.app.acquire_token_for_client.return_value = {
        "access_token": "test_token",
        "expires_in": 3600,
    }
    
    lead_id = "test-lead-id-123"
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={
            "leadid": lead_id,
            "emailaddress1": "test@example.com",
            "subject": "Test Lead"
        })
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        result = await d365_client._find_lead_by_id(lead_id)
        
        assert result is not None
        assert result["leadid"] == lead_id
        # Verify correct API URL was called
        call_args = mock_client_instance.get.call_args
        assert call_args is not None
        url = call_args[0][0]
        assert lead_id in url


@pytest.mark.asyncio
async def test_find_lead_by_id_not_found(d365_client):
    """Test finding lead by ID when lead doesn't exist."""
    d365_client.app.acquire_token_for_client.return_value = {
        "access_token": "test_token",
        "expires_in": 3600,
    }
    
    lead_id = "non-existent-lead-id"
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 404
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        result = await d365_client._find_lead_by_id(lead_id)
        
        assert result is None


@pytest.mark.asyncio
async def test_find_lead_by_id_rate_limit(d365_client):
    """Test finding lead by ID when rate limit exceeded."""
    d365_client.app.acquire_token_for_client.return_value = {
        "access_token": "test_token",
        "expires_in": 3600,
    }
    
    lead_id = "test-lead-id-123"
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 429
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        with pytest.raises(D365RateLimitError):
            await d365_client._find_lead_by_id(lead_id)


@pytest.mark.asyncio
async def test_find_lead_by_email_sql_injection_attempt(d365_client):
    """Test finding lead with SQL injection attempt (OData injection prevention)."""
    d365_client.app.acquire_token_for_client.return_value = {
        "access_token": "test_token",
        "expires_in": 3600,
    }
    
    injection_attempt = "test' OR '1'='1"
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={"value": []})
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        result = await d365_client._find_lead_by_email(injection_attempt)
        
        # Verify that injection attempt was properly escaped
        call_args = mock_client_instance.get.call_args
        assert call_args is not None
        url = call_args[0][0]
        # Should not contain unescaped OR that could break query
        # Single quotes should be escaped: ' -> ''
        assert "test''" in url or "test%27%27" in url


@pytest.mark.asyncio
async def test_find_lead_by_email_odata_injection_attempt(d365_client):
    """Test finding lead with OData injection attempt."""
    d365_client.app.acquire_token_for_client.return_value = {
        "access_token": "test_token",
        "expires_in": 3600,
    }
    
    injection_attempt = "test' eq 'admin"
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={"value": []})
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        result = await d365_client._find_lead_by_email(injection_attempt)
        
        # Verify that injection attempt was properly escaped
        call_args = mock_client_instance.get.call_args
        assert call_args is not None
        url = call_args[0][0]
        # Should not contain unescaped eq that could break query
        # Single quotes should be escaped: ' -> ''
        assert "test''" in url or "test%27%27" in url