"""Тесты CustomFieldsMixin."""

from __future__ import annotations

from amocrm.models.common import CustomFieldsMixin, CustomFieldValue
from amocrm.models.leads import Lead


def _make_lead(**cf_kwargs: object) -> Lead:
    """Вспомогательная функция для создания Lead с кастомными полями."""
    return Lead(
        custom_fields_values=[
            CustomFieldValue(field_id=1, values=[{"value": "hello", "enum_id": 42}]),
            CustomFieldValue(
                field_id=2, values=[{"value": "A"}, {"value": "B"}, {"value": "C"}]
            ),
            CustomFieldValue(field_id=3, values=[{"value": True}]),
            CustomFieldValue(field_id=4, values=[]),
        ]
    )


# --- Getter tests ---


def test_get_cf_raw_existing():
    lead = _make_lead()
    result = lead.get_cf_raw(1)
    assert result == [{"value": "hello", "enum_id": 42}]


def test_get_cf_raw_missing():
    lead = _make_lead()
    assert lead.get_cf_raw(999) is None


def test_get_cf_raw_none_values():
    lead = Lead(custom_fields_values=None)
    assert lead.get_cf_raw(1) is None


def test_get_cf_value_existing():
    lead = _make_lead()
    assert lead.get_cf_value(1) == "hello"


def test_get_cf_value_missing():
    lead = _make_lead()
    assert lead.get_cf_value(999) is None


def test_get_cf_value_empty_values():
    lead = _make_lead()
    assert lead.get_cf_value(4) is None


def test_get_cf_values_multiple():
    lead = _make_lead()
    assert lead.get_cf_values(2) == ["A", "B", "C"]


def test_get_cf_values_single():
    lead = _make_lead()
    assert lead.get_cf_values(1) == ["hello"]


def test_get_cf_values_missing():
    lead = _make_lead()
    assert lead.get_cf_values(999) == []


def test_get_cf_values_empty_values():
    lead = _make_lead()
    assert lead.get_cf_values(4) == []


def test_get_cf_enum_id_existing():
    lead = _make_lead()
    assert lead.get_cf_enum_id(1) == 42


def test_get_cf_enum_id_missing():
    lead = _make_lead()
    assert lead.get_cf_enum_id(999) is None


def test_get_cf_enum_id_no_enum():
    lead = Lead(
        custom_fields_values=[CustomFieldValue(field_id=5, values=[{"value": "x"}])]
    )
    assert lead.get_cf_enum_id(5) is None


def test_mixin_is_not_dataclass():
    """CustomFieldsMixin не должен быть датаклассом."""
    import dataclasses

    assert not dataclasses.is_dataclass(CustomFieldsMixin)


def test_lead_is_instance_of_mixin():
    lead = Lead()
    assert isinstance(lead, CustomFieldsMixin)


# --- Setter tests ---


def test_set_cf_value_new_field():
    """set_cf_value создаёт новое поле, если его нет."""
    lead = Lead(custom_fields_values=None)
    lead.set_cf_value(100, "new_value")
    assert lead.custom_fields_values is not None
    assert len(lead.custom_fields_values) == 1
    assert lead.custom_fields_values[0].field_id == 100
    assert lead.custom_fields_values[0].values == [{"value": "new_value"}]


def test_set_cf_value_update_existing():
    """set_cf_value обновляет значение существующего поля."""
    lead = Lead(
        custom_fields_values=[CustomFieldValue(field_id=100, values=[{"value": "old"}])]
    )
    lead.set_cf_value(100, "updated")
    assert len(lead.custom_fields_values) == 1
    assert lead.custom_fields_values[0].values == [{"value": "updated"}]


def test_set_cf_value_none_clears():
    """set_cf_value с None очищает значения (пустой список)."""
    lead = Lead(
        custom_fields_values=[
            CustomFieldValue(field_id=100, values=[{"value": "something"}])
        ]
    )
    lead.set_cf_value(100, None)
    assert lead.custom_fields_values[0].values == []


