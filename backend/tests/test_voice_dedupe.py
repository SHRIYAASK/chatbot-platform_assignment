import asyncio

from app.core.database import SessionLocal
from app.modules.chat.services.chat_service import ChatService
from app.modules.chat.services.conversation_service import ConversationService

def _create_project(client, headers):
    response = client.post(
        "/projects",
        json={"title": "Voice dedupe", "description": "Voice dedupe test bot."},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_conversation(client, headers, project_id):
    return client.post(
        f"/projects/{project_id}/conversations",
        json={"title": "Voice chat"},
        headers=headers,
    ).json()["id"]


def test_recent_duplicate_voice_user(client, auth_headers):
    project_id = _create_project(client, auth_headers)
    conversation_id = _create_conversation(client, auth_headers, project_id)

    me = client.get("/auth/me", headers=auth_headers).json()
    user_id = me["id"]

    with SessionLocal() as db:
        ConversationService.save_message(
            db,
            project_id=project_id,
            conversation_id=conversation_id,
            role="user",
            content="இந்த டாக்குமெண்டில் என்ன இருக்கு?",
        )
        db.commit()

    assert ChatService._recent_duplicate_voice_user(
        conversation_id,
        "இந்த டாக்குமெண்டில் என்ன இருக்கு?",
    )
    assert not ChatService._recent_duplicate_voice_user(
        conversation_id,
        "வேறு கேள்வி",
    )


def test_stream_message_skips_duplicate_voice_turn(client, auth_headers, monkeypatch):
    project_id = _create_project(client, auth_headers)
    conversation_id = _create_conversation(client, auth_headers, project_id)

    me = client.get("/auth/me", headers=auth_headers).json()
    user_id = me["id"]
    async def fake_stream_reply(*args, **kwargs):
        yield "reply"
        if False:
            yield

    monkeypatch.setattr(
        "app.modules.chat.services.chat_service.LLMService.stream_reply",
        fake_stream_reply,
    )

    async def run():
        first = [
            chunk
            async for chunk in ChatService.stream_message(
                user_id=user_id,
                project_id=project_id,
                conversation_id=conversation_id,
                content="same voice turn",
                response_language="ta-IN",
            )
        ]
        second = [
            chunk
            async for chunk in ChatService.stream_message(
                user_id=user_id,
                project_id=project_id,
                conversation_id=conversation_id,
                content="same voice turn",
                response_language="ta-IN",
            )
        ]
        return first, second

    first, second = asyncio.run(run())
    assert first == ["reply"]
    assert second == []

    messages = client.get(
        f"/projects/{project_id}/conversations/{conversation_id}/messages",
        headers=auth_headers,
    ).json()["messages"]
    user_rows = [m for m in messages if m["role"] == "user" and m["content"] == "same voice turn"]
    assert len(user_rows) == 1
