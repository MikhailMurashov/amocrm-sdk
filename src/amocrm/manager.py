from __future__ import annotations

import requests

from .auth import OAuthConfig
from .client import AmoCRM
from .exceptions import AmoCRMTokenRefreshError

_client: AmoCRM | None = None

_TOKEN_URL = "https://www.amocrm.ru/oauth2/access_token"


def exchange_code(subdomain: str, code: str, oauth: OAuthConfig) -> None:
    """Обменять код авторизации на токены и инициализировать глобальный клиент.

    После успешного обмена глобальный клиент готов к работе;
    повторный вызов :func:`get_client` вернёт уже созданный экземпляр.

    Args:
        subdomain: Поддомен аккаунта AmoCRM (например, ``"mycompany"``).
        code: Одноразовый код авторизации из callback-запроса OAuth 2.0.
        oauth: Конфигурация OAuth с реквизитами интеграции и хранилищем токенов.

    Raises:
        AmoCRMTokenRefreshError: Если обмен кода на токены завершился ошибкой.
    """
    global _client
    resp = requests.post(
        _TOKEN_URL,
        json={
            "client_id": oauth.client_id,
            "client_secret": oauth.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": oauth.redirect_uri,
        },
    )
    if not resp.ok:
        raise AmoCRMTokenRefreshError(
            f"Authorization code exchange failed {resp.status_code}: {resp.text}"
        )
    data = resp.json()
    oauth.storage.save(data["access_token"], data["refresh_token"])
    _client = AmoCRM(subdomain=subdomain, oauth=oauth)


def get_client(subdomain: str, oauth: OAuthConfig) -> AmoCRM:
    """Вернуть глобальный клиент, создав его из хранилища при первом вызове.

    При первом вызове создаёт :class:`~amocrm.client.AmoCRM`, загружая
    токены из ``oauth.storage``. Последующие вызовы возвращают тот же экземпляр.

    Args:
        subdomain: Поддомен аккаунта AmoCRM.
        oauth: Конфигурация OAuth с реквизитами интеграции и хранилищем токенов.

    Returns:
        Инициализированный экземпляр :class:`~amocrm.client.AmoCRM`.
    """
    global _client
    if _client is None:
        _client = AmoCRM(subdomain=subdomain, oauth=oauth)
    return _client


def reset() -> None:
    """Сбросить глобальный клиент (полезно в тестах)."""
    global _client
    _client = None