def test_set_cf_value_none_no_create():
    """set_cf_value с None не создаёт новое поле."""
    lead = Lead(custom_fields_values=[])
    lead.set_cf_value(100, None)
    assert len(lead.custom_fields_values) == 0


def test_set_cf_value_initializes_list():
    """set_cf_value инициализирует custom_fields_values если None."""
    lead = Lead()
    assert lead.custom_fields_values is None
    lead.set_cf_value(100, "test")
    assert lead.custom_fields_values is not None
    assert lead.get_cf_value(100) == "test"


def test_set_cf_values_multiselect():
    """set_cf_values устанавливает несколько значений (multiselect)."""
    lead = Lead(custom_fields_values=None)
    lead.set_cf_values(200, ["A", "B", "C"])
    assert lead.custom_fields_values is not None
    assert len(lead.custom_fields_values) == 1
    assert lead.custom_fields_values[0].field_id == 200
    assert lead.custom_fields_values[0].values == [
        {"value": "A"},
        {"value": "B"},
        {"value": "C"},
    ]


def test_set_cf_values_update_existing():
    """set_cf_values обновляет значения существующего multiselect поля."""
    lead = Lead(
        custom_fields_values=[CustomFieldValue(field_id=200, values=[{"value": "old"}])]
    )
    lead.set_cf_values(200, ["X", "Y"])
    assert lead.custom_fields_values[0].values == [{"value": "X"}, {"value": "Y"}]


def test_set_cf_values_empty_list():
    """set_cf_values с пустым списком создаёт поле с пустым values."""
    lead = Lead(custom_fields_values=[])
    lead.set_cf_values(200, [])
    assert len(lead.custom_fields_values) == 1
    assert lead.custom_fields_values[0].values == []


def test_set_cf_raw_values():
    """set_cf_raw устанавливает raw-значения (например, smart_address)."""
    raw_vals = [
        {"value": "Москва", "type": "city"},
        {"value": "Россия", "type": "country"},
    ]
    lead = Lead(custom_fields_values=None)
    lead.set_cf_raw(300, raw_vals)
    assert lead.custom_fields_values is not None
    assert len(lead.custom_fields_values) == 1
    assert lead.custom_fields_values[0].field_id == 300
    assert lead.custom_fields_values[0].values == raw_vals


def test_set_cf_raw_update_existing():
    """set_cf_raw обновляет raw-значения существующего поля."""
    lead = Lead(
        custom_fields_values=[CustomFieldValue(field_id=300, values=[{"value": "old"}])]
    )
    new_vals = [{"value": "new", "extra": 42}]
    lead.set_cf_raw(300, new_vals)
    assert lead.custom_fields_values[0].values == new_vals


def test_set_cf_raw_none_clears():
    """set_cf_raw с None очищает значения (пустой список)."""
    lead = Lead(
        custom_fields_values=[
            CustomFieldValue(field_id=300, values=[{"value": "data"}])
        ]
    )
    lead.set_cf_raw(300, None)
    assert lead.custom_fields_values[0].values == []


def test_set_cf_raw_none_no_create():
    """set_cf_raw с None не создаёт новое поле."""
    lead = Lead(custom_fields_values=[])
    lead.set_cf_raw(300, None)
    assert len(lead.custom_fields_values) == 0


def test_setters_roundtrip():
    """Установленные через сеттеры значения доступны через геттеры."""
    lead = Lead()
    lead.set_cf_value(1, "hello")
    lead.set_cf_values(2, ["A", "B"])
    lead.set_cf_raw(3, [{"value": "raw", "enum_id": 5}])

    assert lead.get_cf_value(1) == "hello"
    assert lead.get_cf_values(2) == ["A", "B"]
    assert lead.get_cf_raw(3) == [{"value": "raw", "enum_id": 5}]
