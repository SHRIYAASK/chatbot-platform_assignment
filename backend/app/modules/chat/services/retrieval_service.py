from sqlalchemy.orm import Session

from app.core.config import settings
from app.shared.rag.embedding_service import EmbeddingService
from app.shared.rag.prompt_builder import build_rag_system_message
from app.shared.rag.retriever import Retriever, RetrievedContext


import logging

logger = logging.getLogger(__name__)


class RetrievalService:
    """Chat-facing retrieval orchestration."""

    def __init__(
        self,
        db: Session,
        embedding_service: EmbeddingService,
    ) -> None:
        self._db = db
        self._embedding_service = embedding_service

    def retrieve_context(self, project_id: int, query: str) -> str | None:
        if not settings.RAG_ENABLED:
            return None

        try:
            retriever = Retriever(
                db=self._db,
                embedding_service=self._embedding_service,
                top_k=settings.RAG_TOP_K,
            )
            contexts = retriever.retrieve(project_id, query)
            return build_rag_system_message(contexts)
        except Exception:
            logger.warning(
                "RAG context retrieval failed for project %s; falling back to direct prompt",
                project_id,
                exc_info=True,
            )
            return None

    def retrieve_raw(self, project_id: int, query: str) -> list[RetrievedContext]:
        retriever = Retriever(
            db=self._db,
            embedding_service=self._embedding_service,
            top_k=settings.RAG_TOP_K,
        )
        return retriever.retrieve(project_id, query)
