import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.rate_limit import limiter
from app.modules.authentication.models.user import User
from app.modules.chat.schemas.chat import (
    MessageCreate,
    MessageListResponse,
    MessageResponse,
    SendMessageResponse,
)
from app.modules.chat.services.chat_service import ChatService
from app.modules.chat.services.conversation_service import ConversationService
from app.modules.chat.services.llm_service import LLMServiceError

router = APIRouter(prefix="/projects/{project_id}", tags=["Chat"])


def _resolve_conversation_id(
    db: Session,
    current_user: User,
    project_id: int,
    conversation_id: int | None,
) -> int:
    if conversation_id is not None:
        return ConversationService.get_conversation(
            db,
            current_user,
            project_id,
            conversation_id,
        ).id
    return ConversationService.get_or_create_default_conversation(db, project_id).id


@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
def list_conversation_messages(
    project_id: int,
    conversation_id: int,
    limit: int = Query(20, ge=1, le=100),
    cursor: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    page = ChatService.list_messages_paginated(
        db,
        current_user,
        project_id,
        conversation_id,
        limit=limit,
        cursor=cursor,
    )
    return MessageListResponse(
        messages=[MessageResponse.model_validate(message) for message in page.messages],
        next_cursor=page.next_cursor,
        has_more=page.has_more,
    )


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=SendMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.RATE_LIMIT_CHAT)
async def send_conversation_message(
    request: Request,
    project_id: int,
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ConversationService.get_conversation(db, current_user, project_id, conversation_id)

    try:
        user_message, assistant_message = await ChatService.send_message(
            current_user,
            project_id,
            conversation_id,
            message_data,
        )
    except asyncio.CancelledError:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI service is temporarily unavailable. Please try again.",
        ) from exc
    except LLMServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI service is temporarily unavailable. Please try again.",
        ) from exc

    return SendMessageResponse(
        user_message=MessageResponse.model_validate(user_message),
        assistant_message=MessageResponse.model_validate(assistant_message),
    )


@router.get("/messages", response_model=MessageListResponse)
def list_messages(
    project_id: int,
    conversation_id: int | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    cursor: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resolved_conversation_id = _resolve_conversation_id(
        db,
        current_user,
        project_id,
        conversation_id,
    )
    page = ChatService.list_messages_paginated(
        db,
        current_user,
        project_id,
        resolved_conversation_id,
        limit=limit,
        cursor=cursor,
    )
    return MessageListResponse(
        messages=[MessageResponse.model_validate(message) for message in page.messages],
        next_cursor=page.next_cursor,
        has_more=page.has_more,
    )


@router.post("/messages", response_model=SendMessageResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_CHAT)
async def send_message(
    request: Request,
    project_id: int,
    message_data: MessageCreate,
    conversation_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resolved_conversation_id = _resolve_conversation_id(
        db,
        current_user,
        project_id,
        conversation_id,
    )

    try:
        user_message, assistant_message = await ChatService.send_message(
            current_user,
            project_id,
            resolved_conversation_id,
            message_data,
        )
    except asyncio.CancelledError:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI service is temporarily unavailable. Please try again.",
        ) from exc
    except LLMServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI service is temporarily unavailable. Please try again.",
        ) from exc

    return SendMessageResponse(
        user_message=MessageResponse.model_validate(user_message),
        assistant_message=MessageResponse.model_validate(assistant_message),
    )
