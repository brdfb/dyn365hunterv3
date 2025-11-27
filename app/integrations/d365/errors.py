"""D365-specific exceptions."""


class D365Error(Exception):
    """Base exception for D365 integration errors."""
    pass


class D365AuthenticationError(D365Error):
    """D365 authentication failed."""
    pass


class D365APIError(D365Error):
    """D365 API call failed."""
    pass


class D365RateLimitError(D365Error):
    """D365 rate limit exceeded."""
    pass


class D365DuplicateError(D365Error):
    """D365 duplicate lead detected."""
    pass

