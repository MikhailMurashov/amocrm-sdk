from __future__ import annotations

import builtins
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from ..models.contacts import Contact
from ._utils import _iter_all_pages

if TYPE_CHECKING:
    from ..client import AmoCRM


class ContactsResource:
    """Ресурс для работы с контактами AmoCRM (``/api/v4/contacts``)."""

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
    ) -> builtins.list[Contact] | Iterator[Contact]:
        """Получить список контактов с пагинацией и фильтрами.

        Args:
            page: Номер страницы (начиная с 1). Если не передан — автоматически
                обходит все страницы и возвращает ``Iterator[Contact]``.
            limit: Количество контактов на странице (максимум 250). По умолчанию 50
                при авто-пагинации.
            query: Строка полнотекстового поиска.
            filter: Словарь фильтров вида ``{"field": "value"}``; ключи
                преобразуются в параметры ``filter[field]=value``.
            order: Словарь сортировки вида ``{"field": "asc"|"desc"}``; ключи
                преобразуются в параметры ``order[field]=asc``.
            with_: Список дополнительных данных для подгрузки.

        Returns:
            Если ``page`` передан — список :class:`~amocrm.models.contacts.Contact`.
            Если ``page`` не передан — ``Iterator[Contact]`` по всем страницам.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        params: dict[str, Any] = {}
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
        if page is not None:
            params["page"] = page
            raw = self._client._request("GET", "/api/v4/contacts", params=params)
            return [
                Contact.from_dict(d)
                for d in raw.get("_embedded", {}).get("contacts", [])
            ]
        return (
            Contact.from_dict(d)
            for d in _iter_all_pages(
                self._client, "/api/v4/contacts", "contacts", params
            )
        )

    def get(
        self, contact_id: int, *, with_: builtins.list[str] | None = None
    ) -> Contact:
        """Получить контакт по идентификатору.

        Args:
            contact_id: Идентификатор контакта.
            with_: Список дополнительных данных для подгрузки.

        Returns:
            Объект :class:`~amocrm.models.contacts.Contact`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        params: dict[str, Any] = {}
        if with_ is not None:
            params["with"] = ",".join(with_)
        raw = self._client._request(
            "GET", f"/api/v4/contacts/{contact_id}", params=params
        )
        return Contact.from_dict(raw)

    def create(self, contacts: builtins.list[Contact]) -> builtins.list[Contact]:
        """Создать один или несколько контактов.

        Args:
            contacts: Список контактов для создания.

        Returns:
            Список созданных контактов с заполненными идентификаторами.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request(
            "POST", "/api/v4/contacts", json=[c.to_dict() for c in contacts]
        )
        items = raw.get("_embedded", {}).get("contacts", [])
        return [Contact.from_dict(d) for d in items]

    def update(self, contacts: builtins.list[Contact]) -> builtins.list[Contact]:
        """Обновить один или несколько контактов (каждый должен содержать ``id``).

        Args:
            contacts: Список контактов для обновления. Каждый контакт обязан
                содержать заполненное поле ``id``.

        Returns:
            Список обновлённых контактов.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request(
            "PATCH", "/api/v4/contacts", json=[c.to_dict() for c in contacts]
        )
        items = raw.get("_embedded", {}).get("contacts", [])
        return [Contact.from_dict(d) for d in items]

    def update_one(self, contact_id: int, data: Contact) -> Contact:
        """Обновить один контакт по идентификатору.

        Args:
            contact_id: Идентификатор контакта.
            data: Объект с обновляемыми полями.

        Returns:
            Обновлённый объект :class:`~amocrm.models.contacts.Contact`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request(
            "PATCH", f"/api/v4/contacts/{contact_id}", json=data.to_dict()
        )
        return Contact.from_dict(raw)
