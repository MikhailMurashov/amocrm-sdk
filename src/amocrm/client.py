from __future__ import annotations

from typing import Any

import requests

from .auth import OAuthConfig
from .exceptions import AmoCRMAPIError, AmoCRMTokenRefreshError
from .resources.companies import CompaniesResource
from .resources.contacts import ContactsResource
from .resources.leads import LeadsResource
from .resources.pipelines import PipelinesResource

_TOKEN_URL = "https://www.amocrm.ru/oauth2/access_token"


class AmoCRM:
    def __init__(self, subdomain: str, oauth: OAuthConfig) -> None:
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

    @classmethod
    def from_code(cls, subdomain: str, code: str, oauth: OAuthConfig) -> AmoCRM:
        """Exchange authorization code for tokens, save them, return a new client."""
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
        if self._leads is None:
            self._leads = LeadsResource(self)
        return self._leads

    @property
    def pipelines(self) -> PipelinesResource:
        if self._pipelines is None:
            self._pipelines = PipelinesResource(self)
        return self._pipelines

    @property
    def contacts(self) -> ContactsResource:
        if self._contacts is None:
            self._contacts = ContactsResource(self)
        return self._contacts

    @property
    def companies(self) -> CompaniesResource:
        if self._companies is None:
            self._companies = CompaniesResource(self)
        return self._companies
