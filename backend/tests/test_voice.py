import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.voice.services.voice_token_service import VoiceTokenService


def _create_project(client, headers, title="Voice Bot"):
    return client.post(
        "/projects",
        json={"title": title, "description": "Voice test bot."},
        headers=headers,
    )


def _create_conversation(client, headers, project_id, title="Voice chat"):
    return client.post(
        f"/projects/{project_id}/conversations",
        json={"title": title},
        headers=headers,
    )


def _voice_token_url(project_id: int, conversation_id: int) -> str:
    return (
        f"/projects/{project_id}/conversations/{conversation_id}/voice-token"
    )


@pytest.fixture()
def livekit_env(monkeypatch):
    monkeypatch.setenv("LIVEKIT_URL", "wss://test.livekit.cloud")
    monkeypatch.setenv("LIVEKIT_API_KEY", "test-api-key")
    monkeypatch.setenv("LIVEKIT_API_SECRET", "test-api-secret")
    from app.core.config import settings

    settings.LIVEKIT_URL = "wss://test.livekit.cloud"
    settings.LIVEKIT_API_KEY = "test-api-key"
    settings.LIVEKIT_API_SECRET = "test-api-secret"


def test_voice_token_requires_auth(client):
    response = client.post(_voice_token_url(1, 1))
    assert response.status_code in (401, 403)


def test_voice_token_not_found(client, auth_headers):
    project_id = _create_project(client, auth_headers).json()["id"]
    response = client.post(
        _voice_token_url(project_id, 99999),
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_voice_token_other_users_project(client, auth_headers):
    project_id = _create_project(client, auth_headers, title="Private Voice Bot").json()["id"]
    conversation_id = _create_conversation(
        client, auth_headers, project_id
    ).json()["id"]

    other_email = "other_voice@example.com"
    password = "Passw0rd!"
    client.post(
        "/auth/register",
        json={
            "name": "Other User",
            "email": other_email,
            "password": password,
            "confirm_password": password,
        },
    )
    other_login = client.post(
        "/auth/login",
        json={"email": other_email, "password": password},
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    response = client.post(
        _voice_token_url(project_id, conversation_id),
        headers=other_headers,
    )
    assert response.status_code in (403, 404)


def test_voice_token_success(client, auth_headers, livekit_env):
    project_id = _create_project(client, auth_headers).json()["id"]
    conversation_id = _create_conversation(
        client, auth_headers, project_id
    ).json()["id"]

    mock_token = MagicMock()
    mock_token.with_identity.return_value = mock_token
    mock_token.with_name.return_value = mock_token
    mock_token.with_metadata.return_value = mock_token
    mock_token.with_grants.return_value = mock_token
    mock_token.with_room_config.return_value = mock_token
    mock_token.to_jwt.return_value = "mock-livekit-jwt"

    mock_lkapi = MagicMock()
    mock_lkapi.agent_dispatch.create_dispatch = AsyncMock()
    mock_lkapi_cm = MagicMock()
    mock_lkapi_cm.__aenter__ = AsyncMock(return_value=mock_lkapi)
    mock_lkapi_cm.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("app.modules.voice.services.voice_token_service.api.AccessToken", return_value=mock_token),
        patch(
            "app.modules.voice.services.voice_token_service.api.LiveKitAPI",
            return_value=mock_lkapi_cm,
        ),
    ):
        response = client.post(
            _voice_token_url(project_id, conversation_id),
            headers=auth_headers,
        )

    assert response.status_code == 200
    mock_lkapi.agent_dispatch.create_dispatch.assert_awaited_once()
    payload = response.json()
    assert payload["livekit_url"] == "wss://test.livekit.cloud"
    assert payload["token"] == "mock-livekit-jwt"
    assert payload["room_name"] == f"conv-{conversation_id}"


def test_voice_token_not_configured(client, auth_headers, monkeypatch):
    monkeypatch.setenv("LIVEKIT_URL", "")
    monkeypatch.setenv("LIVEKIT_API_KEY", "")
    monkeypatch.setenv("LIVEKIT_API_SECRET", "")
    from app.core.config import settings

    settings.LIVEKIT_URL = ""
    settings.LIVEKIT_API_KEY = ""
    settings.LIVEKIT_API_SECRET = ""

    project_id = _create_project(client, auth_headers).json()["id"]
    conversation_id = _create_conversation(
        client, auth_headers, project_id
    ).json()["id"]

    response = client.post(
        _voice_token_url(project_id, conversation_id),
        headers=auth_headers,
    )
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"].lower()
