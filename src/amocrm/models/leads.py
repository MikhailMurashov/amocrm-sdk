from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any

_LEAD_SCALAR_FIELDS = (
    "id", "name", "price", "status_id", "pipeline_id",
    "responsible_user_id", "group_id", "created_by", "updated_by",
    "created_at", "updated_at", "closed_at", "closest_task_at",
    "is_deleted", "loss_reason_id", "score", "account_id", "labor_cost",
)


@dataclass(kw_only=True)
class Tag:
    id: int | None = None
    name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Tag:
        return cls(id=data.get("id"), name=data.get("name"))

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in dataclasses.asdict(self).items() if v is not None}


@dataclass(kw_only=True)
class CustomFieldValue:
    field_id: int
    values: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CustomFieldValue:
        return cls(field_id=data["field_id"], values=data.get("values", []))

    def to_dict(self) -> dict[str, Any]:
        return {"field_id": self.field_id, "values": self.values}


@dataclass(kw_only=True)
class Lead:
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Lead:
        tags_raw = data.get("_embedded", {}).get("tags")
        cf_raw = data.get("custom_fields_values")
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            price=data.get("price"),
            status_id=data.get("status_id"),
            pipeline_id=data.get("pipeline_id"),
            responsible_user_id=data.get("responsible_user_id"),
            group_id=data.get("group_id"),
            created_by=data.get("created_by"),
            updated_by=data.get("updated_by"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            closed_at=data.get("closed_at"),
            closest_task_at=data.get("closest_task_at"),
            is_deleted=data.get("is_deleted"),
            loss_reason_id=data.get("loss_reason_id"),
            score=data.get("score"),
            account_id=data.get("account_id"),
            labor_cost=data.get("labor_cost"),
            tags=[Tag.from_dict(t) for t in tags_raw] if tags_raw is not None else None,
            custom_fields_values=(
                [CustomFieldValue.from_dict(cf) for cf in cf_raw]
                if cf_raw is not None else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            k: getattr(self, k)
            for k in _LEAD_SCALAR_FIELDS
            if getattr(self, k) is not None
        }
        if self.tags is not None:
            result["tags"] = [t.to_dict() for t in self.tags]
        if self.custom_fields_values is not None:
            result["custom_fields_values"] = [
                cf.to_dict() for cf in self.custom_fields_values
            ]
        return result
