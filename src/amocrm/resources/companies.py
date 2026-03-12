from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from ..models.companies import Company

if TYPE_CHECKING:
    from ..client import AmoCRM


class CompaniesResource:
    """Ресурс для работы с компаниями AmoCRM (``/api/v4/companies``)."""

    def __init__(self, client: AmoCRM) -> None:
        """
        Args:
            client: Экземпляр клиента :class:`~amocrm.client.AmoCRM`.
        """
        self._client = client

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        query: str | None = None,
        filter: dict[str, Any] | None = None,
        order: dict[str, str] | None = None,
        with_: builtins.list[str] | None = None,
    ) -> builtins.list[Company]:
        """Получить список компаний с пагинацией и фильтрами.

        Args:
            page: Номер страницы (начиная с 1).
            limit: Количество компаний на странице (максимум 250).
            query: Строка полнотекстового поиска.
            filter: Словарь фильтров вида ``{"field": "value"}``; ключи
                преобразуются в параметры ``filter[field]=value``.
            order: Словарь сортировки вида ``{"field": "asc"|"desc"}``; ключи
                преобразуются в параметры ``order[field]=asc``.
            with_: Список дополнительных данных для подгрузки.

        Returns:
            Список объектов :class:`~amocrm.models.companies.Company`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if query is not None:
            params["query"] = query
        if filter is not None:
            for key, value in filter.items():
                params[f"filter[{key}]"] = value
        if order is not None:
            for key, value in order.items():
                params[f"order[{key}]"] = value
        if with_ is not None:
            params["with"] = ",".join(with_)
        raw = self._client._request("GET", "/api/v4/companies", params=params)
        items = raw.get("_embedded", {}).get("companies", [])
        return [Company.from_dict(d) for d in items]

    def get(
        self, company_id: int, *, with_: builtins.list[str] | None = None
    ) -> Company:
        """Получить компанию по идентификатору.

        Args:
            company_id: Идентификатор компании.
            with_: Список дополнительных данных для подгрузки.

        Returns:
            Объект :class:`~amocrm.models.companies.Company`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        params: dict[str, Any] = {}
        if with_ is not None:
            params["with"] = ",".join(with_)
        raw = self._client._request(
            "GET", f"/api/v4/companies/{company_id}", params=params
        )
        return Company.from_dict(raw)

    def create(self, companies: builtins.list[Company]) -> builtins.list[Company]:
        """Создать одну или несколько компаний.

        Args:
            companies: Список компаний для создания.

        Returns:
            Список созданных компаний с заполненными идентификаторами.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request(
            "POST", "/api/v4/companies", json=[c.to_dict() for c in companies]
        )
        items = raw.get("_embedded", {}).get("companies", [])
        return [Company.from_dict(d) for d in items]

    def update(self, companies: builtins.list[Company]) -> builtins.list[Company]:
        """Обновить одну или несколько компаний (каждая должна содержать ``id``).

        Args:
            companies: Список компаний для обновления. Каждая компания обязана
                содержать заполненное поле ``id``.

        Returns:
            Список обновлённых компаний.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request(
            "PATCH", "/api/v4/companies", json=[c.to_dict() for c in companies]
        )
        items = raw.get("_embedded", {}).get("companies", [])
        return [Company.from_dict(d) for d in items]

    def update_one(self, company_id: int, data: Company) -> Company:
        """Обновить одну компанию по идентификатору.

        Args:
            company_id: Идентификатор компании.
            data: Объект с обновляемыми полями.

        Returns:
            Обновлённый объект :class:`~amocrm.models.companies.Company`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request(
            "PATCH", f"/api/v4/companies/{company_id}", json=data.to_dict()
        )
        return Company.from_dict(raw)
