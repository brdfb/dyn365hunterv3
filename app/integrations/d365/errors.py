"""D365-specific exceptions."""


class D365Error(Exception):
    """Base exception for D365 integration errors."""
    
    def __init__(self, message: str, error_category: str = "unknown"):
        """
        Initialize D365 error.
        
        Args:
            message: Error message
            error_category: Error category ('auth', 'rate_limit', 'validation', 'network', 'unknown')
        """
        super().__init__(message)
        self.error_category = error_category
        self.is_transient = self._is_transient_error(error_category)
    
    def _is_transient_error(self, category: str) -> bool:
        """Determine if error is transient (retryable) or permanent."""
        transient_categories = ['rate_limit', 'network']
        return category in transient_categories


class D365AuthenticationError(D365Error):
    """D365 authentication failed."""
    
    def __init__(self, message: str):
        super().__init__(message, error_category="auth")


class D365APIError(D365Error):
    """D365 API call failed."""
    
    def __init__(self, message: str, error_category: str = "unknown"):
        super().__init__(message, error_category=error_category)


class D365RateLimitError(D365Error):
    """D365 rate limit exceeded."""
    
    def __init__(self, message: str):
        super().__init__(message, error_category="rate_limit")


class D365DuplicateError(D365Error):
    """D365 duplicate lead detected."""
    
    def __init__(self, message: str):
        super().__init__(message, error_category="validation")


def categorize_error(error: Exception) -> str:
    """
    Categorize error for metrics and retry logic.
    
    Returns:
        Error category: 'auth', 'rate_limit', 'validation', 'network', 'unknown'
    """
    if isinstance(error, D365Error):
        return error.error_category
    
    # Categorize generic exceptions
    error_str = str(error).lower()
    if 'network' in error_str or 'connection' in error_str or 'timeout' in error_str:
        return 'network'
    elif 'auth' in error_str or 'token' in error_str or 'unauthorized' in error_str:
        return 'auth'
    elif 'rate' in error_str or 'limit' in error_str or '429' in error_str:
        return 'rate_limit'
    elif 'validation' in error_str or 'invalid' in error_str or 'duplicate' in error_str:
        return 'validation'
    else:
        return 'unknown'

