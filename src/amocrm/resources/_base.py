from __future__ import annotations

import builtins
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar

from ..exceptions import AmoCRMError
from ._utils import _build_params, _iter_all_pages

if TYPE_CHECKING:
    from ..client import AmoCRM


class _DTOProtocol(Protocol):
    """Структурный интерфейс DTO-моделей, используемых в BaseResource."""

    id: int | None

    def to_dict(self) -> dict[str, Any]: ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Any: ...


_T = TypeVar("_T", bound=_DTOProtocol)


class BaseResource(Generic[_T]):
    """Базовый класс ресурсов AmoCRM API.

    Предоставляет стандартные CRUD-операции: ``list``, ``get``, ``create``,
    ``update``, ``update_one``. Конкретные ресурсы наследуют этот класс,
    задавая ``_path``, ``_embedded_key`` и ``_dto_class``.
    """

    _path: str
    _embedded_key: str
    _dto_class: type[_T]
    _max_per_request: int = 50

    def __init__(self, client: AmoCRM, dto_class: type[_T] | None = None) -> None:
        self._client = client
        if dto_class is not None:
            self._dto_class = dto_class

    def _parse(self, data: dict[str, Any]) -> _T:
        return self._dto_class.from_dict(data)  # type: ignore[no-any-return]

    def _parse_list(self, raw: dict[str, Any]) -> builtins.list[_T]:
        return [
            self._parse(d) for d in raw.get("_embedded", {}).get(self._embedded_key, [])
        ]

    def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        query: str | None = None,
        filter: dict[str, Any] | None = None,
        order: dict[str, str] | None = None,
        with_: builtins.list[str] | None = None,
    ) -> builtins.list[_T] | Iterator[_T]:
        """Получить список сущностей с пагинацией и фильтрами.

        Args:
            page: Номер страницы (начиная с 1). Если не передан — автоматически
                обходит все страницы и возвращает ``Iterator[T]``.
            limit: Количество сущностей на странице (максимум 250).
                По умолчанию 50 при авто-пагинации.
            query: Строка полнотекстового поиска.
            filter: Словарь фильтров ``{"field": "value"}``.
            order: Словарь сортировки ``{"field": "asc"|"desc"}``.
            with_: Список дополнительных данных для подгрузки.

        Returns:
            Если ``page`` передан — ``list[T]``. Иначе — ``Iterator[T]``.
        """
        params = _build_params(
            limit=limit,
            query=query,
            filter=filter,
            order=order,
            with_=with_,
        )
        if page is not None:
            params["page"] = page
            raw = self._client._request("GET", self._path, params=params)
            return self._parse_list(raw)
        return (
            self._parse(d)
            for d in _iter_all_pages(
                self._client, self._path, self._embedded_key, params
            )
        )

    def get(self, entity_id: int, *, with_: builtins.list[str] | None = None) -> _T:
        """Получить сущность по идентификатору.

        Args:
            entity_id: Идентификатор сущности.
            with_: Список дополнительных данных для подгрузки.
        """
        params: dict[str, Any] = {}
        if with_:
            params["with"] = ",".join(with_)
        raw = self._client._request(
            "GET",
            f"{self._path}/{entity_id}",
            params=params,
        )
        return self._parse(raw)

    def create(self, items: builtins.list[_T]) -> builtins.list[_T]:
        """Создать одну или несколько сущностей.

        Raises:
            AmoCRMError: Если передано более ``_max_per_request`` элементов.
        """
        if len(items) > self._max_per_request:
            raise AmoCRMError(
                f"create allows at most {self._max_per_request} items per request"
            )
        raw = self._client._request(
            "POST",
            self._path,
            json=[item.to_dict() for item in items],
        )
        return self._parse_list(raw)

    def update(self, items: builtins.list[_T]) -> builtins.list[_T]:
        """Обновить одну или несколько сущностей (каждая должна содержать ``id``).

        Raises:
            AmoCRMError: Если передано более ``_max_per_request`` элементов.
        """
        if len(items) > self._max_per_request:
            raise AmoCRMError(
                f"update allows at most {self._max_per_request} items per request"
            )
        raw = self._client._request(
            "PATCH",
            self._path,
            json=[item.to_dict() for item in items],
        )
        return self._parse_list(raw)

    def update_one(self, data: _T) -> _T:
        """Обновить одну сущность по идентификатору.

        Raises:
            AmoCRMError: Если ``data.id`` не задан.
        """
        if data.id is None:
            raise AmoCRMError(
                f"{self._dto_class.__name__}.id must be set for update_one"
            )
        raw = self._client._request(
            "PATCH",
            f"{self._path}/{data.id}",
            json=data.to_dict(),
        )
        return self._parse(raw)
