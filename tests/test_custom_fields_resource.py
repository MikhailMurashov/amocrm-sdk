"""Тесты CustomFieldsResource."""

from __future__ import annotations

from unittest.mock import MagicMock

from amocrm.models.custom_fields import CustomFieldDefinition, CustomFieldEnum
from amocrm.resources.custom_fields import CustomFieldsResource


def _make_resource(response: dict) -> CustomFieldsResource:
    client = MagicMock()
    client._request.return_value = response
    return CustomFieldsResource(client)


_FIELD_DATA = {
    "id": 123,
    "name": "Источник",
    "type": "select",
    "sort": 10,
    "is_required": False,
    "enums": [
        {"id": 1, "value": "Сайт", "sort": 1},
        {"id": 2, "value": "Звонок", "sort": 2},
    ],
}

_LIST_RESPONSE = {"_embedded": {"custom_fields": [_FIELD_DATA]}}


def test_list_returns_definitions():
    resource = _make_resource(_LIST_RESPONSE)
    fields = resource.list("leads")
    resource._client._request.assert_called_once_with(
        "GET", "/api/v4/leads/custom_fields"
    )
    assert len(fields) == 1
    f = fields[0]
    assert isinstance(f, CustomFieldDefinition)
    assert f.id == 123
    assert f.name == "Источник"
    assert f.type == "select"
    assert f.sort == 10
    assert f.is_required is False


def test_list_parses_enums():
    resource = _make_resource(_LIST_RESPONSE)
    fields = resource.list("leads")
    assert fields[0].enums is not None
    assert len(fields[0].enums) == 2
    assert fields[0].enums[0].value == "Сайт"
    assert fields[0].enums[1].id == 2


def test_list_empty():
    resource = _make_resource({"_embedded": {"custom_fields": []}})
    assert resource.list("contacts") == []


def test_list_no_embedded():
    resource = _make_resource({})
    assert resource.list("companies") == []


def test_get_returns_definition():
    resource = _make_resource(_FIELD_DATA)
    field = resource.get("leads", 123)
    resource._client._request.assert_called_once_with(
        "GET", "/api/v4/leads/custom_fields/123"
    )
    assert isinstance(field, CustomFieldDefinition)
    assert field.id == 123
    assert field.name == "Источник"


def test_get_contacts():
    resource = _make_resource(
        {**_FIELD_DATA, "id": 456, "name": "Телефон", "type": "phone"}
    )
    field = resource.get("contacts", 456)
    resource._client._request.assert_called_once_with(
        "GET", "/api/v4/contacts/custom_fields/456"
    )
    assert field.type == "phone"


def test_field_definition_to_dict():
    f = CustomFieldDefinition(
        id=1, name="Test", type="text", sort=5, enums=[CustomFieldEnum(id=1, value="A")]
    )
    d = f.to_dict()
    assert d == {
        "id": 1,
        "name": "Test",
        "type": "text",
        "sort": 5,
        "enums": [{"id": 1, "value": "A"}],
    }


def test_field_definition_to_dict_minimal():
    f = CustomFieldDefinition(id=1, name="Test", type="text")
    d = f.to_dict()
    assert d == {"id": 1, "name": "Test", "type": "text"}


def test_custom_field_enum_to_dict_excludes_none():
    e = CustomFieldEnum(id=1, value="A")
    assert e.to_dict() == {"id": 1, "value": "A"}


def test_custom_field_enum_to_dict_with_sort():
    e = CustomFieldEnum(id=1, value="A", sort=3)
    assert e.to_dict() == {"id": 1, "value": "A", "sort": 3}
