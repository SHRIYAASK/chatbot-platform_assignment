from sqlalchemy import JSON, TypeDecorator

from app.core.config import settings


class EmbeddingVector(TypeDecorator):
    """Store vectors as pgvector when enabled, otherwise JSON arrays."""

    impl = JSON
    cache_ok = True

    def __init__(self, dimension: int) -> None:
        super().__init__()
        self.dimension = dimension

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and settings.USE_PGVECTOR:
            from pgvector.sqlalchemy import Vector

            return dialect.type_descriptor(Vector(self.dimension))
        return dialect.type_descriptor(JSON())
