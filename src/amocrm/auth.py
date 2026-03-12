from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class TokenStorage(Protocol):
    """Протокол хранилища токенов OAuth.

    Реализации должны обеспечивать сохранение и загрузку пары
    access_token / refresh_token из произвольного хранилища
    (база данных, файл, переменные окружения и т.д.).
    """

    def save(self, access_token: str, refresh_token: str) -> None:
        """Сохранить токены в хранилище.

        Args:
            access_token: Токен доступа OAuth 2.0.
            refresh_token: Токен обновления OAuth 2.0.
        """
        ...

    def load(self) -> tuple[str, str]:
        """Загрузить токены из хранилища.

        Returns:
            Кортеж ``(access_token, refresh_token)``.
        """
        ...


@dataclass(kw_only=True)
class OAuthConfig:
    """Конфигурация OAuth 2.0 для подключения к AmoCRM.

    Attributes:
        client_id: Идентификатор интеграции из личного кабинета AmoCRM.
        client_secret: Секрет интеграции.
        redirect_uri: URI перенаправления, указанный при создании интеграции.
        storage: Хранилище токенов, реализующее протокол :class:`TokenStorage`.
    """

    client_id: str
    client_secret: str
    redirect_uri: str
    storage: TokenStorage


class DjangoTokenStorage:
    """Хранилище токенов на основе экземпляра модели Django.

    Токены сохраняются в полях ``access_token`` и ``refresh_token``
    переданного объекта и сохраняются вызовом ``instance.save()``.
    """

    def __init__(self, instance: Any) -> None:
        """
        Args:
            instance: Экземпляр модели Django с полями
                ``access_token`` и ``refresh_token``.
        """
        self._instance = instance

    def save(self, access_token: str, refresh_token: str) -> None:
        """Сохранить токены в модель Django и вызвать ``instance.save()``.

        Args:
            access_token: Токен доступа OAuth 2.0.
            refresh_token: Токен обновления OAuth 2.0.
        """
        self._instance.access_token = access_token
        self._instance.refresh_token = refresh_token
        self._instance.save()

    def load(self) -> tuple[str, str]:
        """Загрузить токены из полей модели Django.

        Returns:
            Кортеж ``(access_token, refresh_token)``.
        """
        return self._instance.access_token, self._instance.refresh_token
