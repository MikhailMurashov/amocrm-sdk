from unittest.mock import MagicMock, patch

import pytest

from amocrm import AmoCRM, Company, OAuthConfig
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


def test_list_companies(client: AmoCRM) -> None:
    api_response = {"_embedded": {"companies": [{"id": 1, "name": "Acme Corp"}]}}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.companies.list(page=1, limit=10, with_=["leads"])

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/companies",
        params={"page": 1, "limit": 10, "with": "leads"},
    )
    assert len(result) == 1
    assert isinstance(result[0], Company)
    assert result[0].id == 1
    assert result[0].name == "Acme Corp"


def test_get_company(client: AmoCRM) -> None:
    api_response = {"id": 42, "name": "Big Corp"}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.companies.get(42)

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/companies/42",
        params={},
    )
    assert isinstance(result, Company)
    assert result.id == 42
    assert result.name == "Big Corp"


def test_create_companies(client: AmoCRM) -> None:
    new_company = Company(name="New Corp")
    api_response = {"_embedded": {"companies": [{"id": 10, "name": "New Corp"}]}}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.companies.create([new_company])

    mock_req.assert_called_once_with(
        "POST",
        "https://test.amocrm.ru/api/v4/companies",
        json=[new_company.to_dict()],
    )
    assert len(result) == 1
    assert isinstance(result[0], Company)
    assert result[0].id == 10
    assert result[0].name == "New Corp"


def test_update_companies(client: AmoCRM) -> None:
    updated_company = Company(id=10, name="Updated Corp")
    api_response = {"_embedded": {"companies": [{"id": 10, "name": "Updated Corp"}]}}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.companies.update([updated_company])

    mock_req.assert_called_once_with(
        "PATCH",
        "https://test.amocrm.ru/api/v4/companies",
        json=[updated_company.to_dict()],
    )
    assert len(result) == 1
    assert isinstance(result[0], Company)
    assert result[0].id == 10
    assert result[0].name == "Updated Corp"


def test_update_one_company(client: AmoCRM) -> None:
    data = Company(name="Patched Corp")
    api_response = {"id": 5, "name": "Patched Corp"}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.companies.update_one(5, data)

    mock_req.assert_called_once_with(
        "PATCH",
        "https://test.amocrm.ru/api/v4/companies/5",
        json=data.to_dict(),
    )
    assert isinstance(result, Company)
    assert result.id == 5
    assert result.name == "Patched Corp"


def test_api_error_raises(client: AmoCRM) -> None:
    error_response = MagicMock()
    error_response.status_code = 401
    error_response.ok = False
    error_response.text = "Unauthorized"

    with patch.object(client, "_refresh_tokens"):
        with patch.object(client._session, "request", return_value=error_response):
            with pytest.raises(AmoCRMAPIError) as exc_info:
                client.companies.list()

    assert exc_info.value.status_code == 401
    assert "Unauthorized" in str(exc_info.value)


def test_company_to_dict_excludes_none() -> None:
    company = Company(name="Test Corp")
    result = company.to_dict()
    assert result == {"name": "Test Corp"}
    assert "id" not in result
    assert "account_id" not in result


def test_company_from_dict_with_tags() -> None:
    raw = {
        "id": 7,
        "name": "Tagged Corp",
        "_embedded": {"tags": [{"id": 1, "name": "partner"}, {"id": 2, "name": "key"}]},
    }
    company = Company.from_dict(raw)
    assert company.id == 7
    assert company.tags is not None
    assert len(company.tags) == 2
    assert company.tags[0].id == 1
    assert company.tags[0].name == "partner"
    assert company.tags[1].name == "key"


def test_roundtrip_company() -> None:
    raw = {
        "id": 42,
        "name": "Original Corp",
        "_embedded": {"tags": [{"id": 3, "name": "enterprise"}]},
        "custom_fields_values": [{"field_id": 101, "values": [{"value": "hello"}]}],
    }
    company = Company.from_dict(raw)
    company.name = "Updated Corp"

    payload = company.to_dict()

    assert payload["id"] == 42
    assert payload["name"] == "Updated Corp"
    assert payload["tags"] == [{"id": 3, "name": "enterprise"}]
    assert payload["custom_fields_values"] == [
        {"field_id": 101, "values": [{"value": "hello"}]}
    ]
    assert "_embedded" not in payload
