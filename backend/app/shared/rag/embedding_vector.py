from sqlalchemy import JSON, TypeDecorator

from app.core.config import settings
from app.shared.rag.pgvector_support import embedding_storage_uses_pgvector


class EmbeddingVector(TypeDecorator):
    """Store vectors as pgvector when enabled, otherwise JSON arrays."""

    impl = JSON
    cache_ok = True

    def __init__(self, dimension: int) -> None:
        super().__init__()
        self.dimension = dimension

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and embedding_storage_uses_pgvector():
            from pgvector.sqlalchemy import Vector

            return dialect.type_descriptor(Vector(self.dimension))
        return dialect.type_descriptor(JSON())
