from pydantic import BaseModel


class MessageResponse(BaseModel):
    detail: str


class HealthResponse(BaseModel):
    status: str
