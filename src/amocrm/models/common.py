from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any


@dataclass(kw_only=True)
class Tag:
    """Тег сущности AmoCRM.

    Attributes:
        id: Идентификатор тега.
        name: Название тега.
    """

    id: int | None = None
    name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Tag:
        """Создать экземпляр из словаря API."""
        return cls(id=data.get("id"), name=data.get("name"))

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать в словарь, исключая поля со значением ``None``."""
        return {k: v for k, v in dataclasses.asdict(self).items() if v is not None}


@dataclass(kw_only=True)
class CustomFieldValue:
    """Значение кастомного поля AmoCRM.

    Attributes:
        field_id: Идентификатор кастомного поля.
        values: Список значений поля (каждое — словарь с ключами ``value``
            и опционально ``enum_id`` / ``enum_code``).
    """

    field_id: int
    values: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CustomFieldValue:
        """Создать экземпляр из словаря API."""
        return cls(field_id=data["field_id"], values=data.get("values", []))

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать в словарь для отправки в API."""
        return {"field_id": self.field_id, "values": self.values}
