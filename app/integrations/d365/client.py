"""Dynamics 365 Web API client."""

import os
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from msal import ConfidentialClientApplication
import httpx
from app.config import settings
from app.core.logging import logger
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
        
        # Token cache (in-memory for now, can be persisted later)
        self._token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        
        logger.info("d365_client_initialized", base_url=self.base_url)

    def _get_access_token(self) -> str:
        """
        Get OAuth 2.0 access token (client credentials flow).
        
        Uses MSAL ConfidentialClientApplication for non-interactive authentication.
        Caches token in memory until expiration.
        
        Returns:
            Access token string
            
        Raises:
            D365AuthenticationError: If token acquisition fails
        """
        # Check if cached token is still valid (with 5 minute buffer)
        if self._token and self._token_expires_at:
            if datetime.now() < (self._token_expires_at - timedelta(minutes=5)):
                logger.debug("d365_token_cached", message="Using cached token")
                return self._token
        
        # Acquire new token
        try:
            result = self.app.acquire_token_for_client(scopes=[self.scope])
            
            if "access_token" in result:
                self._token = result["access_token"]
                # Calculate expiration (default 3600 seconds if not provided)
                expires_in = result.get("expires_in", 3600)
                self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                logger.info(
                    "d365_token_acquired",
                    message="Token acquired successfully",
                    expires_in=expires_in
                )
                return self._token
            else:
                error = result.get("error", "unknown")
                error_description = result.get("error_description", "Token acquisition failed")
                logger.error(
                    "d365_token_acquisition_failed",
                    error=error,
                    error_description=error_description
                )
                raise D365AuthenticationError(f"Token acquisition failed: {error} - {error_description}")
        
        except Exception as e:
            logger.error(
                "d365_token_error",
                message="Unexpected error during token acquisition",
                error=str(e),
                exc_info=True
            )
            raise D365AuthenticationError(f"Token acquisition error: {str(e)}") from e

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
        filter_query = f"$filter=emailaddress1 eq '{email}'"
        query_url = f"{api_url}?{filter_query}&$top=1"
        
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

