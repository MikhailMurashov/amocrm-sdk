from unittest.mock import patch

import pytest

from amocrm import AmoCRM, Task
from amocrm.exceptions import AmoCRMError

from .conftest import mock_response


def test_list_tasks(client: AmoCRM) -> None:
    api_response = {
        "_embedded": {"tasks": [{"id": 1, "text": "Call client", "task_type_id": 1}]}
    }
    mock_resp = mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.tasks.list(page=1, limit=10)

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/tasks",
        params={"page": 1, "limit": 10},
    )
    assert len(result) == 1
    assert isinstance(result[0], Task)
    assert result[0].id == 1
    assert result[0].text == "Call client"
    assert result[0].task_type_id == 1


def test_list_tasks_with_filter(client: AmoCRM) -> None:
    api_response = {"_embedded": {"tasks": []}}
    mock_resp = mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        client.tasks.list(
            page=1, filter={"responsible_user_id": 42}, order={"id": "asc"}
        )

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/tasks",
        params={"filter[responsible_user_id]": 42, "order[id]": "asc", "page": 1},
    )


def test_get_task(client: AmoCRM) -> None:
    api_response = {"id": 5, "text": "Send docs", "complete_till": 1700000000}
    mock_resp = mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.tasks.get(5)

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/tasks/5",
        params={},
    )
    assert isinstance(result, Task)
    assert result.id == 5
    assert result.text == "Send docs"
    assert result.complete_till == 1700000000


def test_create_tasks(client: AmoCRM) -> None:
    new_task = Task(text="Follow up", task_type_id=1, complete_till=1700000000)
    api_response = {
        "_embedded": {"tasks": [{"id": 20, "text": "Follow up", "task_type_id": 1}]}
    }
    mock_resp = mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.tasks.create([new_task])

    mock_req.assert_called_once_with(
        "POST",
        "https://test.amocrm.ru/api/v4/tasks",
        json=[new_task.to_dict()],
    )
    assert len(result) == 1
    assert isinstance(result[0], Task)
    assert result[0].id == 20
    assert result[0].text == "Follow up"


def test_update_tasks(client: AmoCRM) -> None:
    updated_task = Task(id=20, text="Updated text")
    api_response = {"_embedded": {"tasks": [{"id": 20, "text": "Updated text"}]}}
    mock_resp = mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.tasks.update([updated_task])

    mock_req.assert_called_once_with(
        "PATCH",
        "https://test.amocrm.ru/api/v4/tasks",
        json=[updated_task.to_dict()],
    )
    assert len(result) == 1
    assert isinstance(result[0], Task)
    assert result[0].id == 20
    assert result[0].text == "Updated text"


def test_update_one_task(client: AmoCRM) -> None:
    data = Task(id=20, text="Done", is_completed=True)
    api_response = {"id": 20, "text": "Done", "is_completed": True}
    mock_resp = mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.tasks.update_one(data)

    mock_req.assert_called_once_with(
        "PATCH",
        "https://test.amocrm.ru/api/v4/tasks/20",
        json=data.to_dict(),
    )
    assert isinstance(result, Task)
    assert result.id == 20
    assert result.is_completed is True


def test_roundtrip_task() -> None:
    raw = {
        "id": 42,
        "text": "Call client",
        "complete_till": 1700000000,
        "task_type_id": 1,
        "responsible_user_id": 7,
        "is_completed": False,
        "entity_id": 100,
        "entity_type": "leads",
        "result": {"text": "Called successfully"},
    }
    task = Task.from_dict(raw)
    task.text = "Call client again"

    payload = task.to_dict()

    assert payload["id"] == 42
    assert payload["text"] == "Call client again"
    assert payload["complete_till"] == 1700000000
    assert payload["task_type_id"] == 1
    assert payload["responsible_user_id"] == 7
    assert payload["is_completed"] is False
    assert payload["entity_id"] == 100
    assert payload["entity_type"] == "leads"
    assert payload["result"] == {"text": "Called successfully"}
    # None-поля не включаются
    assert "duration" not in payload
    assert "group_id" not in payload


def test_list_all_autopagination(client: AmoCRM) -> None:
    page1_items = [
        {"id": i, "text": f"Task {i}", "task_type_id": 1} for i in range(1, 51)
    ]
    page2_items = [
        {"id": i, "text": f"Task {i}", "task_type_id": 1} for i in range(51, 54)
    ]
    mock_resp1 = mock_response({"_embedded": {"tasks": page1_items}})
    mock_resp2 = mock_response({"_embedded": {"tasks": page2_items}})
    with patch.object(
        client._session, "request", side_effect=[mock_resp1, mock_resp2]
    ) as mock_req:
        result = list(client.tasks.list())

    assert mock_req.call_count == 2
    assert len(result) == 53
    assert all(isinstance(r, Task) for r in result)


def test_list_single_page_explicit_tasks(client: AmoCRM) -> None:
    api_response = {
        "_embedded": {"tasks": [{"id": 7, "text": "Follow up", "task_type_id": 2}]}
    }
    mock_resp = mock_response(api_response)
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = client.tasks.list(page=1, limit=5)

    mock_req.assert_called_once_with(
        "GET",
        "https://test.amocrm.ru/api/v4/tasks",
        params={"limit": 5, "page": 1},
    )
    assert isinstance(result, list)
    assert len(result) == 1


def test_list_empty_result_tasks(client: AmoCRM) -> None:
    mock_resp = mock_response({"_embedded": {"tasks": []}})
    with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
        result = list(client.tasks.list())

    mock_req.assert_called_once()
    assert result == []


def test_create_raises_on_too_many_tasks(client: AmoCRM) -> None:
    tasks = [Task(text=f"T{i}") for i in range(51)]
    with pytest.raises(AmoCRMError, match="at most 50"):
        client.tasks.create(tasks)


def test_update_raises_on_too_many_tasks(client: AmoCRM) -> None:
    tasks = [Task(id=i) for i in range(51)]
    with pytest.raises(AmoCRMError, match="at most 50"):
        client.tasks.update(tasks)
