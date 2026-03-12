from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class TokenStorage(Protocol):
    def save(self, access_token: str, refresh_token: str) -> None: ...
    def load(self) -> tuple[str, str]: ...


@dataclass(kw_only=True)
class OAuthConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    storage: TokenStorage


class DjangoTokenStorage:
    """Token storage backed by a Django model instance."""

    def __init__(self, instance: Any) -> None:
        self._instance = instance

    def save(self, access_token: str, refresh_token: str) -> None:
        self._instance.access_token = access_token
        self._instance.refresh_token = refresh_token
        self._instance.save()

    def load(self) -> tuple[str, str]:
        return self._instance.access_token, self._instance.refresh_token
