from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.authentication.models.user import User
from app.modules.chat.schemas.conversation import (
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdate,
)
from app.modules.chat.services.conversation_service import ConversationService

router = APIRouter(prefix="/projects/{project_id}/conversations", tags=["Conversations"])


def _build_response(conversation) -> ConversationResponse:
    if hasattr(conversation, "last_message_at"):
        return ConversationResponse(
            id=conversation.id,
            project_id=conversation.project_id,
            title=conversation.title,
            is_pinned=conversation.is_pinned,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            last_message_at=conversation.last_message_at,
        )

    return ConversationResponse(
        id=conversation.id,
        project_id=conversation.project_id,
        title=conversation.title,
        is_pinned=conversation.is_pinned,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        last_message_at=None,
    )


@router.get("", response_model=ConversationListResponse)
def list_conversations(
    project_id: int,
    search: str | None = Query(None, max_length=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversations = ConversationService.list_conversations(
        db,
        current_user,
        project_id,
        search=search,
    )
    return ConversationListResponse(
        conversations=[_build_response(conversation) for conversation in conversations]
    )


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    project_id: int,
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = ConversationService.create_conversation(
        db,
        current_user,
        project_id,
        title=payload.title,
    )
    db.commit()
    db.refresh(conversation)
    return _build_response(conversation)


@router.patch("/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    project_id: int,
    conversation_id: int,
    payload: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = ConversationService.update_conversation(
        db,
        current_user,
        project_id,
        conversation_id,
        title=payload.title,
    )
    db.commit()
    return _build_response(conversation)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    project_id: int,
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ConversationService.delete_conversation(
        db,
        current_user,
        project_id,
        conversation_id,
    )
    db.commit()
