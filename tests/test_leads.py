from unittest.mock import MagicMock, patch

import pytest

from amocrm import AmoCRM, Lead, OAuthConfig
from amocrm.exceptions import AmoCRMAPIError, AmoCRMError
from amocrm.models import Company, Contact


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


def test_list_leads(client: AmoCRM) -> None:
    api_response = {"_embedded": {"leads": [{"id": 1, "name": "Deal 1", "price": 500}]}}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.leads.list(page=1, limit=10, with_=["contacts"])

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/leads",
        params={"page": 1, "limit": 10, "with": "contacts"},
    )
    assert len(result) == 1
    assert isinstance(result[0], Lead)
    assert result[0].id == 1
    assert result[0].name == "Deal 1"
    assert result[0].price == 500


def test_get_lead(client: AmoCRM) -> None:
    api_response = {"id": 42, "name": "Big Deal", "price": 1000}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.leads.get(42)

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/leads/42",
        params={"with": "contacts"},
    )
    assert isinstance(result, Lead)
    assert result.id == 42
    assert result.name == "Big Deal"
    assert result.price == 1000


def test_get_lead_with_empty_with(client: AmoCRM) -> None:
    mock_resp = _mock_response({"id": 42})
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        client.leads.get(42, with_=[])

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/leads/42",
        params={},
    )


def test_create_leads(client: AmoCRM) -> None:
    new_lead = Lead(name="New Deal", price=5000)
    api_response = {
        "_embedded": {"leads": [{"id": 10, "name": "New Deal", "price": 5000}]}
    }
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.leads.create([new_lead])

    mock_req.assert_called_once_with(
        "POST",
        "https://test.amocrm.ru/api/v4/leads",
        json=[new_lead.to_dict()],
    )
    assert len(result) == 1
    assert isinstance(result[0], Lead)
    assert result[0].id == 10
    assert result[0].name == "New Deal"


def test_update_leads(client: AmoCRM) -> None:
    updated_lead = Lead(id=10, price=9000)
    api_response = {"_embedded": {"leads": [{"id": 10, "price": 9000}]}}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.leads.update([updated_lead])

    mock_req.assert_called_once_with(
        "PATCH",
        "https://test.amocrm.ru/api/v4/leads",
        json=[updated_lead.to_dict()],
    )
    assert len(result) == 1
    assert isinstance(result[0], Lead)
    assert result[0].id == 10
    assert result[0].price == 9000


def test_api_error_raises(client: AmoCRM) -> None:
    error_response = MagicMock()
    error_response.status_code = 401
    error_response.ok = False
    error_response.text = "Unauthorized"

    with patch.object(client, "_refresh_tokens"):
        with patch.object(client._session, "request", return_value=error_response):
            with pytest.raises(AmoCRMAPIError) as exc_info:
                client.leads.list()

    assert exc_info.value.status_code == 401
    assert "Unauthorized" in str(exc_info.value)


def test_lead_to_dict_excludes_none() -> None:
    lead = Lead(name="Test", price=1000)
    result = lead.to_dict()
    assert result == {"name": "Test", "price": 1000}
    assert "id" not in result
    assert "status_id" not in result


def test_lead_from_dict_with_tags() -> None:
    raw = {
        "id": 7,
        "name": "Tagged Deal",
        "price": 3000,
        "_embedded": {"tags": [{"id": 1, "name": "vip"}, {"id": 2, "name": "hot"}]},
    }
    lead = Lead.from_dict(raw)
    assert lead.id == 7
    assert lead.tags is not None
    assert len(lead.tags) == 2
    assert lead.tags[0].id == 1
    assert lead.tags[0].name == "vip"
    assert lead.tags[1].name == "hot"


def test_roundtrip_lead() -> None:
    raw = {
        "id": 42,
        "name": "Original Deal",
        "price": 5000,
        "status_id": 10,
        "_embedded": {"tags": [{"id": 3, "name": "promo"}]},
        "custom_fields_values": [{"field_id": 101, "values": [{"value": "hello"}]}],
    }
    lead = Lead.from_dict(raw)
    lead.price = 9000

    payload = lead.to_dict()

    assert payload["id"] == 42
    assert payload["name"] == "Original Deal"
    assert payload["price"] == 9000
    assert payload["status_id"] == 10
    assert payload["tags"] == [{"id": 3, "name": "promo"}]
    assert payload["custom_fields_values"] == [
        {"field_id": 101, "values": [{"value": "hello"}]}
    ]
    # Теги на верхнем уровне payload, не во _embedded
    assert "_embedded" not in payload


def test_lead_from_dict_with_contacts_and_company() -> None:
    raw = {
        "id": 1,
        "_embedded": {
            "contacts": [{"id": 5, "name": "John"}],
            "companies": [{"id": 10, "name": "Acme"}],
        },
    }
    lead = Lead.from_dict(raw)
    assert lead.contacts is not None
    assert len(lead.contacts) == 1
    assert lead.contacts[0].id == 5
    assert lead.contacts[0].name == "John"
    assert lead.company is not None
    assert lead.company.id == 10
    assert lead.company.name == "Acme"


def test_lead_to_dict_with_contacts_and_company() -> None:
    lead = Lead(
        id=1,
        contacts=[Contact(id=5)],
        company=Company(id=10),
    )
    result = lead.to_dict()
    assert result["_embedded"]["contacts"] == [{"id": 5}]
    assert result["_embedded"]["companies"] == [{"id": 10}]


def test_create_complex_with_linked_entities(client: AmoCRM) -> None:
    lead = Lead(name="Deal", contacts=[Contact(id=5)], company=Company(id=10))
    api_response = {"_embedded": {"leads": [{"id": 99, "name": "Deal"}]}}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.leads.create_complex([lead])

    call_kwargs = mock_req.call_args
    body = call_kwargs[1]["json"]
    assert "_embedded" in body[0]
    assert len(result) == 1
    assert result[0].id == 99


def test_create_complex_raises_on_multiple_contacts(client: AmoCRM) -> None:
    lead = Lead(name="Deal", contacts=[Contact(id=1), Contact(id=2)])
    with pytest.raises(AmoCRMError, match="at most 1 contact"):
        client.leads.create_complex([lead])


def test_create_raises_on_too_many_leads(client: AmoCRM) -> None:
    leads = [Lead(name=f"Deal {i}") for i in range(51)]
    with pytest.raises(AmoCRMError, match="at most 50"):
        client.leads.create(leads)


def test_update_raises_on_too_many_leads(client: AmoCRM) -> None:
    leads = [Lead(id=i) for i in range(51)]
    with pytest.raises(AmoCRMError, match="at most 50"):
        client.leads.update(leads)


def test_create_complex_raises_on_too_many_leads(client: AmoCRM) -> None:
    leads = [Lead(name=f"Deal {i}") for i in range(51)]
    with pytest.raises(AmoCRMError, match="at most 50"):
        client.leads.create_complex(leads)
