from unittest.mock import MagicMock, patch

import pytest

from amocrm import AmoCRM, Contact, OAuthConfig
from amocrm.exceptions import AmoCRMAPIError


@pytest.fixture
def client() -> AmoCRM:
    storage = MagicMock()
    storage.load.return_value = ("token123", "refresh123")
    oauth = OAuthConfig(
        client_id="id",
        client_secret="secret",
        redirect_uri="https://example.com/callback",
        storage=storage,
    )
    return AmoCRM(subdomain="test", oauth=oauth)


def _mock_response(json_data: dict, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.ok = status_code < 400
    mock.content = b"data"
    mock.json.return_value = json_data
    mock.text = str(json_data)
    return mock


def test_list_contacts(client: AmoCRM) -> None:
    api_response = {
        "_embedded": {"contacts": [{"id": 1, "name": "John Doe", "first_name": "John"}]}
    }
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.contacts.list(page=1, limit=10, with_=["leads"])

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/contacts",
        params={"page": 1, "limit": 10, "with": "leads"},
    )
    assert len(result) == 1
    assert isinstance(result[0], Contact)
    assert result[0].id == 1
    assert result[0].name == "John Doe"
    assert result[0].first_name == "John"


def test_get_contact(client: AmoCRM) -> None:
    api_response = {"id": 42, "name": "Jane Smith", "last_name": "Smith"}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.contacts.get(42)

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/contacts/42",
        params={},
    )
    assert isinstance(result, Contact)
    assert result.id == 42
    assert result.name == "Jane Smith"
    assert result.last_name == "Smith"


def test_create_contacts(client: AmoCRM) -> None:
    new_contact = Contact(name="New Contact", first_name="New")
    api_response = {
        "_embedded": {
            "contacts": [{"id": 10, "name": "New Contact", "first_name": "New"}]
        }
    }
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.contacts.create([new_contact])

    mock_req.assert_called_once_with(
        "POST",
        "https://test.amocrm.ru/api/v4/contacts",
        json=[new_contact.to_dict()],
    )
    assert len(result) == 1
    assert isinstance(result[0], Contact)
    assert result[0].id == 10
    assert result[0].name == "New Contact"


def test_update_contacts(client: AmoCRM) -> None:
    updated_contact = Contact(id=10, name="Updated Name")
    api_response = {"_embedded": {"contacts": [{"id": 10, "name": "Updated Name"}]}}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.contacts.update([updated_contact])

    mock_req.assert_called_once_with(
        "PATCH",
        "https://test.amocrm.ru/api/v4/contacts",
        json=[updated_contact.to_dict()],
    )
    assert len(result) == 1
    assert isinstance(result[0], Contact)
    assert result[0].id == 10
    assert result[0].name == "Updated Name"


def test_update_one_contact(client: AmoCRM) -> None:
    data = Contact(name="Patched Name")
    api_response = {"id": 5, "name": "Patched Name"}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.contacts.update_one(5, data)

    mock_req.assert_called_once_with(
        "PATCH",
        "https://test.amocrm.ru/api/v4/contacts/5",
        json=data.to_dict(),
    )
    assert isinstance(result, Contact)
    assert result.id == 5
    assert result.name == "Patched Name"


def test_api_error_raises(client: AmoCRM) -> None:
    error_response = MagicMock()
    error_response.status_code = 401
    error_response.ok = False
    error_response.text = "Unauthorized"

    with patch.object(client, "_refresh_tokens"):
        with patch.object(client._session, "request", return_value=error_response):
            with pytest.raises(AmoCRMAPIError) as exc_info:
                list(client.contacts.list())

    assert exc_info.value.status_code == 401
    assert "Unauthorized" in str(exc_info.value)


def test_contact_to_dict_excludes_none() -> None:
    contact = Contact(name="Test", first_name="T")
    result = contact.to_dict()
    assert result == {"name": "Test", "first_name": "T"}
    assert "id" not in result
    assert "last_name" not in result


def test_contact_from_dict_with_tags() -> None:
    raw = {
        "id": 7,
        "name": "Tagged Contact",
        "first_name": "Tagged",
        "_embedded": {"tags": [{"id": 1, "name": "vip"}, {"id": 2, "name": "hot"}]},
    }
    contact = Contact.from_dict(raw)
    assert contact.id == 7
    assert contact.tags is not None
    assert len(contact.tags) == 2
    assert contact.tags[0].id == 1
    assert contact.tags[0].name == "vip"
    assert contact.tags[1].name == "hot"


def test_roundtrip_contact() -> None:
    raw = {
        "id": 42,
        "name": "Original Contact",
        "first_name": "Original",
        "last_name": "Contact",
        "_embedded": {"tags": [{"id": 3, "name": "promo"}]},
        "custom_fields_values": [{"field_id": 101, "values": [{"value": "hello"}]}],
    }
    contact = Contact.from_dict(raw)
    contact.first_name = "Updated"

    payload = contact.to_dict()

    assert payload["id"] == 42
    assert payload["name"] == "Original Contact"
    assert payload["first_name"] == "Updated"
    assert payload["last_name"] == "Contact"
    assert payload["tags"] == [{"id": 3, "name": "promo"}]
    assert payload["custom_fields_values"] == [
        {"field_id": 101, "values": [{"value": "hello"}]}
    ]
    assert "_embedded" not in payload


def test_list_all_autopagination(client: AmoCRM) -> None:
    page1_items = [{"id": i, "first_name": f"Name{i}"} for i in range(1, 51)]
    page2_items = [{"id": i, "first_name": f"Name{i}"} for i in range(51, 56)]
    mock_resp1 = _mock_response({"_embedded": {"contacts": page1_items}})
    mock_resp2 = _mock_response({"_embedded": {"contacts": page2_items}})
    with patch.object(
        client._session, "request", side_effect=[mock_resp1, mock_resp2]
    ) as mock_req:
        result = list(client.contacts.list())

    assert mock_req.call_count == 2
    assert len(result) == 55
    assert all(isinstance(r, Contact) for r in result)


def test_list_single_page_explicit(client: AmoCRM) -> None:
    api_response = {"_embedded": {"contacts": [{"id": 1, "first_name": "John"}]}}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.contacts.list(page=3, limit=25)

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/contacts",
        params={"limit": 25, "page": 3},
    )
    assert isinstance(result, list)
    assert len(result) == 1


def test_list_empty_result(client: AmoCRM) -> None:
    mock_resp = _mock_response({"_embedded": {"contacts": []}})
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = list(client.contacts.list())

    mock_req.assert_called_once()
    assert result == []
