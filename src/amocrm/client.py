from __future__ import annotations

from typing import Any

import requests

from .exceptions import AmoCRMAPIError
from .resources.companies import CompaniesResource
from .resources.contacts import ContactsResource
from .resources.leads import LeadsResource
from .resources.pipelines import PipelinesResource


class AmoCRM:
    def __init__(self, subdomain: str, access_token: str) -> None:
        self._base_url = f"https://{subdomain}.amocrm.ru"
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {access_token}"})
        self._leads: LeadsResource | None = None
        self._pipelines: PipelinesResource | None = None
        self._contacts: ContactsResource | None = None
        self._companies: CompaniesResource | None = None

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        url = self._base_url + path
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
