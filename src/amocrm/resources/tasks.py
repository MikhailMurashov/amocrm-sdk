from __future__ import annotations

import builtins
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from ..models.tasks import Task
from ._utils import _iter_all_pages

if TYPE_CHECKING:
    from ..client import AmoCRM


class TasksResource:
    """Ресурс для работы с задачами AmoCRM (``/api/v4/tasks``)."""

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
        filter: dict[str, Any] | None = None,
        order: dict[str, str] | None = None,
    ) -> builtins.list[Task] | Iterator[Task]:
        """Получить список задач с пагинацией и фильтрами.

        Args:
            page: Номер страницы (начиная с 1). Если не передан — автоматически
                обходит все страницы и возвращает ``Iterator[Task]``.
            limit: Количество задач на странице (максимум 250). По умолчанию 50
                при авто-пагинации.
            filter: Словарь фильтров вида ``{"field": "value"}``; ключи
                преобразуются в параметры ``filter[field]=value``.
            order: Словарь сортировки вида ``{"field": "asc"|"desc"}``; ключи
                преобразуются в параметры ``order[field]=asc``.

        Returns:
            Если ``page`` передан — список объектов :class:`~amocrm.models.tasks.Task`.
            Если ``page`` не передан — ``Iterator[Task]`` по всем страницам.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if filter is not None:
            for key, value in filter.items():
                params[f"filter[{key}]"] = value
        if order is not None:
            for key, value in order.items():
                params[f"order[{key}]"] = value
        if page is not None:
            params["page"] = page
            raw = self._client._request("GET", "/api/v4/tasks", params=params)
            return [
                Task.from_dict(d) for d in raw.get("_embedded", {}).get("tasks", [])
            ]
        return (
            Task.from_dict(d)
            for d in _iter_all_pages(self._client, "/api/v4/tasks", "tasks", params)
        )

    def get(self, task_id: int) -> Task:
        """Получить задачу по идентификатору.

        Args:
            task_id: Идентификатор задачи.

        Returns:
            Объект :class:`~amocrm.models.tasks.Task`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request("GET", f"/api/v4/tasks/{task_id}")
        return Task.from_dict(raw)

    def create(self, tasks: builtins.list[Task]) -> builtins.list[Task]:
        """Создать одну или несколько задач.

        Args:
            tasks: Список задач для создания.

        Returns:
            Список созданных задач с заполненными идентификаторами.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request(
            "POST", "/api/v4/tasks", json=[task.to_dict() for task in tasks]
        )
        return [Task.from_dict(d) for d in raw.get("_embedded", {}).get("tasks", [])]

    def update(self, tasks: builtins.list[Task]) -> builtins.list[Task]:
        """Обновить одну или несколько задач (каждая должна содержать ``id``).

        Args:
            tasks: Список задач для обновления. Каждая задача обязана
                содержать заполненное поле ``id``.

        Returns:
            Список обновлённых задач.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request(
            "PATCH", "/api/v4/tasks", json=[task.to_dict() for task in tasks]
        )
        return [Task.from_dict(d) for d in raw.get("_embedded", {}).get("tasks", [])]

    def update_one(self, task_id: int, data: Task) -> Task:
        """Обновить одну задачу по идентификатору.

        Args:
            task_id: Идентификатор задачи.
            data: Объект с обновляемыми полями.

        Returns:
            Обновлённый объект :class:`~amocrm.models.tasks.Task`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request(
            "PATCH", f"/api/v4/tasks/{task_id}", json=data.to_dict()
        )
        return Task.from_dict(raw)
