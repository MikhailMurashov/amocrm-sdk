from __future__ import annotations

from typing import Any

import requests

from .auth import OAuthConfig
from .exceptions import AmoCRMAPIError, AmoCRMTokenRefreshError
from .resources.companies import CompaniesResource
from .resources.contacts import ContactsResource
from .resources.custom_fields import CustomFieldsResource
from .resources.leads import LeadsResource
from .resources.pipelines import PipelinesResource
from .resources.tasks import TasksResource

_TOKEN_URL = "https://www.amocrm.ru/oauth2/access_token"


class AmoCRM:
    """Клиент AmoCRM REST API.

    Предоставляет доступ к ресурсам сделок, контактов, компаний и воронок
    через свойства :attr:`leads`, :attr:`contacts`, :attr:`companies`,
    :attr:`pipelines`. Автоматически обновляет токен доступа при получении
    ответа 401 Unauthorized.
    """

    def __init__(self, subdomain: str, oauth: OAuthConfig) -> None:
        """Инициализировать клиент, загрузив токены из хранилища.

        Args:
            subdomain: Поддомен аккаунта AmoCRM (например, ``"mycompany"``).
            oauth: Конфигурация OAuth с реквизитами интеграции и хранилищем
                токенов. Токены загружаются из ``oauth.storage.load()``
                при создании клиента.
        """
        self._base_url = f"https://{subdomain}.amocrm.ru"
        self._oauth = oauth
        access_token, refresh_token = oauth.storage.load()
        self._refresh_token = refresh_token
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {access_token}"})
        self._leads: LeadsResource | None = None
        self._pipelines: PipelinesResource | None = None
        self._contacts: ContactsResource | None = None
        self._companies: CompaniesResource | None = None
        self._tasks: TasksResource | None = None
        self._custom_fields: CustomFieldsResource | None = None

    @classmethod
    def from_code(cls, subdomain: str, code: str, oauth: OAuthConfig) -> AmoCRM:
        """Обменять код авторизации на токены, сохранить их и вернуть новый клиент.

        Args:
            subdomain: Поддомен аккаунта AmoCRM.
            code: Одноразовый код авторизации из callback-запроса OAuth 2.0.
            oauth: Конфигурация OAuth с реквизитами интеграции и хранилищем токенов.

        Returns:
            Инициализированный экземпляр :class:`AmoCRM`.

        Raises:
            AmoCRMTokenRefreshError: Если обмен кода на токены завершился ошибкой.
        """
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
        return cls(subdomain=subdomain, oauth=oauth)

    def _refresh_tokens(self) -> None:
        """Обновить токен доступа через refresh_token и сохранить новые токены.

        Отправляет запрос к ``www.amocrm.ru`` (не через ``self._session``),
        обновляет заголовок ``Authorization`` в сессии и сохраняет токены
        в ``oauth.storage``.

        Raises:
            AmoCRMTokenRefreshError: Если запрос на обновление токена вернул
                статус не 2xx.
        """
        resp = requests.post(
            _TOKEN_URL,
            json={
                "client_id": self._oauth.client_id,
                "client_secret": self._oauth.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
                "redirect_uri": self._oauth.redirect_uri,
            },
        )
        if not resp.ok:
            raise AmoCRMTokenRefreshError(
                f"Token refresh failed {resp.status_code}: {resp.text}"
            )
        data = resp.json()
        new_access = data["access_token"]
        new_refresh = data["refresh_token"]
        self._session.headers.update({"Authorization": f"Bearer {new_access}"})
        self._refresh_token = new_refresh
        self._oauth.storage.save(new_access, new_refresh)

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Выполнить HTTP-запрос к API, автоматически повторив его при 401.

        При получении статуса 401 вызывает :meth:`_refresh_tokens` и повторяет
        запрос ровно один раз.

        Args:
            method: HTTP-метод (``"GET"``, ``"POST"``, ``"PATCH"``, ``"DELETE"``).
            path: Путь API относительно базового URL (например, ``"/api/v4/leads"``).
            **kwargs: Дополнительные аргументы для ``requests.Session.request``
                (``params``, ``json``, ``data`` и др.).

        Returns:
            Декодированный JSON-ответ в виде словаря. При статусе 204 или
            пустом теле возвращает пустой словарь ``{}``.

        Raises:
            AmoCRMAPIError: Если статус ответа не 2xx (после возможного повтора).
        """
        url = self._base_url + path
        response = self._session.request(method, url, **kwargs)
        if response.status_code == 401:
            self._refresh_tokens()
            response = self._session.request(method, url, **kwargs)
        if not response.ok:
            raise AmoCRMAPIError(response.status_code, response.text)
        if response.status_code == 204 or not response.content:
            return {}
        return response.json()  # type: ignore[no-any-return]

    @property
    def leads(self) -> LeadsResource:
        """Ресурс для работы со сделками."""
        if self._leads is None:
            self._leads = LeadsResource(self)
        return self._leads

    @property
    def pipelines(self) -> PipelinesResource:
        """Ресурс для работы с воронками и их статусами."""
        if self._pipelines is None:
            self._pipelines = PipelinesResource(self)
        return self._pipelines

    @property
    def contacts(self) -> ContactsResource:
        """Ресурс для работы с контактами."""
        if self._contacts is None:
            self._contacts = ContactsResource(self)
        return self._contacts

    @property
    def companies(self) -> CompaniesResource:
        """Ресурс для работы с компаниями."""
        if self._companies is None:
            self._companies = CompaniesResource(self)
        return self._companies

    @property
    def tasks(self) -> TasksResource:
        """Ресурс для работы с задачами."""
        if self._tasks is None:
            self._tasks = TasksResource(self)
        return self._tasks

    @property
    def custom_fields(self) -> CustomFieldsResource:
        """Ресурс для работы с кастомными полями."""
        if self._custom_fields is None:
            self._custom_fields = CustomFieldsResource(self)
        return self._custom_fields
