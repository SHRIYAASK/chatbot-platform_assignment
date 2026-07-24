"""Detect whether document_chunks.embedding uses pgvector in the live database."""

import logging
from functools import lru_cache

from sqlalchemy import text

from app.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def embedding_storage_uses_pgvector() -> bool:
    """Return True when embeddings should be read/written as pgvector vectors."""
    if settings.USE_PGVECTOR:
        return True

    from app.core.database import engine

    if engine.dialect.name != "postgresql":
        return False

    try:
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT udt_name
                    FROM information_schema.columns
                    WHERE table_schema = current_schema()
                      AND table_name = 'document_chunks'
                      AND column_name = 'embedding'
                    """
                )
            ).first()
        if row is None:
            return False
        if row[0] == "vector":
            logger.info(
                "Detected pgvector embedding column; using vector storage "
                "even though USE_PGVECTOR=false."
            )
            return True
    except Exception:
        logger.exception("Failed to inspect document_chunks.embedding column type.")

    return False
