from pydantic import BaseModel, Field


class VoiceTokenResponse(BaseModel):
    livekit_url: str
    token: str
    room_name: str


class VoiceMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
