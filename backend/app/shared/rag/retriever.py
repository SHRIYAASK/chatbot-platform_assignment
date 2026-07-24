from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.shared.config.rag_settings import DEFAULT_TOP_K
from app.shared.rag.embedding_service import EmbeddingService
from app.shared.rag.vector_store import StoredChunkMatch, VectorStore


@dataclass(frozen=True)
class RetrievedContext:
    parent_content: str
    matched_child_content: str
    score: float
    source_label: str


class Retriever:
    """Retrieve parent context by searching child embeddings."""

    def __init__(
        self,
        db: Session,
        embedding_service: EmbeddingService,
        vector_store: VectorStore | None = None,
        top_k: int = DEFAULT_TOP_K,
    ) -> None:
        self._db = db
        self._embedding_service = embedding_service
        self._vector_store = vector_store or VectorStore(db, embedding_service)
        self._top_k = top_k

    def retrieve(self, project_id: int, query: str) -> list[RetrievedContext]:
        normalized = query.strip()
        if not normalized:
            return []

        query_embedding = self._embedding_service.embed_texts([normalized])[0]
        matches = self._vector_store.search_similar_children(
            project_id=project_id,
            query_embedding=query_embedding,
            top_k=self._top_k,
        )
        return self._expand_parent_context(matches)

    @staticmethod
    def _expand_parent_context(matches: list[StoredChunkMatch]) -> list[RetrievedContext]:
        seen_parent_ids: set[int] = set()
        contexts: list[RetrievedContext] = []

        for match in matches:
            if match.parent_chunk_id in seen_parent_ids:
                continue
            seen_parent_ids.add(match.parent_chunk_id)
            contexts.append(
                RetrievedContext(
                    parent_content=match.parent_content,
                    matched_child_content=match.child_content,
                    score=match.score,
                    source_label=f"chunk-{match.parent_chunk_id}",
                )
            )

        return contexts
