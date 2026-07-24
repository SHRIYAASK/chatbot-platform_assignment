import re
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.modules.authentication.models.user import User
from app.modules.chat.models.chat_message import ChatMessage
from app.modules.chat.models.conversation import Conversation
from app.shared.authorization.project_access import get_owned_project_or_403
from app.modules.workspace.models.project import Project
from app.shared.exceptions import ResourceNotFoundError

MAX_HISTORY_MESSAGES = 20
DEFAULT_PAGE_SIZE = 20
DEFAULT_CONVERSATION_TITLE = "General Chat"
NEW_CONVERSATION_TITLE = "New Chat"
AUTO_TITLE_MAX_LENGTH = 60
PLACEHOLDER_TITLES = {DEFAULT_CONVERSATION_TITLE, NEW_CONVERSATION_TITLE, "New chat"}


@dataclass(frozen=True)
class PaginatedMessages:
    messages: list[ChatMessage]
    next_cursor: str | None
    has_more: bool


@dataclass(frozen=True)
class ConversationWithActivity:
    id: int
    project_id: int
    title: str
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime | None


def _normalize_title(title: str | None) -> str:
    cleaned = (title or "").strip()
    return cleaned or NEW_CONVERSATION_TITLE


def _title_from_message(content: str) -> str:
    single_line = re.sub(r"\s+", " ", content.strip())
    if not single_line:
        return NEW_CONVERSATION_TITLE
    if len(single_line) <= AUTO_TITLE_MAX_LENGTH:
        return single_line
    return f"{single_line[: AUTO_TITLE_MAX_LENGTH - 3]}..."


