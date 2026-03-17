from unittest.mock import MagicMock, patch

import pytest

from amocrm import AmoCRM, Company
from amocrm.exceptions import AmoCRMAPIError, AmoCRMError

from .conftest import mock_response


def test_list_companies(client: AmoCRM) -> None:
    api_response = {"_embedded": {"companies": [{"id": 1, "name": "Acme Corp"}]}}
    mock_resp = mock_response(api_response)
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
    mock_resp = mock_response(api_response)
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
    mock_resp = mock_response(api_response)
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
    mock_resp = mock_response(api_response)
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
    data = Company(id=5, name="Patched Corp")
    api_response = {"id": 5, "name": "Patched Corp"}
    mock_resp = mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.companies.update_one(data)

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
                list(client.companies.list())

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


def test_list_all_autopagination(client: AmoCRM) -> None:
    page1_items = [{"id": i, "name": f"Company {i}"} for i in range(1, 51)]
    page2_items = [{"id": i, "name": f"Company {i}"} for i in range(51, 58)]
    mock_resp1 = mock_response({"_embedded": {"companies": page1_items}})
    mock_resp2 = mock_response({"_embedded": {"companies": page2_items}})
    with patch.object(
        client._session, "request", side_effect=[mock_resp1, mock_resp2]
    ) as mock_req:
        result = list(client.companies.list())

    assert mock_req.call_count == 2
    assert len(result) == 57
    assert all(isinstance(r, Company) for r in result)


def test_list_single_page_explicit(client: AmoCRM) -> None:
    api_response = {"_embedded": {"companies": [{"id": 10, "name": "Acme"}]}}
    mock_resp = mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.companies.list(page=2, limit=20)

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/companies",
        params={"limit": 20, "page": 2},
    )
    assert isinstance(result, list)
    assert len(result) == 1


def test_list_empty_result(client: AmoCRM) -> None:
    mock_resp = mock_response({"_embedded": {"companies": []}})
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = list(client.companies.list())

    mock_req.assert_called_once()
    assert result == []


def test_create_raises_on_too_many_companies(client: AmoCRM) -> None:
    companies = [Company(name=f"C{i}") for i in range(51)]
    with pytest.raises(AmoCRMError, match="at most 50"):
        client.companies.create(companies)


def test_update_raises_on_too_many_companies(client: AmoCRM) -> None:
    companies = [Company(id=i) for i in range(51)]
    with pytest.raises(AmoCRMError, match="at most 50"):
        client.companies.update(companies)
