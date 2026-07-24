import math
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine
from app.modules.chat.models.document_chunk import DocumentChunk
from app.shared.rag.embedding_service import EmbeddingService
from app.shared.rag.pgvector_support import embedding_storage_uses_pgvector


@dataclass(frozen=True)
class StoredChunkMatch:
    child_chunk_id: int
    parent_chunk_id: int
    child_content: str
    parent_content: str
    score: float


class VectorStore:
    """Persist and search child-chunk embeddings."""

    def __init__(self, db: Session, embedding_service: EmbeddingService) -> None:
        self._db = db
        self._embedding_service = embedding_service
        self._is_postgres = engine.dialect.name == "postgresql"

    @property
    def dimension(self) -> int:
        return self._embedding_service.dimension

    def store_child_embeddings(
        self,
        chunk_ids: list[int],
        embeddings: list[list[float]],
    ) -> None:
        if not chunk_ids:
            return

        embedding_by_id = dict(zip(chunk_ids, embeddings, strict=True))
        chunks = (
            self._db.query(DocumentChunk)
            .filter(DocumentChunk.id.in_(chunk_ids))
            .all()
        )
        for chunk in chunks:
            embedding = embedding_by_id.get(chunk.id)
            if embedding is not None:
                chunk.embedding = embedding
        self._db.flush()

    def search_similar_children(
        self,
        project_id: int,
        query_embedding: list[float],
        top_k: int,
    ) -> list[StoredChunkMatch]:
        if self._is_postgres and embedding_storage_uses_pgvector():
            try:
                return self._search_postgres(project_id, query_embedding, top_k)
            except Exception:
                return self._search_in_memory(project_id, query_embedding, top_k)
        return self._search_in_memory(project_id, query_embedding, top_k)

    def _search_postgres(
        self,
        project_id: int,
        query_embedding: list[float],
        top_k: int,
    ) -> list[StoredChunkMatch]:
        from pgvector.sqlalchemy import Vector

        distance = DocumentChunk.embedding.cosine_distance(query_embedding)
        rows = (
            self._db.query(DocumentChunk, distance.label("distance"))
            .filter(
                DocumentChunk.project_id == project_id,
                DocumentChunk.chunk_type == "child",
                DocumentChunk.embedding.isnot(None),
            )
            .order_by(distance.asc())
            .limit(top_k)
            .all()
        )

        matches: list[StoredChunkMatch] = []
        for child, distance_value in rows:
            parent = (
                self._db.query(DocumentChunk)
                .filter(DocumentChunk.id == child.parent_chunk_id)
                .first()
            )
            if parent is None:
                continue
            score = 1.0 - float(distance_value)
            matches.append(
                StoredChunkMatch(
                    child_chunk_id=child.id,
                    parent_chunk_id=parent.id,
                    child_content=child.content,
                    parent_content=parent.content,
                    score=score,
                )
            )
        return matches

    def _search_in_memory(
        self,
        project_id: int,
        query_embedding: list[float],
        top_k: int,
    ) -> list[StoredChunkMatch]:
        children = (
            self._db.query(DocumentChunk)
            .filter(
                DocumentChunk.project_id == project_id,
                DocumentChunk.chunk_type == "child",
                DocumentChunk.embedding.isnot(None),
            )
            .all()
        )

        scored: list[tuple[float, DocumentChunk]] = []
        for child in children:
            if not isinstance(child.embedding, list):
                continue
            score = _cosine_similarity(query_embedding, child.embedding)
            scored.append((score, child))

        scored.sort(key=lambda item: item[0], reverse=True)
        matches: list[StoredChunkMatch] = []

        for score, child in scored[:top_k]:
            parent = (
                self._db.query(DocumentChunk)
                .filter(DocumentChunk.id == child.parent_chunk_id)
                .first()
            )
            if parent is None:
                continue
            matches.append(
                StoredChunkMatch(
                    child_chunk_id=child.id,
                    parent_chunk_id=parent.id,
                    child_content=child.content,
                    parent_content=parent.content,
                    score=score,
                )
            )
        return matches


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(a * a for a in left)) or 1.0
    right_norm = math.sqrt(sum(b * b for b in right)) or 1.0
    return dot / (left_norm * right_norm)
