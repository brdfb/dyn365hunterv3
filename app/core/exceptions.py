"""Custom exceptions for Partner Center integration."""

from typing import Optional


class PartnerCenterAuthError(Exception):
    """Raised when Partner Center API authentication fails (401/403)."""
    
    def __init__(self, message: str, status_code: int, request_id: Optional[str] = None):
        """
        Initialize authentication error.
        
        Args:
            message: Error message
            status_code: HTTP status code (401 or 403)
            request_id: Optional request ID from API response
        """
        super().__init__(message)
        self.status_code = status_code
        self.request_id = request_id


class PartnerCenterRateLimitError(Exception):
    """Raised when Partner Center API rate limit is exceeded (429)."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, request_id: Optional[str] = None):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            retry_after: Optional retry-after header value (seconds)
            request_id: Optional request ID from API response
        """
        super().__init__(message)
        self.retry_after = retry_after
        self.request_id = request_id

