from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import amocrm.manager as manager_module
from amocrm import AmoCRM, OAuthConfig
from amocrm.auth import DjangoTokenStorage
from amocrm.exceptions import AmoCRMAPIError, AmoCRMTokenRefreshError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_oauth(storage: MagicMock | None = None) -> OAuthConfig:
    if storage is None:
        storage = MagicMock()
        storage.load.return_value = ("access_token", "refresh_token")
    return OAuthConfig(
        client_id="client_id",
        client_secret="client_secret",
        redirect_uri="https://example.com/callback",
        storage=storage,
    )


def _make_client(subdomain: str = "test", storage: MagicMock | None = None) -> AmoCRM:
    return AmoCRM(subdomain=subdomain, oauth=_make_oauth(storage))


def _mock_response(json_data: dict, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.ok = status_code < 400
    mock.content = b"data"
    mock.json.return_value = json_data
    mock.text = str(json_data)
    return mock


# ---------------------------------------------------------------------------
# _request retry logic
# ---------------------------------------------------------------------------


def test_request_retries_on_401() -> None:
    """401 → refresh → retry → success."""
    client = _make_client()

    ok_response = _mock_response({"id": 1})
    refresh_resp = _mock_response(
        {"access_token": "new_access", "refresh_token": "new_refresh"}
    )

    with (
        patch.object(client._session, "request") as mock_req,
        patch("amocrm.client.requests.post", return_value=refresh_resp),
    ):

        unauth = MagicMock(status_code=401, ok=False, content=b"", text="Unauthorized")
        mock_req.side_effect = [unauth, ok_response]

        result = client._request("GET", "/api/v4/leads")

    assert result == {"id": 1}
    assert mock_req.call_count == 2


def test_request_raises_after_failed_refresh() -> None:
    """401 → refresh succeeds → second request still 401 → AmoCRMAPIError."""
    client = _make_client()

    refresh_resp = _mock_response(
        {"access_token": "new_access", "refresh_token": "new_refresh"}
    )
    unauth = MagicMock(status_code=401, ok=False, content=b"err", text="Unauthorized")

    with (
        patch.object(client._session, "request", return_value=unauth),
        patch("amocrm.client.requests.post", return_value=refresh_resp),
    ):

        with pytest.raises(AmoCRMAPIError) as exc_info:
            client._request("GET", "/api/v4/leads")

    assert exc_info.value.status_code == 401


def test_refresh_updates_session_header() -> None:
    client = _make_client()

    refresh_resp = _mock_response(
        {"access_token": "updated_access", "refresh_token": "updated_refresh"}
    )

    with patch("amocrm.client.requests.post", return_value=refresh_resp):
        client._refresh_tokens()

    assert client._session.headers["Authorization"] == "Bearer updated_access"


def test_refresh_calls_storage_save() -> None:
    storage = MagicMock()
    storage.load.return_value = ("old_access", "old_refresh")
    client = _make_client(storage=storage)

    refresh_resp = _mock_response(
        {"access_token": "new_access", "refresh_token": "new_refresh"}
    )

    with patch("amocrm.client.requests.post", return_value=refresh_resp):
        client._refresh_tokens()

    storage.save.assert_called_once_with("new_access", "new_refresh")


def test_token_refresh_error_on_bad_response() -> None:
    client = _make_client()

    bad_resp = MagicMock(status_code=400, ok=False, text="Bad request")

    with patch("amocrm.client.requests.post", return_value=bad_resp):
        with pytest.raises(AmoCRMTokenRefreshError):
            client._refresh_tokens()


# ---------------------------------------------------------------------------
# from_code
# ---------------------------------------------------------------------------


def test_from_code_saves_and_creates_client() -> None:
    storage = MagicMock()
    oauth = _make_oauth(storage)

    code_resp = _mock_response(
        {"access_token": "code_access", "refresh_token": "code_refresh"}
    )
    # After save, load must return the new tokens for the client constructor
    storage.load.return_value = ("code_access", "code_refresh")

    with patch("amocrm.client.requests.post", return_value=code_resp):
        client = AmoCRM.from_code(subdomain="test", code="auth_code", oauth=oauth)

    storage.save.assert_called_once_with("code_access", "code_refresh")
    assert isinstance(client, AmoCRM)
    assert client._session.headers["Authorization"] == "Bearer code_access"


# ---------------------------------------------------------------------------
# DjangoTokenStorage
# ---------------------------------------------------------------------------


def test_django_token_storage_save() -> None:
    instance = MagicMock()
    storage = DjangoTokenStorage(instance)

    storage.save("dj_access", "dj_refresh")

    assert instance.access_token == "dj_access"
    assert instance.refresh_token == "dj_refresh"
    instance.save.assert_called_once()


def test_django_token_storage_load() -> None:
    instance = MagicMock()
    instance.access_token = "dj_acc"
    instance.refresh_token = "dj_ref"
    storage = DjangoTokenStorage(instance)

    result = storage.load()

    assert result == ("dj_acc", "dj_ref")


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_manager() -> None:
    """Reset global client before/after each test."""
    manager_module._client = None
    yield
    manager_module._client = None


def test_manager_get_client() -> None:
    from amocrm.manager import get_client

    storage = MagicMock()
    storage.load.return_value = ("mgr_access", "mgr_refresh")
    oauth = _make_oauth(storage)

    client = get_client(subdomain="mycompany", oauth=oauth)

    assert isinstance(client, AmoCRM)
    assert client._session.headers["Authorization"] == "Bearer mgr_access"


def test_manager_get_client_returns_same_instance() -> None:
    from amocrm.manager import get_client

    storage = MagicMock()
    storage.load.return_value = ("tok", "ref")
    oauth = _make_oauth(storage)

    c1 = get_client(subdomain="test", oauth=oauth)
    c2 = get_client(subdomain="test", oauth=oauth)
    assert c1 is c2


def test_manager_exchange_code() -> None:
    from amocrm.manager import exchange_code, get_client

    storage = MagicMock()
    storage.load.return_value = ("exchanged_access", "exchanged_refresh")
    oauth = _make_oauth(storage)

    code_resp = _mock_response(
        {"access_token": "exchanged_access", "refresh_token": "exchanged_refresh"}
    )
    with patch("amocrm.client.requests.post", return_value=code_resp):
        exchange_code(subdomain="test", code="some_auth_code", oauth=oauth)

    client = get_client(subdomain="test", oauth=oauth)
    assert isinstance(client, AmoCRM)
    storage.save.assert_called_once_with("exchanged_access", "exchanged_refresh")
