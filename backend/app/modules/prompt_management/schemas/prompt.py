from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PromptCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)


class PromptUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)


class PromptResponse(BaseModel):
    id: int
    project_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromptListResponse(BaseModel):
    total: int
    prompts: list[PromptResponse]
