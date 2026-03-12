from __future__ import annotations

from .auth import OAuthConfig
from .client import AmoCRM

_client: AmoCRM | None = None


def exchange_code(subdomain: str, code: str, oauth: OAuthConfig) -> None:
    """Exchange authorization code for tokens and initialize the global client."""
    global _client
    _client = AmoCRM.from_code(subdomain=subdomain, code=code, oauth=oauth)


def get_client(subdomain: str, oauth: OAuthConfig) -> AmoCRM:
    """Return the global client, initializing it from storage on first call."""
    global _client
    if _client is None:
        _client = AmoCRM(subdomain=subdomain, oauth=oauth)
    return _client


def reset() -> None:
    """Reset the global client (useful for testing)."""
    global _client
    _client = None
