from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .common import CustomFieldsMixin, CustomFieldValue, Tag

_COMPANY_SCALAR_FIELDS = (
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


@dataclass(kw_only=True)
class Company(CustomFieldsMixin):
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Company:
        """Создать экземпляр из словаря API AmoCRM."""
        tags_raw = data.get("_embedded", {}).get("tags")
        cf_raw = data.get("custom_fields_values")
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            responsible_user_id=data.get("responsible_user_id"),
            group_id=data.get("group_id"),
            created_by=data.get("created_by"),
            updated_by=data.get("updated_by"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            closest_task_at=data.get("closest_task_at"),
            is_deleted=data.get("is_deleted"),
            account_id=data.get("account_id"),
            tags=[Tag.from_dict(t) for t in tags_raw] if tags_raw is not None else None,
            custom_fields_values=(
                [CustomFieldValue.from_dict(cf) for cf in cf_raw]
                if cf_raw is not None
                else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать в словарь для API, исключая поля со значением ``None``."""
        result: dict[str, Any] = {
            k: getattr(self, k)
            for k in _COMPANY_SCALAR_FIELDS
            if getattr(self, k) is not None
        }
        if self.tags is not None:
            result["tags"] = [t.to_dict() for t in self.tags]
        if self.custom_fields_values is not None:
            result["custom_fields_values"] = [
                cf.to_dict() for cf in self.custom_fields_values
            ]
        return result
