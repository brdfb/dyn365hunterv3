"""Partner Center API client (MVP: Minimal)."""

import time
import structlog
from typing import List, Dict, Any, Optional
from msal import PublicClientApplication
import httpx
from app.config import settings
from app.core.logging import logger, mask_pii

logger = structlog.get_logger(__name__)


class PartnerCenterClient:
    """Minimal Partner Center API client (50-70 lines MVP)."""

    def __init__(self):
        """Initialize Partner Center client."""
        if not settings.partner_center_enabled:
            logger.info("partner_center_disabled", reason="feature_flag_off")
            raise ValueError("Partner Center integration is disabled (feature flag off)")
        
        if not all([
            settings.partner_center_client_id,
            settings.partner_center_tenant_id,
            settings.partner_center_api_url,
        ]):
            logger.warning("partner_center_config_missing")
            raise ValueError("Partner Center credentials not configured")

        self.api_url = settings.partner_center_api_url.rstrip("/")
        self.client_id = settings.partner_center_client_id
        self.tenant_id = settings.partner_center_tenant_id
        self.scope = settings.partner_center_scope
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        
        # Token cache path (optional, defaults to .token_cache)
        cache_path = settings.partner_center_token_cache_path or ".token_cache"
        
        # MSAL PublicClientApplication (for Device Code Flow)
        self.app = PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority,
        )
        
        logger.info("partner_center_client_initialized", client_id=mask_pii(self.client_id))

    def _get_access_token(self) -> str:
        """
        Get access token using MSAL (silent acquisition preferred).
        
        Returns:
            Access token string
            
        Raises:
            ValueError: If token acquisition fails
        """
        # Try silent token acquisition first (uses cached refresh token)
        accounts = self.app.get_accounts()
        if accounts:
            account = accounts[0]
            result = self.app.acquire_token_silent(
                scopes=[self.scope],
                account=account
            )
            if result and "access_token" in result:
                logger.debug("partner_center_token_acquired_silent")
                return result["access_token"]
        
        # Silent acquisition failed - need interactive login
        # This should only happen during initial setup
        error_msg = "Token acquisition failed. Run setup script to authenticate."
        logger.error("partner_center_token_acquisition_failed", error=error_msg)
        raise ValueError(error_msg)

    def get_referrals(self) -> List[Dict[str, Any]]:
        """
        Get referrals from Partner Center API.
        
        Returns:
            List of referral dictionaries
            
        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If token acquisition fails
        """
        # Get access token
        access_token = self._get_access_token()
        
        # API endpoint
        url = f"{self.api_url}/v1/referrals"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        # Basic retry: 2 attempts
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Basic rate limiting: sleep(1) between requests
                if attempt > 0:
                    time.sleep(1)
                
                logger.info("partner_center_fetching_referrals", attempt=attempt + 1)
                
                with httpx.Client(timeout=30.0) as client:
                    response = client.get(url, headers=headers)
                    response.raise_for_status()
                    
                    data = response.json()
                    referrals = data.get("items", [])
                    
                    logger.info(
                        "partner_center_referrals_fetched",
                        count=len(referrals),
                        attempt=attempt + 1
                    )
                    
                    return referrals
                    
            except httpx.HTTPStatusError as e:
                last_error = e
                logger.warning(
                    "partner_center_api_error",
                    status_code=e.response.status_code,
                    attempt=attempt + 1,
                    error=str(e)
                )
                if e.response.status_code == 401:
                    # Token expired, try to refresh
                    try:
                        access_token = self._get_access_token()
                        headers["Authorization"] = f"Bearer {access_token}"
                    except ValueError:
                        raise  # Re-raise if token refresh fails
                        
            except httpx.RequestError as e:
                last_error = e
                logger.warning(
                    "partner_center_network_error",
                    attempt=attempt + 1,
                    error=str(e)
                )
        
        # All retries failed
        logger.error("partner_center_fetch_failed", max_retries=max_retries)
        raise last_error or Exception("Failed to fetch referrals after retries")

