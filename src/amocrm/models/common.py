from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any


class CustomFieldsMixin:
    """Mixin для типизированного доступа к кастомным полям AmoCRM.

    Предоставляет методы для чтения значений кастомных полей по их ID.
    Должен использоваться совместно с датаклассами, имеющими поле
    ``custom_fields_values: list[CustomFieldValue] | None``.
    """

    custom_fields_values: list[CustomFieldValue] | None

    def get_cf_raw(self, field_id: int) -> list[dict[str, Any]] | None:
        """Вернуть список значений кастомного поля по его ID или ``None``."""
        if self.custom_fields_values is None:
            return None
        for cf in self.custom_fields_values:
            if cf.field_id == field_id:
                return cf.values
        return None

    def get_cf_value(self, field_id: int) -> Any:
        """Вернуть первое значение поля (``values[0]["value"]``) или ``None``."""
        values = self.get_cf_raw(field_id)
        if not values:
            return None
        return values[0].get("value")

    def get_cf_values(self, field_id: int) -> list[Any]:
        """Вернуть все значения поля (``values[i]["value"]``)."""
        values = self.get_cf_raw(field_id)
        if not values:
            return []
        return [v.get("value") for v in values]

    def get_cf_enum_id(self, field_id: int) -> int | None:
        """Вернуть ``enum_id`` первого значения поля или ``None``."""
        values = self.get_cf_raw(field_id)
        if not values:
            return None
        return values[0].get("enum_id")


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
