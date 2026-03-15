from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from ..exceptions import AmoCRMError
from ..models.leads import Lead

_MAX_LEADS_PER_REQUEST = 50

if TYPE_CHECKING:
    from ..client import AmoCRM


class LeadsResource:
    """Ресурс для работы со сделками AmoCRM (``/api/v4/leads``)."""

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
    ) -> builtins.list[Lead]:
        """Получить список сделок с пагинацией и фильтрами.

        Args:
            page: Номер страницы (начиная с 1).
            limit: Количество сделок на странице (максимум 250).
            query: Строка полнотекстового поиска.
            filter: Словарь фильтров вида ``{"field": "value"}``; ключи
                преобразуются в параметры ``filter[field]=value``.
            order: Словарь сортировки вида ``{"field": "asc"|"desc"}``; ключи
                преобразуются в параметры ``order[field]=asc``.
            with_: Список дополнительных данных для подгрузки (например,
                ``["contacts", "companies"]``).

        Returns:
            Список объектов :class:`~amocrm.models.leads.Lead`.

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
        raw = self._client._request("GET", "/api/v4/leads", params=params)
        return [Lead.from_dict(d) for d in raw.get("_embedded", {}).get("leads", [])]

    def get(
        self,
        lead_id: int,
        *,
        with_: builtins.list[str] | None = None,
    ) -> Lead:
        """Получить сделку по идентификатору.

        По умолчанию подгружает связанные контакты (``contacts``). Чтобы
        отключить это поведение или запросить другой набор данных, передайте
        ``with_`` явно, например ``with_=[]`` или
        ``with_=["contacts", "companies"]``.

        Args:
            lead_id: Идентификатор сделки.
            with_: Список дополнительных данных для подгрузки.
                По умолчанию ``["contacts"]``.

        Returns:
            Объект :class:`~amocrm.models.leads.Lead`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        if with_ is None:
            with_ = ["contacts"]
        params: dict[str, Any] = {}
        if with_:
            params["with"] = ",".join(with_)
        raw = self._client._request("GET", f"/api/v4/leads/{lead_id}", params=params)
        return Lead.from_dict(raw)

    def create(self, leads: builtins.list[Lead]) -> builtins.list[Lead]:
        """Создать одну или несколько сделок.

        Args:
            leads: Список сделок для создания.

        Returns:
            Список созданных сделок с заполненными идентификаторами.

        Raises:
            AmoCRMError: Если передано более 50 сделок за один запрос.
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        if len(leads) > _MAX_LEADS_PER_REQUEST:
            raise AmoCRMError(
                f"create allows at most {_MAX_LEADS_PER_REQUEST} leads per request"
            )
        raw = self._client._request(
            "POST", "/api/v4/leads", json=[lead.to_dict() for lead in leads]
        )
        return [Lead.from_dict(d) for d in raw.get("_embedded", {}).get("leads", [])]

    def update(self, leads: builtins.list[Lead]) -> builtins.list[Lead]:
        """Обновить одну или несколько сделок (каждая должна содержать ``id``).

        Args:
            leads: Список сделок для обновления. Каждая сделка обязана
                содержать заполненное поле ``id``.

        Returns:
            Список обновлённых сделок.

        Raises:
            AmoCRMError: Если передано более 50 сделок за один запрос.
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        if len(leads) > _MAX_LEADS_PER_REQUEST:
            raise AmoCRMError(
                f"update allows at most {_MAX_LEADS_PER_REQUEST} leads per request"
            )
        raw = self._client._request(
            "PATCH", "/api/v4/leads", json=[lead.to_dict() for lead in leads]
        )
        return [Lead.from_dict(d) for d in raw.get("_embedded", {}).get("leads", [])]

    def update_one(self, lead_id: int, data: Lead) -> Lead:
        """Обновить одну сделку по идентификатору.

        Args:
            lead_id: Идентификатор сделки.
            data: Объект с обновляемыми полями.

        Returns:
            Обновлённый объект :class:`~amocrm.models.leads.Lead`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request(
            "PATCH", f"/api/v4/leads/{lead_id}", json=data.to_dict()
        )
        return Lead.from_dict(raw)

    def create_complex(self, leads: builtins.list[Lead]) -> builtins.list[Lead]:
        """Сложное создание сделок со связанными сущностями.

        Использует эндпоинт ``POST /api/v4/leads/complex``, позволяющий
        одновременно создавать сделки вместе с контактами и компаниями.

        Args:
            leads: Список сделок для создания.

        Returns:
            Список созданных сделок с заполненными идентификаторами.

        Raises:
            AmoCRMError: Если передано более 50 сделок или у сделки
                более одного контакта.
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        if len(leads) > _MAX_LEADS_PER_REQUEST:
            raise AmoCRMError(
                f"create_complex allows at most {_MAX_LEADS_PER_REQUEST} leads"
                " per request"
            )
        for lead in leads:
            if lead.contacts is not None and len(lead.contacts) > 1:
                raise AmoCRMError("create_complex allows at most 1 contact per lead")
        raw = self._client._request(
            "POST", "/api/v4/leads/complex", json=[lead.to_dict() for lead in leads]
        )
        return [Lead.from_dict(d) for d in raw.get("_embedded", {}).get("leads", [])]
