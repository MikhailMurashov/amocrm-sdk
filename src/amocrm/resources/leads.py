from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from ..models.leads import Lead

if TYPE_CHECKING:
    from ..client import AmoCRM


class LeadsResource:
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
    ) -> builtins.list[Lead]:
        """GET /api/v4/leads — список сделок с пагинацией и фильтрами."""
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
        self, lead_id: int, *, with_: builtins.list[str] | None = None
    ) -> Lead:
        """GET /api/v4/leads/{id} — получить сделку по ID."""
        params: dict[str, Any] = {}
        if with_ is not None:
            params["with"] = ",".join(with_)
        raw = self._client._request("GET", f"/api/v4/leads/{lead_id}", params=params)
        return Lead.from_dict(raw)

    def create(self, leads: builtins.list[Lead]) -> builtins.list[Lead]:
        """POST /api/v4/leads — создать сделки."""
        raw = self._client._request(
            "POST", "/api/v4/leads", json=[lead.to_dict() for lead in leads]
        )
        return [Lead.from_dict(d) for d in raw.get("_embedded", {}).get("leads", [])]

    def update(self, leads: builtins.list[Lead]) -> builtins.list[Lead]:
        """PATCH /api/v4/leads — обновить сделки (каждая должна содержать id)."""
        raw = self._client._request(
            "PATCH", "/api/v4/leads", json=[lead.to_dict() for lead in leads]
        )
        return [Lead.from_dict(d) for d in raw.get("_embedded", {}).get("leads", [])]

    def update_one(self, lead_id: int, data: Lead) -> Lead:
        """PATCH /api/v4/leads/{id} — обновить одну сделку."""
        raw = self._client._request(
            "PATCH", f"/api/v4/leads/{lead_id}", json=data.to_dict()
        )
        return Lead.from_dict(raw)

    def create_complex(self, leads: builtins.list[Lead]) -> builtins.list[Lead]:
        """POST /api/v4/leads/complex — сложное создание со связями."""
        raw = self._client._request(
            "POST", "/api/v4/leads/complex", json=[lead.to_dict() for lead in leads]
        )
        return [Lead.from_dict(d) for d in raw.get("_embedded", {}).get("leads", [])]
