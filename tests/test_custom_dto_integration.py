"""Интеграционные тесты кастомных DTO."""
from __future__ import annotations

from dataclasses import dataclass

from amocrm.models.common import CustomFieldValue
from amocrm.models.leads import Lead


def test_custom_lead_to_dict_includes_custom_fields():
    """Кастомный подкласс Lead корректно сериализуется для отправки в API."""

    @dataclass(kw_only=True)
    class MyLead(Lead):
        @property
        def phone(self) -> str | None:
            return self.get_cf_value(123)  # type: ignore[return-value]

    lead = MyLead(
        name="Test Lead",
        custom_fields_values=[
            CustomFieldValue(field_id=123, values=[{"value": "+7999"}])
        ],
    )
    data = lead.to_dict()
    assert data["name"] == "Test Lead"
    cf = next(cf for cf in data["custom_fields_values"] if cf["field_id"] == 123)
    assert cf["values"][0]["value"] == "+7999"


def test_custom_lead_from_dict_populates_properties():
    """Кастомный подкласс Lead корректно разбирает ответ API."""

    @dataclass(kw_only=True)
    class MyLead(Lead):
        @property
        def phone(self) -> str | None:
            return self.get_cf_value(123)  # type: ignore[return-value]

        @property
        def tags_list(self) -> list[str]:
            return self.get_cf_values(456)  # type: ignore[return-value]

    api_response = {
        "id": 1,
        "name": "Test Lead",
        "custom_fields_values": [
            {"field_id": 123, "values": [{"value": "+7999"}]},
            {"field_id": 456, "values": [{"value": "VIP"}, {"value": "Новый"}]},
        ],
    }
    lead = MyLead.from_dict(api_response)
    assert lead.phone == "+7999"
    assert lead.tags_list == ["VIP", "Новый"]


def test_custom_lead_missing_cf_field():
    """get_cf_value возвращает None для несуществующего поля."""

    @dataclass(kw_only=True)
    class MyLead(Lead):
        @property
        def budget(self) -> float | None:
            v = self.get_cf_value(999)
            return float(v) if v is not None else None

    lead = MyLead.from_dict({"name": "No CF"})
    assert lead.budget is None


def test_custom_lead_no_custom_fields():
    """Mixin работает корректно при custom_fields_values=None."""

    @dataclass(kw_only=True)
    class MyLead(Lead):
        @property
        def source(self) -> str | None:
            return self.get_cf_value(1)  # type: ignore[return-value]

    lead = MyLead(name="Empty")
    assert lead.source is None
    assert lead.get_cf_raw(1) is None
    assert lead.get_cf_values(1) == []
    assert lead.get_cf_enum_id(1) is None


def test_custom_lead_multiselect():
    """get_cf_values корректно возвращает все значения мультиселекта."""

    @dataclass(kw_only=True)
    class MyLead(Lead):
        @property
        def categories(self) -> list[str]:
            return self.get_cf_values(10)  # type: ignore[return-value]

    lead = MyLead(
        custom_fields_values=[
            CustomFieldValue(
                field_id=10,
                values=[{"value": "Кат1"}, {"value": "Кат2"}, {"value": "Кат3"}],
            )
        ]
    )
    assert lead.categories == ["Кат1", "Кат2", "Кат3"]


def test_custom_lead_to_dict_no_cf():
    """to_dict не включает custom_fields_values когда они не заданы."""

    @dataclass(kw_only=True)
    class MyLead(Lead):
        pass

    lead = MyLead(name="No CF Lead")
    data = lead.to_dict()
    assert "custom_fields_values" not in data
    assert data["name"] == "No CF Lead"
