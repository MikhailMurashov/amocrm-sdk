from unittest.mock import MagicMock, patch

import pytest

from amocrm import AmoCRM, OAuthConfig
from amocrm.models.pipelines import Pipeline, PipelineStatus, StatusDescription


@pytest.fixture
def client() -> AmoCRM:
    storage = MagicMock()
    storage.load.return_value = ("token123", "refresh123")
    oauth = OAuthConfig(
        client_id="id", client_secret="secret",
        redirect_uri="https://example.com/callback", storage=storage,
    )
    return AmoCRM(subdomain="test", oauth=oauth)


def _mock_response(json_data: dict, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.ok = status_code < 400
    mock.content = b"data" if status_code != 204 else b""
    mock.json.return_value = json_data
    mock.text = str(json_data)
    return mock


# ------------------------------------------------------------------ #
# PipelinesResource                                                    #
# ------------------------------------------------------------------ #


def test_list_pipelines(client: AmoCRM) -> None:
    api_response = {
        "_embedded": {
            "pipelines": [
                {"id": 1, "name": "Main", "sort": 10, "is_main": True},
            ]
        }
    }
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.pipelines.list()

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/leads/pipelines",
    )
    assert len(result) == 1
    assert isinstance(result[0], Pipeline)
    assert result[0].id == 1
    assert result[0].name == "Main"
    assert result[0].is_main is True


def test_get_pipeline(client: AmoCRM) -> None:
    api_response = {"id": 1, "name": "Main", "sort": 10, "account_id": 999}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.pipelines.get(1)

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/leads/pipelines/1",
    )
    assert isinstance(result, Pipeline)
    assert result.id == 1
    assert result.account_id == 999


def test_create_pipelines(client: AmoCRM) -> None:
    new_pipeline = Pipeline(name="New", sort=20)
    api_response = {
        "_embedded": {
            "pipelines": [{"id": 5, "name": "New", "sort": 20}]
        }
    }
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.pipelines.create([new_pipeline])

    mock_req.assert_called_once_with(
        "POST",
        "https://test.amocrm.ru/api/v4/leads/pipelines",
        json=[new_pipeline.to_dict()],
    )
    assert len(result) == 1
    assert isinstance(result[0], Pipeline)
    assert result[0].id == 5
    assert result[0].name == "New"


def test_update_pipeline(client: AmoCRM) -> None:
    data = Pipeline(name="Updated", sort=30)
    api_response = {"id": 1, "name": "Updated", "sort": 30}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.pipelines.update(1, data)

    mock_req.assert_called_once_with(
        "PATCH",
        "https://test.amocrm.ru/api/v4/leads/pipelines/1",
        json=data.to_dict(),
    )
    assert isinstance(result, Pipeline)
    assert result.name == "Updated"


def test_delete_pipeline(client: AmoCRM) -> None:
    mock_resp = _mock_response({}, status_code=204)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.pipelines.delete(1)

    mock_req.assert_called_once_with(
        "DELETE",
        "https://test.amocrm.ru/api/v4/leads/pipelines/1",
    )
    assert result is None


def test_list_statuses(client: AmoCRM) -> None:
    api_response = {
        "_embedded": {
            "statuses": [{"id": 10, "name": "New", "pipeline_id": 1}]
        }
    }
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.pipelines.list_statuses(1)

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/leads/pipelines/1/statuses",
        params={},
    )
    assert len(result) == 1
    assert isinstance(result[0], PipelineStatus)
    assert result[0].id == 10
    assert result[0].name == "New"


def test_list_statuses_with_descriptions(client: AmoCRM) -> None:
    api_response = {
        "_embedded": {
            "statuses": [{"id": 10, "name": "New", "pipeline_id": 1}]
        }
    }
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.pipelines.list_statuses(1, with_descriptions=True)

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/leads/pipelines/1/statuses",
        params={"with": "descriptions"},
    )
    assert len(result) == 1


def test_get_status(client: AmoCRM) -> None:
    api_response = {"id": 5, "name": "Won", "pipeline_id": 1, "color": "#00ff00"}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.pipelines.get_status(1, 5)

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/leads/pipelines/1/statuses/5",
        params={},
    )
    assert isinstance(result, PipelineStatus)
    assert result.id == 5
    assert result.color == "#00ff00"


def test_create_statuses(client: AmoCRM) -> None:
    new_status = PipelineStatus(name="In Progress", sort=20, pipeline_id=1)
    api_response = {
        "_embedded": {
            "statuses": [{"id": 20, "name": "In Progress", "pipeline_id": 1}]
        }
    }
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.pipelines.create_statuses(1, [new_status])

    mock_req.assert_called_once_with(
        "POST",
        "https://test.amocrm.ru/api/v4/leads/pipelines/1/statuses",
        json=[new_status.to_dict()],
    )
    assert len(result) == 1
    assert isinstance(result[0], PipelineStatus)
    assert result[0].id == 20


