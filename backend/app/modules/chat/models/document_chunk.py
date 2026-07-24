from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.config import settings
from app.core.database import Base
from app.shared.rag.embedding_vector import EmbeddingVector


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_type = Column(String(10), nullable=False, index=True)
    parent_chunk_id = Column(
        Integer,
        ForeignKey("document_chunks.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(EmbeddingVector(settings.EMBEDDING_DIMENSION), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=func.now(),
        nullable=False,
    )

    document = relationship("Document", back_populates="chunks")
    parent_chunk = relationship(
        "DocumentChunk",
        remote_side="DocumentChunk.id",
        backref="child_chunks",
    )
