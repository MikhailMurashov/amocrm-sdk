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
        custom_fields_values=[
            CustomFieldValue(field_id=5, values=[{"value": "x"}])
        ]
    )
    assert lead.get_cf_enum_id(5) is None


def test_mixin_is_not_dataclass():
    """CustomFieldsMixin не должен быть датаклассом."""
    import dataclasses
    assert not dataclasses.is_dataclass(CustomFieldsMixin)


def test_lead_is_instance_of_mixin():
    lead = Lead()
    assert isinstance(lead, CustomFieldsMixin)