def test_update_status(client: AmoCRM) -> None:
    data = PipelineStatus(name="Done", sort=100)
    api_response = {"id": 5, "name": "Done", "pipeline_id": 1}
    mock_resp = _mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.pipelines.update_status(1, 5, data)

    mock_req.assert_called_once_with(
        "PATCH",
        "https://test.amocrm.ru/api/v4/leads/pipelines/1/statuses/5",
        json=data.to_dict(),
    )
    assert isinstance(result, PipelineStatus)
    assert result.name == "Done"


def test_delete_status(client: AmoCRM) -> None:
    mock_resp = _mock_response({}, status_code=204)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.pipelines.delete_status(1, 5)

    mock_req.assert_called_once_with(
        "DELETE",
        "https://test.amocrm.ru/api/v4/leads/pipelines/1/statuses/5",
    )
    assert result is None


# ------------------------------------------------------------------ #
# Pipeline model                                                       #
# ------------------------------------------------------------------ #


def test_pipeline_from_dict_with_statuses_as_dict() -> None:
    raw = {
        "id": 1,
        "name": "Main",
        "sort": 10,
        "is_main": True,
        "_embedded": {
            "statuses": {
                "142": {"id": 142, "name": "New lead", "pipeline_id": 1},
                "143": {"id": 143, "name": "In work", "pipeline_id": 1},
            }
        },
    }
    pipeline = Pipeline.from_dict(raw)
    assert pipeline.id == 1
    assert pipeline.is_main is True
    assert pipeline.statuses is not None
    assert len(pipeline.statuses) == 2
    assert all(isinstance(s, PipelineStatus) for s in pipeline.statuses)


def test_pipeline_from_dict_with_statuses_as_list() -> None:
    raw = {
        "id": 2,
        "name": "Secondary",
        "_embedded": {
            "statuses": [
                {"id": 10, "name": "A", "pipeline_id": 2},
                {"id": 11, "name": "B", "pipeline_id": 2},
            ]
        },
    }
    pipeline = Pipeline.from_dict(raw)
    assert pipeline.statuses is not None
    assert len(pipeline.statuses) == 2
    assert pipeline.statuses[0].id == 10
    assert pipeline.statuses[1].name == "B"


def test_pipeline_from_dict_no_statuses() -> None:
    raw = {"id": 3, "name": "Empty", "sort": 1}
    pipeline = Pipeline.from_dict(raw)
    assert pipeline.id == 3
    assert pipeline.statuses is None


def test_pipeline_to_dict_excludes_none() -> None:
    pipeline = Pipeline(name="Test", sort=5)
    result = pipeline.to_dict()
    assert result == {"name": "Test", "sort": 5}
    assert "id" not in result
    assert "is_main" not in result
    assert "_embedded" not in result


def test_pipeline_to_dict_with_statuses() -> None:
    statuses = [PipelineStatus(id=10, name="New", sort=100)]
    pipeline = Pipeline(id=1, name="Main", statuses=statuses)
    result = pipeline.to_dict()
    assert result["id"] == 1
    assert result["name"] == "Main"
    assert "_embedded" in result
    assert result["_embedded"]["statuses"] == [{"id": 10, "name": "New", "sort": 100}]


# ------------------------------------------------------------------ #
# PipelineStatus model                                                 #
# ------------------------------------------------------------------ #


def test_pipeline_status_from_dict_with_descriptions() -> None:
    raw = {
        "id": 10,
        "name": "New",
        "pipeline_id": 1,
        "descriptions": [
            {"id": 1, "level": "newbie", "text": "Just started"},
            {"id": 2, "level": "master", "text": "Experienced"},
        ],
    }
    status = PipelineStatus.from_dict(raw)
    assert status.id == 10
    assert status.descriptions is not None
    assert len(status.descriptions) == 2
    assert all(isinstance(d, StatusDescription) for d in status.descriptions)
    assert status.descriptions[0].level == "newbie"
    assert status.descriptions[1].text == "Experienced"


def test_pipeline_status_from_dict_no_descriptions() -> None:
    raw = {"id": 10, "name": "New", "pipeline_id": 1}
    status = PipelineStatus.from_dict(raw)
    assert status.descriptions is None


def test_pipeline_status_to_dict() -> None:
    status = PipelineStatus(name="In Work", sort=20, color="#ff0000")
    result = status.to_dict()
    assert result == {"name": "In Work", "sort": 20, "color": "#ff0000"}
    assert "id" not in result
    assert "descriptions" not in result


# ------------------------------------------------------------------ #
# StatusDescription model                                              #
# ------------------------------------------------------------------ #


def test_status_description_roundtrip() -> None:
    raw = {"id": 7, "level": "candidate", "text": "Middle stage"}
    desc = StatusDescription.from_dict(raw)
    assert desc.id == 7
    assert desc.level == "candidate"
    assert desc.text == "Middle stage"

    result = desc.to_dict()
    assert result == {"id": 7, "level": "candidate", "text": "Middle stage"}
