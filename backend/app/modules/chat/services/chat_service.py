import asyncio
import logging
from dataclasses import dataclass

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.db_executor import run_sync_db
from app.modules.authentication.models.user import User
from app.modules.chat.models.chat_message import ChatMessage
from app.modules.chat.schemas.chat import MessageCreate
from app.modules.chat.services.conversation_service import (
    MAX_HISTORY_MESSAGES,
    ConversationService,
    PaginatedMessages,
)
from app.modules.chat.services.llm_service import LLMService, LLMServiceError
from app.shared.llm.message_builder import build_chat_messages
from app.modules.chat.services.retrieval_service import RetrievalService
from app.modules.workspace.model_resolver import resolve_project_models
from app.shared.guardrails.moderation.service import ModerationService
from app.shared.rag.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


@dataclass
class PreparedChatRequest:
    user_message: ChatMessage
    llm_messages: list[dict[str, str]]
    primary_model: str
    fallback_model: str
    conversation_id: int


class ChatService:
    @staticmethod
    def list_messages_paginated(
        db: Session,
        current_user: User,
        project_id: int,
        conversation_id: int,
        limit: int = 20,
        cursor: int | None = None,
    ) -> PaginatedMessages:
        return ConversationService.list_messages_paginated(
            db,
            current_user,
            project_id,
            conversation_id,
            limit=limit,
            cursor=cursor,
        )

    @staticmethod
    def list_messages(
        db: Session,
        current_user: User,
        project_id: int,
        conversation_id: int,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[ChatMessage]:
        return ConversationService.list_messages(
            db,
            current_user,
            project_id,
            conversation_id,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def _prepare_send(
        user_id: int,
        project_id: int,
        conversation_id: int,
        content: str,
    ) -> PreparedChatRequest:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user is None:
                raise ValueError("User not found.")

            project = ConversationService.get_project(db, user, project_id)
            ConversationService.get_conversation(db, user, project_id, conversation_id)
            existing_messages = ConversationService.list_messages(
                db,
                user,
                project_id,
                conversation_id,
                limit=MAX_HISTORY_MESSAGES,
            )
            history = ConversationService.build_history(existing_messages)
            retrieval_service = RetrievalService(db, get_embedding_service())
            rag_context = retrieval_service.retrieve_context(project_id, content)
            llm_messages = build_chat_messages(
                project.description,
                history,
                content,
                rag_context=rag_context,
            )

            user_message = ConversationService.save_message(
                db,
                project_id=project_id,
                conversation_id=conversation_id,
                role="user",
                content=content,
                auto_title=True,
            )
            db.commit()
            db.refresh(user_message)

            primary_model, fallback_model = resolve_project_models(
                project.primary_model,
                project.fallback_model,
            )

            return PreparedChatRequest(
                user_message=user_message,
                llm_messages=llm_messages,
                primary_model=primary_model,
                fallback_model=fallback_model,
                conversation_id=conversation_id,
            )
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _save_assistant_message(
        project_id: int,
        conversation_id: int,
        content: str,
        model_used: str | None = None,
        token_count: int | None = None,
    ) -> ChatMessage:
        db = SessionLocal()
        try:
            assistant_message = ConversationService.save_message(
                db,
                project_id=project_id,
                conversation_id=conversation_id,
                role="assistant",
                content=content,
                model_used=model_used,
                token_count=token_count,
            )
            db.commit()
            db.refresh(assistant_message)
            return assistant_message
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _handle_blocked_message(
        project_id: int,
        conversation_id: int,
        content: str,
    ) -> tuple[ChatMessage, ChatMessage]:
        db = SessionLocal()
        try:
            user_message = ConversationService.save_message(
                db,
                project_id=project_id,
                conversation_id=conversation_id,
                role="user",
                content=content,
                auto_title=True,
            )
            assistant_message = ConversationService.save_message(
                db,
                project_id=project_id,
                conversation_id=conversation_id,
                role="assistant",
                content=ModerationService.blocked_response_message(),
                model_used=None,
                token_count=None,
            )
            db.commit()
            db.refresh(user_message)
            db.refresh(assistant_message)
            return user_message, assistant_message
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    async def send_message(
        current_user: User,
        project_id: int,
        conversation_id: int,
        message_data: MessageCreate,
    ) -> tuple[ChatMessage, ChatMessage]:
        content = message_data.content.strip()

        if settings.MODERATION_ENABLED:
            moderation = await run_sync_db(
                lambda: ModerationService.check(
                    content,
                    user_id=current_user.id,
                    project_id=project_id,
                )
            )

            if not moderation.allowed:
                return await run_sync_db(
                    lambda: ChatService._handle_blocked_message(
                        project_id,
                        conversation_id,
                        content,
                    )
                )

        prepared = await run_sync_db(
            lambda: ChatService._prepare_send(
                current_user.id,
                project_id,
                conversation_id,
                content,
            )
        )

        try:
            llm_result = await LLMService.generate_reply(
                prepared.llm_messages,
                primary_model=prepared.primary_model,
                fallback_model=prepared.fallback_model,
            )
        except asyncio.CancelledError:
            logger.info(
                "Chat generation cancelled for project %s conversation %s",
                project_id,
                conversation_id,
            )
            raise
        except LLMServiceError:
            raise
        except OperationalError:
            raise

        sanitized_content = ModerationService.sanitize_output(llm_result.content)

        assistant_message = await run_sync_db(
            lambda: ChatService._save_assistant_message(
                project_id,
                prepared.conversation_id,
                sanitized_content,
                llm_result.model_used,
                llm_result.token_count,
            )
        )

        return prepared.user_message, assistant_message
