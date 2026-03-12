from __future__ import annotations

from .auth import OAuthConfig
from .client import AmoCRM

_client: AmoCRM | None = None


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
    _client = AmoCRM.from_code(subdomain=subdomain, code=code, oauth=oauth)


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
