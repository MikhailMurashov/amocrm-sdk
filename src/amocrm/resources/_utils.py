from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any, Generator

if TYPE_CHECKING:
    from ..client import AmoCRM

_DEFAULT_PAGE_LIMIT = 50


def _build_params(
    *,
    limit: int | None = None,
    query: str | None = None,
    filter: dict[str, Any] | None = None,
    order: dict[str, str] | None = None,
    with_: builtins.list[str] | None = None,
) -> dict[str, Any]:
    """Собрать словарь query-параметров для list-эндпоинтов."""
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
    return params


def _iter_all_pages(
    client: AmoCRM,
    path: str,
    embedded_key: str,
    params: dict[str, Any],
) -> Generator[dict[str, Any], None, None]:
    """Yield raw dicts from all pages of a list endpoint."""
    params = dict(params)
    params.setdefault("limit", _DEFAULT_PAGE_LIMIT)
    limit = params["limit"]
    current_page = 1
    while True:
        params["page"] = current_page
        raw = client._request("GET", path, params=dict(params))
        items = raw.get("_embedded", {}).get(embedded_key, [])
        if not items:
            break
        yield from items
        if len(items) < limit:
            break
        current_page += 1
