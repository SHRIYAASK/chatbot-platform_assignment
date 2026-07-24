from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)


class MessageResponse(BaseModel):
    id: int
    project_id: int
    conversation_id: int
    role: str
    content: str
    model_used: str | None
    token_count: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    messages: list[MessageResponse]
    next_cursor: str | None = None
    has_more: bool = False


class SendMessageResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse


class ChatProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    primary_model: str
    fallback_model: str
    system_prompt: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
