from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any


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
