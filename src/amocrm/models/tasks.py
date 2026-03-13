from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_TASK_SCALAR_FIELDS = (
    "id",
    "text",
    "complete_till",
    "task_type_id",
    "responsible_user_id",
    "is_completed",
    "entity_id",
    "entity_type",
    "duration",
    "created_by",
    "updated_by",
    "created_at",
    "updated_at",
    "group_id",
    "account_id",
)


@dataclass(kw_only=True)
class Task:
    """DTO-модель задачи AmoCRM.

    Attributes:
        id: Идентификатор задачи.
        text: Текст задачи.
        complete_till: Срок выполнения (Unix timestamp).
        task_type_id: Идентификатор типа задачи.
        responsible_user_id: Идентификатор ответственного пользователя.
        is_completed: Признак выполненной задачи.
        entity_id: Идентификатор связанной сущности.
        entity_type: Тип связанной сущности (``"leads"``, ``"contacts"`` и др.).
        duration: Длительность задачи (в секундах).
        created_by: Идентификатор пользователя, создавшего задачу.
        updated_by: Идентификатор пользователя, обновившего задачу.
        created_at: Дата создания (Unix timestamp).
        updated_at: Дата последнего изменения (Unix timestamp).
        group_id: Идентификатор группы пользователей.
        account_id: Идентификатор аккаунта AmoCRM.
        result: Результат выполнения задачи вида ``{"text": "..."}``.
    """

    id: int | None = None
    text: str | None = None
    complete_till: int | None = None
    task_type_id: int | None = None
    responsible_user_id: int | None = None
    is_completed: bool | None = None
    entity_id: int | None = None
    entity_type: str | None = None
    duration: int | None = None
    created_by: int | None = None
    updated_by: int | None = None
    created_at: int | None = None
    updated_at: int | None = None
    group_id: int | None = None
    account_id: int | None = None
    result: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        """Создать экземпляр из словаря API AmoCRM."""
        return cls(
            **{k: data.get(k) for k in _TASK_SCALAR_FIELDS},
            result=data.get("result"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать в словарь для API, исключая поля со значением ``None``."""
        result: dict[str, Any] = {
            k: getattr(self, k)
            for k in _TASK_SCALAR_FIELDS
            if getattr(self, k) is not None
        }
        if self.result is not None:
            result["result"] = self.result
        return result
