"""Dynamics 365 Web API client."""

import os
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from urllib.parse import quote
from msal import ConfidentialClientApplication
import httpx
from app.config import settings
from app.core.logging import logger
from app.core.redis_client import get_redis_client, is_redis_available
from app.core.cache import get_cached_value, set_cached_value
from app.integrations.d365.errors import (
    D365Error,
    D365AuthenticationError,
    D365APIError,
    D365RateLimitError,
    D365DuplicateError,
)


class D365Client:
    """D365 Web API client for lead push operations."""

    def __init__(self):
        """Initialize D365 client with configuration."""
        if not settings.d365_enabled:
            raise ValueError("D365 integration is disabled (feature flag off)")
        
        if not all([
            settings.d365_base_url,
            settings.d365_client_id,
            settings.d365_client_secret,
            settings.d365_tenant_id,
        ]):
            raise ValueError("D365 credentials not configured")
        
        self.base_url = settings.d365_base_url.rstrip("/")
        self.client_id = settings.d365_client_id
        self.client_secret = settings.d365_client_secret
        self.tenant_id = settings.d365_tenant_id
        self.api_version = settings.d365_api_version
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = f"{self.base_url}/.default"
        
        # MSAL ConfidentialClientApplication (Client Credentials Flow)
        self.app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority,
        )
        
        # In-memory token cache (fallback when Redis unavailable)
        self._token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        
        logger.info("d365_client_initialized", base_url=self.base_url)

    def _get_access_token(self) -> str:
        """
        Get OAuth 2.0 access token (client credentials flow).
        
        Uses Redis for distributed token caching across workers.
        Falls back to in-memory cache if Redis is unavailable.
        
        Returns:
            Access token string
            
        Raises:
            D365AuthenticationError: If token acquisition fails
        """
        # Try Redis cache first
        if is_redis_available():
            cached_token = get_cached_value("d365_access_token")
            cached_expires = get_cached_value("d365_token_expires_at")
            
            if cached_token and cached_expires:
                try:
                    expires_at = datetime.fromisoformat(cached_expires)
                    # Check if token is still valid (with 5 minute buffer)
                    if datetime.now() < (expires_at - timedelta(minutes=5)):
                        logger.debug(
                            "d365_token_cached_redis",
                            message="Using cached token from Redis"
                        )
                        return cached_token
                except (ValueError, TypeError) as e:
                    logger.warning(
                        "d365_token_cache_parse_error",
                        message="Failed to parse cached token expiration",
                        error=str(e)
                    )
                    # Continue to acquire new token
        
        # Acquire new token with lock (to prevent concurrent token requests)
        token = self._acquire_token_with_lock()
        
        # Cache in Redis if available
        if is_redis_available() and token:
            try:
                # Get expiration from MSAL result (stored in instance during acquisition)
                expires_at = self._token_expires_at or (datetime.now() + timedelta(seconds=3600))
                expires_in = int((expires_at - datetime.now()).total_seconds())
                
                # Cache token and expiration
                set_cached_value("d365_access_token", token, ttl=expires_in)
                set_cached_value("d365_token_expires_at", expires_at.isoformat(), ttl=expires_in)
            except Exception as e:
                logger.warning(
                    "d365_token_cache_write_error",
                    message="Failed to cache token in Redis",
                    error=str(e)
                )
                # Continue - token is still valid, just not cached
        
        return token
    
    def _acquire_token_with_lock(self) -> str:
        """
        Acquire token with Redis lock to prevent concurrent token requests.
        
        Uses Redis SETNX for distributed locking across workers.
        Falls back to direct acquisition if Redis is unavailable.
        
        Returns:
            Access token string
            
        Raises:
            D365AuthenticationError: If token acquisition fails
        """
        redis_client = get_redis_client()
        lock_key = "d365_token_lock"
        lock_timeout = 30  # seconds
        
        # Try to acquire lock if Redis is available
        lock_acquired = False
        if redis_client:
            try:
                lock_acquired = redis_client.set(lock_key, "locked", nx=True, ex=lock_timeout)
                if not lock_acquired:
                    # Another worker is acquiring token, wait and retry cache
                    logger.debug(
                        "d365_token_lock_wait",
                        message="Another worker is acquiring token, waiting for cache"
                    )
                    time.sleep(1)
                    
                    # Try to get cached token again (other worker might have cached it)
                    if is_redis_available():
                        cached_token = get_cached_value("d365_access_token")
                        cached_expires = get_cached_value("d365_token_expires_at")
                        
                        if cached_token and cached_expires:
                            try:
                                expires_at = datetime.fromisoformat(cached_expires)
                                if datetime.now() < (expires_at - timedelta(minutes=5)):
                                    logger.debug(
                                        "d365_token_cached_after_lock_wait",
                                        message="Token cached by another worker"
                                    )
                                    return cached_token
                            except (ValueError, TypeError):
                                pass
                    
                    # If still no token, wait a bit more and try lock again
                    time.sleep(2)
                    lock_acquired = redis_client.set(lock_key, "locked", nx=True, ex=lock_timeout)
            except Exception as e:
                logger.warning(
                    "d365_token_lock_error",
                    message="Failed to acquire token lock, proceeding without lock",
                    error=str(e)
                )
                # Continue without lock (fallback behavior)
        
        try:
            # Acquire token from MSAL
            result = self.app.acquire_token_for_client(scopes=[self.scope])
            
            if "access_token" in result:
                token = result["access_token"]
                # Calculate expiration (default 3600 seconds if not provided)
                expires_in = result.get("expires_in", 3600)
                expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Store in instance for Redis caching
                self._token = token
                self._token_expires_at = expires_at
                
                logger.info(
                    "d365_token_acquired",
                    message="Token acquired successfully",
                    expires_in=expires_in,
                    with_lock=lock_acquired
                )
                return token
            else:
                error = result.get("error", "unknown")
                error_description = result.get("error_description", "Token acquisition failed")
                logger.error(
                    "d365_token_acquisition_failed",
                    error=error,
                    error_description=error_description
                )
                raise D365AuthenticationError(f"Token acquisition failed: {error} - {error_description}")
        
        except D365AuthenticationError:
            raise
        except Exception as e:
            logger.error(
                "d365_token_error",
                message="Unexpected error during token acquisition",
                error=str(e),
                exc_info=True
            )
            raise D365AuthenticationError(f"Token acquisition error: {str(e)}") from e
        
        finally:
            # Release lock if we acquired it
            if lock_acquired and redis_client:
                try:
                    redis_client.delete(lock_key)
                except Exception as e:
                    logger.warning(
                        "d365_token_lock_release_error",
                        message="Failed to release token lock",
                        error=str(e)
                    )

    async def create_or_update_lead(
        self,
        payload: Dict[str, Any],
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create or update lead in D365 using Web API.
        
        Uses upsert pattern: checks for existing lead by email/domain,
        creates if not exists, updates if exists.
        
        Args:
            payload: D365 Lead entity payload
            idempotency_key: Optional idempotency key for duplicate prevention (not used yet)
            
        Returns:
            D365 Lead entity response with lead ID
            
        Raises:
            D365APIError: If API call fails
            D365RateLimitError: If rate limit exceeded
            D365DuplicateError: If duplicate lead detected
        """
        token = self._get_access_token()
        api_url = f"{self.base_url}/api/data/{self.api_version}/leads"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Prefer": "return=representation",
        }
        
        # Check for existing lead by email (if provided)
        email = payload.get("emailaddress1")
        if email:
            try:
                existing_lead = await self._find_lead_by_email(email)
                if existing_lead and "leadid" in existing_lead:
                    # Update existing lead
                    lead_id = existing_lead["leadid"]
                    update_url = f"{api_url}({lead_id})"
                    
                    logger.info(
                        "d365_lead_update",
                        message="Updating existing lead",
                        lead_id=lead_id,
                        email=email
                    )
                    
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.patch(update_url, json=payload, headers=headers)
                        
                        if response.status_code == 204:
                            # Get updated lead
                            get_response = await client.get(update_url, headers=headers)
                            if get_response.status_code == 200:
                                return get_response.json()
                            else:
                                # Return minimal response if get fails
                                return {"leadid": lead_id}
                        elif response.status_code == 429:
                            raise D365RateLimitError("Rate limit exceeded")
                        else:
                            error_text = response.text
                            logger.error(
                                "d365_lead_update_failed",
                                status_code=response.status_code,
                                error=error_text
                            )
                            raise D365APIError(f"Update failed: {response.status_code} - {error_text}")
            
            except D365RateLimitError:
                raise
            except D365APIError:
                raise
            except Exception as e:
                # If lookup fails, continue with create
                logger.warning(
                    "d365_lead_lookup_failed",
                    message="Failed to lookup existing lead, proceeding with create",
                    error=str(e)
                )
        
        # Create new lead
        logger.info(
            "d365_lead_create",
            message="Creating new lead",
            subject=payload.get("subject", "unknown")
        )
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(api_url, json=payload, headers=headers)
                
                if response.status_code == 201:
                    # httpx response.json() is synchronous, not async
                    result = response.json()
                    logger.info(
                        "d365_lead_created",
                        message="Lead created successfully",
                        lead_id=result.get("leadid")
                    )
                    return result
                elif response.status_code == 429:
                    raise D365RateLimitError("Rate limit exceeded")
                elif response.status_code == 409:
                    # Duplicate detected
                    error_text = response.text
                    logger.warning(
                        "d365_lead_duplicate",
                        message="Duplicate lead detected",
                        error=error_text
                    )
                    raise D365DuplicateError(f"Duplicate lead: {error_text}")
                else:
                    error_text = response.text
                    logger.error(
                        "d365_lead_create_failed",
                        status_code=response.status_code,
                        error=error_text
                    )
                    raise D365APIError(f"Create failed: {response.status_code} - {error_text}")
        
        except httpx.TimeoutException as e:
            logger.error("d365_request_timeout", error=str(e))
            raise D365APIError(f"Request timeout: {str(e)}") from e
        except httpx.RequestError as e:
            logger.error("d365_request_error", error=str(e))
            raise D365APIError(f"Request error: {str(e)}") from e

    async def _find_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """
        Find existing lead by D365 lead ID.
        
        Args:
            lead_id: D365 lead ID (GUID)
            
        Returns:
            Lead entity if found, None otherwise
            
        Raises:
            D365RateLimitError: If rate limit exceeded
        """
        token = self._get_access_token()
        api_url = f"{self.base_url}/api/data/{self.api_version}/leads({lead_id})"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(api_url, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    # Lead not found
                    return None
                elif response.status_code == 429:
                    raise D365RateLimitError("Rate limit exceeded")
                else:
                    logger.warning(
                        "d365_lead_lookup_by_id_error",
                        status_code=response.status_code,
                        lead_id=lead_id,
                        error=response.text
                    )
                    return None
        
        except D365RateLimitError:
            raise
        except Exception as e:
            logger.warning(
                "d365_lead_lookup_by_id_exception",
                lead_id=lead_id,
                error=str(e)
            )
            return None

    async def _find_lead_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find existing lead by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            Lead entity if found, None otherwise
        """
        token = self._get_access_token()
        api_url = f"{self.base_url}/api/data/{self.api_version}/leads"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
        }
        
        # Query by email
        # OData string literal: escape single quotes (' -> '') to prevent injection
        # Then URL encode the entire filter query for safe URL construction
        escaped_email = email.replace("'", "''")  # OData string literal escape (standard)
        filter_query = f"$filter=emailaddress1 eq '{escaped_email}'"
        # URL encode the entire filter query to safely include in URL
        encoded_filter = quote(filter_query, safe="=&")
        query_url = f"{api_url}?{encoded_filter}&$top=1"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(query_url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("value") and len(data["value"]) > 0:
                        return data["value"][0]
                    return None
                elif response.status_code == 429:
                    raise D365RateLimitError("Rate limit exceeded")
                else:
                    logger.warning(
                        "d365_lead_lookup_error",
                        status_code=response.status_code,
                        error=response.text
                    )
                    return None
        
        except D365RateLimitError:
            raise
        except Exception as e:
            logger.warning("d365_lead_lookup_exception", error=str(e))
            return None