class ConversationService:
    @staticmethod
    def get_or_create_default_conversation(
        db: Session,
        project_id: int,
    ) -> Conversation:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.project_id == project_id)
            .order_by(Conversation.created_at.asc(), Conversation.id.asc())
            .first()
        )
        if conversation is not None:
            return conversation

        conversation = Conversation(
            project_id=project_id,
            title=DEFAULT_CONVERSATION_TITLE,
        )
        db.add(conversation)
        db.flush()
        return conversation

    @staticmethod
    def get_project(
        db: Session,
        current_user: User,
        project_id: int,
    ) -> Project:
        return get_owned_project_or_403(db, project_id, current_user)

    @staticmethod
    def get_conversation(
        db: Session,
        current_user: User,
        project_id: int,
        conversation_id: int,
    ) -> Conversation:
        get_owned_project_or_403(db, project_id, current_user)
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.project_id == project_id,
            )
            .first()
        )
        if conversation is None:
            raise ResourceNotFoundError("Conversation not found.")
        return conversation

    @staticmethod
    def list_conversations(
        db: Session,
        current_user: User,
        project_id: int,
        search: str | None = None,
    ) -> list[ConversationWithActivity]:
        get_owned_project_or_403(db, project_id, current_user)

        last_message_subquery = (
            db.query(
                ChatMessage.conversation_id.label("conversation_id"),
                func.max(ChatMessage.created_at).label("last_message_at"),
            )
            .filter(ChatMessage.project_id == project_id)
            .group_by(ChatMessage.conversation_id)
            .subquery()
        )

        query = (
            db.query(Conversation, last_message_subquery.c.last_message_at)
            .outerjoin(
                last_message_subquery,
                Conversation.id == last_message_subquery.c.conversation_id,
            )
            .filter(Conversation.project_id == project_id)
        )

        if search and search.strip():
            query = query.filter(Conversation.title.ilike(f"%{search.strip()}%"))

        rows = query.order_by(
            desc(Conversation.is_pinned),
            desc(func.coalesce(last_message_subquery.c.last_message_at, Conversation.updated_at)),
            desc(Conversation.id),
        ).all()

        return [
            ConversationWithActivity(
                id=conversation.id,
                project_id=conversation.project_id,
                title=conversation.title,
                is_pinned=conversation.is_pinned,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                last_message_at=last_message_at,
            )
            for conversation, last_message_at in rows
        ]

    @staticmethod
    def create_conversation(
        db: Session,
        current_user: User,
        project_id: int,
        title: str | None = None,
    ) -> Conversation:
        get_owned_project_or_403(db, project_id, current_user)
        conversation = Conversation(
            project_id=project_id,
            title=_normalize_title(title),
        )
        db.add(conversation)
        db.flush()
        return conversation

    @staticmethod
    def update_conversation(
        db: Session,
        current_user: User,
        project_id: int,
        conversation_id: int,
        title: str,
    ) -> ConversationWithActivity:
        conversation = ConversationService.get_conversation(
            db,
            current_user,
            project_id,
            conversation_id,
        )
        conversation.title = title.strip()
        ConversationService._touch_conversation(db, conversation)
        db.flush()

        last_message_at = (
            db.query(func.max(ChatMessage.created_at))
            .filter(
                ChatMessage.project_id == project_id,
                ChatMessage.conversation_id == conversation_id,
            )
            .scalar()
        )

        return ConversationWithActivity(
            id=conversation.id,
            project_id=conversation.project_id,
            title=conversation.title,
            is_pinned=conversation.is_pinned,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            last_message_at=last_message_at,
        )

    @staticmethod
    def delete_conversation(
        db: Session,
        current_user: User,
        project_id: int,
        conversation_id: int,
    ) -> None:
        conversation = ConversationService.get_conversation(
            db,
            current_user,
            project_id,
            conversation_id,
        )
        db.delete(conversation)
        db.flush()

    @staticmethod
    def _touch_conversation(db: Session, conversation: Conversation) -> None:
        conversation.updated_at = datetime.now(timezone.utc)
        db.add(conversation)

    @staticmethod
    def _maybe_auto_title(conversation: Conversation, content: str) -> None:
        if conversation.title in PLACEHOLDER_TITLES:
            conversation.title = _title_from_message(content)

    @staticmethod
    def list_messages(
        db: Session,
        current_user: User,
        project_id: int,
        conversation_id: int,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[ChatMessage]:
        ConversationService.get_conversation(db, current_user, project_id, conversation_id)

        query = db.query(ChatMessage).filter(
            ChatMessage.project_id == project_id,
            ChatMessage.conversation_id == conversation_id,
        )

        if limit is None:
            return query.order_by(
                ChatMessage.created_at.asc(), ChatMessage.id.asc()
            ).all()

        rows = (
            query.order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return list(reversed(rows))

    @staticmethod
    def list_messages_paginated(
        db: Session,
        current_user: User,
        project_id: int,
        conversation_id: int,
        limit: int = DEFAULT_PAGE_SIZE,
        cursor: int | None = None,
    ) -> PaginatedMessages:
        ConversationService.get_conversation(db, current_user, project_id, conversation_id)

        query = db.query(ChatMessage).filter(
            ChatMessage.project_id == project_id,
            ChatMessage.conversation_id == conversation_id,
        )

        if cursor is not None:
            cursor_message = (
                db.query(ChatMessage)
                .filter(
                    ChatMessage.id == cursor,
                    ChatMessage.project_id == project_id,
                    ChatMessage.conversation_id == conversation_id,
                )
                .first()
            )
            if cursor_message is None:
                return PaginatedMessages(messages=[], next_cursor=None, has_more=False)

            query = query.filter(
                (ChatMessage.created_at < cursor_message.created_at)
                | (
                    (ChatMessage.created_at == cursor_message.created_at)
                    & (ChatMessage.id < cursor_message.id)
                )
            )

        rows = (
            query.order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
            .limit(limit + 1)
            .all()
        )

        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]

        messages = list(reversed(rows))
        next_cursor = str(messages[0].id) if has_more and messages else None

        return PaginatedMessages(
            messages=messages,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    @staticmethod
    def save_message(
        db: Session,
        project_id: int,
        conversation_id: int,
        role: str,
        content: str,
        model_used: str | None = None,
        token_count: int | None = None,
        auto_title: bool = False,
    ) -> ChatMessage:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.project_id == project_id,
            )
            .first()
        )
        if conversation is None:
            raise ResourceNotFoundError("Conversation not found.")

        if auto_title and role == "user":
            ConversationService._maybe_auto_title(conversation, content)

        message = ChatMessage(
            project_id=project_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            model_used=model_used,
            token_count=token_count,
        )
        db.add(message)
        ConversationService._touch_conversation(db, conversation)
        db.flush()
        return message

    @staticmethod
    def build_history(messages: list[ChatMessage]) -> list[dict[str, str]]:
        history = [
            {"role": message.role, "content": message.content}
            for message in messages
            if message.role in {"user", "assistant"}
        ]
        if len(history) <= MAX_HISTORY_MESSAGES:
            return history
        return history[-MAX_HISTORY_MESSAGES:]
