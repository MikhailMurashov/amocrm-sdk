from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .common import BaseModel, CustomFieldValue, Tag


@dataclass(kw_only=True)
class Contact(BaseModel):
    """DTO-модель контакта AmoCRM.

    Attributes:
        id: Идентификатор контакта.
        name: Полное имя контакта.
        first_name: Имя.
        last_name: Фамилия.
        responsible_user_id: Идентификатор ответственного пользователя.
        group_id: Идентификатор группы пользователей.
        created_by: Идентификатор пользователя, создавшего контакт.
        updated_by: Идентификатор пользователя, обновившего контакт.
        created_at: Дата создания (Unix timestamp).
        updated_at: Дата последнего изменения (Unix timestamp).
        closest_task_at: Дата ближайшей задачи (Unix timestamp).
        is_deleted: Признак удалённого контакта.
        account_id: Идентификатор аккаунта AmoCRM.
        tags: Список тегов контакта.
        custom_fields_values: Список значений кастомных полей.
    """

    _scalar_fields: ClassVar[tuple[str, ...]] = (
        "id",
        "name",
        "first_name",
        "last_name",
        "responsible_user_id",
        "group_id",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
        "closest_task_at",
        "is_deleted",
        "account_id",
    )

    id: int | None = None
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    responsible_user_id: int | None = None
    group_id: int | None = None
    created_by: int | None = None
    updated_by: int | None = None
    created_at: int | None = None
    updated_at: int | None = None
    closest_task_at: int | None = None
    is_deleted: bool | None = None
    account_id: int | None = None
    tags: list[Tag] | None = None
    custom_fields_values: list[CustomFieldValue] | None = None
