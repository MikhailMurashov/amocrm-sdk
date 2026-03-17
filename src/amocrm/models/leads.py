from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

from .common import BaseModel, CustomFieldValue, Tag
from .companies import Company
from .contacts import Contact


@dataclass(kw_only=True)
class ComplexLeadResult:
    """Результат создания сделки через ``/api/v4/leads/complex``.

    Attributes:
        id: Идентификатор созданной сделки.
        contact_id: Идентификатор связанного контакта.
        company_id: Идентификатор связанной компании.
        merged: Признак слияния с существующей сделкой.
        request_id: Список идентификаторов запросов.
    """

    id: int
    contact_id: int | None = None
    company_id: int | None = None
    merged: bool = False
    request_id: list[str] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ComplexLeadResult:
        """Создать экземпляр из словаря API AmoCRM."""
        return cls(
            id=data["id"],
            contact_id=data.get("contact_id"),
            company_id=data.get("company_id"),
            merged=data.get("merged", False),
            request_id=data.get("request_id"),
        )


@dataclass(kw_only=True)
class Lead(BaseModel):
    """DTO-модель сделки AmoCRM.

    Attributes:
        id: Идентификатор сделки.
        name: Название сделки.
        price: Бюджет сделки.
        status_id: Идентификатор статуса воронки.
        pipeline_id: Идентификатор воронки.
        responsible_user_id: Идентификатор ответственного пользователя.
        group_id: Идентификатор группы пользователей.
        created_by: Идентификатор пользователя, создавшего сделку.
        updated_by: Идентификатор пользователя, обновившего сделку.
        created_at: Дата создания (Unix timestamp).
        updated_at: Дата последнего изменения (Unix timestamp).
        closed_at: Дата закрытия сделки (Unix timestamp).
        closest_task_at: Дата ближайшей задачи (Unix timestamp).
        is_deleted: Признак удалённой сделки.
        loss_reason_id: Идентификатор причины закрытия (проигрыша).
        score: Оценка сделки.
        account_id: Идентификатор аккаунта AmoCRM.
        labor_cost: Затраченное время (в минутах).
        tags: Список тегов сделки.
        custom_fields_values: Список значений кастомных полей.
        contacts: Список связанных контактов.
        company: Связанная компания.
    """

    _scalar_fields: ClassVar[tuple[str, ...]] = (
        "id",
        "name",
        "price",
        "status_id",
        "pipeline_id",
        "responsible_user_id",
        "group_id",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
        "closed_at",
        "closest_task_at",
        "is_deleted",
        "loss_reason_id",
        "score",
        "account_id",
        "labor_cost",
    )

    id: int | None = None
    name: str | None = None
    price: int | None = None
    status_id: int | None = None
    pipeline_id: int | None = None
    responsible_user_id: int | None = None
    group_id: int | None = None
    created_by: int | None = None
    updated_by: int | None = None
    created_at: int | None = None
    updated_at: int | None = None
    closed_at: int | None = None
    closest_task_at: int | None = None
    is_deleted: bool | None = None
    loss_reason_id: int | None = None
    score: int | None = None
    account_id: int | None = None
    labor_cost: int | None = None
    tags: list[Tag] | None = None
    custom_fields_values: list[CustomFieldValue] | None = None
    contacts: list[Contact] | None = None
    company: Company | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Lead:
        """Создать экземпляр из словаря API AmoCRM."""
        embedded = data.get("_embedded", {})
        tags_raw = embedded.get("tags")
        cf_raw = data.get("custom_fields_values")
        contacts_raw = embedded.get("contacts")
        companies_raw = embedded.get("companies")
        kwargs: dict[str, Any] = {k: data.get(k) for k in cls._scalar_fields}
        if tags_raw is not None:
            kwargs["tags"] = [Tag.from_dict(t) for t in tags_raw]
        if cf_raw is not None:
            kwargs["custom_fields_values"] = [
                CustomFieldValue.from_dict(cf) for cf in cf_raw
            ]
        kwargs["contacts"] = (
            [Contact.from_dict(c) for c in contacts_raw] if contacts_raw else None
        )
        kwargs["company"] = (
            Company.from_dict(companies_raw[0]) if companies_raw else None
        )
        return cls(**kwargs)

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать в словарь для API, исключая поля со значением ``None``."""
        result = super().to_dict()
        embedded: dict[str, Any] = {}
        if self.contacts is not None:
            embedded["contacts"] = [c.to_dict() for c in self.contacts]
        if self.company is not None:
            embedded["companies"] = [self.company.to_dict()]
        if embedded:
            result["_embedded"] = embedded
        return result
