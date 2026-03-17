from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from amocrm import AmoCRM, OAuthConfig


@pytest.fixture
def mock_oauth() -> OAuthConfig:
    storage = MagicMock()
    storage.load.return_value = ("token123", "refresh123")
    return OAuthConfig(
        client_id="id",
        client_secret="secret",
        redirect_uri="https://example.com/callback",
        storage=storage,
    )


@pytest.fixture
def client(mock_oauth: OAuthConfig) -> AmoCRM:
    return AmoCRM(subdomain="test", oauth=mock_oauth)


def mock_response(json_data: dict, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.ok = status_code < 400
    mock.content = b"data"
    mock.json.return_value = json_data
    mock.text = str(json_data)
    return mock
