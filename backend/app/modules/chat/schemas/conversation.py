from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ConversationCreate(BaseModel):
    title: str | None = Field(default="New Chat", max_length=200)


class ConversationUpdate(BaseModel):
    title: str = Field(..., min_length=3, max_length=60)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 3:
            raise ValueError("Title must be at least 3 characters long.")
        if len(cleaned) > 60:
            raise ValueError("Title must not exceed 60 characters.")
        return cleaned


class ConversationResponse(BaseModel):
    id: int
    project_id: int
    title: str
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
