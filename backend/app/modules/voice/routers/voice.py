import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.authentication.models.user import User
from app.modules.chat.services.chat_service import ChatService
from app.modules.chat.services.llm_service import LLMServiceError
from app.modules.chat.services.conversation_service import ConversationService
from app.modules.voice.dependencies.service_auth import get_voice_service_context
from app.modules.voice.schemas.voice import VoiceMessageCreate, VoiceTokenResponse
from app.modules.voice.services.service_token import VoiceServiceContext
from app.modules.voice.services.voice_token_service import (
    VoiceAgentDispatchError,
    VoiceNotConfiguredError,
    VoiceTokenService,
)

router = APIRouter(
    prefix="/projects/{project_id}/conversations/{conversation_id}",
    tags=["Voice"],
)


@router.post("/voice-token", response_model=VoiceTokenResponse)
async def create_voice_token(
    project_id: int,
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ConversationService.get_conversation(db, current_user, project_id, conversation_id)

    try:
        livekit_url, token, room_name = await VoiceTokenService.mint_token(
            current_user=current_user,
            project_id=project_id,
            conversation_id=conversation_id,
        )
    except VoiceNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except VoiceAgentDispatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return VoiceTokenResponse(
        livekit_url=livekit_url,
        token=token,
        room_name=room_name,
    )


def _verify_service_route_context(
    project_id: int,
    conversation_id: int,
    service_context: VoiceServiceContext = Depends(get_voice_service_context),
) -> VoiceServiceContext:
    if (
        service_context.project_id != project_id
        or service_context.conversation_id != conversation_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Voice service token does not match this conversation.",
        )
    return service_context


@router.post("/voice/messages/stream")
async def stream_voice_message(
    project_id: int,
    conversation_id: int,
    message_data: VoiceMessageCreate,
    db: Session = Depends(get_db),
    service_context: VoiceServiceContext = Depends(_verify_service_route_context),
):
    user = db.query(User).filter(User.id == service_context.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Voice service user not found.",
        )

    ConversationService.get_conversation(
        db, user, project_id, conversation_id
    )

    async def event_stream():
        try:
            async for chunk in ChatService.stream_message(
                user_id=service_context.user_id,
                project_id=project_id,
                conversation_id=conversation_id,
                content=message_data.content,
            ):
                yield f"data: {json.dumps({'delta': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except LLMServiceError as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
