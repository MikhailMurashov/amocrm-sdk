from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any


@dataclass(kw_only=True)
class CustomFieldEnum:
    """Вариант перечисления кастомного поля AmoCRM.

    Attributes:
        id: Идентификатор варианта.
        value: Текстовое значение варианта.
        sort: Порядок сортировки.
    """

    id: int
    value: str
    sort: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CustomFieldEnum:
        """Создать экземпляр из словаря API."""
        return cls(
            id=data["id"],
            value=data["value"],
            sort=data.get("sort"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать в словарь, исключая поля со значением ``None``."""
        return {k: v for k, v in dataclasses.asdict(self).items() if v is not None}


@dataclass(kw_only=True)
class CustomFieldDefinition:
    """Определение кастомного поля AmoCRM.

    Attributes:
        id: Идентификатор поля.
        name: Название поля.
        type: Тип поля (``"text"``, ``"select"``, ``"multiselect"`` и др.).
        sort: Порядок сортировки.
        is_required: Признак обязательного поля.
        enums: Варианты перечисления (для типов ``select``, ``multiselect`` и др.).
    """

    id: int
    name: str
    type: str
    sort: int | None = None
    is_required: bool | None = None
    enums: list[CustomFieldEnum] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CustomFieldDefinition:
        """Создать экземпляр из словаря API."""
        enums_raw = data.get("enums")
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            sort=data.get("sort"),
            is_required=data.get("is_required"),
            enums=(
                [CustomFieldEnum.from_dict(e) for e in enums_raw] if enums_raw else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать в словарь, исключая поля со значением ``None``."""
        result: dict[str, Any] = {"id": self.id, "name": self.name, "type": self.type}
        if self.sort is not None:
            result["sort"] = self.sort
        if self.is_required is not None:
            result["is_required"] = self.is_required
        if self.enums is not None:
            result["enums"] = [e.to_dict() for e in self.enums]
        return result
