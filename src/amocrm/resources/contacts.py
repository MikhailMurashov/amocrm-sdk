from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from ..models.contacts import Contact

if TYPE_CHECKING:
    from ..client import AmoCRM


class ContactsResource:
    def __init__(self, client: AmoCRM) -> None:
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
    ) -> builtins.list[Contact]:
        """GET /api/v4/contacts — список контактов с пагинацией и фильтрами."""
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
        raw = self._client._request("GET", "/api/v4/contacts", params=params)
        items = raw.get("_embedded", {}).get("contacts", [])
        return [Contact.from_dict(d) for d in items]

    def get(
        self, contact_id: int, *, with_: builtins.list[str] | None = None
    ) -> Contact:
        """GET /api/v4/contacts/{id} — получить контакт по ID."""
        params: dict[str, Any] = {}
        if with_ is not None:
            params["with"] = ",".join(with_)
        raw = self._client._request(
            "GET", f"/api/v4/contacts/{contact_id}", params=params
        )
        return Contact.from_dict(raw)

    def create(self, contacts: builtins.list[Contact]) -> builtins.list[Contact]:
        """POST /api/v4/contacts — создать контакты."""
        raw = self._client._request(
            "POST", "/api/v4/contacts", json=[c.to_dict() for c in contacts]
        )
        items = raw.get("_embedded", {}).get("contacts", [])
        return [Contact.from_dict(d) for d in items]

    def update(self, contacts: builtins.list[Contact]) -> builtins.list[Contact]:
        """PATCH /api/v4/contacts — обновить контакты (каждый должен содержать id)."""
        raw = self._client._request(
            "PATCH", "/api/v4/contacts", json=[c.to_dict() for c in contacts]
        )
        items = raw.get("_embedded", {}).get("contacts", [])
        return [Contact.from_dict(d) for d in items]

    def update_one(self, contact_id: int, data: Contact) -> Contact:
        """PATCH /api/v4/contacts/{id} — обновить один контакт."""
        raw = self._client._request(
            "PATCH", f"/api/v4/contacts/{contact_id}", json=data.to_dict()
        )
        return Contact.from_dict(raw)
