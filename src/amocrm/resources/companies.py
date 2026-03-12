from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from ..models.companies import Company

if TYPE_CHECKING:
    from ..client import AmoCRM


class CompaniesResource:
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
    ) -> builtins.list[Company]:
        """GET /api/v4/companies — список компаний с пагинацией и фильтрами."""
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
        """GET /api/v4/companies/{id} — получить компанию по ID."""
        params: dict[str, Any] = {}
        if with_ is not None:
            params["with"] = ",".join(with_)
        raw = self._client._request(
            "GET", f"/api/v4/companies/{company_id}", params=params
        )
        return Company.from_dict(raw)

    def create(self, companies: builtins.list[Company]) -> builtins.list[Company]:
        """POST /api/v4/companies — создать компании."""
        raw = self._client._request(
            "POST", "/api/v4/companies", json=[c.to_dict() for c in companies]
        )
        items = raw.get("_embedded", {}).get("companies", [])
        return [Company.from_dict(d) for d in items]

    def update(self, companies: builtins.list[Company]) -> builtins.list[Company]:
        """PATCH /api/v4/companies — обновить компании (каждая должна содержать id)."""
        raw = self._client._request(
            "PATCH", "/api/v4/companies", json=[c.to_dict() for c in companies]
        )
        items = raw.get("_embedded", {}).get("companies", [])
        return [Company.from_dict(d) for d in items]

    def update_one(self, company_id: int, data: Company) -> Company:
        """PATCH /api/v4/companies/{id} — обновить одну компанию."""
        raw = self._client._request(
            "PATCH", f"/api/v4/companies/{company_id}", json=data.to_dict()
        )
        return Company.from_dict(raw)
