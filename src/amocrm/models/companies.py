from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .common import BaseModel, CustomFieldValue, Tag


@dataclass(kw_only=True)
class Company(BaseModel):
    """DTO-модель компании AmoCRM.

    Attributes:
        id: Идентификатор компании.
        name: Название компании.
        responsible_user_id: Идентификатор ответственного пользователя.
        group_id: Идентификатор группы пользователей.
        created_by: Идентификатор пользователя, создавшего компанию.
        updated_by: Идентификатор пользователя, обновившего компанию.
        created_at: Дата создания (Unix timestamp).
        updated_at: Дата последнего изменения (Unix timestamp).
        closest_task_at: Дата ближайшей задачи (Unix timestamp).
        is_deleted: Признак удалённой компании.
        account_id: Идентификатор аккаунта AmoCRM.
        tags: Список тегов компании.
        custom_fields_values: Список значений кастомных полей.
    """

    _scalar_fields: ClassVar[tuple[str, ...]] = (
        "id",
        "name",
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
