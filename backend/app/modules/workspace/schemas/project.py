from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.shared.validators import validate_project_description, validate_project_title


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=10, max_length=500)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return validate_project_title(value)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        return validate_project_description(value)


class ProjectUpdate(BaseModel):
    title: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=10, max_length=500)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return validate_project_title(value)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        return validate_project_description(value)


class ProjectSummary(BaseModel):
    messages: int
    conversations: int
    documents: int
    storage_mb: float
    model: str


class ProjectResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    primary_model: str
    fallback_model: str
    created_at: datetime
    updated_at: datetime
    summary: ProjectSummary | None = None

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    total: int
    projects: list[ProjectResponse]

