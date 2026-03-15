from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator

if TYPE_CHECKING:
    from ..client import AmoCRM

_DEFAULT_PAGE_LIMIT = 50


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
