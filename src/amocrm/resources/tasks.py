from __future__ import annotations

import builtins
from collections.abc import Iterator
from typing import Any

from ..models.tasks import Task
from ._base import BaseResource


class TasksResource(BaseResource[Task]):
    """Ресурс для работы с задачами AmoCRM (``/api/v4/tasks``)."""

    _path = "/api/v4/tasks"
    _embedded_key = "tasks"
    _dto_class = Task

    def list(  # type: ignore[override]
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
        return super().list(page=page, limit=limit, filter=filter, order=order)

    def get(self, task_id: int) -> Task:  # type: ignore[override]
        """Получить задачу по идентификатору.

        Args:
            task_id: Идентификатор задачи.

        Returns:
            Объект :class:`~amocrm.models.tasks.Task`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        return super().get(task_id)
