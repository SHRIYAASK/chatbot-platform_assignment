from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.config import settings


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("user_id", "title", name="uq_projects_user_id_title"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    primary_model = Column(String(100), nullable=False, default=settings.PRIMARY_MODEL)
    fallback_model = Column(String(100), nullable=False, default=settings.FALLBACK_MODEL)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    owner = relationship("User", back_populates="projects")
    prompts = relationship(
        "Prompt",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    files = relationship(
        "ProjectFile",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    documents = relationship(
        "Document",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    conversations = relationship(
        "Conversation",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    chat_messages = relationship(
        "ChatMessage",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    moderation_events = relationship(
        "ModerationEvent",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
