"""Partner Center API client (MVP: Minimal)."""

import time
import os
import structlog
from typing import List, Dict, Any, Optional
from msal import PublicClientApplication, SerializableTokenCache
import httpx
from app.config import settings
from app.core.logging import logger, mask_pii
from app.core.exceptions import PartnerCenterAuthError, PartnerCenterRateLimitError

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
        # token_cache parameter ensures persistent token storage
        self.cache_path = cache_path
        self.token_cache = SerializableTokenCache()
        
        # Load existing token cache if file exists
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    self.token_cache.deserialize(f.read())
            except Exception as e:
                logger.warning("partner_center_cache_load_failed", error=str(e))
        
        self.app = PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority,
            token_cache=self.token_cache,
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
                # Save token cache after successful acquisition
                self._save_token_cache()
                logger.debug("partner_center_token_acquired_silent")
                return result["access_token"]
        
        # Silent acquisition failed - need interactive login
        # This should only happen during initial setup
        error_msg = "Token acquisition failed. Run setup script to authenticate."
        logger.error("partner_center_token_acquisition_failed", error=error_msg)
        raise ValueError(error_msg)
    
    def _save_token_cache(self):
        """Save token cache to file for persistence."""
        if self.cache_path and self.token_cache.has_state_changed:
            try:
                # Ensure directory exists
                cache_dir = os.path.dirname(self.cache_path) or '.'
                if cache_dir and not os.path.exists(cache_dir):
                    os.makedirs(cache_dir, exist_ok=True)
                
                with open(self.cache_path, 'w') as f:
                    f.write(self.token_cache.serialize())
                logger.debug("partner_center_cache_saved", path=self.cache_path)
            except Exception as e:
                logger.warning("partner_center_cache_save_failed", error=str(e))

    def build_referral_query(
        self,
        direction: Optional[str] = None,
        status: Optional[str] = None,
        top: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Build standard OData query parameters for Partner Center Referrals API.
        
        Standard query template:
        GET {base_url}/{api_version}/engagements/referrals?$filter=direction eq '{direction}'&$top={top}
        
        NOTE: Status filter removed (2025-01-30) - fetch all statuses (Active, Closed, New, etc.)
        Status filtering can be done in UI or application layer after data is stored.
        
        Args:
            direction: Filter by direction ('Incoming' or 'Outgoing'). Default: from config
            status: DEPRECATED - No longer used. All statuses are fetched. Kept for backward compatibility.
            top: Maximum number of results to return. Default: from config
            
        Returns:
            Dictionary with OData query parameters ($filter, $top, $orderby)
        """
        # Use config defaults if not provided
        direction = direction or settings.partner_center_referral_default_direction
        # status filter removed - fetch all statuses
        top = top or settings.partner_center_referral_default_top
        
        # Build filter expression (only direction, no status filter)
        filter_parts = []
        if direction:
            filter_parts.append(f"direction eq '{direction}'")
        # Status filter removed - fetch all statuses
        
        params = {
            "$top": top,
            "$orderby": "createdDateTime desc",
        }
        
        if filter_parts:
            params["$filter"] = " and ".join(filter_parts)
        
        return params

    def _extract_request_id(self, response: httpx.Response) -> Optional[str]:
        """
        Extract request ID from response headers.
        
        Args:
            response: HTTP response object
            
        Returns:
            Request ID if found, None otherwise
        """
        # Common headers for request ID
        request_id_headers = [
            "request-id",
            "x-request-id",
            "x-ms-request-id",
            "x-correlation-id",
        ]
        
        for header in request_id_headers:
            request_id = response.headers.get(header)
            if request_id:
                return request_id
        
        return None

    def _fetch_page(
        self,
        url: str,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]] = None,
        attempt: int = 1,
    ) -> Dict[str, Any]:
        """
        Fetch a single page from Partner Center API with enhanced error handling.
        
        Args:
            url: Full URL to fetch (can be base URL or @odata.nextLink)
            headers: HTTP headers (Authorization, Content-Type)
            params: Query parameters (only used for first page)
            attempt: Retry attempt number
        
        Returns:
            Response JSON data
            
        Raises:
            PartnerCenterAuthError: If authentication fails (401/403)
            PartnerCenterRateLimitError: If rate limit exceeded (429)
            httpx.HTTPError: If API request fails after retries
        """
        max_retries = 3  # Increased for 429/5xx retries
        last_error = None
        
        for retry in range(max_retries):
            try:
                # Exponential backoff for retries (except first attempt)
                if retry > 0:
                    backoff_time = min(2 ** retry, 60)  # Max 60 seconds
                    time.sleep(backoff_time)
                
                logger.debug(
                    "partner_center_fetching_page",
                    url=mask_pii(url),
                    attempt=attempt,
                    retry=retry + 1,
                    max_retries=max_retries
                )
                
                with httpx.Client(timeout=30.0) as client:
                    # If URL is a full URL (contains @odata.nextLink), don't use params
                    if url.startswith("http"):
                        response = client.get(url, headers=headers)
                    else:
                        response = client.get(url, headers=headers, params=params)
                    
                    # Extract request ID for logging
                    request_id = self._extract_request_id(response)
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    # Save token cache after successful API call
                    self._save_token_cache()
                    
                    return data
                    
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                request_id = self._extract_request_id(e.response)
                
                # 401/403: Authentication errors
                if status_code in (401, 403):
                    error_msg = f"Partner Center authentication failed: {status_code}"
                    logger.error(
                        "partner_center_auth_error",
                        status_code=status_code,
                        request_id=request_id,
                        url=mask_pii(url),
                        attempt=attempt,
                        retry=retry + 1,
                        error=str(e)
                    )
                    
                    # Try token refresh for 401
                    if status_code == 401 and retry == 0:
                        try:
                            access_token = self._get_access_token()
                            headers["Authorization"] = f"Bearer {access_token}"
                            continue  # Retry with new token
                        except ValueError:
                            pass  # Token refresh failed, raise error
                    
                    # Raise auth error (don't retry for 403)
                    raise PartnerCenterAuthError(error_msg, status_code, request_id)
                
                # 429: Rate limit exceeded
                elif status_code == 429:
                    retry_after = None
                    if "Retry-After" in e.response.headers:
                        try:
                            retry_after = int(e.response.headers["Retry-After"])
                        except (ValueError, TypeError):
                            pass
                    
                    error_msg = f"Partner Center rate limit exceeded: {status_code}"
                    logger.warning(
                        "partner_center_rate_limit",
                        status_code=status_code,
                        request_id=request_id,
                        url=mask_pii(url),
                        attempt=attempt,
                        retry=retry + 1,
                        retry_after=retry_after,
                        error=str(e)
                    )
                    
                    # Use Retry-After header if available, otherwise exponential backoff
                    if retry_after:
                        time.sleep(retry_after)
                    
                    # Retry up to max_retries
                    if retry < max_retries - 1:
                        last_error = PartnerCenterRateLimitError(error_msg, retry_after, request_id)
                        continue
                    else:
                        raise PartnerCenterRateLimitError(error_msg, retry_after, request_id)
                
                # 5xx: Server errors (retry with exponential backoff)
                elif 500 <= status_code < 600:
                    logger.warning(
                        "partner_center_server_error",
                        status_code=status_code,
                        request_id=request_id,
                        url=mask_pii(url),
                        attempt=attempt,
                        retry=retry + 1,
                        error=str(e)
                    )
                    
                    # Retry up to max_retries
                    if retry < max_retries - 1:
                        last_error = e
                        continue
                    else:
                        last_error = e
                        break
                
                # Other 4xx errors (don't retry)
                else:
                    logger.error(
                        "partner_center_client_error",
                        status_code=status_code,
                        request_id=request_id,
                        url=mask_pii(url),
                        attempt=attempt,
                        retry=retry + 1,
                        error=str(e)
                    )
                    last_error = e
                    break
                        
            except httpx.RequestError as e:
                last_error = e
                logger.warning(
                    "partner_center_network_error",
                    attempt=attempt,
                    retry=retry + 1,
                    error=str(e)
                )
                
                # Retry network errors
                if retry < max_retries - 1:
                    continue
        
        # All retries failed
        logger.error(
            "partner_center_fetch_page_failed",
            max_retries=max_retries,
            attempt=attempt,
            url=mask_pii(url)
        )
        raise last_error or Exception("Failed to fetch page after retries")

    def get_referrals(
        self,
        direction: Optional[str] = None,
        status: Optional[str] = None,  # DEPRECATED - No longer used. All statuses are fetched.
        top: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get referrals from Microsoft Partner Referrals API with pagination support.
        
        Uses standard query template with configurable defaults.
        Handles OData pagination via @odata.nextLink.
        
        NOTE: Status filter removed (2025-01-30) - fetches all statuses (Active, Closed, New, etc.)
        Status filtering can be done in UI or application layer after data is stored.
        
        Args:
            direction: Filter by direction ('Incoming' or 'Outgoing'). Default: from config
            status: DEPRECATED - No longer used. All statuses are fetched. Kept for backward compatibility.
            top: Maximum number of results per page. Default: from config
            
        Returns:
            Flat list of all referral dictionaries (all pages combined)
            
        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If token acquisition fails
            
        References:
            - API Docs: https://learn.microsoft.com/en-us/partner-center/developer/get-a-list-of-referrals
            - Base URL: https://api.partner.microsoft.com
            - Endpoint: /v1.0/engagements/referrals
            - OData Pagination: https://learn.microsoft.com/en-us/partner-center/developer/odata-query-support
        """
        # Get access token
        access_token = self._get_access_token()
        
        # Build query parameters using standard template
        params = self.build_referral_query(direction=direction, status=status, top=top)
        
        # API endpoint with version from config
        api_version = settings.partner_center_api_version
        base_url = f"{self.api_url}/{api_version}/engagements/referrals"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        # Pagination loop
        all_referrals: List[Dict[str, Any]] = []
        current_url = base_url
        max_pages = settings.partner_center_referral_max_pages
        page_count = 0
        
        logger.info("partner_center_fetching_referrals", max_pages=max_pages)
        
        while current_url and page_count < max_pages:
            page_count += 1
            
            # Fetch current page
            # For first page, use params. For subsequent pages, @odata.nextLink is a full URL
            page_params = params if page_count == 1 else None
            data = self._fetch_page(current_url, headers, params=page_params, attempt=page_count)
            
            # Extract referrals from response
            # Microsoft Partner Referrals API returns OData format: {"value": [...], "@odata.nextLink": "..."}
            if isinstance(data, list):
                page_referrals = data
                next_link = None
            elif "value" in data:
                page_referrals = data["value"]
                next_link = data.get("@odata.nextLink")
            elif "items" in data:
                page_referrals = data["items"]
                next_link = data.get("@odata.nextLink")
            else:
                # Fallback: assume entire response is the list
                page_referrals = data if isinstance(data, list) else []
                next_link = None
            
            # Add to accumulated list
            all_referrals.extend(page_referrals)
            
            logger.info(
                "partner_center_page_fetched",
                page=page_count,
                page_count=len(page_referrals),
                total_count=len(all_referrals),
                has_next=next_link is not None
            )
            
            # Check for next page
            if next_link:
                current_url = next_link
                # Basic rate limiting: sleep(1) between pages
                time.sleep(1)
            else:
                current_url = None
        
        if page_count >= max_pages and current_url:
            logger.warning(
                "partner_center_max_pages_reached",
                max_pages=max_pages,
                total_fetched=len(all_referrals),
                has_more=True
            )
        
        logger.info(
            "partner_center_referrals_fetched",
            total_count=len(all_referrals),
            pages_fetched=page_count
        )
        
        return all_referrals

